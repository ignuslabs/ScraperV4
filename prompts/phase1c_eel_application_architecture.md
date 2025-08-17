# Phase 1C: Eel Application Architecture - Web Interface Foundation

## Objective
Build a complete Eel-based web interface architecture for ScraperV4 with real-time communication between Python backend and JavaScript frontend. Create a responsive, modern web UI that seamlessly integrates with the service container architecture and provides real-time scraping progress updates.

## Context
Building upon the project structure from Phase 1B, this phase creates the web interface layer:
- **Eel Integration**: Python-JavaScript bridge with exposed API functions
- **Real-time Updates**: WebSocket-based progress monitoring and notifications
- **Modern UI Components**: Responsive interface with component-based architecture
- **API Routes**: RESTful endpoints for scraping operations and data management
- **Frontend Build System**: Asset compilation and optimization
- **State Management**: Client-side state synchronization with backend services

## Architecture Overview
```
web/
├── index.html              # Main application entry point
├── static/
│   ├── css/
│   │   ├── main.css       # Main stylesheet
│   │   └── components/    # Component-specific styles
│   ├── js/
│   │   ├── app.js         # Main application logic
│   │   ├── api.js         # Eel API communication
│   │   ├── components/    # UI components
│   │   └── utils/         # JavaScript utilities
│   └── images/            # Static images and icons
├── templates/             # HTML templates (if using templating)
└── components/            # Reusable UI components
```

## Implementation Steps

### 1. Main HTML Structure

