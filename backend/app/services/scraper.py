import asyncio
import re
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from readability import Document


class ContentScraper:
    """Advanced web content scraper with intelligent content extraction."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def scrape_url(self, url: str) -> Dict[str, any]:
        """
        Scrape content from a URL and return structured data.
        
        Returns:
            dict: Contains title, description, content, content_type, word_count, and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                response.raise_for_status()
                
                # Detect content type
                content_type = self._detect_content_type(response.headers.get('content-type', ''))
                
                if content_type == 'html':
                    return await self._scrape_html_content(url, response.text)
                else:
                    return {
                        'title': self._extract_title_from_url(url),
                        'description': None,
                        'content': response.text[:10000],  # Limit for non-HTML content
                        'content_type': content_type,
                        'word_count': len(response.text.split()),
                        'metadata': {
                            'url': url,
                            'status_code': response.status_code,
                            'headers': dict(response.headers)
                        }
                    }
                    
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'title': self._extract_title_from_url(url),
                'description': None,
                'content': None,
                'content_type': 'unknown',
                'word_count': 0,
                'metadata': {
                    'url': url,
                    'error': str(e)
                }
            }
    
    async def _scrape_html_content(self, url: str, html_content: str) -> Dict[str, any]:
        """Extract structured content from HTML."""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract metadata
        title = self._extract_title(soup, url)
        description = self._extract_description(soup)
        
        # Use readability for main content extraction
        try:
            doc = Document(html_content)
            main_content = doc.summary()
            content_soup = BeautifulSoup(main_content, 'lxml')
            clean_content = self._clean_text(content_soup.get_text())
        except Exception:
            # Fallback to manual content extraction
            clean_content = self._extract_content_fallback(soup)
        
        # Additional metadata
        metadata = self._extract_metadata(soup, url)
        word_count = len(clean_content.split()) if clean_content else 0
        
        return {
            'title': title,
            'description': description,
            'content': clean_content,
            'content_type': 'html',
            'word_count': word_count,
            'metadata': metadata
        }
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract title from various sources."""
        # Try different title sources in order of preference
        title_sources = [
            lambda: soup.find('meta', property='og:title'),
            lambda: soup.find('meta', attrs={'name': 'twitter:title'}),
            lambda: soup.find('title'),
            lambda: soup.find('h1'),
        ]
        
        for source in title_sources:
            try:
                element = source()
                if element:
                    if element.name == 'meta':
                        title = element.get('content', '').strip()
                    else:
                        title = element.get_text().strip()
                    
                    if title:
                        return self._clean_text(title)
            except:
                continue
        
        return self._extract_title_from_url(url)
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from meta tags."""
        desc_sources = [
            lambda: soup.find('meta', attrs={'name': 'description'}),
            lambda: soup.find('meta', property='og:description'),
            lambda: soup.find('meta', attrs={'name': 'twitter:description'}),
        ]
        
        for source in desc_sources:
            try:
                element = source()
                if element:
                    desc = element.get('content', '').strip()
                    if desc:
                        return self._clean_text(desc)
            except:
                continue
        
        return None
    
    def _extract_content_fallback(self, soup: BeautifulSoup) -> str:
        """Fallback content extraction when readability fails."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
            element.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.post-body',
            '.content-body'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                return self._clean_text(content_element.get_text())
        
        # If no specific content area found, extract from body
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return self._clean_text(soup.get_text())
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract additional metadata from the page."""
        metadata = {'url': url}
        
        # Extract Open Graph data
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                metadata[f'og_{prop}'] = content
        
        # Extract Twitter Card data
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                metadata[f'twitter_{name}'] = content
        
        # Extract author information
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline'
        ]
        
        for selector in author_selectors:
            author_element = soup.select_one(selector)
            if author_element:
                if author_element.name == 'meta':
                    author = author_element.get('content', '')
                else:
                    author = author_element.get_text()
                
                if author:
                    metadata['author'] = self._clean_text(author)
                    break
        
        # Extract publication date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publication_date"]',
            'time[datetime]',
            '.published',
            '.date'
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                if date_element.name == 'meta':
                    date = date_element.get('content', '')
                elif date_element.name == 'time':
                    date = date_element.get('datetime', '') or date_element.get_text()
                else:
                    date = date_element.get_text()
                
                if date:
                    metadata['published_date'] = self._clean_text(date)
                    break
        
        # Extract language
        lang = soup.find('html')
        if lang and lang.get('lang'):
            metadata['language'] = lang.get('lang')
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common unwanted patterns
        text = re.sub(r'^\s*cookie\s+policy.*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'^\s*privacy\s+policy.*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'^\s*subscribe.*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        return text
    
    def _detect_content_type(self, content_type_header: str) -> str:
        """Detect content type from headers."""
        content_type = content_type_header.lower()
        
        if 'text/html' in content_type:
            return 'html'
        elif 'application/pdf' in content_type:
            return 'pdf'
        elif 'text/plain' in content_type:
            return 'text'
        elif 'application/json' in content_type:
            return 'json'
        elif 'text/markdown' in content_type or 'text/x-markdown' in content_type:
            return 'markdown'
        else:
            return 'unknown'
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a title from URL as fallback."""
        try:
            parsed = urlparse(url)
            # Get the path and clean it up
            path = parsed.path.strip('/')
            if path:
                # Remove file extensions and replace separators
                title = re.sub(r'\.[^.]*$', '', path)
                title = re.sub(r'[-_/]', ' ', title)
                title = ' '.join(word.capitalize() for word in title.split())
                return title
            else:
                # Use domain name
                domain = parsed.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
                return domain.replace('.', ' ').title()
        except:
            return "Untitled"


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for better semantic search.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If we're not at the end, try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence endings within the last 200 characters
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + chunk_size - 200:
                end = sentence_end + 1
            else:
                # Look for word boundaries
                word_end = text.rfind(' ', start, end)
                if word_end > start + chunk_size - 100:
                    end = word_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position, considering overlap
        start = max(start + chunk_size - overlap, end)
        
        # Avoid infinite loop
        if start >= len(text):
            break
    
    return chunks
