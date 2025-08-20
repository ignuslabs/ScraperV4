# How to Debug Failed Scraping Operations

This guide covers systematic approaches to diagnosing and fixing common scraping failures in ScraperV4.

## Prerequisites

- ScraperV4 installed and configured
- Basic understanding of HTTP requests and responses
- Familiarity with browser developer tools
- Access to log files and debugging tools

## Overview

Common scraping failure categories:
- **Network Issues**: Connectivity, timeouts, proxy problems
- **Content Issues**: Page structure changes, invalid selectors
- **Protection Systems**: Anti-bot measures, CAPTCHAs, rate limiting
- **Configuration Problems**: Invalid templates, incorrect settings
- **System Resources**: Memory, CPU, or storage limitations

## Systematic Debugging Approach

### 1. Initial Failure Analysis

```python
def analyze_scraping_failure(job_id):
    """Comprehensive failure analysis for scraping jobs."""
    from src.services.scraping_service import ScrapingService
    from src.services.data_service import DataService
    
    scraping_service = ScrapingService()
    data_service = DataService()
    
    # Get job details
    job_status = scraping_service.get_job_status(job_id)
    job_results = data_service.get_job_results(job_id, limit=10)
    
    analysis = {
        'job_id': job_id,
        'overall_status': job_status.get('status'),
        'failure_categories': [],
        'recommendations': [],
        'diagnostic_data': {}
    }
    
    # Analyze job status
    if job_status.get('status') == 'failed':
        error_message = job_status.get('error', '')
        analysis['diagnostic_data']['primary_error'] = error_message
        
        # Categorize error
        if 'timeout' in error_message.lower():
            analysis['failure_categories'].append('network_timeout')
            analysis['recommendations'].append('Increase timeout values or check network connectivity')
        
        elif 'proxy' in error_message.lower():
            analysis['failure_categories'].append('proxy_issues')
            analysis['recommendations'].append('Verify proxy configuration and availability')
        
        elif 'selector' in error_message.lower() or 'not found' in error_message.lower():
            analysis['failure_categories'].append('selector_issues')
            analysis['recommendations'].append('Update CSS selectors or verify page structure')
        
        elif 'rate limit' in error_message.lower() or '429' in error_message:
            analysis['failure_categories'].append('rate_limiting')
            analysis['recommendations'].append('Reduce request frequency and implement delays')
    
    # Analyze results for patterns
    if job_results:
        success_count = len([r for r in job_results if r.status == 'success'])
        total_count = len(job_results)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        analysis['diagnostic_data']['success_rate'] = success_rate
        analysis['diagnostic_data']['total_attempts'] = total_count
        
        if success_rate < 0.5:
            analysis['failure_categories'].append('high_failure_rate')
            analysis['recommendations'].append('Review template configuration and target site changes')
    
    return analysis

# Example usage
failure_analysis = analyze_scraping_failure("job-12345")
print(f"Failure categories: {failure_analysis['failure_categories']}")
print(f"Recommendations: {failure_analysis['recommendations']}")
```

### 2. Detailed Error Investigation

```python
def investigate_error_details(job_id):
    """Deep dive into error details and patterns."""
    import re
    from collections import Counter
    from src.services.data_service import DataService
    
    data_service = DataService()
    results = data_service.get_job_results(job_id, limit=100)
    
    investigation = {
        'error_patterns': Counter(),
        'status_codes': Counter(),
        'response_times': [],
        'url_patterns': Counter(),
        'timeline_analysis': []
    }
    
    for result in results:
        # Extract error patterns
        if hasattr(result, 'data') and result.data:
            error = result.data.get('error', '')
            if error:
                # Categorize error types
                if 'timeout' in error.lower():
                    investigation['error_patterns']['timeout'] += 1
                elif 'connection' in error.lower():
                    investigation['error_patterns']['connection'] += 1
                elif '404' in error or 'not found' in error.lower():
                    investigation['error_patterns']['not_found'] += 1
                elif '403' in error or 'forbidden' in error.lower():
                    investigation['error_patterns']['forbidden'] += 1
                elif '429' in error or 'rate limit' in error.lower():
                    investigation['error_patterns']['rate_limited'] += 1
                else:
                    investigation['error_patterns']['other'] += 1
            
            # Status codes
            status_code = result.data.get('status_code')
            if status_code:
                investigation['status_codes'][status_code] += 1
            
            # Response times
            response_time = result.data.get('response_time')
            if response_time:
                investigation['response_times'].append(response_time)
            
            # URL patterns
            url = result.data.get('url', '')
            if url:
                # Extract domain
                domain = re.search(r'https?://([^/]+)', url)
                if domain:
                    investigation['url_patterns'][domain.group(1)] += 1
    
    # Response time analysis
    if investigation['response_times']:
        times = investigation['response_times']
        investigation['response_time_stats'] = {
            'average': sum(times) / len(times),
            'max': max(times),
            'min': min(times),
            'count_slow': len([t for t in times if t > 10])  # > 10 seconds
        }
    
    return investigation

# Example usage
investigation = investigate_error_details("job-12345")
print(f"Most common errors: {investigation['error_patterns'].most_common(5)}")
print(f"Status code distribution: {dict(investigation['status_codes'])}")
```

