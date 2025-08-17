# Phase 2: Core Backend Development - ScraperV4 Business Logic

## Objective
Implement the complete backend business logic for ScraperV4, including service layer implementations, Scrapling integration with StealthyFetcher, database operations, template processing, and data management. Build a robust, scalable backend that supports concurrent scraping operations with comprehensive error handling and monitoring.

## Context
Building upon the Eel application architecture from Phase 1C, this phase implements:
- **Service Layer**: Complete business logic implementations for all core services
- **Scrapling Integration**: Advanced web scraping with StealthyFetcher and adaptive selectors
- **Template Processing**: Self-healing scraper templates with fallback mechanisms
- **File Operations**: JSON-based data persistence with file locking and atomic writes
- **Async Operations**: Background job processing with progress tracking
- **Data Export**: Multi-format data export with pandas integration
- **Error Handling**: Comprehensive exception handling and logging

## Architecture Overview
```
Backend Services:
├── ScrapingService     # Core scraping operations and job management
├── TemplateService     # Template CRUD and validation
├── DataService         # Data processing and export operations
├── ValidationService   # URL and selector validation
└── BackgroundService   # Async job processing and monitoring

Scrapling Integration:
├── TemplateScraper     # Template-based scraping with Scrapling
├── StealthFetcher      # Anti-detection scraping capabilities
├── AdaptiveSelector    # Self-healing selector management
└── ResultProcessor     # Data cleaning and validation
```

## Implementation Steps

### 1. Core Scraping Service Implementation

