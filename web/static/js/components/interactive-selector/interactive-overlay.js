/**
 * Interactive Overlay System for ScraperV4
 * 
 * Provides visual element selection interface for template creation
 * Features:
 * - Visual element highlighting and selection
 * - Container, Field, and Action mode buttons
 * - Real-time template building
 * - Integration with ScraperV4 template system
 */

class InteractiveOverlay {
    constructor() {
        this.state = {
            mode: 'select', // select, container, field, action
            currentContainer: null,
            containers: [],
            fields: [],
            actions: [],
            isActive: false,
            isPreviewActive: false,
            template: null,
            currentUrl: window.location.href
        };
        
        this.ui = {
            overlay: null,
            toolbar: null,
            inspector: null,
            sidebar: null,
            highlightLayer: null
        };
        
        this.selectionBuffer = {
            hoveredElement: null,
            selectedElement: null,
            candidates: []
        };
        
        this.config = {
            highlightColors: {
                hover: 'rgba(0, 123, 255, 0.3)',
                selected: 'rgba(40, 167, 69, 0.4)',
                container: 'rgba(255, 193, 7, 0.4)',
                field: 'rgba(220, 53, 69, 0.3)',
                action: 'rgba(102, 16, 242, 0.3)'
            },
            ignoredElements: ['html', 'body', 'head', 'script', 'style', 'meta', 'link', 'noscript'],
            minContainerItems: 2
        };
        
        this.eventListeners = [];
        this.originalStyles = new Map();
    }
    
    /**
     * Initialize the interactive overlay
     */
    async init() {
        if (this.state.isActive) return;
        
        this.createOverlay();
        this.createToolbar();
        this.createSidebar();
        this.createInspector();
        this.setupEventListeners();
        this.attachToWindow();
        
        this.state.isActive = true;
        this.show();
        
        console.log('🎯 Interactive Overlay initialized');
        
        // Notify backend that interactive mode started
        if (window.eel) {
            try {
                const response = await eel.start_interactive_mode(this.state.currentUrl)();
                console.log('Interactive mode started:', response);
            } catch (error) {
                console.error('Failed to start interactive mode:', error);
            }
        }
    }
    
    /**
     * Create main overlay container
     */
    createOverlay() {
        this.ui.overlay = this.createElement('div', {
            id: 'scraperv4-interactive-overlay',
            style: `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: none;
            `
        });
        
        // Create highlight layer
        this.ui.highlightLayer = this.createElement('div', {
            id: 'scraperv4-highlight-layer',
            style: `
                position: absolute;
                pointer-events: none;
                border: 2px solid #007bff;
                background: rgba(0, 123, 255, 0.1);
                transition: all 0.2s ease;
                display: none;
            `
        });
        
        this.ui.overlay.appendChild(this.ui.highlightLayer);
        document.body.appendChild(this.ui.overlay);
    }
    
    /**
     * Create toolbar with mode selection buttons
     */
    createToolbar() {
        const toolbar = this.createElement('div', {
            id: 'scraperv4-toolbar',
            style: `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 10px;
                display: flex;
                gap: 10px;
                z-index: 1000000;
                pointer-events: auto;
            `
        });
        
        // Mode buttons
        const modes = [
            { id: 'container', label: '📦 Container', color: '#ffc107' },
            { id: 'field', label: '📝 Field', color: '#dc3545' },
            { id: 'action', label: '🔗 Action', color: '#6610f2' },
            { id: 'auto', label: '🤖 Auto-detect', color: '#17a2b8' }
        ];
        
        modes.forEach(mode => {
            const btn = this.createButton(mode.label, () => this.setMode(mode.id));
            btn.style.cssText += `
                background: ${mode.id === 'auto' ? mode.color : 'white'};
                color: ${mode.id === 'auto' ? 'white' : mode.color};
                border: 2px solid ${mode.color};
            `;
            btn.dataset.mode = mode.id;
            toolbar.appendChild(btn);
        });
        
        // Separator
        toolbar.appendChild(this.createElement('div', {
            style: 'width: 1px; background: #dee2e6; margin: 0 5px;'
        }));
        
        // Action buttons
        const actions = [
            { label: '👁️ Preview', action: () => this.previewTemplate() },
            { label: '💾 Save', action: () => this.saveTemplate() },
            { label: '❌ Exit', action: () => this.destroy() }
        ];
        
        actions.forEach(({ label, action }) => {
            toolbar.appendChild(this.createButton(label, action));
        });
        
        this.ui.toolbar = toolbar;
        this.ui.overlay.appendChild(toolbar);
    }
    
