#!/usr/bin/env python3
"""
News Article Scraper Example

This example demonstrates scraping news articles with proper content extraction,
metadata collection, and text processing capabilities.

Features demonstrated:
- Article headline and content extraction
- Author and publication date detection
- Category and tag collection
- Content summarization and analysis
- Comment and social media metrics
- RSS feed processing capabilities
- Content deduplication

Prerequisites:
- ScraperV4 installed and configured
- Understanding of news website structures
- Optional: natural language processing libraries

Usage:
    python news-article-scraper.py

Expected Output:
- Structured article data with full content
- Metadata including author, date, and tags
- Content analysis and statistics
- Export in multiple formats for content management
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import hashlib

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from services.scraping_service import ScrapingService
from services.template_service import TemplateService
from services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsArticleScraper:
    """News article scraper with content analysis capabilities."""
    
    def __init__(self):
        """Initialize the scraper with required services."""
        self.scraping_service = ScrapingService()
        self.template_service = TemplateService()
        self.data_service = DataService()
        self.scraped_articles = set()  # For deduplication
        
    def create_news_template(self) -> Dict[str, Any]:
        """
        Create a comprehensive news article scraping template.
        
        This template demonstrates:
        - Article content extraction with structured data
        - Author and publication metadata
        - Social media and engagement metrics
        - Tag and category classification
        - Related articles and recommendations
        - Comment counting and analysis
        
        Returns:
            Dict containing the template configuration
        """
        template = {
            "name": "news_article_scraper",
            "description": "Comprehensive template for scraping news articles",
            "version": "2.0.0",
            
            # Standard fetcher configuration for news sites
            "fetcher_config": {
                "type": "basic",
                "basic": {
                    "timeout": 60,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1"
                    }
                }
            },
            
            # Comprehensive article selectors
            "selectors": {
                "headline": {
                    "selector": "h1.headline, h1.article-title, h1[itemprop='headline'], .article-headline h1, .post-title h1",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        "h1",
                        ".title h1",
                        ".entry-title",
                        "[data-testid='headline']",
                        ".story-title"
                    ]
                },
                
                "content": {
                    "selector": ".article-content, .article-body, [itemprop='articleBody'], .post-content, .entry-content",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".content",
                        ".story-body",
                        ".article-text",
                        ".post-body",
                        "#article-content"
                    ]
                },
                
                "author": {
                    "selector": "[itemprop='author'], .author-name, .byline-author, .article-author, .post-author",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".author",
                        ".writer",
                        ".byline",
                        "[data-author]",
                        ".author-link"
                    ]
                },
                
                "publish_date": {
                    "selector": "[itemprop='datePublished'], .publish-date, .article-date, .post-date, time[datetime]",
                    "type": "text",
                    "auto_save": True,
                    "attribute": "datetime",
                    "fallback_selectors": [
                        ".date",
                        ".timestamp",
                        "[data-date]",
                        ".published-date"
                    ]
                },
                
                "update_date": {
                    "selector": "[itemprop='dateModified'], .update-date, .modified-date, .last-updated",
                    "type": "text",
                    "auto_save": True,
                    "attribute": "datetime",
                    "fallback_selectors": [
                        ".updated",
                        ".last-modified",
                        "[data-updated]"
                    ]
                },
                
                "summary": {
                    "selector": ".article-summary, .article-excerpt, .post-excerpt, [itemprop='description'], .lead",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".excerpt",
                        ".intro",
                        ".summary",
                        ".description"
                    ]
                },
                
                "category": {
                    "selector": ".article-category, .post-category, [itemprop='articleSection'], .category",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".section",
                        ".topic",
                        ".channel",
                        "[data-category]"
                    ]
                },
                
                "tags": {
                    "selector": ".article-tags a, .post-tags a, .tag-list a, [rel='tag']",
                    "type": "all",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".tags a",
                        ".keywords a",
                        ".labels a",
                        ".topics a"
                    ]
                },
                
                "featured_image": {
                    "selector": ".featured-image img, .article-image img, [itemprop='image'], .hero-image img",
                    "type": "attribute",
                    "auto_save": True,
                    "attribute": "src",
                    "fallback_selectors": [
                        ".main-image img",
                        ".story-image img",
                        ".post-image img"
                    ]
                },
                
                "image_caption": {
                    "selector": ".image-caption, .photo-caption, figcaption, .caption",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".img-caption",
                        ".figure-caption"
                    ]
                },
                
                "social_shares": {
                    "selector": ".share-count, .social-count, [data-share-count]",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".shares",
                        ".share-number",
                        ".social-stats"
                    ]
                },
                
                "comment_count": {
                    "selector": ".comment-count, .comments-count, [data-comment-count]",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".comments-number",
                        ".discussion-count",
                        ".replies-count"
                    ]
                },
                
                "related_articles": {
                    "selector": ".related-articles a, .recommended-articles a, .more-stories a",
                    "type": "all",
                    "auto_save": True,
                    "attribute": "href",
                    "fallback_selectors": [
                        ".related-content a",
                        ".similar-articles a",
                        ".you-might-like a"
                    ]
                },
                
                "source": {
                    "selector": ".source, .news-source, [itemprop='publisher'], .publisher",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".publication",
                        ".media-source",
                        ".outlet"
                    ]
                }
            },
            
            # No pagination for single articles
            "pagination": {
                "enabled": False
            },
            
            # Advanced post-processing for news content
            "post_processing": [
                {
                    "type": "strip",
                    "field": "headline"
                },
                {
                    "type": "clean_content",
                    "field": "content"
                },
                {
                    "type": "strip",
                    "field": "author"
                },
                {
                    "type": "parse_date",
                    "field": "publish_date"
                },
                {
                    "type": "parse_date",
                    "field": "update_date"
                },
                {
                    "type": "strip",
                    "field": "summary"
                },
                {
                    "type": "strip",
                    "field": "category"
                },
                {
                    "type": "normalize_urls",
                    "field": "featured_image"
                },
                {
                    "type": "extract_number",
                    "field": "social_shares"
                },
                {
                    "type": "extract_number",
                    "field": "comment_count"
                },
                {
                    "type": "normalize_urls",
                    "field": "related_articles"
                },
                {
                    "type": "strip",
                    "field": "source"
                }
            ],
            
            # Validation rules for news articles
            "validation_rules": {
                "required_fields": ["headline", "content"],
                "field_types": {
                    "headline": "string",
                    "content": "string",
                    "author": "string",
                    "publish_date": "string",
                    "update_date": "string",
                    "summary": "string",
                    "category": "string",
                    "tags": "list",
                    "featured_image": "string",
                    "image_caption": "string",
                    "social_shares": "number",
                    "comment_count": "number",
                    "related_articles": "list",
                    "source": "string"
                },
                "min_lengths": {
                    "headline": 10,
                    "content": 100
                }
            },
            
            "adaptive_selectors": {
                "enabled": True,
                "learning_mode": True,
                "similarity_threshold": 0.85
            },
            
            "fallback_selectors": {
                "enabled": True,
                "max_attempts": 3
            },
            
            "is_active": True
        }
        
        return template
    
    def parse_publish_date(self, date_text: str) -> Optional[datetime]:
        """
        Parse publication date from various formats.
        
        Args:
            date_text: Raw date text from webpage
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_text:
            return None
            
        # Common date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',  # ISO format
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\d{4}/\d{1,2}/\d{1,2})',  # YYYY/MM/DD
            r'(\d{1,2}-\d{1,2}-\d{4})',  # DD-MM-YYYY
            r'(\w+ \d{1,2}, \d{4})',     # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    date_str = match.group(1)
                    # Try different parsing approaches
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%m/%d/%Y', '%Y/%m/%d', 
                               '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue
        
        return None
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze article content for various metrics.
        
        Args:
            content: Article content text
            
        Returns:
            Dictionary containing content analysis metrics
        """
        if not content:
            return {}
        
        # Basic text statistics
        word_count = len(content.split())
        char_count = len(content)
        sentence_count = len(re.split(r'[.!?]+', content))
        paragraph_count = len(content.split('\n\n'))
        
        # Reading time estimation (average 200 words per minute)
        reading_time_minutes = max(1, round(word_count / 200))
        
        # Content complexity (simplified)
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_word_length = sum(len(word) for word in content.split()) / max(word_count, 1)
        
        # Extract key phrases (simplified approach)
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top keywords (excluding common words)
        common_words = {'that', 'with', 'have', 'this', 'will', 'your', 'from', 'they', 
                       'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very',
                       'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many',
                       'over', 'such', 'take', 'than', 'them', 'well', 'were'}
        
        keywords = [(word, count) for word, count in word_freq.items() 
                   if word not in common_words and count > 1]
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "reading_time_minutes": reading_time_minutes,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_word_length": round(avg_word_length, 1),
            "top_keywords": keywords[:10],
            "complexity_score": min(10, max(1, round((avg_sentence_length + avg_word_length) / 2)))
        }
    
    def generate_content_hash(self, content: str) -> str:
        """
        Generate hash for content deduplication.
        
        Args:
            content: Article content
            
        Returns:
            SHA-256 hash of normalized content
        """
        # Normalize content for hash generation
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]
    
    def validate_article_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enhance article data.
        
        Args:
            data: Raw scraped article data
            
        Returns:
            Validated and enhanced article data
        """
        validated = {}
        
        # Required fields validation
        if not data.get('headline'):
            raise ValueError("Article headline is required")
        if not data.get('content'):
            raise ValueError("Article content is required")
            
        validated['headline'] = str(data['headline']).strip()
        validated['content'] = str(data['content']).strip()
        
        # Content deduplication check
        content_hash = self.generate_content_hash(validated['content'])
        if content_hash in self.scraped_articles:
            raise ValueError("Duplicate article content detected")
        self.scraped_articles.add(content_hash)
        validated['content_hash'] = content_hash
        
        # Analyze content
        content_analysis = self.analyze_content(validated['content'])
        validated.update(content_analysis)
        
        # Author information
        if data.get('author'):
            validated['author'] = str(data['author']).strip()
        
        # Parse and validate dates
        if data.get('publish_date'):
            parsed_date = self.parse_publish_date(str(data['publish_date']))
            if parsed_date:
                validated['publish_date'] = parsed_date.isoformat()
                validated['publish_timestamp'] = parsed_date.timestamp()
                # Calculate article age
                age_days = (datetime.now() - parsed_date).days
                validated['article_age_days'] = age_days
        
        if data.get('update_date'):
            parsed_date = self.parse_publish_date(str(data['update_date']))
            if parsed_date:
                validated['update_date'] = parsed_date.isoformat()
                validated['update_timestamp'] = parsed_date.timestamp()
        
        # Summary and excerpt
        if data.get('summary'):
            validated['summary'] = str(data['summary']).strip()
        else:
            # Generate summary from content (first 200 words)
            words = validated['content'].split()
            if len(words) > 200:
                validated['generated_summary'] = ' '.join(words[:200]) + '...'
        
        # Category and classification
        if data.get('category'):
            validated['category'] = str(data['category']).strip().lower()
        
        # Tags processing
        if data.get('tags') and isinstance(data['tags'], list):
            validated['tags'] = [str(tag).strip().lower() for tag in data['tags'] if tag]
            validated['tag_count'] = len(validated['tags'])
        
        # Images
        if data.get('featured_image'):
            validated['featured_image'] = str(data['featured_image']).strip()
            validated['has_featured_image'] = True
        else:
            validated['has_featured_image'] = False
            
        if data.get('image_caption'):
            validated['image_caption'] = str(data['image_caption']).strip()
        
        # Social metrics
        if data.get('social_shares'):
            try:
                validated['social_shares'] = int(re.search(r'\d+', str(data['social_shares'])).group())
            except (AttributeError, ValueError):
                validated['social_shares'] = 0
        else:
            validated['social_shares'] = 0
            
        if data.get('comment_count'):
            try:
                validated['comment_count'] = int(re.search(r'\d+', str(data['comment_count'])).group())
            except (AttributeError, ValueError):
                validated['comment_count'] = 0
        else:
            validated['comment_count'] = 0
        
        # Related articles
        if data.get('related_articles') and isinstance(data['related_articles'], list):
            validated['related_articles'] = [str(url).strip() for url in data['related_articles'] if url]
            validated['related_article_count'] = len(validated['related_articles'])
        
        # Source information
        if data.get('source'):
            validated['source'] = str(data['source']).strip()
        
        # Calculate engagement score
        engagement_score = 0
        if validated.get('social_shares', 0) > 0:
            engagement_score += min(5, validated['social_shares'] / 10)
        if validated.get('comment_count', 0) > 0:
            engagement_score += min(3, validated['comment_count'] / 5)
        if validated.get('word_count', 0) > 500:
            engagement_score += 2
        validated['engagement_score'] = round(engagement_score, 1)
        
        # Add metadata
        validated['scraped_at'] = datetime.now(timezone.utc).isoformat()
        validated['content_quality_score'] = self.calculate_content_quality(validated)
        
        return validated
    
    def calculate_content_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate content quality score based on completeness and metrics.
        
        Args:
            data: Validated article data
            
        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 0.0
        
        # Required content (40% of score)
        if data.get('headline') and len(data['headline']) > 10:
            score += 0.2
        if data.get('content') and data.get('word_count', 0) > 100:
            score += 0.2
        
        # Metadata completeness (30% of score)
        if data.get('author'):
            score += 0.1
        if data.get('publish_date'):
            score += 0.1
        if data.get('category'):
            score += 0.05
        if data.get('tags'):
            score += 0.05
        
        # Rich content (20% of score)
        if data.get('has_featured_image'):
            score += 0.1
        if data.get('summary') or data.get('generated_summary'):
            score += 0.1
        
        # Engagement metrics (10% of score)
        if data.get('social_shares', 0) > 0:
            score += 0.05
        if data.get('comment_count', 0) > 0:
            score += 0.05
        
        return min(1.0, score)
    
    async def scrape_article_urls(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape multiple article URLs.
        
        Args:
            urls: List of article URLs to scrape
            **kwargs: Additional configuration options
            
        Returns:
            List of scraped and validated article data
        """
        logger.info(f"Starting batch scraping of {len(urls)} article URLs")
        
        try:
            # Create and save template
            template = self.create_news_template()
            template_result = self.template_service.save_template(template)
            template_id = template_result.get("id")
            
            logger.info(f"Created template with ID: {template_id}")
            
            all_articles = []
            
            for i, url in enumerate(urls):
                logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
                
                try:
                    # Create job configuration
                    job_config = {
                        "name": f"Article scrape: {urlparse(url).netloc}",
                        "template_id": template_id,
                        "target_url": url,
                        "config": {
                            "use_proxy": kwargs.get("use_proxy", False),
                            "stealth_mode": kwargs.get("stealth_mode", "off"),
                            "delay_range": kwargs.get("delay_range", [1, 3]),
                            "retry_attempts": kwargs.get("retry_attempts", 2),
                            "timeout": kwargs.get("timeout", 60)
                        }
                    }
                    
                    # Create and start job
                    job = self.scraping_service.create_job(**job_config)
                    job_id = await self.scraping_service.start_scraping_job(job.id)
                    
                    # Monitor progress
                    await self._monitor_job_progress(job_id)
                    
                    # Get results
                    final_status = self.scraping_service.get_job_status(job_id)
                    
                    if final_status["status"] == "completed":
                        raw_results = self.data_service.get_result_data(job_id)
                        
                        for raw_data in raw_results:
                            try:
                                validated_data = self.validate_article_data(raw_data)
                                validated_data['source_url'] = url
                                validated_data['job_id'] = job_id
                                all_articles.append(validated_data)
                                logger.info(f"Successfully processed article: {validated_data.get('headline', 'Unknown')[:50]}...")
                            except ValueError as e:
                                logger.warning(f"Data validation failed for {url}: {e}")
                                continue
                    else:
                        logger.error(f"Scraping failed for {url}: {final_status.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")
                    continue
                
                # Respectful delay between URLs
                if i < len(urls) - 1:
                    delay = kwargs.get("batch_delay", 2)
                    logger.info(f"Waiting {delay} seconds before next URL...")
                    await asyncio.sleep(delay)
            
            logger.info(f"Batch scraping completed. Successfully processed {len(all_articles)} articles.")
            return all_articles
            
        except Exception as e:
            logger.error(f"Error during batch scraping: {str(e)}")
            return []
    
    async def _monitor_job_progress(self, job_id: str) -> None:
        """Monitor job progress with real-time updates."""
        while True:
            status = self.scraping_service.get_job_status(job_id)
            
            if status["status"] in ["completed", "failed", "stopped"]:
                logger.info(f"Job {job_id} finished with status: {status['status']}")
                break
                
            logger.info(f"Job {job_id} - Progress: {status.get('progress', 0)}% - "
                       f"Items: {status.get('items_scraped', 0)} - "
                       f"Status: {status['status']}")
            
            await asyncio.sleep(2)

async def main():
    """
    Main function demonstrating news article scraping.
    
    This example shows:
    1. Creating a news article scraper
    2. Scraping articles with content analysis
    3. Batch processing multiple URLs
    4. Content quality assessment
    5. Deduplication and validation
    """
    
    scraper = NewsArticleScraper()
    
    # Example article URLs (replace with actual news URLs)
    article_urls = [
        "https://example-news.com/politics/article-123",
        "https://example-news.com/technology/article-456",
        "https://example-news.com/business/article-789"
    ]
    
    print(f"\n{'='*60}")
    print("ScraperV4 News Article Scraping Example")
    print(f"{'='*60}")
    
    try:
        # Configure scraping options
        scraping_options = {
            "use_proxy": False,
            "stealth_mode": "off",  # Most news sites don't require stealth
            "delay_range": [1, 3],
            "retry_attempts": 2,
            "timeout": 60,
            "batch_delay": 2
        }
        
        # Scrape articles
        print(f"\n📰 Scraping {len(article_urls)} articles...")
        articles = await scraper.scrape_article_urls(article_urls, **scraping_options)
        
        if articles:
            print(f"\n✅ Successfully scraped {len(articles)} articles!")
            
            # Display results summary
            total_words = sum(a.get('word_count', 0) for a in articles)
            avg_reading_time = sum(a.get('reading_time_minutes', 0) for a in articles) / len(articles)
            total_engagement = sum(a.get('social_shares', 0) + a.get('comment_count', 0) for a in articles)
            
            print(f"\n📊 Scraping Summary:")
            print(f"   Total Articles: {len(articles)}")
            print(f"   Total Words: {total_words:,}")
            print(f"   Average Reading Time: {avg_reading_time:.1f} minutes")
            print(f"   Total Engagement: {total_engagement:,} shares/comments")
            
            # Show sample articles
            print(f"\n📄 Sample Articles:")
            for i, article in enumerate(articles[:2]):
                print(f"\n   Article {i+1}:")
                print(f"   📰 {article.get('headline', 'Unknown')}")
                print(f"   ✍️  {article.get('author', 'Unknown Author')}")
                if article.get('publish_date'):
                    print(f"   📅 {article.get('publish_date')[:10]}")
                print(f"   📝 {article.get('word_count', 0):,} words ({article.get('reading_time_minutes', 0)} min read)")
                if article.get('category'):
                    print(f"   🏷️  {article.get('category', '').title()}")
                if article.get('tags'):
                    print(f"   🔖 Tags: {', '.join(article.get('tags', [])[:5])}")
                print(f"   📊 Quality Score: {article.get('content_quality_score', 0):.1%}")
                print(f"   💬 {article.get('social_shares', 0)} shares, {article.get('comment_count', 0)} comments")
            
            # Content analysis
            categories = {}
            for article in articles:
                cat = article.get('category', 'uncategorized')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\n📈 Content Analysis:")
            print(f"   Categories: {dict(categories)}")
            
            # Top keywords across all articles
            all_keywords = {}
            for article in articles:
                for keyword, count in article.get('top_keywords', []):
                    all_keywords[keyword] = all_keywords.get(keyword, 0) + count
            
            top_global_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"   Top Keywords: {[kw[0] for kw in top_global_keywords[:5]]}")
            
        else:
            print("❌ No articles were successfully scraped")
            
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    asyncio.run(main())