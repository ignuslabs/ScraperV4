# How to Configure Proxy Rotation and Management

This guide covers setting up and managing proxy rotation in ScraperV4 for improved anonymity and bypassing IP-based restrictions.

## Prerequisites

- ScraperV4 installed and configured
- List of proxy servers (HTTP/HTTPS/SOCKS5)
- Basic understanding of HTTP proxies
- Optional: Proxy authentication credentials

## Overview

ScraperV4's ProxyRotator class provides intelligent proxy management with:
- Automatic rotation strategies
- Performance tracking and optimization
- Blacklisting and recovery mechanisms
- Statistical monitoring and health checks

## Setting Up Basic Proxy Rotation

### 1. Prepare Your Proxy List

First, collect your proxy servers in the proper format:

```python
# HTTP/HTTPS proxies
http_proxies = [
    "http://proxy1.example.com:8080",
    "https://proxy2.example.com:3128",
    "http://username:password@proxy3.example.com:8080"
]

# SOCKS5 proxies
socks_proxies = [
    "socks5://proxy4.example.com:1080",
    "socks5://username:password@proxy5.example.com:1080"
]

# Combined proxy list
proxy_list = http_proxies + socks_proxies
```

### 2. Initialize ProxyRotator

```python
from src.scrapers.proxy_rotator import ProxyRotator

# Create proxy rotator instance
rotator = ProxyRotator(proxy_list)

# Get basic statistics
print("Proxy rotator initialized")
print(f"Total proxies: {len(rotator.proxies)}")
```

### 3. Configure StealthFetcher with Proxies

```python
from src.scrapers.stealth_fetcher import StealthFetcher

# Initialize stealth fetcher
fetcher = StealthFetcher()

# Configure proxy rotation
result = fetcher.configure_proxy_rotation(proxy_list)
print(f"Proxy rotation configured: {result}")
```

## Advanced Proxy Management

### 1. Performance-Based Rotation Strategy

```python
# Get the best performing proxy based on success rate and response time
best_proxy = rotator.get_best_proxy()
print(f"Best proxy: {best_proxy}")

# Get next proxy in rotation
next_proxy = rotator.get_next_proxy()
print(f"Next proxy: {next_proxy}")
```

### 2. Manual Success/Failure Tracking

```python
import time

# Simulate successful request
start_time = time.time()
proxy = rotator.get_next_proxy()

# ... perform your request ...

# Mark success with response time
response_time = time.time() - start_time
rotator.mark_success(proxy, response_time)

# Mark failure (temporary blacklist)
rotator.mark_failed(proxy, permanent=False)

# Mark permanent failure
rotator.mark_failed(proxy, permanent=True)
```

### 3. Proxy Validation and Health Checks

```python
# Validate all proxies against a test URL
validation_results = rotator.validate_proxies(test_url="http://httpbin.org/ip")

for proxy, is_valid in validation_results.items():
    status = "✓ Valid" if is_valid else "✗ Invalid"
    print(f"{proxy}: {status}")
```

## Integration with Scraping Jobs

### 1. Using Proxies in API Requests

```bash
# Start scraping job with proxy configuration
curl -X POST http://localhost:8080/api/scraping/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Proxy-enabled Scraping Job",
    "url": "https://example.com",
    "template_id": "basic-template",
    "options": {
      "use_proxy": true,
      "proxy_strategy": "performance",
      "proxy_list": [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:3128"
      ],
      "proxy_rotation_interval": 30,
      "proxy_retry_attempts": 3
    }
  }'
```

### 2. Programmatic Job Configuration

```python
from src.services.scraping_service import ScrapingService

service = ScrapingService()

# Create job with proxy configuration
job = service.create_job(
    name="Proxy-enabled Job",
    template_id="product-template",
    target_url="https://example-store.com/products",
    config={
        "use_proxy": True,
        "proxy_list": proxy_list,
        "proxy_strategy": "round_robin",  # or "performance", "random"
        "stealth_mode": "high",
        "delay_range": [2, 5]
    }
)

# Start the job
job_id = service.start_scraping_job(job.id)
```

