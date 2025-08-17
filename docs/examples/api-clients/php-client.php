<?php
/**
 * ScraperV4 PHP API Client
 * 
 * A comprehensive PHP client for interacting with ScraperV4's REST API.
 * Provides a clean, object-oriented interface with proper error handling,
 * retry logic, and support for all major API operations.
 * 
 * Features:
 * - PSR-4 autoloading compatible
 * - Comprehensive error handling with custom exceptions
 * - Automatic retry logic with exponential backoff
 * - Real-time job monitoring with callbacks
 * - Streaming data export for large datasets
 * - Extensive logging and debugging support
 * - Type hints and detailed documentation
 * 
 * Requirements:
 * - PHP 7.4 or higher
 * - cURL extension
 * - JSON extension
 * 
 * Installation via Composer:
 *   composer require guzzlehttp/guzzle monolog/monolog
 * 
 * Usage:
 *   require_once 'vendor/autoload.php';
 *   
 *   $client = new ScraperV4Client('http://localhost:8080');
 *   $templates = $client->listTemplates();
 *   echo "Found " . count($templates) . " templates\n";
 * 
 * @author ScraperV4 Team
 * @version 3.0.0
 * @package ScraperV4
 */

declare(strict_types=1);

/**
 * Custom exception for ScraperV4 API errors
 */
class ScraperV4APIException extends Exception
{
    private ?int $statusCode;
    private ?array $responseData;
    
    public function __construct(
        string $message,
        ?int $statusCode = null,
        ?array $responseData = null,
        int $code = 0,
        ?Throwable $previous = null
    ) {
        parent::__construct($message, $code, $previous);
        $this->statusCode = $statusCode;
        $this->responseData = $responseData;
    }
    
    public function getStatusCode(): ?int
    {
        return $this->statusCode;
    }
    
    public function getResponseData(): ?array
    {
        return $this->responseData;
    }
}

/**
 * Main ScraperV4 API Client class
 */
class ScraperV4Client
{
    private string $baseUrl;
    private int $timeout;
    private int $maxRetries;
    private float $retryDelay;
    private array $defaultHeaders;
    private $logger;
    
    /**
     * Create a new ScraperV4 client
     * 
     * @param string $baseUrl ScraperV4 server URL
     * @param array $options Client configuration options
     */
    public function __construct(string $baseUrl = 'http://localhost:8080', array $options = [])
    {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $options['timeout'] ?? 30;
        $this->maxRetries = $options['max_retries'] ?? 3;
        $this->retryDelay = $options['retry_delay'] ?? 1.0;
        
        $this->defaultHeaders = array_merge([
            'Content-Type: application/json',
            'Accept: application/json',
            'User-Agent: ScraperV4-PHP-Client/3.0.0'
        ], $options['headers'] ?? []);
        
        // Initialize logger if provided
        $this->logger = $options['logger'] ?? null;
    }
    
    /**
     * Log a message if logger is available
     * 
     * @param string $level Log level
     * @param string $message Log message
     * @param array $context Context data
     */
    private function log(string $level, string $message, array $context = []): void
    {
        if ($this->logger && method_exists($this->logger, $level)) {
            $this->logger->{$level}($message, $context);
        }
    }
    
