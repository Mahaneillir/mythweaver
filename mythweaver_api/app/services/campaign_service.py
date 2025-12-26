"""
Campaign service for creating and managing campaigns.
"""
from typing import Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.campaign import Campaign
from app.models.character import Character
from app.schemas.campaign import CreateCampaignRequest, CreateCampaignResponse
from app.services.rules_engine import (
    validate_character_creation,
    calculate_max_hp,
    calculate_max_focus,
    calculate_inventory_slots,
)
from app.services.campaign_template_service import (
    load_campaign_template,
    get_opening_narration,
    get_suggested_actions,
    get_starting_location,
    validate_template,
)


class CampaignCreationError(Exception):
    """Raised when campaign creation fails."""
    pass


async def create_campaign(
    request: CreateCampaignRequest,
    user_id: UUID,
    db: AsyncSession
) -> CreateCampaignResponse:
    """
    Create a new campaign with an associated character.
    
    Args:
        request: Campaign creation request data
        user_id: ID of the user creating the campaign
        db: Database session
        
    Returns:
        CreateCampaignResponse with campaign_id, character_id, opening narration, and suggested actions
        
    Raises:
        CampaignCreationError: If campaign creation fails
    """
    # Step 1: Validate template exists
    if not validate_template(request.template_id):
        raise CampaignCreationError(f"Invalid template_id: {request.template_id}")
    
    # Step 2: Validate character creation request
    character_data = request.character
    
    # Basic validation
    attributes_dict = {
        "might": character_data.attributes.might,
        "agility": character_data.attributes.agility,
        "wits": character_data.attributes.wits,
        "presence": character_data.attributes.presence,
    }
    
    # Check attributes sum to 15
    attr_sum = sum(attributes_dict.values())
    if attr_sum != 15:
        raise CampaignCreationError(f"Attributes must sum to 15, got {attr_sum}")
    
    # Check exactly 3 skills selected
    skills_dict = dict(character_data.skills)
    selected_skills = [k for k, v in skills_dict.items() if v > 0]
    if len(selected_skills) != 3:
        raise CampaignCreationError(f"Must select exactly 3 skills, got {len(selected_skills)}")
    
    # Check exactly 2 talents
    if len(character_data.talent_ids) != 2:
        raise CampaignCreationError(f"Must select exactly 2 talents, got {len(character_data.talent_ids)}")
    
    # Step 3: Calculate derived stats
    max_hp = calculate_max_hp(character_data.attributes.might)
    max_focus = calculate_max_focus(character_data.attributes.wits, character_data.attributes.presence)
    inventory_slots = calculate_inventory_slots(character_data.attributes.might)
    
    try:
        # Step 4: Create campaign
        settings_dict = request.settings.model_dump() if request.settings else {}
        campaign = Campaign(
            user_id=user_id,
            name=request.campaign_name,
            template_id=request.template_id,
            current_scene_number=1,
            chapter_number=1,
            total_advances=0,
            tone=settings_dict.get("tone", "balanced"),
            difficulty=settings_dict.get("difficulty", "normal"),
            content_limits=settings_dict.get("content_limits", []),
        )
        db.add(campaign)
        await db.flush()  # Get campaign ID without committing
        
        # Step 5: Create character
        character = Character(
            campaign_id=campaign.id,
            name=character_data.name,
            origin=character_data.origin_id,
            path=character_data.path_id,
            # Attributes
            might_score=character_data.attributes.might,
            agility_score=character_data.attributes.agility,
            wits_score=character_data.attributes.wits,
            presence_score=character_data.attributes.presence,
            # Resources
            current_hp=max_hp,
            max_hp=max_hp,
            current_focus=max_focus,
            max_focus=max_focus,
            supplies=3,  # Default starting supplies
            # JSONB fields
            skills=dict(character_data.skills),
            talents=[],  # Start empty, will be populated from game data
            bonds=[],    # Start empty
            inventory=[],  # Start empty
        )
        db.add(character)
        
        # Commit transaction
        await db.commit()
        await db.refresh(campaign)
        await db.refresh(character)
        
        # Step 6: Generate opening narration
        opening_narration = get_opening_narration(request.template_id, character_data.origin_id)
        
        # Step 7: Get suggested actions
        suggested_actions = get_suggested_actions(request.template_id)
        
        # Step 8: Return response
        return CreateCampaignResponse(
            campaign_id=campaign.id,
            character_id=character.id,
            opening_narration=opening_narration,
            suggested_actions=suggested_actions,
        )
        
    except CampaignCreationError:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise CampaignCreationError(f"Failed to create campaign: {str(e)}")


async def get_campaign(campaign_id: UUID, user_id: UUID, db: AsyncSession) -> Campaign:
    """
    Retrieve a campaign by ID.
    
    Args:
        campaign_id: ID of the campaign to retrieve
        user_id: ID of the user requesting the campaign
        db: Database session
        
    Returns:
        Campaign object with character loaded
        
    Raises:
        CampaignCreationError: If campaign not found or user doesn't own it
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.character))
        .where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise CampaignCreationError("Campaign not found or you don't have access")
    
    return campaign