## Proxy Configuration Options

### 1. Rotation Strategies

```python
# Round-robin rotation (default)
rotator.rotation_strategy = "round_robin"

# Performance-based rotation
rotator.rotation_strategy = "performance"

# Random rotation
rotator.rotation_strategy = "random"
```

### 2. Blacklisting Configuration

```python
# Configure blacklisting behavior
rotator.blacklist_threshold = 3  # failures before temporary blacklist
rotator.blacklist_duration = 300  # seconds (5 minutes)
rotator.permanent_failure_threshold = 10  # failures before permanent blacklist
```

### 3. Validation Settings

```python
# Configure proxy validation
rotator.validation_interval = 300  # seconds between health checks
rotator.validation_timeout = 10  # seconds per validation request
rotator.validation_url = "http://httpbin.org/ip"  # test endpoint
```

## Monitoring and Statistics

### 1. Real-time Statistics

```python
# Get comprehensive statistics
stats = rotator.get_statistics()

print(f"Total proxies: {stats['total_proxies']}")
print(f"Working proxies: {stats['working_proxies']}")
print(f"Failed proxies: {stats['failed_proxies']}")
print(f"Last rotation: {stats['last_rotation']}")

# Detailed proxy information
for proxy_info in stats['proxy_details']:
    print(f"""
Proxy: {proxy_info['proxy']}
Status: {proxy_info['status']}
Success Rate: {proxy_info['success_rate']:.1f}%
Successes: {proxy_info['successes']}
Failures: {proxy_info['failures']}
Last Used: {proxy_info['last_used']}
""")
```

### 2. Performance Monitoring

```python
# Get top performing proxies
def get_top_proxies(rotator, limit=5):
    stats = rotator.get_statistics()
    proxy_details = stats['proxy_details']
    
    # Sort by success rate and average response time
    top_proxies = sorted(
        proxy_details,
        key=lambda x: (x['success_rate'], -x.get('avg_response_time', 999)),
        reverse=True
    )
    
    return top_proxies[:limit]

top_proxies = get_top_proxies(rotator)
for i, proxy in enumerate(top_proxies, 1):
    print(f"{i}. {proxy['proxy']} ({proxy['success_rate']:.1f}% success)")
```

## Environment Variable Configuration

### 1. Create .env File

```bash
# Proxy configuration
SCRAPERV4_USE_PROXIES=true
SCRAPERV4_PROXY_ROTATION_STRATEGY=performance
SCRAPERV4_PROXY_TIMEOUT=30
SCRAPERV4_PROXY_RETRIES=3

# Proxy list (comma-separated)
SCRAPERV4_PROXY_LIST="http://proxy1.example.com:8080,http://proxy2.example.com:3128"

# Authentication (if needed)
SCRAPERV4_PROXY_USERNAME=your_username
SCRAPERV4_PROXY_PASSWORD=your_password
```

### 2. Load Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Build proxy list from environment
proxy_string = os.getenv('SCRAPERV4_PROXY_LIST', '')
proxy_list = [p.strip() for p in proxy_string.split(',') if p.strip()]

# Create rotator with environment settings
rotator = ProxyRotator(proxy_list)
```

## Managing Proxy Pools

### 1. Dynamic Proxy Management

```python
# Add new proxy during runtime
rotator.add_proxy("http://new-proxy.example.com:8080")

# Remove problematic proxy
rotator.remove_proxy("http://bad-proxy.example.com:8080")

# Reset all statistics
rotator.reset_statistics()
```

### 2. Proxy Pool Optimization

```python
def optimize_proxy_pool(rotator, min_success_rate=70):
    """Remove poorly performing proxies."""
    stats = rotator.get_statistics()
    
    for proxy_info in stats['proxy_details']:
        if proxy_info['success_rate'] < min_success_rate:
            proxy = proxy_info['proxy']
            print(f"Removing poor proxy: {proxy} ({proxy_info['success_rate']:.1f}%)")
            rotator.remove_proxy(proxy)

