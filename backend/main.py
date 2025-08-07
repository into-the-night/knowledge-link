from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime
import asyncio
import httpx
from bs4 import BeautifulSoup
from bson import ObjectId

from config import settings
from database import connect_to_mongo, close_mongo_connection, get_database
from models import LinkCreate, LinkResponse, SearchRequest, SearchResult
from scraper import ContentScraper
from vector_db import content_processor, VectorDatabase

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    
    # Initialize vector database
    vector_db = VectorDatabase()
    await vector_db.create_vector_index()
    
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
            "POST /api/links": "Save a new link with automatic content extraction",
            "GET /api/links": "Get all saved links",
            "GET /api/links/{link_id}": "Get a specific link",
            "DELETE /api/links/{link_id}": "Delete a link",
            "POST /api/search": "Search links by content similarity",
            "GET /api/stats": "Get vector database statistics"
        }
    }

async def scrape_and_process_link(link_id: str, url: str):
    """Background task to scrape and process link content."""
    try:
        print(f"Starting content processing for link {link_id}")
        
        # Scrape the content
        scraper = ContentScraper()
        scraped_data = await scraper.scrape_url(url)
        
        if scraped_data.get("content"):
            # Update the link with scraped content
            db = get_database()
            update_data = {
                "content": scraped_data["content"],
                "content_type": scraped_data["content_type"],
                "word_count": scraped_data["word_count"],
                "updated_at": datetime.utcnow()
            }
            
            # Update title and description if they were empty
            existing_link = await db[settings.COLLECTION_NAME].find_one({"_id": ObjectId(link_id)})
            if existing_link:
                if not existing_link.get("title") and scraped_data.get("title"):
                    update_data["title"] = scraped_data["title"]
                if not existing_link.get("description") and scraped_data.get("description"):
                    update_data["description"] = scraped_data["description"]
            
            await db[settings.COLLECTION_NAME].update_one(
                {"_id": ObjectId(link_id)},
                {"$set": update_data}
            )
            
            # Process content for vector storage
            await content_processor.process_link_content(
                link_id=link_id,
                content=scraped_data["content"],
                metadata=scraped_data.get("metadata", {})
            )
            
            print(f"Successfully processed content for link {link_id}")
        else:
            print(f"No content scraped for link {link_id}")
            
    except Exception as e:
        print(f"Error processing link {link_id}: {e}")

@app.post("/api/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(link: LinkCreate):
    """Save a new link to the database and trigger content processing."""
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
        
        # Start background content processing
        link_id = str(created_link["_id"])
        asyncio.create_task(scrape_and_process_link(link_id, str(link.url)))
        
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
    """Delete a link by ID and clean up associated embeddings."""
    db = get_database()
    
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid link ID format")
    
    # Delete the link
    result = await db[settings.COLLECTION_NAME].delete_one({"_id": ObjectId(link_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Clean up embeddings in background
    vector_db = VectorDatabase()
    asyncio.create_task(vector_db.delete_embeddings_by_link(link_id))
    
    return None

@app.post("/api/search", response_model=List[SearchResult])
async def search_links(search_request: SearchRequest):
    """Search links by content similarity using vector embeddings."""
    try:
        if not settings.GEMINI_API_KEY:
            raise HTTPException(
                status_code=503, 
                detail="Vector search is not available. OpenAI API key not configured."
            )
        
        results = await content_processor.search_content(
            query=search_request.query,
            limit=search_request.limit,
            similarity_threshold=search_request.similarity_threshold
        )
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.post("/api/links/{link_id}/reprocess")
async def reprocess_link(link_id: str):
    """Manually reprocess a link's content and regenerate embeddings."""
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid link ID format")
    
    db = get_database()
    link = await db[settings.COLLECTION_NAME].find_one({"_id": ObjectId(link_id)})
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Start reprocessing in background
    asyncio.create_task(scrape_and_process_link(link_id, link["url"]))
    
    return {"message": "Link reprocessing started", "link_id": link_id}

@app.get("/api/stats")
async def get_statistics():
    """Get statistics about the knowledge base."""
    try:
        db = get_database()
        
        # Basic link statistics
        total_links = await db[settings.COLLECTION_NAME].count_documents({})
        links_with_content = await db[settings.COLLECTION_NAME].count_documents({
            "content": {"$exists": True, "$ne": None}
        })
        
        # Vector database statistics
        vector_db = VectorDatabase()
        vector_stats = await vector_db.get_statistics()
        
        return {
            "links": {
                "total": total_links,
                "with_content": links_with_content,
                "processing_rate": f"{(links_with_content / total_links * 100):.1f}%" if total_links > 0 else "0%"
            },
            "embeddings": vector_stats,
            "features": {
                "vector_search_enabled": bool(settings.GEMINI_API_KEY),
                "embedding_model": settings.EMBEDDING_MODEL if settings.GEMINI_API_KEY else None
            }
        }
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db = get_database()
    try:
        # Ping MongoDB to check connection
        await db.command("ping")
        
        # Check if vector search is available
        vector_search_available = bool(settings.GEMINI_API_KEY)
        
        return {
            "status": "healthy", 
            "database": "connected",
            "vector_search": "enabled" if vector_search_available else "disabled"
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
