from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

from config import settings
from database import connect_to_mongo, close_mongo_connection, get_database
from models import LinkCreate, LinkResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="KnowledgeLink API",
    description="API for saving and managing web links",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_page_metadata(url: str) -> dict:
    """Fetch title and description from a webpage."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = None
            if soup.title:
                title = soup.title.string
            elif soup.find('meta', property='og:title'):
                title = soup.find('meta', property='og:title').get('content')
            
            # Extract description
            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content')
            elif soup.find('meta', property='og:description'):
                description = soup.find('meta', property='og:description').get('content')
            
            return {
                "title": title,
                "description": description
            }
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return {"title": None, "description": None}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to KnowledgeLink API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/links": "Save a new link",
            "GET /api/links": "Get all saved links",
            "GET /api/links/{link_id}": "Get a specific link",
            "DELETE /api/links/{link_id}": "Delete a link"
        }
    }

@app.post("/api/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(link: LinkCreate):
    """Save a new link to the database."""
    db = get_database()
    
    # Convert URL to string for storage
    link_dict = link.dict()
    link_dict["url"] = str(link.url)
    
    # If title or description not provided, try to fetch from the webpage
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
    
    # Insert into MongoDB
    result = await db[settings.COLLECTION_NAME].insert_one(link_dict)
    
    # Fetch the created document
    created_link = await db[settings.COLLECTION_NAME].find_one({"_id": result.inserted_id})
    
    if created_link:
        created_link["id"] = str(created_link["_id"])
        return LinkResponse(**created_link)
    
    raise HTTPException(status_code=500, detail="Failed to create link")

@app.get("/api/links", response_model=List[LinkResponse])
async def get_links(skip: int = 0, limit: int = 100):
    """Get all saved links with pagination."""
    db = get_database()
    
    links = []
    cursor = db[settings.COLLECTION_NAME].find().skip(skip).limit(limit).sort("created_at", -1)
    
    async for document in cursor:
        document["id"] = str(document["_id"])
        links.append(LinkResponse(**document))
    
    return links

@app.get("/api/links/{link_id}", response_model=LinkResponse)
async def get_link(link_id: str):
    """Get a specific link by ID."""
    db = get_database()
    
    from bson import ObjectId
    
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid link ID format")
    
    link = await db[settings.COLLECTION_NAME].find_one({"_id": ObjectId(link_id)})
    
    if link:
        link["_id"] = str(link["_id"])
        return LinkResponse(**link)
    
    raise HTTPException(status_code=404, detail="Link not found")

@app.delete("/api/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(link_id: str):
    """Delete a link by ID."""
    db = get_database()
    
    from bson import ObjectId
    
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid link ID format")
    
    result = await db[settings.COLLECTION_NAME].delete_one({"_id": ObjectId(link_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return None

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db = get_database()
    try:
        # Ping MongoDB to check connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
