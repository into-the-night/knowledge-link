from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.config import settings
from app.utils.database import connect_to_mongo, close_mongo_connection
from app.utils.vector_db import VectorDatabase
from app.routes import links, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
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

# Include routers
app.include_router(links.router, prefix="/link", tags=["links"])
app.include_router(auth.router, prefix="/user", tags=["auth"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to KnowledgeLink API",
        "version": "1.0.0",
        "endpoints": {
            "POST /link/links": "Save a new link",
            "GET /link/links": "Get all links for the user",
            "GET /link/search": "Search links by similarity",
            "GET /user/auth/google": "Google OAuth login",
            "GET /user/auth/callback": "OAuth callback",
            "GET /user/me": "Get current user info",
            "POST /user/logout": "Logout user"
        }
    }
