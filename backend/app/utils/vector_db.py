from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import asyncio

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from app.utils.database import get_database
from app.config.config import settings
from app.routes.models import SearchResult, LinkResponse
from app.services.embeddings import ensure_embedding_service


class VectorDatabase:
    """Vector database operations for MongoDB."""
    
    def __init__(self): 
        self.collection_name = settings.VECTOR_COLLECTION_NAME
    
    async def create_vector_index(self):
        """Create vector search index for MongoDB Atlas.
        
        Note: The actual vector search index must be created in MongoDB Atlas UI or via API.
        This method creates supporting indexes.
        
        Vector Search Index Definition (create in Atlas UI):
        {
          "fields": [{
            "type": "vector",
            "path": "embedding",
            "numDimensions": 768,
            "similarity": "cosine"
          }]
        }
        """
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            # Create supporting indexes for filtering and sorting
            await collection.create_index([
                ("link_id", ASCENDING),
                ("user_id", ASCENDING),
                ("created_at", DESCENDING)
            ])
            
            # Create compound index for user-specific queries
            await collection.create_index([
                ("user_id", ASCENDING),
                ("link_id", ASCENDING)
            ])
            
            print(f"Created supporting indexes for {self.collection_name}")
            print("Note: Create vector search index in MongoDB Atlas UI with name 'vector_index'")
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    async def store_embeddings(
        self, 
        link_id: str, 
        content_chunks: List[str], 
        embeddings: List[List[float]],
        metadata: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Store embeddings for a link's content chunks.
        
        Args:
            link_id: ID of the associated link
            content_chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not content_chunks or not embeddings:
            return False
        
        if len(content_chunks) != len(embeddings):
            print(f"Mismatch between chunks ({len(content_chunks)}) and embeddings ({len(embeddings)})")
            return False
        
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            # Remove existing embeddings for this link
            await collection.delete_many({"link_id": link_id})
            
            # Prepare embedding documents
            embedding_docs = []
            for i, (chunk, embedding) in enumerate(zip(content_chunks, embeddings)):
                if embedding:  # Only store non-null embeddings
                    doc = {
                        "link_id": link_id,
                        "user_id": user_id,
                        "chunk_index": i,
                        "content_chunk": chunk,
                        "embedding": embedding,
                        "metadata": metadata or {},
                        "created_at": datetime.utcnow()
                    }
                    embedding_docs.append(doc)
            
            if embedding_docs:
                result = await collection.insert_many(embedding_docs)
                print(f"Stored {len(result.inserted_ids)} embeddings for link {link_id}")
                return True
            else:
                print(f"No valid embeddings to store for link {link_id}")
                return False
                
        except Exception as e:
            print(f"Error storing embeddings: {e}")
            return False
    
    async def search_similar_content(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        similarity_threshold: float = 0.7,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content using MongoDB Atlas Vector Search.
        
        Args:
            query_embedding: Embedding vector of the search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            user_id: Optional user ID to filter results
            
        Returns:
            List of matching documents with similarity scores
        """
        if not query_embedding:
            return []
        
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            # Build the vector search aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",  # Index name created in Atlas UI
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 10,  # Cast a wider net for better results
                        "limit": limit * 3  # Get more results to group by link later
                    }
                },
                {
                    "$addFields": {
                        "similarity_score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            # Add user filter if provided
            if user_id:
                pipeline.append({
                    "$match": {"user_id": user_id}
                })
            
            # Filter by similarity threshold
            pipeline.append({
                "$match": {
                    "similarity_score": {"$gte": similarity_threshold}
                }
            })
            
            # Sort by similarity score
            pipeline.append({
                "$sort": {"similarity_score": -1}
            })
            
            # Limit final results
            pipeline.append({"$limit": limit * 3})
            
            # Execute the aggregation pipeline
            cursor = await collection.aggregate(pipeline)
            results = await cursor.to_list(None)
            
            return results
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            print("Note: Ensure vector search index 'vector_index' exists in MongoDB Atlas")
            print("Falling back to local similarity search...")
            
            # Fallback to local similarity calculation if vector search fails
            return await self._fallback_similarity_search(
                query_embedding, limit, similarity_threshold, user_id
            )
    
    async def get_embeddings_by_link(self, link_id: str) -> List[Dict[str, Any]]:
        """Get all embeddings for a specific link."""
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            cursor = collection.find({"link_id": link_id}).sort("chunk_index", ASCENDING)
            embeddings = []
            async for doc in cursor:
                embeddings.append(doc)
            return embeddings
        except Exception as e:
            print(f"Error fetching embeddings for link {link_id}: {e}")
            return []
    
    async def delete_embeddings_by_link(self, link_id: str) -> bool:
        """Delete all embeddings for a specific link."""
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            result = await collection.delete_many({"link_id": link_id})
            print(f"Deleted {result.deleted_count} embeddings for link {link_id}")
            return True
        except Exception as e:
            print(f"Error deleting embeddings for link {link_id}: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            stats = {}
            
            # Total embeddings count
            stats["total_embeddings"] = await collection.count_documents({})
            
            # Unique links count
            pipeline = [
                {"$group": {"_id": "$link_id"}},
                {"$count": "unique_links"}
            ]
            result = await collection.aggregate(pipeline).to_list(1)
            stats["unique_links"] = result[0]["unique_links"] if result else 0
            
            # Recent embeddings (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            stats["recent_embeddings"] = await collection.count_documents({
                "created_at": {"$gte": yesterday}
            })
            
            return stats
            
        except Exception as e:
            print(f"Error getting vector database statistics: {e}")
            return {}
    
    async def _fallback_similarity_search(
        self,
        query_embedding: List[float],
        limit: int,
        similarity_threshold: float,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback to local similarity calculation if Atlas Vector Search is not available."""
        db = get_database()
        collection = db[self.collection_name]
        
        # Build query filter
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        
        # Fetch embeddings
        cursor = collection.find(query_filter).limit(1000)
        
        results = []
        async for doc in cursor:
            if "embedding" in doc and doc["embedding"]:
                # Calculate similarity locally
                similarity = await self._calculate_similarity(
                    query_embedding, 
                    doc["embedding"]
                )
                
                if similarity >= similarity_threshold:
                    doc["similarity_score"] = similarity
                    results.append(doc)
        
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results[:limit]
    
    @staticmethod
    async def _calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            
            arr1 = np.array(vec1)
            arr2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Convert from [-1, 1] to [0, 1] range
            return max(0.0, min(1.0, (similarity + 1) / 2))
            
        except Exception:
            return 0.0


class ContentProcessor:
    """Process content and generate embeddings for storage."""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
    
    async def process_link_content(
        self, 
        link_id: str, 
        content: str,
        metadata: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Process link content and store embeddings.
        
        Args:
            link_id: ID of the link
            content: Full text content
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not content or not content.strip():
            print(f"No content to process for link {link_id}")
            return False
        
        try:
            # Import chunking function
            from app.services.scraper import chunk_text
            
            # Split content into chunks
            chunks = chunk_text(content, chunk_size=1000, overlap=200)
            if not chunks:
                print(f"No chunks generated for link {link_id}")
                return False
            
            print(f"Generated {len(chunks)} chunks for link {link_id}")
            
            # Generate embeddings
            embedding_service = await ensure_embedding_service()
            embeddings = await embedding_service.generate_embeddings_batch(chunks)
            
            # Filter out None embeddings
            valid_chunks = []
            valid_embeddings = []
            for chunk, embedding in zip(chunks, embeddings):
                if embedding:
                    valid_chunks.append(chunk)
                    valid_embeddings.append(embedding)
            
            if not valid_embeddings:
                print(f"No valid embeddings generated for link {link_id}")
                return False
            
            print(f"Generated {len(valid_embeddings)} embeddings for link {link_id}")
            
            # Store in vector database
            success = await self.vector_db.store_embeddings(
                link_id=link_id,
                content_chunks=valid_chunks,
                embeddings=valid_embeddings,
                metadata=metadata,
                user_id=user_id
            )
            
            return success
            
        except Exception as e:
            print(f"Error processing content for link {link_id}: {e}")
            return False
    
    async def search_content(
        self, 
        query: str, 
        limit: int = 10,
        similarity_threshold: float = 0.7,
        user_id: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for content similar to the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        if not query or not query.strip():
            return []
        
        try:
            # Generate query embedding
            embedding_service = await ensure_embedding_service()
            query_embedding = await embedding_service.generate_query_embedding(query)
            
            if not query_embedding:
                print("Failed to generate query embedding")
                return []
            
            # Search for similar content using MongoDB Atlas Vector Search
            similar_docs = await self.vector_db.search_similar_content(
                query_embedding=query_embedding,
                limit=limit * 3,  # Get more to group by link
                similarity_threshold=similarity_threshold,
                user_id=user_id
            )
            
            if not similar_docs:
                return []
            
            # Group results by link and get link details
            from app.utils.database import get_database
            db = get_database()
            links_collection = db[settings.COLLECTION_NAME]
            
            link_results = {}
            for doc in similar_docs:
                link_id = doc["link_id"]
                
                if link_id not in link_results:
                    # Fetch link details
                    link_doc = await links_collection.find_one({"_id": ObjectId(link_id)})
                    if link_doc:
                        link_doc["id"] = str(link_doc["_id"])
                        link_results[link_id] = {
                            "link": LinkResponse(**link_doc),
                            "chunks": [],
                            "max_similarity": 0.0
                        }
                
                if link_id in link_results:
                    similarity_score = doc["similarity_score"]
                    link_results[link_id]["chunks"].append(doc["content_chunk"])
                    link_results[link_id]["max_similarity"] = max(
                        link_results[link_id]["max_similarity"], 
                        similarity_score
                    )
            
            # Convert to SearchResult objects
            search_results = []
            for link_data in link_results.values():
                search_result = SearchResult(
                    link=link_data["link"],
                    similarity_score=link_data["max_similarity"],
                    relevant_chunks=link_data["chunks"][:3]  # Limit chunks per result
                )
                search_results.append(search_result)
            
            # Sort by similarity score
            search_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return search_results[:limit]
            
        except Exception as e:
            print(f"Error searching content: {e}")
            return []


# Global instance
content_processor = ContentProcessor()
