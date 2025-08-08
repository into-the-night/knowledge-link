from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import asyncio
from bson import ObjectId

from app.config.config import settings
from app.utils.database import get_database
from app.routes.models import LinkCreate, LinkResponse, SearchResult
from app.services.link_service import fetch_page_metadata, scrape_and_process_link
from app.utils.vector_db import content_processor


router = APIRouter()


@router.post("/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(link: LinkCreate):
    """Save a new link and trigger background processing for scraping and embedding."""
    db = get_database()
    
    # Convert URL to string for storage
    link_dict = link.dict()
    link_dict["url"] = str(link.url)
    
    # For now, user_id can be passed in the request or defaulted
    # When auth is implemented, this will come from the authenticated user
    if not link_dict.get("user_id"):
        link_dict["user_id"] = "default_user"
    
    # Try to fetch initial metadata if not provided
    if not link_dict.get("title") or not link_dict.get("description"):
        metadata = await fetch_page_metadata(str(link.url))
        if not link_dict.get("title"):
            link_dict["title"] = metadata["title"]
        if not link_dict.get("description"):
            link_dict["description"] = metadata["description"]
    
    # Add timestamps
    now = datetime.utcnow()
    link_dict["created_at"] = now
    link_dict["updated_at"] = now
    link_dict["summary"] = None  # Will be populated by background task
    
    # Insert into MongoDB
    result = await db[settings.COLLECTION_NAME].insert_one(link_dict)
    
    # Fetch the created document
    created_link = await db[settings.COLLECTION_NAME].find_one({"_id": result.inserted_id})
    
    if created_link:
        created_link["id"] = str(created_link["_id"])
        
        # Start background task for scraping, summarizing, and embedding
        link_id = str(created_link["_id"])
        user_id = link_dict.get("user_id")
        asyncio.create_task(scrape_and_process_link(link_id, str(link.url), user_id))
        
        return LinkResponse(**created_link)
    
    raise HTTPException(status_code=500, detail="Failed to create link")


@router.get("/links", response_model=List[LinkResponse])
async def get_links(
    skip: int = Query(0, ge=0, description="Number of links to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of links to return"),
    user_id: Optional[str] = Query(None, description="User ID (temporary until auth is implemented)")
):
    """Get all links for the user."""
    db = get_database()
    
    # Build query filter
    query_filter = {}
    if user_id:
        query_filter["user_id"] = user_id
    else:
        # Default user for now
        query_filter["user_id"] = "default_user"
    
    links = []
    cursor = db[settings.COLLECTION_NAME].find(query_filter).skip(skip).limit(limit).sort("created_at", -1)
    
    async for document in cursor:
        document["id"] = str(document["_id"])
        links.append(LinkResponse(**document))
    
    return links


@router.get("/search", response_model=List[SearchResult])
async def search_links(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity score"),
    user_id: Optional[str] = Query(None, description="User ID (temporary until auth is implemented)")
):
    """Search links using vector similarity search."""
    try:
        if not settings.GEMINI_API_KEY:
            raise HTTPException(
                status_code=503, 
                detail="Vector search is not available. Gemini API key not configured."
            )
        
        # Default user for now
        if not user_id:
            user_id = "default_user"
        
        # Perform vector search
        results = await content_processor.search_content(
            query=q,
            limit=limit,
            similarity_threshold=similarity_threshold,
            user_id=user_id
        )
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