## Network and Connectivity Issues

### 1. Diagnose Network Problems

```python
def diagnose_network_issues(target_url, proxy_config=None):
    """Diagnose network connectivity and performance issues."""
    import requests
    import time
    from urllib.parse import urlparse
    
    diagnosis = {
        'target_url': target_url,
        'connectivity_tests': {},
        'proxy_tests': {},
        'performance_metrics': {},
        'recommendations': []
    }
    
    # Basic connectivity test
    try:
        start_time = time.time()
        response = requests.get(target_url, timeout=30)
        response_time = time.time() - start_time
        
        diagnosis['connectivity_tests']['direct'] = {
            'status': 'success',
            'status_code': response.status_code,
            'response_time': response_time,
            'content_length': len(response.content)
        }
        
        if response_time > 10:
            diagnosis['recommendations'].append('High response time detected - consider using faster proxies')
        
    except requests.exceptions.Timeout:
        diagnosis['connectivity_tests']['direct'] = {
            'status': 'timeout',
            'error': 'Request timed out'
        }
        diagnosis['recommendations'].append('Increase timeout values or check network connectivity')
        
    except requests.exceptions.ConnectionError as e:
        diagnosis['connectivity_tests']['direct'] = {
            'status': 'connection_error',
            'error': str(e)
        }
        diagnosis['recommendations'].append('Check internet connectivity and target URL validity')
    
    # Test with different User-Agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'ScraperV4/1.0'
    ]
    
    for i, ua in enumerate(user_agents):
        try:
            response = requests.get(
                target_url, 
                headers={'User-Agent': ua}, 
                timeout=15
            )
            diagnosis['connectivity_tests'][f'user_agent_{i}'] = {
                'status': 'success',
                'status_code': response.status_code,
                'user_agent': ua[:50] + '...'
            }
        except Exception as e:
            diagnosis['connectivity_tests'][f'user_agent_{i}'] = {
                'status': 'failed',
                'error': str(e),
                'user_agent': ua[:50] + '...'
            }
    
    # Proxy testing if configured
    if proxy_config:
        for i, proxy in enumerate(proxy_config.get('proxy_list', [])[:3]):
            try:
                proxies = {'http': proxy, 'https': proxy}
                start_time = time.time()
                response = requests.get(target_url, proxies=proxies, timeout=20)
                response_time = time.time() - start_time
                
                diagnosis['proxy_tests'][f'proxy_{i}'] = {
                    'status': 'success',
                    'proxy': proxy,
                    'response_time': response_time,
                    'status_code': response.status_code
                }
                
            except Exception as e:
                diagnosis['proxy_tests'][f'proxy_{i}'] = {
                    'status': 'failed',
                    'proxy': proxy,
                    'error': str(e)
                }
    
    return diagnosis

# Example usage
network_diagnosis = diagnose_network_issues(
    "https://example.com",
    proxy_config={'proxy_list': ['http://proxy1.com:8080', 'http://proxy2.com:8080']}
)
```

### 2. Proxy Troubleshooting