    /**
     * Create sidebar for template display
     */
    createSidebar() {
        const sidebar = this.createElement('div', {
            id: 'scraperv4-sidebar',
            style: `
                position: fixed;
                right: 20px;
                top: 80px;
                width: 300px;
                max-height: 70vh;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 15px;
                overflow-y: auto;
                z-index: 1000000;
                pointer-events: auto;
            `
        });
        
        sidebar.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: #333;">Template Builder</h3>
            <div id="scraperv4-template-content">
                <p style="color: #666; font-size: 14px;">Select elements to build your template</p>
            </div>
        `;
        
        this.ui.sidebar = sidebar;
        this.ui.overlay.appendChild(sidebar);
    }
    
    /**
     * Create inspector panel for element details
     */
    createInspector() {
        const inspector = this.createElement('div', {
            id: 'scraperv4-inspector',
            style: `
                position: fixed;
                left: 20px;
                top: 80px;
                width: 280px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 15px;
                z-index: 1000000;
                pointer-events: auto;
                display: none;
            `
        });
        
        inspector.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: #333;">Element Inspector</h4>
            <div id="scraperv4-inspector-content">
                <p style="color: #666; font-size: 14px;">Hover over elements to inspect</p>
            </div>
        `;
        
        this.ui.inspector = inspector;
        this.ui.overlay.appendChild(inspector);
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Document-level mouse events
        const handleMouseMove = (e) => {
            if (!this.state.isActive) return;
            this.handleElementHover(e);
        };
        
        const handleClick = (e) => {
            if (!this.state.isActive) return;
            if (this.isOverlayElement(e.target)) return;
            
            e.preventDefault();
            e.stopPropagation();
            this.handleElementClick(e);
        };
        
        // Keyboard shortcuts
        const handleKeydown = (e) => {
            if (!this.state.isActive) return;
            
            // ESC to exit
            if (e.key === 'Escape') {
                this.destroy();
            }
            // C for container mode
            else if (e.key === 'c' || e.key === 'C') {
                this.setMode('container');
            }
            // F for field mode
            else if (e.key === 'f' || e.key === 'F') {
                this.setMode('field');
            }
            // A for action mode
            else if (e.key === 'a' || e.key === 'A') {
                this.setMode('action');
            }
        };
        
        document.addEventListener('mousemove', handleMouseMove, true);
        document.addEventListener('click', handleClick, true);
        document.addEventListener('keydown', handleKeydown, true);
        
        this.eventListeners.push(
            { type: 'mousemove', handler: handleMouseMove },
            { type: 'click', handler: handleClick },
            { type: 'keydown', handler: handleKeydown }
        );
    }
    
    /**
     * Handle element hover
     */
    handleElementHover(e) {
        const element = e.target;
        
        if (this.isOverlayElement(element)) {
            this.hideHighlight();
            return;
        }
        
        if (this.isIgnoredElement(element)) return;
        
        this.selectionBuffer.hoveredElement = element;
        this.highlightElement(element);
        this.updateInspector(element);
    }
    
    /**
     * Handle element click
     */
    async handleElementClick(e) {
        const element = e.target;
        
        if (this.isIgnoredElement(element)) return;
        
        this.selectionBuffer.selectedElement = element;
        
        switch (this.state.mode) {
            case 'container':
                await this.addContainer(element);
                break;
            case 'field':
                await this.addField(element);
                break;
            case 'action':
                await this.addAction(element);
                break;
            case 'auto':
                await this.autoDetect(element);
                break;
            default:
                await this.addField(element);
        }
        
        this.updateSidebar();
    }
    