Create `web/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScraperV4 - Professional Web Scraping</title>
    
    <!-- CSS -->
    <link rel="stylesheet" href="static/css/main.css">
    <link rel="stylesheet" href="static/css/components/scraping-form.css">
    <link rel="stylesheet" href="static/css/components/results-table.css">
    <link rel="stylesheet" href="static/css/components/progress-monitor.css">
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div id="app">
        <!-- Header -->
        <header class="app-header">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-spider"></i>
                    <h1>ScraperV4</h1>
                </div>
                <nav class="nav-menu">
                    <button class="nav-btn active" data-page="scraping">
                        <i class="fas fa-search"></i>
                        Scraping
                    </button>
                    <button class="nav-btn" data-page="templates">
                        <i class="fas fa-file-code"></i>
                        Templates
                    </button>
                    <button class="nav-btn" data-page="results">
                        <i class="fas fa-table"></i>
                        Results
                    </button>
                    <button class="nav-btn" data-page="settings">
                        <i class="fas fa-cog"></i>
                        Settings
                    </button>
                </nav>
            </div>
        </header>

        <!-- Main Content -->
        <main class="app-main">
            <!-- Scraping Page -->
            <div id="scraping-page" class="page active">
                <div class="page-header">
                    <h2>New Scraping Job</h2>
                    <button id="quick-start-btn" class="btn btn-secondary">
                        <i class="fas fa-bolt"></i>
                        Quick Start
                    </button>
                </div>
                
                <div class="content-grid">
                    <div class="form-section">
                        <form id="scraping-form" class="scraping-form">
                            <div class="form-group">
                                <label for="job-name">Job Name</label>
                                <input type="text" id="job-name" name="jobName" required 
                                       placeholder="Enter a descriptive name">
                            </div>
                            
                            <div class="form-group">
                                <label for="target-url">Target URL</label>
                                <input type="url" id="target-url" name="targetUrl" required 
                                       placeholder="https://example.com">
                            </div>
                            
                            <div class="form-group">
                                <label for="template-select">Scraping Template</label>
                                <select id="template-select" name="templateId" required>
                                    <option value="">Select a template...</option>
                                </select>
                                <button type="button" id="create-template-btn" class="btn btn-link">
                                    Create New Template
                                </button>
                            </div>
                            
                            <div class="form-group">
                                <label>Advanced Options</label>
                                <div class="checkbox-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="stealth-mode" name="stealthMode" checked>
                                        <span class="checkmark"></span>
                                        Enable Stealth Mode
                                    </label>
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="auto-retry" name="autoRetry" checked>
                                        <span class="checkmark"></span>
                                        Auto Retry on Failure
                                    </label>
                                </div>
                            </div>
                            
                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary" id="start-scraping-btn">
                                    <i class="fas fa-play"></i>
                                    Start Scraping
                                </button>
                                <button type="button" class="btn btn-secondary" id="preview-btn">
                                    <i class="fas fa-eye"></i>
                                    Preview
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    <div class="monitor-section">
                        <div id="progress-monitor" class="progress-monitor">
                            <h3>Progress Monitor</h3>
                            <div class="monitor-content">
                                <div class="status-display">
                                    <span class="status-indicator idle"></span>
                                    <span class="status-text">Ready to start</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: 0%"></div>
                                    </div>
                                    <span class="progress-text">0%</span>
                                </div>
                                <div class="stats-grid">
                                    <div class="stat-item">
                                        <span class="stat-label">Items Scraped</span>
                                        <span class="stat-value" id="items-scraped">0</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Success Rate</span>
                                        <span class="stat-value" id="success-rate">0%</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Elapsed Time</span>
                                        <span class="stat-value" id="elapsed-time">00:00</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="live-logs" class="live-logs">
                            <h3>Live Logs</h3>
                            <div class="logs-content">
                                <div class="log-entry">
                                    <span class="log-time">Ready</span>
                                    <span class="log-message">ScraperV4 initialized and ready</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Templates Page -->
            <div id="templates-page" class="page">
                <div class="page-header">
                    <h2>Scraping Templates</h2>
                    <button id="new-template-btn" class="btn btn-primary">
                        <i class="fas fa-plus"></i>
                        New Template
                    </button>
                </div>
                <div id="templates-grid" class="templates-grid">
                    <!-- Templates will be populated dynamically -->
                </div>
            </div>

            <!-- Results Page -->
            <div id="results-page" class="page">
                <div class="page-header">
                    <h2>Scraping Results</h2>
                    <div class="page-actions">
                        <button id="export-results-btn" class="btn btn-secondary">
                            <i class="fas fa-download"></i>
                            Export
                        </button>
                        <button id="clear-results-btn" class="btn btn-danger">
                            <i class="fas fa-trash"></i>
                            Clear All
                        </button>
                    </div>
                </div>
                <div id="results-table-container" class="results-table-container">
                    <!-- Results table will be populated dynamically -->
                </div>
            </div>

            <!-- Settings Page -->
            <div id="settings-page" class="page">
                <div class="page-header">
                    <h2>Settings</h2>
                </div>
                <div class="settings-content">
                    <!-- Settings form will be populated dynamically -->
                </div>
            </div>
        </main>

        <!-- Notifications -->
        <div id="notifications-container" class="notifications-container">
            <!-- Notifications will be populated dynamically -->
        </div>

        <!-- Modals -->
        <div id="modal-overlay" class="modal-overlay">
            <div id="modal-content" class="modal-content">
                <!-- Modal content will be populated dynamically -->
            </div>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="/eel.js"></script>
    <script src="static/js/utils/helpers.js"></script>
    <script src="static/js/utils/notifications.js"></script>
    <script src="static/js/api.js"></script>
    <script src="static/js/components/scraping-form.js"></script>
    <script src="static/js/components/progress-monitor.js"></script>
    <script src="static/js/components/results-table.js"></script>
    <script src="static/js/components/template-manager.js"></script>
    <script src="static/js/app.js"></script>
</body>
</html>
```

### 2. Main CSS Styling

