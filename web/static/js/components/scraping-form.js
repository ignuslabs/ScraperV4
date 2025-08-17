/**
 * Scraping Form Component
 * Handles the main scraping job form functionality
 */

class ScrapingForm {
    constructor() {
        this.form = document.getElementById('scraping-form');
        this.isSubmitting = false;
        this.init();
    }

    init() {
        if (!this.form) {
            console.warn('Scraping form not found');
            return;
        }

        this.bindEvents();
        this.loadFormState();
        this.initializeValidation();
        
        console.log('Scraping form initialized');
    }

    bindEvents() {
        // Form submission
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // URL validation on blur
        const urlInput = this.form.querySelector('#target-url');
        if (urlInput) {
            urlInput.addEventListener('blur', this.validateUrl.bind(this));
            urlInput.addEventListener('input', this.onUrlInput.bind(this));
        }

        // Template selection
        const templateSelect = this.form.querySelector('#template-select');
        if (templateSelect) {
            templateSelect.addEventListener('change', this.onTemplateChange.bind(this));
        }

        // Create template button
        const createTemplateBtn = this.form.querySelector('#create-template-btn');
        if (createTemplateBtn) {
            createTemplateBtn.addEventListener('click', this.showCreateTemplateModal.bind(this));
        }

        // Preview button
        const previewBtn = this.form.querySelector('#preview-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', this.handlePreview.bind(this));
        }

