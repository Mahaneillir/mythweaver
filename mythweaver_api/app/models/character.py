"""
Mythweaver Character Model
Represents player characters with attributes, skills, talents, and resources
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Character(Base):
    """Player character model with full game stats"""
    __tablename__ = "mythweaver_characters"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("mythweaver_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Character creation choices
    origin = Column(String(50), nullable=False)  # e.g., "Street Urchin", "Veteran", "Acolyte"
    path = Column(String(50), nullable=False)    # e.g., "Blade", "Shadow", "Mystic"
    
    # Attributes (0-20 range)
    might_score = Column(Integer, nullable=False, default=0)
    agility_score = Column(Integer, nullable=False, default=0)
    wits_score = Column(Integer, nullable=False, default=0)
    presence_score = Column(Integer, nullable=False, default=0)
    
    # Resources
    current_hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    current_focus = Column(Integer, nullable=False)
    max_focus = Column(Integer, nullable=False)
    supplies = Column(Integer, nullable=False, default=3)  # Inventory abstraction
    
    # JSONB fields for complex data
    skills = Column(JSONB, nullable=False, default=dict)
    # Format: {"Blade": 8, "Sneak": 4, "Insight": 4, ...}
    
    talents = Column(JSONB, nullable=False, default=list)
    # Format: [{"name": "Riposte", "description": "...", "cost": 2}, ...]
    
    bonds = Column(JSONB, nullable=False, default=list)
    # Format: [{"text": "My sister is in danger", "established_scene": 0}, ...]
    
    inventory = Column(JSONB, nullable=False, default=list)
    # Format: [{"name": "Rusty Sword", "description": "...", "equipped": true}, ...]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="character")
    
    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', path='{self.path}')>"
    
    @property
    def effective_might_bonus(self) -> int:
        """Calculate Effective Attribute Bonus for Might"""
        return self.might_score // 2
    
    @property
    def effective_agility_bonus(self) -> int:
        """Calculate Effective Attribute Bonus for Agility"""
        return self.agility_score // 2
    
    @property
    def effective_wits_bonus(self) -> int:
        """Calculate Effective Attribute Bonus for Wits"""
        return self.wits_score // 2
    
    @property
    def effective_presence_bonus(self) -> int:
        """Calculate Effective Attribute Bonus for Presence"""
        return self.presence_score // 2
    
    def get_skill_rank(self, skill_name: str) -> int:
        """Calculate Skill Rank for a given skill"""
        skill_score = self.skills.get(skill_name, 0)
        return skill_score // 4

    @property
    def inventory_slots(self) -> int:
        """Calculate inventory slots based on Might score"""
        return self.might_score // 2