/**
 * Progress Monitor Component
 * Handles real-time display of scraping job progress and logs
 */

class ProgressMonitor {
    constructor() {
        this.container = document.getElementById('progress-monitor');
        this.logsContainer = document.getElementById('live-logs');
        this.maxLogEntries = 100;
        this.isMonitoring = false;
        this.currentJobId = null;
        this.startTime = null;
        this.timerInterval = null;
        this.init();
    }

    init() {
        if (!this.container) {
            console.warn('Progress monitor container not found');
            return;
        }

        this.initializeElements();
        this.setIdleState();
        
        console.log('Progress monitor initialized');
    }

    initializeElements() {
        this.statusIndicator = this.container.querySelector('.status-indicator');
        this.statusText = this.container.querySelector('.status-text');
        this.progressFill = this.container.querySelector('.progress-fill');
        this.progressText = this.container.querySelector('.progress-text');
        this.itemsScrapedElement = document.getElementById('items-scraped');
        this.successRateElement = document.getElementById('success-rate');
        this.elapsedTimeElement = document.getElementById('elapsed-time');
        this.logsContent = this.logsContainer?.querySelector('.logs-content');
    }

    /**
     * Update progress with job data
     */
    updateProgress(jobData) {
        if (!this.container) return;

        const {
            id,
            name,
            status,
            progress = 0,
            items_scraped = 0,
            items_failed = 0,
            started_at,
            error_message
        } = jobData;

        // Set current job if monitoring
        if (!this.currentJobId || this.currentJobId !== id) {
            this.currentJobId = id;
            this.startTime = started_at ? new Date(started_at) : new Date();
            this.startTimer();
        }

        // Update status
        this.updateStatus(status, name, error_message);

        // Update progress bar
        this.updateProgressBar(progress);

        // Update statistics
        this.updateStatistics(items_scraped, items_failed);

        // Add log entry for status changes
        if (status === 'running' && !this.isMonitoring) {
            this.addLogEntry('Job started', 'info');
            this.isMonitoring = true;
        } else if (status === 'completed') {
            this.addLogEntry(`Job completed successfully. Scraped ${items_scraped} items.`, 'success');
            this.onJobCompleted();
        } else if (status === 'failed') {
            this.addLogEntry(`Job failed: ${error_message || 'Unknown error'}`, 'error');
            this.onJobFailed();
        }
    }

    updateStatus(status, jobName, errorMessage) {
        const statusMap = {
            'idle': { text: 'Ready to start', class: 'idle' },
            'pending': { text: 'Preparing...', class: 'running' },
            'running': { text: `Running: ${jobName}`, class: 'running' },
            'paused': { text: 'Paused', class: 'warning' },
            'completed': { text: 'Completed successfully', class: 'success' },
            'failed': { text: errorMessage || 'Job failed', class: 'error' },
            'cancelled': { text: 'Cancelled', class: 'warning' }
        };

        const statusInfo = statusMap[status] || statusMap['idle'];
        
        if (this.statusIndicator) {
            this.statusIndicator.className = `status-indicator ${statusInfo.class}`;
        }
        
        if (this.statusText) {
            this.statusText.textContent = statusInfo.text;
        }
    }

    updateProgressBar(progress) {
        const percentage = Math.max(0, Math.min(100, progress));
        
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
        
        if (this.progressText) {
            this.progressText.textContent = `${Math.round(percentage)}%`;
        }
    }

    updateStatistics(itemsScraped, itemsFailed) {
        if (this.itemsScrapedElement) {
            this.itemsScrapedElement.textContent = window.helpers.NumberUtils.formatNumber(itemsScraped);
        }

        if (this.successRateElement) {
            const total = itemsScraped + itemsFailed;
            const successRate = total > 0 ? (itemsScraped / total) * 100 : 0;
            this.successRateElement.textContent = `${successRate.toFixed(1)}%`;
        }
    }