        // Auto-save form state
        this.form.addEventListener('input', window.helpers.AsyncUtils.debounce(
            this.saveFormState.bind(this), 1000
        ));
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) {
            return;
        }

        // Validate form
        const validation = this.validateForm();
        if (!validation.isValid) {
            this.showValidationErrors(validation.errors);
            return;
        }

        this.isSubmitting = true;
        this.setSubmitState(true);

        try {
            const formData = this.getFormData();
            
            // Show loading notification
            const loadingId = window.notifications?.loading('Starting scraping job...');
            
            // Start the job via the main app
            const response = await window.scraperApp.startJob(formData);
            
            if (response.success) {
                // Dismiss loading and show success
                if (loadingId) window.notifications.dismiss(loadingId);
                
                // Clear form or reset to initial state
                this.onJobStarted(response);
                
                // Clear saved form state
                this.clearFormState();
                
            } else {
                throw new Error(response.error || 'Failed to start scraping job');
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            window.notifications?.error(
                'Submission Failed',
                error.message || 'Failed to start scraping job. Please try again.'
            );
        } finally {
            this.isSubmitting = false;
            this.setSubmitState(false);
        }
    }

    validateForm() {
        const errors = [];
        
        // Get form fields
        const jobName = this.form.querySelector('#job-name').value.trim();
        const targetUrl = this.form.querySelector('#target-url').value.trim();
        const templateId = this.form.querySelector('#template-select').value;

        // Validate job name
        if (!jobName) {
            errors.push({ field: 'job-name', message: 'Job name is required' });
        } else if (jobName.length < 3) {
            errors.push({ field: 'job-name', message: 'Job name must be at least 3 characters' });
        }

        // Validate URL
        if (!targetUrl) {
            errors.push({ field: 'target-url', message: 'Target URL is required' });
        } else if (!window.helpers.ValidationUtils.isValidUrl(targetUrl)) {
            errors.push({ field: 'target-url', message: 'Please enter a valid URL' });
        }

        // Validate template selection
        if (!templateId) {
            errors.push({ field: 'template-select', message: 'Please select a scraping template' });
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    showValidationErrors(errors) {
        // Clear previous error states
        this.clearValidationErrors();

        errors.forEach(error => {
            const field = this.form.querySelector(`#${error.field}`);
            if (field) {
                field.classList.add('error');
                
                // Add error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                errorDiv.textContent = error.message;
                field.parentNode.appendChild(errorDiv);
            }
        });

        // Show notification with first error
        if (errors.length > 0) {
            window.notifications?.warning(
                'Validation Error',
                errors[0].message
            );
        }
    }

    clearValidationErrors() {
        // Remove error classes
        this.form.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
        });

        // Remove error messages
        this.form.querySelectorAll('.field-error').forEach(error => {
            error.remove();
        });
    }

    async validateUrl() {
        const urlInput = this.form.querySelector('#target-url');
        const url = urlInput.value.trim();
        
        if (!url) return;

        // Clean URL format
        const cleanedUrl = window.helpers.StringUtils.cleanUrl(url);
        if (cleanedUrl !== url) {
            urlInput.value = cleanedUrl;
        }

        try {
            const response = await window.api.validateUrl(cleanedUrl);
            
            if (response.success && response.valid) {
                urlInput.classList.remove('error');
                urlInput.classList.add('success');
            } else {
                urlInput.classList.remove('success');
                urlInput.classList.add('error');
                
                const errorMsg = response.error || 'URL is not accessible';
                this.showFieldError(urlInput, errorMsg);
            }
            
        } catch (error) {
            console.error('URL validation error:', error);
            urlInput.classList.remove('success');
            urlInput.classList.add('warning');
        }
    }

    onUrlInput() {
        const urlInput = this.form.querySelector('#target-url');
        urlInput.classList.remove('error', 'success', 'warning');
        
        // Remove any existing error message
        const existingError = urlInput.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    showFieldError(field, message) {
        // Remove existing error
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // Add new error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    onTemplateChange() {
        const templateSelect = this.form.querySelector('#template-select');
        const templateId = templateSelect.value;
        
        if (templateId) {
            // Could load template preview or show template details
            this.loadTemplateDetails(templateId);
        }
    }

    async loadTemplateDetails(templateId) {
        try {
            const response = await window.api.getTemplate(parseInt(templateId));
            if (response.success) {
                const template = response.template;
                
                // Could show template info in a tooltip or details section
                console.log('Template loaded:', template.name);
                
                // Enable preview button since we have both URL and template
                const previewBtn = this.form.querySelector('#preview-btn');
                const urlInput = this.form.querySelector('#target-url');
                
                if (previewBtn && urlInput.value.trim()) {
                    previewBtn.disabled = false;
                }
            }
        } catch (error) {
            console.error('Failed to load template details:', error);
        }
    }

    async handlePreview() {
        const url = this.form.querySelector('#target-url').value.trim();
        const templateId = this.form.querySelector('#template-select').value;
        
        if (!url || !templateId) {
            window.notifications?.warning(
                'Preview Unavailable',
                'Please enter a URL and select a template to preview'
            );
            return;
        }

        try {
            const loadingId = window.notifications?.loading('Generating preview...');
            
            const response = await window.api.previewUrl(url, parseInt(templateId));
            
            if (loadingId) window.notifications.dismiss(loadingId);
            
            if (response.success) {
                this.showPreviewModal(response.preview);
            } else {
                throw new Error(response.error || 'Preview failed');
            }
            
        } catch (error) {
            console.error('Preview error:', error);
            window.notifications?.error(
                'Preview Failed',
                error.message || 'Failed to generate preview'
            );
        }
    }

    showPreviewModal(previewData) {
        const content = `
            <div class="preview-content">
                <h4>Preview Results</h4>
                <div class="preview-stats">
                    <div class="stat-item">
                        <span class="stat-label">Elements Found</span>
                        <span class="stat-value">${previewData.count || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate</span>
                        <span class="stat-value">${previewData.success_rate || '0%'}</span>
                    </div>
                </div>
                
                ${previewData.sample_data ? `
                    <div class="preview-sample">
                        <h5>Sample Data</h5>
                        <pre class="preview-code">${JSON.stringify(previewData.sample_data, null, 2)}</pre>
                    </div>
                ` : ''}
                
                <div class="preview-actions">
                    <button class="btn btn-primary" onclick="window.scraperApp.hideModal()">
                        Looks Good
                    </button>
                    <button class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        window.scraperApp.showModal('Scraping Preview', content);
    }

    showCreateTemplateModal() {
        // Use the template manager's modal which has fetcher configuration
        if (window.templateManager) {
            window.templateManager.showCreateTemplateModal();
        } else {
            // Fallback to basic modal if template manager not initialized
            const content = `
                <form id="create-template-form" class="create-template-form">
                    <div class="form-group">
                        <label for="new-template-name">Template Name</label>
                        <input type="text" id="new-template-name" required 
                               placeholder="Enter template name">
                    </div>
                    
                    <div class="form-group">
                        <label for="new-template-description">Description</label>
                        <textarea id="new-template-description" rows="3" 
                                  placeholder="Describe what this template scrapes"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Selectors</label>
                        <div id="selectors-container">
                            <div class="selector-row">
                                <input type="text" placeholder="Field name" class="selector-name">
                                <input type="text" placeholder="CSS selector" class="selector-value">
                                <button type="button" class="btn btn-danger btn-sm remove-selector">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <button type="button" class="btn btn-secondary btn-sm" id="add-selector">
                            <i class="fas fa-plus"></i> Add Selector
                        </button>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Create Template</button>
                        <button type="button" class="btn btn-secondary" onclick="window.scraperApp.hideModal()">Cancel</button>
                    </div>
                </form>
            `;
            
            window.scraperApp.showModal('Create New Template', content);
            
            // Bind template form events
            this.bindTemplateFormEvents();
        }
    }

    bindTemplateFormEvents() {
        const form = document.getElementById('create-template-form');
        if (!form) return;

        // Add selector button
        const addSelectorBtn = form.querySelector('#add-selector');
        addSelectorBtn.addEventListener('click', this.addSelectorRow.bind(this));

        // Form submission
        form.addEventListener('submit', this.handleTemplateSubmit.bind(this));

        // Remove selector buttons (using delegation)
        form.addEventListener('click', (e) => {
            if (e.target.closest('.remove-selector')) {
                const row = e.target.closest('.selector-row');
                row.remove();
            }
        });
    }

    addSelectorRow() {
        const container = document.getElementById('selectors-container');
        const row = document.createElement('div');
        row.className = 'selector-row';
        row.innerHTML = `
            <input type="text" placeholder="Field name" class="selector-name">
            <input type="text" placeholder="CSS selector" class="selector-value">
            <button type="button" class="btn btn-danger btn-sm remove-selector">
                <i class="fas fa-trash"></i>
            </button>
        `;
        container.appendChild(row);
    }

    async handleTemplateSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const name = form.querySelector('#new-template-name').value.trim();
        const description = form.querySelector('#new-template-description').value.trim();
        
        // Collect selectors
        const selectorRows = form.querySelectorAll('.selector-row');
        const selectors = {};
        
        selectorRows.forEach(row => {
            const nameInput = row.querySelector('.selector-name');
            const valueInput = row.querySelector('.selector-value');
            
            if (nameInput.value.trim() && valueInput.value.trim()) {
                selectors[nameInput.value.trim()] = valueInput.value.trim();
            }
        });

        if (Object.keys(selectors).length === 0) {
            window.notifications?.warning(
                'Invalid Template',
                'Please add at least one selector'
            );
            return;
        }

        try {
            const templateData = {
                name,
                description,
                selectors
            };
            
            const response = await window.api.createTemplate(templateData);
            
            if (response.success) {
                window.scraperApp.hideModal();
                
                window.notifications?.success(
                    'Template Created',
                    `Template "${name}" created successfully`
                );
                
                // Refresh template dropdown
                await window.scraperApp.loadInitialData();
                
                // Select the new template
                const templateSelect = this.form.querySelector('#template-select');
                templateSelect.value = response.template_id;
                
            } else {
                throw new Error(response.error || 'Failed to create template');
            }
            
        } catch (error) {
            console.error('Template creation error:', error);
            window.notifications?.error(
                'Creation Failed',
                error.message || 'Failed to create template'
            );
        }
    }

    getFormData() {
        return {
            jobName: this.form.querySelector('#job-name').value.trim(),
            targetUrl: this.form.querySelector('#target-url').value.trim(),
            templateId: parseInt(this.form.querySelector('#template-select').value),
            stealthMode: this.form.querySelector('#stealth-mode').checked,
            autoRetry: this.form.querySelector('#auto-retry').checked,
            parameters: {},
            config: {
                stealth_mode: this.form.querySelector('#stealth-mode').checked,
                auto_retry: this.form.querySelector('#auto-retry').checked
            }
        };
    }

    setSubmitState(isSubmitting) {
        const submitBtn = this.form.querySelector('#start-scraping-btn');
        const previewBtn = this.form.querySelector('#preview-btn');
        
        if (isSubmitting) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
            previewBtn.disabled = true;
            this.form.classList.add('loading');
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-play"></i> Start Scraping';
            previewBtn.disabled = false;
            this.form.classList.remove('loading');
        }
    }

    onJobStarted(response) {
        // Could reset form or keep values for similar jobs
        // For now, just show success state
        console.log('Job started:', response.job_id);
    }

    initializeValidation() {
        // Add CSS classes for validation states
        const style = document.createElement('style');
        style.textContent = `
            .form-group input.error,
            .form-group select.error {
                border-color: var(--error-color);
                box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
            }
            
            .form-group input.success {
                border-color: var(--success-color);
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }
            
            .form-group input.warning {
                border-color: var(--warning-color);
                box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
            }
            
            .field-error {
                color: var(--error-color);
                font-size: 0.75rem;
                margin-top: 0.25rem;
            }
            
            .selector-row {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 0.5rem;
                align-items: center;
            }
            
            .selector-row input {
                flex: 1;
            }
            
            .preview-content {
                max-height: 400px;
                overflow-y: auto;
            }
            
            .preview-code {
                background: var(--background-color);
                padding: 1rem;
                border-radius: var(--radius-md);
                font-size: 0.75rem;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .preview-stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
                margin: 1rem 0;
            }
        `;
        document.head.appendChild(style);
    }

    saveFormState() {
        const formData = this.getFormData();
        window.helpers.StorageUtils.setItem('scraperv4-form-state', formData);
    }

    loadFormState() {
        const savedState = window.helpers.StorageUtils.getItem('scraperv4-form-state');
        if (savedState) {
            // Only restore if form is empty
            const jobNameInput = this.form.querySelector('#job-name');
            if (!jobNameInput.value) {
                this.restoreFormState(savedState);
            }
        }
    }

    restoreFormState(state) {
        if (state.jobName) {
            this.form.querySelector('#job-name').value = state.jobName;
        }
        if (state.targetUrl) {
            this.form.querySelector('#target-url').value = state.targetUrl;
        }
        if (state.templateId) {
            this.form.querySelector('#template-select').value = state.templateId;
        }
        if (typeof state.stealthMode === 'boolean') {
            this.form.querySelector('#stealth-mode').checked = state.stealthMode;
        }
        if (typeof state.autoRetry === 'boolean') {
            this.form.querySelector('#auto-retry').checked = state.autoRetry;
        }
    }

    clearFormState() {
        window.helpers.StorageUtils.removeItem('scraperv4-form-state');
    }
}

// Make available globally
window.ScrapingForm = ScrapingForm;