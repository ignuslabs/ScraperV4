# Troubleshooting Guide

This comprehensive troubleshooting guide provides step-by-step solutions for common ScraperV4 issues, debugging techniques, and advanced problem-solving strategies. Use this guide to quickly diagnose and resolve problems in your scraping operations.

## Learning Objectives

By completing this guide, you will:
- Quickly diagnose common scraping issues
- Implement systematic debugging approaches
- Resolve template and selector problems
- Fix proxy and network-related issues
- Handle anti-bot detection and blocking
- Optimize performance and resource usage
- Recover from system failures

## Prerequisites

- Completed previous ScraperV4 tutorials
- Basic understanding of web technologies
- Access to browser developer tools
- ScraperV4 installation with logging enabled

## Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

### System Health Check
```bash
# 1. Verify ScraperV4 is running
curl http://localhost:8080/api/monitoring/status

# 2. Check system resources
curl http://localhost:8080/api/monitoring/metrics

# 3. View recent logs
tail -f logs/scraperv4.log

# 4. Test network connectivity
curl -I https://httpbin.org/get
```

### Common Symptoms and Quick Fixes

| Symptom | Quick Fix | Section |
|---------|-----------|---------|
| No data extracted | Check selectors | [Template Issues](#part-1-template-and-selector-issues) |
| Job stuck in queue | Check concurrent jobs | [Job Management](#part-2-job-and-execution-issues) |
| Frequent timeouts | Check network/proxies | [Network Issues](#part-3-network-and-proxy-issues) |
| Getting blocked | Enable stealth mode | [Anti-Bot Issues](#part-4-anti-bot-and-blocking-issues) |
| High memory usage | Optimize batch size | [Performance Issues](#part-5-performance-and-resource-issues) |
| Playwright won't launch | Check API methods | [Playwright Issues](#part-9-playwright-interactive-mode-issues) |

## Part 1: Template and Selector Issues

### Issue 1.1: Selectors Return No Data

**Symptoms**: Template test returns empty results or null values

**Diagnosis Steps**:
1. **Verify Target Website**: Ensure the URL is accessible
```bash
curl -I "https://your-target-website.com"
```

2. **Inspect HTML Structure**:
```python
# Quick HTML inspection
from src.scrapers.stealth_fetcher import StealthFetcher

fetcher = StealthFetcher()
response = fetcher.fetch_page("https://your-target-website.com")
print(response.text[:1000])  # First 1000 characters
```

3. **Test Selectors in Browser**:
```javascript
// In browser console
document.querySelector('h1.product-title')
document.querySelectorAll('.price-current')
```

**Common Solutions**:

**Solution A**: Website Structure Changed
```json
{
  "selectors": {
    "title": "h1.product-title::text, h1.title::text, .product-name::text",
    "price": ".price-current::text, .price::text, [data-price]::attr(data-price)"
  }
}
```

**Solution B**: Dynamic Content Loading
```json
{
  "wait_conditions": {
    "wait_for_selector": ".dynamic-content",
    "max_wait_time": 10,
    "check_interval": 1
  }
}
```

**Solution C**: JavaScript-Rendered Content
```json
{
  "execution_options": {
    "enable_javascript": true,
    "wait_for_load": 3,
    "scroll_to_load": true
  }
}
```

### Issue 1.2: Extracting Wrong Data

**Symptoms**: Selectors extract unintended content or partial data

**Diagnosis**:
```python
# Debug selector precision
def debug_selector(url, selector):
    from bs4 import BeautifulSoup
    import requests
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    elements = soup.select(selector)
    print(f"Selector '{selector}' found {len(elements)} elements:")
    
    for i, element in enumerate(elements[:5]):  # Show first 5
        print(f"{i+1}: {element.get_text()[:100]}...")
        print(f"   HTML: {str(element)[:200]}...")

# Usage
debug_selector("https://example.com", ".price")
```

**Solutions**:

**Solution A**: More Specific Selectors
```json
{
  "selectors": {
    "price": ".product-details .price-current .amount::text",
    "old_price": ".product-details .price-original .amount::text"
  }
}
```

**Solution B**: Exclude Unwanted Elements
```json
{
  "selectors": {
    "description": ".product-description p:not(.disclaimer)::text"
  }
}
```

**Solution C**: Use XPath for Complex Selection
```json
{
  "selectors": {
    "specifications": "//table[@class='specs']//tr[position()>1]/td[2]/text()"
  }
}
```

### Issue 1.3: Inconsistent Data Extraction

**Symptoms**: Some pages work, others don't with the same template

**Diagnosis Script**:
```python
def diagnose_template_consistency(template_id, test_urls):
    """Test template against multiple URLs to find inconsistencies"""
    
    client = ScraperV4Client()
    results = {}
    
    for url in test_urls:
        try:
            result = client._request('POST', f'/templates/{template_id}/test', 
                                   json={'test_url': url})
            results[url] = {
                'success': True,
                'data': result.json()['data'],
                'extracted_fields': len([v for v in result.json()['data'].values() if v])
            }
        except Exception as e:
            results[url] = {
                'success': False,
                'error': str(e)
            }
    
    # Analyze results
    successful = [url for url, r in results.items() if r['success']]
    failed = [url for url, r in results.items() if not r['success']]
    
    print(f"Success rate: {len(successful)}/{len(test_urls)} ({len(successful)/len(test_urls)*100:.1f}%)")
    
    if failed:
        print(f"Failed URLs: {failed}")
    
    return results

# Usage
test_urls = [
    "https://example.com/product/1",
    "https://example.com/product/2", 
    "https://example.com/product/3"
]
diagnose_template_consistency("your-template-id", test_urls)
```

**Solutions**:

**Solution A**: Adaptive Selectors
```json
{
  "selectors": {
    "title": [
      "h1.product-title::text",
      "h1.item-title::text", 
      ".product-name::text",
      "h1::text"
    ]
  },
  "fallback_strategy": "first_match"
}
```

**Solution B**: Conditional Logic
```json
{
  "conditional_selectors": {
    "price": {
      "conditions": [
        {
          "if_exists": ".sale-price",
          "then": ".sale-price::text"
        },
        {
          "else": ".regular-price::text"
        }
      ]
    }
  }
}
```

## Part 2: Job and Execution Issues

### Issue 2.1: Jobs Stuck in Queue

**Symptoms**: Jobs remain in "queued" status indefinitely

**Diagnosis**:
```python
def diagnose_job_queue():
    """Check job queue status and system capacity"""
    
    client = ScraperV4Client()
    
    # Get system status
    status = client._request('GET', '/monitoring/status').json()
    print(f"Active jobs: {status['active_jobs']}")
    print(f"Queue size: {status['queue_size']}")
    print(f"Max concurrent: {status['max_concurrent_jobs']}")
    
    # Get job queue details
    queue = client._request('GET', '/scraping/queue').json()
    print(f"Queued jobs: {len(queue['jobs'])}")
    
    for job in queue['jobs'][:5]:  # Show first 5
        print(f"- {job['name']} (Priority: {job['priority']}, Queued: {job['queued_at']})")

diagnose_job_queue()
```

**Solutions**:

**Solution A**: Increase Concurrent Job Limit
```python
# Update system configuration
config_update = {
    "max_concurrent_jobs": 10,  # Increase from default
    "worker_threads": 8
}

client._request('PUT', '/system/config', json=config_update)
```

**Solution B**: Clear Stuck Jobs
```python
def clear_stuck_jobs():
    """Clear jobs stuck in invalid states"""
    
    client = ScraperV4Client()
    
    # Get all jobs
    jobs = client._request('GET', '/scraping/jobs').json()['jobs']
    
    # Find stuck jobs (running for more than 1 hour)
    from datetime import datetime, timedelta
    threshold = datetime.now() - timedelta(hours=1)
    
    stuck_jobs = []
    for job in jobs:
        if job['status'] == 'running':
            start_time = datetime.fromisoformat(job['started_at'])
            if start_time < threshold:
                stuck_jobs.append(job)
    
    print(f"Found {len(stuck_jobs)} stuck jobs")
    
    # Cancel stuck jobs
    for job in stuck_jobs:
        try:
            client._request('DELETE', f'/scraping/cancel/{job["job_id"]}')
            print(f"Cancelled stuck job: {job['name']}")
        except Exception as e:
            print(f"Failed to cancel job {job['job_id']}: {e}")

clear_stuck_jobs()
```

### Issue 2.2: Jobs Failing Immediately

**Symptoms**: Jobs fail within seconds of starting

**Diagnosis**:
```python
def diagnose_job_failures(job_id):
    """Analyze why a job failed quickly"""
    
    client = ScraperV4Client()
    
    # Get job details
    job = client._request('GET', f'/scraping/jobs/{job_id}').json()
    print(f"Job: {job['name']}")
    print(f"Status: {job['status']}")
    print(f"Error: {job.get('error_message', 'No error message')}")
    
    # Get execution logs
    logs = client._request('GET', f'/scraping/logs/{job_id}').json()
    print("\nRecent logs:")
    for log in logs['logs'][-10:]:  # Last 10 log entries
        print(f"[{log['timestamp']}] {log['level']}: {log['message']}")
    
    # Test template if available
    if job.get('template_id'):
        try:
            test_result = client._request('POST', f'/templates/{job["template_id"]}/test',
                                        json={'test_url': job['target_url']})
            print(f"\nTemplate test successful: {test_result.json()['success']}")
        except Exception as e:
            print(f"\nTemplate test failed: {e}")

# Usage
diagnose_job_failures("your-failed-job-id")
```

**Common Failure Causes and Solutions**:

**Solution A**: Invalid Template
```python
# Validate template before creating job
def validate_job_template(template_id, target_url):
    client = ScraperV4Client()
    
    try:
        # Test template
        result = client._request('POST', f'/templates/{template_id}/test',
                               json={'test_url': target_url})
        
        if not result.json()['success']:
            print("Template validation failed")
            return False
            
        print("Template validation passed")
        return True
        
    except Exception as e:
        print(f"Template validation error: {e}")
        return False
```

**Solution B**: Network/URL Issues
```python
# Validate target URL
def validate_target_url(url):
    import requests
    
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            print(f"URL accessible: {url}")
            return True
        else:
            print(f"URL returned status {response.status_code}: {url}")
            return False
    except Exception as e:
        print(f"URL not accessible: {url} - {e}")
        return False
```

### Issue 2.3: Jobs Running Too Long

**Symptoms**: Jobs that should complete quickly run for hours

**Diagnosis**:
```python
def diagnose_slow_jobs(job_id):
    """Analyze why a job is running slowly"""
    
    client = ScraperV4Client()
    
    # Get real-time job status
    status = client._request('GET', f'/scraping/status/{job_id}').json()
    
    print(f"Job Progress: {status['progress']:.1f}%")
    print(f"Items scraped: {status['items_scraped']}")
    print(f"Pages processed: {status['pages_processed']}")
    print(f"Current page: {status.get('current_page', 'Unknown')}")
    print(f"Avg time per page: {status.get('avg_page_time', 0):.2f}s")
    
    # Get performance metrics
    metrics = client._request('GET', f'/scraping/metrics/{job_id}').json()
    print(f"\nPerformance Metrics:")
    print(f"- Success rate: {metrics['success_rate']:.2%}")
    print(f"- Error rate: {metrics['error_rate']:.2%}")
    print(f"- Retry rate: {metrics['retry_rate']:.2%}")
    print(f"- Avg response time: {metrics['avg_response_time']:.2f}s")

diagnose_slow_jobs("your-slow-job-id")
```

**Solutions**:

**Solution A**: Optimize Delays
```python
# Reduce delays for faster execution
optimized_config = {
    "options": {
        "delay_range": [0.5, 1.5],  # Reduced from [2, 5]
        "page_load_wait": 1,        # Reduced from 3
        "retry_attempts": 2         # Reduced from 3
    }
}
```

**Solution B**: Limit Pages
```python
# Add pagination limits
limited_config = {
    "pagination": {
        "max_pages": 10,           # Limit page count
        "timeout_per_page": 30,    # Page timeout
        "early_termination": {
            "no_new_items": 3       # Stop if no new items
        }
    }
}
```

## Part 3: Network and Proxy Issues

### Issue 3.1: Frequent Connection Timeouts

**Symptoms**: Jobs fail with timeout errors

**Diagnosis**:
```python
def diagnose_network_issues():
    """Test network connectivity and performance"""
    
    import requests
    import time
    
    test_urls = [
        "https://httpbin.org/get",
        "https://google.com",
        "https://your-target-site.com"
    ]
    
    for url in test_urls:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            duration = time.time() - start_time
            
            print(f"{url}: {response.status_code} ({duration:.2f}s)")
            
        except requests.Timeout:
            print(f"{url}: TIMEOUT")
        except Exception as e:
            print(f"{url}: ERROR - {e}")

diagnose_network_issues()
```

**Solutions**:

**Solution A**: Increase Timeouts
```json
{
  "network_settings": {
    "connection_timeout": 30,
    "read_timeout": 60,
    "total_timeout": 90
  }
}
```

**Solution B**: Implement Connection Pooling
```python
# Configure connection pooling
network_config = {
    "connection_pool": {
        "pool_connections": 10,
        "pool_maxsize": 20,
        "max_retries": 3
    }
}
```

### Issue 3.2: Proxy Rotation Problems

**Symptoms**: Proxy rotation not working or proxies getting blocked

**Diagnosis**:
```python
def diagnose_proxy_issues():
    """Check proxy health and rotation"""
    
    from src.scrapers.proxy_rotator import ProxyRotator
    
    # Test proxy list
    proxy_list = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080"
    ]
    
    rotator = ProxyRotator(proxy_list)
    
    # Get proxy statistics
    stats = rotator.get_proxy_statistics()
    print("Proxy Statistics:")
    print(f"- Total proxies: {stats['total_proxies']}")
    print(f"- Active proxies: {stats['active_proxies']}")
    print(f"- Blacklisted proxies: {stats['blacklisted_proxies']}")
    print(f"- Success rate: {stats['overall_success_rate']:.2%}")
    
    # Test each proxy individually
    for proxy in proxy_list:
        try:
            test_result = rotator.test_proxy(proxy)
            print(f"{proxy}: {'WORKING' if test_result else 'FAILED'}")
        except Exception as e:
            print(f"{proxy}: ERROR - {e}")

diagnose_proxy_issues()
```

**Solutions**:

**Solution A**: Improve Proxy Quality
```python
# Configure better proxy selection
proxy_config = {
    "rotation_strategy": "performance",
    "validation": {
        "test_url": "https://httpbin.org/ip",
        "timeout": 15,
        "success_threshold": 0.8
    },
    "health_check": {
        "interval": 300,  # 5 minutes
        "failure_threshold": 3
    }
}
```

**Solution B**: Proxy Failover
```python
# Implement smart failover
failover_config = {
    "failover": {
        "enabled": True,
        "max_failures": 3,
        "cooldown_period": 1800,  # 30 minutes
        "backup_proxies": [
            "http://backup1.proxy.com:8080",
            "http://backup2.proxy.com:8080"
        ]
    }
}
```

### Issue 3.3: SSL Certificate Errors

**Symptoms**: Jobs fail with SSL verification errors

**Diagnosis and Solution**:
```python
def handle_ssl_issues():
    """Configure SSL handling for problematic sites"""
    
    ssl_config = {
        "ssl_verify": False,  # Disable SSL verification
        "ssl_context": {
            "check_hostname": False,
            "verify_mode": "none"
        },
        "certificates": {
            "ca_bundle": "/path/to/ca-bundle.crt"  # Custom CA bundle
        }
    }
    
    return ssl_config

# Apply to job configuration
job_config = {
    "name": "SSL-Problematic Site",
    "template_id": "your-template",
    "target_url": "https://problematic-ssl-site.com",
    "options": {
        **handle_ssl_issues(),
        "stealth_mode": "medium"
    }
}
```

## Part 4: Anti-Bot and Blocking Issues

### Issue 4.1: Getting Blocked or Detected

**Symptoms**: Requests return 403, Cloudflare challenges, or CAPTCHAs

**Diagnosis**:
```python
def diagnose_bot_detection(url):
    """Check what protection systems are active"""
    
    from src.scrapers.stealth_fetcher import StealthFetcher
    
    fetcher = StealthFetcher()
    response = fetcher.fetch_page(url)
    
    # Analyze response for protection systems
    detection = fetcher.detect_anti_bot_measures(response)
    
    print(f"Bot detection analysis for {url}:")
    print(f"Protection detected: {detection['detected']}")
    
    if detection['detected']:
        print(f"Systems found: {detection['measures']}")
        print(f"Confidence: {detection['confidence']:.2%}")
        print(f"Recommendations: {detection['recommendations']}")

diagnose_bot_detection("https://protected-site.com")
```

**Solutions**:

**Solution A**: Enhanced Stealth Configuration
```json
{
  "stealth_settings": {
    "profile": "high",
    "browser_fingerprint": {
      "randomize_user_agent": true,
      "randomize_headers": true,
      "randomize_screen_resolution": true,
      "randomize_timezone": true,
      "randomize_language": true
    },
    "behavioral_simulation": {
      "mouse_movements": true,
      "typing_patterns": true,
      "scroll_behavior": true,
      "page_interaction_time": [10, 30]
    }
  }
}
```

**Solution B**: Advanced Anti-Detection
```python
def configure_advanced_stealth():
    """Configure advanced anti-detection measures"""
    
    stealth_config = {
        "fingerprint_evasion": {
            "canvas_fingerprint": "randomize",
            "webgl_fingerprint": "randomize", 
            "audio_fingerprint": "randomize",
            "font_fingerprint": "randomize"
        },
        "request_patterns": {
            "randomize_timing": True,
            "human_like_delays": True,
            "vary_request_order": True,
            "simulate_cache_behavior": True
        },
        "browser_automation_hiding": {
            "hide_webdriver": True,
            "hide_chrome_automation": True,
            "spoof_permissions": True,
            "disable_automation_flags": True
        }
    }
    
    return stealth_config
```

### Issue 4.2: Cloudflare Challenge Handling

**Symptoms**: Stuck on Cloudflare "Checking your browser" page

**Solution**:
```python
def configure_cloudflare_bypass():
    """Configure Cloudflare challenge handling"""
    
    cloudflare_config = {
        "cloudflare_bypass": {
            "enabled": True,
            "wait_for_challenge": 30,  # Wait up to 30 seconds
            "solve_challenges": True,
            "bypass_strategies": [
                "wait_and_retry",
                "javascript_execution",
                "header_manipulation"
            ]
        },
        "detection_selectors": {
            "challenge_running": "#cf-challenge-running",
            "challenge_error": ".cf-error-details",
            "success_indicator": "body:not(.cf-browser-verification)"
        }
    }
    
    return cloudflare_config

# Apply to template
template_config = {
    "name": "Cloudflare-Protected Site",
    "anti_bot_handling": configure_cloudflare_bypass(),
    "selectors": {
        # Your normal selectors
    }
}
```

### Issue 4.3: Rate Limiting

**Symptoms**: 429 "Too Many Requests" errors

**Solutions**:

**Solution A**: Intelligent Rate Limiting
```python
def configure_rate_limiting():
    """Configure intelligent rate limiting"""
    
    rate_limit_config = {
        "rate_limiting": {
            "requests_per_minute": 30,
            "burst_allowance": 5,
            "backoff_strategy": "exponential",
            "respect_retry_after": True
        },
        "detection": {
            "http_codes": [429, 503],
            "response_indicators": [
                "rate limit",
                "too many requests",
                "temporarily blocked"
            ]
        },
        "response_strategy": {
            "initial_delay": 60,
            "max_delay": 3600,
            "jitter": True,
            "proxy_rotation_on_limit": True
        }
    }
    
    return rate_limit_config
```

**Solution B**: Adaptive Delays
```python
def implement_adaptive_delays():
    """Implement adaptive delay system"""
    
    adaptive_config = {
        "adaptive_delays": {
            "enabled": True,
            "base_delay": 2,
            "success_factor": 0.9,     # Reduce delay on success
            "failure_factor": 1.5,     # Increase delay on failure
            "min_delay": 0.5,
            "max_delay": 30
        },
        "monitoring": {
            "track_response_times": True,
            "adjust_for_server_load": True,
            "consider_time_of_day": True
        }
    }
    
    return adaptive_config
```

## Part 5: Performance and Resource Issues

### Issue 5.1: High Memory Usage

**Symptoms**: System running out of memory, jobs crashing

**Diagnosis**:
```python
def diagnose_memory_usage():
    """Monitor memory usage patterns"""
    
    import psutil
    import gc
    
    # Get current memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"Memory Usage:")
    print(f"- RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
    print(f"- VMS: {memory_info.vms / 1024 / 1024:.1f} MB")
    print(f"- Memory percent: {process.memory_percent():.1f}%")
    
    # Check for memory leaks
    gc.collect()
    print(f"- Objects in memory: {len(gc.get_objects())}")
    
    # System memory
    system_memory = psutil.virtual_memory()
    print(f"System Memory:")
    print(f"- Available: {system_memory.available / 1024 / 1024:.1f} MB")
    print(f"- Used: {system_memory.percent:.1f}%")

diagnose_memory_usage()
```

**Solutions**:

**Solution A**: Optimize Batch Processing
```python
def configure_memory_optimization():
    """Configure memory-efficient processing"""
    
    memory_config = {
        "processing": {
            "batch_size": 100,          # Smaller batches
            "streaming_mode": True,      # Process items as they come
            "clear_cache_interval": 50,  # Clear cache every 50 items
            "gc_frequency": 100         # Garbage collect every 100 items
        },
        "storage": {
            "write_frequency": 25,      # Write to disk more frequently
            "compress_data": True,      # Compress stored data
            "use_temp_files": True      # Use temp files for large datasets
        }
    }
    
    return memory_config
```

**Solution B**: Limit Concurrent Operations
```python
# Reduce concurrent operations
performance_config = {
    "concurrency": {
        "max_concurrent_jobs": 3,    # Reduced from 10
        "max_concurrent_requests": 5, # Limit simultaneous requests
        "thread_pool_size": 4        # Smaller thread pool
    }
}
```

### Issue 5.2: Slow Performance

**Symptoms**: Jobs taking much longer than expected

**Diagnosis**:
```python
def profile_performance():
    """Profile scraping performance"""
    
    import time
    from src.utils.performance_monitor import PerformanceMonitor
    
    monitor = PerformanceMonitor()
    
    # Start profiling
    monitor.start_profiling()
    
    # Run test job
    client = ScraperV4Client()
    job_config = {
        "name": "Performance Test",
        "template_id": "test-template",
        "target_url": "https://example.com",
        "options": {"max_pages": 5}
    }
    
    start_time = time.time()
    job_id = start_scraping_job(client, job_config)
    monitor_job_progress(client, job_id)
    duration = time.time() - start_time
    
    # Get performance report
    report = monitor.get_performance_report()
    
    print(f"Performance Report:")
    print(f"- Total duration: {duration:.2f}s")
    print(f"- CPU usage: {report['avg_cpu_usage']:.1f}%")
    print(f"- Memory usage: {report['avg_memory_usage']:.1f}%")
    print(f"- Network I/O: {report['network_io']} MB")
    print(f"- Bottlenecks: {report['bottlenecks']}")

profile_performance()
```

**Solutions**:

**Solution A**: Optimize Network Settings
```python
def optimize_network_performance():
    """Optimize network performance"""
    
    network_config = {
        "connection_settings": {
            "keep_alive": True,
            "connection_pool_size": 10,
            "max_redirects": 3,
            "compress_requests": True
        },
        "caching": {
            "dns_cache": True,
            "connection_cache": True,
            "response_cache": False  # Disable for fresh data
        },
        "optimization": {
            "tcp_nodelay": True,
            "socket_keepalive": True,
            "buffer_size": 8192
        }
    }
    
    return network_config
```

**Solution B**: Parallel Processing
```python
def enable_parallel_processing():
    """Enable parallel processing for better performance"""
    
    parallel_config = {
        "parallel_processing": {
            "enabled": True,
            "worker_threads": 4,
            "page_processing": "parallel",
            "data_extraction": "parallel"
        },
        "load_balancing": {
            "distribute_pages": True,
            "balance_by_complexity": True
        }
    }
    
    return parallel_config
```

## Part 6: Data Quality Issues

### Issue 6.1: Inconsistent Data Formats

**Symptoms**: Exported data has inconsistent formats or missing fields

**Diagnosis and Solution**:
```python
def implement_data_validation():
    """Implement comprehensive data validation"""
    
    validation_config = {
        "data_validation": {
            "required_fields": ["title", "price"],
            "field_types": {
                "price": "number",
                "rating": "float",
                "date": "datetime",
                "url": "url"
            },
            "value_constraints": {
                "price": {"min": 0, "max": 10000},
                "rating": {"min": 0, "max": 5}
            }
        },
        "data_cleaning": {
            "remove_empty_fields": True,
            "normalize_whitespace": True,
            "convert_currency": True,
            "standardize_dates": True
        },
        "quality_checks": {
            "duplicate_detection": True,
            "completeness_threshold": 0.8,
            "consistency_checks": True
        }
    }
    
    return validation_config

def clean_scraped_data(data):
    """Clean and validate scraped data"""
    
    cleaned_data = []
    
    for item in data:
        # Remove empty fields
        cleaned_item = {k: v for k, v in item.items() if v and str(v).strip()}
        
        # Validate required fields
        if 'title' in cleaned_item and 'price' in cleaned_item:
            # Clean price field
            if 'price' in cleaned_item:
                price_str = str(cleaned_item['price'])
                price_cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
                try:
                    cleaned_item['price'] = float(price_cleaned)
                except ValueError:
                    continue  # Skip invalid items
            
            cleaned_data.append(cleaned_item)
    
    return cleaned_data
```

### Issue 6.2: Duplicate Data

**Symptoms**: Same items appearing multiple times in results

**Solution**:
```python
def implement_deduplication():
    """Implement intelligent deduplication"""
    
    dedup_config = {
        "deduplication": {
            "enabled": True,
            "strategy": "fuzzy_matching",
            "similarity_threshold": 0.85,
            "key_fields": ["title", "url"],
            "ignore_fields": ["scraped_at", "position"]
        },
        "fuzzy_matching": {
            "algorithm": "levenshtein",
            "title_weight": 0.7,
            "url_weight": 0.3
        }
    }
    
    return dedup_config

def deduplicate_data(data):
    """Remove duplicate items from scraped data"""
    
    from difflib import SequenceMatcher
    
    unique_items = []
    seen_titles = set()
    
    for item in data:
        title = item.get('title', '').lower().strip()
        
        # Check for exact duplicates
        if title in seen_titles:
            continue
        
        # Check for fuzzy duplicates
        is_duplicate = False
        for existing_title in seen_titles:
            similarity = SequenceMatcher(None, title, existing_title).ratio()
            if similarity > 0.85:  # 85% similarity threshold
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_items.append(item)
            seen_titles.add(title)
    
    print(f"Removed {len(data) - len(unique_items)} duplicates")
    return unique_items
```

## Part 7: System and Infrastructure Issues

### Issue 7.1: Application Won't Start

**Symptoms**: ScraperV4 fails to start or crashes immediately

**Diagnostic Steps**:

1. **Check Dependencies**:
```bash
# Verify Python version
python --version  # Should be 3.8+

# Check virtual environment
which python
which pip

# Verify dependencies
pip list | grep -E "(scrapling|eel|pandas|aiohttp)"
```

2. **Check Configuration**:
```python
def validate_configuration():
    """Validate ScraperV4 configuration"""
    
    import os
    import json
    
    # Check required directories
    required_dirs = ['data', 'templates', 'logs']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"Creating missing directory: {dir_name}")
            os.makedirs(dir_name)
    
    # Check configuration file
    config_file = 'config/config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("Configuration file is valid")
        except json.JSONDecodeError as e:
            print(f"Configuration file is invalid: {e}")
    else:
        print("Configuration file not found, using defaults")

validate_configuration()
```

3. **Check Port Availability**:
```bash
# Check if port 8080 is in use
netstat -an | grep 8080
lsof -i :8080  # On macOS/Linux

# Or use alternative port
export SCRAPERV4_PORT=8081
```

**Solutions**:

**Solution A**: Reinstall Dependencies
```bash
# Clean reinstall
pip uninstall -r requirements.txt
pip install -r requirements.txt

# Or use requirements lock file
pip install -r requirements.lock
```

**Solution B**: Reset Configuration
```python
def reset_configuration():
    """Reset to default configuration"""
    
    default_config = {
        "server": {
            "host": "localhost",
            "port": 8080,
            "debug": False
        },
        "scraping": {
            "max_concurrent_jobs": 5,
            "default_delay": 2,
            "timeout": 30
        },
        "storage": {
            "data_dir": "data",
            "export_dir": "data/exports"
        }
    }
    
    import json
    import os
    
    os.makedirs('config', exist_ok=True)
    with open('config/config.json', 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("Configuration reset to defaults")

reset_configuration()
```

### Issue 7.2: Database/Storage Issues

**Symptoms**: Data not saving, export failures

**Diagnosis and Solution**:
```python
def diagnose_storage_issues():
    """Diagnose and fix storage issues"""
    
    import os
    import json
    import shutil
    
    # Check storage directories
    storage_dirs = ['data', 'data/jobs', 'data/results', 'data/exports']
    
    for dir_path in storage_dirs:
        if not os.path.exists(dir_path):
            print(f"Creating missing directory: {dir_path}")
            os.makedirs(dir_path)
        else:
            # Check permissions
            if not os.access(dir_path, os.W_OK):
                print(f"No write permission for: {dir_path}")
            else:
                print(f"Directory OK: {dir_path}")
    
    # Check disk space
    disk_usage = shutil.disk_usage('.')
    free_gb = disk_usage.free / (1024**3)
    print(f"Free disk space: {free_gb:.1f} GB")
    
    if free_gb < 1:
        print("WARNING: Low disk space!")
    
    # Test file operations
    test_file = 'data/test_write.json'
    try:
        with open(test_file, 'w') as f:
            json.dump({"test": "data"}, f)
        os.remove(test_file)
        print("File operations: OK")
    except Exception as e:
        print(f"File operations failed: {e}")

diagnose_storage_issues()
```

## Part 8: Recovery and Maintenance

### Recovery Procedures

**Procedure A**: Job Recovery
```python
def recover_interrupted_jobs():
    """Recover jobs that were interrupted"""
    
    client = ScraperV4Client()
    
    # Find interrupted jobs
    jobs = client._request('GET', '/scraping/jobs').json()['jobs']
    interrupted_jobs = [job for job in jobs if job['status'] == 'running']
    
    print(f"Found {len(interrupted_jobs)} interrupted jobs")
    
    for job in interrupted_jobs:
        try:
            # Try to get current status
            status = client._request('GET', f'/scraping/status/{job["job_id"]}')
            
            # If no response, mark as failed
            if not status:
                client._request('PUT', f'/scraping/jobs/{job["job_id"]}', 
                              json={'status': 'failed', 'error': 'System restart'})
                print(f"Marked job as failed: {job['name']}")
        
        except Exception as e:
            print(f"Error recovering job {job['job_id']}: {e}")

recover_interrupted_jobs()
```

**Procedure B**: Data Backup
```python
def backup_data():
    """Create backup of important data"""
    
    import shutil
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_{timestamp}"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup critical directories
    backup_items = [
        ('data/jobs', f'{backup_dir}/jobs'),
        ('data/results', f'{backup_dir}/results'),
        ('templates', f'{backup_dir}/templates'),
        ('config', f'{backup_dir}/config')
    ]
    
    for src, dst in backup_items:
        if os.path.exists(src):
            shutil.copytree(src, dst)
            print(f"Backed up: {src} -> {dst}")
    
    print(f"Backup completed: {backup_dir}")

backup_data()
```

### Maintenance Tasks

**Task A**: Cleanup Old Data
```python
def cleanup_old_data(days_to_keep=30):
    """Clean up old job data and logs"""
    
    import os
    import time
    from pathlib import Path
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    
    # Clean old job results
    results_dir = Path('data/results')
    if results_dir.exists():
        for file_path in results_dir.iterdir():
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                print(f"Deleted old result: {file_path}")
    
    # Clean old logs
    logs_dir = Path('logs')
    if logs_dir.exists():
        for file_path in logs_dir.iterdir():
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                print(f"Deleted old log: {file_path}")
    
    print(f"Cleanup completed: removed files older than {days_to_keep} days")

cleanup_old_data()
```

**Task B**: Performance Optimization
```python
def optimize_system_performance():
    """Optimize system performance"""
    
    import gc
    import os
    
    # Force garbage collection
    gc.collect()
    
    # Clear caches
    client = ScraperV4Client()
    try:
        client._request('POST', '/system/clear-cache')
        print("Cleared system caches")
    except:
        print("Cache clearing not available")
    
    # Optimize database (if using SQLite)
    try:
        import sqlite3
        for db_file in ['data/jobs.db', 'data/results.db']:
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file)
                conn.execute('VACUUM')
                conn.close()
                print(f"Optimized database: {db_file}")
    except:
        pass
    
    print("Performance optimization completed")

optimize_system_performance()
```

## Prevention Best Practices

### Monitoring Setup
```python
def setup_monitoring():
    """Setup proactive monitoring"""
    
    monitoring_config = {
        "health_checks": {
            "enabled": True,
            "interval": 300,  # 5 minutes
            "endpoints": [
                "/api/monitoring/status",
                "/api/monitoring/metrics"
            ]
        },
        "alerts": {
            "memory_threshold": 0.85,
            "cpu_threshold": 0.90,
            "disk_threshold": 0.95,
            "error_rate_threshold": 0.10
        },
        "logging": {
            "level": "INFO",
            "rotation": {
                "max_size": "100MB",
                "backup_count": 5
            }
        }
    }
    
    return monitoring_config
```

### Regular Maintenance Schedule
```python
def create_maintenance_schedule():
    """Create automated maintenance schedule"""
    
    import schedule
    
    # Daily tasks
    schedule.every().day.at("02:00").do(cleanup_old_data, days_to_keep=30)
    schedule.every().day.at("03:00").do(optimize_system_performance)
    
    # Weekly tasks
    schedule.every().monday.at("01:00").do(backup_data)
    schedule.every().sunday.at("04:00").do(recover_interrupted_jobs)
    
    print("Maintenance schedule created")
    print("Daily: Cleanup (02:00), Optimization (03:00)")
    print("Weekly: Backup (Monday 01:00), Recovery (Sunday 04:00)")

create_maintenance_schedule()
```

## Emergency Procedures

### Complete System Reset
```python
def emergency_reset():
    """Emergency system reset procedure"""
    
    import os
    import shutil
    
    print("WARNING: This will reset all ScraperV4 data!")
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != 'RESET':
        print("Reset cancelled")
        return
    
    # Stop all jobs
    try:
        client = ScraperV4Client()
        client._request('POST', '/system/emergency-stop')
    except:
        pass
    
    # Backup current data
    backup_data()
    
    # Reset directories
    reset_dirs = ['data/jobs', 'data/results', 'logs']
    for dir_path in reset_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            os.makedirs(dir_path)
    
    # Reset configuration
    reset_configuration()
    
    print("Emergency reset completed")
    print("Please restart ScraperV4")

# Use with extreme caution!
# emergency_reset()
```

## Summary

This troubleshooting guide covers:

1. **Template Issues**: Selector problems, data extraction errors
2. **Job Management**: Queue issues, execution problems
3. **Network Problems**: Timeouts, proxy issues, SSL errors
4. **Anti-Bot Detection**: Blocking, Cloudflare, rate limiting
5. **Performance Issues**: Memory usage, slow execution
6. **Data Quality**: Validation, deduplication, formatting
7. **System Issues**: Startup problems, storage issues
8. **Recovery**: Job recovery, backups, maintenance
9. **Playwright Interactive Mode**: Frontend API integration, browser launch issues

### Quick Reference Commands

```bash
# System health check
curl http://localhost:8080/api/monitoring/status

# View logs
tail -f logs/scraperv4.log

# Test network connectivity
curl -I https://httpbin.org/get

# Check disk space
df -h

# Check memory usage
free -m  # Linux
vm_stat  # macOS
```

## Part 9: Playwright Interactive Mode Issues

### Issue 9.1: Playwright Interactive Mode Won't Launch

**Symptoms**: 
- Frontend shows "Error starting Playwright interactive mode: {}"
- Empty error objects in console logs
- Interactive mode button produces no visible response

**Quick Diagnosis**:
```javascript
// Check in browser console
console.log(typeof window.api.startPlaywrightInteractive);
// Should return "function", not "undefined"
```

**Most Common Cause**: Missing frontend API methods in `/web/static/js/api.js`.

**Quick Solution**: Add the missing Playwright methods to the `ScraperAPI` class:

```javascript
// Add these methods to the ScraperAPI class
async startPlaywrightInteractive(url, options = {}) {
    try {
        return await eel.start_playwright_interactive(url, options)();
    } catch (error) {
        console.error('Failed to start Playwright interactive mode:', error);
        throw error;
    }
}

// Add remaining methods: getBrowserScreenshot, startElementSelection, 
// stopElementSelection, selectElementAtCoordinates, etc.
```

**Detailed Solution**: See the [complete Playwright troubleshooting guide](../troubleshooting/playwright-interactive-issues.md) for:
- Full list of required API methods
- Step-by-step implementation
- Dependency installation 
- Advanced debugging techniques

### Issue 9.2: Browser Dependencies Missing

**Symptoms**: Backend errors about missing Playwright modules

**Quick Solution**:
```bash
source venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium
```

### Issue 9.3: Sessions Not Closing Properly

**Symptoms**: Multiple browser instances remain open

**Quick Solution**: Implement proper session cleanup in your application lifecycle.

**For comprehensive Playwright troubleshooting**, including detailed solutions, diagnostic scripts, and prevention strategies, see: [Playwright Interactive Mode Troubleshooting Guide](../troubleshooting/playwright-interactive-issues.md)

---

Keep this guide handy for quick problem resolution and system maintenance!