    /**
     * Make HTTP request with retry logic
     * 
     * @param string $method HTTP method
     * @param string $endpoint API endpoint
     * @param array|null $data Request data
     * @param array $options Additional cURL options
     * @return array Response data
     * @throws ScraperV4APIException
     */
    private function makeRequest(string $method, string $endpoint, ?array $data = null, array $options = []): array
    {
        $url = $this->baseUrl . $endpoint;
        
        for ($attempt = 0; $attempt <= $this->maxRetries; $attempt++) {
            try {
                $this->log('debug', "API Request: {$method} {$url}", ['attempt' => $attempt + 1]);
                
                $curl = curl_init();
                
                // Basic cURL options
                curl_setopt_array($curl, [
                    CURLOPT_URL => $url,
                    CURLOPT_RETURNTRANSFER => true,
                    CURLOPT_TIMEOUT => $this->timeout,
                    CURLOPT_HTTPHEADER => $this->defaultHeaders,
                    CURLOPT_CUSTOMREQUEST => $method,
                    CURLOPT_FOLLOWLOCATION => true,
                    CURLOPT_MAXREDIRS => 3,
                    CURLOPT_SSL_VERIFYPEER => false, // For development
                ]);
                
                // Add request data for POST/PUT requests
                if ($data !== null) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
                }
                
                // Apply additional options
                if (!empty($options)) {
                    curl_setopt_array($curl, $options);
                }
                
                $response = curl_exec($curl);
                $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
                $error = curl_error($curl);
                
                curl_close($curl);
                
                if ($response === false) {
                    throw new ScraperV4APIException("cURL error: {$error}");
                }
                
                // Parse JSON response
                $responseData = json_decode($response, true);
                if (json_last_error() !== JSON_ERROR_NONE) {
                    // Handle non-JSON responses
                    if ($httpCode >= 200 && $httpCode < 300) {
                        return ['data' => $response, 'content_type' => 'text/plain'];
                    } else {
                        throw new ScraperV4APIException("Invalid JSON response: " . json_last_error_msg(), $httpCode);
                    }
                }
                
                // Handle HTTP errors
                if ($httpCode >= 400) {
                    $errorMessage = $responseData['error'] ?? "HTTP {$httpCode} Error";
                    throw new ScraperV4APIException($errorMessage, $httpCode, $responseData);
                }
                
                return $responseData;
                
            } catch (ScraperV4APIException $e) {
                if ($attempt === $this->maxRetries) {
                    throw $e;
                }
                
                // Exponential backoff
                $delay = $this->retryDelay * pow(2, $attempt);
                $this->log('warning', "Request failed (attempt " . ($attempt + 1) . "), retrying in {$delay}s: " . $e->getMessage());
                usleep((int)($delay * 1000000)); // Convert to microseconds
            }
        }
        
