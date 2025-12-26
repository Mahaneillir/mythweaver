from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ..core.database import get_db
from ..models.user import User
from ..models.character import Character
from ..schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate
from ..utils.auth import get_current_user
from ..services.character_service import CharacterService

router = APIRouter()


@router.post("/", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new D&D character"""
    character_service = CharacterService(db)
    character = await character_service.create_character(current_user.id, character_data)
    return character


@router.get("/", response_model=List[CharacterResponse])
async def list_characters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all characters for the current user"""
    stmt = select(Character).where(Character.user_id == current_user.id)
    result = await db.execute(stmt)
    characters = result.scalars().all()
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific character details"""
    stmt = select(Character).where(
        Character.id == character_id,
        Character.user_id == current_user.id
    )
    result = await db.execute(stmt)
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    return character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: UUID,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update character (for level-ups, equipment changes)"""
    character_service = CharacterService(db)
    character = await character_service.update_character(
        character_id, current_user.id, character_update
    )
    return character


@router.delete("/{character_id}")
async def delete_character(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a character"""
    stmt = select(Character).where(
        Character.id == character_id,
        Character.user_id == current_user.id
    )
    result = await db.execute(stmt)
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    await db.delete(character)
    await db.commit()
    
    return {"message": "Character deleted successfully"}