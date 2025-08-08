import asyncio
from typing import List, Optional, Tuple
import numpy as np
from google import genai

from app.config.config import settings


class EmbeddingService:
    """Service for generating and managing text embeddings using Gemini."""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is required for embeddings")
        
        # Initialize the client with API key
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text using Gemini.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            return None
        
        try:
            # Clean and truncate text if necessary
            clean_text = self._prepare_text(text)
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.model,
                    contents=clean_text
                )
            )
            
            # Extract embedding from response
            if response and response.embeddings:
                return response.embeddings[0].values
            return None
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (some may be None if generation failed)
        """
        if not texts:
            return []
        
        # Filter out empty texts and prepare them
        prepared_texts = []
        text_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                prepared_texts.append(self._prepare_text(text))
                text_indices.append(i)
        
        if not prepared_texts:
            return [None] * len(texts)
        
        try:
            embeddings = [None] * len(texts)
            
            # Process texts one by one or in batches
            # Gemini supports batch processing
            loop = asyncio.get_event_loop()
            
            # Process in smaller batches to avoid API limits
            batch_size = 100
            
            for i in range(0, len(prepared_texts), batch_size):
                batch = prepared_texts[i:i + batch_size]
                batch_indices = text_indices[i:i + batch_size]
                
                # Generate embeddings for batch
                batch_response = await loop.run_in_executor(
                    None,
                    lambda b=batch: self.client.models.embed_content(
                        model=self.model,
                        contents=b
                    )
                )
                
                # Extract embeddings from response
                if batch_response and batch_response.embeddings:
                    for j, embedding_obj in enumerate(batch_response.embeddings):
                        if j < len(batch_indices):
                            original_index = batch_indices[j]
                            embeddings[original_index] = embedding_obj.values
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating embeddings batch: {e}")
            return [None] * len(texts)
    
    def _prepare_text(self, text: str) -> str:
        """
        Prepare text for embedding generation.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned and truncated text
        """
        # Clean the text
        text = text.strip()
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Gemini has different token limits
        # Truncate if too long (conservative limit)
        max_chars = 8000 * 4  # Conservative limit for tokens
        if len(text) > max_chars:
            text = text[:max_chars]
            # Try to cut at a sentence boundary
            last_period = text.rfind('.')
            if last_period > max_chars * 0.8:  # If we can find a period in the last 20%
                text = text[:last_period + 1]
        
        return text
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between 0 and 1
        """
        if not vec1 or not vec2:
            return 0.0
        
        try:
            arr1 = np.array(vec1)
            arr2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, (similarity + 1) / 2))
            
        except Exception:
            return 0.0
    
    async def find_similar_chunks(
        self, 
        query_embedding: List[float], 
        chunk_embeddings: List[Tuple[str, List[float]]], 
        threshold: float = 0.7,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find chunks similar to the query embedding.
        
        Args:
            query_embedding: Embedding of the search query
            chunk_embeddings: List of (chunk_text, embedding) tuples
            threshold: Minimum similarity threshold
            limit: Maximum number of results
            
        Returns:
            List of (chunk_text, similarity_score) tuples sorted by similarity
        """
        if not query_embedding or not chunk_embeddings:
            return []
        
        similarities = []
        
        for chunk_text, chunk_embedding in chunk_embeddings:
            if chunk_embedding:
                similarity = self.cosine_similarity(query_embedding, chunk_embedding)
                if similarity >= threshold:
                    similarities.append((chunk_text, similarity))
        
        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    async def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for a search query using Gemini.
        
        Args:
            query: Search query text
            
        Returns:
            List of floats representing the embedding vector
        """
        if not query or not query.strip():
            return None
        
        try:
            # Clean the query
            clean_query = query.strip()
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.model,
                    contents=clean_query
                )
            )
            
            # Extract embedding from response
            if response and response.embeddings:
                return response.embeddings[0].values
            return None
            
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return None


# Global instance
embedding_service = EmbeddingService() if settings.GEMINI_API_KEY else None


async def ensure_embedding_service() -> EmbeddingService:
    """Ensure embedding service is available."""
    global embedding_service
    
    if embedding_service is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is required but not configured")
        embedding_service = EmbeddingService()
    
    return embedding_service