Create `src/services/scraping_service.py`:
```python
"""Core scraping service with job management and Scrapling integration."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, AsyncGenerator
from src.services.base_service import BaseService
from src.scrapers.template_scraper import TemplateScraper
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class ScrapingService(BaseService):
    """Service for managing scraping operations and jobs."""
    
    def __init__(self):
        super().__init__()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.job_progress: Dict[str, Dict[str, Any]] = {}
    
    def create_job(self, name: str, template_name: str, target_url: str,
                   config: Optional[Dict[str, Any]] = None,
                   parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new scraping job."""
        try:
            # Validate template exists
            if not self.template_manager.template_exists(template_name):
                raise ValueError(f"Template '{template_name}' not found")
            
            # Create job using JobManager
            job = self.job_manager.create_job(
                name=name,
                template_name=template_name,
                target_url=target_url,
                job_config=config,
                parameters=parameters
            )
            
            logger.info(f"Created scraping job {job['id']}: {name}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to create scraping job: {e}")
            raise
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get scraping job by ID."""
        return self.job_manager.get_job(job_id)
    
    def get_jobs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get scraping jobs with optional filtering."""
        return self.job_manager.list_jobs(status=status)
    
    async def execute_job_async(self, job_id: str) -> None:
        """Execute scraping job asynchronously."""
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Check if job is already running
        if job_id in self.active_jobs:
            logger.warning(f"Job {job_id} is already running")
            return
        
        try:
            # Mark job as started
            self.job_manager.update_job(job_id, {
                "status": "running",
                "started_at": datetime.utcnow().isoformat()
            })
            
            # Initialize progress tracking
            self.job_progress[job_id] = {
                "status": "running",
                "progress": 0,
                "items_scraped": 0,
                "items_failed": 0,
                "start_time": time.time()
            }
            
            # Get template
            template = self.template_manager.load_template(job["template_name"])
            if not template:
                raise ValueError(f"Template {job['template_name']} not found")
            
            # Create scraper instance
            scraper = TemplateScraper(template)
            
            # Execute scraping
            await self._execute_scraping_operation(job, scraper)
            
            # Mark job as completed
            self.job_manager.update_job(job_id, {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "items_scraped": self.job_progress[job_id]["items_scraped"],
                "items_failed": self.job_progress[job_id]["items_failed"]
            })
            
            logger.info(f"Completed scraping job {job_id}")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            
            # Mark job as failed
            self.job_manager.update_job(job_id, {
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error_message": str(e),
                "items_scraped": self.job_progress.get(job_id, {}).get("items_scraped", 0),
                "items_failed": self.job_progress.get(job_id, {}).get("items_failed", 0)
            })
            
        finally:
            # Clean up
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            if job_id in self.job_progress:
                del self.job_progress[job_id]
    
    async def _execute_scraping_operation(self, job: ScrapingJob, scraper: TemplateScraper) -> None:
        """Execute the actual scraping operation."""
        try:
            # Determine URLs to scrape
            urls_to_scrape = await self._get_urls_to_scrape(job)
            total_urls = len(urls_to_scrape)
            
            if total_urls == 0:
                logger.warning(f"No URLs to scrape for job {job.id}")
                return
            
            logger.info(f"Scraping {total_urls} URLs for job {job.id}")
            
            # Process URLs in batches
            batch_size = job.config.get('batch_size', 10)
            concurrent_limit = job.config.get('concurrent_limit', 3)
            
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            for i in range(0, total_urls, batch_size):
                batch_urls = urls_to_scrape[i:i + batch_size]
                
                # Process batch concurrently
                tasks = [
                    self._scrape_url_with_semaphore(semaphore, job, scraper, url, i + j, total_urls)
                    for j, url in enumerate(batch_urls)
                ]
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update progress
                progress = min(100, int(((i + len(batch_urls)) / total_urls) * 100))
                self.job_progress[job.id]["progress"] = progress
                
                # Add delay between batches
                if i + batch_size < total_urls:
                    delay = job.config.get('batch_delay', 2)
                    await asyncio.sleep(delay)
                    
        except Exception as e:
            logger.error(f"Scraping operation failed for job {job.id}: {e}")
            raise
    
    async def _scrape_url_with_semaphore(self, semaphore: asyncio.Semaphore,
                                       job: ScrapingJob, scraper: TemplateScraper,
                                       url: str, index: int, total: int) -> None:
        """Scrape a single URL with concurrency control."""
        async with semaphore:
            try:
                # Scrape the URL
                result_data = await scraper.scrape_async(url)
                
                if result_data and result_data.get('status') == 'success':
                    # Save successful result
                    await self._save_scraping_result(job.id, url, result_data)
                    self.job_progress[job.id]["items_scraped"] += 1
                    
                    logger.debug(f"Scraped {index + 1}/{total}: {url}")
                else:
                    # Handle failed scraping
                    error_msg = result_data.get('error', 'Unknown error') if result_data else 'No data returned'
                    await self._save_failed_result(job.id, url, error_msg)
                    self.job_progress[job.id]["items_failed"] += 1
                    
                    logger.warning(f"Failed to scrape {index + 1}/{total}: {url} - {error_msg}")
                    
            except Exception as e:
                logger.error(f"Exception scraping {url}: {e}")
                await self._save_failed_result(job.id, url, str(e))
                self.job_progress[job.id]["items_failed"] += 1
    
    async def _get_urls_to_scrape(self, job: ScrapingJob) -> List[str]:
        """Get list of URLs to scrape based on job configuration."""
        target_url = job.target_url
        
        # For now, just return the target URL
        # In future, this could handle sitemaps, pagination, etc.
        urls = [target_url]
        
        # Handle URL patterns or lists if provided in parameters
        if 'url_list' in job.parameters:
            urls.extend(job.parameters['url_list'])
        
        if 'url_pattern' in job.parameters:
            # Handle URL pattern generation
            pattern = job.parameters['url_pattern']
            start = job.parameters.get('start_page', 1)
            end = job.parameters.get('end_page', 10)
            
            for page in range(start, end + 1):
                url = pattern.format(page=page)
                urls.append(url)
        
        return list(set(urls))  # Remove duplicates
    
    async def _save_scraping_result(self, job_id: int, url: str, result_data: Dict[str, Any]) -> None:
        """Save successful scraping result to database."""
        try:
            result = ScrapingResult(
                job_id=job_id,
                source_url=url,
                page_title=result_data.get('page_title'),
                data=result_data.get('data', {}),
                raw_html=result_data.get('raw_html'),
                processing_time=result_data.get('processing_time'),
                status='success'
            )
            
            self.db.add(result)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save scraping result: {e}")
            self.db.rollback()
    
    async def _save_failed_result(self, job_id: int, url: str, error_message: str) -> None:
        """Save failed scraping attempt to database."""
        try:
            result = ScrapingResult(
                job_id=job_id,
                source_url=url,
                data={},
                status='failed',
                validation_errors=[{"error": error_message}]
            )
            
            self.db.add(result)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save failed result: {e}")
            self.db.rollback()
    
    def stop_job(self, job_id: int) -> bool:
        """Stop a running scraping job."""
        if job_id in self.active_jobs:
            task = self.active_jobs[job_id]
            task.cancel()
            
            # Update job status
            job = self.get_job(job_id)
            if job:
                job.status = "stopped"
                job.completed_at = datetime.utcnow()
                self.db.commit()
            
            logger.info(f"Stopped scraping job {job_id}")
            return True
        
        return False
    
    def get_job_progress(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get real-time progress for a job."""
        return self.job_progress.get(job_id)
    
    async def preview_scraping(self, url: str, template_id: int) -> Dict[str, Any]:
        """Preview scraping results for a URL with a specific template."""
        try:
            template = self.db.query(Template).filter(Template.id == template_id).first()
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            scraper = TemplateScraper(template)
            result = await scraper.scrape_async(url, preview_mode=True)
            
            return {
                "success": True,
                "preview_data": result,
                "template_name": template.name
            }
            
        except Exception as e:
            logger.error(f"Preview failed for {url}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
```

### 2. Template Service Implementation