Create `web/static/css/main.css`:
```css
/* Main CSS for ScraperV4 */

:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --background-color: #f8fafc;
    --surface-color: #ffffff;
    --border-color: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.6;
}

/* Layout */
#app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.app-header {
    background: var(--surface-color);
    border-bottom: 1px solid var(--border-color);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 4rem;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 700;
    color: var(--primary-color);
}

.logo i {
    font-size: 1.5rem;
}

.logo h1 {
    font-size: 1.5rem;
    font-weight: 700;
}

.nav-menu {
    display: flex;
    gap: 0.5rem;
}

.nav-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}

.nav-btn:hover {
    background: var(--background-color);
    color: var(--text-primary);
}

.nav-btn.active {
    background: var(--primary-color);
    color: white;
}

.app-main {
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
    width: 100%;
}

/* Pages */
.page {
    display: none;
}

.page.active {
    display: block;
}

.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
}

.page-header h2 {
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--text-primary);
}

.page-actions {
    display: flex;
    gap: 0.75rem;
}

/* Content Grid */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 400px;
    gap: 2rem;
}

@media (max-width: 1024px) {
    .content-grid {
        grid-template-columns: 1fr;
    }
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    border: none;
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-hover);
}

.btn-secondary {
    background: var(--surface-color);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background: var(--background-color);
}

.btn-danger {
    background: var(--error-color);
    color: white;
}

.btn-danger:hover {
    background: #dc2626;
}

.btn-link {
    background: transparent;
    color: var(--primary-color);
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
}

.btn-link:hover {
    background: var(--background-color);
}

/* Form Elements */
.form-section {
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group:last-child {
    margin-bottom: 0;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-primary);
}

input[type="text"],
input[type="url"],
input[type="email"],
input[type="password"],
input[type="number"],
select,
textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--surface-color);
    color: var(--text-primary);
    font-size: 0.875rem;
    transition: border-color 0.2s;
}

input:focus,
select:focus,
textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-weight: 400;
}

.checkbox-label input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.form-actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color);
}

/* Monitor Section */
.monitor-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.progress-monitor,
.live-logs {
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

.progress-monitor h3,
.live-logs h3 {
    margin-bottom: 1rem;
    font-size: 1.125rem;
    font-weight: 600;
}

/* Notifications */
.notifications-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.notification {
    background: var(--surface-color);
    border-radius: var(--radius-md);
    padding: 1rem;
    box-shadow: var(--shadow-lg);
    border-left: 4px solid var(--primary-color);
    max-width: 400px;
    animation: slideIn 0.3s ease-out;
}

.notification.success {
    border-left-color: var(--success-color);
}

.notification.error {
    border-left-color: var(--error-color);
}

.notification.warning {
    border-left-color: var(--warning-color);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-overlay.active {
    display: flex;
}

.modal-content {
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    padding: 2rem;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: var(--shadow-lg);
}

/* Utility Classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.text-sm { font-size: 0.875rem; }
.text-xs { font-size: 0.75rem; }
.text-primary { color: var(--primary-color); }
.text-success { color: var(--success-color); }
.text-error { color: var(--error-color); }
.text-warning { color: var(--warning-color); }
.text-muted { color: var(--text-muted); }
.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mt-2 { margin-top: 1rem; }
.hidden { display: none; }
.loading { opacity: 0.6; pointer-events: none; }
```

### 3. JavaScript API Communication Layer

