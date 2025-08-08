from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


# Link Models
class LinkCreate(BaseModel):
    """Model for creating a new link."""
    url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    user_id: Optional[str] = None  # Will be used when auth is implemented


class LinkResponse(BaseModel):
    """Model for link response."""
    id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = []
    content: Optional[str] = None
    content_type: Optional[str] = None
    word_count: Optional[int] = None
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        validate_by_name = True


class SearchResult(BaseModel):
    """Model for search results."""
    link: LinkResponse
    similarity_score: float
    relevant_chunks: List[str]


# User Models
class UserResponse(BaseModel):
    """Model for user response."""
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        validate_by_name = True


class TokenResponse(BaseModel):
    """Model for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None