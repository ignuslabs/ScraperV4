/**
 * Template Manager Component
 * Handles template creation, editing, and management
 */

class TemplateManager {
    constructor() {
        this.container = document.getElementById('templates-grid');
        this.templates = [];
        this.selectedTemplate = null;
        this.init();
    }

    init() {
        if (!this.container) {
            console.warn('Templates grid container not found');
            if (window.logger) {
                window.logger.warning('TemplateManager', 'Templates grid container not found');
            }
            return;
        }

        this.bindEvents();
        console.log('Template manager initialized');
        if (window.logger) {
            window.logger.info('TemplateManager', 'Template manager initialized');
        }
    }

    bindEvents() {
        // New template button
        const newTemplateBtn = document.getElementById('new-template-btn');
        if (newTemplateBtn) {
            newTemplateBtn.addEventListener('click', this.showCreateTemplateModal.bind(this));
        }
        
        // Interactive mode button
        const interactiveBtn = document.getElementById('interactive-mode-btn');
        if (interactiveBtn) {
            interactiveBtn.addEventListener('click', this.startInteractiveMode.bind(this));
        } else {
            // Create the button if it doesn't exist
            this.createInteractiveModeButton();
        }
    }

    /**
     * Render templates in the grid
     */
    renderTemplates(templates) {
        this.templates = templates || [];
        
        if (window.logger) {
            window.logger.info('TemplateManager', 'Rendering templates', { count: this.templates.length });
        }
        
        if (!templates || templates.length === 0) {
            this.renderEmptyState();
            return;
        }

        const templatesHTML = templates.map(template => this.renderTemplateCard(template)).join('');
        this.container.innerHTML = templatesHTML;
        
        if (window.logger) {
            window.logger.debug('TemplateManager', 'Templates HTML added to DOM');
        }
        
        this.bindTemplateEvents();
    }

    renderTemplateCard(template) {
        const usageColor = template.usage_count > 10 ? 'success' : 
                          template.usage_count > 5 ? 'warning' : 'muted';
        
        const successRateColor = template.success_rate > 80 ? 'success' : 
                                template.success_rate > 60 ? 'warning' : 'error';

        return `
            <div class="template-card" data-id="${template.id}">
                <div class="template-header">
                    <div class="template-info">
                        <h3 class="template-name">${template.name}</h3>
                        <span class="template-version">v${template.version}</span>
                    </div>
                    <div class="template-menu">
                        <button class="btn btn-xs btn-secondary template-menu-btn" data-template-id="${template.id}">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <div class="template-dropdown" id="dropdown-${template.id}">
                            <button class="dropdown-item test-template" data-template-id="${template.id}">
                                <i class="fas fa-vial"></i> Test Template
                            </button>
                            <button class="dropdown-item edit-template" data-template-id="${template.id}">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="dropdown-item duplicate-template" data-template-id="${template.id}">
                                <i class="fas fa-copy"></i> Duplicate
                            </button>
                            <button class="dropdown-item export-template" data-template-id="${template.id}">
                                <i class="fas fa-download"></i> Export
                            </button>
                            <hr class="dropdown-divider">
                            <button class="dropdown-item delete-template text-error" data-template-id="${template.id}">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="template-description">
                    ${template.description || 'No description provided'}
                </div>
                
                <div class="template-stats">
                    <div class="stat-item">
                        <span class="stat-label">Usage</span>
                        <span class="stat-value text-${usageColor}">${template.usage_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate</span>
                        <span class="stat-value text-${successRateColor}">${template.success_rate}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Created</span>
                        <span class="stat-value">${window.helpers.DateUtils.getRelativeTime(template.created_at)}</span>
                    </div>
                </div>
                
                <div class="template-actions">
                    <button class="btn btn-primary btn-sm use-template" data-template-id="${template.id}">
                        <i class="fas fa-play"></i> Use Template
                    </button>
                    <button class="btn btn-secondary btn-sm view-template" data-template-id="${template.id}">
                        <i class="fas fa-eye"></i> View
                    </button>
                </div>
            </div>
        `;
    }

