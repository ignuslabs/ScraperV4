/**
 * ScraperV4 JavaScript/Node.js API Client
 * 
 * A comprehensive JavaScript client for interacting with ScraperV4's REST API.
 * Supports both Node.js and browser environments with modern ES6+ features.
 * 
 * Features:
 * - Promise-based API with async/await support
 * - Automatic retry logic with exponential backoff
 * - Real-time job monitoring with event callbacks
 * - Streaming data export for large datasets
 * - Comprehensive error handling and validation
 * - Browser and Node.js compatibility
 * - TypeScript-ready with JSDoc annotations
 * 
 * Installation:
 *   npm install axios
 * 
 * Usage:
 *   import { ScraperV4Client } from './scraperv4-client.js';
 *   
 *   const client = new ScraperV4Client('http://localhost:8080');
 *   const templates = await client.listTemplates();
 *   console.log(`Found ${templates.length} templates`);
 * 
 * @author ScraperV4 Team
 * @version 3.0.0
 */

// Import dependencies (adjust for your environment)
const axios = require('axios'); // For Node.js
const fs = require('fs').promises; // For Node.js file operations
const path = require('path'); // For Node.js path operations

/**
 * Custom error class for ScraperV4 API errors
 */
class ScraperV4APIError extends Error {
    /**
     * Create a new API error
     * @param {string} message - Error message
     * @param {number} [statusCode] - HTTP status code
     * @param {Object} [responseData] - Response data from API
     */
    constructor(message, statusCode = null, responseData = null) {
        super(message);
        this.name = 'ScraperV4APIError';
        this.statusCode = statusCode;
        this.responseData = responseData;
    }
}

/**
 * Main ScraperV4 API Client class
 */
class ScraperV4Client {
    /**
     * Create a new ScraperV4 client
     * @param {string} [baseURL='http://localhost:8080'] - ScraperV4 server URL
     * @param {Object} [options={}] - Client configuration options
     * @param {number} [options.timeout=30000] - Request timeout in milliseconds
     * @param {number} [options.maxRetries=3] - Maximum retry attempts
     * @param {number} [options.retryDelay=1000] - Initial retry delay in milliseconds
     * @param {Object} [options.headers={}] - Default headers for all requests
     */
    constructor(baseURL = 'http://localhost:8080', options = {}) {
        this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
        this.timeout = options.timeout || 30000;
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
        
        // Create axios instance with default configuration
        this.httpClient = axios.create({
            baseURL: this.baseURL,
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            }
        });
        
