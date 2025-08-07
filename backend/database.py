from pymongo import AsyncMongoClient
from typing import Optional
from config import settings

class MongoDB:
    client: Optional[AsyncMongoClient] = None
    database = None
    
mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection."""
    mongodb.client = AsyncMongoClient(settings.MONGODB_URI)
    mongodb.database = mongodb.client[settings.DATABASE_NAME]
    print(f"Connected to MongoDB at {settings.MONGODB_URI}")

async def close_mongo_connection():
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance."""
    return mongodb.database