Create `src/services/template_service.py`:
```python
"""Template management service with validation and CRUD operations."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.services.base_service import BaseService
from src.models.template import Template
from src.templates.template_validator import TemplateValidator
from src.templates.adaptive_selector import AdaptiveSelector
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class TemplateService(BaseService):
    """Service for managing scraping templates."""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(db_session)
        self.validator = TemplateValidator()
        self.adaptive_selector = AdaptiveSelector()
    
    def create_template(self, name: str, description: str,
                       selectors: Dict[str, Any],
                       validation_rules: Optional[Dict[str, Any]] = None,
                       post_processing: Optional[List[Dict[str, Any]]] = None) -> Template:
        """Create a new scraping template."""
        try:
            # Validate template data
            validation_result = self.validator.validate_template({
                'name': name,
                'selectors': selectors,
                'validation_rules': validation_rules or {},
                'post_processing': post_processing or []
            })
            
            if not validation_result['valid']:
                raise ValueError(f"Template validation failed: {validation_result['errors']}")
            
            # Check for name uniqueness
            existing = self.db.query(Template).filter(Template.name == name).first()
            if existing:
                raise ValueError(f"Template with name '{name}' already exists")
            
            # Create template
            template = Template(
                name=name,
                description=description,
                selectors=selectors,
                validation_rules=validation_rules or {},
                post_processing=post_processing or [],
                adaptive_selectors=True,
                fallback_selectors=self._generate_fallback_selectors(selectors),
                learning_enabled=True
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            logger.info(f"Created template: {name}")
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create template '{name}': {e}")
            raise
    
    def get_template(self, template_id: int) -> Optional[Template]:
        """Get template by ID."""
        return self.db.query(Template).filter(Template.id == template_id).first()
    
    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get template by name."""
        return self.db.query(Template).filter(Template.name == name).first()
    
    def get_all_templates(self, active_only: bool = True) -> List[Template]:
        """Get all templates."""
        query = self.db.query(Template)
        return query.order_by(Template.created_at.desc()).all()
    
    def update_template(self, template_id: int, updates: Dict[str, Any]) -> Template:
        """Update an existing template."""
        try:
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Validate updates if selectors are being changed
            if 'selectors' in updates:
                validation_data = {
                    'name': updates.get('name', template.name),
                    'selectors': updates['selectors'],
                    'validation_rules': updates.get('validation_rules', template.validation_rules),
                    'post_processing': updates.get('post_processing', template.post_processing)
                }
                
                validation_result = self.validator.validate_template(validation_data)
                if not validation_result['valid']:
                    raise ValueError(f"Template validation failed: {validation_result['errors']}")
                
                # Update fallback selectors
                updates['fallback_selectors'] = self._generate_fallback_selectors(updates['selectors'])
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = self.db.func.now()
            self.db.commit()
            self.db.refresh(template)
            
            logger.info(f"Updated template {template_id}: {template.name}")
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update template {template_id}: {e}")
            raise
    
    def delete_template(self, template_id: int) -> bool:
        """Delete a template."""
        try:
            template = self.get_template(template_id)
            if not template:
                return False
            
            # Check if template is being used by active jobs
            from src.models.scraping_job import ScrapingJob
            active_jobs = self.db.query(ScrapingJob).filter(
                and_(
                    ScrapingJob.template_id == template_id,
                    ScrapingJob.status.in_(['pending', 'running'])
                )
            ).count()
            
            if active_jobs > 0:
                raise ValueError(f"Cannot delete template: {active_jobs} active jobs are using it")
            
            self.db.delete(template)
            self.db.commit()
            
            logger.info(f"Deleted template {template_id}: {template.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete template {template_id}: {e}")
            raise
    
    def _generate_fallback_selectors(self, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback selectors for adaptive scraping."""
        fallbacks = {}
        
        for field_name, selector_config in selectors.items():
            if isinstance(selector_config, str):
                # Simple selector string
                fallbacks[field_name] = self.adaptive_selector.generate_fallbacks(selector_config)
            elif isinstance(selector_config, dict):
                # Complex selector configuration
                primary_selector = selector_config.get('selector', selector_config.get('css'))
                if primary_selector:
                    fallbacks[field_name] = self.adaptive_selector.generate_fallbacks(primary_selector)
        
        return fallbacks
    
    def test_template(self, template_id: int, test_url: str) -> Dict[str, Any]:
        """Test a template against a URL."""
        try:
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Import here to avoid circular dependency
            from src.scrapers.template_scraper import TemplateScraper
            
            scraper = TemplateScraper(template)
            result = scraper.scrape(test_url)
            
            return {
                "success": True,
                "result": result,
                "template_name": template.name
            }
            
        except Exception as e:
            logger.error(f"Template test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clone_template(self, template_id: int, new_name: str) -> Template:
        """Clone an existing template."""
        try:
            original = self.get_template(template_id)
            if not original:
                raise ValueError(f"Template {template_id} not found")
            
            # Create new template with copied data
            cloned = self.create_template(
                name=new_name,
                description=f"Cloned from {original.name}",
                selectors=original.selectors.copy(),
                validation_rules=original.validation_rules.copy(),
                post_processing=original.post_processing.copy()
            )
            
            logger.info(f"Cloned template {template_id} to {cloned.id}")
            return cloned
            
        except Exception as e:
            logger.error(f"Failed to clone template {template_id}: {e}")
            raise
    
    def get_template_statistics(self, template_id: int) -> Dict[str, Any]:
        """Get usage statistics for a template."""
        try:
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Get job statistics
            from src.models.scraping_job import ScrapingJob
            from sqlalchemy import func
            
            job_stats = self.db.query(
                func.count(ScrapingJob.id).label('total_jobs'),
                func.sum(ScrapingJob.items_scraped).label('total_items'),
                func.avg(ScrapingJob.items_scraped).label('avg_items'),
                func.count(
                    case([(ScrapingJob.status == 'completed', 1)])
                ).label('successful_jobs')
            ).filter(ScrapingJob.template_id == template_id).first()
            
            success_rate = 0
            if job_stats.total_jobs > 0:
                success_rate = (job_stats.successful_jobs / job_stats.total_jobs) * 100
            
            return {
                "template_id": template_id,
                "template_name": template.name,
                "total_jobs": job_stats.total_jobs or 0,
                "total_items_scraped": job_stats.total_items or 0,
                "average_items_per_job": float(job_stats.avg_items or 0),
                "success_rate": round(success_rate, 2),
                "last_used": template.updated_at,
                "created_at": template.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get template statistics {template_id}: {e}")
            raise
    
    def search_templates(self, query: str, limit: int = 50) -> List[Template]:
        """Search templates by name or description."""
        search_term = f"%{query.lower()}%"
        
        return self.db.query(Template).filter(
            or_(
                Template.name.ilike(search_term),
                Template.description.ilike(search_term)
            )
        ).limit(limit).all()
```