```python
def troubleshoot_proxy_issues(proxy_list):
    """Comprehensive proxy troubleshooting."""
    import requests
    import time
    from src.scrapers.proxy_rotator import ProxyRotator
    
    troubleshooting = {
        'proxy_analysis': [],
        'recommendations': [],
        'working_proxies': [],
        'failed_proxies': []
    }
    
    # Test each proxy individually
    for proxy in proxy_list:
        proxy_test = {
            'proxy': proxy,
            'tests': {}
        }
        
        # Basic connectivity test
        try:
            proxies = {'http': proxy, 'https': proxy}
            start_time = time.time()
            response = requests.get(
                'http://httpbin.org/ip', 
                proxies=proxies, 
                timeout=10
            )
            response_time = time.time() - start_time
            
            proxy_test['tests']['connectivity'] = {
                'status': 'success',
                'response_time': response_time,
                'ip_returned': response.json().get('origin')
            }
            
        except Exception as e:
            proxy_test['tests']['connectivity'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # HTTPS test
        try:
            response = requests.get(
                'https://httpbin.org/ip', 
                proxies=proxies, 
                timeout=10
            )
            proxy_test['tests']['https'] = {
                'status': 'success',
                'status_code': response.status_code
            }
            
        except Exception as e:
            proxy_test['tests']['https'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Performance test
        performance_times = []
        for _ in range(3):
            try:
                start_time = time.time()
                requests.get('http://httpbin.org/delay/1', proxies=proxies, timeout=15)
                performance_times.append(time.time() - start_time)
            except:
                break
        
        if performance_times:
            avg_time = sum(performance_times) / len(performance_times)
            proxy_test['tests']['performance'] = {
                'status': 'success',
                'average_time': avg_time,
                'consistency': max(performance_times) - min(performance_times)
            }
        
        # Determine if proxy is working
        connectivity_ok = proxy_test['tests'].get('connectivity', {}).get('status') == 'success'
        https_ok = proxy_test['tests'].get('https', {}).get('status') == 'success'
        
        if connectivity_ok and https_ok:
            troubleshooting['working_proxies'].append(proxy)
        else:
            troubleshooting['failed_proxies'].append(proxy)
        
        troubleshooting['proxy_analysis'].append(proxy_test)
    
    # Generate recommendations
    working_count = len(troubleshooting['working_proxies'])
    total_count = len(proxy_list)
    
    if working_count == 0:
        troubleshooting['recommendations'].append('No working proxies found - verify proxy credentials and endpoints')
    elif working_count < total_count * 0.5:
        troubleshooting['recommendations'].append('Less than 50% of proxies working - review proxy quality')
    else:
        troubleshooting['recommendations'].append(f'{working_count}/{total_count} proxies working - configuration looks good')
    
    return troubleshooting

# Example usage
proxy_troubleshooting = troubleshoot_proxy_issues([
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080'
])
```

## Content and Selector Issues

### 1. Validate CSS Selectors

```python
def validate_selectors(url, selectors):
    """Validate CSS selectors against target page."""
    from bs4 import BeautifulSoup
    import requests
    
    validation = {
        'url': url,
        'selector_results': {},
        'page_analysis': {},
        'recommendations': []
    }
    
    try:
        # Fetch the page
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        validation['page_analysis'] = {
            'status_code': response.status_code,
            'content_length': len(response.content),
            'title': soup.title.string if soup.title else 'No title',
            'total_elements': len(soup.find_all())
        }
        
        # Test each selector
        for name, selector in selectors.items():
            try:
                # Parse selector for type
                if '::text' in selector:
                    base_selector = selector.replace('::text', '')
                    elements = soup.select(base_selector)
                    texts = [elem.get_text().strip() for elem in elements]
                    
                    validation['selector_results'][name] = {
                        'status': 'success',
                        'element_count': len(elements),
                        'sample_text': texts[:3] if texts else [],
                        'selector': selector
                    }
                
                elif '::attr(' in selector:
                    # Extract attribute name
                    attr_match = selector.split('::attr(')[1].rstrip(')')
                    base_selector = selector.split('::attr(')[0]
                    elements = soup.select(base_selector)
                    attrs = [elem.get(attr_match) for elem in elements if elem.get(attr_match)]
                    
                    validation['selector_results'][name] = {
                        'status': 'success',
                        'element_count': len(elements),
                        'attribute_count': len(attrs),
                        'sample_values': attrs[:3] if attrs else [],
                        'selector': selector
                    }
                
                else:
                    # Regular selector
                    elements = soup.select(selector)
                    
                    validation['selector_results'][name] = {
                        'status': 'success',
                        'element_count': len(elements),
                        'sample_html': [str(elem)[:100] + '...' for elem in elements[:2]],
                        'selector': selector
                    }
                
                # Generate recommendations for problematic selectors
                element_count = validation['selector_results'][name]['element_count']
                if element_count == 0:
                    validation['recommendations'].append(
                        f"Selector '{name}' found no elements - verify selector syntax and page structure"
                    )
                elif element_count > 100:
                    validation['recommendations'].append(
                        f"Selector '{name}' found {element_count} elements - consider making selector more specific"
                    )
                
            except Exception as e:
                validation['selector_results'][name] = {
                    'status': 'error',
                    'error': str(e),
                    'selector': selector
                }
                validation['recommendations'].append(
                    f"Selector '{name}' has syntax error: {str(e)}"
                )
    
    except Exception as e:
        validation['page_analysis']['error'] = str(e)
        validation['recommendations'].append(f"Failed to fetch page: {str(e)}")
    
    return validation

# Example usage
selector_validation = validate_selectors(
    "https://example.com",
    {
        'title': 'h1::text',
        'links': 'a::attr(href)',
        'content': '.main-content p::text'
    }
)
```

