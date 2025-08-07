import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "knowledgelink")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "links")
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

settings = Settings()