        // Setup request/response interceptors
        this._setupInterceptors();
    }
    
    /**
     * Setup axios interceptors for error handling and retries
     * @private
     */
    _setupInterceptors() {
        // Request interceptor for logging
        this.httpClient.interceptors.request.use(
            (config) => {
                console.debug(`API Request: ${config.method.toUpperCase()} ${config.url}`);
                return config;
            },
            (error) => Promise.reject(error)
        );
        
        // Response interceptor for error handling
        this.httpClient.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response) {
                    // Server responded with error status
                    const { status, data } = error.response;
                    const message = data?.error || `HTTP ${status} Error`;
                    throw new ScraperV4APIError(message, status, data);
                } else if (error.request) {
                    // Network error
                    throw new ScraperV4APIError(`Network error: ${error.message}`);
                } else {
                    // Other error
                    throw new ScraperV4APIError(`Request error: ${error.message}`);
                }
            }
        );
    }
    
    /**
     * Make HTTP request with retry logic
     * @param {string} method - HTTP method
     * @param {string} url - Request URL
     * @param {Object} [data] - Request data
     * @param {Object} [config] - Axios config
     * @returns {Promise<any>} Response data
     * @private
     */
    async _makeRequest(method, url, data = null, config = {}) {
        for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
            try {
                const response = await this.httpClient.request({
                    method,
                    url,
                    data,
                    ...config
                });
                return response.data;
            } catch (error) {
                if (attempt === this.maxRetries) {
                    throw error;
                }
                
                // Exponential backoff
                const delay = this.retryDelay * Math.pow(2, attempt);
                console.warn(`Request failed (attempt ${attempt + 1}), retrying in ${delay}ms: ${error.message}`);
                await this._sleep(delay);
            }
        }
    }
    
    /**
     * Sleep for specified duration
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise<void>}
     * @private
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Template Management Methods
    
    /**
     * List all scraping templates
     * @param {boolean} [includeInactive=false] - Include inactive templates
     * @returns {Promise<Array>} List of templates
     */
    async listTemplates(includeInactive = false) {
        const params = includeInactive ? { include_inactive: true } : {};
        const response = await this._makeRequest('GET', '/api/templates', null, { params });
        return response.templates || [];
    }
    
    /**
     * Get a specific template by ID
     * @param {string} templateId - Template identifier
     * @returns {Promise<Object>} Template object
     */
    async getTemplate(templateId) {
        const response = await this._makeRequest('GET', `/api/templates/${templateId}`);
        return response.template || {};
    }
    
    /**
     * Create a new scraping template
     * @param {Object} templateData - Template configuration
     * @returns {Promise<Object>} Created template with ID
     */
    async createTemplate(templateData) {
        return await this._makeRequest('POST', '/api/templates', templateData);
    }
    
    /**
     * Update an existing template
     * @param {string} templateId - Template identifier
     * @param {Object} templateData - Updated template configuration
     * @returns {Promise<Object>} Updated template
     */
    async updateTemplate(templateId, templateData) {
        return await this._makeRequest('PUT', `/api/templates/${templateId}`, templateData);
    }
    
    /**
     * Delete a template
     * @param {string} templateId - Template identifier
     * @returns {Promise<boolean>} Success status
     */
    async deleteTemplate(templateId) {
        await this._makeRequest('DELETE', `/api/templates/${templateId}`);
        return true;
    }
    
    /**
     * Test a template against a URL
     * @param {string} templateId - Template identifier
     * @param {string} testUrl - URL to test against
     * @returns {Promise<Object>} Test results
     */
    async testTemplate(templateId, testUrl) {
        return await this._makeRequest('POST', `/api/templates/${templateId}/test`, { url: testUrl });
    }
    
    // Job Management Methods
    
    /**
     * Create a new scraping job
     * @param {Object} jobConfig - Job configuration
     * @param {string} jobConfig.name - Job name
     * @param {string} jobConfig.templateId - Template ID to use
     * @param {string} jobConfig.targetUrl - URL to scrape
     * @param {Object} [jobConfig.config] - Additional job configuration
     * @returns {Promise<Object>} Created job with ID
     */
    async createJob({ name, templateId, targetUrl, config = {} }) {
        const jobData = {
            name,
            template_id: templateId,
            target_url: targetUrl,
            config
        };
        return await this._makeRequest('POST', '/api/scraping/jobs', jobData);
    }
    
    /**
     * Start a scraping job
     * @param {string} jobId - Job identifier
     * @returns {Promise<Object>} Job status
     */
    async startJob(jobId) {
        return await this._makeRequest('POST', '/api/scraping/start', { job_id: jobId });
    }
    
    /**
     * Stop a running job
     * @param {string} jobId - Job identifier
     * @returns {Promise<Object>} Updated job status
     */
    async stopJob(jobId) {
        return await this._makeRequest('POST', `/api/scraping/stop/${jobId}`);
    }
    
    /**
     * Get current job status
     * @param {string} jobId - Job identifier
     * @returns {Promise<Object>} Job status with progress information
     */
    async getJobStatus(jobId) {
        return await this._makeRequest('GET', `/api/scraping/status/${jobId}`);
    }
    
    /**
     * List scraping jobs with optional filtering
     * @param {Object} [options={}] - Filtering options
     * @param {string} [options.status] - Filter by job status
     * @param {number} [options.limit=50] - Maximum jobs to return
     * @param {number} [options.offset=0] - Number of jobs to skip
     * @returns {Promise<Object>} Jobs list with pagination info
     */
    async listJobs({ status, limit = 50, offset = 0 } = {}) {
        const params = { limit, offset };
        if (status) params.status = status;
        
        return await this._makeRequest('GET', '/api/scraping/jobs', null, { params });
    }
    
    /**
     * Monitor a job until completion with progress callback
     * @param {string} jobId - Job identifier
     * @param {Function} [onProgress] - Progress callback function
     * @param {number} [pollInterval=2000] - Polling interval in milliseconds
     * @returns {Promise<Object>} Final job status
     */
    async monitorJob(jobId, onProgress = null, pollInterval = 2000) {
        console.log(`Monitoring job ${jobId}`);
        
        while (true) {
            const status = await this.getJobStatus(jobId);
            
            if (onProgress) {
                onProgress(status);
            }
            
            const jobStatus = status.status || 'unknown';
            if (['completed', 'failed', 'stopped', 'error'].includes(jobStatus)) {
                console.log(`Job ${jobId} finished with status: ${jobStatus}`);
                return status;
            }
            
            console.debug(`Job ${jobId} - Status: ${jobStatus}, Progress: ${status.progress || 0}%`);
            await this._sleep(pollInterval);
        }
    }
    
    // Data Access Methods
    
    /**
     * Get scraped results for a job
     * @param {string} jobId - Job identifier
     * @returns {Promise<Array>} List of scraped data items
     */
    async getJobResults(jobId) {
        const response = await this._makeRequest('GET', `/api/data/results/${jobId}`);
        return response.results || [];
    }
    
    /**
     * Export job data to specified format
     * @param {string} jobId - Job identifier
     * @param {Object} [options={}] - Export options
     * @param {string} [options.format='json'] - Export format (json, csv, xlsx)
     * @param {boolean} [options.includeMetadata=true] - Include job metadata
     * @param {string} [options.outputFile] - Local file path to save export
     * @returns {Promise<Object|string>} Export result or file path
     */
    async exportJobData(jobId, { format = 'json', includeMetadata = true, outputFile } = {}) {
        const exportData = {
            job_id: jobId,
            format,
            include_metadata: includeMetadata
        };
        
        const response = await this._makeRequest('POST', '/api/data/export', exportData);
        
        // Download file if local path specified
        if (outputFile && response.file_path) {
            const fileUrl = response.file_path.startsWith('http') 
                ? response.file_path 
                : `${this.baseURL}${response.file_path}`;
            
            try {
                const fileResponse = await axios.get(fileUrl, { responseType: 'stream' });
                
                // For Node.js environment
                if (typeof fs !== 'undefined') {
                    const writer = fs.createWriteStream(outputFile);
                    fileResponse.data.pipe(writer);
                    
                    return new Promise((resolve, reject) => {
                        writer.on('finish', () => resolve(outputFile));
                        writer.on('error', reject);
                    });
                } else {
                    console.warn('File download not supported in browser environment');
                    return response;
                }
            } catch (error) {
                throw new ScraperV4APIError(`Failed to download export file: ${error.message}`);
            }
        }
        
        return response;
    }
    
    /**
     * Stream job results in chunks for large datasets
     * @param {string} jobId - Job identifier
     * @param {number} [chunkSize=100] - Items per chunk
     * @returns {AsyncGenerator<Array>} Async generator yielding result chunks
     */
    async* streamJobResults(jobId, chunkSize = 100) {
        let offset = 0;
        
        while (true) {
            const params = { limit: chunkSize, offset };
            const response = await this._makeRequest('GET', `/api/data/results/${jobId}`, null, { params });
            
            const results = response.results || [];
            if (results.length === 0) {
                break;
            }
            
            yield results;
            
            // Check if we've reached the end
            const totalResults = response.total || 0;
            if (offset + results.length >= totalResults) {
                break;
            }
            
            offset += chunkSize;
        }
    }
    
    // Preview and Testing Methods
    
    /**
     * Preview scraping results without creating a full job
     * @param {string} url - URL to preview
     * @param {string} [templateId] - Optional template ID
     * @returns {Promise<Object>} Preview results
     */
    async previewScraping(url, templateId = null) {
        const previewData = { url };
        if (templateId) {
            previewData.template_id = templateId;
        }
        
        return await this._makeRequest('POST', '/api/scraping/preview', previewData);
    }
    
    // Statistics and Monitoring Methods
    
    /**
     * Get system-wide scraping statistics
     * @returns {Promise<Object>} System statistics
     */
    async getSystemStats() {
        return await this._makeRequest('GET', '/api/data/stats');
    }
    
    /**
     * Check API health status
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        return await this._makeRequest('GET', '/api/health');
    }
}

/**
 * High-level job management utility
 */