Create `web/static/js/api.js`:
```javascript
/**
 * API communication layer for ScraperV4
 * Handles all communication between frontend and Python backend via Eel
 */

class ScraperAPI {
    constructor() {
        this.isConnected = false;
        this.eventHandlers = new Map();
        this.init();
    }

    async init() {
        try {
            // Test connection to backend
            await this.ping();
            this.isConnected = true;
            console.log('✅ Connected to ScraperV4 backend');
        } catch (error) {
            console.error('❌ Failed to connect to backend:', error);
            this.showConnectionError();
        }
    }

    // Connection Management
    async ping() {
        return await eel.ping()();
    }

    // Scraping Operations
    async startScrapingJob(jobData) {
        try {
            const response = await eel.start_scraping_job(jobData)();
            this.emit('job_started', response);
            return response;
        } catch (error) {
            console.error('Failed to start scraping job:', error);
            throw error;
        }
    }

    async stopScrapingJob(jobId) {
        try {
            const response = await eel.stop_scraping_job(jobId)();
            this.emit('job_stopped', response);
            return response;
        } catch (error) {
            console.error('Failed to stop scraping job:', error);
            throw error;
        }
    }

    async getJobStatus(jobId) {
        try {
            return await eel.get_job_status(jobId)();
        } catch (error) {
            console.error('Failed to get job status:', error);
            throw error;
        }
    }

    async getJobResults(jobId, limit = 100, offset = 0) {
        try {
            return await eel.get_job_results(jobId, limit, offset)();
        } catch (error) {
            console.error('Failed to get job results:', error);
            throw error;
        }
    }

    // Template Management
    async getTemplates() {
        try {
            return await eel.get_templates()();
        } catch (error) {
            console.error('Failed to get templates:', error);
            throw error;
        }
    }

    async getTemplate(templateId) {
        try {
            return await eel.get_template(templateId)();
        } catch (error) {
            console.error('Failed to get template:', error);
            throw error;
        }
    }

    async createTemplate(templateData) {
        try {
            const response = await eel.create_template(templateData)();
            this.emit('template_created', response);
            return response;
        } catch (error) {
            console.error('Failed to create template:', error);
            throw error;
        }
    }

    async updateTemplate(templateId, templateData) {
        try {
            const response = await eel.update_template(templateId, templateData)();
            this.emit('template_updated', response);
            return response;
        } catch (error) {
            console.error('Failed to update template:', error);
            throw error;
        }
    }

    async deleteTemplate(templateId) {
        try {
            const response = await eel.delete_template(templateId)();
            this.emit('template_deleted', response);
            return response;
        } catch (error) {
            console.error('Failed to delete template:', error);
            throw error;
        }
    }

    // Data Export
    async exportResults(jobId, format = 'csv') {
        try {
            return await eel.export_results(jobId, format)();
        } catch (error) {
            console.error('Failed to export results:', error);
            throw error;
        }
    }

    // Settings
    async getSettings() {
        try {
            return await eel.get_settings()();
        } catch (error) {
            console.error('Failed to get settings:', error);
            throw error;
        }
    }

    async updateSettings(settings) {
        try {
            const response = await eel.update_settings(settings)();
            this.emit('settings_updated', response);
            return response;
        } catch (error) {
            console.error('Failed to update settings:', error);
            throw error;
        }
    }

    // URL Preview
    async previewUrl(url, templateId) {
        try {
            return await eel.preview_url(url, templateId)();
        } catch (error) {
            console.error('Failed to preview URL:', error);
            throw error;
        }
    }

    // Event System
    on(eventName, handler) {
        if (!this.eventHandlers.has(eventName)) {
            this.eventHandlers.set(eventName, []);
        }
        this.eventHandlers.get(eventName).push(handler);
    }

    off(eventName, handler) {
        if (this.eventHandlers.has(eventName)) {
            const handlers = this.eventHandlers.get(eventName);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(eventName, data) {
        if (this.eventHandlers.has(eventName)) {
            this.eventHandlers.get(eventName).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${eventName}:`, error);
                }
            });
        }
    }

    // Error Handling
    showConnectionError() {
        const notification = {
            type: 'error',
            title: 'Connection Error',
            message: 'Failed to connect to ScraperV4 backend. Please ensure the application is running.',
            duration: 0 // Persistent
        };
        
        if (window.notifications) {
            window.notifications.show(notification);
        }
    }

    // Utility Methods
    async validateUrl(url) {
        try {
            return await eel.validate_url(url)();
        } catch (error) {
            console.error('Failed to validate URL:', error);
            return { valid: false, error: error.message };
        }
    }

    async testSelector(url, selector) {
        try {
            return await eel.test_selector(url, selector)();
        } catch (error) {
            console.error('Failed to test selector:', error);
            throw error;
        }
    }
}

// Global API instance
window.api = new ScraperAPI();
```

### 4. Backend API Routes Implementation

Create `src/web/api_routes.py`:
```python
"""API routes for Eel web interface."""