    startTimer() {
        this.stopTimer(); // Clear any existing timer
        
        this.timerInterval = setInterval(() => {
            if (this.startTime && this.elapsedTimeElement) {
                const elapsed = Math.floor((Date.now() - this.startTime.getTime()) / 1000);
                this.elapsedTimeElement.textContent = window.helpers.DateUtils.formatDuration(elapsed);
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    setIdleState() {
        this.updateStatus('idle');
        this.updateProgressBar(0);
        this.updateStatistics(0, 0);
        this.stopTimer();
        
        if (this.elapsedTimeElement) {
            this.elapsedTimeElement.textContent = '00:00';
        }
        
        this.isMonitoring = false;
        this.currentJobId = null;
        this.startTime = null;
    }

    onJobCompleted() {
        this.isMonitoring = false;
        this.stopTimer();
        
        // Keep the final statistics visible
        setTimeout(() => {
            // Could auto-reset after some time
            // this.setIdleState();
        }, 30000); // Reset after 30 seconds
    }

    onJobFailed() {
        this.isMonitoring = false;
        this.stopTimer();
        
        // Keep error state visible longer
        setTimeout(() => {
            this.setIdleState();
        }, 60000); // Reset after 1 minute
    }

    /**
     * Add a log entry to the live logs
     */
    addLogEntry(message, type = 'info', timestamp = new Date()) {
        if (!this.logsContent) return;

        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        
        const timeString = timestamp.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        logEntry.innerHTML = `
            <span class="log-time">${timeString}</span>
            <span class="log-message">${message}</span>
        `;

        // Add to top of logs
        this.logsContent.insertBefore(logEntry, this.logsContent.firstChild);

        // Limit number of log entries
        this.limitLogEntries();

        // Auto-scroll to top for new entries
        this.logsContent.scrollTop = 0;
    }

    limitLogEntries() {
        if (!this.logsContent) return;

        const entries = this.logsContent.querySelectorAll('.log-entry');
        if (entries.length > this.maxLogEntries) {
            // Remove oldest entries
            for (let i = this.maxLogEntries; i < entries.length; i++) {
                entries[i].remove();
            }
        }
    }

    /**
     * Clear all log entries
     */
    clearLogs() {
        if (this.logsContent) {
            this.logsContent.innerHTML = '';
            this.addLogEntry('Logs cleared', 'info');
        }
    }

    /**
     * Export logs as text
     */
    exportLogs() {
        if (!this.logsContent) return;

        const entries = Array.from(this.logsContent.querySelectorAll('.log-entry'));
        const logText = entries.reverse().map(entry => {
            const time = entry.querySelector('.log-time').textContent;
            const message = entry.querySelector('.log-message').textContent;
            return `[${time}] ${message}`;
        }).join('\n');

        const filename = `scraperv4-logs-${new Date().toISOString().split('T')[0]}.txt`;
        window.helpers.FileUtils.downloadAsFile(logText, filename, 'text/plain');
    }

    /**
     * Start monitoring a specific job
     */
    startMonitoring(jobId, jobName) {
        this.currentJobId = jobId;
        this.isMonitoring = true;
        this.startTime = new Date();
        
        this.updateStatus('running', jobName);
        this.addLogEntry(`Started monitoring job: ${jobName}`, 'info');
        this.startTimer();
    }

    /**
     * Stop monitoring current job
     */
    stopMonitoring() {
        if (this.currentJobId) {
            this.addLogEntry('Monitoring stopped', 'warning');
        }
        
        this.setIdleState();
    }

    /**
     * Handle real-time updates from backend
     */
    handleRealtimeUpdate(data) {
        const { type, payload } = data;

        switch (type) {
            case 'job_progress':
                this.updateProgress(payload);
                break;
                
            case 'job_log':
                this.addLogEntry(payload.message, payload.level || 'info', new Date(payload.timestamp));
                break;
                
            case 'job_error':
                this.addLogEntry(`Error: ${payload.message}`, 'error');
                break;
                
            case 'job_completed':
                this.addLogEntry('Job completed successfully', 'success');
                this.onJobCompleted();
                break;
                
            case 'job_failed':
                this.addLogEntry(`Job failed: ${payload.error}`, 'error');
                this.onJobFailed();
                break;
                
            default:
                console.log('Unknown realtime update type:', type);
        }
    }

    /**
     * Initialize controls (if needed)
     */
    initControls() {
        // Add control buttons to monitor
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'monitor-controls';
        controlsContainer.innerHTML = `
            <button class="btn btn-sm btn-secondary" id="clear-logs-btn">
                <i class="fas fa-trash"></i> Clear Logs
            </button>
            <button class="btn btn-sm btn-secondary" id="export-logs-btn">
                <i class="fas fa-download"></i> Export
            </button>
        `;

        // Add controls to logs container
        if (this.logsContainer) {
            const header = this.logsContainer.querySelector('h3');
            if (header) {
                header.appendChild(controlsContainer);
            }
        }

        // Bind control events
        document.getElementById('clear-logs-btn')?.addEventListener('click', () => {
            this.clearLogs();
        });

        document.getElementById('export-logs-btn')?.addEventListener('click', () => {
            this.exportLogs();
        });
    }

    /**
     * Add custom CSS for log types
     */
    addLogStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .log-entry.log-error .log-message {
                color: var(--error-color);
            }
            
            .log-entry.log-success .log-message {
                color: var(--success-color);
            }
            
            .log-entry.log-warning .log-message {
                color: var(--warning-color);
            }
            
            .log-entry.log-info .log-message {
                color: var(--text-primary);
            }
            
            .monitor-controls {
                float: right;
                display: flex;
                gap: 0.5rem;
            }
            
            .monitor-controls .btn {
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
            }
            
            .logs-content {
                scrollbar-width: thin;
                scrollbar-color: var(--border-color) transparent;
            }
            
            .logs-content::-webkit-scrollbar {
                width: 6px;
            }
            
            .logs-content::-webkit-scrollbar-track {
                background: transparent;
            }
            
            .logs-content::-webkit-scrollbar-thumb {
                background: var(--border-color);
                border-radius: 3px;
            }
            
            .logs-content::-webkit-scrollbar-thumb:hover {
                background: var(--text-muted);
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize styles and make available globally
document.addEventListener('DOMContentLoaded', () => {
    const monitor = new ProgressMonitor();
    monitor.addLogStyles();
    // monitor.initControls(); // Uncomment if you want log controls
});

window.ProgressMonitor = ProgressMonitor;