        throw new ScraperV4APIException("Max retries ({$this->maxRetries}) exceeded");
    }
    
    // Template Management Methods
    
    /**
     * List all scraping templates
     * 
     * @param bool $includeInactive Include inactive templates
     * @return array List of templates
     * @throws ScraperV4APIException
     */
    public function listTemplates(bool $includeInactive = false): array
    {
        $endpoint = '/api/templates';
        if ($includeInactive) {
            $endpoint .= '?include_inactive=true';
        }
        
        $response = $this->makeRequest('GET', $endpoint);
        return $response['templates'] ?? [];
    }
    
    /**
     * Get a specific template by ID
     * 
     * @param string $templateId Template identifier
     * @return array Template data
     * @throws ScraperV4APIException
     */
    public function getTemplate(string $templateId): array
    {
        $response = $this->makeRequest('GET', "/api/templates/{$templateId}");
        return $response['template'] ?? [];
    }
    
    /**
     * Create a new scraping template
     * 
     * @param array $templateData Template configuration
     * @return array Created template with ID
     * @throws ScraperV4APIException
     */
    public function createTemplate(array $templateData): array
    {
        return $this->makeRequest('POST', '/api/templates', $templateData);
    }
    
    /**
     * Update an existing template
     * 
     * @param string $templateId Template identifier
     * @param array $templateData Updated configuration
     * @return array Updated template
     * @throws ScraperV4APIException
     */
    public function updateTemplate(string $templateId, array $templateData): array
    {
        return $this->makeRequest('PUT', "/api/templates/{$templateId}", $templateData);
    }
    
    /**
     * Delete a template
     * 
     * @param string $templateId Template identifier
     * @return bool Success status
     * @throws ScraperV4APIException
     */
    public function deleteTemplate(string $templateId): bool
    {
        $this->makeRequest('DELETE', "/api/templates/{$templateId}");
        return true;
    }
    
    /**
     * Test a template against a URL
     * 
     * @param string $templateId Template identifier
     * @param string $testUrl URL to test against
     * @return array Test results
     * @throws ScraperV4APIException
     */
    public function testTemplate(string $templateId, string $testUrl): array
    {
        return $this->makeRequest('POST', "/api/templates/{$templateId}/test", ['url' => $testUrl]);
    }
    
    // Job Management Methods
    
    /**
     * Create a new scraping job
     * 
     * @param string $name Job name
     * @param string $templateId Template ID to use
     * @param string $targetUrl URL to scrape
     * @param array $config Optional job configuration
     * @return array Created job with ID
     * @throws ScraperV4APIException
     */
    public function createJob(string $name, string $templateId, string $targetUrl, array $config = []): array
    {
        $jobData = [
            'name' => $name,
            'template_id' => $templateId,
            'target_url' => $targetUrl,
            'config' => $config
        ];
        
        return $this->makeRequest('POST', '/api/scraping/jobs', $jobData);
    }
    
    /**
     * Start a scraping job
     * 
     * @param string $jobId Job identifier
     * @return array Job status
     * @throws ScraperV4APIException
     */
    public function startJob(string $jobId): array
    {
        return $this->makeRequest('POST', '/api/scraping/start', ['job_id' => $jobId]);
    }
    
    /**
     * Stop a running job
     * 
     * @param string $jobId Job identifier
     * @return array Updated job status
     * @throws ScraperV4APIException
     */
    public function stopJob(string $jobId): array
    {
        return $this->makeRequest('POST', "/api/scraping/stop/{$jobId}");
    }
    
    /**
     * Get current job status
     * 
     * @param string $jobId Job identifier
     * @return array Job status with progress information
     * @throws ScraperV4APIException
     */
    public function getJobStatus(string $jobId): array
    {
        return $this->makeRequest('GET', "/api/scraping/status/{$jobId}");
    }
    
    /**
     * List scraping jobs with optional filtering
     * 
     * @param array $options Filtering options
     * @return array Jobs list with pagination info
     * @throws ScraperV4APIException
     */
    public function listJobs(array $options = []): array
    {
        $params = http_build_query([
            'limit' => $options['limit'] ?? 50,
            'offset' => $options['offset'] ?? 0,
            'status' => $options['status'] ?? null
        ]);
        
        $endpoint = '/api/scraping/jobs?' . $params;
        return $this->makeRequest('GET', $endpoint);
    }
    
    /**
     * Monitor a job until completion with progress callback
     * 
     * @param string $jobId Job identifier
     * @param callable|null $progressCallback Progress callback function
     * @param int $pollInterval Polling interval in seconds
     * @return array Final job status
     * @throws ScraperV4APIException
     */
    public function monitorJob(string $jobId, ?callable $progressCallback = null, int $pollInterval = 2): array
    {
        $this->log('info', "Monitoring job {$jobId}");
        
        while (true) {
            $status = $this->getJobStatus($jobId);
            
            if ($progressCallback) {
                call_user_func($progressCallback, $status);
            }
            
            $jobStatus = $status['status'] ?? 'unknown';
            if (in_array($jobStatus, ['completed', 'failed', 'stopped', 'error'])) {
                $this->log('info', "Job {$jobId} finished with status: {$jobStatus}");
                return $status;
            }
            
            $progress = $status['progress'] ?? 0;
            $this->log('debug', "Job {$jobId} - Status: {$jobStatus}, Progress: {$progress}%");
            
            sleep($pollInterval);
        }
    }
    
    // Data Access Methods
    
    /**
     * Get scraped results for a job
     * 
     * @param string $jobId Job identifier
     * @param int $limit Maximum results to return
     * @param int $offset Number of results to skip
     * @return array List of scraped data items
     * @throws ScraperV4APIException
     */
    public function getJobResults(string $jobId, int $limit = 100, int $offset = 0): array
    {
        $params = http_build_query(['limit' => $limit, 'offset' => $offset]);
        $endpoint = "/api/data/results/{$jobId}?" . $params;
        
        $response = $this->makeRequest('GET', $endpoint);
        return $response['results'] ?? [];
    }
    
    /**
     * Export job data to specified format
     * 
     * @param string $jobId Job identifier
     * @param string $format Export format (json, csv, xlsx)
     * @param bool $includeMetadata Include job metadata
     * @param string|null $outputFile Local file path to save export
     * @return array|string Export result or file path
     * @throws ScraperV4APIException
     */
    public function exportJobData(string $jobId, string $format = 'json', bool $includeMetadata = true, ?string $outputFile = null)
    {
        $exportData = [
            'job_id' => $jobId,
            'format' => $format,
            'include_metadata' => $includeMetadata
        ];
        
        $response = $this->makeRequest('POST', '/api/data/export', $exportData);
        
        // Download file if local path specified
        if ($outputFile && isset($response['file_path'])) {
            $fileUrl = $response['file_path'];
            if (!filter_var($fileUrl, FILTER_VALIDATE_URL)) {
                $fileUrl = $this->baseUrl . $fileUrl;
            }
            
            $fileContent = file_get_contents($fileUrl);
            if ($fileContent === false) {
                throw new ScraperV4APIException("Failed to download export file from: {$fileUrl}");
            }
            
            if (file_put_contents($outputFile, $fileContent) === false) {
                throw new ScraperV4APIException("Failed to save export file to: {$outputFile}");
            }
            
            return $outputFile;
        }
        
        return $response;
    }
    
    /**
     * Stream job results in chunks for large datasets
     * 
     * @param string $jobId Job identifier
     * @param int $chunkSize Items per chunk
     * @return Generator Generator yielding result chunks
     * @throws ScraperV4APIException
     */
    public function streamJobResults(string $jobId, int $chunkSize = 100): Generator
    {
        $offset = 0;
        
        while (true) {
            $results = $this->getJobResults($jobId, $chunkSize, $offset);
            
            if (empty($results)) {
                break;
            }
            
            yield $results;
            
            if (count($results) < $chunkSize) {
                break; // No more results
            }
            
            $offset += $chunkSize;
        }
    }
    
    // Preview and Testing Methods
    
    /**
     * Preview scraping results without creating a full job
     * 
     * @param string $url URL to preview
     * @param string|null $templateId Optional template ID
     * @return array Preview results
     * @throws ScraperV4APIException
     */
    public function previewScraping(string $url, ?string $templateId = null): array
    {
        $previewData = ['url' => $url];
        if ($templateId) {
            $previewData['template_id'] = $templateId;
        }
        
        return $this->makeRequest('POST', '/api/scraping/preview', $previewData);
    }
    
    // Statistics and Monitoring Methods
    
    /**
     * Get system-wide scraping statistics
     * 
     * @return array System statistics
     * @throws ScraperV4APIException
     */
    public function getSystemStats(): array
    {
        return $this->makeRequest('GET', '/api/data/stats');
    }
    
    /**
     * Check API health status
     * 
     * @return array Health status
     * @throws ScraperV4APIException
     */
    public function healthCheck(): array
    {
        return $this->makeRequest('GET', '/api/health');
    }
}

