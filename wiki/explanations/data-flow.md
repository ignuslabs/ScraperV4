# Data Flow

This document explains how data moves through ScraperV4, from initial request to final export. Understanding this flow is crucial for debugging, optimization, and extending the system.

## Overview of Data Flow

ScraperV4 processes data through multiple stages, each with specific responsibilities and transformations. The flow is designed to be resilient, observable, and efficient.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Request   │ -> │  Job Queue  │ -> │  Scraping   │ -> │   Storage   │
│ (User/API)  │    │ Management  │    │  Execution  │    │ & Processing│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       |                   |                   |                   |
       v                   v                   v                   v
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Validation  │    │ Job State   │    │ Real-time   │    │   Export    │
│ & Queuing   │    │ Tracking    │    │ Progress    │    │ & Delivery  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Stage 1: Request Processing and Validation

### Initial Request

Data flow begins when a user or API client submits a scraping request:

```python
# Web Interface Request
request_data = {
    'name': 'Product Catalog Scrape',
    'template_id': 'ecommerce-product',
    'target_url': 'https://example.com/products',
    'options': {
        'use_proxy': True,
        'max_pages': 50,
        'delay_range': [1, 3]
    }
}
```

### Request Validation

The `ScrapingService` validates incoming requests:

```python
def validate_scraping_request(self, request_data: Dict[str, Any]) -> ValidationResult:
    """Validate scraping request before processing."""
    
    # 1. Schema Validation
    schema_validation = self._validate_against_schema(request_data)
    if not schema_validation.valid:
        return schema_validation
    
    # 2. Template Validation
    template_id = request_data.get('template_id')
    if template_id:
        template_validation = self._validate_template_exists(template_id)
        if not template_validation.valid:
            return template_validation
    
    # 3. URL Validation
    url_validation = self._validate_target_url(request_data.get('target_url'))
    if not url_validation.valid:
        return url_validation
    
    # 4. Resource Availability
    resource_validation = self._validate_resources_available()
    
    return ValidationResult(valid=True)
```

**Validation Checks**:
- Request schema compliance
- Template existence and validity
- URL accessibility and format
- Resource availability (CPU, memory, concurrent jobs)
- Permission and rate limiting

### Job Creation

Valid requests are transformed into job objects:

```python
def create_job(self, name: str, template_id: str, target_url: str, **options) -> JobData:
    """Create a new scraping job."""
    
    job_data = {
        'id': str(uuid.uuid4()),
        'name': name,
        'template_id': template_id,
        'target_url': target_url,
        'status': 'pending',
        'progress': 0,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'options': options,
        'metadata': {
            'estimated_duration': self._estimate_job_duration(template_id, options),
            'resource_requirements': self._calculate_resource_needs(options)
        }
    }
    
    # Persist job to storage
    self.job_manager.save_job(job_data)
    
    return JobData(job_data)
```

## Stage 2: Job Queue Management

### Job Queueing Strategy

ScraperV4 uses a file-based job queue with priority scheduling:

```python
class JobManager:
    def queue_job(self, job: JobData) -> None:
        """Add job to processing queue."""
        
        # Calculate job priority
        priority = self._calculate_job_priority(job)
        
        # Add to appropriate queue
        queue_name = self._determine_queue(job)
        self.queues[queue_name].put((priority, job.id, job))
        
        # Update job status
        self._update_job_status(job.id, 'queued')
        
        # Notify monitoring systems
        self._emit_job_event('job_queued', job.id)
```

**Queue Types**:
- **High Priority**: Small, fast jobs
- **Standard**: Regular scraping jobs
- **Bulk**: Large, multi-page scraping operations
- **Background**: Maintenance and cleanup tasks

### Resource Allocation

Jobs are allocated resources based on requirements:

```python
def allocate_resources(self, job: JobData) -> ResourceAllocation:
    """Allocate system resources for job execution."""
    
    requirements = job.metadata.get('resource_requirements', {})
    
    allocation = ResourceAllocation(
        cpu_cores=min(requirements.get('cpu_cores', 1), self.max_cpu_cores),
        memory_mb=min(requirements.get('memory_mb', 512), self.max_memory_mb),
        network_bandwidth=requirements.get('bandwidth', 'standard'),
        proxy_pool=self._select_proxy_pool(job.options)
    )
    
    # Reserve resources
    self.resource_manager.reserve(job.id, allocation)
    
    return allocation
```

## Stage 3: Scraping Execution

### Template Loading and Preparation

The scraping engine loads the specified template:

```python
def prepare_scraping_context(self, job: JobData) -> ScrapingContext:
    """Prepare everything needed for scraping execution."""
    
    # Load template
    template = self.template_manager.load_template(job.template_id)
    
    # Initialize scrapers
    stealth_fetcher = StealthFetcher(job.options.get('stealth_config', {}))
    template_scraper = TemplateScraper(template)
    
    # Setup proxy rotation
    if job.options.get('use_proxy'):
        proxy_rotator = ProxyRotator(self.proxy_list)
        stealth_fetcher.set_proxy_rotator(proxy_rotator)
    
    return ScrapingContext(
        job=job,
        template=template,
        stealth_fetcher=stealth_fetcher,
        template_scraper=template_scraper
    )
```

### Page Fetching Process

Each page goes through a structured fetching process:

```python
async def fetch_page(self, url: str, context: ScrapingContext) -> PageResult:
    """Fetch and process a single page."""
    
    try:
        # 1. Pre-fetch validation
        if not self._should_fetch_url(url, context):
            return PageResult(skipped=True, reason='URL filtered')
        
        # 2. Apply delays and throttling
        await self._apply_request_delay(context)
        
        # 3. Fetch page with stealth measures
        response = await context.stealth_fetcher.fetch_async(url)
        
        # 4. Detect anti-bot measures
        detection_result = context.stealth_fetcher.detect_anti_bot_measures(response)
        if detection_result['detected']:
            return await self._handle_anti_bot_detection(url, detection_result, context)
        
        # 5. Extract data using template
        extracted_data = context.template_scraper.extract_data(response)
        
        # 6. Post-process data
        processed_data = self._post_process_data(extracted_data, context.template)
        
        # 7. Validate extracted data
        validation_result = self._validate_extracted_data(processed_data, context.template)
        
        return PageResult(
            success=True,
            url=url,
            data=processed_data,
            metadata={
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code,
                'content_length': len(response.content),
                'validation_score': validation_result.score
            }
        )
        
    except Exception as e:
        return PageResult(
            success=False,
            url=url,
            error=str(e),
            metadata={'error_type': type(e).__name__}
        )
```

### Data Extraction Flow

Template-based extraction follows a systematic process:

```python
def extract_data(self, response: Response) -> Dict[str, Any]:
    """Extract data from response using template."""
    
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    extracted_data = {}
    
    for field_name, selector_config in self.template.selectors.items():
        try:
            # 1. Try primary selector
            value = self._extract_with_selector(soup, selector_config['primary'])
            
            # 2. Try fallback selectors if primary fails
            if value is None and 'fallbacks' in selector_config:
                for fallback_selector in selector_config['fallbacks']:
                    value = self._extract_with_selector(soup, fallback_selector)
                    if value is not None:
                        break
            
            # 3. Apply field-specific processing
            if value is not None:
                value = self._process_field_value(value, selector_config)
            
            # 4. Handle required fields
            if value is None and selector_config.get('required', False):
                raise ExtractionError(f"Required field '{field_name}' not found")
            
            extracted_data[field_name] = value
            
        except Exception as e:
            self._log_extraction_error(field_name, str(e))
            if selector_config.get('required', False):
                raise
            extracted_data[field_name] = None
    
    # Apply template-level post-processing
    processed_data = self._apply_template_processing(extracted_data)
    
    return processed_data
```

### Pagination Handling

For multi-page scraping, pagination is handled systematically:

```python
async def handle_pagination(self, initial_url: str, context: ScrapingContext) -> List[PageResult]:
    """Handle paginated content scraping."""
    
    results = []
    current_url = initial_url
    page_count = 0
    
    pagination_config = context.template.pagination
    max_pages = pagination_config.get('max_pages', 10)
    
    while current_url and page_count < max_pages:
        # Fetch and process current page
        page_result = await self.fetch_page(current_url, context)
        results.append(page_result)
        
        # Update progress
        progress = min(100, (page_count + 1) * 100 // max_pages)
        self._update_job_progress(context.job.id, progress)
        
        if not page_result.success:
            break
        
        # Find next page URL
        next_url = self._extract_next_page_url(page_result.response, pagination_config)
        
        # Check stop conditions
        if self._should_stop_pagination(results, pagination_config):
            break
        
        current_url = next_url
        page_count += 1
        
        # Apply inter-page delay
        await self._apply_pagination_delay(pagination_config)
    
    return results
```

## Stage 4: Real-time Progress Tracking

### Progress Updates

Progress is tracked and communicated in real-time:

```python
def update_job_progress(self, job_id: str, progress: int, details: Dict = None):
    """Update job progress and notify interested parties."""
    
    # Update job data
    job_data = self.job_manager.load_job(job_id)
    job_data['progress'] = progress
    job_data['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    if details:
        job_data.setdefault('progress_details', {}).update(details)
    
    # Persist changes
    self.job_manager.save_job(job_data)
    
    # Notify web interface via EEL
    eel.update_job_progress(job_id, progress, details)
    
    # Emit event for monitoring
    self._emit_progress_event(job_id, progress, details)
```

### Status Transitions

Jobs move through defined status states:

```
pending -> queued -> running -> processing -> completed/failed
                        |
                        v
                   cancelling -> cancelled
```

```python
def transition_job_status(self, job_id: str, new_status: str, reason: str = None):
    """Safely transition job to new status."""
    
    job_data = self.job_manager.load_job(job_id)
    current_status = job_data.get('status')
    
    # Validate transition
    if not self._is_valid_status_transition(current_status, new_status):
        raise InvalidStatusTransition(f"Cannot transition from {current_status} to {new_status}")
    
    # Update status
    job_data['status'] = new_status
    job_data['status_updated_at'] = datetime.now(timezone.utc).isoformat()
    
    if reason:
        job_data.setdefault('status_history', []).append({
            'status': new_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        })
    
    self.job_manager.save_job(job_data)
    
    # Notify stakeholders
    self._notify_status_change(job_id, current_status, new_status)
```

## Stage 5: Data Storage and Processing

### Result Storage

Scraped data is stored with comprehensive metadata:

```python
def store_scraping_results(self, job_id: str, results: List[PageResult]) -> str:
    """Store scraping results with metadata."""
    
    # Aggregate successful results
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]
    
    # Compile result data
    result_data = {
        'job_id': job_id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_pages': len(results),
            'successful_pages': len(successful_results),
            'failed_pages': len(failed_results),
            'total_items': sum(len(r.data) for r in successful_results if r.data),
            'average_response_time': self._calculate_average_response_time(results)
        },
        'data': [r.data for r in successful_results],
        'errors': [{'url': r.url, 'error': r.error} for r in failed_results],
        'metadata': {
            'extraction_version': self.version,
            'template_version': self._get_template_version(job_id),
            'processing_rules': self._get_processing_rules(job_id)
        }
    }
    
    # Generate unique result ID
    result_id = f"result_{job_id}_{int(time.time())}"
    
    # Store to file system
    result_path = self._get_result_path(result_id)
    with open(result_path, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    # Update job with result reference
    self._update_job_result_reference(job_id, result_id)
    
    return result_id
```

### Data Processing Pipeline

Stored data goes through additional processing:

```python
def process_scraped_data(self, result_id: str, processing_rules: Dict) -> ProcessedResult:
    """Apply post-processing rules to scraped data."""
    
    raw_data = self.load_result_data(result_id)
    
    processed_data = []
    
    for item in raw_data['data']:
        processed_item = item.copy()
        
        # 1. Text cleaning
        if processing_rules.get('text_cleaning', {}).get('enabled', True):
            processed_item = self._clean_text_fields(processed_item, processing_rules['text_cleaning'])
        
        # 2. Data type conversion
        if 'type_conversions' in processing_rules:
            processed_item = self._convert_data_types(processed_item, processing_rules['type_conversions'])
        
        # 3. Data validation
        if 'validation_rules' in processing_rules:
            validation_result = self._validate_item(processed_item, processing_rules['validation_rules'])
            if not validation_result.valid:
                processed_item['_validation_errors'] = validation_result.errors
        
        # 4. Data enrichment
        if 'enrichment_rules' in processing_rules:
            processed_item = self._enrich_item(processed_item, processing_rules['enrichment_rules'])
        
        processed_data.append(processed_item)
    
    # Store processed version
    processed_result_id = f"{result_id}_processed"
    self._store_processed_data(processed_result_id, processed_data)
    
    return ProcessedResult(processed_result_id, processed_data)
```

## Stage 6: Export and Delivery

### Export Format Selection

Data can be exported in multiple formats:

```python
def export_result_data(self, result_id: str, format: str, options: Dict = None) -> ExportResult:
    """Export scraped data in specified format."""
    
    options = options or {}
    result_data = self.load_result_data(result_id)
    
    if format == 'json':
        return self._export_json(result_data, options)
    elif format == 'csv':
        return self._export_csv(result_data, options)
    elif format == 'xlsx':
        return self._export_excel(result_data, options)
    else:
        raise UnsupportedExportFormat(f"Format '{format}' not supported")
```

### Excel Export with Formatting

Excel exports include rich formatting and metadata:

```python
def _export_excel(self, result_data: Dict, options: Dict) -> ExportResult:
    """Export data to Excel with formatting."""
    
    workbook = openpyxl.Workbook()
    
    # Main data sheet
    data_sheet = workbook.active
    data_sheet.title = "Scraped Data"
    
    # Extract data items
    items = result_data.get('data', [])
    if not items:
        return ExportResult(success=False, error="No data to export")
    
    # Get all unique field names
    all_fields = set()
    for item in items:
        all_fields.update(item.keys())
    
    headers = sorted(all_fields)
    
    # Write headers
    for col, header in enumerate(headers, 1):
        cell = data_sheet.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
    
    # Write data
    for row, item in enumerate(items, 2):
        for col, field in enumerate(headers, 1):
            value = item.get(field, '')
            data_sheet.cell(row=row, column=col, value=value)
    
    # Auto-adjust column widths
    for column in data_sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column)
        data_sheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
    
    # Add metadata sheet if requested
    if options.get('include_metadata', False):
        self._add_metadata_sheet(workbook, result_data)
    
    # Save to file
    export_path = self._get_export_path(result_data['job_id'], 'xlsx')
    workbook.save(export_path)
    
    return ExportResult(
        success=True,
        file_path=export_path,
        format='xlsx',
        record_count=len(items)
    )
```

## Data Flow Monitoring

### Metrics Collection

ScraperV4 collects detailed metrics throughout the data flow:

```python
class DataFlowMetrics:
    def __init__(self):
        self.metrics = {
            'requests_processed': Counter(),
            'jobs_created': Counter(),
            'pages_scraped': Counter(),
            'extraction_errors': Counter(),
            'processing_time': Histogram(),
            'queue_wait_time': Histogram(),
            'export_requests': Counter()
        }
    
    def record_job_created(self, job_id: str, template_id: str):
        self.metrics['jobs_created'].inc({'template_id': template_id})
    
    def record_page_scraped(self, job_id: str, success: bool, response_time: float):
        self.metrics['pages_scraped'].inc({'status': 'success' if success else 'failed'})
        self.metrics['processing_time'].observe(response_time)
```

### Error Tracking

Errors are tracked and categorized throughout the flow:

```python
def track_error(self, error_type: str, job_id: str, details: Dict = None):
    """Track and categorize errors for analysis."""
    
    error_record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'error_type': error_type,
        'job_id': job_id,
        'details': details or {}
    }
    
    # Store error record
    self.error_tracker.record_error(error_record)
    
    # Emit monitoring event
    self._emit_error_event(error_record)
    
    # Check for error patterns
    if self._detect_error_pattern(error_type, job_id):
        self._alert_error_pattern(error_type, job_id)
```

## Performance Optimization

### Caching Strategy

Results and intermediate data are cached strategically:

```python
class DataFlowCache:
    def __init__(self):
        self.page_cache = {}  # Cache fetched pages
        self.template_cache = {}  # Cache compiled templates
        self.processing_cache = {}  # Cache processing results
    
    def get_cached_page(self, url: str, cache_duration: int = 3600) -> Optional[Response]:
        """Get cached page if available and fresh."""
        cache_key = self._generate_cache_key(url)
        
        if cache_key in self.page_cache:
            cached_item = self.page_cache[cache_key]
            if time.time() - cached_item['timestamp'] < cache_duration:
                return cached_item['response']
        
        return None
```

### Parallel Processing

Multiple stages can run in parallel:

```python
async def process_job_parallel(self, job: JobData) -> JobResult:
    """Process job with parallel execution where possible."""
    
    # Create processing context
    context = await self.prepare_scraping_context(job)
    
    # Get URLs to process
    urls = await self.discover_urls(job.target_url, context)
    
    # Process URLs in batches
    batch_size = job.options.get('batch_size', 10)
    url_batches = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)]
    
    all_results = []
    
    for batch in url_batches:
        # Process batch in parallel
        batch_tasks = [self.fetch_page(url, context) for url in batch]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        all_results.extend(batch_results)
        
        # Update progress
        progress = len(all_results) * 100 // len(urls)
        self.update_job_progress(job.id, progress)
    
    return JobResult(job.id, all_results)
```

## Conclusion

ScraperV4's data flow is designed for reliability, observability, and performance. Each stage has clear responsibilities and well-defined interfaces, making the system maintainable and extensible.

The flow supports both simple single-page scraping and complex multi-page operations, with comprehensive error handling and recovery mechanisms. Real-time progress tracking keeps users informed, while detailed metrics enable continuous optimization.

Understanding this data flow helps developers debug issues, optimize performance, and extend the system with new capabilities. The modular design ensures that improvements to one stage don't affect others, supporting the system's long-term evolution.