### 2. Page Structure Analysis

```python
def analyze_page_structure(url, previous_structure=None):
    """Analyze page structure and detect changes."""
    from bs4 import BeautifulSoup
    import requests
    from collections import Counter
    
    analysis = {
        'url': url,
        'structure_info': {},
        'changes_detected': [],
        'element_distribution': {},
        'recommendations': []
    }
    
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Basic structure analysis
        analysis['structure_info'] = {
            'title': soup.title.string if soup.title else None,
            'total_elements': len(soup.find_all()),
            'unique_tags': len(set(tag.name for tag in soup.find_all())),
            'has_javascript': bool(soup.find_all('script')),
            'has_forms': bool(soup.find_all('form')),
            'meta_description': None
        }
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            analysis['structure_info']['meta_description'] = meta_desc.get('content', '')[:100]
        
        # Element distribution
        tag_counter = Counter(tag.name for tag in soup.find_all())
        analysis['element_distribution'] = dict(tag_counter.most_common(10))
        
        # Class and ID analysis
        classes = []
        ids = []
        for elem in soup.find_all():
            if elem.get('class'):
                classes.extend(elem.get('class'))
            if elem.get('id'):
                ids.append(elem.get('id'))
        
        analysis['structure_info']['common_classes'] = [
            cls for cls, count in Counter(classes).most_common(10)
        ]
        analysis['structure_info']['total_ids'] = len(set(ids))
        
        # Compare with previous structure if provided
        if previous_structure:
            current_total = analysis['structure_info']['total_elements']
            previous_total = previous_structure.get('structure_info', {}).get('total_elements', 0)
            
            if abs(current_total - previous_total) > previous_total * 0.1:  # >10% change
                analysis['changes_detected'].append(
                    f"Significant element count change: {previous_total} -> {current_total}"
                )
            
            current_title = analysis['structure_info']['title']
            previous_title = previous_structure.get('structure_info', {}).get('title')
            
            if current_title != previous_title:
                analysis['changes_detected'].append(
                    f"Page title changed: '{previous_title}' -> '{current_title}'"
                )
        
        # Generate recommendations
        if analysis['structure_info']['total_elements'] < 50:
            analysis['recommendations'].append("Page has very few elements - check if page loaded completely")
        
        if not analysis['structure_info']['has_javascript']:
            analysis['recommendations'].append("No JavaScript detected - static scraping should work well")
        else:
            analysis['recommendations'].append("JavaScript detected - consider using browser automation for dynamic content")
        
        if len(analysis['changes_detected']) > 0:
            analysis['recommendations'].append("Page structure changes detected - update selectors accordingly")
    
    except Exception as e:
        analysis['error'] = str(e)
        analysis['recommendations'].append(f"Failed to analyze page structure: {str(e)}")
    
    return analysis

# Example usage
structure_analysis = analyze_page_structure("https://example.com")
```

## Template and Configuration Debugging

### 1. Template Validation