/**
 * High-level job management utility
 */
class ScraperV4JobManager
{
    private ScraperV4Client $client;
    private array $activeJobs = [];
    
    /**
     * Create a new job manager
     * 
     * @param ScraperV4Client $client ScraperV4 client instance
     */
    public function __construct(ScraperV4Client $client)
    {
        $this->client = $client;
    }
    
    /**
     * Complete scraping workflow: create, monitor, and export
     * 
     * @param array $config Scraping configuration
     * @return array Complete job results
     * @throws ScraperV4APIException
     */
    public function scrapeUrlWithTemplate(array $config): array
    {
        $url = $config['url'] ?? throw new InvalidArgumentException('URL is required');
        $templateId = $config['template_id'] ?? throw new InvalidArgumentException('Template ID is required');
        $jobName = $config['job_name'] ?? 'Scrape ' . parse_url($url, PHP_URL_HOST) . ' ' . date('Y-m-d H:i:s');
        $jobConfig = $config['job_config'] ?? [];
        $monitor = $config['monitor'] ?? true;
        $exportFormat = $config['export_format'] ?? null;
        
        // Create job
        echo "Creating job: {$jobName}\n";
        $job = $this->client->createJob($jobName, $templateId, $url, $jobConfig);
        $jobId = $job['job_id'] ?? $job['id'];
        
        // Start job
        echo "Starting job: {$jobId}\n";
        $this->client->startJob($jobId);
        
        // Monitor if requested
        $finalStatus = null;
        if ($monitor) {
            $progressCallback = function ($status) use ($jobId) {
                $progress = $status['progress'] ?? 0;
                $items = $status['items_scraped'] ?? 0;
                echo "Job {$jobId} - Progress: {$progress}%, Items: {$items}\n";
            };
            
            $finalStatus = $this->client->monitorJob($jobId, $progressCallback);
        }
        
        // Get results
        $results = [];
        if (!$finalStatus || ($finalStatus['status'] ?? '') === 'completed') {
            echo "Getting results for job: {$jobId}\n";
            $results = $this->client->getJobResults($jobId);
        }
        
        // Export if requested
        $exportInfo = null;
        if ($exportFormat && !empty($results)) {
            echo "Exporting results in {$exportFormat} format\n";
            $exportInfo = $this->client->exportJobData($jobId, $exportFormat);
        }
        
        return [
            'job_id' => $jobId,
            'job_name' => $jobName,
            'status' => $finalStatus,
            'results' => $results,
            'export_info' => $exportInfo,
            'total_items' => count($results)
        ];
    }
    
