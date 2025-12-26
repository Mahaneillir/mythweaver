"""
Narrator Router - AI Narrator Endpoints

This router will handle all narrator-related endpoints:
- Process player actions
- Generate AI narration
- Manage game state updates
- Handle check resolution

To be implemented in Week 4.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.exceptions import StoryfireExhausted, CampaignNotFound

router = APIRouter(
    prefix="/narrator",
    tags=["narrator"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def narrator_root():
    """
    Placeholder endpoint for narrator router.
    Will be replaced with actual gameplay endpoints in Week 4.
    """
    return {
        "message": "Narrator router initialized",
        "status": "placeholder",
        "planned_endpoints": [
            "POST /narrator/action - Process player action",
            "GET /narrator/context/{campaign_id} - Get game context",
            "POST /narrator/check - Perform skill check",
        ]
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Test endpoint to verify authentication.
    Returns current user information if authenticated.
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat(),
        "message": "Authentication successful"
    }
