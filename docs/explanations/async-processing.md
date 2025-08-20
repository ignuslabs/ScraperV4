# Asynchronous Processing

This document explains how ScraperV4 leverages asynchronous processing for efficient web scraping, job management, and real-time user interaction. Understanding async patterns is crucial for developing high-performance scraping applications.

## The Challenge of Synchronous Web Scraping

### Traditional Synchronous Approach

In synchronous web scraping, each operation blocks until completion:

```python
# Synchronous scraping - blocks on each request
def scrape_urls_sync(urls):
    results = []
    for url in urls:
        response = requests.get(url)  # Blocks here
        data = extract_data(response)  # Blocks here
        results.append(data)
    return results
```

**Problems with Synchronous Approach**:
- **Thread Blocking**: Each request waits for network I/O
- **Poor Resource Utilization**: CPU sits idle during network calls
- **Linear Scaling**: Time increases linearly with number of URLs
- **Unresponsive UI**: User interface freezes during operations
- **Limited Concurrency**: Cannot efficiently handle multiple jobs

### Asynchronous Solution

ScraperV4 uses `asyncio` for non-blocking operations:

```python
# Asynchronous scraping - concurrent requests
async def scrape_urls_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_single_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

**Benefits of Asynchronous Approach**:
- **Non-blocking I/O**: CPU can process other tasks during network waits
- **High Concurrency**: Handle hundreds of concurrent requests
- **Better Resource Utilization**: Maximize CPU and network usage
- **Responsive UI**: User interface remains interactive
- **Scalable Performance**: Performance scales with available resources

## ScraperV4's Async Architecture

### Event Loop Management

ScraperV4 uses a dedicated event loop for async operations:

```python
class AsyncJobProcessor:
    def __init__(self):
        self.loop = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    def start(self):
        """Start the async processing loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Start the main processing coroutine
        self.loop.create_task(self._process_job_queue())
        self.loop.run_forever()
    
    async def _process_job_queue(self):
        """Main async loop for processing jobs."""
        while True:
            try:
                # Check for new jobs
                pending_jobs = await self.get_pending_jobs()
                
                # Process jobs concurrently
                if pending_jobs:
                    tasks = [self.process_job(job) for job in pending_jobs]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next check
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in job processing loop: {e}")
                await asyncio.sleep(5)  # Back off on errors
```

### Concurrent Request Management

ScraperV4 controls concurrency to avoid overwhelming target servers:

```python
class ConcurrentScraper:
    def __init__(self, max_concurrent=10, delay_range=(1, 3)):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay_range = delay_range
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=50)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str, context: ScrapingContext) -> PageResult:
        """Scrape a single URL with concurrency control."""
        async with self.semaphore:  # Limit concurrent requests
            try:
                # Apply random delay
                delay = random.uniform(*self.delay_range)
                await asyncio.sleep(delay)
                
                # Perform the actual scraping
                result = await self._fetch_and_extract(url, context)
                
                return result
                
            except Exception as e:
                return PageResult(success=False, url=url, error=str(e))
    
    async def scrape_multiple_urls(self, urls: List[str], context: ScrapingContext) -> List[PageResult]:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_url(url, context) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(PageResult(success=False, error=str(result)))
            else:
                processed_results.append(result)
        
        return processed_results
```

## Job Management and Lifecycle

### Asynchronous Job States

Jobs in ScraperV4 progress through async-friendly states:

```python
class AsyncJobManager:
    def __init__(self):
        self.active_jobs = {}
        self.job_tasks = {}
        self.progress_callbacks = {}
    
    async def start_job(self, job: JobData) -> str:
        """Start a job asynchronously."""
        
        # Update job status
        await self.update_job_status(job.id, 'running')
        
        # Create async task for job processing
        task = asyncio.create_task(self._execute_job(job))
        self.job_tasks[job.id] = task
        
        # Setup progress monitoring
        progress_task = asyncio.create_task(self._monitor_job_progress(job.id))
        
        # Don't await - let job run in background
        return job.id
    
    async def _execute_job(self, job: JobData) -> JobResult:
        """Execute job asynchronously."""
        try:
            # Prepare scraping context
            context = await self._prepare_scraping_context(job)
            
            # Discover URLs to scrape
            urls = await self._discover_urls(job.target_url, context)
            
            # Process URLs in batches
            batch_size = job.options.get('batch_size', 10)
            all_results = []
            
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                
                # Process batch concurrently
                async with ConcurrentScraper() as scraper:
                    batch_results = await scraper.scrape_multiple_urls(batch_urls, context)
                
                all_results.extend(batch_results)
                
                # Update progress
                progress = min(100, len(all_results) * 100 // len(urls))
                await self.update_job_progress(job.id, progress)
                
                # Check for cancellation
                if await self._is_job_cancelled(job.id):
                    break
            
            # Store results
            result_id = await self._store_results(job.id, all_results)
            
            # Mark job as completed
            await self.update_job_status(job.id, 'completed')
            
            return JobResult(job.id, result_id, all_results)
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            await self.update_job_status(job.id, 'failed', str(e))
            raise
        
        finally:
            # Cleanup
            self.active_jobs.pop(job.id, None)
            self.job_tasks.pop(job.id, None)
```

### Real-time Progress Updates

Progress updates are sent asynchronously to the UI:

```python
class ProgressManager:
    def __init__(self):
        self.progress_callbacks = {}
        self.update_queue = asyncio.Queue()
        
        # Start background task for progress updates
        asyncio.create_task(self._process_progress_updates())
    
    async def update_job_progress(self, job_id: str, progress: int, details: Dict = None):
        """Update job progress asynchronously."""
        
        update_data = {
            'job_id': job_id,
            'progress': progress,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'details': details or {}
        }
        
        # Queue update for processing
        await self.update_queue.put(update_data)
    
    async def _process_progress_updates(self):
        """Process progress updates in background."""
        while True:
            try:
                # Get next update
                update = await self.update_queue.get()
                
                # Update job data
                await self._persist_progress_update(update)
                
                # Notify UI via EEL (non-blocking)
                asyncio.create_task(self._notify_ui_progress(update))
                
                # Notify any registered callbacks
                await self._notify_progress_callbacks(update)
                
                # Mark task as done
                self.update_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing progress update: {e}")
    
    async def _notify_ui_progress(self, update):
        """Notify UI of progress update."""
        try:
            # Use EEL to send update to frontend
            eel.update_job_progress(
                update['job_id'],
                update['progress'],
                update['details']
            )
        except Exception as e:
            logger.error(f"Failed to notify UI: {e}")
```

## Integration with EEL Framework

### Bridging Async and Sync Worlds

EEL operates synchronously, but ScraperV4 needs async operations:

```python
class EelAsyncBridge:
    def __init__(self):
        self.loop = None
        self.bridge_thread = None
    
    def start_bridge(self):
        """Start the async bridge in a separate thread."""
        self.bridge_thread = threading.Thread(target=self._run_async_loop)
        self.bridge_thread.daemon = True
        self.bridge_thread.start()
    
    def _run_async_loop(self):
        """Run async event loop in separate thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def run_async(self, coro):
        """Run async coroutine from sync context."""
        if self.loop is None:
            raise RuntimeError("Async bridge not started")
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=30)  # 30 second timeout