    bindTemplateEvents() {
        // Use template buttons
        const useButtons = this.container.querySelectorAll('.use-template');
        if (window.logger) {
            window.logger.debug('TemplateManager', `Binding ${useButtons.length} use-template buttons`);
        }
        useButtons.forEach(btn => {
            btn.addEventListener('click', this.handleUseTemplate.bind(this));
        });

        // View template buttons
        const viewButtons = this.container.querySelectorAll('.view-template');
        if (window.logger) {
            window.logger.debug('TemplateManager', `Binding ${viewButtons.length} view-template buttons`);
        }
        viewButtons.forEach(btn => {
            btn.addEventListener('click', this.handleViewTemplate.bind(this));
        });

        // Template menu buttons
        this.container.querySelectorAll('.template-menu-btn').forEach(btn => {
            btn.addEventListener('click', this.toggleTemplateMenu.bind(this));
        });

        // Menu actions
        this.container.querySelectorAll('.test-template').forEach(btn => {
            btn.addEventListener('click', this.handleTestTemplate.bind(this));
        });

        this.container.querySelectorAll('.edit-template').forEach(btn => {
            btn.addEventListener('click', this.handleEditTemplate.bind(this));
        });

        this.container.querySelectorAll('.duplicate-template').forEach(btn => {
            btn.addEventListener('click', this.handleDuplicateTemplate.bind(this));
        });

        this.container.querySelectorAll('.export-template').forEach(btn => {
            btn.addEventListener('click', this.handleExportTemplate.bind(this));
        });

        this.container.querySelectorAll('.delete-template').forEach(btn => {
            btn.addEventListener('click', this.handleDeleteTemplate.bind(this));
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', this.handleOutsideClick.bind(this));
    }

    toggleTemplateMenu(e) {
        e.stopPropagation();
        const templateId = e.currentTarget.dataset.templateId;
        const dropdown = document.getElementById(`dropdown-${templateId}`);
        
        // Close all other dropdowns
        this.container.querySelectorAll('.template-dropdown').forEach(d => {
            if (d !== dropdown) {
                d.classList.remove('show');
            }
        });
        
        dropdown.classList.toggle('show');
    }

    handleOutsideClick(e) {
        if (!e.target.closest('.template-menu')) {
            this.container.querySelectorAll('.template-dropdown').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    }

    handleUseTemplate(e) {
        try {
            const templateId = e.currentTarget.dataset.templateId;
            
            if (!templateId) {
                throw new Error('Template ID is missing. Please refresh the page and try again.');
            }
            
            const template = this.templates.find(t => t.id === templateId);
            
            if (window.logger) {
                window.logger.logUserInteraction('use-template-button', 'click', { templateId, template });
            }
            
            if (!template) {
                throw new Error(`Template "${templateId}" not found. Please refresh the page and try again.`);
            }
            
            // Check if scraperApp exists
            if (!window.scraperApp) {
                throw new Error('Application not fully loaded. Please refresh the page and try again.');
            }
            
            // Navigate to scraping page and select this template
            window.scraperApp.navigateToPage('scraping');
            
            // Wait for page to load then select template
            setTimeout(() => {
                try {
                    const templateSelect = document.getElementById('template-select');
                    if (templateSelect) {
                        // Check if template exists in dropdown
                        const optionExists = Array.from(templateSelect.options).some(opt => opt.value === templateId);
                        
                        if (!optionExists) {
                            // Add the template to dropdown if it doesn't exist
                            const option = document.createElement('option');
                            option.value = templateId;
                            option.textContent = `${template.name} (v${template.version})`;
                            templateSelect.appendChild(option);
                        }
                        
                        templateSelect.value = templateId;
                        templateSelect.dispatchEvent(new Event('change'));
                        
                        if (window.logger) {
                            window.logger.info('TemplateManager', 'Template selected in dropdown', { templateId });
                        }
                        
                        // Show success notification
                        window.notifications?.success('Template Selected', `Now using template: ${template.name}`);
                    } else {
                        throw new Error('Template selector not found on scraping page');
                    }
                } catch (error) {
                    console.error('Error selecting template:', error);
                    window.notifications?.error('Selection Failed', error.message);
                    if (window.logger) {
                        window.logger.error('TemplateManager', error.message, { templateId });
                    }
                }
            }, 200);
            
        } catch (error) {
            console.error('Failed to use template:', error);
            
            // Show error popup
            if (window.notifications) {
                window.notifications.error('Template Error', error.message);
            } else {
                alert(`Error: ${error.message}`);
            }
            
            if (window.logger) {
                window.logger.logError(error, 'TemplateManager', { action: 'useTemplate' });
            }
        }
    }

    async handleViewTemplate(e) {
        try {
            const templateId = e.currentTarget.dataset.templateId;
            
            if (!templateId) {
                throw new Error('Template ID is missing. Please refresh the page and try again.');
            }
            
            if (window.logger) {
                window.logger.logUserInteraction('view-template-button', 'click', { templateId });
            }
            
            if (!window.api) {
                throw new Error('API not initialized. Please refresh the page and try again.');
            }
            
            if (window.logger) {
                window.logger.info('TemplateManager', 'Fetching template details', { templateId });
            }
            
            // Show loading state
            const btn = e.currentTarget;
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            
            try {
                const response = await window.api.getTemplate(templateId);
                
                if (window.logger) {
                    window.logger.logApiCall('GET', `template/${templateId}`, null, response);
                }
                
                if (response.success) {
                    this.showTemplateDetailsModal(response.template);
                } else {
                    throw new Error(response.error || 'Failed to load template details');
                }
            } finally {
                // Restore button state
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
            
        } catch (error) {
            console.error('Failed to view template:', error);
            
            // Show error popup
            if (window.notifications) {
                window.notifications.error('View Failed', error.message);
            } else {
                alert(`Error: ${error.message}`);
            }
            
            if (window.logger) {
                window.logger.logError(error, 'TemplateManager', { action: 'viewTemplate', templateId: e.currentTarget.dataset.templateId });
            }
        }
    }

    showTemplateDetailsModal(template) {
        const content = `
            <div class="template-details">
                <div class="template-meta">
                    <div class="meta-grid">
                        <div class="meta-item">
                            <label>Name:</label>
                            <span>${template.name}</span>
                        </div>
                        <div class="meta-item">
                            <label>Version:</label>
                            <span>v${template.version}</span>
                        </div>
                        <div class="meta-item">
                            <label>Usage Count:</label>
                            <span>${template.usage_count}</span>
                        </div>
                        <div class="meta-item">
                            <label>Success Rate:</label>
                            <span>${template.success_rate}%</span>
                        </div>
                    </div>
                    
                    ${template.description ? `
                        <div class="meta-item full-width">
                            <label>Description:</label>
                            <p>${template.description}</p>
                        </div>
                    ` : ''}
                </div>
                
                <div class="template-selectors">
                    <h4>Selectors</h4>
                    <div class="selectors-list">
                        ${Object.entries(template.selectors || {}).map(([key, value]) => `
                            <div class="selector-item">
                                <label>${key}:</label>
                                <code>${value}</code>
                                <button class="btn btn-xs btn-secondary test-selector" 
                                        data-selector="${value}" title="Test Selector">
                                    <i class="fas fa-vial"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${template.fetcher_config ? `
                    <div class="template-fetcher-config">
                        <h4>Fetcher Configuration</h4>
                        <div class="config-display">
                            <div class="config-item">
                                <label>Type:</label>
                                <span class="config-value">${template.fetcher_config.fetcher_type || 'AUTO'}</span>
                            </div>
                            ${template.fetcher_config.timeout ? `
                                <div class="config-item">
                                    <label>Timeout:</label>
                                    <span class="config-value">${template.fetcher_config.timeout}s</span>
                                </div>
                            ` : ''}
                            ${template.fetcher_config.headless !== undefined ? `
                                <div class="config-item">
                                    <label>Headless:</label>
                                    <span class="config-value">${template.fetcher_config.headless ? 'Yes' : 'No'}</span>
                                </div>
                            ` : ''}
                            ${template.fetcher_config.stealth ? `
                                <div class="config-item">
                                    <label>Stealth Mode:</label>
                                    <span class="config-value">Enabled</span>
                                </div>
                            ` : ''}
                            ${template.fetcher_config.viewport ? `
                                <div class="config-item">
                                    <label>Viewport:</label>
                                    <span class="config-value">${template.fetcher_config.viewport.width}x${template.fetcher_config.viewport.height}</span>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${template.validation_rules && Object.keys(template.validation_rules).length > 0 ? `
                    <div class="template-validation">
                        <h4>Validation Rules</h4>
                        <pre class="code-block">${JSON.stringify(template.validation_rules, null, 2)}</pre>
                    </div>
                ` : ''}
                
                ${template.post_processing && template.post_processing.length > 0 ? `
                    <div class="template-processing">
                        <h4>Post Processing</h4>
                        <pre class="code-block">${JSON.stringify(template.post_processing, null, 2)}</pre>
                    </div>
                ` : ''}
                
                <div class="template-actions">
                    <button class="btn btn-primary" onclick="window.templateManager.useTemplateFromModal(${template.id})">
                        <i class="fas fa-play"></i> Use Template
                    </button>
                    <button class="btn btn-secondary" onclick="window.templateManager.editTemplateFromModal(${template.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        window.scraperApp.showModal(`Template: ${template.name}`, content);
        
        // Bind test selector buttons
        document.querySelectorAll('.test-selector').forEach(btn => {
            btn.addEventListener('click', this.handleTestSelector.bind(this));
        });
    }

    useTemplateFromModal(templateId) {
        window.scraperApp.hideModal();
        this.handleUseTemplate({ currentTarget: { dataset: { templateId } } });
    }

    editTemplateFromModal(templateId) {
        window.scraperApp.hideModal();
        this.handleEditTemplate({ currentTarget: { dataset: { templateId } } });
    }

    async handleTestSelector(e) {
        const selector = e.currentTarget.dataset.selector;
        const url = prompt('Enter URL to test selector against:');
        
        if (!url) return;

        try {
            const loadingId = window.notifications?.loading('Testing selector...');
            
            const response = await window.api.testSelector(url, selector);
            
            if (loadingId) window.notifications.dismiss(loadingId);
            
            if (response.success) {
                window.notifications?.success(
                    'Selector Test', 
                    `Found ${response.count} matches`
                );
                
                if (response.sample_data && response.sample_data.length > 0) {
                    this.showSelectorResults(selector, response);
                }
            } else {
                throw new Error(response.error || 'Selector test failed');
            }
            
        } catch (error) {
            console.error('Selector test failed:', error);
            window.notifications?.error('Test Failed', error.message);
        }
    }

    showSelectorResults(selector, results) {
        const content = `
            <div class="selector-results">
                <div class="selector-info">
                    <label>Selector:</label>
                    <code>${selector}</code>
                </div>
                
                <div class="results-stats">
                    <div class="stat-item">
                        <label>Matches Found:</label>
                        <span>${results.count}</span>
                    </div>
                </div>
                
                ${results.sample_data && results.sample_data.length > 0 ? `
                    <div class="sample-results">
                        <h4>Sample Results</h4>
                        <div class="results-list">
                            ${results.sample_data.slice(0, 5).map((data, index) => `
                                <div class="result-item">
                                    <label>Result ${index + 1}:</label>
                                    <div class="result-content">${data}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="actions">
                    <button class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        window.scraperApp.showModal('Selector Test Results', content);
    }

    handleTestTemplate(e) {
        const templateId = e.currentTarget.dataset.templateId;
        const template = this.templates.find(t => t.id === templateId);
        
        if (template) {
            this.showTestTemplateModal(template);
        }
    }

    showTestTemplateModal(template) {
        const content = `
            <form id="test-template-form" class="test-template-form">
                <div class="form-group">
                    <label for="test-url">Test URL</label>
                    <input type="url" id="test-url" required 
                           placeholder="Enter URL to test template against">
                </div>
                
                <div class="template-info">
                    <h4>Template: ${template.name}</h4>
                    <p>This will test all selectors in the template against the provided URL.</p>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-vial"></i> Run Test
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Cancel
                    </button>
                </div>
            </form>
        `;
        
        window.scraperApp.showModal('Test Template', content);
        
        const form = document.getElementById('test-template-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = form.querySelector('#test-url').value;
            this.runTemplateTest(template.id, url);
        });
    }

    async runTemplateTest(templateId, url) {
        try {
            const loadingId = window.notifications?.loading('Running template test...');
            
            const response = await window.api.previewUrl(url, templateId);
            
            if (loadingId) window.notifications.dismiss(loadingId);
            
            if (response.success) {
                window.scraperApp.hideModal();
                this.showTemplateTestResults(templateId, url, response.preview);
            } else {
                throw new Error(response.error || 'Template test failed');
            }
            
        } catch (error) {
            console.error('Template test failed:', error);
            window.notifications?.error('Test Failed', error.message);
        }
    }

    showTemplateTestResults(templateId, url, results) {
        const template = this.templates.find(t => t.id === templateId);
        
        const content = `
            <div class="template-test-results">
                <div class="test-info">
                    <div class="info-item">
                        <label>Template:</label>
                        <span>${template.name}</span>
                    </div>
                    <div class="info-item">
                        <label>Test URL:</label>
                        <a href="${url}" target="_blank">${window.helpers.StringUtils.truncate(url, 50)}</a>
                    </div>
                </div>
                
                <div class="test-stats">
                    <div class="stat-item">
                        <label>Elements Found:</label>
                        <span class="stat-value">${results.count || 0}</span>
                    </div>
                    <div class="stat-item">
                        <label>Success Rate:</label>
                        <span class="stat-value">${results.success_rate || '0%'}</span>
                    </div>
                </div>
                
                ${results.sample_data ? `
                    <div class="sample-data">
                        <h4>Sample Extracted Data</h4>
                        <pre class="code-block">${JSON.stringify(results.sample_data, null, 2)}</pre>
                    </div>
                ` : ''}
                
                ${results.errors && results.errors.length > 0 ? `
                    <div class="test-errors">
                        <h4>Errors Found</h4>
                        <ul class="error-list">
                            ${results.errors.map(error => `<li class="text-error">${error}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="actions">
                    <button class="btn btn-primary" onclick="window.templateManager.useTemplateFromTest(${templateId}, '${url}')">
                        <i class="fas fa-play"></i> Use Template
                    </button>
                    <button class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        window.scraperApp.showModal('Template Test Results', content);
    }

    useTemplateFromTest(templateId, testUrl) {
        window.scraperApp.hideModal();
        window.scraperApp.navigateToPage('scraping');
        
        setTimeout(() => {
            const templateSelect = document.getElementById('template-select');
            const urlInput = document.getElementById('target-url');
            
            if (templateSelect) {
                templateSelect.value = templateId;
                templateSelect.dispatchEvent(new Event('change'));
            }
            
            if (urlInput) {
                urlInput.value = testUrl;
            }
        }, 100);
    }

    async handleEditTemplate(e) {
        const templateId = e.currentTarget.dataset.templateId;
        
        try {
            const response = await window.api.getTemplate(templateId);
            if (response.success) {
                this.showEditTemplateModal(response.template);
            } else {
                throw new Error(response.error || 'Failed to load template');
            }
        } catch (error) {
            console.error('Failed to load template for editing:', error);
            window.notifications?.error('Load Failed', error.message);
        }
    }

    showEditTemplateModal(template) {
        const selectorsHTML = Object.entries(template.selectors || {}).map(([key, value]) => `
            <div class="selector-row">
                <input type="text" class="selector-name" value="${key}" placeholder="Field name">
                <input type="text" class="selector-value" value="${value}" placeholder="CSS selector">
                <button type="button" class="btn btn-danger btn-sm remove-selector">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');

        const content = `
            <form id="edit-template-form" class="edit-template-form">
                <input type="hidden" id="template-id" value="${template.id}">
                
                <div class="form-group">
                    <label for="edit-template-name">Template Name</label>
                    <input type="text" id="edit-template-name" value="${template.name}" required>
                </div>
                
                <div class="form-group">
                    <label for="edit-template-description">Description</label>
                    <textarea id="edit-template-description" rows="3">${template.description || ''}</textarea>
                </div>
                
                <div class="form-group">
                    <label>Selectors</label>
                    <div id="edit-selectors-container">
                        ${selectorsHTML}
                    </div>
                    <button type="button" class="btn btn-secondary btn-sm" id="add-edit-selector">
                        <i class="fas fa-plus"></i> Add Selector
                    </button>
                </div>
                
                ${this.getFetcherConfigHTML(template.fetcher_config)}
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Save Changes
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Cancel
                    </button>
                </div>
            </form>
        `;
        
        window.scraperApp.showModal(`Edit Template: ${template.name}`, content);
        
        this.bindEditTemplateEvents();
    }

    bindEditTemplateEvents() {
        const form = document.getElementById('edit-template-form');
        if (!form) return;

        // Add selector button
        const addBtn = form.querySelector('#add-edit-selector');
        addBtn.addEventListener('click', this.addEditSelectorRow.bind(this));

        // Form submission
        form.addEventListener('submit', this.handleEditTemplateSubmit.bind(this));

        // Remove selector buttons (using delegation)
        form.addEventListener('click', (e) => {
            if (e.target.closest('.remove-selector')) {
                const row = e.target.closest('.selector-row');
                row.remove();
            }
        });

        // Bind fetcher configuration events
        this.bindFetcherConfigEvents();
    }

    addEditSelectorRow() {
        const container = document.getElementById('edit-selectors-container');
        const row = document.createElement('div');
        row.className = 'selector-row';
        row.innerHTML = `
            <input type="text" class="selector-name" placeholder="Field name">
            <input type="text" class="selector-value" placeholder="CSS selector">
            <button type="button" class="btn btn-danger btn-sm remove-selector">
                <i class="fas fa-trash"></i>
            </button>
        `;
        container.appendChild(row);
    }

    async handleEditTemplateSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const templateId = parseInt(form.querySelector('#template-id').value);
        const name = form.querySelector('#edit-template-name').value.trim();
        const description = form.querySelector('#edit-template-description').value.trim();
        
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
            window.notifications?.warning('Invalid Template', 'Please add at least one selector');
            return;
        }

        // Collect fetcher configuration
        const fetcherConfig = this.collectFetcherConfig();
        
        // Validate fetcher configuration
        const configErrors = this.validateFetcherConfig(fetcherConfig);
        if (configErrors.length > 0) {
            window.notifications?.warning('Invalid Configuration', configErrors.join(', '));
            return;
        }

        try {
            const templateData = {
                name,
                description,
                selectors,
                fetcher_config: fetcherConfig
            };
            
            const response = await window.api.updateTemplate(templateId, templateData);
            
            if (response.success) {
                window.scraperApp.hideModal();
                
                window.notifications?.success('Template Updated', `Template "${name}" updated successfully`);
                
                // Refresh templates
                await this.loadTemplates();
                
            } else {
                throw new Error(response.error || 'Failed to update template');
            }
            
        } catch (error) {
            console.error('Template update error:', error);
            window.notifications?.error('Update Failed', error.message);
        }
    }

    async handleDuplicateTemplate(e) {
        const templateId = e.currentTarget.dataset.templateId;
        const template = this.templates.find(t => t.id === templateId);
        
        if (!template) return;

        try {
            const duplicateData = {
                name: `${template.name} (Copy)`,
                description: template.description,
                selectors: template.selectors,
                fetcher_config: template.fetcher_config
            };
            
            const response = await window.api.createTemplate(duplicateData);
            
            if (response.success) {
                window.notifications?.success('Template Duplicated', `Created copy: ${duplicateData.name}`);
                await this.loadTemplates();
            } else {
                throw new Error(response.error || 'Failed to duplicate template');
            }
            
        } catch (error) {
            console.error('Template duplication error:', error);
            window.notifications?.error('Duplication Failed', error.message);
        }
    }

    async handleExportTemplate(e) {
        const templateId = e.currentTarget.dataset.templateId;
        
        try {
            const response = await window.api.getTemplate(templateId);
            if (response.success) {
                const template = response.template;
                const exportData = {
                    name: template.name,
                    description: template.description,
                    selectors: template.selectors,
                    fetcher_config: template.fetcher_config,
                    validation_rules: template.validation_rules,
                    post_processing: template.post_processing,
                    version: template.version,
                    exported_at: new Date().toISOString()
                };
                
                const filename = `${template.name.replace(/[^a-zA-Z0-9]/g, '_')}_template.json`;
                const jsonString = JSON.stringify(exportData, null, 2);
                
                window.helpers.FileUtils.downloadAsFile(jsonString, filename, 'application/json');
                
                window.notifications?.success('Template Exported', `Template exported as ${filename}`);
                
            } else {
                throw new Error(response.error || 'Failed to load template');
            }
        } catch (error) {
            console.error('Template export error:', error);
            window.notifications?.error('Export Failed', error.message);
        }
    }

    async handleDeleteTemplate(e) {
        const templateId = e.currentTarget.dataset.templateId;
        const template = this.templates.find(t => t.id === templateId);
        
        if (!template) return;

        if (!confirm(`Are you sure you want to delete the template "${template.name}"? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await window.api.deleteTemplate(templateId);
            
            if (response.success) {
                window.notifications?.success('Template Deleted', `Template "${template.name}" deleted successfully`);
                await this.loadTemplates();
            } else {
                throw new Error(response.error || 'Failed to delete template');
            }
            
        } catch (error) {
            console.error('Template deletion error:', error);
            window.notifications?.error('Deletion Failed', error.message);
        }
    }

    /**
     * Generate fetcher configuration HTML
     */
    getFetcherConfigHTML(existingConfig = null) {
        const config = existingConfig || {};
        const fetcherType = config.fetcher_type || 'AUTO';
        
        return `
            <div class="form-group">
                <label>Fetcher Configuration</label>
                
                <!-- High-level trigger checkboxes -->
                <div class="fetcher-triggers">
                    <h5>Quick Setup</h5>
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" class="trigger-checkbox" data-trigger="javascript_required" 
                                   ${config.javascript_required ? 'checked' : ''}>
                            <span class="checkbox-text">JavaScript Required <small>(auto-selects PLAYWRIGHT)</small></span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" class="trigger-checkbox" data-trigger="stealth_required"
                                   ${config.stealth_required ? 'checked' : ''}>
                            <span class="checkbox-text">Stealth Required <small>(auto-selects STEALTH)</small></span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" class="trigger-checkbox" data-trigger="anti_bot_protection"
                                   ${config.anti_bot_protection ? 'checked' : ''}>
                            <span class="checkbox-text">Anti-Bot Protection <small>(auto-selects STEALTH)</small></span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" class="trigger-checkbox" data-trigger="concurrent_scraping"
                                   ${config.concurrent_scraping ? 'checked' : ''}>
                            <span class="checkbox-text">Concurrent Scraping <small>(auto-selects ASYNC)</small></span>
                        </label>
                    </div>
                </div>
                
                <!-- Fetcher type selection -->
                <div class="form-group">
                    <label for="fetcher-type">Fetcher Type</label>
                    <select id="fetcher-type" class="form-control">
                        <option value="AUTO" ${fetcherType === 'AUTO' ? 'selected' : ''}>AUTO (Automatic selection)</option>
                        <option value="BASIC" ${fetcherType === 'BASIC' ? 'selected' : ''}>BASIC (Simple HTTP requests)</option>
                        <option value="ASYNC" ${fetcherType === 'ASYNC' ? 'selected' : ''}>ASYNC (Concurrent requests)</option>
                        <option value="STEALTH" ${fetcherType === 'STEALTH' ? 'selected' : ''}>STEALTH (Anti-detection)</option>
                        <option value="PLAYWRIGHT" ${fetcherType === 'PLAYWRIGHT' ? 'selected' : ''}>PLAYWRIGHT (Full browser)</option>
                    </select>
                </div>
                
                <!-- Configuration fields for each fetcher type -->
                <div class="fetcher-configs">
                    ${this.getBasicAsyncConfigHTML(config)}
                    ${this.getStealthConfigHTML(config)}
                    ${this.getPlaywrightConfigHTML(config)}
                </div>
            </div>
        `;
    }

    getBasicAsyncConfigHTML(config) {
        return `
            <div class="fetcher-config" data-types="BASIC,ASYNC">
                <h5>Basic/Async Configuration</h5>
                <div class="config-grid">
                    <div class="form-group">
                        <label for="basic-timeout">Timeout (seconds)</label>
                        <input type="number" id="basic-timeout" value="${config.timeout || 30}" min="1" max="300">
                        <small class="help-text">Request timeout in seconds</small>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="follow-redirects" ${config.follow_redirects !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Follow Redirects</span>
                        </label>
                    </div>
                    <div class="form-group full-width">
                        <label for="request-headers">Headers (JSON)</label>
                        <textarea id="request-headers" rows="3" placeholder='{"User-Agent": "Custom Agent", "Accept": "text/html"}'>${config.headers ? JSON.stringify(config.headers, null, 2) : ''}</textarea>
                        <small class="help-text">Custom HTTP headers as JSON object</small>
                    </div>
                    <div class="form-group full-width">
                        <label for="request-cookies">Cookies (JSON)</label>
                        <textarea id="request-cookies" rows="2" placeholder='{"session_id": "abc123", "token": "xyz789"}'>${config.cookies ? JSON.stringify(config.cookies, null, 2) : ''}</textarea>
                        <small class="help-text">Custom cookies as JSON object</small>
                    </div>
                </div>
            </div>
        `;
    }

    getStealthConfigHTML(config) {
        return `
            <div class="fetcher-config" data-types="STEALTH">
                <h5>Stealth Configuration</h5>
                <div class="config-grid">
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="stealth-headless" ${config.headless !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Headless Mode</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="block-images" ${config.block_images ? 'checked' : ''}>
                            <span class="checkbox-text">Block Images</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="block-webrtc" ${config.block_webrtc !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Block WebRTC</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="humanize" ${config.humanize !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Humanize Behavior</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="stealth-network-idle" ${config.network_idle !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Wait for Network Idle</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="os-randomization" ${config.os_randomization !== false ? 'checked' : ''}>
                            <span class="checkbox-text">OS Randomization</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="spoof-canvas" ${config.spoof_canvas !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Spoof Canvas</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="spoof-webgl" ${config.spoof_webgl !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Spoof WebGL</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="disable-ads" ${config.disable_ads !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Disable Ads</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="google-search" ${config.google_search !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Google Search Mode</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label for="stealth-wait-selector">Wait for Selector</label>
                        <input type="text" id="stealth-wait-selector" value="${config.wait_for_selector || ''}" placeholder=".content, #main">
                        <small class="help-text">CSS selector to wait for before scraping</small>
                    </div>
                    <div class="form-group">
                        <label for="stealth-timeout">Timeout (seconds)</label>
                        <input type="number" id="stealth-timeout" value="${config.timeout || 60}" min="1" max="300">
                    </div>
                </div>
            </div>
        `;
    }

    getPlaywrightConfigHTML(config) {
        return `
            <div class="fetcher-config" data-types="PLAYWRIGHT">
                <h5>Playwright Configuration</h5>
                <div class="config-grid">
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="playwright-headless" ${config.headless !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Headless Mode</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="playwright-network-idle" ${config.network_idle !== false ? 'checked' : ''}>
                            <span class="checkbox-text">Wait for Network Idle</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="playwright-stealth" ${config.stealth ? 'checked' : ''}>
                            <span class="checkbox-text">Stealth Mode</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="real-chrome" ${config.real_chrome ? 'checked' : ''}>
                            <span class="checkbox-text">Use Real Chrome</span>
                        </label>
                    </div>
                    <div class="form-group">
                        <label>Block Resources</label>
                        <div class="checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="block-image" ${config.block_resources?.includes('image') ? 'checked' : ''}>
                                <span class="checkbox-text">Images</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" id="block-font" ${config.block_resources?.includes('font') ? 'checked' : ''}>
                                <span class="checkbox-text">Fonts</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" id="block-media" ${config.block_resources?.includes('media') ? 'checked' : ''}>
                                <span class="checkbox-text">Media</span>
                            </label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="playwright-wait-selector">Wait for Selector</label>
                        <input type="text" id="playwright-wait-selector" value="${config.wait_for_selector || ''}" placeholder=".content, #main">
                        <small class="help-text">CSS selector to wait for before scraping</small>
                    </div>
                    <div class="form-group">
                        <label for="wait-timeout">Wait Timeout (seconds)</label>
                        <input type="number" id="wait-timeout" value="${config.wait_for_timeout || 30}" min="1" max="300">
                    </div>
                    <div class="form-group">
                        <label for="viewport-width">Viewport Width</label>
                        <input type="number" id="viewport-width" value="${config.viewport?.width || 1920}" min="320" max="3840">
                    </div>
                    <div class="form-group">
                        <label for="viewport-height">Viewport Height</label>
                        <input type="number" id="viewport-height" value="${config.viewport?.height || 1080}" min="240" max="2160">
                    </div>
                    <div class="form-group">
                        <label for="locale">Locale</label>
                        <input type="text" id="locale" value="${config.locale || 'en-US'}" placeholder="en-US">
                        <small class="help-text">Browser locale setting</small>
                    </div>
                    <div class="form-group">
                        <label for="timezone">Timezone</label>
                        <input type="text" id="timezone" value="${config.timezone || 'America/New_York'}" placeholder="America/New_York">
                        <small class="help-text">Browser timezone setting</small>
                    </div>
                    <div class="form-group">
                        <label for="playwright-timeout">Timeout (seconds)</label>
                        <input type="number" id="playwright-timeout" value="${config.timeout || 60}" min="1" max="300">
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Bind events for fetcher configuration
     */
    bindFetcherConfigEvents() {
        const fetcherTypeSelect = document.getElementById('fetcher-type');
        const triggerCheckboxes = document.querySelectorAll('.trigger-checkbox');

        // Handle fetcher type changes
        if (fetcherTypeSelect) {
            fetcherTypeSelect.addEventListener('change', this.updateFetcherConfigVisibility.bind(this));
            this.updateFetcherConfigVisibility();
        }

        // Handle trigger checkbox changes
        triggerCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', this.handleTriggerChange.bind(this));
        });
    }

    /**
     * Update visibility of fetcher config sections
     */
    updateFetcherConfigVisibility() {
        const fetcherType = document.getElementById('fetcher-type')?.value;
        const configSections = document.querySelectorAll('.fetcher-config');

        configSections.forEach(section => {
            const supportedTypes = section.dataset.types.split(',');
            if (supportedTypes.includes(fetcherType) || fetcherType === 'AUTO') {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }

    /**
     * Handle trigger checkbox changes
     */
    handleTriggerChange(e) {
        const trigger = e.target.dataset.trigger;
        const fetcherTypeSelect = document.getElementById('fetcher-type');
        
        if (!e.target.checked || !fetcherTypeSelect) return;

        const triggerMappings = {
            'javascript_required': 'PLAYWRIGHT',
            'stealth_required': 'STEALTH',
            'anti_bot_protection': 'STEALTH',
            'concurrent_scraping': 'ASYNC'
        };

        if (triggerMappings[trigger]) {
            fetcherTypeSelect.value = triggerMappings[trigger];
            fetcherTypeSelect.dispatchEvent(new Event('change'));
        }
    }

    /**
     * Collect fetcher configuration from form
     */
    collectFetcherConfig() {
        const fetcherType = document.getElementById('fetcher-type')?.value || 'AUTO';
        const config = { fetcher_type: fetcherType };

        // Collect trigger flags
        document.querySelectorAll('.trigger-checkbox').forEach(checkbox => {
            config[checkbox.dataset.trigger] = checkbox.checked;
        });

        // Collect configuration based on fetcher type
        if (fetcherType === 'BASIC' || fetcherType === 'ASYNC') {
            config.timeout = parseInt(document.getElementById('basic-timeout')?.value) || 30;
            config.follow_redirects = document.getElementById('follow-redirects')?.checked;
            
            const headersText = document.getElementById('request-headers')?.value.trim();
            if (headersText) {
                try {
                    config.headers = JSON.parse(headersText);
                } catch (e) {
                    console.warn('Invalid headers JSON:', e);
                }
            }
            
            const cookiesText = document.getElementById('request-cookies')?.value.trim();
            if (cookiesText) {
                try {
                    config.cookies = JSON.parse(cookiesText);
                } catch (e) {
                    console.warn('Invalid cookies JSON:', e);
                }
            }
        }

        if (fetcherType === 'STEALTH') {
            config.headless = document.getElementById('stealth-headless')?.checked;
            config.block_images = document.getElementById('block-images')?.checked;
            config.block_webrtc = document.getElementById('block-webrtc')?.checked;
            config.humanize = document.getElementById('humanize')?.checked;
            config.network_idle = document.getElementById('stealth-network-idle')?.checked;
            config.wait_for_selector = document.getElementById('stealth-wait-selector')?.value.trim() || null;
            config.os_randomization = document.getElementById('os-randomization')?.checked;
            config.spoof_canvas = document.getElementById('spoof-canvas')?.checked;
            config.spoof_webgl = document.getElementById('spoof-webgl')?.checked;
            config.disable_ads = document.getElementById('disable-ads')?.checked;
            config.google_search = document.getElementById('google-search')?.checked;
            config.timeout = parseInt(document.getElementById('stealth-timeout')?.value) || 60;
        }

        if (fetcherType === 'PLAYWRIGHT') {
            config.headless = document.getElementById('playwright-headless')?.checked;
            config.network_idle = document.getElementById('playwright-network-idle')?.checked;
            config.stealth = document.getElementById('playwright-stealth')?.checked;
            config.real_chrome = document.getElementById('real-chrome')?.checked;
            config.wait_for_selector = document.getElementById('playwright-wait-selector')?.value.trim() || null;
            config.wait_for_timeout = parseInt(document.getElementById('wait-timeout')?.value) || 30;
            config.locale = document.getElementById('locale')?.value.trim() || 'en-US';
            config.timezone = document.getElementById('timezone')?.value.trim() || 'America/New_York';
            config.timeout = parseInt(document.getElementById('playwright-timeout')?.value) || 60;
            
            // Collect viewport settings
            config.viewport = {
                width: parseInt(document.getElementById('viewport-width')?.value) || 1920,
                height: parseInt(document.getElementById('viewport-height')?.value) || 1080
            };

            // Collect block resources
            const blockResources = [];
            if (document.getElementById('block-image')?.checked) blockResources.push('image');
            if (document.getElementById('block-font')?.checked) blockResources.push('font');
            if (document.getElementById('block-media')?.checked) blockResources.push('media');
            if (blockResources.length > 0) config.block_resources = blockResources;
        }

        return config;
    }

    /**
     * Validate fetcher configuration
     */
    validateFetcherConfig(config) {
        const errors = [];

        if (config.timeout && (config.timeout < 1 || config.timeout > 300)) {
            errors.push('Timeout must be between 1 and 300 seconds');
        }

        if (config.viewport) {
            if (config.viewport.width < 320 || config.viewport.width > 3840) {
                errors.push('Viewport width must be between 320 and 3840 pixels');
            }
            if (config.viewport.height < 240 || config.viewport.height > 2160) {
                errors.push('Viewport height must be between 240 and 2160 pixels');
            }
        }

        return errors;
    }

    showCreateTemplateModal() {
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
                
                ${this.getFetcherConfigHTML()}
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Create Template</button>
                    <button type="button" class="btn btn-secondary" onclick="window.scraperApp.hideModal()">Cancel</button>
                </div>
            </form>
        `;
        
        window.scraperApp.showModal('Create New Template', content);
        
        // Bind template form events
        this.bindCreateTemplateEvents();
    }

    bindCreateTemplateEvents() {
        const form = document.getElementById('create-template-form');
        if (!form) return;

        // Add selector button
        const addSelectorBtn = form.querySelector('#add-selector');
        addSelectorBtn.addEventListener('click', this.addSelectorRow.bind(this));

        // Form submission
        form.addEventListener('submit', this.handleCreateTemplateSubmit.bind(this));

        // Remove selector buttons (using delegation)
        form.addEventListener('click', (e) => {
            if (e.target.closest('.remove-selector')) {
                const row = e.target.closest('.selector-row');
                row.remove();
            }
        });

        // Bind fetcher configuration events
        this.bindFetcherConfigEvents();
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

    async handleCreateTemplateSubmit(e) {
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
            window.notifications?.warning('Invalid Template', 'Please add at least one selector');
            return;
        }

        // Collect fetcher configuration
        const fetcherConfig = this.collectFetcherConfig();
        
        // Validate fetcher configuration
        const configErrors = this.validateFetcherConfig(fetcherConfig);
        if (configErrors.length > 0) {
            window.notifications?.warning('Invalid Configuration', configErrors.join(', '));
            return;
        }

        try {
            const templateData = {
                name,
                description,
                selectors,
                fetcher_config: fetcherConfig
            };
            
            const response = await window.api.createTemplate(templateData);
            
            if (response.success) {
                window.scraperApp.hideModal();
                
                window.notifications?.success('Template Created', `Template "${name}" created successfully`);
                
                // Refresh templates
                await this.loadTemplates();
                
            } else {
                throw new Error(response.error || 'Failed to create template');
            }
            
        } catch (error) {
            console.error('Template creation error:', error);
            window.notifications?.error('Creation Failed', error.message);
        }
    }

    async loadTemplates() {
        try {
            if (window.logger) {
                window.logger.info('TemplateManager', 'Loading templates');
            }
            
            if (!window.api) {
                throw new Error('window.api is not defined');
            }
            
            const response = await window.api.getTemplates();
            
            if (window.logger) {
                window.logger.logApiCall('GET', 'templates', null, response);
            }
            
            if (response.success) {
                this.renderTemplates(response.templates);
            } else {
                throw new Error(response.error || 'Failed to load templates');
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
            if (window.logger) {
                window.logger.logError(error, 'TemplateManager', { action: 'loadTemplates' });
            }
            this.renderErrorState(error.message);
        }
    }

    renderEmptyState() {
        this.container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-file-code"></i>
                </div>
                <h3>No Templates Found</h3>
                <p>Create your first scraping template to get started.</p>
                <button class="btn btn-primary" onclick="window.templateManager.showCreateTemplateModal()">
                    <i class="fas fa-plus"></i> Create Template
                </button>
            </div>
        `;
    }

    renderErrorState(message) {
        this.container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Failed to Load Templates</h3>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="window.templateManager.loadTemplates()">
                    <i class="fas fa-sync"></i> Try Again
                </button>
            </div>
        `;
    }
    
    /**
     * Create interactive mode button
     */
    createInteractiveModeButton() {
        // Find the header or toolbar area
        const header = document.querySelector('.templates-header') || 
                      document.querySelector('.page-header') ||
                      document.querySelector('.toolbar');
        
        if (header) {
            // Check if button already exists
            if (document.getElementById('interactive-mode-btn')) return;
            
            // Create button
            const button = document.createElement('button');
            button.id = 'interactive-mode-btn';
            button.className = 'btn btn-success';
            button.innerHTML = '<i class="fas fa-mouse-pointer"></i> Interactive Mode';
            button.title = 'Create template by selecting elements visually';
            button.style.cssText = 'margin-left: 10px;';
            
            // Add click handler
            button.addEventListener('click', this.startInteractiveMode.bind(this));
            
            // Find new template button and add next to it
            const newTemplateBtn = document.getElementById('new-template-btn');
            if (newTemplateBtn && newTemplateBtn.parentElement) {
                newTemplateBtn.parentElement.appendChild(button);
            } else if (header) {
                // Add to header if no new template button found
                header.appendChild(button);
            }
            
            if (window.logger) {
                window.logger.info('TemplateManager', 'Interactive mode button created');
            }
        }
    }
    
    /**
     * Start interactive template creation mode
     */
    async startInteractiveMode() {
        if (window.logger) {
            window.logger.info('TemplateManager', 'Starting Playwright interactive mode');
        }
        
        // Prompt for URL
        const url = prompt('Enter the URL to create a template for:');
        if (!url) return;
        
        // Validate URL
        try {
            new URL(url);
        } catch (error) {
            if (window.notifications) {
                window.notifications.error('Invalid URL', 'Please enter a valid URL');
            } else {
                alert('Invalid URL provided');
            }
            return;
        }
        
        // Use new Playwright-based interactive mode
        this.startPlaywrightInteractiveMode(url);
    }
    
    /**
     * Start Playwright-based interactive mode
     */
    async startPlaywrightInteractiveMode(url) {
        try {
            // Show loading indicator
            if (window.notifications) {
                window.notifications.info('Starting Interactive Mode', 'Launching browser session...');
            }
            
            // Start Playwright session
            const result = await window.api.startPlaywrightInteractive(url, {
                headless: false,
                viewport: { width: 1280, height: 720 }
            });
            
            if (!result.success) {
                if (window.notifications) {
                    window.notifications.error('Failed to Start', result.error || 'Could not start interactive mode');
                } else {
                    alert('Failed to start interactive mode: ' + (result.error || 'Unknown error'));
                }
                return;
            }
            
            // Store session info
            this.currentInteractiveSession = {
                sessionId: result.session_id,
                url: result.url,
                viewport: result.viewport
            };
            
            // Show the interactive interface
            this.showPlaywrightInteractiveInterface(result);
            
            if (window.logger) {
                window.logger.info('TemplateManager', 'Playwright interactive session started', {
                    sessionId: result.session_id,
                    url: result.url
                });
            }
            
        } catch (error) {
            console.error('Error starting Playwright interactive mode:', error);
            if (window.notifications) {
                window.notifications.error('Error', 'Failed to start interactive mode');
            } else {
                alert('Error starting interactive mode: ' + error.message);
            }
        }
    }
    
    /**
     * Show the Playwright interactive interface
     */
    showPlaywrightInteractiveInterface(sessionData) {
        // Create modal for interactive interface
        const modal = document.createElement('div');
        modal.id = 'playwright-interactive-modal';
        modal.className = 'modal-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            justify-content: center;
            align-items: center;
        `;
        
        modal.innerHTML = `
            <div class="interactive-container" style="
                width: 90%;
                height: 90%;
                background: #1a1a1a;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            ">
                <!-- Header -->
                <div class="interactive-header" style="
                    background: #2d2d2d;
                    padding: 15px 20px;
                    display: flex;
                    justify-content: between;
                    align-items: center;
                    border-bottom: 1px solid #404040;
                ">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <h3 style="margin: 0; color: #ffffff; font-size: 16px;">
                            🎯 Interactive Template Creator
                        </h3>
                        <span style="color: #888; font-size: 12px;" id="session-url">
                            ${sessionData.url}
                        </span>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button id="start-selection-btn" class="btn btn-success btn-sm" style="
                            background: #28a745;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 12px;
                        ">▶ Start Selection</button>
                        
                        <button id="stop-selection-btn" class="btn btn-danger btn-sm" style="
                            background: #dc3545;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 12px;
                            display: none;
                        ">⏹ Stop Selection</button>
                        
                        <button id="refresh-screenshot-btn" class="btn btn-secondary btn-sm" style="
                            background: #6c757d;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 12px;
                        ">🔄 Refresh</button>
                        
                        <span id="selected-count" style="
                            color: #28a745;
                            font-weight: bold;
                            font-size: 12px;
                            margin: 0 10px;
                        ">Selected: 0</span>
                        
                        <button id="create-template-btn" class="btn btn-primary btn-sm" style="
                            background: #007bff;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 12px;
                        ">📁 Create Template</button>
                        
                        <button id="close-interactive-btn" class="btn btn-light btn-sm" style="
                            background: #f8f9fa;
                            color: #333;
                            border: none;
                            padding: 6px 10px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: bold;
                        ">✕</button>
                    </div>
                </div>
                
                <!-- Content Area -->
                <div class="interactive-content" style="
                    flex: 1;
                    display: flex;
                    overflow: hidden;
                ">
                    <!-- Browser View -->
                    <div class="browser-view" style="
                        flex: 1;
                        background: #000;
                        position: relative;
                        overflow: auto;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    ">
                        <img id="browser-screenshot" style="
                            max-width: 100%;
                            max-height: 100%;
                            cursor: crosshair;
                            border: 1px solid #404040;
                        " src="${sessionData.screenshot || ''}" alt="Browser Screenshot">
                        
                        <div id="loading-overlay" style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            background: rgba(0, 0, 0, 0.7);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            color: white;
                            font-size: 16px;
                        ">
                            Loading browser view...
                        </div>
                    </div>
                    
                    <!-- Side Panel -->
                    <div class="side-panel" style="
                        width: 350px;
                        background: #2d2d2d;
                        border-left: 1px solid #404040;
                        display: flex;
                        flex-direction: column;
                    ">
                        <!-- Selected Elements -->
                        <div style="
                            padding: 15px;
                            border-bottom: 1px solid #404040;
                        ">
                            <h4 style="margin: 0 0 10px 0; color: #ffffff; font-size: 14px;">
                                📋 Selected Elements
                            </h4>
                            <div id="selected-elements-list" style="
                                max-height: 200px;
                                overflow-y: auto;
                                background: #1a1a1a;
                                border-radius: 4px;
                                padding: 8px;
                            ">
                                <div style="color: #888; text-align: center; padding: 20px; font-size: 12px;">
                                    No elements selected yet.<br>
                                    Click "Start Selection" and then click on elements in the browser view.
                                </div>
                            </div>
                        </div>
                        
                        <!-- Page Info -->
                        <div style="
                            padding: 15px;
                            flex: 1;
                            overflow-y: auto;
                        ">
                            <h4 style="margin: 0 0 10px 0; color: #ffffff; font-size: 14px;">
                                ℹ️ Page Information
                            </h4>
                            <div id="page-info" style="
                                background: #1a1a1a;
                                border-radius: 4px;
                                padding: 10px;
                                font-size: 12px;
                                color: #ccc;
                            ">
                                Loading page information...
                            </div>
                        </div>
                        
                        <!-- Instructions -->
                        <div style="
                            padding: 15px;
                            border-top: 1px solid #404040;
                            background: #1f1f1f;
                        ">
                            <h4 style="margin: 0 0 8px 0; color: #ffffff; font-size: 12px;">
                                💡 Instructions
                            </h4>
                            <div style="font-size: 11px; color: #aaa; line-height: 1.4;">
                                1. Click "Start Selection" to begin<br>
                                2. Click on elements in the browser view<br>
                                3. Selected elements will appear in the list<br>
                                4. Click "Create Template" when done
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Bind events
        this.bindPlaywrightInteractiveEvents();
        
        // Load initial data
        this.refreshBrowserScreenshot();
        this.loadPageInfo();
        
        // Hide loading overlay once screenshot is loaded
        if (sessionData.screenshot) {
            document.getElementById('loading-overlay').style.display = 'none';
        }
    }
    
    /**
     * Bind events for Playwright interactive interface
     */
    bindPlaywrightInteractiveEvents() {
        const modal = document.getElementById('playwright-interactive-modal');
        if (!modal) return;
        
        // Close modal
        modal.querySelector('#close-interactive-btn').addEventListener('click', () => {
            this.closePlaywrightInteractiveMode();
        });
        
        // Start/stop selection
        modal.querySelector('#start-selection-btn').addEventListener('click', () => {
            this.startElementSelection();
        });
        
        modal.querySelector('#stop-selection-btn').addEventListener('click', () => {
            this.stopElementSelection();
        });
        
        // Refresh screenshot
        modal.querySelector('#refresh-screenshot-btn').addEventListener('click', () => {
            this.refreshBrowserScreenshot();
        });
        
        // Create template
        modal.querySelector('#create-template-btn').addEventListener('click', () => {
            this.createTemplateFromSelections();
        });
        
        // Click on screenshot to select elements
        modal.querySelector('#browser-screenshot').addEventListener('click', (e) => {
            this.handleScreenshotClick(e);
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closePlaywrightInteractiveMode();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleInteractiveKeyboard.bind(this));
    }
    
    /**
     * Handle keyboard shortcuts in interactive mode
     */
    handleInteractiveKeyboard(e) {
        if (!document.getElementById('playwright-interactive-modal')) return;
        
        if (e.key === 'Escape') {
            e.preventDefault();
            this.closePlaywrightInteractiveMode();
        } else if (e.key === ' ' && e.ctrlKey) {
            e.preventDefault();
            // Toggle selection mode
            const startBtn = document.getElementById('start-selection-btn');
            const stopBtn = document.getElementById('stop-selection-btn');
            if (startBtn.style.display !== 'none') {
                this.startElementSelection();
            } else {
                this.stopElementSelection();
            }
        }
    }
    
    /**
     * Handle clicks on the browser screenshot
     */
    async handleScreenshotClick(e) {
        if (!this.isSelectionModeActive) return;
        
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Calculate coordinates relative to the actual image size
        const img = e.target;
        const scaleX = img.naturalWidth / img.clientWidth;
        const scaleY = img.naturalHeight / img.clientHeight;
        
        const actualX = Math.round(x * scaleX);
        const actualY = Math.round(y * scaleY);
        
        try {
            // Select element at coordinates
            const result = await window.api.selectElementAtCoordinates(
                this.currentInteractiveSession.sessionId,
                actualX,
                actualY
            );
            
            if (result.success && result.element) {
                this.addSelectedElement(result.element);
                this.updateSelectedElementsList();
                
                if (window.notifications) {
                    window.notifications.success('Element Selected', 
                        `Selected ${result.element.tag} element`);
                }
            } else {
                if (window.notifications) {
                    window.notifications.warning('No Element', 
                        'No element found at click position');
                }
            }
        } catch (error) {
            console.error('Error selecting element:', error);
            if (window.notifications) {
                window.notifications.error('Selection Error', 'Failed to select element');
            }
        }
    }
    
    /**
     * Start element selection mode
     */
    async startElementSelection() {
        try {
            const result = await window.api.startElementSelection(
                this.currentInteractiveSession.sessionId
            );
            
            if (result.success) {
                this.isSelectionModeActive = true;
                
                // Update UI
                document.getElementById('start-selection-btn').style.display = 'none';
                document.getElementById('stop-selection-btn').style.display = 'inline-block';
                
                const screenshot = document.getElementById('browser-screenshot');
                screenshot.style.cursor = 'crosshair';
                
                if (window.notifications) {
                    window.notifications.success('Selection Active', 
                        'Click on elements in the browser view to select them');
                }
            }
        } catch (error) {
            console.error('Error starting selection:', error);
            if (window.notifications) {
                window.notifications.error('Error', 'Failed to start element selection');
            }
        }
    }
    
    /**
     * Stop element selection mode
     */
    async stopElementSelection() {
        try {
            const result = await window.api.stopElementSelection(
                this.currentInteractiveSession.sessionId
            );
            
            if (result.success) {
                this.isSelectionModeActive = false;
                
                // Update UI
                document.getElementById('start-selection-btn').style.display = 'inline-block';
                document.getElementById('stop-selection-btn').style.display = 'none';
                
                const screenshot = document.getElementById('browser-screenshot');
                screenshot.style.cursor = 'default';
                
                if (window.notifications) {
                    window.notifications.info('Selection Stopped', 
                        'Element selection mode deactivated');
                }
            }
        } catch (error) {
            console.error('Error stopping selection:', error);
        }
    }
    
    /**
     * Refresh the browser screenshot
     */
    async refreshBrowserScreenshot() {
        try {
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
                loadingOverlay.textContent = 'Refreshing...';
            }
            
            const result = await window.api.getBrowserScreenshot(
                this.currentInteractiveSession.sessionId
            );
            
            if (result.success && result.screenshot) {
                const screenshot = document.getElementById('browser-screenshot');
                if (screenshot) {
                    screenshot.src = result.screenshot;
                }
            }
            
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        } catch (error) {
            console.error('Error refreshing screenshot:', error);
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
                loadingOverlay.textContent = 'Error loading screenshot';
            }
        }
    }
    
    /**
     * Load page information
     */
    async loadPageInfo() {
        try {
            const result = await window.api.getPageInfo(
                this.currentInteractiveSession.sessionId
            );
            
            if (result.success && result.info) {
                const info = result.info;
                const pageInfoDiv = document.getElementById('page-info');
                if (pageInfoDiv) {
                    pageInfoDiv.innerHTML = `
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #4CAF50;">Title:</strong><br>
                            <span style="color: #ccc;">${info.title || 'No title'}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #4CAF50;">Domain:</strong><br>
                            <span style="color: #ccc;">${info.domain || 'Unknown'}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #4CAF50;">Elements:</strong>
                            <span style="color: #81C784;">${info.elements_count || 0}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #4CAF50;">Forms:</strong>
                            <span style="color: #81C784;">${info.forms_count || 0}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #4CAF50;">Links:</strong>
                            <span style="color: #81C784;">${info.links_count || 0}</span>
                        </div>
                        <div>
                            <strong style="color: #4CAF50;">Images:</strong>
                            <span style="color: #81C784;">${info.images_count || 0}</span>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Error loading page info:', error);
        }
    }
    
    /**
     * Add selected element to the list
     */
    addSelectedElement(element) {
        if (!this.selectedElements) {
            this.selectedElements = [];
        }
        
        // Check if element already selected (by selector)
        const existingIndex = this.selectedElements.findIndex(
            el => el.css_selector === element.css_selector
        );
        
        if (existingIndex >= 0) {
            // Remove if already selected
            this.selectedElements.splice(existingIndex, 1);
        } else {
            // Add new selection
            this.selectedElements.push(element);
        }
        
        this.updateSelectedElementsList();
    }
    
    /**
     * Update the selected elements list UI
     */
    updateSelectedElementsList() {
        const listDiv = document.getElementById('selected-elements-list');
        const countSpan = document.getElementById('selected-count');
        
        if (!listDiv || !this.selectedElements) return;
        
        // Update count
        if (countSpan) {
            countSpan.textContent = `Selected: ${this.selectedElements.length}`;
        }
        
        if (this.selectedElements.length === 0) {
            listDiv.innerHTML = `
                <div style="color: #888; text-align: center; padding: 20px; font-size: 12px;">
                    No elements selected yet.<br>
                    Click "Start Selection" and then click on elements in the browser view.
                </div>
            `;
            return;
        }
        
        // Build elements list
        const elementsHTML = this.selectedElements.map((element, index) => `
            <div style="
                background: #333;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 6px;
                border-left: 3px solid #4CAF50;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 4px;
                ">
                    <span style="color: #4CAF50; font-weight: bold; font-size: 11px;">
                        ${index + 1}. ${element.tag?.toUpperCase() || 'ELEMENT'}
                    </span>
                    <button onclick="templateManager.removeSelectedElement(${index})" style="
                        background: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 2px;
                        padding: 2px 6px;
                        cursor: pointer;
                        font-size: 10px;
                    ">✕</button>
                </div>
                ${element.text ? `
                <div style="color: #ccc; font-size: 10px; margin-bottom: 4px;">
                    "${element.text.substring(0, 40)}${element.text.length > 40 ? '...' : ''}"
                </div>` : ''}
                <div style="color: #81C784; font-size: 9px; font-family: monospace;">
                    ${element.css_selector}
                </div>
            </div>
        `).join('');
        
        listDiv.innerHTML = elementsHTML;
    }
    
    /**
     * Remove selected element by index
     */
    removeSelectedElement(index) {
        if (this.selectedElements && index >= 0 && index < this.selectedElements.length) {
            this.selectedElements.splice(index, 1);
            this.updateSelectedElementsList();
        }
    }
    
    /**
     * Create template from selected elements
     */
    async createTemplateFromSelections() {
        if (!this.selectedElements || this.selectedElements.length === 0) {
            if (window.notifications) {
                window.notifications.warning('No Elements', 'Please select some elements first');
            } else {
                alert('Please select some elements first');
            }
            return;
        }
        
        // Prompt for template name
        const templateName = prompt('Enter template name:');
        if (!templateName) return;
        
        const templateDescription = prompt('Enter template description (optional):') || '';
        
        try {
            const result = await window.api.createTemplateFromSelections(
                this.currentInteractiveSession.sessionId,
                templateName,
                templateDescription
            );
            
            if (result.success) {
                if (window.notifications) {
                    window.notifications.success('Template Created', 
                        `Template "${templateName}" created successfully with ${this.selectedElements.length} elements`);
                } else {
                    alert(`Template "${templateName}" created successfully!`);
                }
                
                // Close interactive mode
                this.closePlaywrightInteractiveMode();
                
                // Refresh templates list
                await this.loadTemplates();
                
            } else {
                if (window.notifications) {
                    window.notifications.error('Creation Failed', result.error || 'Failed to create template');
                } else {
                    alert('Failed to create template: ' + (result.error || 'Unknown error'));
                }
            }
        } catch (error) {
            console.error('Error creating template:', error);
            if (window.notifications) {
                window.notifications.error('Error', 'Failed to create template');
            } else {
                alert('Error creating template: ' + error.message);
            }
        }
    }
    
    /**
     * Close Playwright interactive mode
     */
    async closePlaywrightInteractiveMode() {
        try {
            // Close session
            if (this.currentInteractiveSession) {
                await window.api.closeInteractiveSession(this.currentInteractiveSession.sessionId);
                this.currentInteractiveSession = null;
            }
            
            // Remove modal
            const modal = document.getElementById('playwright-interactive-modal');
            if (modal) {
                modal.remove();
            }
            
            // Clean up state
            this.selectedElements = [];
            this.isSelectionModeActive = false;
            
            // Remove keyboard listener
            document.removeEventListener('keydown', this.handleInteractiveKeyboard);
            
            if (window.logger) {
                window.logger.info('TemplateManager', 'Playwright interactive mode closed');
            }
            
        } catch (error) {
            console.error('Error closing interactive mode:', error);
        }
    }
    
    /**
     * Start interactive mode in new window (LEGACY - keeping for fallback)
     */
    startInteractiveModeInNewWindow(url) {
        // Create a proxy page that loads the target site's content
        const proxyUrl = `/interactive-proxy.html?url=${encodeURIComponent(url)}`;
        
        // Open our proxy page in a new window
        const newWindow = window.open(proxyUrl, 'interactive_mode', 'width=1200,height=800');
        
        if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
            // Pop-up was blocked
            if (window.notifications) {
                window.notifications.error(
                    'Pop-up Blocked',
                    'Please allow pop-ups for this site to use Interactive Mode. Click the pop-up blocker icon in your browser\'s address bar.'
                );
            } else {
                alert('Pop-up Blocked!\n\nPlease allow pop-ups for this site to use Interactive Mode.\n\nClick the pop-up blocker icon in your browser\'s address bar and select "Always allow pop-ups from this site".');
            }
            return;
        }
        
        // Listen for messages from the interactive window
        window.addEventListener('message', (event) => {
            // Verify the message is from our window
            if (event.source !== newWindow) return;
            
            if (event.data && event.data.type === 'template_created') {
                this.handleInteractiveTemplateCreated(event.data.template);
                newWindow.close();
            } else if (event.data && event.data.type === 'interactive_ready') {
                // Send the URL to analyze
                newWindow.postMessage({
                    type: 'analyze_url',
                    url: url
                }, '*');
            }
        });
    }
    
    /**
     * Handle template created from interactive mode
     */
    async handleInteractiveTemplateCreated(template) {
        if (window.logger) {
            window.logger.info('TemplateManager', 'Template created from interactive mode', template);
        }
        
        // Save template via API
        if (window.eel) {
            try {
                const result = await eel.create_template(template)();
                if (result.success) {
                    if (window.notifications) {
                        window.notifications.success('Template created successfully!');
                    }
                    // Reload templates
                    this.loadTemplates();
                } else {
                    throw new Error(result.error || 'Failed to save template');
                }
            } catch (error) {
                console.error('Failed to save template:', error);
                if (window.notifications) {
                    window.notifications.error('Failed to save template: ' + error.message);
                }
            }
        }
    }
}

// Add required CSS styles
document.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = `
        .template-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            min-width: 160px;
            display: none;
        }
        
        .template-dropdown.show {
            display: block;
        }
        
        .dropdown-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            width: 100%;
            padding: 0.5rem 0.75rem;
            border: none;
            background: none;
            text-align: left;
            cursor: pointer;
            font-size: 0.875rem;
            color: var(--text-primary);
            transition: background-color 0.2s;
        }
        
        .dropdown-item:hover {
            background: var(--background-color);
        }
        
        .dropdown-divider {
            margin: 0.25rem 0;
            border: none;
            border-top: 1px solid var(--border-color);
        }
        
        .template-menu {
            position: relative;
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
        
        .code-block {
            background: var(--background-color);
            padding: 1rem;
            border-radius: var(--radius-md);
            font-size: 0.75rem;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .meta-item.full-width {
            grid-column: 1 / -1;
        }
        
        .meta-item label {
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        
        .selectors-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .selector-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            background: var(--background-color);
            border-radius: var(--radius-md);
        }
        
        .selector-item label {
            min-width: 100px;
            font-weight: 500;
        }
        
        .selector-item code {
            flex: 1;
            padding: 0.25rem 0.5rem;
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
        }

        /* Template details configuration display */
        .template-fetcher-config {
            margin-bottom: 1.5rem;
        }

        .config-display {
            background: var(--background-color);
            padding: 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        }

        .config-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
        }

        .config-item:last-child {
            border-bottom: none;
        }

        .config-item label {
            font-weight: 500;
            color: var(--text-secondary);
        }

        .config-value {
            font-weight: 600;
            color: var(--text-primary);
        }

        /* Fetcher Configuration Styles */
        .fetcher-triggers {
            background: var(--background-color);
            padding: 1rem;
            border-radius: var(--radius-md);
            margin-bottom: 1rem;
        }

        .fetcher-triggers h5 {
            margin: 0 0 0.75rem 0;
            color: var(--text-primary);
            font-size: 0.875rem;
            font-weight: 600;
        }

        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            cursor: pointer;
            margin: 0;
        }

        .checkbox-label input[type="checkbox"] {
            margin: 0;
        }

        .checkbox-text small {
            color: var(--text-secondary);
            font-weight: normal;
        }

        .fetcher-configs {
            margin-top: 1rem;
        }

        .fetcher-config {
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .fetcher-config h5 {
            margin: 0 0 1rem 0;
            color: var(--text-primary);
            font-size: 0.875rem;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }

        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }

        .config-grid .form-group.full-width {
            grid-column: 1 / -1;
        }

        .config-grid .form-group {
            margin-bottom: 0;
        }

        .config-grid .form-group label {
            display: block;
            margin-bottom: 0.25rem;
            font-weight: 500;
            font-size: 0.875rem;
            color: var(--text-primary);
        }

        .config-grid .form-group input,
        .config-grid .form-group textarea {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            background: var(--background-color);
            color: var(--text-primary);
            font-size: 0.875rem;
        }

        .config-grid .form-group input:focus,
        .config-grid .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px var(--primary-color-alpha);
        }

        .help-text {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
            line-height: 1.3;
        }

        .checkbox-group .checkbox-label {
            margin-bottom: 0.25rem;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .config-grid {
                grid-template-columns: 1fr;
            }
            
            .fetcher-config {
                padding: 0.75rem;
            }
            
            .fetcher-triggers {
                padding: 0.75rem;
            }
        }
    `;
    document.head.appendChild(style);
});

// Make available globally
window.TemplateManager = TemplateManager;