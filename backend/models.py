from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
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
        validate_by_name = True
        arbitrary_types_allowed = True

class LinkResponse(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []
    content: Optional[str] = None
    content_type: Optional[str] = None
    word_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        validate_by_name = True

class LinkEmbedding(BaseModel):
    link_id: str
    content_chunks: List[str]
    embeddings: List[List[float]]
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_by_name = True

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    similarity_threshold: float = 0.7

class SearchResult(BaseModel):
    link: LinkResponse
    similarity_score: float
    relevant_chunks: List[str]
