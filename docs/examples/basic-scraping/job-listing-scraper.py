#!/usr/bin/env python3
"""
Job Listing Scraper Example

This example demonstrates scraping job listings from employment websites with
comprehensive data extraction, salary parsing, and skill analysis.

Features demonstrated:
- Job title and description extraction
- Company information and requirements
- Salary range parsing and normalization
- Location and work type classification
- Skill extraction and categorization
- Application deadline tracking
- Job market analysis capabilities

Prerequisites:
- ScraperV4 installed and configured
- Understanding of job board website structures
- Optional: natural language processing for skill extraction

Usage:
    python job-listing-scraper.py

Expected Output:
- Structured job listing data
- Salary analysis and market insights
- Skill demand tracking
- Export formats suitable for job market research
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlparse
from decimal import Decimal, InvalidOperation

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from services.scraping_service import ScrapingService
from services.template_service import TemplateService
from services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobListingScraper:
    """Job listing scraper with market analysis capabilities."""
    
    def __init__(self):
        """Initialize the scraper with required services."""
        self.scraping_service = ScrapingService()
        self.template_service = TemplateService()
        self.data_service = DataService()
        self.scraped_jobs = set()  # For deduplication
        
        # Common tech skills for extraction
        self.tech_skills = {
            'programming_languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'scala', 'r'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails', 'tensorflow', 'pytorch'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server', 'cassandra', 'dynamodb'],
            'cloud_platforms': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'kubernetes', 'docker'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack', 'figma', 'photoshop', 'tableau', 'power bi']
        }
        
    def create_job_template(self) -> Dict[str, Any]:
        """
        Create a comprehensive job listing scraping template.
        
        This template demonstrates:
        - Job title and company information
        - Detailed job descriptions and requirements
        - Salary ranges and compensation details
        - Location and work arrangement info
        - Application deadlines and processes
        - Company culture and benefits
        
        Returns:
            Dict containing the template configuration
        """
        template = {
            "name": "job_listing_scraper",
            "description": "Comprehensive template for scraping job listings",
            "version": "2.0.0",
            
            # Standard fetcher configuration for job boards
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
            
            # Comprehensive job listing selectors
            "selectors": {
                "job_title": {
                    "selector": "h1.job-title, h1.jobsearch-JobInfoHeader-title, .job-header h1, [data-testid='job-title']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        "h1",
                        ".title",
                        ".job-name",
                        ".position-title",
                        "#job-title"
                    ]
                },
                
                "company_name": {
                    "selector": ".company-name, [data-testid='company-name'], .employer-name, .hiring-company",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".company",
                        ".employer",
                        ".organization",
                        "[itemprop='hiringOrganization']"
                    ]
                },
                
                "location": {
                    "selector": ".job-location, [data-testid='job-location'], .location, .workplace-location",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".address",
                        ".city",
                        ".geographic-location",
                        "[itemprop='jobLocation']"
                    ]
                },
                
                "salary_range": {
                    "selector": ".salary-range, .compensation, .pay-range, [data-testid='salary']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".salary",
                        ".wage",
                        ".compensation-info",
                        ".pay-info"
                    ]
                },
                
                "job_description": {
                    "selector": ".job-description, .job-details, .description, .job-summary",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".content",
                        ".details",
                        ".job-content",
                        "#job-description"
                    ]
                },
                
                "requirements": {
                    "selector": ".requirements, .qualifications, .job-requirements, .skills-required",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".qualifications-section",
                        ".requirements-section",
                        ".skills-section"
                    ]
                },
                
                "experience_level": {
                    "selector": ".experience-level, .seniority-level, .job-level, [data-testid='experience']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".level",
                        ".seniority",
                        ".experience"
                    ]
                },
                
                "employment_type": {
                    "selector": ".employment-type, .job-type, .work-type, [data-testid='employment-type']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".type",
                        ".schedule",
                        ".work-arrangement"
                    ]
                },
                
                "remote_option": {
                    "selector": ".remote-option, .work-from-home, .remote-work, [data-testid='remote']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".remote",
                        ".wfh",
                        ".telecommute"
                    ]
                },
                
                "posted_date": {
                    "selector": ".posted-date, .publish-date, .job-date, time[datetime]",
                    "type": "text",
                    "auto_save": True,
                    "attribute": "datetime",
                    "fallback_selectors": [
                        ".date",
                        ".published",
                        ".time-posted"
                    ]
                },
                
                "application_deadline": {
                    "selector": ".deadline, .application-deadline, .expires, .closing-date",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".expiry",
                        ".close-date",
                        ".application-close"
                    ]
                },
                
                "benefits": {
                    "selector": ".benefits, .perks, .job-benefits, .compensation-benefits",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".perks-section",
                        ".benefits-section",
                        ".additional-compensation"
                    ]
                },
                
                "company_size": {
                    "selector": ".company-size, .organization-size, .team-size, [data-testid='company-size']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".size",
                        ".employees",
                        ".company-info .size"
                    ]
                },
                
                "industry": {
                    "selector": ".industry, .sector, .company-industry, [data-testid='industry']",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".field",
                        ".domain",
                        ".business-area"
                    ]
                },
                
                "application_url": {
                    "selector": ".apply-button, .application-link, .apply-link, [data-testid='apply']",
                    "type": "attribute",
                    "auto_save": True,
                    "attribute": "href",
                    "fallback_selectors": [
                        ".apply a",
                        ".application a",
                        ".job-apply a"
                    ]
                },
                
                "job_id": {
                    "selector": ".job-id, .listing-id, [data-job-id], [data-listing-id]",
                    "type": "text",
                    "auto_save": True,
                    "attribute": "data-job-id",
                    "fallback_selectors": [
                        "[data-id]",
                        ".id",
                        ".reference"
                    ]
                }
            },
            
            # Pagination for job search results
            "pagination": {
                "enabled": True,
                "next_selector": ".next-page, .pagination-next, [aria-label='Next']",
                "max_pages": 10,
                "delay_between_pages": [2, 4]
            },
            
            # Advanced post-processing for job data
            "post_processing": [
                {
                    "type": "strip",
                    "field": "job_title"
                },
                {
                    "type": "strip",
                    "field": "company_name"
                },
                {
                    "type": "strip",
                    "field": "location"
                },
                {
                    "type": "parse_salary",
                    "field": "salary_range"
                },
                {
                    "type": "clean_content",
                    "field": "job_description"
                },
                {
                    "type": "clean_content",
                    "field": "requirements"
                },
                {
                    "type": "normalize_experience",
                    "field": "experience_level"
                },
                {
                    "type": "normalize_employment",
                    "field": "employment_type"
                },
                {
                    "type": "parse_date",
                    "field": "posted_date"
                },
                {
                    "type": "parse_date",
                    "field": "application_deadline"
                },
                {
                    "type": "strip",
                    "field": "benefits"
                },
                {
                    "type": "strip",
                    "field": "industry"
                },
                {
                    "type": "normalize_urls",
                    "field": "application_url"
                }
            ],
            
            # Validation rules for job listings
            "validation_rules": {
                "required_fields": ["job_title", "company_name"],
                "field_types": {
                    "job_title": "string",
                    "company_name": "string",
                    "location": "string",
                    "salary_range": "string",
                    "job_description": "string",
                    "requirements": "string",
                    "experience_level": "string",
                    "employment_type": "string",
                    "remote_option": "string",
                    "posted_date": "string",
                    "application_deadline": "string",
                    "benefits": "string",
                    "company_size": "string",
                    "industry": "string",
                    "application_url": "string",
                    "job_id": "string"
                },
                "min_lengths": {
                    "job_title": 5,
                    "company_name": 2
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
    
    def parse_salary_range(self, salary_text: str) -> Dict[str, Any]:
        """
        Parse salary range from text with various formats.
        
        Args:
            salary_text: Raw salary text from job listing
            
        Returns:
            Dictionary containing parsed salary information
        """
        if not salary_text:
            return {}
        
        # Clean the text
        clean_text = salary_text.strip().replace(',', '').replace('$', '')
        
        # Common salary patterns
        patterns = [
            r'(\d+)k?\s*-\s*(\d+)k?\s*(per\s+year|annually|yearly)?',  # 50k - 80k
            r'(\d+)\s*-\s*(\d+)\s*(per\s+year|annually|yearly)?',      # 50000 - 80000
            r'(\d+)k?\s*to\s*(\d+)k?\s*(per\s+year|annually|yearly)?', # 50k to 80k
            r'up\s*to\s*(\d+)k?\s*(per\s+year|annually|yearly)?',      # up to 80k
            r'from\s*(\d+)k?\s*(per\s+year|annually|yearly)?',         # from 50k
            r'(\d+)k?\s*\+?\s*(per\s+year|annually|yearly)?'           # 60k+
        ]
        
        result = {
            'original_text': salary_text,
            'min_salary': None,
            'max_salary': None,
            'currency': 'USD',
            'period': 'yearly',
            'is_range': False
        }
        
        # Detect currency
        if '€' in salary_text or 'EUR' in salary_text.upper():
            result['currency'] = 'EUR'
        elif '£' in salary_text or 'GBP' in salary_text.upper():
            result['currency'] = 'GBP'
        
        # Detect time period
        if any(word in salary_text.lower() for word in ['hourly', 'per hour', '/hr', 'hour']):
            result['period'] = 'hourly'
        elif any(word in salary_text.lower() for word in ['monthly', 'per month', '/month', 'month']):
            result['period'] = 'monthly'
        
        for pattern in patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) >= 2 and match.group(2):
                        # Range pattern
                        min_val = int(match.group(1))
                        max_val = int(match.group(2))
                        
                        # Handle 'k' suffix
                        if 'k' in match.group(0).lower():
                            min_val *= 1000
                            max_val *= 1000
                        
                        result['min_salary'] = min_val
                        result['max_salary'] = max_val
                        result['is_range'] = True
                        break
                    else:
                        # Single value pattern
                        val = int(match.group(1))
                        if 'k' in match.group(0).lower():
                            val *= 1000
                        
                        if 'up to' in match.group(0).lower():
                            result['max_salary'] = val
                        elif 'from' in match.group(0).lower():
                            result['min_salary'] = val
                        else:
                            result['min_salary'] = val
                            result['max_salary'] = val
                        break
                except (ValueError, IndexError):
                    continue
        
        # Calculate average if range
        if result['min_salary'] and result['max_salary']:
            result['avg_salary'] = (result['min_salary'] + result['max_salary']) / 2
        elif result['min_salary']:
            result['avg_salary'] = result['min_salary']
        elif result['max_salary']:
            result['avg_salary'] = result['max_salary']
        
        return result
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technical skills from job description or requirements.
        
        Args:
            text: Job description or requirements text
            
        Returns:
            Dictionary of categorized skills found
        """
        if not text:
            return {}
        
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.tech_skills.items():
            found_in_category = []
            for skill in skills:
                # Look for whole word matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_in_category.append(skill)
            
            if found_in_category:
                found_skills[category] = found_in_category
        
        return found_skills
    
    def classify_experience_level(self, text: str) -> str:
        """
        Classify experience level from text.
        
        Args:
            text: Experience level text
            
        Returns:
            Standardized experience level
        """
        if not text:
            return "not_specified"
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['entry', 'junior', 'intern', 'graduate', 'fresh', 'new grad']):
            return "entry_level"
        elif any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect', 'expert']):
            return "senior_level"
        elif any(word in text_lower for word in ['mid', 'intermediate', 'experienced', '3-5', '2-4']):
            return "mid_level"
        elif any(word in text_lower for word in ['director', 'manager', 'head', 'vp', 'chief']):
            return "management"
        else:
            return "not_specified"
    
    def classify_employment_type(self, text: str) -> str:
        """
        Classify employment type from text.
        
        Args:
            text: Employment type text
            
        Returns:
            Standardized employment type
        """
        if not text:
            return "not_specified"
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['full-time', 'full time', 'fulltime', 'permanent']):
            return "full_time"
        elif any(word in text_lower for word in ['part-time', 'part time', 'parttime']):
            return "part_time"
        elif any(word in text_lower for word in ['contract', 'contractor', 'freelance', 'consulting']):
            return "contract"
        elif any(word in text_lower for word in ['intern', 'internship', 'co-op']):
            return "internship"
        elif any(word in text_lower for word in ['temporary', 'temp', 'seasonal']):
            return "temporary"
        else:
            return "not_specified"
    
    def analyze_remote_work(self, location_text: str, remote_text: str, description: str) -> Dict[str, Any]:
        """
        Analyze remote work options from various text sources.
        
        Args:
            location_text: Location field text
            remote_text: Remote option field text
            description: Job description text
            
        Returns:
            Dictionary containing remote work analysis
        """
        combined_text = f"{location_text} {remote_text} {description}".lower()
        
        remote_indicators = {
            'fully_remote': ['fully remote', 'completely remote', '100% remote', 'remote only'],
            'hybrid': ['hybrid', 'flexible', 'remote/office', 'office/remote'],
            'remote_friendly': ['remote friendly', 'remote option', 'work from home option'],
            'no_remote': ['on-site', 'onsite', 'office only', 'no remote']
        }
        
        result = {
            'remote_type': 'not_specified',
            'remote_friendly': False,
            'location_flexibility': 'not_specified'
        }
        
        for remote_type, indicators in remote_indicators.items():
            if any(indicator in combined_text for indicator in indicators):
                result['remote_type'] = remote_type
                result['remote_friendly'] = remote_type != 'no_remote'
                break
        
        # Check for location flexibility
        if any(word in combined_text for word in ['anywhere', 'any location', 'location independent']):
            result['location_flexibility'] = 'anywhere'
        elif any(word in combined_text for word in ['us only', 'usa only', 'united states']):
            result['location_flexibility'] = 'country_restricted'
        elif any(word in combined_text for word in ['time zone', 'timezone', 'pst', 'est', 'cst']):
            result['location_flexibility'] = 'timezone_restricted'
        
        return result
    
    def calculate_job_attractiveness(self, data: Dict[str, Any]) -> float:
        """
        Calculate job attractiveness score based on various factors.
        
        Args:
            data: Validated job data
            
        Returns:
            Attractiveness score from 0.0 to 10.0
        """
        score = 5.0  # Base score
        
        # Salary considerations
        if data.get('salary_info', {}).get('avg_salary'):
            avg_salary = data['salary_info']['avg_salary']
            if avg_salary > 100000:
                score += 2.0
            elif avg_salary > 70000:
                score += 1.0
            elif avg_salary < 40000:
                score -= 1.0
        
        # Remote work options
        remote_info = data.get('remote_analysis', {})
        if remote_info.get('remote_type') == 'fully_remote':
            score += 1.5
        elif remote_info.get('remote_type') == 'hybrid':
            score += 1.0
        elif remote_info.get('remote_type') == 'no_remote':
            score -= 0.5
        
        # Company and role factors
        if data.get('experience_level_normalized') == 'senior_level':
            score += 0.5
        elif data.get('experience_level_normalized') == 'management':
            score += 1.0
        
        # Benefits and perks
        if data.get('benefits') and len(data['benefits']) > 100:
            score += 0.5
        
        # Job market timing
        if data.get('days_since_posted', 0) < 7:
            score += 0.5  # Fresh posting
        elif data.get('days_since_posted', 0) > 30:
            score -= 0.5  # Old posting
        
        # Skills demand
        skills_count = sum(len(skills) for skills in data.get('extracted_skills', {}).values())
        if skills_count > 10:
            score += 1.0
        elif skills_count > 5:
            score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def validate_job_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enhance job listing data.
        
        Args:
            data: Raw scraped job data
            
        Returns:
            Validated and enhanced job data
        """
        validated = {}
        
        # Required fields validation
        if not data.get('job_title'):
            raise ValueError("Job title is required")
        if not data.get('company_name'):
            raise ValueError("Company name is required")
            
        validated['job_title'] = str(data['job_title']).strip()
        validated['company_name'] = str(data['company_name']).strip()
        
        # Create job identifier for deduplication
        job_id = f"{validated['job_title']}:{validated['company_name']}".lower()
        job_hash = hashlib.sha256(job_id.encode('utf-8')).hexdigest()[:16]
        
        if job_hash in self.scraped_jobs:
            raise ValueError("Duplicate job listing detected")
        self.scraped_jobs.add(job_hash)
        validated['job_hash'] = job_hash
        
        # Basic information
        if data.get('location'):
            validated['location'] = str(data['location']).strip()
        
        # Salary parsing
        if data.get('salary_range'):
            salary_info = self.parse_salary_range(str(data['salary_range']))
            validated['salary_info'] = salary_info
            validated['salary_range_original'] = str(data['salary_range']).strip()
        
        # Text content
        for field in ['job_description', 'requirements', 'benefits']:
            if data.get(field):
                validated[field] = str(data[field]).strip()
        
        # Experience and employment classification
        validated['experience_level_original'] = data.get('experience_level', '')
        validated['experience_level_normalized'] = self.classify_experience_level(data.get('experience_level', ''))
        
        validated['employment_type_original'] = data.get('employment_type', '')
        validated['employment_type_normalized'] = self.classify_employment_type(data.get('employment_type', ''))
        
        # Remote work analysis
        remote_analysis = self.analyze_remote_work(
            data.get('location', ''),
            data.get('remote_option', ''),
            data.get('job_description', '')
        )
        validated['remote_analysis'] = remote_analysis
        
        # Skills extraction
        description_text = f"{data.get('job_description', '')} {data.get('requirements', '')}"
        extracted_skills = self.extract_skills(description_text)
        validated['extracted_skills'] = extracted_skills
        validated['total_skills_count'] = sum(len(skills) for skills in extracted_skills.values())
        
        # Date processing
        if data.get('posted_date'):
            # This would need proper date parsing in production
            validated['posted_date'] = str(data['posted_date']).strip()
            # Calculate days since posted (placeholder)
            validated['days_since_posted'] = 0
        
        if data.get('application_deadline'):
            validated['application_deadline'] = str(data['application_deadline']).strip()
        
        # Company information
        for field in ['company_size', 'industry']:
            if data.get(field):
                validated[field] = str(data[field]).strip()
        
        # Application information
        if data.get('application_url'):
            validated['application_url'] = str(data['application_url']).strip()
        if data.get('job_id'):
            validated['external_job_id'] = str(data['job_id']).strip()
        
        # Calculate metrics
        validated['attractiveness_score'] = self.calculate_job_attractiveness(validated)
        validated['content_quality_score'] = self.calculate_job_quality(validated)
        
        # Add metadata
        validated['scraped_at'] = datetime.now(timezone.utc).isoformat()
        
        return validated
    
    def calculate_job_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score for job listings.
        
        Args:
            data: Validated job data
            
        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 0.0
        
        # Required fields (40% of score)
        if data.get('job_title'):
            score += 0.2
        if data.get('company_name'):
            score += 0.2
        
        # Important details (30% of score)
        if data.get('job_description') and len(data['job_description']) > 100:
            score += 0.1
        if data.get('location'):
            score += 0.05
        if data.get('salary_info', {}).get('avg_salary'):
            score += 0.1
        if data.get('employment_type_normalized') != 'not_specified':
            score += 0.05
        
        # Additional information (20% of score)
        if data.get('requirements'):
            score += 0.05
        if data.get('benefits'):
            score += 0.05
        if data.get('experience_level_normalized') != 'not_specified':
            score += 0.05
        if data.get('industry'):
            score += 0.05
        
        # Rich data (10% of score)
        if data.get('total_skills_count', 0) > 5:
            score += 0.05
        if data.get('application_url'):
            score += 0.05
        
        return min(1.0, score)
    
    async def scrape_job_urls(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape multiple job listing URLs.
        
        Args:
            urls: List of job listing URLs to scrape
            **kwargs: Additional configuration options
            
        Returns:
            List of scraped and validated job data
        """
        logger.info(f"Starting job listing scraping of {len(urls)} URLs")
        
        try:
            # Create and save template
            template = self.create_job_template()
            template_result = self.template_service.save_template(template)
            template_id = template_result.get("id")
            
            logger.info(f"Created template with ID: {template_id}")
            
            all_jobs = []
            
            for i, url in enumerate(urls):
                logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
                
                try:
                    # Create job configuration
                    job_config = {
                        "name": f"Job listing scrape: {urlparse(url).netloc}",
                        "template_id": template_id,
                        "target_url": url,
                        "config": {
                            "use_proxy": kwargs.get("use_proxy", False),
                            "stealth_mode": kwargs.get("stealth_mode", "off"),
                            "delay_range": kwargs.get("delay_range", [2, 4]),
                            "retry_attempts": kwargs.get("retry_attempts", 3),
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
                                validated_data = self.validate_job_data(raw_data)
                                validated_data['source_url'] = url
                                validated_data['job_id'] = job_id
                                all_jobs.append(validated_data)
                                logger.info(f"Successfully processed job: {validated_data.get('job_title', 'Unknown')} at {validated_data.get('company_name', 'Unknown')}")
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
                    delay = kwargs.get("batch_delay", 3)
                    logger.info(f"Waiting {delay} seconds before next URL...")
                    await asyncio.sleep(delay)
            
            logger.info(f"Job listing scraping completed. Successfully processed {len(all_jobs)} jobs.")
            return all_jobs
            
        except Exception as e:
            logger.error(f"Error during job listing scraping: {str(e)}")
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
    Main function demonstrating job listing scraping.
    
    This example shows:
    1. Creating a job listing scraper
    2. Scraping jobs with comprehensive analysis
    3. Salary parsing and skill extraction
    4. Remote work classification
    5. Job market insights generation
    """
    
    scraper = JobListingScraper()
    
    # Example job listing URLs (replace with actual job board URLs)
    job_urls = [
        "https://example-jobs.com/software-engineer-123",
        "https://example-jobs.com/data-scientist-456", 
        "https://example-jobs.com/product-manager-789"
    ]
    
    print(f"\n{'='*60}")
    print("ScraperV4 Job Listing Scraping Example")
    print(f"{'='*60}")
    
    try:
        # Configure scraping options
        scraping_options = {
            "use_proxy": False,
            "stealth_mode": "off",
            "delay_range": [2, 4],
            "retry_attempts": 3,
            "timeout": 60,
            "batch_delay": 3
        }
        
        # Scrape job listings
        print(f"\n💼 Scraping {len(job_urls)} job listings...")
        jobs = await scraper.scrape_job_urls(job_urls, **scraping_options)
        
        if jobs:
            print(f"\n✅ Successfully scraped {len(jobs)} job listings!")
            
            # Calculate market insights
            total_jobs = len(jobs)
            remote_jobs = sum(1 for j in jobs if j.get('remote_analysis', {}).get('remote_friendly'))
            avg_attractiveness = sum(j.get('attractiveness_score', 0) for j in jobs) / total_jobs
            
            # Salary analysis
            salaries = [j.get('salary_info', {}).get('avg_salary') for j in jobs if j.get('salary_info', {}).get('avg_salary')]
            avg_salary = sum(salaries) / len(salaries) if salaries else 0
            
            print(f"\n📊 Job Market Analysis:")
            print(f"   Total Jobs: {total_jobs}")
            print(f"   Remote-Friendly: {remote_jobs}/{total_jobs} ({remote_jobs/total_jobs*100:.1f}%)")
            print(f"   Average Attractiveness: {avg_attractiveness:.1f}/10.0")
            if avg_salary > 0:
                print(f"   Average Salary: ${avg_salary:,.0f}")
            
            # Experience level distribution
            exp_levels = {}
            for job in jobs:
                level = job.get('experience_level_normalized', 'not_specified')
                exp_levels[level] = exp_levels.get(level, 0) + 1
            print(f"   Experience Levels: {dict(exp_levels)}")
            
            # Skills analysis
            all_skills = {}
            for job in jobs:
                for category, skills in job.get('extracted_skills', {}).items():
                    for skill in skills:
                        all_skills[skill] = all_skills.get(skill, 0) + 1
            
            top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"   Top Skills: {[skill[0] for skill in top_skills[:5]]}")
            
            # Show sample jobs
            print(f"\n📄 Sample Job Listings:")
            for i, job in enumerate(jobs[:2]):
                print(f"\n   Job {i+1}:")
                print(f"   🏢 {job.get('job_title', 'Unknown')} at {job.get('company_name', 'Unknown')}")
                print(f"   📍 {job.get('location', 'Location not specified')}")
                
                salary_info = job.get('salary_info', {})
                if salary_info.get('avg_salary'):
                    print(f"   💰 ${salary_info['avg_salary']:,.0f}/year")
                elif salary_info.get('original_text'):
                    print(f"   💰 {salary_info['original_text']}")
                
                remote_type = job.get('remote_analysis', {}).get('remote_type', 'not_specified')
                print(f"   🏠 Remote: {remote_type.replace('_', ' ').title()}")
                
                exp_level = job.get('experience_level_normalized', 'not_specified')
                print(f"   📈 Level: {exp_level.replace('_', ' ').title()}")
                
                print(f"   ⭐ Attractiveness: {job.get('attractiveness_score', 0):.1f}/10.0")
                print(f"   📊 Quality Score: {job.get('content_quality_score', 0):.1%}")
                
                # Show top skills for this job
                job_skills = []
                for skills_list in job.get('extracted_skills', {}).values():
                    job_skills.extend(skills_list)
                if job_skills:
                    print(f"   🛠️  Skills: {', '.join(job_skills[:5])}")
            
        else:
            print("❌ No job listings were successfully scraped")
            
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    asyncio.run(main())