```python
def debug_template_configuration(template_id):
    """Debug template configuration issues."""
    from src.services.template_service import TemplateService
    
    template_service = TemplateService()
    debugging = {
        'template_id': template_id,
        'validation_results': {},
        'test_results': {},
        'recommendations': []
    }
    
    try:
        # Get template
        template = template_service.get_template(template_id)
        if not template:
            debugging['validation_results']['template_exists'] = False
            debugging['recommendations'].append('Template not found - verify template ID')
            return debugging
        
        debugging['validation_results']['template_exists'] = True
        
        # Validate required fields
        required_fields = ['name', 'selectors']
        for field in required_fields:
            if field in template:
                debugging['validation_results'][f'has_{field}'] = True
            else:
                debugging['validation_results'][f'has_{field}'] = False
                debugging['recommendations'].append(f'Template missing required field: {field}')
        
        # Validate selectors
        selectors = template.get('selectors', {})
        if selectors:
            debugging['validation_results']['selector_count'] = len(selectors)
            
            for name, selector in selectors.items():
                if not selector or not isinstance(selector, str):
                    debugging['recommendations'].append(f'Invalid selector for {name}: {selector}')
                elif '::' not in selector and not selector.startswith('.') and not selector.startswith('#'):
                    debugging['recommendations'].append(f'Selector {name} may need refinement: {selector}')
        
        # Test template against a sample URL if provided
        test_url = template.get('test_url')
        if test_url:
            try:
                test_result = template_service.test_template(template_id, test_url)
                debugging['test_results'] = test_result
                
                if test_result.get('success'):
                    debugging['recommendations'].append('Template test passed successfully')
                else:
                    debugging['recommendations'].append(f"Template test failed: {test_result.get('error')}")
            
            except Exception as e:
                debugging['test_results']['error'] = str(e)
                debugging['recommendations'].append(f'Template testing failed: {str(e)}')
        
        # Validate post-processing rules
        post_processing = template.get('post_processing', {})
        if post_processing:
            debugging['validation_results']['has_post_processing'] = True
            
            # Check for common issues
            if 'extract_numbers' in post_processing:
                fields = post_processing['extract_numbers']
                if not all(field in selectors for field in fields):
                    debugging['recommendations'].append('Post-processing references non-existent selector fields')
    
    except Exception as e:
        debugging['error'] = str(e)
        debugging['recommendations'].append(f'Template debugging failed: {str(e)}')
    
    return debugging

# Example usage
template_debugging = debug_template_configuration("product-template")
```

### 2. Configuration Validation

```python
def validate_scraping_configuration(config):
    """Validate scraping job configuration."""
    validation = {
        'config_valid': True,
        'issues': [],
        'warnings': [],
        'recommendations': []
    }
    
    # Required fields
    required_fields = ['name', 'template_id', 'target_url']
    for field in required_fields:
        if field not in config:
            validation['issues'].append(f'Missing required field: {field}')
            validation['config_valid'] = False
    
    # URL validation
    target_url = config.get('target_url')
    if target_url:
        if not target_url.startswith(('http://', 'https://')):
            validation['issues'].append('Invalid target URL format')
            validation['config_valid'] = False
        
        # Check for localhost/private IPs in production
        if any(private in target_url for private in ['localhost', '127.0.0.1', '192.168.', '10.']):
            validation['warnings'].append('Target URL appears to be local/private - verify accessibility')
    
    # Validate delay settings
    delay_range = config.get('delay_range', [1, 3])
    if isinstance(delay_range, (list, tuple)) and len(delay_range) == 2:
        min_delay, max_delay = delay_range
        if min_delay < 0 or max_delay < min_delay:
            validation['issues'].append('Invalid delay range configuration')
            validation['config_valid'] = False
        elif min_delay < 0.5:
            validation['warnings'].append('Very short delay may trigger rate limiting')
    
    # Validate proxy configuration
    proxy_config = config.get('proxy_config', {})
    if proxy_config.get('use_proxy'):
        proxy_list = proxy_config.get('proxy_list', [])
        if not proxy_list:
            validation['warnings'].append('Proxy enabled but no proxy list provided')
        else:
            for proxy in proxy_list[:3]:  # Check first 3
                if not proxy.startswith(('http://', 'https://', 'socks5://')):
                    validation['issues'].append(f'Invalid proxy format: {proxy}')
    
    # Validate concurrency settings
    concurrent_requests = config.get('concurrent_requests', 1)
    if concurrent_requests > 10:
        validation['warnings'].append('High concurrency may overwhelm target server')
    elif concurrent_requests < 1:
        validation['issues'].append('Concurrent requests must be at least 1')
        validation['config_valid'] = False
    
    # Generate recommendations
    if validation['config_valid']:
        validation['recommendations'].append('Configuration appears valid')
    else:
        validation['recommendations'].append('Fix configuration issues before proceeding')
    
    if validation['warnings']:
        validation['recommendations'].append('Review warnings for potential issues')
    
    return validation

# Example usage
config_validation = validate_scraping_configuration({
    'name': 'Test Job',
    'template_id': 'product-template',
    'target_url': 'https://example.com',
    'delay_range': [1, 3],
    'concurrent_requests': 2
})
```

## Performance and Resource Issues

### 1. Memory Usage Analysis

