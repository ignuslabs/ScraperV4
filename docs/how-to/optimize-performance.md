# How to Optimize Performance

This guide covers memory optimization, speed improvements, and resource management techniques for ScraperV4 to handle high-volume scraping efficiently.

## Prerequisites

- ScraperV4 installed and configured
- Understanding of system resources (CPU, memory, disk)
- Basic knowledge of Python performance optimization
- Access to system monitoring tools

## Overview

ScraperV4 performance optimization focuses on:
- **Memory Management**: Efficient data handling and garbage collection
- **CPU Optimization**: Concurrent processing and intelligent scheduling
- **Network Efficiency**: Connection pooling and request optimization
- **Storage Optimization**: Fast I/O and data persistence strategies
- **Resource Monitoring**: Real-time performance tracking

## Memory Optimization

### 1. Configure Memory-Efficient Processing

```python
# Configure memory-efficient scraping
from src.core.config import config
from src.services.scraping_service import ScrapingService

# Memory optimization settings
memory_config = {
    'max_concurrent_jobs': 2,  # Limit concurrent jobs
    'result_batch_size': 100,  # Process results in batches
    'memory_limit_mb': 512,    # Memory limit per job
    'gc_frequency': 50,        # Garbage collection frequency
    'stream_processing': True   # Enable streaming for large datasets
}

# Apply configuration
service = ScrapingService()
service.configure_memory_optimization(memory_config)
```

### 2. Implement Result Streaming

```python
def stream_large_dataset(job_id, batch_size=100):
    """Stream large datasets to avoid memory overload."""
    from src.services.data_service import DataService
    import gc
    
    data_service = DataService()
    total_count = data_service.get_job_results_count(job_id)
    
    processed_count = 0
    
    for offset in range(0, total_count, batch_size):
        # Get batch of results
        batch_results = data_service.get_job_results(
            job_id,
            limit=batch_size,
            offset=offset
        )
        
        # Process batch
        for result in batch_results:
            # Process individual result
            yield result
            processed_count += 1
        
        # Force garbage collection after each batch
        gc.collect()
        
        # Progress indicator
        progress = (processed_count / total_count) * 100
        print(f"Streaming progress: {progress:.1f}% ({processed_count}/{total_count})")

# Example usage
for result in stream_large_dataset("job-12345", batch_size=50):
    # Process result without loading all data into memory
    process_single_result(result)
```

### 3. Memory-Efficient Data Processing

```python
class MemoryEfficientProcessor:
    """Process data with minimal memory footprint."""
    
    def __init__(self, max_memory_mb=256):
        self.max_memory_mb = max_memory_mb
        self.current_memory_usage = 0
        
    def process_with_memory_monitoring(self, data_iterator):
        """Process data while monitoring memory usage."""
        import psutil
        import gc
        
        results = []
        process = psutil.Process()
        
        for item in data_iterator:
            # Check memory usage
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.max_memory_mb:
                # Memory limit reached, yield current results and clean up
                yield results
                results = []
                gc.collect()
                
                # Wait for memory to be freed
                import time
                time.sleep(0.1)
            
            # Process item
            processed_item = self.process_item(item)
            results.append(processed_item)
        
        # Yield remaining results
        if results:
            yield results
    
    def process_item(self, item):
        """Process individual item efficiently."""
        # Implement memory-efficient processing
        return {
            'processed': True,
            'data': item.data if hasattr(item, 'data') else item,
            'size': len(str(item))
        }

# Example usage
processor = MemoryEfficientProcessor(max_memory_mb=128)

for batch in processor.process_with_memory_monitoring(stream_large_dataset("job-12345")):
    # Process batch efficiently
    print(f"Processed batch of {len(batch)} items")
```

## CPU and Concurrency Optimization

