"""
Pydantic schemas for character-related requests and responses
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID


class AttributeScores(BaseModel):
    """Character attribute scores"""
    might: int = Field(..., ge=0, le=20, description="Might attribute (0-20)")
    agility: int = Field(..., ge=0, le=20, description="Agility attribute (0-20)")
    wits: int = Field(..., ge=0, le=20, description="Wits attribute (0-20)")
    presence: int = Field(..., ge=0, le=20, description="Presence attribute (0-20)")
    
    @field_validator('might', 'agility', 'wits', 'presence')
    @classmethod
    def validate_attribute_range(cls, v):
        if not 0 <= v <= 20:
            raise ValueError('Attribute must be between 0 and 20')
        return v
    
    @property
    def total(self) -> int:
        """Calculate total attribute points"""
        return self.might + self.agility + self.wits + self.presence


class SkillsDict(BaseModel):
    """Character skills dictionary with skill names as keys and scores as values"""
    blade: int = Field(default=0, ge=0, le=20)
    bow: int = Field(default=0, ge=0, le=20)
    brawl: int = Field(default=0, ge=0, le=20)
    sneak: int = Field(default=0, ge=0, le=20)
    survival: int = Field(default=0, ge=0, le=20)
    lore: int = Field(default=0, ge=0, le=20)
    craft: int = Field(default=0, ge=0, le=20)
    influence: int = Field(default=0, ge=0, le=20)
    insight: int = Field(default=0, ge=0, le=20)
    channel: int = Field(default=0, ge=0, le=20)
    
    def model_dump(self, **kwargs) -> Dict[str, int]:
        """Convert to dictionary for database storage"""
        return super().model_dump(**kwargs)


class TalentData(BaseModel):
    """Individual talent data"""
    name: str
    description: str
    cost: int = Field(..., description="Focus cost to use")


class BondData(BaseModel):
    """Character bond data"""
    text: str = Field(..., max_length=200, description="Bond description")
    established_scene: int = Field(default=0, description="Scene where bond was established")


class CharacterCreate(BaseModel):
    """Request schema for creating a new character"""
    name: str = Field(..., min_length=1, max_length=100)
    origin_id: str = Field(..., description="Character origin ID (e.g., 'street_urchin')")
    path_id: str = Field(..., description="Character path ID (e.g., 'blade', 'shadow', 'mystic')")
    
    # Attributes
    attributes: AttributeScores
    
    # Skills (exactly 3 starting skills with scores)
    skills: SkillsDict
    
    # Talents (exactly 2 starting talent IDs)
    talent_ids: List[str] = Field(..., min_length=2, max_length=2)
    
    @field_validator('attributes')
    @classmethod
    def validate_attribute_total(cls, v):
        """Ensure attributes sum to exactly 15 (6+4+3+2)"""
        total = v.total
        if total != 15:
            raise ValueError(f'Attributes must sum to 15, got {total}')
        return v
    
    @field_validator('skills')
    @classmethod
    def validate_starting_skills(cls, v):
        """Ensure exactly 3 skills are selected (non-zero)"""
        selected_skills = [skill for skill, score in v.model_dump().items() if score > 0]
        if len(selected_skills) != 3:
            raise ValueError(f'Must select exactly 3 starting skills, got {len(selected_skills)}')
        return v


class CharacterResponse(BaseModel):
    """Response schema for character data"""
    id: UUID
    campaign_id: UUID
    name: str
    origin_id: str
    path_id: str

    # Attributes
    might_score: int
    agility_score: int
    wits_score: int
    presence_score: int

    # Resources
    current_hp: int
    max_hp: int
    current_focus: int
    max_focus: int
    supplies: int
    inventory_slots: Optional[int] = None

    # Complex data
    skills: Dict[str, int]
    talents: List[Dict]
    bonds: List[Dict]
    inventory: List[Dict]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CharacterUpdate(BaseModel):
    """Schema for updating character state during gameplay"""
    current_hp: Optional[int] = None
    current_focus: Optional[int] = None
    supplies: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)