```python
def analyze_memory_usage(job_id):
    """Analyze memory usage patterns for a scraping job."""
    import psutil
    import gc
    from src.services.data_service import DataService
    
    analysis = {
        'job_id': job_id,
        'memory_stats': {},
        'gc_stats': {},
        'recommendations': []
    }
    
    # Current memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    
    analysis['memory_stats'] = {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent(),
        'available_mb': psutil.virtual_memory().available / 1024 / 1024
    }
    
    # Garbage collection statistics
    analysis['gc_stats'] = {
        'collections': gc.get_stats(),
        'objects': len(gc.get_objects()),
        'referrers': len(gc.get_referrers())
    }
    
    # Job-specific memory analysis
    data_service = DataService()
    results_count = data_service.get_job_results_count(job_id)
    
    if results_count > 0:
        estimated_memory_per_result = analysis['memory_stats']['rss_mb'] / results_count
        analysis['memory_stats']['estimated_mb_per_result'] = estimated_memory_per_result
        
        if estimated_memory_per_result > 1:  # >1MB per result
            analysis['recommendations'].append('High memory usage per result - consider data optimization')
    
    # Memory recommendations
    if analysis['memory_stats']['percent'] > 80:
        analysis['recommendations'].append('High memory usage - consider reducing batch size or enabling streaming')
    
    if analysis['memory_stats']['available_mb'] < 500:
        analysis['recommendations'].append('Low available memory - monitor for potential out-of-memory errors')
    
    if analysis['gc_stats']['objects'] > 100000:
        analysis['recommendations'].append('High object count - consider explicit garbage collection')
    
    return analysis

# Example usage
memory_analysis = analyze_memory_usage("job-12345")
```

### 2. Performance Bottleneck Detection

```python
def detect_performance_bottlenecks(job_id):
    """Detect performance bottlenecks in scraping operations."""
    import time
    from src.services.scraping_service import ScrapingService
    from src.services.data_service import DataService
    
    bottlenecks = {
        'job_id': job_id,
        'bottleneck_analysis': {},
        'timing_analysis': {},
        'recommendations': []
    }
    
    # Get job timing data
    scraping_service = ScrapingService()
    job_status = scraping_service.get_job_status(job_id)
    
    start_time = job_status.get('start_time')
    current_time = time.time()
    
    if start_time:
        elapsed_time = current_time - start_time
        progress = job_status.get('progress', 0)
        
        bottlenecks['timing_analysis'] = {
            'elapsed_minutes': elapsed_time / 60,
            'progress_percent': progress,
            'estimated_total_minutes': (elapsed_time / max(progress, 0.01)) / 60,
            'rate_per_minute': progress / max(elapsed_time / 60, 0.01)
        }
        
        # Bottleneck detection
        if bottlenecks['timing_analysis']['rate_per_minute'] < 1:
            bottlenecks['bottleneck_analysis']['slow_processing'] = True
            bottlenecks['recommendations'].append('Very slow processing rate - check delays and network issues')
        
        if elapsed_time > 3600 and progress < 50:  # >1 hour, <50% progress
            bottlenecks['bottleneck_analysis']['stalled_job'] = True
            bottlenecks['recommendations'].append('Job appears stalled - investigate error logs')
    
    # Analyze recent results for performance patterns
    data_service = DataService()
    recent_results = data_service.get_job_results(job_id, limit=20)
    
    if recent_results:
        response_times = []
        error_count = 0
        
        for result in recent_results:
            if hasattr(result, 'data') and result.data:
                response_time = result.data.get('response_time')
                if response_time:
                    response_times.append(response_time)
                
                if result.data.get('error'):
                    error_count += 1
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            bottlenecks['timing_analysis']['avg_response_time'] = avg_response_time
            bottlenecks['timing_analysis']['max_response_time'] = max_response_time
            
            if avg_response_time > 10:
                bottlenecks['bottleneck_analysis']['slow_responses'] = True
                bottlenecks['recommendations'].append('Slow server responses - consider faster proxies or different timing')
            
            if max_response_time > 30:
                bottlenecks['bottleneck_analysis']['timeout_risk'] = True
                bottlenecks['recommendations'].append('Some very slow responses - increase timeout values')
        
        error_rate = error_count / len(recent_results)
        if error_rate > 0.2:  # >20% error rate
            bottlenecks['bottleneck_analysis']['high_error_rate'] = True
            bottlenecks['recommendations'].append('High error rate affecting performance - investigate error causes')
    
    return bottlenecks

# Example usage
bottleneck_analysis = detect_performance_bottlenecks("job-12345")
```

