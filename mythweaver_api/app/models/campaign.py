"""
Mythweaver Campaign Model
Represents ongoing campaigns with full game state
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Campaign(Base):
    """Campaign model tracking story progress and game state"""
    __tablename__ = "mythweaver_campaigns"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Campaign identity
    name = Column(String(200), nullable=False)
    template_id = Column(String(50), nullable=False, default="broken_kingdom")  # e.g., "broken_kingdom"
    
    # Story progression
    current_scene_number = Column(Integer, nullable=False, default=1)
    chapter_number = Column(Integer, nullable=False, default=1)
    total_advances = Column(Integer, nullable=False, default=0)  # Character progression counter
    current_location = Column(String(200), nullable=True, default="The Crossroads Inn")  # Current location in story
    
    # Game settings (stored as individual fields to match database schema)
    tone = Column(String(50), nullable=False, default="balanced")
    difficulty = Column(String(50), nullable=False, default="normal")
    content_limits = Column(JSONB, nullable=False, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    character = relationship("Character", back_populates="campaign", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', scene={self.current_scene_number})>"