    /**
     * Add container from selected element
     */
    async addContainer(element) {
        const selector = this.generateSelector(element);
        const similarElements = this.findSimilarElements(element);
        
        if (similarElements.length < this.config.minContainerItems) {
            this.showNotification('Not enough similar elements for a container', 'warning');
            return;
        }
        
        const container = {
            id: `container_${Date.now()}`,
            label: this.generateFieldName(element, 'container'),
            selector: selector,
            element_type: 'container',
            count: similarElements.length,
            sub_elements: []
        };
        
        this.state.containers.push(container);
        this.state.currentContainer = container;
        
        // Highlight all similar elements
        similarElements.forEach(el => {
            this.highlightElement(el, this.config.highlightColors.container);
        });
        
        this.showNotification(`Container added: ${similarElements.length} items found`, 'success');
        
        // Analyze container structure
        if (window.eel) {
            try {
                const analysis = await eel.analyze_element({
                    selector: selector,
                    html: element.outerHTML,
                    type: 'container'
                })();
                
                if (analysis.sub_fields) {
                    container.suggested_fields = analysis.sub_fields;
                }
            } catch (error) {
                console.error('Failed to analyze container:', error);
            }
        }
    }
    
    /**
     * Add field from selected element
     */
    async addField(element) {
        const selector = this.generateSelector(element);
        const fieldType = this.detectFieldType(element);
        
        const field = {
            id: `field_${Date.now()}`,
            label: this.generateFieldName(element, 'field'),
            selector: selector,
            element_type: fieldType,
            is_required: false,
            sample_text: this.extractSampleText(element)
        };
        
        // Add to current container or standalone
        if (this.state.currentContainer) {
            this.state.currentContainer.sub_elements.push(field);
        } else {
            this.state.fields.push(field);
        }
        
        this.highlightElement(element, this.config.highlightColors.field);
        this.showNotification(`Field added: ${field.label}`, 'success');
        
        // Validate selector with backend
        if (window.eel) {
            try {
                const validation = await eel.test_selector_live(selector, this.state.currentUrl)();
                if (!validation.valid) {
                    this.showNotification('Selector may not be reliable', 'warning');
                }
            } catch (error) {
                console.error('Failed to validate selector:', error);
            }
        }
    }
    
    /**
     * Add action element
     */
    async addAction(element) {
        const selector = this.generateSelector(element);
        const actionType = this.detectActionType(element);
        
        const action = {
            id: `action_${Date.now()}`,
            label: this.generateFieldName(element, 'action'),
            selector: selector,
            action_type: actionType,
            element_type: 'action'
        };
        
        this.state.actions.push(action);
        this.highlightElement(element, this.config.highlightColors.action);
        this.showNotification(`Action added: ${action.label}`, 'success');
        
        // Check if it's a detail page link
        if (actionType === 'link' && element.href) {
            const shouldAnalyze = confirm('This looks like a detail page link. Analyze the target page?');
            if (shouldAnalyze) {
                await this.analyzeDetailPage(element.href, action);
            }
        }
    }
    
    /**
     * Auto-detect elements on the page
     */
    async autoDetect(element) {
        this.showNotification('Running auto-detection...', 'info');
        
        // Load auto-detector if not already loaded
        if (!window.AutoDetector) {
            const script = document.createElement('script');
            script.src = '/static/js/components/interactive-selector/auto-detector.js';
            document.head.appendChild(script);
            
            await new Promise(resolve => {
                script.onload = resolve;
                script.onerror = () => {
                    this.showNotification('Failed to load auto-detector', 'error');
                    resolve();
                };
            });
        }
        
        if (window.AutoDetector) {
            const detector = new AutoDetector();
            const results = await detector.detectPatterns(document.body);
            
            if (results.containers.length > 0 || results.fields.length > 0) {
                this.showDetectionResults(results);
                this.showNotification(`Detected ${results.siteType} site with ${results.containers.length} containers and ${results.fields.length} fields`, 'success');
            } else {
                this.showNotification('No patterns detected', 'warning');
            }
        }
    }
    
