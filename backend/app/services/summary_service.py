import asyncio
from typing import Optional
from google import genai
from app.config.config import settings


class SummaryService:
    """Service for generating text summaries using Gemini."""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is required for summary generation")
        
        # Initialize the client with API key
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Use a text generation model for summaries
        self.model = "models/gemini-1.5-flash"
    
    async def generate_summary(self, text: str, max_length: int = 300) -> Optional[str]:
        """
        Generate a summary of the provided text using Gemini.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            
        Returns:
            Summary string or None if generation failed
        """
        if not text or not text.strip():
            return None
        
        try:
            # Prepare the prompt
            prompt = f"""Please provide a concise summary of the following text in no more than {max_length} words. 
            Focus on the main points and key information.
            
            Text:
            {text[:10000]}  # Limit input to avoid token limits
            
            Summary:"""
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
            )
            
            # Extract summary from response
            if response and response.text:
                return response.text.strip()
            return None
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
    
    async def generate_title_from_content(self, text: str) -> Optional[str]:
        """
        Generate a title from content if none exists.
        
        Args:
            text: Text content
            
        Returns:
            Generated title or None
        """
        if not text or not text.strip():
            return None
        
        try:
            prompt = f"""Generate a short, descriptive title (max 10 words) for the following content:
            
            {text[:2000]}
            
            Title:"""
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
            )
            
            if response and response.text:
                # Clean up the title
                title = response.text.strip()
                # Remove quotes if present
                title = title.strip('"\'')
                return title
            return None
            
        except Exception as e:
            print(f"Error generating title: {e}")
            return None


# Global instance
summary_service = SummaryService() if settings.GEMINI_API_KEY else None


async def ensure_summary_service() -> SummaryService:
    """Ensure summary service is available."""
    global summary_service
    
    if summary_service is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is required but not configured")
        summary_service = SummaryService()
    
    return summary_service