### 3. Advanced Scrapling Integration

Create `src/scrapers/template_scraper.py`:
```python
"""Template-based scraper using Scrapling with advanced features."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from scrapling import Fetcher
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper
from src.models.template import Template
from src.templates.adaptive_selector import AdaptiveSelector
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class TemplateScraper(BaseScraper):
    """Advanced template-based scraper with self-healing capabilities."""
    
    def __init__(self, template: Template):
        super().__init__()
        self.template = template
        self.adaptive_selector = AdaptiveSelector()
        self._setup_fetcher()
    
    def _setup_fetcher(self):
        """Set up Scrapling fetcher with template-specific configuration."""
        self.fetcher = Fetcher(
            stealth=self.config.stealth_mode,
            timeout=self.config.timeout,
            user_agent=self.config.user_agent,
            headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Synchronous scraping method."""
        return asyncio.run(self.scrape_async(url, **kwargs))
    
    async def scrape_async(self, url: str, preview_mode: bool = False, **kwargs) -> Dict[str, Any]:
        """Asynchronous scraping with template processing."""
        start_time = time.time()
        
        try:
            # Fetch the page
            response = await self._fetch_page_async(url)
            
            if not response:
                return {
                    'status': 'failed',
                    'error': 'Failed to fetch page',
                    'url': url
                }
            
            # Parse content
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract data using template
            extracted_data = await self._extract_data_from_template(soup, url, preview_mode)
            
            # Post-process data
            processed_data = self._post_process_data(extracted_data)
            
            # Validate results
            validation_result = self._validate_results(processed_data)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                'status': 'success',
                'url': url,
                'page_title': soup.title.string.strip() if soup.title else None,
                'data': processed_data,
                'processing_time': processing_time,
                'template_id': self.template.id,
                'template_name': self.template.name,
                'validation': validation_result
            }
            
            if preview_mode:
                result['raw_html'] = response.content[:5000]  # First 5KB for preview
                result['selector_matches'] = self._get_selector_debug_info(soup)
            
            return result
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'url': url,
                'processing_time': int((time.time() - start_time) * 1000)
            }
    
    async def _fetch_page_async(self, url: str) -> Optional[Any]:
        """Fetch page content asynchronously."""
        try:
            # Use Scrapling's async capabilities
            response = await asyncio.to_thread(self.fetcher.get, url)
            
            if response and response.status_code == 200:
                return response
            else:
                logger.warning(f"HTTP {response.status_code if response else 'None'} for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    async def _extract_data_from_template(self, soup: BeautifulSoup, 
                                        url: str, preview_mode: bool = False) -> Dict[str, Any]:
        """Extract data using template selectors with fallback support."""
        extracted_data = {}
        selector_attempts = {}
        
        for field_name, selector_config in self.template.selectors.items():
            try:
                # Extract single field
                field_data, attempts = await self._extract_field_data(
                    soup, field_name, selector_config, preview_mode
                )
                
                extracted_data[field_name] = field_data
                selector_attempts[field_name] = attempts
                
            except Exception as e:
                logger.warning(f"Failed to extract field '{field_name}': {e}")
                extracted_data[field_name] = None
                selector_attempts[field_name] = [{'selector': str(selector_config), 'error': str(e)}]
        
        if preview_mode:
            extracted_data['_selector_attempts'] = selector_attempts
        
        return extracted_data
    
    async def _extract_field_data(self, soup: BeautifulSoup, field_name: str,
                                selector_config: Union[str, Dict[str, Any]], 
                                preview_mode: bool = False) -> tuple:
        """Extract data for a single field with adaptive selector fallback."""
        attempts = []
        
        # Normalize selector configuration
        if isinstance(selector_config, str):
            selectors_to_try = [selector_config]
            extraction_type = 'text'
            is_list = False
        else:
            selectors_to_try = [selector_config.get('selector', selector_config.get('css'))]
            extraction_type = selector_config.get('type', 'text')
            is_list = selector_config.get('multiple', False)
        
        # Add fallback selectors if adaptive mode is enabled
        if self.template.adaptive_selectors and field_name in self.template.fallback_selectors:
            fallback_selectors = self.template.fallback_selectors[field_name]
            if isinstance(fallback_selectors, list):
                selectors_to_try.extend(fallback_selectors)
        
        # Try selectors in order
        for selector in selectors_to_try:
            if not selector:
                continue
                
            try:
                result = self._extract_with_selector(soup, selector, extraction_type, is_list)
                
                if result is not None and (not isinstance(result, list) or len(result) > 0):
                    attempts.append({'selector': selector, 'success': True, 'result_count': 
                                   len(result) if isinstance(result, list) else 1})
                    return result, attempts
                else:
                    attempts.append({'selector': selector, 'success': False, 'reason': 'no_matches'})
                    
            except Exception as e:
                attempts.append({'selector': selector, 'success': False, 'error': str(e)})
                logger.debug(f"Selector '{selector}' failed for field '{field_name}': {e}")
        
        # No selectors worked
        return None, attempts
    
    def _extract_with_selector(self, soup: BeautifulSoup, selector: str,
                             extraction_type: str, is_list: bool) -> Any:
        """Extract data using a specific selector."""
        # Find elements
        if selector.startswith('//') or selector.startswith('.//'):
            # XPath selector (would need lxml for proper XPath support)
            raise ValueError("XPath selectors not supported in this implementation")
        else:
            # CSS selector
            elements = soup.select(selector)
        
        if not elements:
            return None if not is_list else []
        
        # Extract data based on type
        if is_list:
            return [self._extract_element_data(elem, extraction_type) for elem in elements]
        else:
            return self._extract_element_data(elements[0], extraction_type)
    
    def _extract_element_data(self, element, extraction_type: str) -> Any:
        """Extract data from a single element based on extraction type."""
        if extraction_type == 'text':
            return element.get_text(strip=True)
        elif extraction_type == 'html':
            return str(element)
        elif extraction_type == 'attr':
            # Would need attribute name specified in config
            return element.get('href') or element.get('src') or element.get('value')
        elif extraction_type.startswith('attr:'):
            attr_name = extraction_type.split(':', 1)[1]
            return element.get(attr_name)
        elif extraction_type == 'link':
            return element.get('href')
        elif extraction_type == 'image':
            return element.get('src')
        else:
            return element.get_text(strip=True)
    
    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply post-processing rules to extracted data."""
        if not self.template.post_processing:
            return data
        
        processed_data = data.copy()
        
        for rule in self.template.post_processing:
            try:
                rule_type = rule.get('type')
                field = rule.get('field')
                
                if not field or field not in processed_data:
                    continue
                
                if rule_type == 'clean_text':
                    processed_data[field] = self._clean_text(processed_data[field])
                elif rule_type == 'extract_numbers':
                    processed_data[field] = self._extract_numbers(processed_data[field])
                elif rule_type == 'format_url':
                    base_url = rule.get('base_url', '')
                    processed_data[field] = self._format_url(processed_data[field], base_url)
                elif rule_type == 'regex_extract':
                    pattern = rule.get('pattern')
                    if pattern:
                        processed_data[field] = self._regex_extract(processed_data[field], pattern)
                
            except Exception as e:
                logger.warning(f"Post-processing rule failed: {e}")
        
        return processed_data
    
    def _clean_text(self, text: str) -> str:
        """Clean text data."""
        if not isinstance(text, str):
            return text
        
        import re
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove common unwanted characters
        text = re.sub(r'[^\w\s\-.,!?():]', '', text)
        return text
    
    def _extract_numbers(self, text: str) -> Optional[float]:
        """Extract numeric value from text."""
        if not isinstance(text, str):
            return text
        
        import re
        numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
        return float(numbers[0]) if numbers else None
    
    def _format_url(self, url: str, base_url: str) -> str:
        """Format relative URLs to absolute."""
        if not isinstance(url, str):
            return url
        
        from urllib.parse import urljoin
        return urljoin(base_url, url) if base_url else url
    
    def _regex_extract(self, text: str, pattern: str) -> Optional[str]:
        """Extract text using regex pattern."""
        if not isinstance(text, str):
            return text
        
        import re
        match = re.search(pattern, text)
        return match.group(1) if match and match.groups() else match.group(0) if match else None
    
    def _validate_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted results against template rules."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not self.template.validation_rules:
            return validation_result
        
        for field, rules in self.template.validation_rules.items():
            if field not in data:
                validation_result['errors'].append(f"Required field '{field}' missing")
                validation_result['valid'] = False
                continue
            
            field_value = data[field]
            
            # Check required
            if rules.get('required', False) and not field_value:
                validation_result['errors'].append(f"Field '{field}' is required but empty")
                validation_result['valid'] = False
            
            # Check data type
            expected_type = rules.get('type')
            if expected_type and field_value:
                if expected_type == 'number' and not isinstance(field_value, (int, float)):
                    try:
                        float(field_value)
                    except (ValueError, TypeError):
                        validation_result['warnings'].append(f"Field '{field}' should be numeric")
                
                elif expected_type == 'url' and not self._is_valid_url(field_value):
                    validation_result['warnings'].append(f"Field '{field}' should be a valid URL")
        
        return validation_result
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if string is a valid URL."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def _get_selector_debug_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Get debug information about selector matches."""
        debug_info = {}
        
        for field_name, selector_config in self.template.selectors.items():
            if isinstance(selector_config, str):
                selector = selector_config
            else:
                selector = selector_config.get('selector', selector_config.get('css'))
            
            if selector:
                try:
                    matches = soup.select(selector)
                    debug_info[field_name] = {
                        'selector': selector,
                        'match_count': len(matches),
                        'sample_text': matches[0].get_text(strip=True)[:100] if matches else None
                    }
                except Exception as e:
                    debug_info[field_name] = {
                        'selector': selector,
                        'error': str(e)
                    }
        
        return debug_info
```

