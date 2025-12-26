from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID
from typing import Dict, List, Any
import json

from ..models.character import Character
from ..schemas.character import CharacterCreate, CharacterUpdate, InventoryItem
from ..utils.dnd_rules import DnDRules


class CharacterService:
    """Service for character management and D&D rule calculations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dnd_rules = DnDRules()
    
    async def create_character(self, user_id: UUID, character_data: CharacterCreate) -> Character:
        """Create a new D&D character with proper stats and equipment"""
        
        # Calculate derived stats
        armor_class = self.dnd_rules.calculate_armor_class(
            character_data.stats.dexterity,
            armor_type="leather_armor"
        )
        
        proficiency_bonus = self.dnd_rules.get_proficiency_bonus(1)  # Level 1
        
        saving_throws = self.dnd_rules.calculate_saving_throws(
            character_data.stats.dict(),
            character_data.character_class,
            proficiency_bonus
        )
        
        # Generate starting equipment based on class
        inventory, equipment = self.dnd_rules.get_starting_equipment(
            character_data.character_class,
            character_data.background
        )
        
        # Calculate starting health
        health = self.dnd_rules.calculate_starting_health(
            character_data.character_class,
            character_data.stats.constitution
        )
        
        # Create character
        character = Character(
            user_id=user_id,
            name=character_data.name,
            character_class=character_data.character_class,
            race=character_data.race,
            background=character_data.background,
            level=1,
            experience=0,
            stats=character_data.stats.dict(),
            skills=character_data.skills.dict(),
            inventory=inventory,
            equipment=equipment,
            health=health,
            armor_class=armor_class,
            proficiency_bonus=proficiency_bonus,
            saving_throws=saving_throws
        )
        
        self.db.add(character)
        await self.db.commit()
        await self.db.refresh(character)
        
        return character
    
    async def update_character(
        self, 
        character_id: UUID, 
        user_id: UUID, 
        character_update: CharacterUpdate
    ) -> Character:
        """Update character for progression, equipment, etc."""
        
        stmt = select(Character).where(
            Character.id == character_id,
            Character.user_id == user_id
        )
        result = await self.db.execute(stmt)
        character = result.scalar_one_or_none()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        
        # Update fields
        update_data = character_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                if field == "level" and value != character.level:
                    # Handle level up - recalculate derived stats
                    character.level = value
                    character.proficiency_bonus = self.dnd_rules.get_proficiency_bonus(value)
                    character.armor_class = self.dnd_rules.calculate_armor_class_from_equipment(
                        character.stats["dexterity"], 
                        character.equipment
                    )
                else:
                    setattr(character, field, value)
        
        await self.db.commit()
        await self.db.refresh(character)
        
        return character
    
    async def level_up_character(self, character: Character, new_level: int) -> Dict[str, Any]:
        """Handle character leveling up with new abilities"""
        
        level_up_benefits = self.dnd_rules.get_level_up_benefits(
            character.character_class,
            character.level,
            new_level
        )
        
        # Update character
        character.level = new_level
        character.proficiency_bonus = self.dnd_rules.get_proficiency_bonus(new_level)
        
        # Add new features or skills
        if level_up_benefits.get("new_features"):
            # Handle new class features
            pass
        
        if level_up_benefits.get("skill_improvements"):
            # Handle skill improvements
            current_skills = character.skills
            for skill in level_up_benefits["skill_improvements"]:
                if skill not in current_skills["improved"]:
                    current_skills["improved"].append(skill)
            character.skills = current_skills
        
        await self.db.commit()
        await self.db.refresh(character)
        
        return level_up_benefits