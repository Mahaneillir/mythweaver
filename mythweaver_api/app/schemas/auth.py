"""
Mythweaver Authentication Schemas
Pydantic models for auth requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100, description="Valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserLogin(BaseModel):
    """User login request"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """JWT token response"""
    model_config = ConfigDict(populate_by_name=True)
    
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: Optional[UUID] = None