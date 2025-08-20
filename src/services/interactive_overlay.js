/**
 * ScraperV4 Interactive Mode Overlay
 * 
 * This script provides visual element selection capabilities for template creation.
 * It creates an overlay that allows users to hover and click on elements to select them
 * for CSS selector generation and template building.
 */

(function() {
    'use strict';
    
    // Prevent multiple initialization
    if (window.scraperV4Interactive) {
        console.warn('ScraperV4 Interactive Mode already initialized');
        return;
    }
    
    // Main interactive object
    window.scraperV4Interactive = {
        // State management
        isSelecting: false,
        selectedElements: [],
        currentTarget: null,
        selectionMode: 'single', // 'single' or 'multiple'
        
        // DOM elements
        overlay: null,
        highlight: null,
        infoBox: null,
        toolbar: null,
        
        // Configuration
        config: {
            highlightColor: '#007bff',
            selectedColor: '#28a745',
            highlightOpacity: 0.1,
            zIndex: 999999,
            infoBoxPosition: 'top-right'
        },
        
        /**
         * Initialize the interactive overlay system
         */
        init: function() {
            console.log('ScraperV4 Interactive Mode: Initializing...');
            
            this.createOverlay();
            this.createHighlight();
            this.createInfoBox();
            this.createToolbar();
            this.bindEvents();
            this.setupKeyboardShortcuts();
            
            console.log('ScraperV4 Interactive Mode: Ready');
            this.showWelcomeMessage();
        },
        
        /**
         * Create the main overlay container
         */
        createOverlay: function() {
            this.overlay = document.createElement('div');
            this.overlay.id = 'scraperv4-overlay';
            this.overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: ${this.config.zIndex};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;
            document.body.appendChild(this.overlay);
        },
        
        /**
         * Create the element highlight box
         */
        createHighlight: function() {
            this.highlight = document.createElement('div');
            this.highlight.id = 'scraperv4-highlight';
            this.highlight.style.cssText = `
                position: absolute;
                border: 2px solid ${this.config.highlightColor};
                background: ${this.config.highlightColor}${Math.round(this.config.highlightOpacity * 255).toString(16).padStart(2, '0')};
                pointer-events: none;
                z-index: ${this.config.zIndex + 1};
                display: none;
                transition: all 0.1s ease;
                box-shadow: 0 0 10px rgba(0, 123, 255, 0.3);
            `;
            document.body.appendChild(this.highlight);
        },
        
        /**
         * Create the information display box
         */
        createInfoBox: function() {
            this.infoBox = document.createElement('div');
            this.infoBox.id = 'scraperv4-info';
            this.infoBox.style.cssText = `
                position: fixed;
                ${this.config.infoBoxPosition.includes('top') ? 'top: 10px;' : 'bottom: 10px;'}
                ${this.config.infoBoxPosition.includes('right') ? 'right: 10px;' : 'left: 10px;'}
                background: rgba(33, 33, 33, 0.95);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 11px;
                z-index: ${this.config.zIndex + 2};
                max-width: 350px;
                min-width: 200px;
                word-wrap: break-word;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                display: none;
            `;
            
            this.infoBox.innerHTML = `
                <div style="margin-bottom: 8px; font-weight: bold; color: #4CAF50;">
                    🎯 ScraperV4 Interactive Mode
                </div>
                <div style="color: #ccc;">
                    Hover over elements to inspect<br>
                    Click to select elements for template
                </div>
            `;
            document.body.appendChild(this.infoBox);
        },
        
        /**
         * Create the toolbar with controls
         */
        createToolbar: function() {
            this.toolbar = document.createElement('div');
            this.toolbar.id = 'scraperv4-toolbar';
            this.toolbar.style.cssText = `
                position: fixed;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(33, 33, 33, 0.95);
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 12px;
                z-index: ${this.config.zIndex + 3};
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                display: none;
                pointer-events: auto;
            `;
            
            this.toolbar.innerHTML = `
                <div style="display: flex; align-items: center; gap: 15px;">
                    <button id="scraperv4-start-btn" style="
                        background: #4CAF50;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 15px;
                        cursor: pointer;
                        font-size: 11px;
                        font-weight: 500;
                    ">▶ Start Selecting</button>
                    
                    <button id="scraperv4-stop-btn" style="
                        background: #f44336;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 15px;
                        cursor: pointer;
                        font-size: 11px;
                        font-weight: 500;
                        display: none;
                    ">⏹ Stop</button>
                    
                    <span id="scraperv4-selected-count" style="
                        color: #4CAF50;
                        font-weight: 500;
                    ">Selected: 0</span>
                    
                    <button id="scraperv4-clear-btn" style="
                        background: #ff9800;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 15px;
                        cursor: pointer;
                        font-size: 11px;
                        font-weight: 500;
                    ">🗑 Clear</button>
                    
                    <button id="scraperv4-export-btn" style="
                        background: #2196F3;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 15px;
                        cursor: pointer;
                        font-size: 11px;
                        font-weight: 500;
                    ">📁 Export</button>
                    
                    <button id="scraperv4-close-btn" style="
                        background: transparent;
                        color: #ccc;
                        border: none;
                        padding: 6px 8px;
                        border-radius: 15px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                    ">✕</button>
                </div>
            `;
            
            document.body.appendChild(this.toolbar);
            
            // Bind toolbar events
            this.bindToolbarEvents();
        },
        
        /**
         * Bind toolbar button events
         */
        bindToolbarEvents: function() {
            document.getElementById('scraperv4-start-btn').addEventListener('click', () => {
                this.startSelecting();
            });
            
            document.getElementById('scraperv4-stop-btn').addEventListener('click', () => {
                this.stopSelecting();
            });
            
            document.getElementById('scraperv4-clear-btn').addEventListener('click', () => {
                this.clearSelections();
            });
            
            document.getElementById('scraperv4-export-btn').addEventListener('click', () => {
                this.exportSelections();
            });
            
            document.getElementById('scraperv4-close-btn').addEventListener('click', () => {
                this.cleanup();
            });
        },
        
        /**
         * Bind mouse and keyboard events
         */
        bindEvents: function() {
            // Mouse events for element selection
            document.addEventListener('mouseover', this.handleMouseOver.bind(this), true);
            document.addEventListener('mouseout', this.handleMouseOut.bind(this), true);
            document.addEventListener('click', this.handleClick.bind(this), true);
            
            // Prevent context menu during selection
            document.addEventListener('contextmenu', this.handleContextMenu.bind(this), true);
        },
        
        /**
         * Setup keyboard shortcuts
         */
        setupKeyboardShortcuts: function() {
            document.addEventListener('keydown', (e) => {
                // Escape key - stop selection
                if (e.key === 'Escape') {
                    e.preventDefault();
                    this.stopSelecting();
                }
                
                // Space key - toggle selection mode
                if (e.key === ' ' && e.ctrlKey) {
                    e.preventDefault();
                    if (this.isSelecting) {
                        this.stopSelecting();
                    } else {
                        this.startSelecting();
                    }
                }
                
                // Delete key - clear selections
                if (e.key === 'Delete' && e.ctrlKey) {
                    e.preventDefault();
                    this.clearSelections();
                }
                
                // Enter key - export selections
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.exportSelections();
                }
            });
        },
        
        /**
         * Handle mouse over events
         */
        handleMouseOver: function(e) {
            if (!this.isSelecting) return;
            
            const target = e.target;
            
            // Ignore our own elements
            if (this.isOwnElement(target)) return;
            
            this.currentTarget = target;
            this.highlightElement(target);
            this.updateInfoBox(target);
        },
        
        /**
         * Handle mouse out events
         */
        handleMouseOut: function(e) {
            if (!this.isSelecting) return;
            
            const target = e.target;
            if (this.isOwnElement(target)) return;
            
            this.hideHighlight();
        },
        
        /**
         * Handle click events
         */
        handleClick: function(e) {
            if (!this.isSelecting) return;
            
            const target = e.target;
            
            // Ignore our own elements
            if (this.isOwnElement(target)) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            this.selectElement(target);
        },
        
        /**
         * Handle context menu (right-click)
         */
        handleContextMenu: function(e) {
            if (!this.isSelecting) return;
            
            const target = e.target;
            if (this.isOwnElement(target)) return;
            
            e.preventDefault();
            
            // Show context menu for element (future enhancement)
            this.showElementContextMenu(target, e.clientX, e.clientY);
        },
        
        /**
         * Check if element belongs to our overlay system
         */
        isOwnElement: function(element) {
            if (!element || !element.id) return false;
            return element.id.startsWith('scraperv4-') || 
                   element.closest('#scraperv4-overlay') ||
                   element.closest('#scraperv4-toolbar') ||
                   element.closest('#scraperv4-info');
        },
        
        /**
         * Highlight an element visually
         */
        highlightElement: function(element) {
            const rect = element.getBoundingClientRect();
            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
            
            this.highlight.style.display = 'block';
            this.highlight.style.left = (rect.left + scrollX) + 'px';
            this.highlight.style.top = (rect.top + scrollY) + 'px';
            this.highlight.style.width = rect.width + 'px';
            this.highlight.style.height = rect.height + 'px';
        },
        
        /**
         * Hide the highlight
         */
        hideHighlight: function() {
            this.highlight.style.display = 'none';
        },
        
        /**
         * Update the information box with element details
         */
        updateInfoBox: function(element) {
            const elementInfo = this.analyzeElement(element);
            
            this.infoBox.innerHTML = `
                <div style="margin-bottom: 8px; font-weight: bold; color: #4CAF50;">
                    🎯 Element Inspector
                </div>
                <div style="margin-bottom: 6px;">
                    <strong style="color: #ffeb3b;">Tag:</strong> 
                    <span style="color: #4CAF50;">&lt;${elementInfo.tag}&gt;</span>
                </div>
                ${elementInfo.id ? `
                <div style="margin-bottom: 6px;">
                    <strong style="color: #ffeb3b;">ID:</strong> 
                    <span style="color: #81C784;">#${elementInfo.id}</span>
                </div>` : ''}
                ${elementInfo.classes.length > 0 ? `
                <div style="margin-bottom: 6px;">
                    <strong style="color: #ffeb3b;">Classes:</strong> 
                    <span style="color: #81C784;">.${elementInfo.classes.join('.')}</span>
                </div>` : ''}
                ${elementInfo.text ? `
                <div style="margin-bottom: 6px;">
                    <strong style="color: #ffeb3b;">Text:</strong> 
                    <span style="color: #B39DDB;">"${elementInfo.text}"</span>
                </div>` : ''}
                <div style="margin-bottom: 8px;">
                    <strong style="color: #ffeb3b;">CSS Selector:</strong><br>
                    <code style="color: #FF7043; font-size: 10px; word-break: break-all;">
                        ${elementInfo.selector}
                    </code>
                </div>
                <div style="color: #4CAF50; font-size: 10px;">
                    💡 Click to select this element
                </div>
            `;
            
            this.infoBox.style.display = 'block';
        },
        
        /**
         * Analyze an element and extract useful information
         */
        analyzeElement: function(element) {
            return {
                tag: element.tagName.toLowerCase(),
                id: element.id || null,
                classes: element.className ? 
                    element.className.split(' ').filter(c => c.trim()) : [],
                text: element.textContent ? 
                    element.textContent.trim().substring(0, 50) + 
                    (element.textContent.trim().length > 50 ? '...' : '') : '',
                selector: this.generateOptimalSelector(element),
                xpath: this.generateXPath(element),
                attributes: this.getElementAttributes(element),
                position: element.getBoundingClientRect()
            };
        },
        
        /**
         * Get all attributes of an element
         */
        getElementAttributes: function(element) {
            const attrs = {};
            if (element.attributes) {
                for (let attr of element.attributes) {
                    attrs[attr.name] = attr.value;
                }
            }
            return attrs;
        },
        
        /**
         * Select an element for template creation
         */
        selectElement: function(element) {
            const elementData = this.analyzeElement(element);
            
            // Add selection metadata
            elementData.selected_at = new Date().toISOString();
            elementData.selection_order = this.selectedElements.length + 1;
            
            // Check if already selected
            const existingIndex = this.selectedElements.findIndex(
                el => el.selector === elementData.selector
            );
            
            if (existingIndex >= 0) {
                // Remove if already selected
                this.selectedElements.splice(existingIndex, 1);
                this.removeElementHighlight(element);
                this.showNotification('Element deselected', 'info');
            } else {
                // Add to selection
                this.selectedElements.push(elementData);
                this.addElementHighlight(element);
                this.showNotification('Element selected', 'success');
            }
            
            this.updateSelectedCount();
            this.sendToBackend('element_selected', elementData);
            
            console.log('Selected elements:', this.selectedElements);
        },
        
        /**
         * Add permanent highlight to selected element
         */
        addElementHighlight: function(element) {
            element.style.outline = `3px solid ${this.config.selectedColor}`;
            element.style.outlineOffset = '1px';
            element.setAttribute('data-scraperv4-selected', 'true');
        },
        
        /**
         * Remove permanent highlight from element
         */
        removeElementHighlight: function(element) {
            element.style.outline = '';
            element.style.outlineOffset = '';
            element.removeAttribute('data-scraperv4-selected');
        },
        
        /**
         * Generate an optimal CSS selector for the element
         */
        generateOptimalSelector: function(element) {
            // Strategy 1: Use ID if unique
            if (element.id) {
                const testSelector = `#${element.id}`;
                if (document.querySelectorAll(testSelector).length === 1) {
                    return testSelector;
                }
            }
            
            // Strategy 2: Use class combination if unique
            if (element.className) {
                const classes = element.className.split(' ').filter(c => c.trim());
                if (classes.length > 0) {
                    const classSelector = `.${classes.join('.')}`;
                    if (document.querySelectorAll(classSelector).length === 1) {
                        return classSelector;
                    }
                }
            }
            
            // Strategy 3: Build path from unique parent
            let current = element;
            let path = [];
            
            while (current && current !== document.body) {
                let selector = current.tagName.toLowerCase();
                
                // Add ID if present
                if (current.id) {
                    selector += `#${current.id}`;
                    path.unshift(selector);
                    break;
                }
                
                // Add classes if present
                if (current.className) {
                    const classes = current.className.split(' ')
                        .filter(c => c.trim())
                        .slice(0, 3); // Limit to first 3 classes
                    if (classes.length > 0) {
                        selector += `.${classes.join('.')}`;
                    }
                }
                
                // Add nth-child if needed for uniqueness
                const parent = current.parentElement;
                if (parent) {
                    const siblings = Array.from(parent.children)
                        .filter(s => s.tagName === current.tagName);
                    if (siblings.length > 1) {
                        const index = siblings.indexOf(current) + 1;
                        selector += `:nth-child(${index})`;
                    }
                }
                
                path.unshift(selector);
                current = current.parentElement;
                
                // Test if current path is unique
                const testSelector = path.join(' > ');
                if (document.querySelectorAll(testSelector).length === 1) {
                    return testSelector;
                }
            }
            
            return path.join(' > ') || 'unknown';
        },
        
        /**
         * Generate XPath for element
         */
        generateXPath: function(element) {
            if (element.id) {
                return `//*[@id="${element.id}"]`;
            }
            
            let path = '';
            let current = element;
            
            while (current && current.nodeType === Node.ELEMENT_NODE) {
                let name = current.nodeName.toLowerCase();
                let index = 1;
                
                // Count preceding siblings with same tag name
                let sibling = current.previousElementSibling;
                while (sibling) {
                    if (sibling.nodeName.toLowerCase() === name) {
                        index++;
                    }
                    sibling = sibling.previousElementSibling;
                }
                
                path = `/${name}[${index}]${path}`;
                current = current.parentElement;
            }
            
            return path;
        },
        
        /**
         * Start element selection mode
         */
        startSelecting: function() {
            this.isSelecting = true;
            document.body.style.cursor = 'crosshair';
            
            // Update toolbar
            document.getElementById('scraperv4-start-btn').style.display = 'none';
            document.getElementById('scraperv4-stop-btn').style.display = 'inline-block';
            
            this.toolbar.style.display = 'block';
            this.infoBox.style.display = 'block';
            
            this.showNotification('Selection mode activated', 'success');
            console.log('ScraperV4: Selection mode started');
        },
        
        /**
         * Stop element selection mode
         */
        stopSelecting: function() {
            this.isSelecting = false;
            document.body.style.cursor = '';
            
            // Update toolbar
            document.getElementById('scraperv4-start-btn').style.display = 'inline-block';
            document.getElementById('scraperv4-stop-btn').style.display = 'none';
            
            this.hideHighlight();
            this.infoBox.style.display = 'none';
            
            this.showNotification('Selection mode deactivated', 'info');
            console.log('ScraperV4: Selection mode stopped');
        },
        
        /**
         * Clear all selections
         */
        clearSelections: function() {
            // Remove highlights from all selected elements
            document.querySelectorAll('[data-scraperv4-selected]').forEach(el => {
                this.removeElementHighlight(el);
            });
            
            this.selectedElements = [];
            this.updateSelectedCount();
            this.showNotification('All selections cleared', 'info');
            console.log('ScraperV4: Selections cleared');
        },
        
        /**
         * Export selected elements
         */
        exportSelections: function() {
            if (this.selectedElements.length === 0) {
                this.showNotification('No elements selected', 'warning');
                return;
            }
            
            const exportData = {
                timestamp: new Date().toISOString(),
                url: window.location.href,
                domain: window.location.hostname,
                selections: this.selectedElements
            };
            
            // Send to backend
            this.sendToBackend('export_selections', exportData);
            
            // Also create downloadable JSON for backup
            this.downloadJSON(exportData, `scraperv4-selections-${Date.now()}.json`);
            
            this.showNotification(`Exported ${this.selectedElements.length} selections`, 'success');
            console.log('ScraperV4: Selections exported', exportData);
        },
        
        /**
         * Update the selected elements count in toolbar
         */
        updateSelectedCount: function() {
            const countElement = document.getElementById('scraperv4-selected-count');
            if (countElement) {
                countElement.textContent = `Selected: ${this.selectedElements.length}`;
            }
        },
        
        /**
         * Show notification message
         */
        showNotification: function(message, type = 'info') {
            const colors = {
                success: '#4CAF50',
                error: '#f44336',
                warning: '#ff9800',
                info: '#2196F3'
            };
            
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${colors[type]};
                color: white;
                padding: 12px 16px;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 12px;
                font-weight: 500;
                z-index: ${this.config.zIndex + 10};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                transform: translateX(100%);
                transition: transform 0.3s ease;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 10);
            
            // Remove after delay
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 3000);
        },
        
        /**
         * Show welcome message
         */
        showWelcomeMessage: function() {
            this.toolbar.style.display = 'block';
            this.showNotification('ScraperV4 Interactive Mode Ready! Click "Start Selecting" to begin.', 'success');
        },
        
        /**
         * Send data to backend via bridge
         */
        sendToBackend: function(action, data) {
            if (window.scraperV4Bridge && typeof window.scraperV4Bridge[action] === 'function') {
                try {
                    window.scraperV4Bridge[action](data);
                } catch (error) {
                    console.error('ScraperV4: Backend communication error:', error);
                }
            } else {
                // Fallback: store in window object for Python to retrieve
                window.scraperV4Data = window.scraperV4Data || {};
                window.scraperV4Data[action] = data;
                console.log(`ScraperV4: Stored ${action} data for backend retrieval`, data);
            }
        },
        
        /**
         * Download data as JSON file
         */
        downloadJSON: function(data, filename) {
            const blob = new Blob([JSON.stringify(data, null, 2)], { 
                type: 'application/json' 
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        },
        
        /**
         * Show context menu for element (future enhancement)
         */
        showElementContextMenu: function(element, x, y) {
            // TODO: Implement context menu with options like:
            // - Select similar elements
            // - Get parent selector
            // - Copy selector
            // - Element properties
            console.log('Context menu for element:', element, 'at', x, y);
        },
        
        /**
         * Get all selected elements
         */
        getSelectedElements: function() {
            return this.selectedElements;
        },
        
        /**
         * Set selection mode (single/multiple)
         */
        setSelectionMode: function(mode) {
            this.selectionMode = mode;
        },
        
        /**
         * Clean up and remove overlay
         */
        cleanup: function() {
            this.stopSelecting();
            this.clearSelections();
            
            // Remove event listeners
            document.removeEventListener('mouseover', this.handleMouseOver, true);
            document.removeEventListener('mouseout', this.handleMouseOut, true);
            document.removeEventListener('click', this.handleClick, true);
            document.removeEventListener('contextmenu', this.handleContextMenu, true);
            
            // Remove DOM elements
            if (this.overlay) this.overlay.remove();
            if (this.highlight) this.highlight.remove();
            if (this.infoBox) this.infoBox.remove();
            if (this.toolbar) this.toolbar.remove();
            
            // Clean up window objects
            delete window.scraperV4Interactive;
            delete window.scraperV4Data;
            
            // Restore cursor
            document.body.style.cursor = '';
            
            this.showNotification('ScraperV4 Interactive Mode closed', 'info');
            console.log('ScraperV4: Cleanup completed');
        }
    };
    
    // Initialize the interactive system
    window.scraperV4Interactive.init();
    
})();