# Global bridge instance
eel_bridge = EelAsyncBridge()

@eel.expose
def start_scraping_job_sync(job_data):
    """EEL-exposed function that runs async job."""
    try:
        # Convert to async and run
        coro = start_scraping_job_async(job_data)
        job_id = eel_bridge.run_async(coro)
        
        return {'success': True, 'job_id': job_id}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

async def start_scraping_job_async(job_data):
    """Actual async implementation."""
    # Create job
    service = container.resolve(ScrapingService)
    job = await service.create_job_async(job_data)
    
    # Start async execution
    job_id = await service.start_job_async(job.id)
    
    return job_id
```

### Non-blocking UI Updates

The UI receives updates without blocking the scraping process:

```python
class UINotificationManager:
    def __init__(self):
        self.notification_queue = asyncio.Queue()
        asyncio.create_task(self._process_notifications())
    
    async def notify_job_started(self, job_id: str, job_name: str):
        """Notify UI that job has started."""
        notification = {
            'type': 'job_started',
            'job_id': job_id,
            'job_name': job_name,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        await self.notification_queue.put(notification)
    
    async def notify_job_progress(self, job_id: str, progress: int, details: Dict):
        """Notify UI of job progress."""
        notification = {
            'type': 'job_progress',
            'job_id': job_id,
            'progress': progress,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        await self.notification_queue.put(notification)
    
    async def _process_notifications(self):
        """Process UI notifications asynchronously."""
        while True:
            try:
                notification = await self.notification_queue.get()
                
                # Send to UI based on notification type
                if notification['type'] == 'job_started':
                    eel.on_job_started(notification)
                elif notification['type'] == 'job_progress':
                    eel.on_job_progress(notification)
                elif notification['type'] == 'job_completed':
                    eel.on_job_completed(notification)
                
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing UI notification: {e}")
```

## Error Handling in Async Context

### Exception Propagation

Async operations require careful exception handling:

```python
async def safe_async_operation(operation, *args, **kwargs):
    """Safely execute async operation with proper error handling."""
    try:
        result = await operation(*args, **kwargs)
        return {'success': True, 'result': result}
    
    except asyncio.TimeoutError:
        return {'success': False, 'error': 'Operation timed out', 'error_type': 'timeout'}
    
    except aiohttp.ClientError as e:
        return {'success': False, 'error': f'Network error: {e}', 'error_type': 'network'}
    
    except Exception as e:
        logger.exception(f"Unexpected error in async operation: {e}")
        return {'success': False, 'error': str(e), 'error_type': 'unknown'}

async def robust_scraping_job(job: JobData) -> JobResult:
    """Execute scraping job with comprehensive error handling."""
    
    partial_results = []
    errors = []
    
    try:
        urls = await discover_urls(job.target_url)
        
        # Process URLs with individual error handling
        for url in urls:
            result = await safe_async_operation(scrape_single_url, url)
            
            if result['success']:
                partial_results.append(result['result'])
            else:
                errors.append({
                    'url': url,
                    'error': result['error'],
                    'error_type': result['error_type']
                })
        
        # Return results even if some URLs failed
        return JobResult(
            success=len(partial_results) > 0,
            results=partial_results,
            errors=errors,
            summary={
                'total_urls': len(urls),
                'successful': len(partial_results),
                'failed': len(errors),
                'success_rate': len(partial_results) / len(urls) if urls else 0
            }
        )
    
    except Exception as e:
        # Complete job failure
        return JobResult(
            success=False,
            results=[],
            errors=[{'error': str(e), 'error_type': 'job_failure'}],
            summary={'total_urls': 0, 'successful': 0, 'failed': 1, 'success_rate': 0}
        )
```

### Circuit Breaker Pattern

Prevent cascade failures in async operations:

```python
class AsyncCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    async def call(self, async_func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        
        if self.state == 'open':
            if time.time() - self.last_failure_time < self.timeout:
                raise CircuitBreakerOpen("Circuit breaker is open")
            else:
                self.state = 'half-open'
        
        try:
            result = await async_func(*args, **kwargs)
            
            # Success - reset circuit breaker
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
            
            raise e

# Usage in scraping
circuit_breaker = AsyncCircuitBreaker()

async def protected_scrape_url(url: str):
    """Scrape URL with circuit breaker protection."""
    return await circuit_breaker.call(scrape_url_raw, url)
```

## Performance Optimization

### Connection Pooling

Efficient connection management for async HTTP requests:

```python
class OptimizedHttpClient:
    def __init__(self):
        self.connector = aiohttp.TCPConnector(
            limit=100,              # Total connection pool size
            limit_per_host=30,      # Connections per host
            keepalive_timeout=30,   # Keep connections alive
            enable_cleanup_closed=True
        )
        
        self.timeout = aiohttp.ClientTimeout(
            total=30,               # Total request timeout
            connect=10,             # Connection timeout
            sock_read=20            # Socket read timeout
        )
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers={
                'User-Agent': 'ScraperV4/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.connector.close()
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make optimized GET request."""
        return await self.session.get(url, **kwargs)
```

### Memory Management

Prevent memory leaks in long-running async operations:

```python
async def memory_efficient_batch_processing(urls: List[str], batch_size: int = 50):
    """Process URLs in memory-efficient batches."""
    
    results = []
    
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]
        
        # Process batch
        async with OptimizedHttpClient() as client:
            batch_tasks = [process_url(client, url) for url in batch_urls]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Process results immediately to free memory
        for result in batch_results:
            if not isinstance(result, Exception):
                results.append(result)
                
                # Optional: Stream results to storage instead of keeping in memory
                # await stream_result_to_storage(result)
        
        # Clear batch from memory
        del batch_results
        del batch_tasks
        
        # Optional: Force garbage collection
        import gc
        gc.collect()
        
        # Small delay to prevent overwhelming the event loop
        await asyncio.sleep(0.1)
    
    return results
```

## Testing Async Code

### Async Test Patterns

Testing async code requires special considerations:

```python
import pytest
import pytest_asyncio

@pytest_asyncio.async_test
async def test_async_scraping():
    """Test async scraping functionality."""
    
    # Setup
    scraper = AsyncScraper()
    test_urls = ['http://example.com/page1', 'http://example.com/page2']
    
    # Execute
    results = await scraper.scrape_multiple_urls(test_urls)
    
    # Assert
    assert len(results) == 2
    assert all(result.success for result in results)

@pytest_asyncio.async_test
async def test_job_progress_updates():
    """Test real-time progress updates."""
    
    # Setup progress tracking
    progress_updates = []
    
    async def capture_progress(job_id, progress, details):
        progress_updates.append({'job_id': job_id, 'progress': progress})
    
    # Create job with progress callback
    job_manager = AsyncJobManager()
    job_manager.register_progress_callback('test-job', capture_progress)
    
    # Execute job
    job = JobData({'id': 'test-job', 'target_url': 'http://example.com'})
    await job_manager.start_job(job)
    
    # Wait for completion
    await asyncio.sleep(2)
    
    # Assert progress was tracked
    assert len(progress_updates) > 0
    assert progress_updates[-1]['progress'] == 100

class AsyncMockServer:
    """Mock server for testing async HTTP operations."""
    
    def __init__(self):
        self.app = web.Application()
        self.app.router.add_get('/test', self.test_handler)
        self.app.router.add_get('/slow', self.slow_handler)
        
    async def test_handler(self, request):
        return web.Response(text="Test response")
    
    async def slow_handler(self, request):
        await asyncio.sleep(2)  # Simulate slow response
        return web.Response(text="Slow response")
    
    async def start_server(self, port=8888):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        return runner

@pytest_asyncio.async_test
async def test_timeout_handling():
    """Test timeout handling in async operations."""
    
    # Start mock server
    mock_server = AsyncMockServer()
    runner = await mock_server.start_server()
    
    try:
        # Test normal request
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8888/test') as response:
                assert response.status == 200
        
        # Test timeout
        with pytest.raises(asyncio.TimeoutError):
            timeout = aiohttp.ClientTimeout(total=1)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('http://localhost:8888/slow') as response:
                    pass
    
    finally:
        await runner.cleanup()
```

## Conclusion

Asynchronous processing is fundamental to ScraperV4's performance and scalability. By leveraging `asyncio`, the framework can handle multiple concurrent operations efficiently while maintaining responsiveness.

Key benefits of the async approach:
- **High Concurrency**: Process hundreds of URLs simultaneously
- **Resource Efficiency**: Maximum utilization of CPU and network
- **Real-time Updates**: Non-blocking progress reporting
- **Scalable Architecture**: Performance scales with available resources
- **Responsive UI**: User interface remains interactive during operations

The async architecture requires careful design to handle errors, manage resources, and coordinate between sync and async components. ScraperV4's implementation provides a robust foundation that balances performance with reliability, making it suitable for both small-scale scraping and large enterprise operations.

Understanding these async patterns is essential for developers working with ScraperV4, whether they're debugging performance issues, extending functionality, or optimizing for specific use cases.