### 4. Data Service Implementation

Create `src/services/data_service.py`:
```python
"""Data management and export service."""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.services.base_service import BaseService
from src.models.scraping_job import ScrapingJob
from src.models.scraping_result import ScrapingResult
from src.core.config import config
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class DataService(BaseService):
    """Service for data processing, analysis, and export operations."""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(db_session)
        self.data_folder = Path(config.data_folder)
        self.data_folder.mkdir(parents=True, exist_ok=True)
    
    def get_job_results(self, job_id: int, limit: int = 100, 
                       offset: int = 0, status: Optional[str] = None) -> List[ScrapingResult]:
        """Get results for a specific job."""
        query = self.db.query(ScrapingResult).filter(ScrapingResult.job_id == job_id)
        
        if status:
            query = query.filter(ScrapingResult.status == status)
        
        return query.order_by(ScrapingResult.scraped_at.desc()).offset(offset).limit(limit).all()
    
    def get_job_results_count(self, job_id: int, status: Optional[str] = None) -> int:
        """Get total count of results for a job."""
        query = self.db.query(func.count(ScrapingResult.id)).filter(ScrapingResult.job_id == job_id)
        
        if status:
            query = query.filter(ScrapingResult.status == status)
        
        return query.scalar()
    
    def get_recent_results(self, limit: int = 100, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent scraping results across all jobs."""
        cutoff_time = datetime.utcnow() - pd.Timedelta(hours=hours)
        
        results = self.db.query(ScrapingResult, ScrapingJob.name).join(
            ScrapingJob, ScrapingResult.job_id == ScrapingJob.id
        ).filter(
            ScrapingResult.scraped_at >= cutoff_time
        ).order_by(ScrapingResult.scraped_at.desc()).limit(limit).all()
        
        return [
            {
                'id': result.id,
                'job_id': result.job_id,
                'job_name': job_name,
                'source_url': result.source_url,
                'status': result.status,
                'scraped_at': result.scraped_at,
                'data_preview': self._create_data_preview(result.data)
            }
            for result, job_name in results
        ]
    
    def export_job_results(self, job_id: int, format: str = 'csv', 
                          filename: Optional[str] = None) -> Path:
        """Export job results to specified format."""
        try:
            # Get job information
            job = self.db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            # Get all results
            results = self.get_job_results(job_id, limit=10000)  # Large limit for full export
            
            if not results:
                raise ValueError(f"No results found for job {job_id}")
            
            # Convert to pandas DataFrame
            df = self._results_to_dataframe(results)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_job_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in job.name)
                filename = f"{safe_job_name}_{timestamp}"
            
            # Export based on format
            if format.lower() == 'csv':
                file_path = self.data_folder / f"{filename}.csv"
                df.to_csv(file_path, index=False, encoding='utf-8')
            
            elif format.lower() == 'excel':
                file_path = self.data_folder / f"{filename}.xlsx"
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Results', index=False)
                    
                    # Add summary sheet
                    summary_df = self._create_export_summary(job, results)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            elif format.lower() == 'json':
                file_path = self.data_folder / f"{filename}.json"
                df.to_json(file_path, orient='records', indent=2, force_ascii=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Exported {len(results)} results to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Export failed for job {job_id}: {e}")
            raise
    
    def _results_to_dataframe(self, results: List[ScrapingResult]) -> pd.DataFrame:
        """Convert scraping results to pandas DataFrame."""
        data_rows = []
        
        for result in results:
            # Start with basic information
            row = {
                'result_id': result.id,
                'job_id': result.job_id,
                'source_url': result.source_url,
                'page_title': result.page_title,
                'status': result.status,
                'scraped_at': result.scraped_at,
                'processing_time_ms': result.processing_time
            }
            
            # Add scraped data fields
            if result.data:
                for key, value in result.data.items():
                    # Handle nested data by converting to string
                    if isinstance(value, (dict, list)):
                        row[f"data_{key}"] = str(value)
                    else:
                        row[f"data_{key}"] = value
            
            # Add validation errors if any
            if result.validation_errors:
                row['validation_errors'] = str(result.validation_errors)
            
            data_rows.append(row)
        
        return pd.DataFrame(data_rows)
    
    def _create_export_summary(self, job: ScrapingJob, results: List[ScrapingResult]) -> pd.DataFrame:
        """Create summary information for export."""
        total_results = len(results)
        successful_results = sum(1 for r in results if r.status == 'success')
        failed_results = total_results - successful_results
        
        summary_data = [
            {'Metric': 'Job Name', 'Value': job.name},
            {'Metric': 'Job ID', 'Value': job.id},
            {'Metric': 'Template ID', 'Value': job.template_id},
            {'Metric': 'Target URL', 'Value': job.target_url},
            {'Metric': 'Created At', 'Value': job.created_at},
            {'Metric': 'Started At', 'Value': job.started_at},
            {'Metric': 'Completed At', 'Value': job.completed_at},
            {'Metric': 'Total Results', 'Value': total_results},
            {'Metric': 'Successful Results', 'Value': successful_results},
            {'Metric': 'Failed Results', 'Value': failed_results},
            {'Metric': 'Success Rate', 'Value': f"{(successful_results/total_results)*100:.1f}%" if total_results > 0 else "0%"},
            {'Metric': 'Export Date', 'Value': datetime.utcnow()}
        ]
        
        return pd.DataFrame(summary_data)
    
    def _create_data_preview(self, data: Dict[str, Any], max_length: int = 100) -> str:
        """Create a preview string of scraped data."""
        if not data:
            return "No data"
        
        preview_parts = []
        for key, value in list(data.items())[:3]:  # Show first 3 fields
            if isinstance(value, str) and len(value) > max_length:
                value = value[:max_length] + "..."
            elif isinstance(value, (dict, list)):
                value = f"[{type(value).__name__}]"
            
            preview_parts.append(f"{key}: {value}")
        
        preview = " | ".join(preview_parts)
        if len(data) > 3:
            preview += f" ... (+{len(data) - 3} more fields)"
        
        return preview
    
    def analyze_job_performance(self, job_id: int) -> Dict[str, Any]:
        """Analyze performance metrics for a job."""
        try:
            job = self.db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            results = self.get_job_results(job_id, limit=10000)
            
            if not results:
                return {"error": "No results found for analysis"}
            
            # Calculate metrics
            total_results = len(results)
            successful_results = [r for r in results if r.status == 'success']
            failed_results = [r for r in results if r.status == 'failed']
            
            processing_times = [r.processing_time for r in results if r.processing_time]
            
            analysis = {
                "job_info": {
                    "id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "duration_seconds": job.duration
                },
                "result_metrics": {
                    "total_results": total_results,
                    "successful_results": len(successful_results),
                    "failed_results": len(failed_results),
                    "success_rate": (len(successful_results) / total_results) * 100 if total_results > 0 else 0
                },
                "performance_metrics": {
                    "avg_processing_time_ms": sum(processing_times) / len(processing_times) if processing_times else 0,
                    "min_processing_time_ms": min(processing_times) if processing_times else 0,
                    "max_processing_time_ms": max(processing_times) if processing_times else 0,
                    "total_processing_time_ms": sum(processing_times)
                },
                "data_quality": self._analyze_data_quality(successful_results)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed for job {job_id}: {e}")
            raise
    
    def _analyze_data_quality(self, successful_results: List[ScrapingResult]) -> Dict[str, Any]:
        """Analyze data quality metrics."""
        if not successful_results:
            return {}
        
        # Collect all field names
        all_fields = set()
        for result in successful_results:
            if result.data:
                all_fields.update(result.data.keys())
        
        field_analysis = {}
        for field in all_fields:
            values = []
            for result in successful_results:
                if result.data and field in result.data:
                    value = result.data[field]
                    if value is not None and value != "":
                        values.append(value)
            
            field_analysis[field] = {
                "completeness": (len(values) / len(successful_results)) * 100,
                "unique_values": len(set(str(v) for v in values)),
                "avg_length": sum(len(str(v)) for v in values) / len(values) if values else 0
            }
        
        return {
            "total_fields": len(all_fields),
            "field_analysis": field_analysis,
            "overall_completeness": sum(fa["completeness"] for fa in field_analysis.values()) / len(field_analysis) if field_analysis else 0
        }
    
    def cleanup_old_results(self, days: int = 30) -> int:
        """Clean up old scraping results."""
        try:
            cutoff_date = datetime.utcnow() - pd.Timedelta(days=days)
            
            # Find old results
            old_results = self.db.query(ScrapingResult).filter(
                ScrapingResult.scraped_at < cutoff_date
            ).all()
            
            count = len(old_results)
            
            # Delete old results
            for result in old_results:
                self.db.delete(result)
            
            self.db.commit()
            
            logger.info(f"Cleaned up {count} old results (older than {days} days)")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to cleanup old results: {e}")
            raise
```

