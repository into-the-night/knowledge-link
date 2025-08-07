import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "knowledgelink")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "links")
    VECTOR_COLLECTION_NAME: str = os.getenv("VECTOR_COLLECTION_NAME", "link_embeddings")
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Gemini settings for embeddings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))

settings = Settings()
