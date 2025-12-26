"""
Custom Exception Classes for Mythweaver API

These exceptions provide standardized error handling for game-specific scenarios.
"""

from fastapi import HTTPException, status


class MythweaverException(HTTPException):
    """Base exception for all Mythweaver-specific errors"""
    
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class StoryfireExhausted(MythweaverException):
    """Raised when user has exhausted their daily Storyfire allocation"""
    
    def __init__(self, detail: str = "Daily Storyfire limit reached. Upgrade to Premium for unlimited actions."):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            error_code="STORYFIRE_EXHAUSTED"
        )


class CampaignNotFound(MythweaverException):
    """Raised when a requested campaign does not exist or user lacks access"""
    
    def __init__(self, campaign_id: str = None):
        detail = f"Campaign {campaign_id} not found" if campaign_id else "Campaign not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="CAMPAIGN_NOT_FOUND"
        )


class CharacterNotFound(MythweaverException):
    """Raised when a requested character does not exist"""
    
    def __init__(self, character_id: str = None):
        detail = f"Character {character_id} not found" if character_id else "Character not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="CHARACTER_NOT_FOUND"
        )


class UnauthorizedCampaignAccess(MythweaverException):
    """Raised when user tries to access a campaign they don't own"""
    
    def __init__(self, detail: str = "You do not have permission to access this campaign"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="UNAUTHORIZED_ACCESS"
        )


class InvalidGameState(MythweaverException):
    """Raised when game state is invalid or corrupted"""
    
    def __init__(self, detail: str = "Invalid game state"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="INVALID_GAME_STATE"
        )


class AIProviderError(MythweaverException):
    """Raised when OpenAI or other AI provider fails"""
    
    def __init__(self, detail: str = "AI service temporarily unavailable. Please try again."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="AI_PROVIDER_ERROR"
        )


class CharacterCreationError(MythweaverException):
    """Raised when character creation validation fails"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="CHARACTER_CREATION_ERROR"
        )
