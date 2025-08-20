#!/usr/bin/env python3
"""
Social Media Scraper Example

This example demonstrates scraping public social media content with proper
rate limiting, content extraction, and engagement metrics collection.

Features demonstrated:
- Public post content extraction
- User profile information gathering
- Engagement metrics (likes, shares, comments)
- Hashtag and mention extraction
- Timestamp and metadata collection
- Content sentiment analysis preparation
- Rate limiting and respectful scraping

Prerequisites:
- ScraperV4 installed and configured
- Understanding of social media platform structures
- Awareness of platform terms of service and rate limits
- Optional: sentiment analysis libraries

Usage:
    python social-media-scraper.py

Expected Output:
- Structured social media post data
- User and engagement information
- Hashtag and trend analysis
- Export formats suitable for social listening

Note: Always respect platform terms of service and rate limits.
      This example is for educational purposes with public content only.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from services.scraping_service import ScrapingService
from services.template_service import TemplateService
from services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SocialMediaScraper:
    """Social media scraper with engagement analysis capabilities."""
    
    def __init__(self):
        """Initialize the scraper with required services."""
        self.scraping_service = ScrapingService()
        self.template_service = TemplateService()
        self.data_service = DataService()
        self.scraped_posts = set()  # For deduplication
        
    def create_social_template(self) -> Dict[str, Any]:
        """
        Create a comprehensive social media scraping template.
        
        This template demonstrates:
        - Post content and metadata extraction
        - User profile information collection
        - Engagement metrics gathering
        - Hashtag and mention detection
        - Media content identification
        - Timestamp and location data
        
        Returns:
            Dict containing the template configuration
        """
        template = {
            "name": "social_media_scraper",
            "description": "Comprehensive template for scraping public social media content",
            "version": "2.0.0",
            
            # Stealth configuration for social media platforms
            "fetcher_config": {
                "type": "stealth",
                "stealth": {
                    "headless": True,
                    "humanize": True,
                    "block_webrtc": True,
                    "spoof_canvas": True,
                    "os_randomization": True,
                    "network_idle": True,
                    "wait_for_selector": "[data-testid='tweet'], .post-content, article",
                    "google_search": False,
                    "disable_ads": True
                },
                "basic": {
                    "timeout": 45,
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
            
            # Comprehensive social media selectors
            "selectors": {
                "post_content": {
                    "selector": "[data-testid='tweetText'], .post-message, .tweet-text, article p, .status-content",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".post-content",
                        ".message-body",
                        ".tweet-content", 
                        ".status-text",
                        ".post-text"
                    ]
                },
                
                "username": {
                    "selector": "[data-testid='User-Name'], .username, .user-name, .profile-link, .author-name",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".user",
                        ".account-name",
                        ".profile-name",
                        "[data-username]"
                    ]
                },
                
                "user_handle": {
                    "selector": "[data-testid='username'], .handle, .user-handle, .screen-name",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".username",
                        ".twitter-handle",
                        ".account-handle"
                    ]
                },
                
                "user_avatar": {
                    "selector": "[data-testid='Tweet-User-Avatar'] img, .avatar img, .profile-image img, .user-photo img",
                    "type": "attribute",
                    "auto_save": True,
                    "attribute": "src",
                    "fallback_selectors": [
                        ".profile-pic img",
                        ".user-avatar img",
                        ".author-image img"
                    ]
                },
                
                "post_timestamp": {
                    "selector": "[data-testid='Time'] time, time[datetime], .timestamp, .post-time",
                    "type": "text",
                    "auto_save": True,
                    "attribute": "datetime",
                    "fallback_selectors": [
                        ".time",
                        ".date",
                        ".post-date",
                        "[data-time]"
                    ]
                },
                
                "like_count": {
                    "selector": "[data-testid='like'] span, .like-count, .likes-count, .heart-count",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".likes",
                        ".favorite-count",
                        "[data-like-count]"
                    ]
                },
                
                "share_count": {
                    "selector": "[data-testid='retweet'] span, .share-count, .retweet-count, .shares-count",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".retweets",
                        ".shares",
                        "[data-share-count]"
                    ]
                },
                
                "comment_count": {
                    "selector": "[data-testid='reply'] span, .comment-count, .reply-count, .comments-count",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".replies",
                        ".comments",
                        "[data-comment-count]"
                    ]
                },
                
                "post_images": {
                    "selector": "[data-testid='tweetPhoto'] img, .media-container img, .post-image img, .attached-media img",
                    "type": "all",
                    "auto_save": True,
                    "attribute": "src",
                    "fallback_selectors": [
                        ".tweet-media img",
                        ".post-media img",
                        ".image-attachment img"
                    ]
                },
                
                "post_videos": {
                    "selector": "video source, .video-container video, .post-video source",
                    "type": "all",
                    "auto_save": True,
                    "attribute": "src",
                    "fallback_selectors": [
                        ".media-video source",
                        ".tweet-video source"
                    ]
                },
                
                "hashtags": {
                    "selector": "a[href*='hashtag'], .hashtag, [data-query-source='hashtag_click']",
                    "type": "all",
                    "auto_save": True,
                    "fallback_selectors": [
                        "a[href*='#']",
                        ".hash-tag",
                        ".tag-link"
                    ]
                },
                
                "mentions": {
                    "selector": "a[href*='/'], .mention, [data-query-source='user_click']",
                    "type": "all",
                    "auto_save": True,
                    "fallback_selectors": [
                        "a[href*='@']",
                        ".user-mention",
                        ".mention-link"
                    ]
                },
                
                "post_url": {
                    "selector": "[data-testid='Time'] a, .permalink, .post-link, .tweet-link",
                    "type": "attribute",
                    "auto_save": True,
                    "attribute": "href",
                    "fallback_selectors": [
                        ".status-link",
                        ".timestamp a"
                    ]
                },
                
                "verification_badge": {
                    "selector": "[data-testid='verificationBadge'], .verified-badge, .verification-icon",
                    "type": "presence",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".verified",
                        ".blue-checkmark",
                        ".verification"
                    ]
                },
                
                "location": {
                    "selector": ".location, .geo-tag, [data-testid='place']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".place",
                        ".geo-location",
                        ".check-in"
                    ]
                },
                
                "language": {
                    "selector": "[lang], [data-lang]",
                    "type": "attribute",
                    "auto_save": True,
                    "attribute": "lang",
                    "fallback_selectors": [
                        "[data-language]"
                    ]
                }
            },
            
            # Pagination for feed scraping
            "pagination": {
                "enabled": True,
                "next_selector": "[data-testid='primaryColumn'] button, .load-more, .show-more",
                "max_pages": 5,  # Limited for respectful scraping
                "delay_between_pages": [3, 6]  # Longer delays for social media
            },
            
            # Advanced post-processing for social media data
            "post_processing": [
                {
                    "type": "strip",
                    "field": "post_content"
                },
                {
                    "type": "strip",
                    "field": "username"
                },
                {
                    "type": "normalize_handle",
                    "field": "user_handle"
                },
                {
                    "type": "parse_timestamp",
                    "field": "post_timestamp"
                },
                {
                    "type": "extract_number",
                    "field": "like_count"
                },
                {
                    "type": "extract_number",
                    "field": "share_count"
                },
                {
                    "type": "extract_number",
                    "field": "comment_count"
                },
                {
                    "type": "normalize_urls",
                    "field": "post_images"
                },
                {
                    "type": "normalize_urls",
                    "field": "post_videos"
                },
                {
                    "type": "extract_hashtags",
                    "field": "hashtags"
                },
                {
                    "type": "extract_mentions",
                    "field": "mentions"
                },
                {
                    "type": "normalize_urls",
                    "field": "post_url"
                },
                {
                    "type": "strip",
                    "field": "location"
                }
            ],
            
            # Validation rules for social media posts
            "validation_rules": {
                "required_fields": ["post_content"],
                "field_types": {
                    "post_content": "string",
                    "username": "string",
                    "user_handle": "string",
                    "user_avatar": "string",
                    "post_timestamp": "string",
                    "like_count": "number",
                    "share_count": "number",
                    "comment_count": "number",
                    "post_images": "list",
                    "post_videos": "list",
                    "hashtags": "list",
                    "mentions": "list",
                    "post_url": "string",
                    "verification_badge": "boolean",
                    "location": "string",
                    "language": "string"
                },
                "min_lengths": {
                    "post_content": 1
                },
                "max_lengths": {
                    "post_content": 10000  # Platform limits vary
                }
            },
            
            "adaptive_selectors": {
                "enabled": True,
                "learning_mode": True,
                "similarity_threshold": 0.8
            },
            
            "fallback_selectors": {
                "enabled": True,
                "max_attempts": 3
            },
            
            "is_active": True
        }
        
        return template
    
    def extract_hashtags(self, content: str) -> List[str]:
        """
        Extract hashtags from post content.
        
        Args:
            content: Post content text
            
        Returns:
            List of extracted hashtags
        """
        if not content:
            return []
            
        # Find hashtags using regex
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content, re.IGNORECASE)
        
        # Clean and deduplicate
        cleaned_hashtags = []
        seen = set()
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen and len(tag) > 1:
                cleaned_hashtags.append(tag_lower)
                seen.add(tag_lower)
        
        return cleaned_hashtags
    
    def extract_mentions(self, content: str) -> List[str]:
        """
        Extract user mentions from post content.
        
        Args:
            content: Post content text
            
        Returns:
            List of extracted user mentions
        """
        if not content:
            return []
            
        # Find mentions using regex
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, content, re.IGNORECASE)
        
        # Clean and deduplicate
        cleaned_mentions = []
        seen = set()
        for mention in mentions:
            mention_lower = mention.lower()
            if mention_lower not in seen and len(mention) > 1:
                cleaned_mentions.append(mention_lower)
                seen.add(mention_lower)
        
        return cleaned_mentions
    
    def parse_engagement_count(self, count_text: str) -> int:
        """
        Parse engagement count text (e.g., "1.2K", "5M") to integer.
        
        Args:
            count_text: Raw count text from webpage
            
        Returns:
            Parsed count as integer
        """
        if not count_text:
            return 0
            
        # Clean the text
        clean_text = str(count_text).strip().upper()
        
        # Handle abbreviated numbers
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        # Extract number and multiplier
        match = re.search(r'([\d,.]+)([KMB])?', clean_text)
        if match:
            number_str = match.group(1).replace(',', '')
            multiplier_str = match.group(2)
            
            try:
                number = float(number_str)
                if multiplier_str and multiplier_str in multipliers:
                    number *= multipliers[multiplier_str]
                return int(number)
            except ValueError:
                pass
        
        # Try to extract just digits
        digits_only = re.findall(r'\d+', clean_text)
        if digits_only:
            try:
                return int(digits_only[0])
            except ValueError:
                pass
        
        return 0
    
    def analyze_post_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze post content for various metrics and features.
        
        Args:
            content: Post content text
            
        Returns:
            Dictionary containing content analysis
        """
        if not content:
            return {}
        
        # Basic text statistics
        word_count = len(content.split())
        char_count = len(content)
        
        # Extract hashtags and mentions
        hashtags = self.extract_hashtags(content)
        mentions = self.extract_mentions(content)
        
        # Detect URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        
        # Content type analysis
        content_features = {
            "has_hashtags": len(hashtags) > 0,
            "has_mentions": len(mentions) > 0,
            "has_urls": len(urls) > 0,
            "has_emojis": bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)),
            "has_question": '?' in content,
            "has_exclamation": '!' in content,
            "is_long_form": word_count > 50,
            "is_short_form": word_count <= 10
        }
        
        # Sentiment indicators (basic approach)
        positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'happy', 'excellent', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'frustrated', 'disappointed']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "hashtag_count": len(hashtags),
            "mention_count": len(mentions),
            "url_count": len(urls),
            "hashtags": hashtags,
            "mentions": mentions,
            "urls": urls,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "sentiment_score": positive_count - negative_count,
            **content_features
        }
    
    def calculate_engagement_rate(self, likes: int, shares: int, comments: int, 
                                 follower_estimate: int = None) -> float:
        """
        Calculate engagement rate for the post.
        
        Args:
            likes: Number of likes
            shares: Number of shares
            comments: Number of comments
            follower_estimate: Estimated follower count (if available)
            
        Returns:
            Engagement rate as percentage
        """
        total_engagement = likes + shares + comments
        
        if follower_estimate and follower_estimate > 0:
            return (total_engagement / follower_estimate) * 100
        else:
            # Return raw engagement score if no follower data
            return total_engagement
    
    def generate_post_hash(self, content: str, username: str, timestamp: str) -> str:
        """
        Generate unique hash for post deduplication.
        
        Args:
            content: Post content
            username: Username
            timestamp: Post timestamp
            
        Returns:
            SHA-256 hash of post identifiers
        """
        # Create unique identifier from content + user + time
        identifier = f"{content}:{username}:{timestamp}"
        return hashlib.sha256(identifier.encode('utf-8')).hexdigest()[:16]
    
    def validate_social_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enhance social media data.
        
        Args:
            data: Raw scraped social media data
            
        Returns:
            Validated and enhanced social media data
        """
        validated = {}
        
        # Required fields validation
        if not data.get('post_content'):
            raise ValueError("Post content is required")
            
        validated['post_content'] = str(data['post_content']).strip()
        
        # Deduplication check
        username = data.get('username', 'unknown')
        timestamp = data.get('post_timestamp', '')
        post_hash = self.generate_post_hash(validated['post_content'], username, timestamp)
        
        if post_hash in self.scraped_posts:
            raise ValueError("Duplicate post detected")
        self.scraped_posts.add(post_hash)
        validated['post_hash'] = post_hash
        
        # Analyze content
        content_analysis = self.analyze_post_content(validated['post_content'])
        validated.update(content_analysis)
        
        # User information
        if data.get('username'):
            validated['username'] = str(data['username']).strip()
        if data.get('user_handle'):
            handle = str(data['user_handle']).strip()
            # Ensure handle starts with @
            if not handle.startswith('@'):
                handle = '@' + handle
            validated['user_handle'] = handle
        if data.get('user_avatar'):
            validated['user_avatar'] = str(data['user_avatar']).strip()
        
        # Parse timestamp
        if data.get('post_timestamp'):
            try:
                # Try to parse various timestamp formats
                timestamp_str = str(data['post_timestamp'])
                # This would need more sophisticated parsing in production
                validated['post_timestamp'] = timestamp_str
                validated['scraped_age_hours'] = 0  # Placeholder
            except Exception:
                pass
        
        # Engagement metrics
        validated['like_count'] = self.parse_engagement_count(data.get('like_count', '0'))
        validated['share_count'] = self.parse_engagement_count(data.get('share_count', '0'))
        validated['comment_count'] = self.parse_engagement_count(data.get('comment_count', '0'))
        
        # Calculate total engagement
        validated['total_engagement'] = (validated['like_count'] + 
                                       validated['share_count'] + 
                                       validated['comment_count'])
        
        # Calculate engagement score
        validated['engagement_score'] = self.calculate_engagement_rate(
            validated['like_count'],
            validated['share_count'], 
            validated['comment_count']
        )
        
        # Media content
        if data.get('post_images') and isinstance(data['post_images'], list):
            validated['post_images'] = [str(img).strip() for img in data['post_images'] if img]
            validated['image_count'] = len(validated['post_images'])
            validated['has_images'] = len(validated['post_images']) > 0
        else:
            validated['image_count'] = 0
            validated['has_images'] = False
            
        if data.get('post_videos') and isinstance(data['post_videos'], list):
            validated['post_videos'] = [str(vid).strip() for vid in data['post_videos'] if vid]
            validated['video_count'] = len(validated['post_videos'])
            validated['has_videos'] = len(validated['post_videos']) > 0
        else:
            validated['video_count'] = 0
            validated['has_videos'] = False
        
        # Other metadata
        if data.get('post_url'):
            validated['post_url'] = str(data['post_url']).strip()
        if data.get('verification_badge'):
            validated['is_verified'] = True
        else:
            validated['is_verified'] = False
        if data.get('location'):
            validated['location'] = str(data['location']).strip()
        if data.get('language'):
            validated['language'] = str(data['language']).strip()
        
        # Content classification
        validated['content_type'] = self.classify_content_type(validated)
        validated['virality_score'] = self.calculate_virality_score(validated)
        
        # Add metadata
        validated['scraped_at'] = datetime.now(timezone.utc).isoformat()
        validated['data_quality_score'] = self.calculate_social_quality(validated)
        
        return validated
    
    def classify_content_type(self, data: Dict[str, Any]) -> str:
        """
        Classify the type of social media content.
        
        Args:
            data: Validated social media data
            
        Returns:
            Content type classification
        """
        if data.get('has_videos'):
            return "video"
        elif data.get('has_images'):
            return "image"
        elif data.get('has_urls'):
            return "link_share"
        elif data.get('has_question'):
            return "question"
        elif data.get('mention_count', 0) > 0:
            return "conversation"
        elif data.get('hashtag_count', 0) > 3:
            return "promotional"
        elif data.get('word_count', 0) > 100:
            return "long_form"
        else:
            return "text"
    
    def calculate_virality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate virality score based on engagement patterns.
        
        Args:
            data: Validated social media data
            
        Returns:
            Virality score from 0.0 to 10.0
        """
        score = 0.0
        
        # Engagement-based scoring
        total_engagement = data.get('total_engagement', 0)
        if total_engagement > 1000:
            score += 3.0
        elif total_engagement > 100:
            score += 2.0
        elif total_engagement > 10:
            score += 1.0
        
        # Content features that increase virality
        if data.get('has_images') or data.get('has_videos'):
            score += 1.0
        if data.get('hashtag_count', 0) > 0:
            score += 0.5
        if data.get('has_emojis'):
            score += 0.5
        if data.get('has_question'):
            score += 0.5
        if data.get('is_verified'):
            score += 1.0
        
        # Sharing indicates high engagement
        if data.get('share_count', 0) > data.get('like_count', 0) * 0.1:
            score += 2.0
        
        return min(10.0, score)
    
    def calculate_social_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score for social media posts.
        
        Args:
            data: Validated social media data
            
        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 0.0
        
        # Required content (30% of score)
        if data.get('post_content'):
            score += 0.3
        
        # User information (25% of score)
        if data.get('username'):
            score += 0.15
        if data.get('user_handle'):
            score += 0.1
        
        # Engagement data (25% of score)
        if data.get('like_count', 0) > 0:
            score += 0.1
        if data.get('share_count', 0) > 0:
            score += 0.08
        if data.get('comment_count', 0) > 0:
            score += 0.07
        
        # Rich content (10% of score)
        if data.get('has_images') or data.get('has_videos'):
            score += 0.05
        if data.get('hashtag_count', 0) > 0:
            score += 0.05
        
        # Metadata completeness (10% of score)
        if data.get('post_timestamp'):
            score += 0.05
        if data.get('post_url'):
            score += 0.05
        
        return min(1.0, score)
    
    async def scrape_social_urls(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape multiple social media URLs.
        
        Args:
            urls: List of social media URLs to scrape
            **kwargs: Additional configuration options
            
        Returns:
            List of scraped and validated social media data
        """
        logger.info(f"Starting social media scraping of {len(urls)} URLs")
        
        try:
            # Create and save template
            template = self.create_social_template()
            template_result = self.template_service.save_template(template)
            template_id = template_result.get("id")
            
            logger.info(f"Created template with ID: {template_id}")
            
            all_posts = []
            
            for i, url in enumerate(urls):
                logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
                
                try:
                    # Create job configuration with strict rate limiting
                    job_config = {
                        "name": f"Social media scrape: {urlparse(url).netloc}",
                        "template_id": template_id,
                        "target_url": url,
                        "config": {
                            "use_proxy": kwargs.get("use_proxy", True),  # Recommended for social media
                            "stealth_mode": kwargs.get("stealth_mode", "high"),
                            "delay_range": kwargs.get("delay_range", [5, 10]),  # Longer delays
                            "retry_attempts": kwargs.get("retry_attempts", 2),
                            "timeout": kwargs.get("timeout", 45),
                            "enable_anti_bot_detection": True
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
                                validated_data = self.validate_social_data(raw_data)
                                validated_data['source_url'] = url
                                validated_data['job_id'] = job_id
                                all_posts.append(validated_data)
                                logger.info(f"Successfully processed post: {validated_data.get('username', 'Unknown')} - {validated_data.get('post_content', '')[:50]}...")
                            except ValueError as e:
                                logger.warning(f"Data validation failed for {url}: {e}")
                                continue
                    else:
                        logger.error(f"Scraping failed for {url}: {final_status.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")
                    continue
                
                # Respectful delay between URLs (important for social media)
                if i < len(urls) - 1:
                    delay = kwargs.get("batch_delay", 10)
                    logger.info(f"Waiting {delay} seconds before next URL...")
                    await asyncio.sleep(delay)
            
            logger.info(f"Social media scraping completed. Successfully processed {len(all_posts)} posts.")
            return all_posts
            
        except Exception as e:
            logger.error(f"Error during social media scraping: {str(e)}")
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
            
            await asyncio.sleep(3)

async def main():
    """
    Main function demonstrating social media scraping.
    
    This example shows:
    1. Creating a social media scraper
    2. Scraping posts with engagement analysis
    3. Content classification and virality scoring
    4. Hashtag and mention extraction
    5. Respectful rate-limited scraping
    """
    
    scraper = SocialMediaScraper()
    
    # Example social media URLs (replace with actual public URLs)
    # Note: Always check platform terms of service
    social_urls = [
        "https://example-social.com/user/post-123",
        "https://example-social.com/user/post-456",
        "https://example-social.com/user/post-789"
    ]
    
    print(f"\n{'='*60}")
    print("ScraperV4 Social Media Scraping Example")
    print(f"{'='*60}")
    print("⚠️  Note: Always respect platform terms of service")
    print("⚠️  This example is for educational purposes only")
    
    try:
        # Configure scraping options with conservative settings
        scraping_options = {
            "use_proxy": True,  # Recommended for social media
            "stealth_mode": "high",
            "delay_range": [5, 10],  # Longer delays for respectful scraping
            "retry_attempts": 2,
            "timeout": 45,
            "batch_delay": 10  # Wait between posts
        }
        
        # Scrape social media posts
        print(f"\n📱 Scraping {len(social_urls)} social media posts...")
        posts = await scraper.scrape_social_urls(social_urls, **scraping_options)
        
        if posts:
            print(f"\n✅ Successfully scraped {len(posts)} posts!")
            
            # Display results summary
            total_engagement = sum(p.get('total_engagement', 0) for p in posts)
            avg_virality = sum(p.get('virality_score', 0) for p in posts) / len(posts)
            verified_count = sum(1 for p in posts if p.get('is_verified'))
            
            print(f"\n📊 Scraping Summary:")
            print(f"   Total Posts: {len(posts)}")
            print(f"   Total Engagement: {total_engagement:,}")
            print(f"   Average Virality Score: {avg_virality:.1f}/10.0")
            print(f"   Verified Users: {verified_count}/{len(posts)}")
            
            # Content type analysis
            content_types = {}
            for post in posts:
                ctype = post.get('content_type', 'unknown')
                content_types[ctype] = content_types.get(ctype, 0) + 1
            
            print(f"   Content Types: {dict(content_types)}")
            
            # Show sample posts
            print(f"\n📄 Sample Posts:")
            for i, post in enumerate(posts[:2]):
                print(f"\n   Post {i+1}:")
                print(f"   👤 @{post.get('user_handle', 'unknown').replace('@', '')}")
                if post.get('is_verified'):
                    print(f"   ✅ Verified User")
                content_preview = post.get('post_content', '')[:100]
                if len(post.get('post_content', '')) > 100:
                    content_preview += '...'
                print(f"   💬 \"{content_preview}\"")
                print(f"   📈 {post.get('like_count', 0):,} likes, {post.get('share_count', 0):,} shares, {post.get('comment_count', 0):,} comments")
                print(f"   🔥 Virality Score: {post.get('virality_score', 0):.1f}/10.0")
                print(f"   📊 Quality Score: {post.get('data_quality_score', 0):.1%}")
                if post.get('hashtags'):
                    print(f"   🏷️  Hashtags: {', '.join(['#' + tag for tag in post.get('hashtags', [])[:5]])}")
                if post.get('has_images'):
                    print(f"   🖼️  {post.get('image_count', 0)} images")
                if post.get('has_videos'):
                    print(f"   🎥 {post.get('video_count', 0)} videos")
            
            # Hashtag analysis
            all_hashtags = {}
            for post in posts:
                for hashtag in post.get('hashtags', []):
                    all_hashtags[hashtag] = all_hashtags.get(hashtag, 0) + 1
            
            if all_hashtags:
                top_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)[:10]
                print(f"\n📈 Trending Hashtags:")
                for hashtag, count in top_hashtags[:5]:
                    print(f"   #{hashtag}: {count} posts")
            
        else:
            print("❌ No posts were successfully scraped")
            
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    asyncio.run(main())