## Validation Criteria

### Success Metrics
1. ✅ All service classes implement proper dependency injection
2. ✅ Scrapling integration works with StealthyFetcher capabilities
3. ✅ Template system processes selectors with fallback mechanisms
4. ✅ Database operations handle concurrent access properly
5. ✅ Async job processing supports multiple concurrent scraping operations
6. ✅ Data export functions generate properly formatted CSV/Excel/JSON files
7. ✅ Error handling provides detailed logging and user-friendly messages
8. ✅ Performance monitoring tracks job progress and statistics
9. ✅ Validation system ensures data quality and completeness
10. ✅ Self-healing selectors adapt to page structure changes

### Validation Commands
```bash
# Test service container resolution
python -c "from src.core.container import container; from src.services.scraping_service import ScrapingService; print(container.resolve(ScrapingService))"

# Test Scrapling integration
python -c "from src.scrapers.template_scraper import TemplateScraper; print('Scrapling integration ready')"

# Test database operations
python -c "from src.models.base import engine; from src.models import Base; Base.metadata.create_all(engine); print('Database schema created')"

# Test template processing
python -c "from src.templates.template_manager import TemplateManager; tm = TemplateManager(); print('Template manager initialized')"

# Run basic scraping test
python -c "
from src.scrapers.base_scraper import BaseScraper
class TestScraper(BaseScraper):
    def scrape(self, url, **kwargs):
        return {'status': 'test', 'url': url}
scraper = TestScraper()
result = scraper.scrape('https://httpbin.org/html')
print(f'Test result: {result}')
"
```

