"""Core scraping operations service."""

from typing import Dict, Any, Optional
import asyncio
import re
import ipaddress
from urllib.parse import urlparse
from datetime import datetime, timezone
from .base_service import BaseService

class JobData:
    """Wrapper class to provide attribute access to job data."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def __getattr__(self, name):
        """Provide attribute-style access to dictionary keys."""
        return self._data.get(name)
    
    @property
    def id(self):
        return self._data.get('id', '')
    
    @property
    def name(self):
        return self._data.get('name', '')
    
    @property
    def status(self):
        return self._data.get('status', 'pending')
    
    @property
    def progress(self):
        return self._data.get('progress', 0)
    
    @property
    def items_scraped(self):
        return self._data.get('items_scraped', 0)
    
    @property
    def items_failed(self):
        return self._data.get('items_failed', 0)
    
    @property
    def created_at(self):
        timestamp = self._data.get('created_at')
        if timestamp:
            return datetime.fromisoformat(timestamp)
        return None
    
    @property
    def started_at(self):
        timestamp = self._data.get('started_at')
        if timestamp:
            return datetime.fromisoformat(timestamp)
        return None
    
    @property
    def completed_at(self):
        timestamp = self._data.get('completed_at')
        if timestamp:
            return datetime.fromisoformat(timestamp)
        return None
    
    @property
    def duration(self):
        return self._data.get('duration', 0)
    
    @property
    def error_message(self):
        return self._data.get('error_message')

class ScrapingService(BaseService):
    """Service for managing scraping operations."""
    
    def __init__(self):
        super().__init__()
        self.active_tasks = {}  # Track running async tasks for cancellation
    
    def create_job(self, name: str, template_id: str, target_url: str,
                   config: Optional[Dict[str, Any]] = None,
                   parameters: Optional[Dict[str, Any]] = None) -> JobData:
        """Create a new scraping job."""
        # Convert template_id to template_name (for now they're the same)
        job_dict = self.job_manager.create_job(
            name=name,
            template_name=template_id,
            target_url=target_url,
            job_config=config,
            parameters=parameters
        )
        return JobData(job_dict)
    
    async def execute_job_async(self, job_id: str) -> None:
        """Execute a scraping job asynchronously."""
        try:
            # Get job details
            job = self.job_manager.get_job(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            # Update job status to running
            self.job_manager.update_job_status(job_id, "running")
            self.job_manager.update_job(job_id, {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "progress": 0
            })
            
            # Extract job parameters
            template_name = job.get('template_name')
            target_url = job.get('target_url')
            job_config = job.get('job_config', {})
            # parameters = job.get('parameters', {})  # Currently unused in this method
            
            # Validate required parameters
            if not template_name:
                raise ValueError("Template name is required")
            if not target_url:
                raise ValueError("Target URL is required")
            
            # Load template
            template = self.template_manager.load_template(template_name)
            if not template:
                raise ValueError(f"Template '{template_name}' not found")
            
            # Import TemplateScraper
            from src.scrapers.template_scraper import TemplateScraper
            
            # Create scraper instance
            scraper = TemplateScraper(template)
            
            # Check if pagination is enabled
            max_pages = job_config.get('max_pages', 1)
            use_pagination = template.get('pagination', {}).get('enabled', False) and max_pages > 1
            
            # Track scraping progress
            items_scraped = 0
            items_failed = 0
            all_results = []
            template_name = str(template_name)  # Ensure it's a string
            
            try:
                if use_pagination:
                    # Use async pagination scraping
                    pagination_result = await scraper.scrape_with_pagination_async(
                        target_url, 
                        max_pages=max_pages
                    )
                    
                    # Process pagination result
                    if pagination_result.get('status') == 'success':
                        page_results = pagination_result.get('results', [])
                        # Process pagination results
                        
                        for page_result in page_results:
                            if page_result.get('status') == 'success':
                                page_data = page_result.get('data', [])
                                if isinstance(page_data, list):
                                    items_scraped += len(page_data)
                                    all_results.extend(page_data)
                                else:
                                    items_scraped += 1
                                    all_results.append(page_data)
                            else:
                                items_failed += 1
                        
                        # Update final progress
                        self.job_manager.update_job(job_id, {
                            "progress": 100,
                            "items_scraped": items_scraped,
                            "items_failed": items_failed
                        })
                        
                        # Broadcast final progress update via Eel
                        self._broadcast_job_progress(job_id, 100, items_scraped, items_failed)
                    else:
                        items_failed = 1
                        raise Exception(pagination_result.get('error', 'Pagination scraping failed'))
                else:
                    # Single page scraping
                    result = scraper.scrape(target_url)
                    
                    if result.get('status') == 'success':
                        scraped_data = result.get('data', {})
                        if isinstance(scraped_data, list):
                            items_scraped = len(scraped_data)
                            all_results = scraped_data
                        else:
                            items_scraped = 1
                            all_results = [scraped_data]
                    else:
                        items_failed = 1
                        raise Exception(result.get('error', 'Scraping failed'))
                    
                    # Update progress
                    self.job_manager.update_job(job_id, {
                        "progress": 100,
                        "items_scraped": items_scraped,
                        "items_failed": items_failed
                    })
                    
                    # Broadcast progress update via Eel
                    self._broadcast_job_progress(job_id, 100, items_scraped, items_failed)
                
                # Save results using data service
                from src.services.data_service import DataService
                data_service = DataService()
                
                # Process data if post-processing rules exist
                if template.get('post_processing'):
                    processed_result = data_service.process_scraped_data(
                        all_results,
                        template.get('post_processing')
                    )
                    if processed_result.get('success'):
                        all_results = processed_result.get('data', all_results)
                
                # Save results
                result_id = data_service.save_scraping_result(
                    job_id,
                    all_results,
                    metadata={
                        "template": template_name,
                        "url": target_url,
                        "items_scraped": items_scraped,
                        "items_failed": items_failed
                    }
                )
                
                # Update job as completed
                self.job_manager.update_job(job_id, {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "progress": 100,
                    "items_scraped": items_scraped,
                    "items_failed": items_failed,
                    "result_id": result_id
                })
                
                # Clean up task reference
                if job_id in self.active_tasks:
                    del self.active_tasks[job_id]
                
                # Update template statistics
                self.template_manager.update_template_stats(
                    template_name, 
                    success=items_scraped > 0
                )
                
            except asyncio.CancelledError:
                # Handle job cancellation
                self.job_manager.update_job_status(job_id, "cancelled")
                # Clean up task reference if it still exists
                if job_id in self.active_tasks:
                    del self.active_tasks[job_id]
                raise
                
        except Exception as e:
            # Ensure variables are defined for error handling
            items_failed = locals().get('items_failed', 1)
            template_name = locals().get('template_name', '')
            
            # Update job as failed
            self.job_manager.update_job(job_id, {
                "status": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": str(e),
                "items_failed": items_failed
            })
            
            # Clean up task reference
            if job_id in self.active_tasks:
                del self.active_tasks[job_id]
            
            # Update template statistics with failure
            if template_name:
                self.template_manager.update_template_stats(template_name, False)
            
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Job {job_id} failed: {e}")
    
    def stop_job(self, job_id: str) -> bool:
        """Stop a running scraping job."""
        return self.stop_scraping_job(str(job_id))
    
    def get_job(self, job_id: str) -> Optional[JobData]:
        """Get job by ID."""
        job_dict = self.job_manager.get_job(str(job_id))
        if job_dict:
            return JobData(job_dict)
        return None
    
    def start_scraping_job(self, job_id: str) -> bool:
        """Start a scraping job."""
        try:
            # Create async task to execute the job and store reference for cancellation
            task = asyncio.create_task(self.execute_job_async(job_id))
            self.active_tasks[job_id] = task
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to start job {job_id}: {e}")
            return False
    
    def stop_scraping_job(self, job_id: str) -> bool:
        """Stop a running scraping job."""
        # Cancel the async task if it exists
        if job_id in self.active_tasks:
            self.active_tasks[job_id].cancel()
            del self.active_tasks[job_id]
        
        # Update job status to cancelled
        return self.job_manager.update_job_status(job_id, "cancelled")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a scraping job."""
        job = self.job_manager.get_job(job_id)
        if job:
            return {
                "id": job["id"],
                "status": job["status"],
                "progress": job["progress"],
                "items_scraped": job["items_scraped"],
                "items_failed": job["items_failed"],
                "error_message": job.get("error_message")
            }
        return None
    
    def scrape_with_template(self, template_name: str, target_url: str, 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scrape a URL using a template with Scrapling and TemplateScraper."""
        try:
            # Load template using template_manager
            template = self.template_manager.load_template(template_name)
            if not template:
                return {
                    "status": "failed",
                    "error": f"Template '{template_name}' not found",
                    "url": target_url,
                    "template": template_name,
                    "parameters": parameters or {}
                }
            
            # Import TemplateScraper here to avoid circular imports
            from src.scrapers.template_scraper import TemplateScraper
            
            # Create TemplateScraper instance with the loaded template
            scraper = TemplateScraper(template)
            
            # Validate template before scraping
            validation_result = scraper.validate_template()
            if not validation_result.get('valid', False):
                return {
                    "status": "failed",
                    "error": f"Template validation failed: {', '.join(validation_result.get('errors', []))}",
                    "url": target_url,
                    "template": template_name,
                    "parameters": parameters or {}
                }
            
            # Validate target URL
            url_validation = self.validate_scraping_target(target_url)
            if not url_validation.get('valid', False):
                return {
                    "status": "failed",
                    "error": f"Invalid target URL: {url_validation.get('error', 'Unknown error')}",
                    "url": target_url,
                    "template": template_name,
                    "parameters": parameters or {}
                }
            
            # Apply parameters to template if provided
            if parameters and scraper.template:
                # Merge parameters with template configuration
                scraper.template.update(parameters)
            
            # Perform the scraping using TemplateScraper
            result = scraper.scrape(target_url)
            
            # Update template statistics based on result
            success = result.get('status') == 'success'
            self.template_manager.update_template_stats(template_name, success)
            
            # Add metadata to result
            result['template'] = template_name
            result['parameters'] = parameters or {}
            result['scraped_at'] = datetime.now(timezone.utc).isoformat()
            
            return result
            
        except Exception as e:
            # Update template stats with failure
            self.template_manager.update_template_stats(template_name, False)
            
            return {
                "status": "failed",
                "error": f"Scraping failed: {str(e)}",
                "url": target_url,
                "template": template_name,
                "parameters": parameters or {},
                "scraped_at": datetime.now(timezone.utc).isoformat()
            }
    
    def validate_scraping_target(self, url: str) -> Dict[str, Any]:
        """
        Comprehensive URL validation for scraping targets with security checks.
        
        Security validations include:
        - Scheme validation (only HTTP/HTTPS)
        - Private IP range blocking
        - Localhost blocking
        - Suspicious pattern detection
        - URL injection prevention
        
        Args:
            url: The URL to validate
            
        Returns:
            Dict containing validation results with 'valid', 'error', and metadata
        """
        if not url or not isinstance(url, str):
            return {
                "valid": False,
                "error": "URL is required and must be a string",
                "security_risk": "high",
                "details": []
            }
        
        # Strip whitespace and normalize
        url = url.strip()
        
        # Check for suspicious patterns first
        suspicious_patterns = [
            r'[^a-zA-Z0-9:/._?&=%\-#+]',  # Non-standard characters
            r'javascript:',               # JavaScript scheme
            r'data:',                    # Data scheme
            r'vbscript:',               # VBScript scheme
            r'[@].*[@]',                # Multiple @ symbols (credential injection)
            r'\.\./',                   # Path traversal attempts
            r'%2e%2e%2f',              # Encoded path traversal
            r'%00',                     # Null byte injection
            r'<script',                 # Script injection
            r'<iframe',                 # Iframe injection
        ]
        
        security_issues = []
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                security_issues.append(f"Suspicious pattern detected: {pattern}")
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return {
                "valid": False,
                "error": f"URL parsing failed: {str(e)}",
                "security_risk": "high",
                "details": security_issues
            }
        
        # Validate scheme - only allow HTTP/HTTPS
        if parsed.scheme.lower() not in ['http', 'https']:
            security_issues.append(f"Blocked scheme: {parsed.scheme}")
            return {
                "valid": False,
                "error": f"Only HTTP and HTTPS schemes are allowed, got: {parsed.scheme}",
                "security_risk": "high",
                "details": security_issues
            }
        
        # Validate hostname exists
        if not parsed.hostname:
            security_issues.append("Missing hostname")
            return {
                "valid": False,
                "error": "URL must contain a valid hostname",
                "security_risk": "medium",
                "details": security_issues
            }
        
        hostname = parsed.hostname.lower()
        
        # Check for localhost and loopback addresses
        localhost_patterns = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '::1',
            '0:0:0:0:0:0:0:1'
        ]
        
        if hostname in localhost_patterns or hostname.startswith('127.'):
            security_issues.append(f"Localhost access blocked: {hostname}")
            return {
                "valid": False,
                "error": "Access to localhost and loopback addresses is not allowed",
                "security_risk": "high",
                "details": security_issues
            }
        
        # Check for private IP ranges
        try:
            # Try to parse as IP address
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                security_issues.append(f"Private/restricted IP blocked: {hostname}")
                return {
                    "valid": False,
                    "error": f"Access to private/restricted IP addresses is not allowed: {hostname}",
                    "security_risk": "high",
                    "details": security_issues
                }
        except ValueError:
            # Not an IP address, continue with domain validation
            pass
        
        # Check for internal domain patterns
        internal_domains = [
            '.local',
            '.internal',
            '.corp',
            '.private',
            'intranet',
            'internal'
        ]
        
        for internal_pattern in internal_domains:
            if internal_pattern in hostname:
                security_issues.append(f"Internal domain pattern detected: {internal_pattern}")
                return {
                    "valid": False,
                    "error": f"Access to internal domains is not allowed: {hostname}",
                    "security_risk": "high",
                    "details": security_issues
                }
        
        # Check for credentials in URL (user:pass@host)
        if parsed.username or parsed.password:
            security_issues.append("URL contains embedded credentials")
            return {
                "valid": False,
                "error": "URLs with embedded credentials are not allowed",
                "security_risk": "high",
                "details": security_issues
            }
        
        # Validate port if specified
        if parsed.port:
            # Block common internal service ports
            blocked_ports = [
                22,    # SSH
                23,    # Telnet
                25,    # SMTP
                53,    # DNS
                110,   # POP3
                143,   # IMAP
                993,   # IMAPS
                995,   # POP3S
                1433,  # SQL Server
                3306,  # MySQL
                5432,  # PostgreSQL
                6379,  # Redis
                27017, # MongoDB
            ]
            
            if parsed.port in blocked_ports:
                security_issues.append(f"Blocked port: {parsed.port}")
                return {
                    "valid": False,
                    "error": f"Access to port {parsed.port} is not allowed",
                    "security_risk": "high",
                    "details": security_issues
                }
        
        # Check URL length to prevent abuse
        if len(url) > 2048:
            security_issues.append("URL exceeds maximum length")
            return {
                "valid": False,
                "error": "URL exceeds maximum allowed length (2048 characters)",
                "security_risk": "medium",
                "details": security_issues
            }
        
        # Determine security risk level
        risk_level = "low"
        if security_issues:
            risk_level = "medium"
        
        # Additional validation warnings (non-blocking)
        warnings = []
        
        # Check for non-standard ports
        if parsed.port and parsed.port not in [80, 443, 8080, 8443]:
            warnings.append(f"Non-standard port detected: {parsed.port}")
        
        # Check for suspicious TLD patterns
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.onion']
        for tld in suspicious_tlds:
            if hostname.endswith(tld):
                warnings.append(f"Suspicious TLD detected: {tld}")
                risk_level = "medium"
        
        # Success response with comprehensive metadata
        return {
            "valid": True,
            "url": url,
            "parsed_url": {
                "scheme": parsed.scheme,
                "hostname": hostname,
                "port": parsed.port,
                "path": parsed.path,
                "query": parsed.query,
                "fragment": parsed.fragment
            },
            "domain": hostname,
            "security_risk": risk_level,
            "warnings": warnings,
            "details": security_issues,
            "validation_checks": {
                "scheme_valid": True,
                "hostname_valid": True,
                "no_localhost": True,
                "no_private_ip": True,
                "no_credentials": True,
                "safe_port": True,
                "length_valid": True,
                "no_suspicious_patterns": len(security_issues) == 0
            }
        }
    
    def preview_scraping(self, url: str, template_id: str) -> Dict[str, Any]:
        """Preview URL scraping with template to show what would be scraped."""
        try:
            # Validate URL first
            url_validation = self.validate_scraping_target(url)
            if not url_validation.get('valid', False):
                return {
                    "url": url,
                    "template_id": template_id,
                    "success": False,
                    "error": f"Invalid target URL: {url_validation.get('error', 'Unknown error')}",
                    "preview": {
                        "count": 0,
                        "success_rate": "0%",
                        "sample_data": []
                    },
                    "preview_data": {
                        "title": "",
                        "items_found": 0,
                        "selectors_matched": 0,
                        "sample_data": [],
                        "fields_extracted": [],
                        "validation_results": {}
                    }
                }
            
            # Load template using template_manager
            template = self.template_manager.load_template(template_id)
            if not template:
                return {
                    "url": url,
                    "template_id": template_id,
                    "success": False,
                    "error": f"Template '{template_id}' not found",
                    "preview": {
                        "count": 0,
                        "success_rate": "0%",
                        "sample_data": []
                    },
                    "preview_data": {
                        "title": "",
                        "items_found": 0,
                        "selectors_matched": 0,
                        "sample_data": [],
                        "fields_extracted": [],
                        "validation_results": {}
                    }
                }
            
            # Import TemplateScraper here to avoid circular imports
            from src.scrapers.template_scraper import TemplateScraper
            
            # Create TemplateScraper instance with the loaded template
            scraper = TemplateScraper(template)
            
            # Validate template before using it
            validation_result = scraper.validate_template()
            if not validation_result.get('valid', False):
                return {
                    "url": url,
                    "template_id": template_id,
                    "success": False,
                    "error": f"Template validation failed: {', '.join(validation_result.get('errors', []))}",
                    "preview": {
                        "count": 0,
                        "success_rate": "0%",
                        "sample_data": []
                    },
                    "preview_data": {
                        "title": "",
                        "items_found": 0,
                        "selectors_matched": 0,
                        "sample_data": [],
                        "fields_extracted": [],
                        "validation_results": validation_result
                    }
                }
            
            # Test selectors to see which ones work
            selector_test_results = scraper.test_selectors(url)
            
            # Check if selector testing completely failed (no results at all)
            if 'selector_results' not in selector_test_results:
                return {
                    "url": url,
                    "template_id": template_id,
                    "success": False,
                    "error": f"Failed to test selectors: {selector_test_results.get('error', 'Unknown error')}",
                    "preview": {
                        "count": 0,
                        "success_rate": "0%",
                        "sample_data": []
                    },
                    "preview_data": {
                        "title": "",
                        "items_found": 0,
                        "selectors_matched": 0,
                        "sample_data": [],
                        "fields_extracted": [],
                        "validation_results": selector_test_results
                    }
                }
            
            # Extract statistics from selector test results
            statistics = selector_test_results.get('statistics', {})
            selector_results = selector_test_results.get('selector_results', {})
            
            total_selectors = statistics.get('total_selectors', 0)
            successful_selectors = statistics.get('successful_selectors', 0)
            success_rate_num = statistics.get('success_rate', 0)
            success_rate_str = f"{success_rate_num:.0f}%"
            
            # Perform actual scraping to get sample data
            scraping_result = scraper.scrape(url)
            
            # Extract sample data and calculate items found
            sample_data = []
            fields_extracted = []
            items_found = 0
            title = ""
            
            if scraping_result.get('status') == 'success':
                scraped_data = scraping_result.get('data', {})
                items_found = scraping_result.get('items_count', 0)
                
                # Build sample data from scraped results
                for field_name, field_value in scraped_data.items():
                    if field_value:  # Only include fields with actual data
                        fields_extracted.append(field_name)
                        
                        # Handle different data types for sample display
                        if isinstance(field_value, list):
                            if field_value:  # Non-empty list
                                sample_data.append({
                                    "field": field_name,
                                    "value": field_value[0] if len(field_value) == 1 else field_value[:3],  # Show first item or first 3 items
                                    "type": "list",
                                    "count": len(field_value)
                                })
                                items_found = max(items_found, len(field_value))
                        else:
                            sample_data.append({
                                "field": field_name,
                                "value": str(field_value)[:200] + ("..." if len(str(field_value)) > 200 else ""),  # Truncate long values
                                "type": "string"
                            })
                        
                        # Extract title if it's a common field name
                        if field_name.lower() in ['title', 'name', 'heading', 'headline'] and not title:
                            if isinstance(field_value, list) and field_value:
                                title = str(field_value[0])[:100]
                            else:
                                title = str(field_value)[:100]
            
            # If we don't have items_found from scraping, estimate from selector results
            if items_found == 0:
                # Look for selectors that found multiple elements
                for field_name, result in selector_results.items():
                    element_count = result.get('element_count', 0)
                    if element_count > items_found:
                        items_found = element_count
            
            # Ensure we have at least 1 item if any selectors worked
            if items_found == 0 and successful_selectors > 0:
                items_found = 1
            
            # Extract page title from selector results if not found in scraped data
            if not title:
                for field_name, result in selector_results.items():
                    if (field_name.lower() in ['title', 'name', 'heading', 'headline'] and 
                        result.get('found') and result.get('sample_value')):
                        title = result['sample_value'][:100]
                        break
            
            # Fallback title
            if not title:
                title = f"Preview for {url.split('/')[2] if '/' in url else url}"
            
            # Build comprehensive response
            preview_response = {
                "url": url,
                "template_id": template_id,
                "success": True,
                "preview": {
                    "count": items_found,
                    "success_rate": success_rate_str,
                    "sample_data": sample_data
                },
                "preview_data": {
                    "title": title,
                    "items_found": items_found,
                    "selectors_matched": successful_selectors,
                    "sample_data": sample_data,
                    "fields_extracted": fields_extracted,
                    "validation_results": {
                        "template_valid": validation_result.get('valid', False),
                        "selectors_working": successful_selectors,
                        "total_selectors": total_selectors,
                        "success_rate": success_rate_num,
                        "detailed_results": selector_results
                    }
                }
            }
            
            return preview_response
            
        except Exception as e:
            # Return error response with consistent structure
            return {
                "url": url,
                "template_id": template_id,
                "success": False,
                "error": f"Preview failed: {str(e)}",
                "preview": {
                    "count": 0,
                    "success_rate": "0%",
                    "sample_data": []
                },
                "preview_data": {
                    "title": "",
                    "items_found": 0,
                    "selectors_matched": 0,
                    "sample_data": [],
                    "fields_extracted": [],
                    "validation_results": {"error": str(e)}
                }
            }
    
    def _broadcast_job_progress(self, job_id: str, progress: int, items_scraped: int, items_failed: int):
        """Broadcast job progress updates via Eel to connected clients."""
        try:
            import eel
            # Check if Eel is initialized and has the broadcast function
            # Use getattr to safely call the function if it exists (dynamic Eel functions)
            broadcast_func = getattr(eel, 'broadcast_job_progress', None)
            if broadcast_func:
                broadcast_func({
                    'job_id': job_id,
                    'progress': progress,
                    'items_scraped': items_scraped,
                    'items_failed': items_failed,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        except Exception as e:
            # Don't let broadcast failures affect the scraping process
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to broadcast progress for job {job_id}: {e}")