    /**
     * Scrape multiple URLs with rate limiting
     * 
     * @param array $urls URLs to scrape
     * @param string $templateId Template to use for all URLs
     * @param array $options Batch scraping options
     * @return array List of job results
     * @throws ScraperV4APIException
     */
    public function batchScrapeUrls(array $urls, string $templateId, array $options = []): array
    {
        $maxConcurrent = $options['max_concurrent'] ?? 3;
        $jobConfig = $options['job_config'] ?? [];
        $delay = $options['delay'] ?? 2; // Delay between job starts
        
        $results = [];
        $activeJobs = [];
        
        foreach ($urls as $i => $url) {
            // Wait for slot if at max concurrent
            while (count($activeJobs) >= $maxConcurrent) {
                $activeJobs = $this->checkCompletedJobs($activeJobs, $results);
                sleep(1);
            }
            
            try {
                $jobName = "Batch Scrape " . ($i + 1) . "/" . count($urls);
                $job = $this->client->createJob($jobName, $templateId, $url, $jobConfig);
                $jobId = $job['job_id'] ?? $job['id'];
                
                $this->client->startJob($jobId);
                $activeJobs[$jobId] = ['url' => $url, 'start_time' => time()];
                
                echo "Started job {$jobId} for {$url} (" . ($i + 1) . "/" . count($urls) . ")\n";
                
                // Delay between starts
                if ($i < count($urls) - 1) {
                    sleep($delay);
                }
                
            } catch (Exception $e) {
                echo "Failed to start job for {$url}: " . $e->getMessage() . "\n";
                $results[] = ['url' => $url, 'error' => $e->getMessage(), 'success' => false];
            }
        }
        
        // Wait for all remaining jobs to complete
        while (!empty($activeJobs)) {
            $activeJobs = $this->checkCompletedJobs($activeJobs, $results);
            sleep(1);
        }
        
        return $results;
    }
    