class ScraperV4JobManager {
    /**
     * Create a new job manager
     * @param {ScraperV4Client} client - ScraperV4 client instance
     */
    constructor(client) {
        this.client = client;
        this.activeJobs = new Map();
    }
    
    /**
     * Complete scraping workflow: create, monitor, and export
     * @param {Object} config - Scraping configuration
     * @param {string} config.url - URL to scrape
     * @param {string} config.templateId - Template to use
     * @param {string} [config.jobName] - Job name (auto-generated if not provided)
     * @param {Object} [config.jobConfig] - Job configuration
     * @param {boolean} [config.monitor=true] - Monitor job until completion
     * @param {string} [config.exportFormat] - Export format (json, csv, xlsx)
     * @returns {Promise<Object>} Complete job results
     */
    async scrapeUrlWithTemplate({
        url,
        templateId,
        jobName,
        jobConfig = {},
        monitor = true,
        exportFormat = null
    }) {
        // Generate job name if not provided
        if (!jobName) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const domain = new URL(url).hostname || 'unknown';
            jobName = `Scrape_${domain}_${timestamp}`;
        }
        
        // Create job
        console.log(`Creating job: ${jobName}`);
        const job = await this.client.createJob({
            name: jobName,
            templateId,
            targetUrl: url,
            config: jobConfig
        });
        
        const jobId = job.job_id;
        
        // Start job
        console.log(`Starting job: ${jobId}`);
        await this.client.startJob(jobId);
        
