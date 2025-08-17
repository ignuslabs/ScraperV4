#!/usr/bin/env python3
"""
ScraperV4 Python Client Library
===============================

Complete Python client implementation for ScraperV4 API with all features:
- Template management (CRUD operations)
- Job management and monitoring
- Data export in multiple formats
- Async job handling
- Error handling and retries
- Webhook support

Prerequisites:
- ScraperV4 server running
- requests library: pip install requests
- Optional: aiohttp for async support: pip install aiohttp

Usage:
    from scraperv4_client import ScraperV4Client
    
    client = ScraperV4Client("http://localhost:5000")
    
    # Create and run a simple scraping job
    template_id = client.create_template(template_data)
    job_id = client.start_job(template_id, "https://example.com")
    results = client.wait_for_completion(job_id)
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin
import asyncio
import aiohttp

class ScraperV4Error(Exception):
    """Base exception for ScraperV4 client errors"""
    pass

class ScraperV4APIError(ScraperV4Error):
    """API-related errors"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class ScraperV4Client:
    """
    Comprehensive Python client for ScraperV4 API
    
    Provides both synchronous and asynchronous methods for:
    - Template management
    - Job execution and monitoring
    - Data export and retrieval
    - System status and configuration
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: str = None):
        """
        Initialize ScraperV4 client
        
        Args:
            base_url: ScraperV4 server URL
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ScraperV4-Python-Client/1.0"
        })
        
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Request configuration
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            ScraperV4APIError: On API errors
        """
        url = urljoin(f"{self.api_url}/", endpoint.lstrip('/'))
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Handle different response types
                if response.status_code == 204:  # No content
                    return {}
                
                if not response.content:
                    return {}
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {"content": response.text}
                
                if response.status_code >= 400:
                    error_msg = data.get("error", f"HTTP {response.status_code}")
                    raise ScraperV4APIError(
                        error_msg, 
                        response.status_code, 
                        data
                    )
                
                return data
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ScraperV4Error(f"Request failed after {self.max_retries} attempts: {str(e)}")
                
                self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
    # Template Management Methods
    
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """
        Create a new scraping template
        
        Args:
            template_data: Template configuration dictionary
            
        Returns:
            Template ID
        """
        response = self._make_request("POST", "/templates", json=template_data)
        return response["id"]
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get template by ID"""
        return self._make_request("GET", f"/templates/{template_id}")
    
    def list_templates(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all templates with pagination"""
        params = {"limit": limit, "offset": offset}
        response = self._make_request("GET", "/templates", params=params)
        return response.get("templates", [])
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing template"""
        return self._make_request("PUT", f"/templates/{template_id}", json=template_data)
    
    def delete_template(self, template_id: str) -> bool:
        """Delete template by ID"""
        self._make_request("DELETE", f"/templates/{template_id}")
        return True
    
    def test_template(self, template_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Test template against a URL without saving"""
        data = {"template": template_data, "url": url}
        return self._make_request("POST", "/templates/test", json=data)
    
    # Job Management Methods
    
    def start_job(self, template_id: str, url: str, options: Dict[str, Any] = None) -> str:
        """
        Start a new scraping job
        
        Args:
            template_id: ID of template to use
            url: Target URL to scrape
            options: Additional job options
            
        Returns:
            Job ID
        """
        job_data = {
            "template_id": template_id,
            "url": url,
            "options": options or {}
        }
        response = self._make_request("POST", "/scrape", json=job_data)
        return response["job_id"]
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current job status and progress"""
        return self._make_request("GET", f"/jobs/{job_id}/status")
    
    def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Get job results (only available when job is completed)"""
        return self._make_request("GET", f"/jobs/{job_id}/results")
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        self._make_request("POST", f"/jobs/{job_id}/cancel")
        return True
    
    def list_jobs(self, status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List jobs with optional status filter"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        response = self._make_request("GET", "/jobs", params=params)
        return response.get("jobs", [])
    
    def wait_for_completion(self, job_id: str, poll_interval: float = 2.0, timeout: float = 300.0) -> Dict[str, Any]:
        """
        Wait for job completion and return results
        
        Args:
            job_id: Job ID to monitor
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            
        Returns:
            Job results
            
        Raises:
            ScraperV4Error: On job failure or timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            self.logger.info(f"Job {job_id}: {status['status']} - {status.get('progress', 0)}% complete")
            
            if status["status"] == "completed":
                return self.get_job_results(job_id)
            elif status["status"] in ["failed", "cancelled"]:
                raise ScraperV4Error(f"Job {status['status']}: {status.get('error', 'Unknown error')}")
            
            time.sleep(poll_interval)
        
        raise ScraperV4Error(f"Job {job_id} did not complete within {timeout} seconds")
    
    # Data Export Methods
    
    def export_job_data(self, job_id: str, format: str = "json", filename: str = None) -> bytes:
        """
        Export job data in specified format
        
        Args:
            job_id: Job ID
            format: Export format (json, csv, xlsx, xml)
            filename: Optional custom filename
            
        Returns:
            Exported data as bytes
        """
        params = {"format": format}
        if filename:
            params["filename"] = filename
            
        url = urljoin(f"{self.api_url}/", f"jobs/{job_id}/export")
        response = self.session.get(url, params=params)
        
        if response.status_code >= 400:
            raise ScraperV4APIError(f"Export failed: HTTP {response.status_code}")
        
        return response.content
    
    def save_export(self, job_id: str, format: str = "json", filename: str = None) -> str:
        """
        Export and save job data to file
        
        Returns:
            Saved filename
        """
        data = self.export_job_data(job_id, format, filename)
        
        if not filename:
            filename = f"scraperv4_job_{job_id}.{format}"
        
        with open(filename, 'wb') as f:
            f.write(data)
        
        self.logger.info(f"Data exported to {filename}")
        return filename
    
    # System Status Methods
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system health and status information"""
        return self._make_request("GET", "/status")
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Get current system configuration"""
        return self._make_request("GET", "/settings")
    
    def update_system_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update system configuration"""
        return self._make_request("PUT", "/settings", json=settings)
    
    # Webhook Methods
    
    def register_webhook(self, webhook_data: Dict[str, Any]) -> str:
        """Register a webhook for job notifications"""
        response = self._make_request("POST", "/webhooks", json=webhook_data)
        return response["webhook_id"]
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all registered webhooks"""
        response = self._make_request("GET", "/webhooks")
        return response.get("webhooks", [])
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        self._make_request("DELETE", f"/webhooks/{webhook_id}")
        return True

    # Batch Operations
    
    def start_batch_jobs(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """
        Start multiple jobs at once
        
        Args:
            jobs: List of job configurations
            
        Returns:
            List of job IDs
        """
        response = self._make_request("POST", "/batch/scrape", json={"jobs": jobs})
        return response["job_ids"]
    
    def monitor_batch_jobs(self, job_ids: List[str], poll_interval: float = 5.0) -> Dict[str, Dict[str, Any]]:
        """
        Monitor multiple jobs until completion
        
        Returns:
            Dictionary mapping job IDs to their results
        """
        results = {}
        remaining_jobs = set(job_ids)
        
        while remaining_jobs:
            for job_id in list(remaining_jobs):
                try:
                    status = self.get_job_status(job_id)
                    
                    if status["status"] == "completed":
                        results[job_id] = self.get_job_results(job_id)
                        remaining_jobs.remove(job_id)
                        self.logger.info(f"Job {job_id} completed successfully")
                    elif status["status"] in ["failed", "cancelled"]:
                        results[job_id] = {"error": status.get("error", "Job failed")}
                        remaining_jobs.remove(job_id)
                        self.logger.error(f"Job {job_id} failed: {status.get('error')}")
                
                except Exception as e:
                    self.logger.error(f"Error checking job {job_id}: {str(e)}")
            
            if remaining_jobs:
                time.sleep(poll_interval)
        
        return results

# Async Client Implementation
class AsyncScraperV4Client:
    """Asynchronous version of ScraperV4Client using aiohttp"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ScraperV4-Python-AsyncClient/1.0"
        }
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Async version of _make_request"""
        url = urljoin(f"{self.api_url}/", endpoint.lstrip('/'))
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    text = await response.text()
                    raise ScraperV4APIError(f"HTTP {response.status}: {text}", response.status)
                
                if response.status == 204:
                    return {}
                
                return await response.json()
    
    async def start_job_async(self, template_id: str, url: str, options: Dict[str, Any] = None) -> str:
        """Async version of start_job"""
        job_data = {
            "template_id": template_id,
            "url": url,
            "options": options or {}
        }
        response = await self._make_request("POST", "/scrape", json=job_data)
        return response["job_id"]
    
    async def wait_for_completion_async(self, job_id: str, poll_interval: float = 2.0) -> Dict[str, Any]:
        """Async version of wait_for_completion"""
        while True:
            status = await self._make_request("GET", f"/jobs/{job_id}/status")
            
            if status["status"] == "completed":
                return await self._make_request("GET", f"/jobs/{job_id}/results")
            elif status["status"] in ["failed", "cancelled"]:
                raise ScraperV4Error(f"Job {status['status']}: {status.get('error')}")
            
            await asyncio.sleep(poll_interval)

# Example usage and demonstrations
def example_basic_usage():
    """Basic usage example"""
    print("ScraperV4 Python Client - Basic Usage Example")
    print("=" * 50)
    
    # Initialize client
    client = ScraperV4Client("http://localhost:5000")
    
    # Create a simple template
    template = {
        "name": "Example Template",
        "config": {
            "selectors": {
                "title": {"css": "h1", "attribute": "text"}
            }
        }
    }
    
    try:
        # Create template
        template_id = client.create_template(template)
        print(f"✓ Template created: {template_id}")
        
        # Start scraping job
        job_id = client.start_job(template_id, "https://example.com")
        print(f"✓ Job started: {job_id}")
        
        # Wait for completion
        results = client.wait_for_completion(job_id)
        print(f"✓ Job completed with {len(results.get('data', {}))} items")
        
        # Export to CSV
        filename = client.save_export(job_id, format="csv")
        print(f"✓ Results exported to {filename}")
        
    except ScraperV4Error as e:
        print(f"✗ Error: {str(e)}")

def example_batch_processing():
    """Batch processing example"""
    print("Batch Processing Example")
    print("=" * 30)
    
    client = ScraperV4Client()
    
    # Create multiple jobs
    jobs = [
        {"template_id": "template_1", "url": "https://site1.com"},
        {"template_id": "template_1", "url": "https://site2.com"},
        {"template_id": "template_2", "url": "https://site3.com"}
    ]
    
    try:
        job_ids = client.start_batch_jobs(jobs)
        print(f"✓ Started {len(job_ids)} jobs")
        
        results = client.monitor_batch_jobs(job_ids)
        
        successful = [jid for jid, result in results.items() if "error" not in result]
        print(f"✓ {len(successful)}/{len(job_ids)} jobs completed successfully")
        
    except ScraperV4Error as e:
        print(f"✗ Batch processing error: {str(e)}")

async def example_async_usage():
    """Async usage example"""
    print("Async Usage Example")
    print("=" * 20)
    
    client = AsyncScraperV4Client()
    
    try:
        job_id = await client.start_job_async("template_id", "https://example.com")
        print(f"✓ Async job started: {job_id}")
        
        results = await client.wait_for_completion_async(job_id)
        print(f"✓ Async job completed")
        
    except ScraperV4Error as e:
        print(f"✗ Async error: {str(e)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    example_basic_usage()
    print("\n")
    example_batch_processing()
    print("\n")
    
    # Run async example
    try:
        asyncio.run(example_async_usage())
    except ImportError:
        print("aiohttp not installed - skipping async example")