## Automated Debugging Tools

### 1. Comprehensive Debug Report

```python
def generate_debug_report(job_id):
    """Generate comprehensive debug report for failed job."""
    import json
    from datetime import datetime
    
    debug_report = {
        'report_generated': datetime.utcnow().isoformat(),
        'job_id': job_id,
        'sections': {}
    }
    
    # Run all diagnostic functions
    try:
        debug_report['sections']['failure_analysis'] = analyze_scraping_failure(job_id)
    except Exception as e:
        debug_report['sections']['failure_analysis'] = {'error': str(e)}
    
    try:
        debug_report['sections']['error_investigation'] = investigate_error_details(job_id)
    except Exception as e:
        debug_report['sections']['error_investigation'] = {'error': str(e)}
    
    try:
        debug_report['sections']['memory_analysis'] = analyze_memory_usage(job_id)
    except Exception as e:
        debug_report['sections']['memory_analysis'] = {'error': str(e)}
    
    try:
        debug_report['sections']['bottleneck_analysis'] = detect_performance_bottlenecks(job_id)
    except Exception as e:
        debug_report['sections']['bottleneck_analysis'] = {'error': str(e)}
    
    # Compile all recommendations
    all_recommendations = []
    for section_name, section_data in debug_report['sections'].items():
        if isinstance(section_data, dict):
            recommendations = section_data.get('recommendations', [])
            for rec in recommendations:
                all_recommendations.append(f"[{section_name}] {rec}")
    
    debug_report['consolidated_recommendations'] = all_recommendations
    
    # Save report to file
    from pathlib import Path
    report_dir = Path("data/debug_reports")
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"debug_report_{job_id}_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(debug_report, f, indent=2, default=str)
    
    debug_report['report_file'] = str(report_file)
    
    return debug_report

# Example usage
full_debug_report = generate_debug_report("job-12345")
print(f"Debug report saved to: {full_debug_report['report_file']}")
```

### 2. Real-time Debugging Monitor

```python
class DebuggingMonitor:
    """Real-time monitoring for debugging scraping issues."""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.monitoring = False
        self.alert_thresholds = {
            'error_rate': 0.3,  # 30%
            'response_time': 15,  # 15 seconds
            'memory_usage': 80   # 80%
        }
        self.recent_metrics = []
    
    def start_monitoring(self):
        """Start real-time monitoring."""
        import threading
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        import time
        from src.services.data_service import DataService
        
        data_service = DataService()
        
        while self.monitoring:
            try:
                # Get recent results
                recent_results = data_service.get_job_results(self.job_id, limit=10)
                
                if recent_results:
                    # Calculate metrics
                    error_count = 0
                    response_times = []
                    
                    for result in recent_results:
                        if hasattr(result, 'data') and result.data:
                            if result.data.get('error'):
                                error_count += 1
                            
                            response_time = result.data.get('response_time')
                            if response_time:
                                response_times.append(response_time)
                    
                    current_metrics = {
                        'timestamp': time.time(),
                        'error_rate': error_count / len(recent_results),
                        'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
                        'result_count': len(recent_results)
                    }
                    
                    # Add memory usage
                    import psutil
                    current_metrics['memory_usage'] = psutil.virtual_memory().percent
                    
                    # Check for alerts
                    self._check_alerts(current_metrics)
                    
                    # Store metrics
                    self.recent_metrics.append(current_metrics)
                    if len(self.recent_metrics) > 20:
                        self.recent_metrics.pop(0)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(30)
    
    def _check_alerts(self, metrics):
        """Check metrics against alert thresholds."""
        alerts = []
        
        if metrics['error_rate'] > self.alert_thresholds['error_rate']:
            alerts.append(f"High error rate: {metrics['error_rate']:.1%}")
        
        if metrics['avg_response_time'] > self.alert_thresholds['response_time']:
            alerts.append(f"Slow responses: {metrics['avg_response_time']:.1f}s average")
        
        if metrics['memory_usage'] > self.alert_thresholds['memory_usage']:
            alerts.append(f"High memory usage: {metrics['memory_usage']:.1f}%")
        
        if alerts:
            print(f"[ALERT] Job {self.job_id}: {', '.join(alerts)}")
    
    def get_current_status(self):
        """Get current monitoring status."""
        if not self.recent_metrics:
            return {'status': 'no_data'}
        
        latest = self.recent_metrics[-1]
        return {
            'status': 'monitoring',
            'latest_metrics': latest,
            'trend_analysis': self._analyze_trends(),
            'alert_status': self._check_alert_status(latest)
        }
    
    def _analyze_trends(self):
        """Analyze metric trends."""
        if len(self.recent_metrics) < 3:
            return {'insufficient_data': True}
        
        recent_3 = self.recent_metrics[-3:]
        error_rates = [m['error_rate'] for m in recent_3]
        response_times = [m['avg_response_time'] for m in recent_3]
        
        return {
            'error_rate_trend': 'increasing' if error_rates[-1] > error_rates[0] else 'stable_or_decreasing',
            'response_time_trend': 'increasing' if response_times[-1] > response_times[0] else 'stable_or_decreasing'
        }
    
    def _check_alert_status(self, metrics):
        """Check if any alerts are currently active."""
        active_alerts = []
        
        for threshold_name, threshold_value in self.alert_thresholds.items():
            if threshold_name in metrics and metrics[threshold_name] > threshold_value:
                active_alerts.append(threshold_name)
        
        return {
            'active_alerts': active_alerts,
            'alert_count': len(active_alerts)
        }

# Example usage
monitor = DebuggingMonitor("job-12345")
monitor_thread = monitor.start_monitoring()

# Let it run for a while, then check status
import time
time.sleep(60)

status = monitor.get_current_status()
print(f"Monitoring status: {status}")

monitor.stop_monitoring()
```