    /**
     * Show detection results and allow user to apply them
     */
    showDetectionResults(results) {
        // Create results modal
        const modal = this.createElement('div', {
            style: `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                padding: 20px;
                max-width: 600px;
                max-height: 70vh;
                overflow-y: auto;
                z-index: 1000002;
            `
        });
        
        let html = `
            <h3 style="margin: 0 0 15px 0;">Auto-Detection Results</h3>
            <p style="color: #666;">Site Type: <strong>${results.siteType}</strong> (${Math.round(results.confidence * 100)}% confidence)</p>
        `;
        
        if (results.suggestions && results.suggestions.length > 0) {
            html += '<h4>Suggestions:</h4>';
            html += '<div style="max-height: 300px; overflow-y: auto;">';
            
            results.suggestions.forEach((suggestion, index) => {
                html += `
                    <div style="padding: 10px; margin-bottom: 10px; background: #f8f9fa; border-radius: 4px;">
                        <input type="checkbox" id="suggestion_${index}" checked style="margin-right: 10px;">
                        <label for="suggestion_${index}" style="cursor: pointer;">
                            <strong>${suggestion.type}:</strong> ${suggestion.message}
                            <br><small style="color: #666;">Confidence: ${Math.round(suggestion.confidence * 100)}%</small>
                        </label>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        html += `
            <div style="margin-top: 20px; text-align: right;">
                <button id="apply-suggestions" style="padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; margin-right: 10px; cursor: pointer;">
                    Apply Selected
                </button>
                <button id="cancel-suggestions" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Cancel
                </button>
            </div>
        `;
        
        modal.innerHTML = html;
        this.ui.overlay.appendChild(modal);
        
        // Add event handlers
        document.getElementById('apply-suggestions').onclick = () => {
            this.applySelectedSuggestions(results.suggestions);
            modal.remove();
        };
        
        document.getElementById('cancel-suggestions').onclick = () => {
            modal.remove();
        };
    }
    
    /**
     * Apply selected suggestions
     */
    applySelectedSuggestions(suggestions) {
        suggestions.forEach((suggestion, index) => {
            const checkbox = document.getElementById(`suggestion_${index}`);
            if (checkbox && checkbox.checked) {
                if (suggestion.action === 'add_container' && suggestion.selector) {
                    const elements = document.querySelectorAll(suggestion.selector);
                    if (elements.length > 0) {
                        this.addContainer(elements[0]);
                    }
                } else if (suggestion.action === 'add_field' && suggestion.selector) {
                    const element = document.querySelector(suggestion.selector);
                    if (element) {
                        // Set the field type based on detection
                        const originalType = this.detectFieldType(element);
                        this.detectFieldType = () => suggestion.fieldType || originalType;
                        this.addField(element);
                        this.detectFieldType = this.constructor.prototype.detectFieldType;
                    }
                }
            }
        });
        
        this.updateSidebar();
    }
    
    /**
     * Generate CSS selector for element
     */
    generateSelector(element) {
        const path = [];
        let current = element;
        
        while (current && current !== document.body) {
            let selector = current.tagName.toLowerCase();
            
            // Add ID if available
            if (current.id) {
                selector = `#${current.id}`;
                path.unshift(selector);
                break;
            }
            
            // Add classes
            if (current.className && typeof current.className === 'string') {
                const classes = current.className.trim().split(/\s+/)
                    .filter(c => c && !c.startsWith('scraperv4-'));
                if (classes.length > 0) {
                    selector += '.' + classes.join('.');
                }
            }
            
            // Add nth-child if needed
            if (current.parentElement) {
                const siblings = Array.from(current.parentElement.children);
                const index = siblings.indexOf(current);
                if (siblings.filter(s => s.tagName === current.tagName).length > 1) {
                    selector += `:nth-child(${index + 1})`;
                }
            }
            
            path.unshift(selector);
            current = current.parentElement;
        }
        
        return path.join(' > ');
    }
    
    /**
     * Find similar elements to create containers
     */
    findSimilarElements(element) {
        const selector = this.generateContainerSelector(element);
        const allElements = document.querySelectorAll(selector);
        
        return Array.from(allElements).filter(el => {
            return this.calculateSimilarity(element, el) > 0.8;
        });
    }
    
    /**
     * Generate container selector (less specific)
     */
    generateContainerSelector(element) {
        let selector = element.tagName.toLowerCase();
        
        // Use primary class if available
        if (element.className && typeof element.className === 'string') {
            const classes = element.className.trim().split(/\s+/)
                .filter(c => c && !c.startsWith('scraperv4-'));
            if (classes.length > 0) {
                selector += '.' + classes[0];
            }
        }
        
        // Check parent for container context
        if (element.parentElement) {
            const parentClass = element.parentElement.className;
            if (parentClass && parentClass.includes('list') || parentClass.includes('grid') || parentClass.includes('container')) {
                selector = element.parentElement.tagName.toLowerCase() + ' > ' + selector;
            }
        }
        
        return selector;
    }
    
    /**
     * Calculate similarity between two elements
     */
    calculateSimilarity(element1, element2) {
        let score = 0;
        let factors = 0;
        
        // Tag name match
        if (element1.tagName === element2.tagName) {
            score += 0.3;
        }
        factors += 0.3;
        
        // Class similarity
        const classes1 = new Set(element1.className.split(/\s+/).filter(c => c));
        const classes2 = new Set(element2.className.split(/\s+/).filter(c => c));
        const classIntersection = new Set([...classes1].filter(c => classes2.has(c)));
        const classUnion = new Set([...classes1, ...classes2]);
        
        if (classUnion.size > 0) {
            score += (classIntersection.size / classUnion.size) * 0.3;
        }
        factors += 0.3;
        
        // Structure similarity
        if (element1.children.length === element2.children.length) {
            score += 0.2;
        }
        factors += 0.2;
        
        // Parent similarity
        if (element1.parentElement && element2.parentElement &&
            element1.parentElement.tagName === element2.parentElement.tagName) {
            score += 0.2;
        }
        factors += 0.2;
        
        return factors > 0 ? score / factors : 0;
    }
    
    /**
     * Detect field type from element
     */
    detectFieldType(element) {
        const text = element.textContent.toLowerCase();
        const tagName = element.tagName.toLowerCase();
        
        // Check for specific types
        if (element.href) return 'link';
        if (tagName === 'img') return 'image';
        if (text.match(/\$[\d,]+\.?\d*/) || text.match(/[\d,]+\.?\d*\s*(usd|eur|gbp)/i)) return 'price';
        if (text.match(/\b\d{4}-\d{2}-\d{2}\b/) || text.match(/\b\d{1,2}\/\d{1,2}\/\d{4}\b/)) return 'date';
        if (text.match(/[\w.-]+@[\w.-]+\.\w+/)) return 'email';
        if (text.match(/\+?\d[\d\s()-]+\d/)) return 'phone';
        
        return 'text';
    }
    
    /**
     * Detect action type from element
     */
    detectActionType(element) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.toLowerCase();
        
        if (tagName === 'a') return 'link';
        if (tagName === 'button') return 'button';
        if (text.includes('next') || text.includes('load more')) return 'pagination';
        if (element.onclick || element.getAttribute('onclick')) return 'button';
        
        return 'link';
    }
    
