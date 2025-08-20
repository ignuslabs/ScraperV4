#!/usr/bin/env python3
"""
ScraperV4 Python Async API Client

This module provides a comprehensive async Python client for interacting with 
ScraperV4's REST API. It includes all major functionality with proper error 
handling, retry mechanisms, and async/await support.

Features:
- Async/await support for non-blocking operations
- Comprehensive API coverage (templates, jobs, data export)
- Built-in retry logic with exponential backoff
- Real-time job monitoring with progress callbacks
- Streaming data export for large datasets
- Connection pooling and session management
- Type hints and detailed documentation

Usage:
    from scraperv4_client import ScraperV4AsyncClient
    
    async def main():
        client = ScraperV4AsyncClient("http://localhost:8080")
        templates = await client.list_templates()
        print(f"Found {len(templates)} templates")

Requirements:
    pip install aiohttp aiofiles typing-extensions
"""

import asyncio
import aiohttp
import aiofiles
import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable, AsyncIterator, Union
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperV4APIError(Exception):
    """Base exception for ScraperV4 API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ScraperV4AsyncClient:
    """
    Async client for ScraperV4 REST API.
    
    Provides comprehensive access to all ScraperV4 functionality with async/await support,
    automatic retries, and robust error handling.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the async client.
        
        Args:
            base_url: ScraperV4 server URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            session: Optional aiohttp session (will create if not provided)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session = session
        self._own_session = session is None
        
    async def __aenter__(self):
        """Async context manager entry."""
        if self._own_session:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._own_session and self._session:
            await self._session.close()
    
    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if not self._session:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON payload for request body
            params: Query parameters
            **kwargs: Additional aiohttp arguments
            
        Returns:
            Response JSON data
            
        Raises:
            ScraperV4APIError: On API errors or network failures
        """
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(
                    method, url, json=json_data, params=params, **kwargs
                ) as response:
                    
                    # Handle non-JSON responses
                    if response.content_type != 'application/json':
                        text = await response.text()
                        if not response.ok:
                            raise ScraperV4APIError(
                                f"HTTP {response.status}: {text}",
                                status_code=response.status
                            )
                        return {"data": text, "content_type": response.content_type}
                    
                    # Parse JSON response
                    data = await response.json()
                    
                    if not response.ok:
                        error_msg = data.get('error', f"HTTP {response.status}")
                        raise ScraperV4APIError(
                            error_msg,
                            status_code=response.status,
                            response_data=data
                        )
                    
                    return data
                    
            except aiohttp.ClientError as e:
                if attempt == self.max_retries:
                    raise ScraperV4APIError(f"Network error after {self.max_retries} retries: {e}")
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
        
        raise ScraperV4APIError(f"Max retries ({self.max_retries}) exceeded")
    
    # Template Management Methods
    
    async def list_templates(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        List all scraping templates.
        
        Args:
            include_inactive: Include inactive templates in results
            
        Returns:
            List of template dictionaries
        """
        params = {"include_inactive": include_inactive} if include_inactive else None
        response = await self._make_request("GET", "/api/templates", params=params)
        return response.get("templates", [])
    
    async def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get a specific template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template dictionary
        """
        response = await self._make_request("GET", f"/api/templates/{template_id}")
        return response.get("template", {})
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new scraping template.
        
        Args:
            template_data: Template configuration dictionary
            
        Returns:
            Created template with assigned ID
        """
        response = await self._make_request("POST", "/api/templates", json_data=template_data)
        return response
    
    async def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing template.
        
        Args:
            template_id: Template identifier
            template_data: Updated template configuration
            
        Returns:
            Updated template dictionary
        """
        response = await self._make_request("PUT", f"/api/templates/{template_id}", json_data=template_data)
        return response
    
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if deletion was successful
        """
        await self._make_request("DELETE", f"/api/templates/{template_id}")
        return True
    
    async def test_template(self, template_id: str, test_url: str) -> Dict[str, Any]:
        """
        Test a template against a URL.
        
        Args:
            template_id: Template identifier
            test_url: URL to test the template against
            
        Returns:
            Test results including extracted data and validation
        """
        test_data = {"url": test_url}
        response = await self._make_request("POST", f"/api/templates/{template_id}/test", json_data=test_data)
        return response
    
    # Job Management Methods
    
    async def create_job(
        self,
        name: str,
        template_id: str,
        target_url: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new scraping job.
        
        Args:
            name: Job name/description
            template_id: Template to use for scraping
            target_url: URL to scrape
            config: Optional job configuration overrides
            
        Returns:
            Created job dictionary with job ID
        """
        job_data = {
            "name": name,
            "template_id": template_id,
            "target_url": target_url,
            "config": config or {}
        }
        response = await self._make_request("POST", "/api/scraping/jobs", json_data=job_data)
        return response
    
    async def start_job(self, job_id: str) -> Dict[str, Any]:
        """
        Start a scraping job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        response = await self._make_request("POST", f"/api/scraping/start", json_data={"job_id": job_id})
        return response
    
    async def stop_job(self, job_id: str) -> Dict[str, Any]:
        """
        Stop a running job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Updated job status
        """
        response = await self._make_request("POST", f"/api/scraping/stop/{job_id}")
        return response
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary with progress information
        """
        response = await self._make_request("GET", f"/api/scraping/status/{job_id}")
        return response
    
    async def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List scraping jobs with optional filtering.
        
        Args:
            status: Filter by job status (running, completed, failed, etc.)
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip (for pagination)
            
        Returns:
            Dictionary with jobs list and pagination info
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        
        response = await self._make_request("GET", "/api/scraping/jobs", params=params)
        return response
    
    async def monitor_job(
        self,
        job_id: str,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        Monitor a job until completion with optional progress callback.
        
        Args:
            job_id: Job identifier
            callback: Optional callback function for progress updates
            poll_interval: Polling interval in seconds
            
        Returns:
            Final job status
        """
        logger.info(f"Monitoring job {job_id}")
        
        while True:
            status = await self.get_job_status(job_id)
            
            if callback:
                callback(status)
            
            job_status = status.get("status", "unknown")
            if job_status in ["completed", "failed", "stopped", "error"]:
                logger.info(f"Job {job_id} finished with status: {job_status}")
                return status
            
            logger.debug(f"Job {job_id} - Status: {job_status}, Progress: {status.get('progress', 0)}%")
            await asyncio.sleep(poll_interval)
    
    # Data Access Methods
    
    async def get_job_results(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get scraped results for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of scraped data items
        """
        response = await self._make_request("GET", f"/api/data/results/{job_id}")
        return response.get("results", [])
    
    async def export_job_data(
        self,
        job_id: str,
        format: str = "json",
        include_metadata: bool = True,
        output_file: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Export job data to specified format.
        
        Args:
            job_id: Job identifier
            format: Export format (json, csv, xlsx)
            include_metadata: Include job metadata in export
            output_file: Optional local file path to save export
            
        Returns:
            Export result dictionary or file path if saved locally
        """
        export_data = {
            "job_id": job_id,
            "format": format,
            "include_metadata": include_metadata
        }
        
        response = await self._make_request("POST", "/api/data/export", json_data=export_data)
        
        if output_file and "file_path" in response:
            # Download the exported file
            file_url = response["file_path"]
            if not file_url.startswith("http"):
                file_url = urljoin(self.base_url, file_url)
            
            async with self.session.get(file_url) as file_response:
                if file_response.ok:
                    async with aiofiles.open(output_file, 'wb') as f:
                        async for chunk in file_response.content.iter_chunked(8192):
                            await f.write(chunk)
                    return output_file
                else:
                    raise ScraperV4APIError(f"Failed to download export file: {file_response.status}")
        
        return response
    
    async def stream_job_results(self, job_id: str, chunk_size: int = 100) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Stream job results in chunks for large datasets.
        
        Args:
            job_id: Job identifier
            chunk_size: Number of items per chunk
            
        Yields:
            Chunks of scraped data items
        """
        offset = 0
        
        while True:
            params = {"limit": chunk_size, "offset": offset}
            response = await self._make_request("GET", f"/api/data/results/{job_id}", params=params)
            
            results = response.get("results", [])
            if not results:
                break
            
            yield results
            
            # Check if we've reached the end
            total_results = response.get("total", 0)
            if offset + len(results) >= total_results:
                break
            
            offset += chunk_size
    
    # Preview and Testing Methods
    
    async def preview_scraping(self, url: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Preview scraping results without creating a full job.
        
        Args:
            url: URL to preview
            template_id: Optional template ID to use
            
        Returns:
            Preview results with extracted data
        """
        preview_data = {"url": url}
        if template_id:
            preview_data["template_id"] = template_id
        
        response = await self._make_request("POST", "/api/scraping/preview", json_data=preview_data)
        return response
    
    # Statistics and Monitoring Methods
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide scraping statistics.
        
        Returns:
            System statistics dictionary
        """
        response = await self._make_request("GET", "/api/data/stats")
        return response
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status information
        """
        response = await self._make_request("GET", "/api/health")
        return response


class ScraperV4JobManager:
    """
    High-level job management utility for common scraping workflows.
    """
    
    def __init__(self, client: ScraperV4AsyncClient):
        """
        Initialize job manager with a client instance.
        
        Args:
            client: ScraperV4AsyncClient instance
        """
        self.client = client
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
    
    async def scrape_url_with_template(
        self,
        url: str,
        template_id: str,
        job_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        monitor: bool = True,
        export_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete scraping workflow: create job, monitor, and optionally export.
        
        Args:
            url: URL to scrape
            template_id: Template to use
            job_name: Optional job name (auto-generated if not provided)
            config: Optional job configuration
            monitor: Whether to monitor job until completion
            export_format: Optional export format (json, csv, xlsx)
            
        Returns:
            Complete job results with optional export info
        """
        # Generate job name if not provided
        if not job_name:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            domain = urlparse(url).netloc or "unknown"
            job_name = f"Scrape_{domain}_{timestamp}"
        
        # Create job
        logger.info(f"Creating job: {job_name}")
        job = await self.client.create_job(job_name, template_id, url, config)
        job_id = job["job_id"]
        
        # Start job
        logger.info(f"Starting job: {job_id}")
        await self.client.start_job(job_id)
        
        # Monitor if requested
        final_status = None
        if monitor:
            def progress_callback(status: Dict[str, Any]):
                progress = status.get("progress", 0)
                items = status.get("items_scraped", 0)
                logger.info(f"Job {job_id} - Progress: {progress}%, Items: {items}")
            
            final_status = await self.client.monitor_job(job_id, progress_callback)
        
        # Get results
        results = []
        if not final_status or final_status.get("status") == "completed":
            logger.info(f"Getting results for job: {job_id}")
            results = await self.client.get_job_results(job_id)
        
        # Export if requested
        export_info = None
        if export_format and results:
            logger.info(f"Exporting results in {export_format} format")
            export_info = await self.client.export_job_data(job_id, export_format)
        
        return {
            "job_id": job_id,
            "job_name": job_name,
            "status": final_status,
            "results": results,
            "export_info": export_info,
            "total_items": len(results)
        }
    
    async def batch_scrape_urls(
        self,
        urls: List[str],
        template_id: str,
        max_concurrent: int = 3,
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently with rate limiting.
        
        Args:
            urls: List of URLs to scrape
            template_id: Template to use for all URLs
            max_concurrent: Maximum concurrent jobs
            config: Optional configuration for all jobs
            
        Returns:
            List of job results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single_url(url: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self.scrape_url_with_template(
                        url, template_id, config=config, monitor=True
                    )
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return {"url": url, "error": str(e), "success": False}
        
        # Create tasks for all URLs
        tasks = [scrape_single_url(url) for url in urls]
        
        # Execute with progress tracking
        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            logger.info(f"Completed {i + 1}/{len(urls)} URLs")
        
        return results


async def main():
    """
    Example usage of the ScraperV4 async client.
    """
    # Initialize client
    async with ScraperV4AsyncClient("http://localhost:8080") as client:
        
        try:
            # Health check
            health = await client.health_check()
            print(f"✅ API Health: {health}")
            
            # List templates
            templates = await client.list_templates()
            print(f"📋 Found {len(templates)} templates")
            
            if templates:
                template_id = templates[0]["id"]
                
                # Test template
                test_url = "https://example.com"
                print(f"🧪 Testing template {template_id} on {test_url}")
                
                test_result = await client.test_template(template_id, test_url)
                print(f"✅ Test result: {test_result.get('success', False)}")
                
                # Create and run a job
                job = await client.create_job(
                    name="Example scraping job",
                    template_id=template_id,
                    target_url=test_url,
                    config={
                        "use_proxy": False,
                        "delay_range": [1, 2]
                    }
                )
                
                job_id = job["job_id"]
                print(f"📋 Created job: {job_id}")
                
                # Start job
                await client.start_job(job_id)
                print(f"🚀 Started job: {job_id}")
                
                # Monitor job with progress callback
                def progress_callback(status):
                    progress = status.get("progress", 0)
                    items = status.get("items_scraped", 0)
                    print(f"📊 Progress: {progress}%, Items: {items}")
                
                final_status = await client.monitor_job(job_id, progress_callback)
                print(f"✅ Job completed with status: {final_status.get('status')}")
                
                # Get results
                if final_status.get("status") == "completed":
                    results = await client.get_job_results(job_id)
                    print(f"📄 Retrieved {len(results)} results")
                    
                    # Export data
                    export_info = await client.export_job_data(job_id, "json")
                    print(f"💾 Exported data: {export_info}")
            
            # High-level job manager example
            job_manager = ScraperV4JobManager(client)
            
            # Single URL scraping with export
            if templates:
                complete_result = await job_manager.scrape_url_with_template(
                    url="https://example.com",
                    template_id=templates[0]["id"],
                    job_name="High-level scraping test",
                    export_format="json"
                )
                print(f"🎯 Complete workflow result: {complete_result['total_items']} items")
            
        except ScraperV4APIError as e:
            print(f"❌ API Error: {e}")
            if e.status_code:
                print(f"   Status Code: {e.status_code}")
            if e.response_data:
                print(f"   Response: {e.response_data}")
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())