        // Monitor if requested
        let finalStatus = null;
        if (monitor) {
            const progressCallback = (status) => {
                const progress = status.progress || 0;
                const items = status.items_scraped || 0;
                console.log(`Job ${jobId} - Progress: ${progress}%, Items: ${items}`);
            };
            
            finalStatus = await this.client.monitorJob(jobId, progressCallback);
        }
        
        // Get results
        let results = [];
        if (!finalStatus || finalStatus.status === 'completed') {
            console.log(`Getting results for job: ${jobId}`);
            results = await this.client.getJobResults(jobId);
        }
        
        // Export if requested
        let exportInfo = null;
        if (exportFormat && results.length > 0) {
            console.log(`Exporting results in ${exportFormat} format`);
            exportInfo = await this.client.exportJobData(jobId, { format: exportFormat });
        }
        
        return {
            jobId,
            jobName,
            status: finalStatus,
            results,
            exportInfo,
            totalItems: results.length
        };
    }
    
    /**
     * Scrape multiple URLs concurrently with rate limiting
     * @param {Array<string>} urls - URLs to scrape
     * @param {string} templateId - Template to use for all URLs
     * @param {Object} [options={}] - Batch scraping options
     * @param {number} [options.maxConcurrent=3] - Maximum concurrent jobs
     * @param {Object} [options.jobConfig] - Configuration for all jobs
     * @returns {Promise<Array>} List of job results
     */
    async batchScrapeUrls(urls, templateId, { maxConcurrent = 3, jobConfig = {} } = {}) {
        const results = [];
        const executing = [];
        
        for (const url of urls) {
            const promise = this.scrapeUrlWithTemplate({
                url,
                templateId,
                jobConfig,
                monitor: true
            }).then(result => {
                console.log(`Completed ${results.length + 1}/${urls.length} URLs`);
                return result;
            }).catch(error => {
                console.error(`Failed to scrape ${url}: ${error.message}`);
                return { url, error: error.message, success: false };
            });
            
            results.push(promise);
            executing.push(promise);
            
            if (executing.length >= maxConcurrent) {
                await Promise.race(executing);
                executing.splice(executing.findIndex(p => p === promise), 1);
            }
        }
        
        return Promise.all(results);
    }
}

/**
 * Browser-compatible file download utility
 * @param {string} url - File URL
 * @param {string} filename - Download filename
 */
function downloadFile(url, filename) {
    if (typeof window !== 'undefined') {
        // Browser environment
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        console.warn('File download only supported in browser environment');
    }
}

// Example usage
async function exampleUsage() {
    try {
        // Initialize client
        const client = new ScraperV4Client('http://localhost:8080');
        
        // Health check
        const health = await client.healthCheck();
        console.log('✅ API Health:', health);
        
        // List templates
        const templates = await client.listTemplates();
        console.log(`📋 Found ${templates.length} templates`);
        
        if (templates.length > 0) {
            const templateId = templates[0].id;
            
            // Test template
            const testUrl = 'https://example.com';
            console.log(`🧪 Testing template ${templateId} on ${testUrl}`);
            
            const testResult = await client.testTemplate(templateId, testUrl);
            console.log('✅ Test result:', testResult.success || false);
            
            // High-level job manager example
            const jobManager = new ScraperV4JobManager(client);
            
            // Complete workflow
            const result = await jobManager.scrapeUrlWithTemplate({
                url: testUrl,
                templateId,
                jobName: 'JavaScript client test',
                exportFormat: 'json'
            });
            
            console.log(`🎯 Scraping completed: ${result.totalItems} items`);
            
            // Batch scraping example
            const urls = [
                'https://example.com',
                'https://httpbin.org/html',
                'https://quotes.toscrape.com'
            ];
            
            const batchResults = await jobManager.batchScrapeUrls(urls, templateId, {
                maxConcurrent: 2
            });
            
            console.log(`📦 Batch scraping completed: ${batchResults.length} jobs`);
        }
        
    } catch (error) {
        if (error instanceof ScraperV4APIError) {
            console.error('❌ API Error:', error.message);
            if (error.statusCode) {
                console.error('   Status Code:', error.statusCode);
            }
        } else {
            console.error('❌ Unexpected error:', error.message);
        }
    }
}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = {
        ScraperV4Client,
        ScraperV4JobManager,
        ScraperV4APIError,
        downloadFile
    };
} else if (typeof window !== 'undefined') {
    // Browser
    window.ScraperV4Client = ScraperV4Client;
    window.ScraperV4JobManager = ScraperV4JobManager;
    window.ScraperV4APIError = ScraperV4APIError;
    window.downloadFile = downloadFile;
}

// Run example if this file is executed directly
if (require.main === module) {
    exampleUsage();
}