    /**
     * Generate field name from element
     */
    generateFieldName(element, type) {
        const text = element.textContent.trim().substring(0, 30);
        const className = element.className.split(/\s+/)[0] || '';
        const tagName = element.tagName.toLowerCase();
        
        if (text && text.length < 20) {
            return text.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
        } else if (className) {
            return className.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
        } else {
            return `${type}_${tagName}_${Date.now()}`;
        }
    }
    
    /**
     * Extract sample text from element
     */
    extractSampleText(element) {
        if (element.tagName === 'IMG') {
            return element.src || element.alt || '';
        }
        return element.textContent.trim().substring(0, 100);
    }
    
    /**
     * Highlight element
     */
    highlightElement(element, color = null) {
        const rect = element.getBoundingClientRect();
        const highlightColor = color || this.config.highlightColors.hover;
        
        this.ui.highlightLayer.style.cssText = `
            position: fixed;
            left: ${rect.left}px;
            top: ${rect.top}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            background: ${highlightColor};
            border: 2px solid ${highlightColor.replace('0.3', '1').replace('0.4', '1')};
            pointer-events: none;
            z-index: 999998;
            display: block;
        `;
    }
    
    /**
     * Hide highlight
     */
    hideHighlight() {
        this.ui.highlightLayer.style.display = 'none';
    }
    
    /**
     * Update inspector with element details
     */
    updateInspector(element) {
        const content = document.getElementById('scraperv4-inspector-content');
        if (!content) return;
        
        const selector = this.generateSelector(element);
        const fieldType = this.detectFieldType(element);
        
        content.innerHTML = `
            <div style="font-size: 13px; color: #333;">
                <p><strong>Tag:</strong> ${element.tagName.toLowerCase()}</p>
                <p><strong>Type:</strong> ${fieldType}</p>
                <p><strong>Classes:</strong> ${element.className || 'none'}</p>
                <p><strong>ID:</strong> ${element.id || 'none'}</p>
                <p><strong>Selector:</strong></p>
                <code style="display: block; padding: 5px; background: #f8f9fa; border-radius: 3px; font-size: 11px; word-break: break-all;">
                    ${selector}
                </code>
                <p><strong>Sample:</strong> ${this.extractSampleText(element).substring(0, 50)}...</p>
            </div>
        `;
        
        this.ui.inspector.style.display = 'block';
    }
    