### Integration Testing
```python
# Create test script: test_backend_integration.py
import asyncio
from src.core.container import container
from src.services.scraping_service import ScrapingService
from src.services.template_service import TemplateService

async def test_integration():
    # Test service resolution
    scraping_service = container.resolve(ScrapingService)
    template_service = container.resolve(TemplateService)
    
    # Test template creation
    template = template_service.create_template(
        name="Test Template",
        description="Integration test template",
        selectors={"title": "h1", "content": "p"}
    )
    
    # Test job creation
    job = scraping_service.create_job(
        name="Test Job",
        template_id=template.id,
        target_url="https://httpbin.org/html"
    )
    
    print(f"Created job {job.id} with template {template.id}")
    return True

if __name__ == "__main__":
    asyncio.run(test_integration())
```

## Troubleshooting Guide

### Service Container Issues
```python
# Debug service registration
from src.core.container import container
print("Registered services:", list(container._services.keys()))
print("Registered factories:", list(container._factories.keys()))
```

### Database Connection Problems
```python
# Test database connection
from src.models.base import engine, SessionLocal
try:
    connection = engine.connect()
    print("✅ Database connection successful")
    connection.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

### Scrapling Integration Issues
- Verify scrapling installation: `pip list | grep scrapling`
- Check StealthyFetcher configuration in `config.py`
- Test basic fetching: `python -c "from scrapling import Fetcher; f = Fetcher(); print(f.get('https://httpbin.org/html').status_code)"`

### Template Processing Errors
- Validate template JSON structure
- Check CSS selector syntax
- Test selectors in browser developer tools
- Verify fallback selector generation

### Async Operation Problems
- Check for proper `await` usage in async functions
- Verify asyncio event loop configuration
- Monitor background task execution with logging
- Ensure proper exception handling in async contexts

## Next Steps
After successful completion:
1. Proceed to **Phase 3: Frontend Development** to build interactive UI components
2. All backend services are implemented and tested
3. Database schema is created and operational
4. Scraping engine is ready for production workloads
5. API endpoints are ready for frontend integration

## File Deliverables
- `src/services/scraping_service.py` - Core scraping operations and job management
- `src/services/template_service.py` - Template CRUD and validation
- `src/services/data_service.py` - Data processing and export operations
- `src/scrapers/template_scraper.py` - Advanced Scrapling integration
- `src/templates/adaptive_selector.py` - Self-healing selector system
- `src/utils/validation_utils.py` - URL and data validation utilities
- Database migration scripts for schema updates
- Integration test suite for backend components