## Troubleshooting Quick Reference

### Common Error Patterns and Solutions

```python
ERROR_SOLUTIONS = {
    'timeout': {
        'description': 'Request timeout errors',
        'solutions': [
            'Increase timeout values in configuration',
            'Check network connectivity',
            'Use faster proxy servers',
            'Reduce concurrent requests'
        ]
    },
    'connection_error': {
        'description': 'Network connection failures',
        'solutions': [
            'Verify target URL accessibility',
            'Check proxy configuration',
            'Test internet connectivity',
            'Try different user agents'
        ]
    },
    'selector_not_found': {
        'description': 'CSS selectors not finding elements',
        'solutions': [
            'Verify selectors against current page structure',
            'Check if page requires JavaScript',
            'Update selectors for layout changes',
            'Test selectors in browser developer tools'
        ]
    },
    'rate_limited': {
        'description': 'Too many requests / rate limiting',
        'solutions': [
            'Increase delays between requests',
            'Implement proxy rotation',
            'Reduce concurrent requests',
            'Add randomization to request timing'
        ]
    },
    'captcha_detected': {
        'description': 'CAPTCHA or bot detection',
        'solutions': [
            'Enable stealth mode',
            'Use browser automation',
            'Implement CAPTCHA solving',
            'Change request patterns'
        ]
    },
    'memory_error': {
        'description': 'Out of memory errors',
        'solutions': [
            'Enable streaming mode',
            'Reduce batch sizes',
            'Implement garbage collection',
            'Increase system memory'
        ]
    }
}

def get_quick_solution(error_message):
    """Get quick solution for common errors."""
    error_lower = error_message.lower()
    
    for error_type, info in ERROR_SOLUTIONS.items():
        if error_type.replace('_', ' ') in error_lower:
            return {
                'error_type': error_type,
                'description': info['description'],
                'solutions': info['solutions']
            }
    
    return {
        'error_type': 'unknown',
        'description': 'Unknown error pattern',
        'solutions': [
            'Check logs for more details',
            'Verify configuration',
            'Test with simpler setup',
            'Contact support with error details'
        ]
    }

# Example usage
solution = get_quick_solution("Connection timeout after 30 seconds")
print(f"Error type: {solution['error_type']}")
print(f"Solutions: {solution['solutions']}")
```

## Expected Outcomes

After implementing debugging procedures:

1. **Faster Problem Resolution**: Systematic approach to identifying issues
2. **Improved Reliability**: Proactive detection of potential problems
3. **Better Understanding**: Clear insights into failure patterns
4. **Reduced Downtime**: Quick identification and resolution of issues
5. **Enhanced Monitoring**: Real-time visibility into scraping operations

## Success Criteria

- [ ] Comprehensive debugging tools implemented
- [ ] Error categorization and analysis working
- [ ] Network and connectivity diagnostics functional
- [ ] Template and configuration validation complete
- [ ] Performance bottleneck detection operational
- [ ] Real-time monitoring capabilities available
- [ ] Quick reference solutions documented