    /**
     * Check for completed jobs and update results
     * 
     * @param array $activeJobs Active job tracking
     * @param array &$results Results array to update
     * @return array Updated active jobs
     */
    private function checkCompletedJobs(array $activeJobs, array &$results): array
    {
        foreach ($activeJobs as $jobId => $jobInfo) {
            try {
                $status = $this->client->getJobStatus($jobId);
                $jobStatus = $status['status'] ?? 'unknown';
                
                if (in_array($jobStatus, ['completed', 'failed', 'stopped', 'error'])) {
                    $result = [
                        'job_id' => $jobId,
                        'url' => $jobInfo['url'],
                        'status' => $jobStatus,
                        'success' => $jobStatus === 'completed'
                    ];
                    
                    if ($jobStatus === 'completed') {
                        $jobResults = $this->client->getJobResults($jobId);
                        $result['results'] = $jobResults;
                        $result['total_items'] = count($jobResults);
                    } else {
                        $result['error'] = $status['error'] ?? 'Job failed';
                    }
                    
                    $results[] = $result;
                    unset($activeJobs[$jobId]);
                    
                    echo "Completed job {$jobId} for {$jobInfo['url']} - Status: {$jobStatus}\n";
                }
                
            } catch (Exception $e) {
                echo "Error checking job {$jobId}: " . $e->getMessage() . "\n";
                unset($activeJobs[$jobId]);
            }
        }
        
        return $activeJobs;
    }
}

/**
 * Example usage and testing
 */
function exampleUsage(): void
{
    try {
        // Initialize client
        $client = new ScraperV4Client('http://localhost:8080');
        
        // Health check
        $health = $client->healthCheck();
        echo "✅ API Health: " . json_encode($health) . "\n";
        
        // List templates
        $templates = $client->listTemplates();
        echo "📋 Found " . count($templates) . " templates\n";
        
        if (!empty($templates)) {
            $templateId = $templates[0]['id'];
            
            // Test template
            $testUrl = 'https://example.com';
            echo "🧪 Testing template {$templateId} on {$testUrl}\n";
            
            $testResult = $client->testTemplate($templateId, $testUrl);
            $success = $testResult['success'] ?? false;
            echo "✅ Test result: " . ($success ? 'SUCCESS' : 'FAILED') . "\n";
            
            // High-level job manager example
            $jobManager = new ScraperV4JobManager($client);
            
            // Complete workflow
            $result = $jobManager->scrapeUrlWithTemplate([
                'url' => $testUrl,
                'template_id' => $templateId,
                'job_name' => 'PHP client test',
                'export_format' => 'json'
            ]);
            
            echo "🎯 Scraping completed: " . $result['total_items'] . " items\n";
            
            // Batch scraping example
            $urls = [
                'https://example.com',
                'https://httpbin.org/html'
            ];
            
            $batchResults = $jobManager->batchScrapeUrls($urls, $templateId, [
                'max_concurrent' => 2,
                'delay' => 1
            ]);
            
            echo "📦 Batch scraping completed: " . count($batchResults) . " jobs\n";
            
            // Display batch results summary
            $successful = array_filter($batchResults, fn($r) => $r['success'] ?? false);
            echo "   Successful: " . count($successful) . "/" . count($batchResults) . "\n";
        }
        
    } catch (ScraperV4APIException $e) {
        echo "❌ API Error: " . $e->getMessage() . "\n";
        if ($e->getStatusCode()) {
            echo "   Status Code: " . $e->getStatusCode() . "\n";
        }
        if ($e->getResponseData()) {
            echo "   Response: " . json_encode($e->getResponseData()) . "\n";
        }
    } catch (Exception $e) {
        echo "❌ Unexpected error: " . $e->getMessage() . "\n";
    }
}

// Run example if this file is executed directly
if (basename(__FILE__) === basename($_SERVER['SCRIPT_NAME'])) {
    exampleUsage();
}

?>