# Run optimization
optimize_proxy_pool(rotator)
```

## Troubleshooting Common Issues

### 1. All Proxies Blacklisted

```python
# Check if all proxies are blacklisted
stats = rotator.get_statistics()
if stats['working_proxies'] == 0:
    print("All proxies blacklisted - resetting statistics")
    rotator.reset_statistics()
```

### 2. Proxy Authentication Issues

```python
# Test individual proxy authentication
import requests

def test_proxy_auth(proxy_url):
    try:
        response = requests.get(
            "http://httpbin.org/ip",
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Proxy auth failed: {e}")
        return False

# Test each proxy
for proxy in proxy_list:
    if test_proxy_auth(proxy):
        print(f"✓ {proxy} - Authentication successful")
    else:
        print(f"✗ {proxy} - Authentication failed")
```

### 3. Slow Proxy Detection

```python
# Monitor response times
def monitor_proxy_performance(rotator, duration_minutes=10):
    import time
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    while time.time() < end_time:
        proxy = rotator.get_next_proxy()
        
        # Test proxy speed
        start_request = time.time()
        try:
            # Perform test request
            response = requests.get(
                "http://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
            response_time = time.time() - start_request
            
            if response.status_code == 200:
                rotator.mark_success(proxy, response_time)
                print(f"✓ {proxy}: {response_time:.2f}s")
            else:
                rotator.mark_failed(proxy)
                print(f"✗ {proxy}: HTTP {response.status_code}")
                
        except Exception as e:
            rotator.mark_failed(proxy)
            print(f"✗ {proxy}: {e}")
        
        time.sleep(5)  # Wait between tests

# Run performance monitoring
monitor_proxy_performance(rotator, duration_minutes=5)
```

## Best Practices

### 1. Proxy Selection Criteria

- **Geographic Distribution**: Use proxies from different countries/regions
- **Provider Diversity**: Avoid single proxy provider dependency
- **Performance Testing**: Regularly validate proxy performance
- **Rotation Frequency**: Balance between anonymity and efficiency

### 2. Resource Management

```python
# Implement proxy pool health monitoring
def maintain_proxy_health(rotator):
    """Maintain healthy proxy pool."""
    stats = rotator.get_statistics()
    
    # Alert if too few working proxies
    if stats['working_proxies'] < 3:
        print("WARNING: Low proxy availability")
        
    # Reset statistics if success rate is too low
    overall_success = sum(p['successes'] for p in stats['proxy_details'])
    overall_total = sum(p['successes'] + p['failures'] for p in stats['proxy_details'])
    
    if overall_total > 0 and (overall_success / overall_total) < 0.5:
        print("Resetting proxy statistics due to low success rate")
        rotator.reset_statistics()

# Run maintenance
maintain_proxy_health(rotator)
```

### 3. Security Considerations

- **Encrypted Connections**: Prefer HTTPS proxies when possible
- **Authentication**: Use authenticated proxies for better reliability
- **IP Rotation**: Implement proper IP rotation to avoid detection
- **Data Protection**: Ensure proxy providers don't log sensitive data

## Expected Outcomes

After implementing proxy rotation:

1. **Improved Success Rates**: Bypass IP-based rate limiting and blocking
2. **Geographic Flexibility**: Access geo-restricted content
3. **Enhanced Anonymity**: Distribute requests across multiple IP addresses
4. **Fault Tolerance**: Automatic failover when proxies become unavailable
5. **Performance Optimization**: Use fastest available proxies for better response times

## Success Criteria

- [ ] Proxy rotator successfully initialized with multiple proxies
- [ ] Automatic failover working when proxies fail
- [ ] Performance monitoring showing response times and success rates
- [ ] Integration with scraping jobs completed
- [ ] Health checks and validation running automatically
- [ ] Statistics and monitoring providing actionable insights