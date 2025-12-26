"""
Pydantic schemas for campaign-related requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from .character import CharacterCreate, CharacterResponse


class CampaignSettings(BaseModel):
    """Campaign settings and preferences"""
    tone: str = Field(default="balanced", description="Campaign tone: gritty, heroic, balanced")
    content_limits: List[str] = Field(default_factory=list, description="Content restrictions")
    difficulty: str = Field(default="normal", description="Difficulty: easy, normal, hard")


class CreateCampaignRequest(BaseModel):
    """Request to create a new campaign with character"""
    campaign_name: str = Field(..., min_length=1, max_length=200)
    template_id: str = Field(default="broken_kingdom", description="Campaign template to use")
    settings: CampaignSettings = Field(default_factory=CampaignSettings)
    character: CharacterCreate


class CreateCampaignResponse(BaseModel):
    """Response after creating a campaign"""
    campaign_id: UUID
    character_id: UUID
    opening_narration: str
    suggested_actions: List[str]
    
    model_config = ConfigDict(from_attributes=True)


class CampaignResponse(BaseModel):
    """Full campaign state response"""
    id: UUID
    user_id: UUID
    name: str
    template_id: str
    current_scene_number: int
    chapter_number: int
    total_advances: int
    tone: str
    difficulty: str
    content_limits: List[str]
    current_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Include character data
    character: Optional[CharacterResponse] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignUpdate(BaseModel):
    """Schema for updating campaign state"""
    current_scene_number: Optional[int] = None
    chapter_number: Optional[int] = None
    total_advances: Optional[int] = None
    current_location: Optional[str] = None
    current_objective: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
