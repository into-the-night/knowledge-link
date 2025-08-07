from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = []

class Link(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class LinkResponse(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        allow_population_by_field_name = True
