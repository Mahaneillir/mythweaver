"""
Pydantic schemas module for request/response validation
"""
from .character import (
    AttributeScores,
    SkillsDict,
    TalentData,
    BondData,
    CharacterCreate,
    CharacterResponse,
    CharacterUpdate
)
from .campaign import (
    CampaignSettings,
    CreateCampaignRequest,
    CreateCampaignResponse,
    CampaignResponse,
    CampaignUpdate
)

__all__ = [
    # Character schemas
    'AttributeScores',
    'SkillsDict',
    'TalentData',
    'BondData',
    'CharacterCreate',
    'CharacterResponse',
    'CharacterUpdate',
    # Campaign schemas
    'CampaignSettings',
    'CreateCampaignRequest',
    'CreateCampaignResponse',
    'CampaignResponse',
    'CampaignUpdate',
]