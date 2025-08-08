import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
from bson import ObjectId

from app.config.config import settings
from app.utils.database import get_database
from app.services.summary_service import ensure_summary_service
from app.utils.vector_db import content_processor


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


async def scrape_and_process_link(link_id: str, url: str, user_id: Optional[str] = None):
    """Background task to scrape, summarize, embed and save link content."""
    try:
        print(f"Starting content processing for link {link_id}")
        
        # Import scraper
        from app.services.scraper import ContentScraper
        
        # Step 1: Scrape the content
        scraper = ContentScraper()
        scraped_data = await scraper.scrape_url(url)
        
        if scraped_data.get("content"):
            db = get_database()
            update_data = {
                "content": scraped_data["content"],
                "content_type": scraped_data["content_type"],
                "word_count": scraped_data["word_count"],
                "updated_at": datetime.utcnow()
            }
            
            # Update title if it was empty
            existing_link = await db[settings.COLLECTION_NAME].find_one({"_id": ObjectId(link_id)})
            if existing_link:
                if not existing_link.get("title"):
                    if scraped_data.get("title"):
                        update_data["title"] = scraped_data["title"]
                    else:
                        # Generate title from content if needed
                        try:
                            summary_service = await ensure_summary_service()
                            generated_title = await summary_service.generate_title_from_content(
                                scraped_data["content"]
                            )
                            if generated_title:
                                update_data["title"] = generated_title
                        except Exception as e:
                            print(f"Error generating title: {e}")
                
                if not existing_link.get("description") and scraped_data.get("description"):
                    update_data["description"] = scraped_data["description"]
            
            # Step 2: Generate summary using Gemini
            try:
                summary_service = await ensure_summary_service()
                summary = await summary_service.generate_summary(scraped_data["content"])
                if summary:
                    update_data["summary"] = summary
                    print(f"Generated summary for link {link_id}")
            except Exception as e:
                print(f"Error generating summary for link {link_id}: {e}")
            
            # Step 3: Update the link with scraped content and summary
            await db[settings.COLLECTION_NAME].update_one(
                {"_id": ObjectId(link_id)},
                {"$set": update_data}
            )
            
            # Step 4: Generate embeddings and store in vector database
            await content_processor.process_link_content(
                link_id=link_id,
                content=scraped_data["content"],
                metadata=scraped_data.get("metadata", {}),
                user_id=user_id
            )
            
            print(f"Successfully processed content for link {link_id}")
        else:
            print(f"No content scraped for link {link_id}")
            
    except Exception as e:
        print(f"Error processing link {link_id}: {e}")
