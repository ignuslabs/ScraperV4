/**
 * Frontend Logger Utility
 * Sends logs to backend for persistent storage in logs/ folder
 */

class FrontendLogger {
    constructor() {
        this.logLevel = 'DEBUG';
        this.buffer = [];
        this.bufferSize = 10;
        this.flushInterval = 2000; // Flush every 2 seconds
        
        // Log levels
        this.levels = {
            DEBUG: 0,
            INFO: 1,
            WARNING: 2,
            ERROR: 3,
            CRITICAL: 4
        };
        
        // Start flush timer
        this.startFlushTimer();
        
        // Log on page unload
        window.addEventListener('beforeunload', () => this.flush());
    }
    
    setLogLevel(level) {
        if (this.levels.hasOwnProperty(level)) {
            this.logLevel = level;
        }
    }
    
    shouldLog(level) {
        return this.levels[level] >= this.levels[this.logLevel];
    }
    
    formatMessage(level, component, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            component,
            message,
            data,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        // Also log to console for immediate feedback
        const consoleMsg = `[${timestamp}] [${level}] [${component}] ${message}`;
        if (data) {
            console.log(consoleMsg, data);
        } else {
            console.log(consoleMsg);
        }
        
        return logEntry;
    }
    
    async sendToBackend(logs) {
        try {
            if (window.eel && window.eel.log_frontend_activity) {
                await window.eel.log_frontend_activity(logs)();
            }
        } catch (error) {
            console.error('Failed to send logs to backend:', error);
        }
    }
    
    addToBuffer(logEntry) {
        this.buffer.push(logEntry);
        
        // Flush if buffer is full
        if (this.buffer.length >= this.bufferSize) {
            this.flush();
        }
    }
    
    flush() {
        if (this.buffer.length === 0) return;
        
        const logs = [...this.buffer];
        this.buffer = [];
        this.sendToBackend(logs);
    }
    
    startFlushTimer() {
        setInterval(() => this.flush(), this.flushInterval);
    }
    
    // Main logging methods
    debug(component, message, data = null) {
        if (!this.shouldLog('DEBUG')) return;
        const logEntry = this.formatMessage('DEBUG', component, message, data);
        this.addToBuffer(logEntry);
    }
    
    info(component, message, data = null) {
        if (!this.shouldLog('INFO')) return;
        const logEntry = this.formatMessage('INFO', component, message, data);
        this.addToBuffer(logEntry);
    }
    
    warning(component, message, data = null) {
        if (!this.shouldLog('WARNING')) return;
        const logEntry = this.formatMessage('WARNING', component, message, data);
        this.addToBuffer(logEntry);
    }
    
    error(component, message, data = null) {
        if (!this.shouldLog('ERROR')) return;
        const logEntry = this.formatMessage('ERROR', component, message, data);
        this.addToBuffer(logEntry);
        // Flush errors immediately
        this.flush();
    }
    
    critical(component, message, data = null) {
        if (!this.shouldLog('CRITICAL')) return;
        const logEntry = this.formatMessage('CRITICAL', component, message, data);
        this.addToBuffer(logEntry);
        // Flush critical errors immediately
        this.flush();
    }
    
    // Template-specific logging
    logTemplateAction(action, templateId, data = null) {
        const message = `Template action: ${action} for template ID: ${templateId}`;
        this.info('TemplateManager', message, data);
    }
    
    logApiCall(method, endpoint, data = null, response = null) {
        const message = `API Call: ${method} ${endpoint}`;
        const logData = {
            request: data,
            response: response
        };
        this.debug('API', message, logData);
    }
    
    logUserInteraction(element, action, data = null) {
        const message = `User interaction: ${action} on ${element}`;
        this.debug('UI', message, data);
    }
    
    // Performance logging
    logPerformance(operation, duration, details = null) {
        const message = `Performance: ${operation} took ${duration}ms`;
        this.info('Performance', message, details);
    }
    
    // Error tracking
    logError(error, component = 'Unknown', context = null) {
        const errorData = {
            message: error.message,
            stack: error.stack,
            context: context
        };
        this.error(component, `JavaScript Error: ${error.message}`, errorData);
    }
}

// Create singleton instance
window.logger = new FrontendLogger();

// Override console.error to capture all errors
const originalConsoleError = console.error;
console.error = function(...args) {
    originalConsoleError.apply(console, args);
    window.logger.error('Console', 'Console error', { args });
};

// Capture unhandled errors
window.addEventListener('error', (event) => {
    window.logger.logError(event.error, 'Window', {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
    });
});

// Capture unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    window.logger.error('Promise', 'Unhandled promise rejection', {
        reason: event.reason,
        promise: event.promise
    });
});

console.log('Frontend logger initialized');