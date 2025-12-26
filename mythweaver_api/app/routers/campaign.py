"""
Campaign endpoints for creating and managing campaigns.
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CreateCampaignRequest,
    CreateCampaignResponse,
    CampaignResponse,
)
from app.schemas.character import CharacterResponse
from app.services.campaign_service import (
    create_campaign,
    get_campaign,
    CampaignCreationError,
)

router = APIRouter(prefix="/campaign", tags=["Campaign"])


@router.post("/create", response_model=CreateCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_new_campaign(
    request: CreateCampaignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new campaign with an associated character.
    
    This endpoint:
    1. Validates the character creation request
    2. Calculates derived stats (HP, Focus, etc.)
    3. Creates a campaign and character in the database
    4. Loads the campaign template
    5. Generates the opening narration based on character origin
    6. Returns the campaign ID, character ID, opening narration, and suggested actions
    
    **Validation Rules:**
    - Attributes must sum to 15
    - Exactly 3 skills must be selected
    - Exactly 2 talents must be selected
    - Talents must match the character's path
    - Origin and path must be valid
    """
    try:
        response = await create_campaign(
            request=request,
            user_id=current_user.id,
            db=db,
        )
        return response
    except CampaignCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign_by_id(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a campaign by ID.
    
    Returns the campaign details along with the associated character.
    Only the owner of the campaign can access it.
    """
    try:
        campaign = await get_campaign(
            campaign_id=campaign_id,
            user_id=current_user.id,
            db=db,
        )
        
        # Convert to response schema
        response = CampaignResponse(
            id=campaign.id,
            user_id=campaign.user_id,
            name=campaign.name,
            template_id=campaign.template_id,
            current_scene_number=campaign.current_scene_number,
            chapter_number=campaign.chapter_number,
            total_advances=campaign.total_advances,
            tone=campaign.tone,
            difficulty=campaign.difficulty,
            content_limits=campaign.content_limits,
            current_location=campaign.current_location,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
        )
        
        # Add character if it exists
        if campaign.character:
            char = campaign.character
            response.character = CharacterResponse(
                id=char.id,
                campaign_id=char.campaign_id,
                name=char.name,
                origin_id=char.origin,
                path_id=char.path,
                might_score=char.might_score,
                agility_score=char.agility_score,
                wits_score=char.wits_score,
                presence_score=char.presence_score,
                current_hp=char.current_hp,
                max_hp=char.max_hp,
                current_focus=char.current_focus,
                max_focus=char.max_focus,
                supplies=char.supplies,
                inventory_slots=char.inventory_slots,
                skills=char.skills,
                talents=char.talents,
                bonds=char.bonds,
                inventory=char.inventory,
                created_at=char.created_at,
                updated_at=char.updated_at,
            )
        
        return response
        
    except CampaignCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign: {str(e)}",
        )