    /**
     * Update sidebar with template content
     */
    updateSidebar() {
        const content = document.getElementById('scraperv4-template-content');
        if (!content) return;
        
        let html = '';
        
        // Containers
        if (this.state.containers.length > 0) {
            html += '<h4 style="color: #ffc107;">📦 Containers</h4>';
            this.state.containers.forEach(container => {
                html += `
                    <div style="margin-bottom: 10px; padding: 8px; background: #fff3cd; border-radius: 4px;">
                        <strong>${container.label}</strong> (${container.count} items)
                        ${container.sub_elements.length > 0 ? 
                            `<ul style="margin: 5px 0; padding-left: 20px; font-size: 13px;">
                                ${container.sub_elements.map(f => `<li>${f.label}</li>`).join('')}
                            </ul>` : ''}
                    </div>
                `;
            });
        }
        
        // Fields
        if (this.state.fields.length > 0) {
            html += '<h4 style="color: #dc3545;">📝 Fields</h4>';
            this.state.fields.forEach(field => {
                html += `
                    <div style="margin-bottom: 8px; padding: 6px; background: #f8d7da; border-radius: 4px;">
                        ${field.label} (${field.element_type})
                    </div>
                `;
            });
        }
        
        // Actions
        if (this.state.actions.length > 0) {
            html += '<h4 style="color: #6610f2;">🔗 Actions</h4>';
            this.state.actions.forEach(action => {
                html += `
                    <div style="margin-bottom: 8px; padding: 6px; background: #e7d6f8; border-radius: 4px;">
                        ${action.label} (${action.action_type})
                    </div>
                `;
            });
        }
        
        content.innerHTML = html || '<p style="color: #666; font-size: 14px;">No elements selected yet</p>';
    }
    
    /**
     * Build template from selections
     */
    buildTemplate() {
        const template = {
            name: `template_${Date.now()}`,
            description: 'Template created with Interactive Selector',
            version: '1.0.0',
            selectors: {},
            fetcher_config: {
                type: 'auto'
            },
            validation_rules: {
                required_fields: []
            },
            post_processing: []
        };
        
        // Add standalone fields
        this.state.fields.forEach(field => {
            template.selectors[field.label] = {
                selector: field.selector,
                type: 'text',
                auto_save: true,
                required: field.is_required
            };
            
            if (field.is_required) {
                template.validation_rules.required_fields.push(field.label);
            }
        });
        
        // Add container fields
        this.state.containers.forEach(container => {
            template.selectors[container.label] = {
                selector: container.selector,
                type: 'all',
                auto_save: true,
                sub_elements: {}
            };
            
            container.sub_elements.forEach(subField => {
                template.selectors[container.label].sub_elements[subField.label] = {
                    selector: subField.selector,
                    type: 'text',
                    auto_save: true
                };
            });
        });
        
        // Add pagination if action exists
        const paginationAction = this.state.actions.find(a => a.action_type === 'pagination');
        if (paginationAction) {
            template.pagination = {
                enabled: true,
                next_selector: paginationAction.selector,
                max_pages: 10
            };
        }
        
        this.state.template = template;
        return template;
    }
    
    /**
     * Preview template
     */
    async previewTemplate() {
        const template = this.buildTemplate();
        
        if (Object.keys(template.selectors).length === 0) {
            this.showNotification('No elements selected for preview', 'warning');
            return;
        }
        
        this.showNotification('Testing template...', 'info');
        
        if (window.eel) {
            try {
                const result = await eel.test_selector_live(JSON.stringify(template.selectors), this.state.currentUrl)();
                
                if (result.success) {
                    this.showPreviewModal(result.data);
                } else {
                    this.showNotification('Preview failed: ' + result.error, 'error');
                }
            } catch (error) {
                console.error('Preview error:', error);
                this.showNotification('Preview failed', 'error');
            }
        }
    }
    
