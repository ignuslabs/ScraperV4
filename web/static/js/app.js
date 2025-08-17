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
            // Make it globally accessible for other components
            window.templateManager = this.templateManager;
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
            console.log('Loading templates data...');
            console.log('window.api exists:', !!window.api);
            console.log('templateManager exists:', !!this.templateManager);
            
            if (!window.api) {
                throw new Error('API not initialized');
            }
            
            const response = await window.api.getTemplates();
            console.log('Templates response:', response);
            
            if (response.success && this.templateManager) {
                this.templateManager.renderTemplates(response.templates);
            } else if (!response.success) {
                console.error('Failed to get templates:', response.error);
                if (this.templateManager) {
                    this.templateManager.renderErrorState(response.error || 'Failed to load templates');
                }
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
            if (this.templateManager) {
                this.templateManager.renderErrorState(error.message);
            }
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
                        <label class="checkbox-label">
                            <input type="checkbox" id="stealth-mode" 
                                   ${settings.stealth_mode ? 'checked' : ''}>
                            <span class="checkmark"></span>
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
        document.getElementById('reset-settings').addEventListener('click', this.handleSettingsReset.bind(this));
    }

    async handleSettingsSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const settings = {
            default_delay: parseFloat(form.querySelector('#default-delay').value),
            max_retries: parseInt(form.querySelector('#max-retries').value),
            timeout: parseInt(form.querySelector('#timeout').value),
            stealth_mode: form.querySelector('#stealth-mode').checked
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

    async handleSettingsReset() {
        const defaultSettings = {
            default_delay: 2,
            max_retries: 3,
            timeout: 30,
            stealth_mode: true
        };
        
        try {
            const response = await window.api.updateSettings(defaultSettings);
            if (response.success) {
                this.renderSettingsForm(defaultSettings);
                window.notifications?.show({
                    type: 'success',
                    title: 'Settings Reset',
                    message: 'Settings have been reset to defaults'
                });
            }
        } catch (error) {
            console.error('Failed to reset settings:', error);
            window.notifications?.show({
                type: 'error',
                title: 'Reset Failed',
                message: 'Failed to reset settings. Please try again.'
            });
        }
    }

    // Job Management
    async startJob(jobData) {
        try {
            const response = await window.api.startScrapingJob(jobData);
            if (response.success) {
                this.activeJobs.set(response.job_id, jobData);
                
                // Start monitoring job progress
                this.monitorJob(response.job_id);
                
                window.notifications?.show({
                    type: 'success',
                    title: 'Job Started',
                    message: `Scraping job "${jobData.jobName}" started successfully`
                });
                
                return response;
            }
        } catch (error) {
            console.error('Failed to start job:', error);
            window.notifications?.show({
                type: 'error',
                title: 'Job Failed',
                message: 'Failed to start scraping job. Please try again.'
            });
            throw error;
        }
    }

    async monitorJob(jobId) {
        const interval = setInterval(async () => {
            try {
                const response = await window.api.getJobStatus(jobId);
                if (response.success) {
                    const job = response.job;
                    
                    // Update progress monitor if it exists
                    if (this.progressMonitor) {
                        this.progressMonitor.updateProgress(job);
                    }
                    
                    // Check if job is complete
                    if (job.status === 'completed' || job.status === 'failed') {
                        clearInterval(interval);
                        this.activeJobs.delete(jobId);
                        
                        window.notifications?.show({
                            type: job.status === 'completed' ? 'success' : 'error',
                            title: job.status === 'completed' ? 'Job Completed' : 'Job Failed',
                            message: job.status === 'completed' 
                                ? `Successfully scraped ${job.items_scraped} items`
                                : job.error_message || 'Job failed with unknown error'
                        });
                    }
                }
            } catch (error) {
                console.error('Failed to get job status:', error);
                clearInterval(interval);
            }
        }, 2000); // Poll every 2 seconds
    }

    // Modal Management
    showModal(title, content) {
        const modalOverlay = document.getElementById('modal-overlay');
        const modalContent = document.getElementById('modal-content');
        
        modalContent.innerHTML = `
            <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
                <button class="modal-close" onclick="window.scraperApp.hideModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
        `;
        
        modalOverlay.classList.add('active');
    }

    hideModal() {
        const modalOverlay = document.getElementById('modal-overlay');
        modalOverlay.classList.remove('active');
    }

    // Quick Start functionality
    initQuickStart() {
        const quickStartBtn = document.getElementById('quick-start-btn');
        if (quickStartBtn) {
            quickStartBtn.addEventListener('click', this.showQuickStartModal.bind(this));
        }
    }

    showQuickStartModal() {
        const content = `
            <div class="quick-start-content">
                <p>Quick Start will automatically detect the page structure and create a basic scraping template.</p>
                <div class="form-group">
                    <label for="quick-url">URL to Analyze</label>
                    <input type="url" id="quick-url" placeholder="https://example.com" required>
                </div>
                <div class="form-actions">
                    <button class="btn btn-primary" onclick="window.scraperApp.runQuickStart()">
                        <i class="fas fa-magic"></i>
                        Analyze Page
                    </button>
                    <button class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Cancel
                    </button>
                </div>
            </div>
        `;
        
        this.showModal('Quick Start', content);
    }

    async runQuickStart() {
        const urlInput = document.getElementById('quick-url');
        const url = urlInput.value.trim();
        
        if (!url) {
            window.notifications?.show({
                type: 'warning',
                title: 'URL Required',
                message: 'Please enter a URL to analyze'
            });
            return;
        }
        
        try {
            // This would call a backend function to analyze the page
            window.notifications?.show({
                type: 'info',
                title: 'Analyzing Page',
                message: 'Analyzing page structure, please wait...'
            });
            
            this.hideModal();
            
            // For now, just fill in basic form data
            document.getElementById('target-url').value = url;
            document.getElementById('job-name').value = `Quick Job - ${new Date().toLocaleString()}`;
            
        } catch (error) {
            console.error('Quick start failed:', error);
            window.notifications?.show({
                type: 'error',
                title: 'Analysis Failed',
                message: 'Failed to analyze page. Please try again.'
            });
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.scraperApp = new ScraperApp();
});