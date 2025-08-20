"""API routes for Eel web interface."""

import eel
import asyncio
from typing import Dict, Any, List, Optional
from src.core.container import container
from src.services.scraping_service import ScrapingService
from src.services.template_service import TemplateService
from src.services.data_service import DataService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def register_api_routes():
    """Register all API routes with Eel."""
    
    # Register broadcast function for real-time updates
    @eel.expose
    def broadcast_job_progress(data):
        """Broadcast job progress to all connected clients."""
        # This will be called from the backend to send updates to frontend
        # Eel handles the actual broadcasting
        pass
    
    @eel.expose
    def ping():
        """Health check endpoint."""
        return {"status": "ok", "message": "ScraperV4 backend is running"}
    
    @eel.expose
    def log_frontend_activity(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Log frontend activity to backend logs."""
        try:
            from pathlib import Path
            import json
            from datetime import datetime
            
            # Create frontend log file
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            frontend_log = log_dir / "frontend.log"
            
            # Append logs to file
            with open(frontend_log, 'a') as f:
                for log_entry in logs:
                    log_line = json.dumps(log_entry) + "\n"
                    f.write(log_line)
                    
                    # Also log to backend logger based on level
                    level = log_entry.get('level', 'INFO')
                    component = log_entry.get('component', 'Frontend')
                    message = log_entry.get('message', '')
                    
                    log_msg = f"[FRONTEND:{component}] {message}"
                    if log_entry.get('data'):
                        log_msg += f" - Data: {json.dumps(log_entry['data'])}"
                    
                    if level == 'ERROR' or level == 'CRITICAL':
                        logger.error(log_msg)
                    elif level == 'WARNING':
                        logger.warning(log_msg)
                    elif level == 'DEBUG':
                        logger.debug(log_msg)
                    else:
                        logger.info(log_msg)
            
            return {"success": True, "logged": len(logs)}
            
        except Exception as e:
            logger.error(f"Failed to log frontend activity: {e}")
            return {"success": False, "error": str(e)}
    
    # Scraping Job Endpoints
    @eel.expose
    def start_scraping_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new scraping job."""
        try:
            scraping_service = container.resolve(ScrapingService)
            job = scraping_service.create_job(
                name=job_data['jobName'],
                template_id=job_data['templateId'],
                target_url=job_data['targetUrl'],
                config=job_data.get('config', {}),
                parameters=job_data.get('parameters', {})
            )
            
            # Start job in background using asyncio.run()
            import threading
            def run_async_job():
                asyncio.run(scraping_service.execute_job_async(job.id))
            
            thread = threading.Thread(target=run_async_job, daemon=True)
            thread.start()
            
            logger.info(f"Started scraping job: {job.id}")
            return {
                "success": True,
                "job_id": job.id,
                "message": "Scraping job started successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to start scraping job: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def stop_scraping_job(job_id: int) -> Dict[str, Any]:
        """Stop a running scraping job."""
        try:
            scraping_service = container.resolve(ScrapingService)
            success = scraping_service.stop_job(str(job_id))
            
            if success:
                logger.info(f"Stopped scraping job: {job_id}")
                return {
                    "success": True,
                    "message": "Scraping job stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Job not found or already stopped"
                }
                
        except Exception as e:
            logger.error(f"Failed to stop scraping job {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_job_status(job_id: int) -> Dict[str, Any]:
        """Get status of a scraping job."""
        try:
            scraping_service = container.resolve(ScrapingService)
            job = scraping_service.get_job(str(job_id))
            
            if not job:
                return {
                    "success": False,
                    "error": "Job not found"
                }
            
            return {
                "success": True,
                "job": {
                    "id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "progress": job.progress,
                    "items_scraped": job.items_scraped,
                    "items_failed": job.items_failed,
                    "created_at": job.created_at,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "duration": job.duration,
                    "error_message": job.error_message
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_job_results(job_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get results for a scraping job."""
        try:
            data_service = container.resolve(DataService)
            results = data_service.get_job_results(str(job_id), limit=limit, offset=offset)
            
            return {
                "success": True,
                "results": [
                    {
                        "id": result.id,
                        "source_url": result.source_url,
                        "data": result.data,
                        "scraped_at": result.scraped_at.isoformat(),
                        "status": result.status
                    }
                    for result in results
                ],
                "total": data_service.get_job_results_count(str(job_id))
            }
            
        except Exception as e:
            logger.error(f"Failed to get job results {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Template Management Endpoints
    @eel.expose
    def get_templates() -> Dict[str, Any]:
        """Get all scraping templates."""
        try:
            logger.info("API: get_templates called")
            template_service = container.resolve(TemplateService)
            templates = template_service.get_all_templates()
            
            logger.info(f"API: Found {len(templates)} templates")
            
            template_list = []
            for template in templates:
                template_data = {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "version": template.version,
                    "usage_count": template.usage_count,
                    "success_rate": template.success_rate,
                    "created_at": template.created_at,
                    "selectors": template.selectors,
                    "fetcher_config": getattr(template, 'fetcher_config', {})
                }
                template_list.append(template_data)
                logger.debug(f"API: Template {template.id}: {template.name}")
            
            return {
                "success": True,
                "templates": template_list
            }
            
        except Exception as e:
            logger.error(f"Failed to get templates: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_template(template_id: str) -> Dict[str, Any]:
        """Get a specific template. template_id can be the template name."""
        try:
            logger.info(f"API: get_template called with template_id: {template_id}")
            
            # Handle None or empty template_id
            if not template_id or template_id == 'None' or template_id == 'null':
                logger.warning(f"API: Invalid template_id received: {template_id}")
                return {
                    "success": False,
                    "error": "Invalid template ID"
                }
            
            template_service = container.resolve(TemplateService)
            
            # Template IDs are strings (template names), no conversion needed
            template = template_service.get_template(template_id)
            
            if not template:
                logger.warning(f"API: Template not found: {template_id}")
                return {
                    "success": False,
                    "error": "Template not found"
                }
            
            logger.info(f"API: Found template: {template.id} - {template.name}")
            
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "selectors": template.selectors,
                "fetcher_config": getattr(template, 'fetcher_config', {}),
                "validation_rules": template.validation_rules,
                "post_processing": template.post_processing,
                "adaptive_selectors": template.adaptive_selectors,
                "fallback_selectors": template.fallback_selectors,
                "version": template.version,
                "usage_count": template.usage_count,
                "success_rate": template.success_rate,
                "created_at": getattr(template, 'created_at', '')
            }
            
            return {
                "success": True,
                "template": template_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def create_template(template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scraping template."""
        try:
            template_service = container.resolve(TemplateService)
            template = template_service.create_template(
                name=template_data['name'],
                description=template_data.get('description', ''),
                selectors=template_data['selectors'],
                fetcher_config=template_data.get('fetcher_config', {}),
                validation_rules=template_data.get('validation_rules', {})
            )
            
            logger.info(f"Created template: {template.name}")
            return {
                "success": True,
                "template_id": template.id,
                "message": "Template created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def update_template(template_id: int, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing template."""
        try:
            template_service = container.resolve(TemplateService)
            success = template_service.update_template(str(template_id), template_data)
            
            if success:
                logger.info(f"Updated template: {template_id}")
                return {
                    "success": True,
                    "message": "Template updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Template not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def delete_template(template_id: int) -> Dict[str, Any]:
        """Delete a template."""
        try:
            template_service = container.resolve(TemplateService)
            success = template_service.delete_template(str(template_id))
            
            if success:
                logger.info(f"Deleted template: {template_id}")
                return {
                    "success": True,
                    "message": "Template deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Template not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Data Export Endpoints
    @eel.expose
    def export_results(job_id: str, format: str = 'csv') -> Dict[str, Any]:
        """Export job results to file."""
        try:
            data_service = container.resolve(DataService)
            file_path = data_service.export_job_results(job_id, format)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "message": f"Results exported to {format.upper()} successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to export results {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Settings Endpoints
    @eel.expose
    def get_settings() -> Dict[str, Any]:
        """Get application settings."""
        try:
            from src.core.config import config
            return {
                "success": True,
                "settings": {
                    "default_delay": config.scraping.default_delay,
                    "max_retries": config.scraping.max_retries,
                    "timeout": config.scraping.timeout,
                    "stealth_mode": config.scraping.stealth_mode,
                    "concurrent_jobs": config.scraping.concurrent_jobs
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def update_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update application settings."""
        try:
            from src.core.config import config
            
            # Update configuration
            if 'default_delay' in settings:
                config.scraping.default_delay = settings['default_delay']
            if 'max_retries' in settings:
                config.scraping.max_retries = settings['max_retries']
            if 'timeout' in settings:
                config.scraping.timeout = settings['timeout']
            if 'stealth_mode' in settings:
                config.scraping.stealth_mode = settings['stealth_mode']
            if 'concurrent_jobs' in settings:
                config.scraping.concurrent_jobs = settings['concurrent_jobs']
            
            logger.info("Updated application settings")
            return {
                "success": True,
                "message": "Settings updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # URL Preview and Validation
    @eel.expose
    def preview_url(url: str, template_id: str) -> Dict[str, Any]:
        """Preview URL scraping with template."""
        try:
            scraping_service = container.resolve(ScrapingService)
            preview_data = scraping_service.preview_scraping(url, template_id)
            
            return {
                "success": True,
                "preview": preview_data
            }
            
        except Exception as e:
            logger.error(f"Failed to preview URL {url}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def validate_url(url: str) -> Dict[str, Any]:
        """Validate URL accessibility."""
        try:
            from src.utils.validation_utils import validate_url
            result = validate_url(url)
            
            return {
                "success": True,
                "valid": result['valid'],
                "status_code": result.get('status_code'),
                "error": result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Failed to validate URL {url}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def test_selector(url: str, selector: str) -> Dict[str, Any]:
        """Test selector against URL."""
        try:
            from src.utils.validation_utils import test_selector
            result = test_selector(url, selector)
            
            return {
                "success": True,
                "matches": result['matches'],
                "count": result['count'],
                "sample_data": result.get('sample_data', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to test selector {selector}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Interactive mode routes
    @eel.expose
    def start_interactive_mode(url: str) -> Dict[str, Any]:
        """Start interactive template creation mode."""
        try:
            from src.services.interactive_service import InteractiveService
            from src.core.container import container
            
            # Get or create interactive service
            if not container.has(InteractiveService):
                container.register_singleton(InteractiveService, InteractiveService)
            
            interactive_service = container.get(InteractiveService)
            
            # Analyze page structure
            analysis = interactive_service.analyze_page_structure(url)
            
            logger.info(f"Started interactive mode for URL: {url}")
            
            return {
                "success": True,
                "url": url,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to start interactive mode: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def analyze_element(element_data: Dict) -> Dict[str, Any]:
        """Analyze selected element and suggest selectors."""
        try:
            from src.services.interactive_service import InteractiveService
            from src.core.container import container
            
            interactive_service = container.get(InteractiveService)
            
            # Get HTML if provided
            html = element_data.get('html', '')
            
            # Suggest selectors
            suggestions = interactive_service.suggest_selectors(html, element_data)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "element_type": element_data.get('type', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze element: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def save_interactive_template(template_data: Dict) -> Dict[str, Any]:
        """Save template created with interactive selector."""
        try:
            from src.services.interactive_service import InteractiveService
            from src.services.template_service import TemplateService
            from src.core.container import container
            
            interactive_service = container.get(InteractiveService)
            template_service = container.get(TemplateService)
            
            # Generate template from selections
            result = interactive_service.generate_template_from_selection(template_data)
            
            if result['success']:
                template = result['template']
                
                # Save template using template service
                saved = template_service.create_template(
                    name=template['name'],
                    selectors=template['selectors'],
                    description=template.get('description', ''),
                    fetcher_config=template.get('fetcher_config'),
                    validation_rules=template.get('validation_rules'),
                    post_processing=template.get('post_processing')
                )
                
                if saved:
                    logger.info(f"Interactive template saved: {template['name']}")
                    return {
                        "success": True,
                        "template_name": template['name'],
                        "validation": result.get('validation', {})
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to save template"
                    }
            else:
                return result
            
        except Exception as e:
            logger.error(f"Failed to save interactive template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def test_selector_live(selector: str, url: str) -> Dict[str, Any]:
        """Test selector on live URL."""
        try:
            from src.services.interactive_service import InteractiveService
            from src.scrapers.template_scraper import TemplateScraper
            from src.core.container import container
            
            interactive_service = container.get(InteractiveService)
            
            # Fetch page HTML
            scraper = TemplateScraper()
            html = scraper.fetch_page(url)
            
            if not html:
                return {
                    "success": False,
                    "error": "Failed to fetch page"
                }
            
            # Validate selector
            result = interactive_service.validate_selector(selector, html)
            
            return {
                "success": True,
                "valid": result['valid'],
                "count": result['count'],
                "samples": result.get('samples', []),
                "quality": result.get('quality', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to test selector: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_detail_page_suggestions(url: str) -> Dict[str, Any]:
        """Get suggestions for detail page extraction."""
        try:
            from src.scrapers.detail_page_analyzer import DetailPageAnalyzer
            
            analyzer = DetailPageAnalyzer()
            suggestions = analyzer.analyze_detail_page(url)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "url": url
            }
            
        except ImportError:
            logger.warning("Detail page analyzer not available")
            return {
                "success": False,
                "error": "Detail page analyzer not implemented yet"
            }
        except Exception as e:
            logger.error(f"Failed to get detail page suggestions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def apply_learning_correction(correction_data: Dict) -> Dict[str, Any]:
        """Apply user correction for learning."""
        try:
            from src.services.interactive_service import InteractiveService
            from src.core.container import container
            
            interactive_service = container.get(InteractiveService)
            
            # Apply correction
            success = interactive_service.apply_learning_corrections(correction_data)
            
            if success:
                logger.info(f"Applied learning correction for domain: {correction_data.get('domain', 'general')}")
                return {
                    "success": True,
                    "message": "Correction applied successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to apply correction"
                }
            
        except Exception as e:
            logger.error(f"Failed to apply learning correction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    logger.info("API routes registered successfully")