    /**
     * Save template
     */
    async saveTemplate() {
        const template = this.buildTemplate();
        
        if (Object.keys(template.selectors).length === 0) {
            this.showNotification('No elements selected to save', 'warning');
            return;
        }
        
        const name = prompt('Enter template name:', template.name);
        if (!name) return;
        
        template.name = name;
        template.description = prompt('Enter template description:', template.description) || template.description;
        
        if (window.eel) {
            try {
                const result = await eel.save_interactive_template(template)();
                
                if (result.success) {
                    this.showNotification('Template saved successfully!', 'success');
                    setTimeout(() => this.destroy(), 2000);
                } else {
                    this.showNotification('Failed to save template: ' + result.error, 'error');
                }
            } catch (error) {
                console.error('Save error:', error);
                this.showNotification('Failed to save template', 'error');
            }
        }
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = this.createElement('div', {
            style: `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 12px 24px;
                background: ${type === 'success' ? '#28a745' : 
                             type === 'error' ? '#dc3545' : 
                             type === 'warning' ? '#ffc107' : '#17a2b8'};
                color: white;
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                z-index: 1000001;
                animation: slideUp 0.3s ease;
            `
        });
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    /**
     * Set selection mode
     */
    setMode(mode) {
        this.state.mode = mode;
        
        // Update toolbar buttons
        document.querySelectorAll('#scraperv4-toolbar button[data-mode]').forEach(btn => {
            const btnMode = btn.dataset.mode;
            if (btnMode === mode) {
                btn.style.background = btn.style.borderColor;
                btn.style.color = 'white';
            } else {
                btn.style.background = 'white';
                btn.style.color = btn.style.borderColor;
            }
        });
        
        if (mode === 'auto') {
            this.autoDetect();
        }
    }
    
    /**
     * Check if element is part of overlay
     */
    isOverlayElement(element) {
        return element.id && element.id.startsWith('scraperv4-');
    }
    
    /**
     * Check if element should be ignored
     */
    isIgnoredElement(element) {
        return this.config.ignoredElements.includes(element.tagName.toLowerCase());
    }
    
    /**
     * Show overlay
     */
    show() {
        this.ui.overlay.style.display = 'block';
        document.body.style.cursor = 'crosshair';
    }
    
    /**
     * Hide overlay
     */
    hide() {
        this.ui.overlay.style.display = 'none';
        document.body.style.cursor = '';
    }
    
    /**
     * Attach to window for global access
     */
    attachToWindow() {
        window.InteractiveOverlay = this;
        window.scraperv4Interactive = this;
    }
    
    /**
     * Create element helper
     */
    createElement(tag, attributes = {}) {
        const element = document.createElement(tag);
        
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'style') {
                element.style.cssText = value;
            } else {
                element.setAttribute(key, value);
            }
        }
        
        return element;
    }
    
    /**
     * Create button helper
     */
    createButton(label, onClick) {
        const button = this.createElement('button', {
            style: `
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
            `
        });
        
        button.textContent = label;
        button.onclick = onClick;
        
        button.onmouseenter = () => {
            button.style.transform = 'translateY(-1px)';
            button.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        };
        
        button.onmouseleave = () => {
            button.style.transform = '';
            button.style.boxShadow = '';
        };
        
        return button;
    }
    
    /**
     * Destroy overlay and cleanup
     */
    destroy() {
        // Remove event listeners
        this.eventListeners.forEach(({ type, handler }) => {
            document.removeEventListener(type, handler, true);
        });
        
        // Remove UI elements
        if (this.ui.overlay) {
            this.ui.overlay.remove();
        }
        
        // Reset cursor
        document.body.style.cursor = '';
        
        // Clear state
        this.state.isActive = false;
        
        // Remove from window
        delete window.InteractiveOverlay;
        delete window.scraperv4Interactive;
        
        console.log('Interactive overlay destroyed');
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            transform: translate(-50%, 20px);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
    
    @keyframes slideDown {
        from {
            transform: translate(-50%, 0);
            opacity: 1;
        }
        to {
            transform: translate(-50%, 20px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on demand
window.startInteractiveSelector = function() {
    const overlay = new InteractiveOverlay();
    overlay.init();
    return overlay;
};