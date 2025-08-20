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

    // Playwright Interactive Mode Methods
    async startPlaywrightInteractive(url, options = {}) {
        try {
            return await eel.start_playwright_interactive(url, options)();
        } catch (error) {
            console.error('Failed to start Playwright interactive mode:', error);
            throw error;
        }
    }

    async getBrowserScreenshot(sessionId, fullPage = false) {
        try {
            return await eel.get_browser_screenshot(sessionId, fullPage)();
        } catch (error) {
            console.error('Failed to get screenshot:', error);
            throw error;
        }
    }

    async startElementSelection(sessionId) {
        try {
            return await eel.start_element_selection(sessionId)();
        } catch (error) {
            console.error('Failed to start element selection:', error);
            throw error;
        }
    }

    async stopElementSelection(sessionId) {
        try {
            return await eel.stop_element_selection(sessionId)();
        } catch (error) {
            console.error('Failed to stop element selection:', error);
            throw error;
        }
    }

    async selectElementAtCoordinates(sessionId, x, y) {
        try {
            return await eel.select_element_at_coordinates(sessionId, x, y)();
        } catch (error) {
            console.error('Failed to select element:', error);
            throw error;
        }
    }

    async getSelectedElements(sessionId) {
        try {
            return await eel.get_selected_elements(sessionId)();
        } catch (error) {
            console.error('Failed to get selected elements:', error);
            throw error;
        }
    }

    async closePlaywrightSession(sessionId) {
        try {
            return await eel.close_playwright_session(sessionId)();
        } catch (error) {
            console.error('Failed to close session:', error);
            throw error;
        }
    }

    // Note: Additional methods like navigateToUrl, clickElement, fillFormField, 
    // and savePlaywrightTemplate can be added when backend endpoints are implemented

    async getPageInfo(sessionId) {
        try {
            return await eel.get_page_info(sessionId)();
        } catch (error) {
            console.error('Failed to get page info:', error);
            throw error;
        }
    }

    async closeInteractiveSession(sessionId) {
        try {
            return await eel.close_interactive_session(sessionId)();
        } catch (error) {
            console.error('Failed to close interactive session:', error);
            throw error;
        }
    }

    async getActiveInteractiveSessions() {
        try {
            return await eel.get_active_interactive_sessions()();
        } catch (error) {
            console.error('Failed to get active sessions:', error);
            throw error;
        }
    }

    async createTemplateFromSelections(sessionId, templateName, templateDescription = "") {
        try {
            return await eel.create_template_from_selections(sessionId, templateName, templateDescription)();
        } catch (error) {
            console.error('Failed to create template from selections:', error);
            throw error;
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