### 1. Optimize Concurrent Job Execution

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class OptimizedScrapingManager:
    """Manage scraping jobs with optimized concurrency."""
    
    def __init__(self, max_workers=4, cpu_threshold=80):
        self.max_workers = max_workers
        self.cpu_threshold = cpu_threshold
        self.active_jobs = {}
        
    def get_optimal_worker_count(self):
        """Determine optimal worker count based on system resources."""
        import psutil
        
        # Get system specs
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        
        # Adjust worker count based on system load
        if cpu_usage > self.cpu_threshold:
            workers = max(1, cpu_count // 2)
        elif memory_usage > 80:
            workers = max(1, cpu_count // 3)
        else:
            workers = min(self.max_workers, cpu_count)
        
        return workers
    
    async def execute_jobs_optimized(self, job_configs):
        """Execute multiple jobs with optimal resource usage."""
        optimal_workers = self.get_optimal_worker_count()
        
        print(f"Using {optimal_workers} workers for {len(job_configs)} jobs")
        
        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            # Submit all jobs
            future_to_job = {
                executor.submit(self.execute_single_job, config): config
                for config in job_configs
            }
            
            # Process completed jobs
            results = []
            for future in asyncio.as_completed(future_to_job):
                job_config = future_to_job[future]
                try:
                    result = await future
                    results.append({
                        'job_config': job_config,
                        'result': result,
                        'status': 'success'
                    })
                except Exception as e:
                    results.append({
                        'job_config': job_config,
                        'error': str(e),
                        'status': 'failed'
                    })
        
        return results
    
    def execute_single_job(self, job_config):
        """Execute single job efficiently."""
        from src.services.scraping_service import ScrapingService
        
        service = ScrapingService()
        
        # Create job with optimized settings
        job = service.create_job(
            name=job_config['name'],
            template_id=job_config['template_id'],
            target_url=job_config['url'],
            config={
                'delay_range': [0.5, 1.5],  # Faster delays for performance
                'concurrent_requests': 3,   # Moderate concurrency
                'timeout': 15,              # Shorter timeout
                'retry_attempts': 2         # Fewer retries for speed
            }
        )
        
        return service.start_scraping_job(job.id)

# Example usage
manager = OptimizedScrapingManager(max_workers=6)

job_configs = [
    {'name': 'Job 1', 'template_id': 'template-1', 'url': 'https://site1.com'},
    {'name': 'Job 2', 'template_id': 'template-2', 'url': 'https://site2.com'},
    {'name': 'Job 3', 'template_id': 'template-3', 'url': 'https://site3.com'}
]

# Execute jobs optimally
results = asyncio.run(manager.execute_jobs_optimized(job_configs))
```

### 2. Intelligent Request Scheduling

```python
class SmartRequestScheduler:
    """Schedule requests intelligently to optimize performance."""
    
    def __init__(self):
        self.domain_stats = {}
        self.global_rate_limit = 10  # requests per second
        self.last_request_time = {}
        
    def calculate_optimal_delay(self, domain):
        """Calculate optimal delay for domain based on performance stats."""
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {
                'success_rate': 1.0,
                'avg_response_time': 1.0,
                'consecutive_failures': 0
            }
        
        stats = self.domain_stats[domain]
        
        # Base delay calculation
        base_delay = 1.0 / self.global_rate_limit
        
        # Adjust based on success rate
        if stats['success_rate'] < 0.8:
            base_delay *= 2  # Slower for unreliable domains
        
        # Adjust based on response time
        if stats['avg_response_time'] > 5.0:
            base_delay *= 1.5  # Slower for slow domains
        
        # Adjust based on consecutive failures
        failure_multiplier = 1 + (stats['consecutive_failures'] * 0.5)
        base_delay *= failure_multiplier
        
        return min(base_delay, 10.0)  # Cap at 10 seconds
    
    def update_stats(self, domain, response_time, success):
        """Update domain statistics."""
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {
                'success_rate': 1.0,
                'avg_response_time': 1.0,
                'consecutive_failures': 0,
                'total_requests': 0,
                'successful_requests': 0
            }
        
        stats = self.domain_stats[domain]
        stats['total_requests'] += 1
        
        if success:
            stats['successful_requests'] += 1
            stats['consecutive_failures'] = 0
        else:
            stats['consecutive_failures'] += 1
        
        # Update success rate
        stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
        
        # Update average response time (moving average)
        alpha = 0.1  # Smoothing factor
        stats['avg_response_time'] = (
            alpha * response_time + 
            (1 - alpha) * stats['avg_response_time']
        )
    
    def schedule_request(self, domain):
        """Schedule request with optimal timing."""
        import time
        from urllib.parse import urlparse
        
        # Extract domain from URL
        if domain.startswith('http'):
            domain = urlparse(domain).netloc
        
        # Calculate delay
        optimal_delay = self.calculate_optimal_delay(domain)
        
        # Check if we need to wait
        last_request = self.last_request_time.get(domain, 0)
        time_since_last = time.time() - last_request
        
        if time_since_last < optimal_delay:
            sleep_time = optimal_delay - time_since_last
            time.sleep(sleep_time)
        
        # Update last request time
        self.last_request_time[domain] = time.time()
        
        return optimal_delay

# Example usage
scheduler = SmartRequestScheduler()

def optimized_scraping_with_scheduling(urls):
    """Scrape URLs with intelligent scheduling."""
    from src.scrapers.stealth_fetcher import StealthFetcher
    import time
    
    fetcher = StealthFetcher()
    results = []
    
    for url in urls:
        # Schedule request optimally
        delay_used = scheduler.schedule_request(url)
        
        # Execute request
        start_time = time.time()
        result = fetcher.scrape(url)
        response_time = time.time() - start_time
        
        # Update scheduler stats
        success = result.get('status') == 'success'
        scheduler.update_stats(url, response_time, success)
        
        results.append({
            'url': url,
            'result': result,
            'response_time': response_time,
            'delay_used': delay_used
        })
        
        print(f"✓ {url} - {response_time:.2f}s (delay: {delay_used:.2f}s)")
    
    return results

# Example usage
urls = ['https://site1.com', 'https://site2.com', 'https://site1.com/page2']
optimized_results = optimized_scraping_with_scheduling(urls)
```

## Network Optimization

### 1. Connection Pooling and Session Management

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedHTTPManager:
    """Manage HTTP connections with optimal performance."""
    
    def __init__(self):
        self.session_pool = {}
        self.connection_pool_size = 20
        self.max_retries = 3
        
    def get_optimized_session(self, domain):
        """Get or create optimized session for domain."""
        if domain not in self.session_pool:
            session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            # Configure adapter with connection pooling
            adapter = HTTPAdapter(
                pool_connections=self.connection_pool_size,
                pool_maxsize=self.connection_pool_size,
                max_retries=retry_strategy
            )
            
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Optimize headers
            session.headers.update({
                'User-Agent': 'ScraperV4/1.0 (Performance Optimized)',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Keep-Alive': 'timeout=30, max=100'
            })
            
            self.session_pool[domain] = session
        
        return self.session_pool[domain]
    
    def fetch_urls_optimized(self, urls, timeout=15):
        """Fetch multiple URLs with connection reuse."""
        from urllib.parse import urlparse
        import time
        
        results = []
        
        for url in urls:
            domain = urlparse(url).netloc
            session = self.get_optimized_session(domain)
            
            start_time = time.time()
            try:
                response = session.get(url, timeout=timeout)
                response_time = time.time() - start_time
                
                results.append({
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'content_size': len(response.content),
                    'success': True
                })
                
            except Exception as e:
                response_time = time.time() - start_time
                results.append({
                    'url': url,
                    'error': str(e),
                    'response_time': response_time,
                    'success': False
                })
        
        return results
    
    def cleanup_sessions(self):
        """Clean up session pool."""
        for session in self.session_pool.values():
            session.close()
        self.session_pool.clear()

# Example usage
http_manager = OptimizedHTTPManager()

urls = [
    'https://example.com/page1',
    'https://example.com/page2',
    'https://another-site.com/data'
]

optimized_fetches = http_manager.fetch_urls_optimized(urls)

# Clean up when done
http_manager.cleanup_sessions()
```

### 2. Async Network Operations

```python
import asyncio
import aiohttp
import time

class AsyncScrapingOptimizer:
    """Optimize scraping using async operations."""
    
    def __init__(self, max_concurrent=10, timeout=30):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def fetch_single_url(self, session, url):
        """Fetch single URL asynchronously."""
        async with self.semaphore:
            start_time = time.time()
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    content = await response.text()
                    response_time = time.time() - start_time
                    
                    return {
                        'url': url,
                        'status': response.status,
                        'content': content,
                        'response_time': response_time,
                        'success': True
                    }
            except Exception as e:
                response_time = time.time() - start_time
                return {
                    'url': url,
                    'error': str(e),
                    'response_time': response_time,
                    'success': False
                }
    
    async def fetch_urls_batch(self, urls):
        """Fetch multiple URLs concurrently."""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'ScraperV4/1.0 (Async Performance)',
                'Accept-Encoding': 'gzip, deflate'
            }
        ) as session:
            
            tasks = [self.fetch_single_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({
                        'error': str(result),
                        'success': False
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def run_optimized_scraping(self, urls):
        """Run optimized async scraping."""
        start_time = time.time()
        
        # Run async operations
        results = asyncio.run(self.fetch_urls_batch(urls))
        
        total_time = time.time() - start_time
        successful_requests = len([r for r in results if r.get('success')])
        
        return {
            'results': results,
            'total_time': total_time,
            'total_urls': len(urls),
            'successful_requests': successful_requests,
            'requests_per_second': len(urls) / total_time,
            'success_rate': successful_requests / len(urls)
        }

# Example usage
async_optimizer = AsyncScrapingOptimizer(max_concurrent=15)

large_url_list = [f'https://httpbin.org/delay/{i%3}' for i in range(50)]
async_results = async_optimizer.run_optimized_scraping(large_url_list)

print(f"Processed {async_results['total_urls']} URLs in {async_results['total_time']:.2f}s")
print(f"Rate: {async_results['requests_per_second']:.2f} requests/second")
print(f"Success rate: {async_results['success_rate']:.2%}")
```

## Storage and I/O Optimization

### 1. Efficient Result Storage

```python
import json
import gzip
from pathlib import Path
import threading

class OptimizedStorage:
    """Optimized storage for scraping results."""
    
    def __init__(self, storage_dir="data/optimized"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.write_buffer = {}
        self.buffer_lock = threading.Lock()
        self.buffer_size = 1000  # Buffer up to 1000 results
        
    def store_result_buffered(self, job_id, result_data):
        """Store result with buffering for performance."""
        with self.buffer_lock:
            if job_id not in self.write_buffer:
                self.write_buffer[job_id] = []
            
            self.write_buffer[job_id].append(result_data)
            
            # Flush buffer if it's full
            if len(self.write_buffer[job_id]) >= self.buffer_size:
                self._flush_buffer(job_id)
    
    def _flush_buffer(self, job_id):
        """Flush write buffer to disk."""
        if job_id not in self.write_buffer or not self.write_buffer[job_id]:
            return
        
        buffer_data = self.write_buffer[job_id]
        self.write_buffer[job_id] = []
        
        # Write to compressed file
        file_path = self.storage_dir / f"{job_id}_buffer.json.gz"
        
        try:
            # Append to existing file or create new
            mode = 'ab' if file_path.exists() else 'wb'
            
            with gzip.open(file_path, mode) as f:
                for item in buffer_data:
                    json_line = json.dumps(item) + '\n'
                    f.write(json_line.encode('utf-8'))
                    
            print(f"Flushed {len(buffer_data)} results for job {job_id}")
            
        except Exception as e:
            print(f"Error flushing buffer for job {job_id}: {e}")
            # Put data back in buffer
            self.write_buffer[job_id] = buffer_data + self.write_buffer[job_id]
    
    def flush_all_buffers(self):
        """Flush all pending buffers."""
        with self.buffer_lock:
            for job_id in list(self.write_buffer.keys()):
                self._flush_buffer(job_id)
    
    def read_results_streaming(self, job_id):
        """Read results as a generator for memory efficiency."""
        file_path = self.storage_dir / f"{job_id}_buffer.json.gz"
        
        if not file_path.exists():
            return
        
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
        except Exception as e:
            print(f"Error reading results for job {job_id}: {e}")

# Example usage
optimized_storage = OptimizedStorage()

# Store results efficiently
for i in range(5000):
    result = {
        'id': f'result_{i}',
        'data': {'title': f'Item {i}', 'value': i * 10},
        'timestamp': time.time()
    }
    optimized_storage.store_result_buffered('job-performance-test', result)

# Flush remaining buffers
optimized_storage.flush_all_buffers()

# Read results efficiently
count = 0
for result in optimized_storage.read_results_streaming('job-performance-test'):
    count += 1

print(f"Read {count} results efficiently")
```

### 2. Database Optimization for High Volume

```python
import sqlite3
import threading
from queue import Queue
import time

class HighPerformanceDB:
    """High-performance database for scraping results."""
    
    def __init__(self, db_path="data/performance.db"):
        self.db_path = db_path
        self.write_queue = Queue()
        self.writer_thread = None
        self.running = True
        self._init_db()
        self._start_writer_thread()
    
    def _init_db(self):
        """Initialize database with optimal settings."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        conn.execute("PRAGMA cache_size=10000")  # Larger cache
        conn.execute("PRAGMA temp_store=MEMORY")  # In-memory temp tables
        
        # Create optimized table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                url TEXT,
                data TEXT,
                created_at REAL,
                INDEX(job_id),
                INDEX(created_at)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _start_writer_thread(self):
        """Start background writer thread."""
        self.writer_thread = threading.Thread(target=self._writer_worker, daemon=True)
        self.writer_thread.start()
    
    def _writer_worker(self):
        """Background worker for writing to database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        batch = []
        batch_size = 100
        last_write = time.time()
        
        while self.running:
            try:
                # Get item from queue with timeout
                item = self.write_queue.get(timeout=1.0)
                batch.append(item)
                
                # Write batch if full or timeout reached
                if len(batch) >= batch_size or (time.time() - last_write) > 5.0:
                    self._write_batch(conn, batch)
                    batch = []
                    last_write = time.time()
                    
            except:
                # Timeout or shutdown
                if batch:
                    self._write_batch(conn, batch)
                    batch = []
                continue
        
        # Write remaining batch
        if batch:
            self._write_batch(conn, batch)
        
        conn.close()
    
    def _write_batch(self, conn, batch):
        """Write batch of results to database."""
        try:
            conn.executemany(
                "INSERT INTO results (job_id, url, data, created_at) VALUES (?, ?, ?, ?)",
                batch
            )
            conn.commit()
            print(f"Wrote batch of {len(batch)} results")
        except Exception as e:
            print(f"Error writing batch: {e}")
    
    def store_result_async(self, job_id, url, data):
        """Store result asynchronously."""
        import json
        self.write_queue.put((
            job_id,
            url,
            json.dumps(data),
            time.time()
        ))
    
    def get_results_streaming(self, job_id, batch_size=1000):
        """Get results as generator for memory efficiency."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        offset = 0
        while True:
            cursor = conn.execute(
                "SELECT * FROM results WHERE job_id = ? LIMIT ? OFFSET ?",
                (job_id, batch_size, offset)
            )
            
            results = cursor.fetchall()
            if not results:
                break
            
            for row in results:
                yield {
                    'id': row['id'],
                    'job_id': row['job_id'],
                    'url': row['url'],
                    'data': json.loads(row['data']),
                    'created_at': row['created_at']
                }
            
            offset += batch_size
        
        conn.close()
    
    def shutdown(self):
        """Shutdown database writer."""
        self.running = False
        if self.writer_thread:
            self.writer_thread.join()

# Example usage
high_perf_db = HighPerformanceDB()

# Store results asynchronously
for i in range(10000):
    data = {
        'title': f'High Performance Item {i}',
        'value': i,
        'metadata': {'index': i, 'batch': i // 100}
    }
    high_perf_db.store_result_async('perf-job-1', f'https://example.com/item/{i}', data)

# Read results efficiently
count = 0
for result in high_perf_db.get_results_streaming('perf-job-1'):
    count += 1

print(f"Processed {count} results from high-performance database")

# Clean shutdown
high_perf_db.shutdown()
```

## Performance Monitoring and Metrics

### 1. Real-time Performance Monitoring

```python
import psutil
import time
from threading import Thread
from collections import deque

class PerformanceMonitor:
    """Monitor system and application performance."""
    
    def __init__(self, history_size=100):
        self.history_size = history_size
        self.metrics_history = {
            'cpu_usage': deque(maxlen=history_size),
            'memory_usage': deque(maxlen=history_size),
            'disk_io': deque(maxlen=history_size),
            'network_io': deque(maxlen=history_size),
            'active_jobs': deque(maxlen=history_size),
            'requests_per_second': deque(maxlen=history_size)
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval=5):
        """Start performance monitoring."""
        self.monitoring = True
        self.monitor_thread = Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval):
        """Main monitoring loop."""
        last_disk_io = psutil.disk_io_counters()
        last_network_io = psutil.net_io_counters()
        last_time = time.time()
        
        while self.monitoring:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # CPU and Memory
                cpu_usage = psutil.cpu_percent(interval=None)
                memory_usage = psutil.virtual_memory().percent
                
                # Disk I/O
                current_disk_io = psutil.disk_io_counters()
                disk_read_rate = (current_disk_io.read_bytes - last_disk_io.read_bytes) / time_delta
                disk_write_rate = (current_disk_io.write_bytes - last_disk_io.write_bytes) / time_delta
                
                # Network I/O
                current_network_io = psutil.net_io_counters()
                network_sent_rate = (current_network_io.bytes_sent - last_network_io.bytes_sent) / time_delta
                network_recv_rate = (current_network_io.bytes_recv - last_network_io.bytes_recv) / time_delta
                
                # Store metrics
                self.metrics_history['cpu_usage'].append(cpu_usage)
                self.metrics_history['memory_usage'].append(memory_usage)
                self.metrics_history['disk_io'].append({
                    'read_rate': disk_read_rate,
                    'write_rate': disk_write_rate
                })
                self.metrics_history['network_io'].append({
                    'sent_rate': network_sent_rate,
                    'recv_rate': network_recv_rate
                })
                
                # Update for next iteration
                last_disk_io = current_disk_io
                last_network_io = current_network_io
                last_time = current_time
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def get_current_metrics(self):
        """Get current performance metrics."""
        if not self.metrics_history['cpu_usage']:
            return None
        
        return {
            'cpu_usage': self.metrics_history['cpu_usage'][-1],
            'memory_usage': self.metrics_history['memory_usage'][-1],
            'disk_io': self.metrics_history['disk_io'][-1] if self.metrics_history['disk_io'] else None,
            'network_io': self.metrics_history['network_io'][-1] if self.metrics_history['network_io'] else None,
            'timestamp': time.time()
        }
    
    def get_performance_report(self):
        """Generate performance report."""
        if not self.metrics_history['cpu_usage']:
            return {'error': 'No metrics available'}
        
        cpu_avg = sum(self.metrics_history['cpu_usage']) / len(self.metrics_history['cpu_usage'])
        memory_avg = sum(self.metrics_history['memory_usage']) / len(self.metrics_history['memory_usage'])
        
        return {
            'period_minutes': len(self.metrics_history['cpu_usage']) * 5 / 60,
            'cpu_usage': {
                'current': self.metrics_history['cpu_usage'][-1],
                'average': cpu_avg,
                'max': max(self.metrics_history['cpu_usage']),
                'min': min(self.metrics_history['cpu_usage'])
            },
            'memory_usage': {
                'current': self.metrics_history['memory_usage'][-1],
                'average': memory_avg,
                'max': max(self.metrics_history['memory_usage']),
                'min': min(self.metrics_history['memory_usage'])
            },
            'recommendations': self._generate_recommendations(cpu_avg, memory_avg)
        }
    
    def _generate_recommendations(self, cpu_avg, memory_avg):
        """Generate performance recommendations."""
        recommendations = []
        
        if cpu_avg > 80:
            recommendations.append("High CPU usage - consider reducing concurrent jobs")
        
        if memory_avg > 80:
            recommendations.append("High memory usage - enable memory optimization features")
        
        if cpu_avg < 30 and memory_avg < 50:
            recommendations.append("Resources underutilized - consider increasing concurrency")
        
        return recommendations

# Example usage
monitor = PerformanceMonitor()
monitor.start_monitoring(interval=2)

# Let it run for a while
time.sleep(30)

# Get current metrics
current = monitor.get_current_metrics()
print(f"Current CPU: {current['cpu_usage']:.1f}%")
print(f"Current Memory: {current['memory_usage']:.1f}%")

# Get performance report
report = monitor.get_performance_report()
print(f"Average CPU: {report['cpu_usage']['average']:.1f}%")
print(f"Recommendations: {report['recommendations']}")

monitor.stop_monitoring()
```

### 2. Scraping Performance Metrics

```python
class ScrapingPerformanceTracker:
    """Track scraping-specific performance metrics."""
    
    def __init__(self):
        self.job_metrics = {}
        self.global_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'total_response_time': 0,
            'total_data_scraped': 0
        }
    
    def start_job_tracking(self, job_id):
        """Start tracking performance for a job."""
        self.job_metrics[job_id] = {
            'start_time': time.time(),
            'requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0,
            'data_points_scraped': 0,
            'errors': [],
            'avg_delay_between_requests': 0
        }
    
    def record_request(self, job_id, success, response_time, data_points=0, error=None):
        """Record request metrics."""
        if job_id not in self.job_metrics:
            self.start_job_tracking(job_id)
        
        metrics = self.job_metrics[job_id]
        metrics['requests'] += 1
        metrics['total_response_time'] += response_time
        
        if success:
            metrics['successful_requests'] += 1
            metrics['data_points_scraped'] += data_points
            self.global_metrics['successful_requests'] += 1
        else:
            metrics['failed_requests'] += 1
            if error:
                metrics['errors'].append(error)
        
        self.global_metrics['total_requests'] += 1
        self.global_metrics['total_response_time'] += response_time
        self.global_metrics['total_data_scraped'] += data_points
    
    def get_job_performance(self, job_id):
        """Get performance metrics for a specific job."""
        if job_id not in self.job_metrics:
            return None
        
        metrics = self.job_metrics[job_id]
        elapsed_time = time.time() - metrics['start_time']
        
        return {
            'job_id': job_id,
            'elapsed_time': elapsed_time,
            'total_requests': metrics['requests'],
            'success_rate': metrics['successful_requests'] / metrics['requests'] if metrics['requests'] > 0 else 0,
            'requests_per_minute': (metrics['requests'] / elapsed_time) * 60 if elapsed_time > 0 else 0,
            'avg_response_time': metrics['total_response_time'] / metrics['requests'] if metrics['requests'] > 0 else 0,
            'data_points_per_minute': (metrics['data_points_scraped'] / elapsed_time) * 60 if elapsed_time > 0 else 0,
            'total_data_points': metrics['data_points_scraped'],
            'error_count': len(metrics['errors']),
            'recent_errors': metrics['errors'][-5:]  # Last 5 errors
        }
    
    def get_global_performance(self):
        """Get global performance metrics."""
        return {
            'total_requests': self.global_metrics['total_requests'],
            'global_success_rate': (
                self.global_metrics['successful_requests'] / self.global_metrics['total_requests']
                if self.global_metrics['total_requests'] > 0 else 0
            ),
            'avg_response_time': (
                self.global_metrics['total_response_time'] / self.global_metrics['total_requests']
                if self.global_metrics['total_requests'] > 0 else 0
            ),
            'total_data_scraped': self.global_metrics['total_data_scraped'],
            'active_jobs': len(self.job_metrics)
        }

# Example usage
perf_tracker = ScrapingPerformanceTracker()

# Simulate some scraping activity
perf_tracker.start_job_tracking('job-1')

for i in range(100):
    success = i % 10 != 0  # 90% success rate
    response_time = 0.5 + (i % 3) * 0.2  # Variable response times
    data_points = 5 if success else 0
    error = "Rate limited" if not success else None
    
    perf_tracker.record_request('job-1', success, response_time, data_points, error)

# Get performance report
job_perf = perf_tracker.get_job_performance('job-1')
global_perf = perf_tracker.get_global_performance()

print(f"Job Success Rate: {job_perf['success_rate']:.2%}")
print(f"Requests per minute: {job_perf['requests_per_minute']:.1f}")
print(f"Average response time: {job_perf['avg_response_time']:.2f}s")
print(f"Data points per minute: {job_perf['data_points_per_minute']:.1f}")
```

## Integration with ScraperV4

### 1. Configure Performance Settings via API

```bash
# Configure performance optimization via API
curl -X POST http://localhost:8080/api/config/performance \
  -H "Content-Type: application/json" \
  -d '{
    "memory_optimization": {
      "max_memory_mb": 512,
      "gc_frequency": 100,
      "streaming_enabled": true
    },
    "concurrency": {
      "max_concurrent_jobs": 4,
      "requests_per_second": 10,
      "connection_pool_size": 20
    },
    "storage": {
      "buffer_size": 1000,
      "compression_enabled": true,
      "async_writes": true
    }
  }'
```

### 2. Performance-Optimized Job Configuration

```python
# Create performance-optimized scraping job
optimized_job_config = {
    "name": "Performance Optimized Job",
    "template_id": "optimized-template",
    "target_url": "https://high-volume-site.com",
    "performance_config": {
        "memory_limit_mb": 256,
        "concurrent_requests": 5,
        "request_delay_range": [0.1, 0.5],
        "connection_reuse": True,
        "compression": True,
        "streaming_results": True,
        "batch_size": 100
    },
    "monitoring": {
        "track_performance": True,
        "alert_on_high_memory": True,
        "alert_on_low_success_rate": True
    }
}

# Start optimized job
from src.services.scraping_service import ScrapingService
service = ScrapingService()
job = service.create_job(**optimized_job_config)
job_id = service.start_scraping_job(job.id)
```

## Expected Outcomes

After implementing performance optimizations:

1. **Reduced Memory Usage**: 40-60% reduction in memory consumption
2. **Increased Throughput**: 2-5x improvement in requests per second
3. **Better Resource Utilization**: Optimal CPU and network usage
4. **Faster Data Processing**: Reduced time for large dataset processing
5. **Improved Stability**: Fewer memory-related crashes and timeouts
6. **Real-time Monitoring**: Visibility into performance bottlenecks

## Success Criteria

- [ ] Memory usage optimized and monitored
- [ ] Concurrent processing efficiency improved
- [ ] Network operations optimized with connection pooling
- [ ] Storage operations streamlined
- [ ] Real-time performance monitoring working
- [ ] Performance metrics tracking functional
- [ ] Integration with existing ScraperV4 components completed