import eel
import asyncio
from typing import Dict, Any, List, Optional
from src.core.container import container
from src.services.scraping_service import ScrapingService
from src.services.template_service import TemplateService
from src.services.data_service import DataService
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def register_api_routes():
    """Register all API routes with Eel."""
    
    @eel.expose
    def ping():
        """Health check endpoint."""
        return {"status": "ok", "message": "ScraperV4 backend is running"}
    
    # Scraping Job Endpoints
    @eel.expose
    def start_scraping_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new scraping job."""
        try:
            scraping_service = container.resolve(ScrapingService)
            job = scraping_service.create_job(
                name=job_data['jobName'],
                template_id=job_data['templateId'],
                target_url=job_data['targetUrl'],
                config=job_data.get('config', {}),
                parameters=job_data.get('parameters', {})
            )
            
            # Start job in background
            asyncio.create_task(scraping_service.execute_job_async(job.id))
            
            logger.info(f"Started scraping job: {job.id}")
            return {
                "success": True,
                "job_id": job.id,
                "message": "Scraping job started successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to start scraping job: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def stop_scraping_job(job_id: int) -> Dict[str, Any]:
        """Stop a running scraping job."""
        try:
            scraping_service = container.resolve(ScrapingService)
            success = scraping_service.stop_job(job_id)
            
            if success:
                logger.info(f"Stopped scraping job: {job_id}")
                return {
                    "success": True,
                    "message": "Scraping job stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Job not found or already stopped"
                }
                
        except Exception as e:
            logger.error(f"Failed to stop scraping job {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_job_status(job_id: int) -> Dict[str, Any]:
        """Get status of a scraping job."""
        try:
            scraping_service = container.resolve(ScrapingService)
            job = scraping_service.get_job(job_id)
            
            if not job:
                return {
                    "success": False,
                    "error": "Job not found"
                }
            
            return {
                "success": True,
                "job": {
                    "id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "progress": job.progress,
                    "items_scraped": job.items_scraped,
                    "items_failed": job.items_failed,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "duration": job.duration,
                    "error_message": job.error_message
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_job_results(job_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get results for a scraping job."""
        try:
            data_service = container.resolve(DataService)
            results = data_service.get_job_results(job_id, limit=limit, offset=offset)
            
            return {
                "success": True,
                "results": [
                    {
                        "id": result.id,
                        "source_url": result.source_url,
                        "data": result.data,
                        "scraped_at": result.scraped_at.isoformat(),
                        "status": result.status
                    }
                    for result in results
                ],
                "total": data_service.get_job_results_count(job_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to get job results {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Template Management Endpoints
    @eel.expose
    def get_templates() -> Dict[str, Any]:
        """Get all scraping templates."""
        try:
            template_service = container.resolve(TemplateService)
            templates = template_service.get_all_templates()
            
            return {
                "success": True,
                "templates": [
                    {
                        "id": template.id,
                        "name": template.name,
                        "description": template.description,
                        "version": template.version,
                        "usage_count": template.usage_count,
                        "success_rate": template.success_rate,
                        "created_at": template.created_at.isoformat()
                    }
                    for template in templates
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def get_template(template_id: int) -> Dict[str, Any]:
        """Get a specific template."""
        try:
            template_service = container.resolve(TemplateService)
            template = template_service.get_template(template_id)
            
            if not template:
                return {
                    "success": False,
                    "error": "Template not found"
                }
            
            return {
                "success": True,
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "selectors": template.selectors,
                    "validation_rules": template.validation_rules,
                    "post_processing": template.post_processing,
                    "adaptive_selectors": template.adaptive_selectors,
                    "fallback_selectors": template.fallback_selectors,
                    "version": template.version,
                    "usage_count": template.usage_count,
                    "success_rate": template.success_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def create_template(template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scraping template."""
        try:
            template_service = container.resolve(TemplateService)
            template = template_service.create_template(
                name=template_data['name'],
                description=template_data.get('description', ''),
                selectors=template_data['selectors'],
                validation_rules=template_data.get('validation_rules', {}),
                post_processing=template_data.get('post_processing', [])
            )
            
            logger.info(f"Created template: {template.name}")
            return {
                "success": True,
                "template_id": template.id,
                "message": "Template created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Data Export Endpoints
    @eel.expose
    def export_results(job_id: int, format: str = 'csv') -> Dict[str, Any]:
        """Export job results to file."""
        try:
            data_service = container.resolve(DataService)
            file_path = data_service.export_job_results(job_id, format)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "message": f"Results exported to {format.upper()} successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to export results {job_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # URL Preview and Validation
    @eel.expose
    def preview_url(url: str, template_id: int) -> Dict[str, Any]:
        """Preview URL scraping with template."""
        try:
            scraping_service = container.resolve(ScrapingService)
            preview_data = scraping_service.preview_scraping(url, template_id)
            
            return {
                "success": True,
                "preview": preview_data
            }
            
        except Exception as e:
            logger.error(f"Failed to preview URL {url}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @eel.expose
    def validate_url(url: str) -> Dict[str, Any]:
        """Validate URL accessibility."""
        try:
            from src.utils.validation_utils import validate_url
            result = validate_url(url)
            
            return {
                "success": True,
                "valid": result['valid'],
                "status_code": result.get('status_code'),
                "error": result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Failed to validate URL {url}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    logger.info("API routes registered successfully")
```

### 5. Main Application JavaScript

Create `web/static/js/app.js`:
```javascript
/**
 * Main application logic for ScraperV4
 */

class ScraperApp {
    constructor() {
        this.currentPage = 'scraping';
        this.activeJobs = new Map();
        this.init();
    }

    async init() {
        console.log('🚀 Initializing ScraperV4...');
        
        // Wait for API connection
        await this.waitForAPI();
        
        // Initialize components
        this.initNavigation();
        this.initComponents();
        this.loadInitialData();
        
        console.log('✅ ScraperV4 initialized successfully');
    }

    async waitForAPI() {
        let attempts = 0;
        const maxAttempts = 10;
        
        while (attempts < maxAttempts) {
            try {
                await window.api.ping();
                return;
            } catch (error) {
                attempts++;
                console.log(`Waiting for API connection... (${attempts}/${maxAttempts})`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        
        throw new Error('Failed to connect to backend API');
    }

    initNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.navigateToPage(page);
            });
        });
    }

    navigateToPage(pageName) {
        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
        
        // Show/hide pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(`${pageName}-page`).classList.add('active');
        
        this.currentPage = pageName;
        
        // Load page-specific data
        this.loadPageData(pageName);
    }

    async loadPageData(pageName) {
        switch (pageName) {
            case 'templates':
                await this.loadTemplatesData();
                break;
            case 'results':
                await this.loadResultsData();
                break;
            case 'settings':
                await this.loadSettingsData();
                break;
        }
    }

    initComponents() {
        // Initialize scraping form
        if (window.ScrapingForm) {
            this.scrapingForm = new ScrapingForm();
        }
        
        // Initialize progress monitor
        if (window.ProgressMonitor) {
            this.progressMonitor = new ProgressMonitor();
        }
        
        // Initialize results table
        if (window.ResultsTable) {
            this.resultsTable = new ResultsTable();
        }
        
        // Initialize template manager
        if (window.TemplateManager) {
            this.templateManager = new TemplateManager();
        }
        
        // Initialize notifications
        if (window.notifications) {
            window.notifications.init();
        }
    }

    async loadInitialData() {
        try {
            // Load templates for dropdown
            const templatesResponse = await window.api.getTemplates();
            if (templatesResponse.success) {
                this.populateTemplateDropdown(templatesResponse.templates);
            }
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            window.notifications?.show({
                type: 'error',
                title: 'Loading Error',
                message: 'Failed to load initial application data'
            });
        }
    }

    populateTemplateDropdown(templates) {
        const select = document.getElementById('template-select');
        if (!select) return;
        
        // Clear existing options (except first)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add template options
        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = `${template.name} (v${template.version})`;
            select.appendChild(option);
        });
    }

    async loadTemplatesData() {
        try {
            const response = await window.api.getTemplates();
            if (response.success && this.templateManager) {
                this.templateManager.renderTemplates(response.templates);
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
        }
    }

    async loadResultsData() {
        // Results will be loaded by ResultsTable component
        if (this.resultsTable) {
            await this.resultsTable.loadRecentResults();
        }
    }

    async loadSettingsData() {
        try {
            const response = await window.api.getSettings();
            if (response.success) {
                this.renderSettingsForm(response.settings);
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    renderSettingsForm(settings) {
        const container = document.querySelector('#settings-page .settings-content');
        if (!container) return;
        
        container.innerHTML = `
            <div class="form-section">
                <h3>Scraping Settings</h3>
                <form id="settings-form">
                    <div class="form-group">
                        <label for="default-delay">Default Delay (seconds)</label>
                        <input type="number" id="default-delay" 
                               value="${settings.default_delay || 2}" min="0" max="10" step="0.1">
                    </div>
                    
                    <div class="form-group">
                        <label for="max-retries">Max Retries</label>
                        <input type="number" id="max-retries" 
                               value="${settings.max_retries || 3}" min="0" max="10">
                    </div>
                    
                    <div class="form-group">
                        <label for="timeout">Request Timeout (seconds)</label>
                        <input type="number" id="timeout" 
                               value="${settings.timeout || 30}" min="5" max="120">
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="stealth-mode" 
                                   ${settings.stealth_mode ? 'checked' : ''}>
                            Enable Stealth Mode by Default
                        </label>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Save Settings</button>
                        <button type="button" class="btn btn-secondary" id="reset-settings">Reset to Defaults</button>
                    </div>
                </form>
            </div>
        `;
        
        // Add form event listener
        document.getElementById('settings-form').addEventListener('submit', this.handleSettingsSubmit.bind(this));
    }

    async handleSettingsSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const settings = {
            default_delay: parseFloat(formData.get('default-delay')),
            max_retries: parseInt(formData.get('max-retries')),
            timeout: parseInt(formData.get('timeout')),
            stealth_mode: formData.has('stealth-mode')
        };
        
        try {
            const response = await window.api.updateSettings(settings);
            if (response.success) {
                window.notifications?.show({
                    type: 'success',
                    title: 'Settings Saved',
                    message: 'Application settings have been updated successfully'
                });
            }
        } catch (error) {
            console.error('Failed to save settings:', error);
            window.notifications?.show({
                type: 'error',
                title: 'Save Failed',
                message: 'Failed to save settings. Please try again.'
            });
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.scraperApp = new ScraperApp();
});
```

## Validation Criteria

### Success Metrics
1. ✅ HTML structure renders correctly with all navigation and forms
2. ✅ CSS styling provides professional, responsive design
3. ✅ JavaScript API layer connects to Python backend via Eel
4. ✅ Navigation between pages works smoothly
5. ✅ Forms collect and validate user input properly
6. ✅ Real-time progress monitoring displays correctly
7. ✅ API endpoints respond with proper data structure
8. ✅ Error handling displays user-friendly messages
9. ✅ Notifications system shows status updates
10. ✅ Application state management works consistently

### Validation Commands
```bash
# Start the application
python src/main.py

# Test in browser
open http://localhost:8080

# Verify Eel integration
python -c "import eel; print('Eel imported successfully')"

# Check web assets
ls web/index.html web/static/css/main.css web/static/js/app.js
```

### Browser Testing Checklist
- [ ] Page loads without JavaScript errors
- [ ] Navigation buttons switch between pages
- [ ] Forms validate input correctly
- [ ] API calls return expected responses
- [ ] Progress monitor updates in real-time
- [ ] Notifications appear and dismiss properly
- [ ] Responsive design works on different screen sizes
- [ ] Console shows no critical errors

## Troubleshooting Guide

### Eel Connection Issues
```bash
# Check if Eel is properly initialized
python -c "import eel; eel.init('web'); print('Eel initialized')"

# Verify web folder structure
ls -la web/static/js/
ls -la web/static/css/
```

### JavaScript Errors
- Check browser console for errors
- Verify all script files are loaded in correct order
- Ensure `/eel.js` is accessible (auto-generated by Eel)

### Styling Issues
- Verify CSS files are linked correctly in HTML
- Check for CSS syntax errors
- Test responsive design at different breakpoints

### API Communication Problems
- Verify backend services are registered in container
- Check Python function decorators (`@eel.expose`)
- Ensure proper error handling in both frontend and backend

## Next Steps
After successful completion:
1. Proceed to **Phase 2: Core Backend Development** to implement business logic
2. Web interface foundation is ready for integration with services
3. API routes are prepared for scraping operations
4. Real-time communication layer is established

## File Deliverables
- `web/index.html` - Main application interface
- `web/static/css/main.css` - Core styling system
- `web/static/js/app.js` - Main application logic
- `web/static/js/api.js` - API communication layer
- `src/web/api_routes.py` - Backend API endpoints
- Component CSS files for modular styling
- JavaScript component files for UI interactions