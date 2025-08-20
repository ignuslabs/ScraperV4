/**
 * V3 Interactive Overlay System
 * 
 * Provides visual element selection interface for V3 scraper
 * Features:
 * - Visual element highlighting and selection
 * - Container, Field, and Action mode buttons
 * - Real-time template building
 * - Integration with V3 async cookie manager
 * - Save/Export functionality
 */

class V3InteractiveOverlay {
    constructor() {
        this.state = {
            mode: 'select', // select, container, field, action
            currentContainer: null,
            containers: [],
            fields: [],
            actions: [],
            isActive: false,
            isPreviewActive: false,
            template: null
        };
        
        this.ui = {
            overlay: null,
            toolbar: null,
            inspector: null,
            sidebar: null,
            realTimeLogger: null
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
            ignoredElements: ['html', 'body', 'head', 'script', 'style', 'meta', 'link'],
            minContainerItems: 3
        };
        
        this.eventListeners = [];
        this.windowResizeHandler = null;
        
        // Real-time logging system
        this.logger = {
            logs: [],
            maxLogs: 100,
            startTime: Date.now(),
            enabled: true,
            hoverThrottle: 500, // ms between hover logs
            lastHoverTime: 0,
            excludeHover: false
        };
        this.init();
    }
    
    init() {
        this.createOverlay();
        this.setupEventListeners();
        this.attachToWindow();
        
        // Detect and log screen size
        const screenWidth = window.innerWidth;
        const screenHeight = window.innerHeight;
        console.log(`🖥️ Detected screen size: ${screenWidth}x${screenHeight}`);
        
        // Force initial positioning
        setTimeout(() => {
            this.updateUIPositioning();
        }, 100);
        
        console.log('🎯 V3 Interactive Overlay initialized');
    }
    
    createOverlay() {
        // Main overlay container
        this.ui.overlay = this.createElement('div', {
            id: 'v3-interactive-overlay',
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
        
        // Toolbar
        this.ui.toolbar = this.createToolbar();
        this.ui.overlay.appendChild(this.ui.toolbar);
        
        // Inspector panel
        this.ui.inspector = this.createInspector();
        this.ui.overlay.appendChild(this.ui.inspector);
        
        // Sidebar
        this.ui.sidebar = this.createSidebar();
        this.ui.overlay.appendChild(this.ui.sidebar);
        
        // Real-time logger
        this.ui.realTimeLogger = this.createRealTimeLogger();
        this.ui.overlay.appendChild(this.ui.realTimeLogger);
        
        document.body.appendChild(this.ui.overlay);
    }
    
    createToolbar() {
        const toolbar = this.createElement('div', {
            id: 'v3-toolbar',
            style: `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                display: flex;
                gap: 8px;
                padding: 12px;
                pointer-events: auto;
                z-index: 1000000;
                border: 1px solid rgba(0,0,0,0.1);
            `
        });
        
        const buttons = [
            { id: 'container-btn', text: '📦 Container', mode: 'container', color: '#ffc107' },
            { id: 'field-btn', text: '🏷️ Field', mode: 'field', color: '#dc3545' },
            { id: 'action-btn', text: '⚡ Action', mode: 'action', color: '#6610f2' },
            { id: 'auto-btn', text: '🤖 Auto', mode: 'auto', color: '#17a2b8' },
            { id: 'save-btn', text: '💾 Save', mode: 'save', color: '#28a745' },
            { id: 'exit-btn', text: '❌ Exit', mode: 'exit', color: '#6c757d' }
        ];
        
        buttons.forEach(btn => {
            const button = this.createElement('button', {
                id: btn.id,
                textContent: btn.text,
                style: `
                    background: ${btn.color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    min-width: 100px;
                `,
                'data-mode': btn.mode
            });
            
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-2px)';
                button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
                button.style.boxShadow = 'none';
            });
            
            button.addEventListener('click', () => this.handleToolbarClick(btn.mode));
            toolbar.appendChild(button);
        });
        
        return toolbar;
    }
    
    createInspector() {
        const inspector = this.createElement('div', {
            id: 'v3-inspector',
            style: `
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 350px;
                max-height: 300px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                pointer-events: auto;
                z-index: 1000000;
                border: 1px solid rgba(0,0,0,0.1);
                overflow: hidden;
                display: none;
            `
        });
        
        inspector.innerHTML = `
            <div id="inspector-header" style="padding: 16px; border-bottom: 1px solid #eee; background: #f8f9fa; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #333;">🔍 Element Inspector</h3>
                <button id="inspector-toggle" style="background: none; border: none; font-size: 18px; cursor: pointer; color: #666; padding: 4px;" title="Collapse/Expand">−</button>
            </div>
            <div id="inspector-content" class="inspector-content" style="padding: 16px; overflow-y: auto; max-height: 240px;">
                <div id="element-info" style="margin-bottom: 12px;">
                    <strong>No element selected</strong>
                </div>
                <div id="element-path" style="font-size: 12px; color: #666; font-family: monospace; margin-bottom: 12px;"></div>
                <div id="element-attributes" style="font-size: 12px;"></div>
            </div>
        `;
        
        return inspector;
    }
    
    createSidebar() {
        const sidebar = this.createElement('div', {
            id: 'v3-sidebar',
            style: `
                position: fixed;
                top: 20px;
                right: 20px;
                width: 320px;
                max-height: calc(100vh - 40px);
                background: #ffffff !important;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                pointer-events: auto;
                z-index: 1000000;
                border: 1px solid rgba(0,0,0,0.1);
                overflow: hidden;
                display: none;
                opacity: 1 !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `
        });
        
        sidebar.innerHTML = `
            <div id="sidebar-header" style="padding: 16px; border-bottom: 1px solid #eee; background: #f8f9fa; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #333;">📋 Template Builder</h3>
                    <div style="font-size: 12px; color: #666; margin-top: 4px;">Build your scraping template</div>
                </div>
                <button id="sidebar-toggle" style="background: none; border: none; font-size: 18px; cursor: pointer; color: #666; padding: 4px;" title="Collapse/Expand">−</button>
            </div>
            <div id="sidebar-content" style="padding: 16px; overflow-y: auto; max-height: calc(100vh - 120px); background: #ffffff !important;">
                <div id="containers-section" style="background: #ffffff !important;">
                    <h4 style="margin: 0 0 12px 0; font-size: 14px; color: #333;">📦 Containers</h4>
                    <div id="containers-list" style="margin-bottom: 20px;">
                        <div style="color: #666; font-size: 12px; font-style: italic;">No containers added yet</div>
                    </div>
                </div>
                
                <div id="fields-section" style="background: #ffffff !important;">
                    <h4 style="margin: 0 0 12px 0; font-size: 14px; color: #333;">🏷️ Fields</h4>
                    <div id="fields-list" style="margin-bottom: 20px;">
                        <div style="color: #666; font-size: 12px; font-style: italic;">No fields added yet</div>
                    </div>
                </div>
                
                <div id="actions-section" style="background: #ffffff !important;">
                    <h4 style="margin: 0 0 12px 0; font-size: 14px; color: #333;">⚡ Actions</h4>
                    <div id="actions-list" style="margin-bottom: 20px;">
                        <div style="color: #666; font-size: 12px; font-style: italic;">No actions added yet</div>
                    </div>
                </div>
                
                <div id="template-actions" style="border-top: 1px solid #eee; padding-top: 16px;">
                    <button id="preview-template" style="background: #17a2b8; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-size: 12px; cursor: pointer; margin-right: 8px;">
                        👁️ Preview
                    </button>
                    <button id="test-template" style="background: #ffc107; color: black; border: none; border-radius: 6px; padding: 8px 16px; font-size: 12px; cursor: pointer; margin-right: 8px;">
                        🧪 Test
                    </button>
                    <button id="save-export-template" style="background: #28a745; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-size: 12px; cursor: pointer;">
                        💾 Save & Export
                    </button>
                </div>
            </div>
        `;
        
        return sidebar;
    }
    
    createRealTimeLogger() {
        const logger = this.createElement('div', {
            id: 'v3-realtime-logger',
            style: `
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 400px;
                max-height: 250px;
                background: rgba(0, 0, 0, 0.9);
                color: #00ff00;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                pointer-events: auto;
                z-index: 1000001;
                overflow-y: auto;
                border: 1px solid #333;
                display: none;
            `
        });
        
        logger.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #333; padding-bottom: 4px;">
                <span style="color: #00ff00; font-weight: bold; font-size: 12px; cursor: pointer;" title="Click to toggle logger size">📊 Real-Time Log</span>
                <div>
                    <button id="toggle-hover-logs" style="background: #444; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; margin-right: 2px; cursor: pointer; transition: all 0.2s; pointer-events: auto; z-index: 1000002;" title="Toggle hover logging">Hover</button>
                    <button id="pause-logs" style="background: #444; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; margin-right: 2px; cursor: pointer; transition: all 0.2s; pointer-events: auto; z-index: 1000002;" title="Pause/Resume logging">Pause</button>
                    <button id="clear-logs" style="background: #444; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; margin-right: 2px; cursor: pointer; transition: all 0.2s; pointer-events: auto; z-index: 1000002;" title="Clear all logs">Clear</button>
                    <button id="minimize-logger" style="background: #666; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; margin-right: 2px; cursor: pointer; transition: all 0.2s; pointer-events: auto; z-index: 1000002;" title="Minimize logger">_</button>
                    <button id="toggle-logger" style="background: #444; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; margin-right: 2px; cursor: pointer; transition: all 0.2s; pointer-events: auto; z-index: 1000002;" title="Collapse/Expand">−</button>
                    <button id="close-logger" style="background: #e74c3c; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; cursor: pointer; transition: all 0.2s; pointer-events: auto; z-index: 1000002;" title="Close logger">✕</button>
                </div>
            </div>
            <div id="log-content" style="max-height: 180px; overflow-y: auto; font-size: 10px;"></div>
        `;
        
        // Add hover effects to buttons
        setTimeout(() => {
            const buttons = logger.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.addEventListener('mouseenter', () => {
                    if (btn.id === 'close-logger') {
                        btn.style.background = '#c0392b';
                    } else if (btn.id === 'minimize-logger') {
                        btn.style.background = '#555';
                    } else {
                        btn.style.background = '#555';
                    }
                    btn.style.transform = 'translateY(-1px)';
                });
                
                btn.addEventListener('mouseleave', () => {
                    if (btn.id === 'close-logger') {
                        btn.style.background = '#e74c3c';
                    } else if (btn.id === 'minimize-logger') {
                        btn.style.background = '#666';
                    } else {
                        btn.style.background = '#444';
                    }
                    btn.style.transform = 'translateY(0)';
                });
            });
            
            // Make logger title clickable to toggle collapse
            const title = logger.querySelector('span');
            if (title) {
                title.addEventListener('click', () => this.toggleLogger());
            }
        }, 100);
        
        return logger;
    }
    
    setupEventListeners() {
        // Global keyboard shortcuts
        this.addEventHandler(document, 'keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                e.preventDefault();
                this.toggle();
            }
            if (this.state.isActive && e.key === 'Escape') {
                e.preventDefault();
                this.exit();
            }
        });
        
        // Mouse events for element selection
        this.addEventHandler(document, 'mousemove', (e) => {
            if (!this.state.isActive || this.state.mode === 'select') return;
            this.handleMouseMove(e);
        });
        
        this.addEventHandler(document, 'click', (e) => {
            if (!this.state.isActive) return;
            if (this.isOverlayElement(e.target)) return;
            this.handleElementClick(e);
        });
        
        // Sidebar event listeners
        this.addEventHandler(document, 'click', (e) => {
            // Log all button clicks with detailed info
            if (e.target.id) {
                this.logInteraction('BUTTON_CLICK', {
                    elementId: e.target.id,
                    elementClass: e.target.className,
                    elementTag: e.target.tagName,
                    elementText: e.target.textContent?.substring(0, 50) || 'No text',
                    timestamp: new Date().toISOString()
                });
            }
            
            if (e.target.id === 'preview-template') {
                this.logInteraction('ACTION', { type: 'PREVIEW_TEMPLATE', data: this.buildTemplate() });
                this.previewTemplate();
            }
            if (e.target.id === 'test-template') {
                this.logInteraction('ACTION', { type: 'TEST_TEMPLATE', data: this.buildTemplate() });
                this.testTemplate();
            }
            if (e.target.id === 'save-export-template') {
                this.logInteraction('ACTION', { type: 'SAVE_EXPORT_TEMPLATE', data: this.buildTemplate() });
                this.saveAndExportTemplate();
            }
            if (e.target.id === 'sidebar-toggle') {
                this.logInteraction('UI_TOGGLE', { type: 'SIDEBAR' });
                this.toggleSidebar();
            }
            if (e.target.id === 'inspector-toggle') {
                this.logInteraction('UI_TOGGLE', { type: 'INSPECTOR' });
                this.toggleInspector();
            }
            if (e.target.id === 'clear-logs') {
                this.clearLogs();
            }
            if (e.target.id === 'toggle-logger') {
                this.toggleLogger();
            }
            if (e.target.id === 'pause-logs') {
                this.toggleLogging();
            }
            if (e.target.id === 'toggle-hover-logs') {
                this.toggleHoverLogging();
            }
            if (e.target.id === 'minimize-logger') {
                this.minimizeLogger();
            }
            if (e.target.id === 'close-logger') {
                this.closeLogger();
            }
            
            // Handle logger title click for toggling
            if (e.target.textContent && e.target.textContent.includes('📊 Real-Time Log')) {
                this.toggleLogger();
            }
            
            // Handle remove buttons
            if (e.target.classList.contains('remove-container-btn')) {
                const containerId = e.target.getAttribute('data-container-id');
                const containerIndex = parseInt(e.target.getAttribute('data-container-index'));
                this.removeContainer(containerId, containerIndex);
            }
            
            if (e.target.classList.contains('remove-field-btn')) {
                const fieldId = e.target.getAttribute('data-field-id');
                const containerId = e.target.getAttribute('data-container-id');
                this.removeField(fieldId, containerId);
            }
            
            if (e.target.classList.contains('remove-action-btn')) {
                const actionId = e.target.getAttribute('data-action-id');
                const actionIndex = parseInt(e.target.getAttribute('data-action-index'));
                this.removeAction(actionId, actionIndex);
            }
        });
        
        // Window resize handler for responsive positioning
        this.windowResizeHandler = () => this.handleWindowResize();
        window.addEventListener('resize', this.windowResizeHandler);
        
        // Initial positioning
        this.updateUIPositioning();
    }
    
    addEventHandler(element, event, handler) {
        element.addEventListener(event, handler);
        this.eventListeners.push({ element, event, handler });
    }
    
    removeAllEventListeners() {
        this.eventListeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventListeners = [];
        
        // Remove window resize handler
        if (this.windowResizeHandler) {
            window.removeEventListener('resize', this.windowResizeHandler);
        }
    }
    
    handleWindowResize() {
        // Debounce resize events
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.updateUIPositioning();
        }, 100);
    }
    
    updateUIPositioning() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const screenWidth = window.screen.width;
        const screenHeight = window.screen.height;
        
        console.log(`🖥️ Viewport: ${viewportWidth}x${viewportHeight}, Screen: ${screenWidth}x${screenHeight}`);
        
        // Better scaling based on actual usage
        const isSmallScreen = viewportWidth < 1200 || viewportHeight < 800;
        const isTinyScreen = viewportWidth < 900 || viewportHeight < 600;
        
        // Conservative padding and sizing
        const padding = isTinyScreen ? 8 : isSmallScreen ? 12 : 20;
        const toolbarHeight = isTinyScreen ? 50 : 80;
        
        // Calculate maximum available space
        const availableWidth = viewportWidth - (padding * 2);
        const availableHeight = viewportHeight - (padding * 2);
        
        // Responsive widths with constraints
        const sidebarWidth = Math.min(Math.max(250, availableWidth * 0.25), 350);
        const inspectorWidth = Math.min(Math.max(250, availableWidth * 0.25), 400);
        
        console.log(`📊 Calculated dimensions - available: ${availableWidth}x${availableHeight}, sidebar: ${sidebarWidth}, inspector: ${inspectorWidth}`);
        
        // Update toolbar position (top center) with safe positioning
        if (this.ui.toolbar) {
            this.ui.toolbar.style.position = 'fixed';
            this.ui.toolbar.style.left = '50%';
            this.ui.toolbar.style.transform = 'translateX(-50%)';
            this.ui.toolbar.style.top = `${padding}px`;
            this.ui.toolbar.style.zIndex = '1000000';
            
            // Scale buttons for very small screens
            if (isTinyScreen) {
                const buttons = this.ui.toolbar.querySelectorAll('button');
                buttons.forEach(btn => {
                    btn.style.padding = '6px 8px';
                    btn.style.fontSize = '11px';
                    btn.style.minWidth = '60px';
                });
                this.ui.toolbar.style.gap = '4px';
            }
        }
        
        // Update sidebar position (right side) with proper constraints
        if (this.ui.sidebar) {
            const sidebarTop = padding + toolbarHeight;
            const maxSidebarHeight = availableHeight - toolbarHeight;
            
            this.ui.sidebar.style.position = 'fixed';
            this.ui.sidebar.style.right = `${padding}px`;
            this.ui.sidebar.style.top = `${sidebarTop}px`;
            this.ui.sidebar.style.width = `${sidebarWidth}px`;
            this.ui.sidebar.style.maxHeight = `${maxSidebarHeight}px`;
            this.ui.sidebar.style.zIndex = '1000000';
            
            // Ensure sidebar content is properly scrollable
            const sidebarContent = this.ui.sidebar.querySelector('#sidebar-content');
            if (sidebarContent) {
                const contentHeight = maxSidebarHeight - 80; // Account for header
                sidebarContent.style.maxHeight = `${Math.max(200, contentHeight)}px`;
                sidebarContent.style.overflowY = 'auto';
            }
        }
        
        // Update inspector position (bottom left) with proper constraints
        if (this.ui.inspector) {
            const maxInspectorHeight = Math.min(300, availableHeight * 0.4);
            
            this.ui.inspector.style.position = 'fixed';
            this.ui.inspector.style.left = `${padding}px`;
            this.ui.inspector.style.bottom = `${padding}px`;
            this.ui.inspector.style.width = `${inspectorWidth}px`;
            this.ui.inspector.style.maxHeight = `${maxInspectorHeight}px`;
            this.ui.inspector.style.zIndex = '1000000';
            
            // Adjust inspector content
            const inspectorContent = this.ui.inspector.querySelector('#inspector-content');
            if (inspectorContent) {
                const contentHeight = maxInspectorHeight - 60; // Account for header
                inspectorContent.style.maxHeight = `${Math.max(120, contentHeight)}px`;
                inspectorContent.style.overflowY = 'auto';
            }
        }
        
        // Update auto-detect panel if it exists
        const autoDetectPanel = document.getElementById('v3-autodetect-panel');
        if (autoDetectPanel) {
            const panelTop = padding + toolbarHeight;
            const maxPanelHeight = availableHeight - toolbarHeight - 100;
            const panelWidth = Math.min(inspectorWidth + 50, availableWidth * 0.3);
            
            autoDetectPanel.style.position = 'fixed';
            autoDetectPanel.style.left = `${padding}px`;
            autoDetectPanel.style.top = `${panelTop}px`;
            autoDetectPanel.style.width = `${panelWidth}px`;
            autoDetectPanel.style.maxHeight = `${maxPanelHeight}px`;
            autoDetectPanel.style.zIndex = '1000001';
            
            // Adjust auto-detect content
            const autoDetectContent = autoDetectPanel.querySelector('#autodetect-content');
            if (autoDetectContent) {
                const contentHeight = maxPanelHeight - 120; // Account for header and buttons
                autoDetectContent.style.maxHeight = `${Math.max(200, contentHeight)}px`;
                autoDetectContent.style.overflowY = 'auto';
            }
        }
        
        // Update real-time logger position to avoid conflicts
        if (this.ui.realTimeLogger) {
            const loggerWidth = Math.min(400, availableWidth * 0.4);
            
            this.ui.realTimeLogger.style.position = 'fixed';
            this.ui.realTimeLogger.style.right = `${padding}px`;
            this.ui.realTimeLogger.style.bottom = `${padding}px`;
            this.ui.realTimeLogger.style.width = `${loggerWidth}px`;
            this.ui.realTimeLogger.style.zIndex = '1000001';
            
            // Scale for small screens
            if (isTinyScreen) {
                this.ui.realTimeLogger.style.fontSize = '10px';
                this.ui.realTimeLogger.style.padding = '8px';
                this.ui.realTimeLogger.style.maxHeight = '200px';
            }
        }
        
        // Log final positioning for debugging
        console.log(`📐 Final positioning:`, {
            padding,
            toolbarHeight,
            sidebarWidth,
            inspectorWidth,
            isSmallScreen,
            isTinyScreen
        });
    }
    
    attachToWindow() {
        // Make globally accessible
        window.V3InteractiveOverlay = this;
        
        // Integration with existing ScraperModules
        if (window.ScraperModules) {
            window.ScraperModules.v3InteractiveOverlay = this;
        }
        
        // Create global activation function
        window.startV3Interactive = () => this.start();
    }
    
    handleToolbarClick(mode) {
        this.logInteraction('TOOLBAR_CLICK', {
            mode: mode,
            previousMode: this.state.mode,
            currentState: {
                containers: this.state.containers.length,
                fields: this.state.fields.length,
                actions: this.state.actions.length
            }
        });
        
        switch (mode) {
            case 'container':
                this.setMode('container');
                break;
            case 'field':
                this.setMode('field');
                break;
            case 'action':
                this.setMode('action');
                break;
            case 'auto':
                this.logInteraction('AUTO_DETECTION', { action: 'START' });
                this.runAutoDetection();
                break;
            case 'save':
                this.logInteraction('TEMPLATE_SAVE', { action: 'START', templateData: this.buildTemplate() });
                this.saveTemplate();
                break;
            case 'exit':
                this.logInteraction('OVERLAY_EXIT', { reason: 'USER_CLICKED_EXIT' });
                this.exit();
                break;
        }
    }
    
    setMode(newMode) {
        const oldMode = this.state.mode;
        this.state.mode = newMode;
        
        this.logInteraction('MODE_CHANGE', {
            from: oldMode,
            to: newMode,
            cursor: newMode === 'select' ? 'default' : 'crosshair'
        });
        
        this.updateToolbarState();
        this.updateInstructions();
        
        // Update cursor
        document.body.style.cursor = newMode === 'select' ? 'default' : 'crosshair';
        
        console.log(`🎯 Mode changed to: ${newMode}`);
    }
    
    updateToolbarState() {
        const buttons = this.ui.toolbar.querySelectorAll('button');
        buttons.forEach(btn => {
            const mode = btn.getAttribute('data-mode');
            if (mode === this.state.mode) {
                btn.style.background = '#007bff';
                btn.style.transform = 'translateY(-2px)';
            } else {
                // Reset to original color
                const colorMap = {
                    container: '#ffc107',
                    field: '#dc3545',
                    action: '#6610f2',
                    auto: '#17a2b8',
                    save: '#28a745',
                    exit: '#6c757d'
                };
                btn.style.background = colorMap[mode] || '#6c757d';
                btn.style.transform = 'translateY(0)';
            }
        });
    }
    
    updateInstructions() {
        const instructions = {
            container: 'Click on repeating elements to create a container',
            field: 'Click on data elements within containers',
            action: 'Click on navigation elements (buttons, links)',
            auto: 'Auto-detection in progress...'
        };
        
        // You could add an instruction banner here
        console.log(`📖 ${instructions[this.state.mode] || 'Select a mode from the toolbar'}`);
    }
    
    handleMouseMove(e) {
        const element = e.target;
        
        if (this.isIgnoredElement(element) || this.isOverlayElement(element)) {
            this.clearHoverHighlight();
            return;
        }
        
        // Log element hover with throttling to avoid spam
        if (this.selectionBuffer.hoveredElement !== element && !this.logger.excludeHover) {
            const now = Date.now();
            if (now - this.logger.lastHoverTime > this.logger.hoverThrottle) {
                this.logger.lastHoverTime = now;
                this.logInteraction('ELEMENT_HOVER', {
                    tagName: element.tagName,
                    className: element.className,
                    id: element.id,
                    textContent: element.textContent?.substring(0, 50) || 'No text',
                    selector: this.generateSelector(element),
                    mode: this.state.mode
                });
            }
        }
        
        // Update hover highlight
        this.clearHoverHighlight();
        this.highlightElement(element, this.config.highlightColors.hover);
        this.selectionBuffer.hoveredElement = element;
        
        // Update inspector
        this.updateInspector(element);
    }
    
    handleElementClick(e) {
        const element = e.target;
        
        if (this.isIgnoredElement(element) || this.isOverlayElement(element)) {
            return; // Let default behavior happen for ignored/overlay elements
        }
        
        // Only prevent default if we're in template building mode, not preview mode
        if (!this.state.isPreviewActive) {
            e.preventDefault();
            e.stopPropagation();
        } else {
            // In preview mode, allow normal navigation but log the interaction
            this.logInteraction('PREVIEW_CLICK', {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                href: element.href || 'No href'
            });
            return; // Let the click proceed normally
        }
        
        // Log detailed element click info
        this.logInteraction('ELEMENT_CLICK', {
            mode: this.state.mode,
            element: {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                textContent: element.textContent?.substring(0, 100) || 'No text',
                attributes: this.getElementAttributes(element),
                selector: this.generateSelector(element),
                innerHTML: element.innerHTML?.substring(0, 200) || 'No HTML',
                position: {
                    offsetTop: element.offsetTop,
                    offsetLeft: element.offsetLeft,
                    clientWidth: element.clientWidth,
                    clientHeight: element.clientHeight
                }
            },
            mousePosition: { x: e.clientX, y: e.clientY },
            timestamp: new Date().toISOString()
        });
        
        switch (this.state.mode) {
            case 'container':
                this.addContainer(element);
                break;
            case 'field':
                this.addField(element);
                break;
            case 'action':
                this.addAction(element);
                break;
        }
    }
    
    addContainer(element) {
        const selector = this.generateSelector(element);
        const similarElements = this.findSimilarElements(element);
        
        this.logInteraction('CONTAINER_ANALYSIS', {
            element: {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                selector: selector,
                textContent: element.textContent?.substring(0, 100) || 'No text',
                attributes: this.getElementAttributes(element)
            },
            similarElements: similarElements.length,
            minRequired: this.config.minContainerItems,
            similarElementsData: similarElements.slice(0, 5).map(el => ({
                tagName: el.tagName,
                className: el.className,
                textContent: el.textContent?.substring(0, 50) || 'No text'
            }))
        });
        
        if (similarElements.length < this.config.minContainerItems) {
            this.logInteraction('CONTAINER_REJECTED', {
                reason: 'INSUFFICIENT_SIMILAR_ELEMENTS',
                found: similarElements.length,
                required: this.config.minContainerItems
            });
            alert(`Found only ${similarElements.length} similar elements. Containers need at least ${this.config.minContainerItems} items.`);
            return;
        }
        
        const container = {
            id: `container_${Date.now()}`,
            label: this.generateContainerLabel(element),
            selector: selector,
            element_type: 'container',
            count: similarElements.length,
            sub_elements: []
        };
        
        this.logInteraction('CONTAINER_CREATED', {
            container: container,
            similarElementsCount: similarElements.length,
            previousContainers: this.state.containers.length,
            currentContainerSelector: selector
        });
        
        this.state.containers.push(container);
        this.state.currentContainer = container;
        
        // Highlight all similar elements
        similarElements.forEach(el => {
            this.highlightElement(el, this.config.highlightColors.container, 'container', true, container.id);
            el.setAttribute('data-v3-container-id', container.id);
        });
        
        this.updateSidebar();
        this.showNotification(`Container added: ${container.label} (${container.count} items)`);
        
        console.log('📦 Container added:', container);
    }
    
    addField(element) {
        const fieldType = this.detectFieldType(element);
        const sampleText = this.getSampleText(element);
        
        const field = {
            id: `field_${Date.now()}`,
            label: this.generateFieldLabel(element, fieldType),
            element_type: fieldType,
            is_required: false,
            sample_text: sampleText
        };
        
        this.logInteraction('FIELD_ANALYSIS', {
            element: {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                textContent: element.textContent?.substring(0, 100) || 'No text',
                attributes: this.getElementAttributes(element),
                innerHTML: element.innerHTML?.substring(0, 150) || 'No HTML'
            },
            detectedType: fieldType,
            sampleText: sampleText,
            currentContainer: this.state.currentContainer ? this.state.currentContainer.label : null,
            fieldLabel: field.label
        });
        
        // If we have a current container, add field to it with relative selector
        if (this.state.currentContainer) {
            field.selector = this.generateRelativeSelector(element, this.state.currentContainer);
            this.state.currentContainer.sub_elements.push(field);
            
            this.logInteraction('FIELD_ADDED_TO_CONTAINER', {
                field: field,
                container: this.state.currentContainer.label,
                containerSubElements: this.state.currentContainer.sub_elements.length,
                relativeSelector: field.selector
            });
            
            this.showNotification(`Field added to container: ${field.label}`);
        } else {
            // Add as standalone field with absolute selector
            field.selector = this.generateSelector(element);
            this.state.fields.push(field);
            
            this.logInteraction('STANDALONE_FIELD_ADDED', {
                field: field,
                totalStandaloneFields: this.state.fields.length,
                absoluteSelector: field.selector
            });
            
            this.showNotification(`Standalone field added: ${field.label}`);
        }
        
        // Highlight the field
        this.highlightElement(element, this.config.highlightColors.field, 'field', true, field.id);
        element.setAttribute('data-v3-field-id', field.id);
        
        this.updateSidebar();
        console.log('🏷️ Field added:', field);
    }
    
    addAction(element) {
        const selector = this.generateSelector(element);
        const actionType = this.detectActionType(element);
        
        const action = {
            id: `action_${Date.now()}`,
            label: this.generateActionLabel(element, actionType),
            selector: selector,
            action_type: actionType,
            element_type: 'action'
        };
        
        this.state.actions.push(action);
        
        // Highlight the action element
        this.highlightElement(element, this.config.highlightColors.action, 'action', true, action.id);
        element.setAttribute('data-v3-action-id', action.id);
        
        this.updateSidebar();
        this.showNotification(`Action added: ${action.label}`);
        
        console.log('⚡ Action added:', action);
    }
    
    removeContainer(containerId, containerIndex) {
        // Remove from state
        this.state.containers.splice(containerIndex, 1);
        
        // Reset current container if it was the removed one
        if (this.state.currentContainer && this.state.currentContainer.id === containerId) {
            this.state.currentContainer = null;
        }
        
        // Clear highlights for this container
        this.clearHighlightsForContainer(containerId);
        
        // Update sidebar
        this.updateSidebar();
        
        this.showNotification('Container removed');
        this.logInteraction('CONTAINER_REMOVED', { containerId, containerIndex });
        console.log('🗑️ Container removed:', containerId);
    }
    
    removeField(fieldId, containerId) {
        // If field is in a container, remove from container
        if (containerId) {
            const container = this.state.containers.find(c => c.id === containerId);
            if (container) {
                const fieldIndex = container.sub_elements.findIndex(f => f.id === fieldId);
                if (fieldIndex !== -1) {
                    container.sub_elements.splice(fieldIndex, 1);
                }
            }
        } else {
            // Remove from standalone fields
            const fieldIndex = this.state.fields.findIndex(f => f.id === fieldId);
            if (fieldIndex !== -1) {
                this.state.fields.splice(fieldIndex, 1);
            }
        }
        
        // Clear highlights for this field
        this.clearHighlightsForField(fieldId);
        
        // Update sidebar
        this.updateSidebar();
        
        this.showNotification('Field removed');
        this.logInteraction('FIELD_REMOVED', { fieldId, containerId });
        console.log('🗑️ Field removed:', fieldId);
    }
    
    removeAction(actionId, actionIndex) {
        // Remove from state
        this.state.actions.splice(actionIndex, 1);
        
        // Clear highlights for this action
        this.clearHighlightsForAction(actionId);
        
        // Update sidebar
        this.updateSidebar();
        
        this.showNotification('Action removed');
        this.logInteraction('ACTION_REMOVED', { actionId, actionIndex });
        console.log('🗑️ Action removed:', actionId);
    }
    
    clearHighlightsForContainer(containerId) {
        // Find and remove highlight elements for this container
        const highlights = document.querySelectorAll(`.v3-highlighted[data-element-id="${containerId}"]`);
        highlights.forEach(highlight => highlight.remove());
        
        // Remove highlights from actual elements
        const elements = document.querySelectorAll(`[data-v3-container-id="${containerId}"]`);
        elements.forEach(el => {
            el.style.boxShadow = '';
            el.style.outline = '';
            el.removeAttribute('data-v3-container-id');
        });
    }
    
    clearHighlightsForField(fieldId) {
        // Find and remove highlight elements for this field
        const highlights = document.querySelectorAll(`.v3-highlighted[data-element-id="${fieldId}"]`);
        highlights.forEach(highlight => highlight.remove());
        
        // Remove highlights from actual elements
        const elements = document.querySelectorAll(`[data-v3-field-id="${fieldId}"]`);
        elements.forEach(el => {
            el.style.boxShadow = '';
            el.style.outline = '';
            el.removeAttribute('data-v3-field-id');
        });
    }
    
    clearHighlightsForAction(actionId) {
        // Find and remove highlight elements for this action
        const highlights = document.querySelectorAll(`.v3-highlighted[data-element-id="${actionId}"]`);
        highlights.forEach(highlight => highlight.remove());
        
        // Remove highlights from actual elements
        const elements = document.querySelectorAll(`[data-v3-action-id="${actionId}"]`);
        elements.forEach(el => {
            el.style.boxShadow = '';
            el.style.outline = '';
            el.removeAttribute('data-v3-action-id');
        });
    }
    
    runAutoDetection() {
        if (window.V3AutoDetector) {
            this.showNotification('Running auto-detection...');
            window.V3AutoDetector.startV3AutoDetection();
        } else {
            alert('Auto-detection module not available');
        }
    }
    
    // Utility methods
    
    createElement(tag, attributes = {}) {
        const element = document.createElement(tag);
        Object.keys(attributes).forEach(key => {
            if (key === 'style') {
                element.style.cssText = attributes[key];
            } else if (key === 'textContent') {
                element.textContent = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });
        return element;
    }
    
    isIgnoredElement(element) {
        const tagName = element.tagName.toLowerCase();
        return this.config.ignoredElements.includes(tagName) ||
               element.offsetWidth === 0 ||
               element.offsetHeight === 0;
    }
    
    isOverlayElement(element) {
        // Check for all overlay-related elements that should be excluded from selection
        return element.closest('#v3-interactive-overlay') !== null ||
               element.closest('#v3-autodetect-panel') !== null ||
               element.closest('#v3-fallback-toolbar') !== null ||
               element.id.startsWith('v3-') ||
               element.classList.contains('v3-overlay') ||
               element.classList.contains('v3-highlighted') ||
               element.classList.contains('v3-element-label') ||
               element.classList.contains('auto-detect-label') ||
               element.classList.contains('preview-btn') ||
               element.classList.contains('apply-btn') ||
               (element.tagName === 'BUTTON' && element.closest('#v3-autodetect-panel'));
    }
    
    generateSelector(element) {
        // Enhanced hierarchical selector generation with fallback strategies
        console.log('🎯 Generating hierarchical selectors for element:', element);
        
        const fallbackSelectors = this.generateFallbackSelectors(element);
        const bestSelector = this.selectBestSelector(fallbackSelectors, element);
        
        console.log(`✅ Selected best selector: ${bestSelector.selector} (confidence: ${bestSelector.confidence})`);
        return bestSelector.selector;
    }

    /**
     * Generate multiple fallback selector strategies
     * Returns array of selector objects with confidence scores
     */
    generateFallbackSelectors(element) {
        const selectors = [];
        const tagName = element.tagName.toLowerCase();
        const id = element.id;
        const classes = Array.from(element.classList).filter(cls => !cls.startsWith('v3-'));
        
        // Level 1: Unique identifier-based selectors (highest confidence)
        if (id && !id.startsWith('v3-') && this.isUniqueSelector(`#${id}`)) {
            selectors.push({
                selector: `#${id}`,
                type: 'id',
                confidence: 0.95,
                specificity: 100
            });
        }
        
        // Check for unique data attributes
        const dataAttrs = this.getUniqueDataAttributes(element);
        for (const attr of dataAttrs) {
            const selector = `[${attr.name}="${attr.value}"]`;
            if (this.isUniqueSelector(selector)) {
                selectors.push({
                    selector: selector,
                    type: 'data-attribute',
                    confidence: 0.9,
                    specificity: 90
                });
            }
        }
        
        // Level 2: Contextual class-based selectors
        if (classes.length > 0) {
            // Try single meaningful class
            for (const cls of classes) {
                const selector = `${tagName}.${cls}`;
                if (this.isReliableSelector(selector, element)) {
                    selectors.push({
                        selector: selector,
                        type: 'tag-class',
                        confidence: 0.8,
                        specificity: 70
                    });
                }
            }
            
            // Try combined classes
            if (classes.length > 1) {
                const selector = `${tagName}.${classes.join('.')}`;
                if (this.isReliableSelector(selector, element)) {
                    selectors.push({
                        selector: selector,
                        type: 'tag-multiclass',
                        confidence: 0.85,
                        specificity: 80
                    });
                }
            }
        }
        
        // Level 3: Structural position selectors
        const structuralSelectors = this.generateStructuralSelectors(element);
        selectors.push(...structuralSelectors);
        
        // Level 4: Content-based selectors
        const contentSelectors = this.generateContentBasedSelectors(element);
        selectors.push(...contentSelectors);
        
        // Level 5: Generic fallback with validation
        const genericSelectors = this.generateGenericFallbacks(element);
        selectors.push(...genericSelectors);
        
        console.log(`📋 Generated ${selectors.length} fallback selectors`);
        return selectors;
    }

    /**
     * Get unique data attributes from element
     */
    getUniqueDataAttributes(element) {
        const attributes = [];
        for (const attr of element.attributes) {
            if (attr.name.startsWith('data-') && attr.value && attr.value.length > 0) {
                attributes.push({
                    name: attr.name,
                    value: attr.value
                });
            }
        }
        return attributes;
    }

    /**
     * Generate structural position-based selectors
     */
    generateStructuralSelectors(element) {
        const selectors = [];
        const tagName = element.tagName.toLowerCase();
        
        // nth-child based selectors
        const nthChild = this.getNthChildPosition(element);
        if (nthChild !== null) {
            const parent = element.parentElement;
            const parentSelector = this.getSimpleParentSelector(parent);
            
            if (parentSelector) {
                selectors.push({
                    selector: `${parentSelector} > ${tagName}:nth-child(${nthChild})`,
                    type: 'nth-child',
                    confidence: 0.7,
                    specificity: 60
                });
            }
        }
        
        // nth-of-type based selectors
        const nthOfType = this.getNthOfTypePosition(element);
        if (nthOfType !== null) {
            const parent = element.parentElement;
            const parentSelector = this.getSimpleParentSelector(parent);
            
            if (parentSelector) {
                selectors.push({
                    selector: `${parentSelector} > ${tagName}:nth-of-type(${nthOfType})`,
                    type: 'nth-of-type',
                    confidence: 0.75,
                    specificity: 65
                });
            }
        }
        
        // Hierarchical path selectors
        const pathSelector = this.generateHierarchicalPath(element, 3); // Max 3 levels
        if (pathSelector) {
            selectors.push({
                selector: pathSelector,
                type: 'hierarchical',
                confidence: 0.6,
                specificity: 50
            });
        }
        
        return selectors;
    }

    /**
     * Generate content-based selectors for elements with meaningful text
     */
    generateContentBasedSelectors(element) {
        const selectors = [];
        const text = element.textContent.trim();
        const tagName = element.tagName.toLowerCase();
        
        // Text content selectors (limited length for practicality)
        if (text && text.length > 3 && text.length < 50 && !text.includes('\n')) {
            const escapedText = text.replace(/['"]/g, '');
            selectors.push({
                selector: `${tagName}:contains("${escapedText}")`,
                type: 'content',
                confidence: 0.65,
                specificity: 40
            });
        }
        
        // Attribute-based content selectors
        const title = element.getAttribute('title');
        if (title && title.length < 30) {
            selectors.push({
                selector: `${tagName}[title="${title}"]`,
                type: 'title-attribute',
                confidence: 0.7,
                specificity: 55
            });
        }
        
        const alt = element.getAttribute('alt');
        if (alt && alt.length < 30) {
            selectors.push({
                selector: `${tagName}[alt="${alt}"]`,
                type: 'alt-attribute',
                confidence: 0.7,
                specificity: 55
            });
        }
        
        return selectors;
    }

    /**
     * Generate generic fallback selectors
     */
    generateGenericFallbacks(element) {
        const selectors = [];
        const tagName = element.tagName.toLowerCase();
        
        // Simple tag selector as last resort
        selectors.push({
            selector: tagName,
            type: 'tag',
            confidence: 0.3,
            specificity: 10
        });
        
        // Universal selector as absolute fallback
        selectors.push({
            selector: '*',
            type: 'universal',
            confidence: 0.1,
            specificity: 0
        });
        
        return selectors;
    }

    /**
     * Select the best selector from available options
     */
    selectBestSelector(selectors, element) {
        // Filter out selectors that don't work
        const workingSelectors = selectors.filter(s => {
            try {
                const elements = document.querySelectorAll(s.selector);
                return elements.length > 0 && Array.from(elements).includes(element);
            } catch (e) {
                return false; // Invalid selector
            }
        });
        
        if (workingSelectors.length === 0) {
            console.warn('⚠️ No working selectors found, using tag fallback');
            return {
                selector: element.tagName.toLowerCase(),
                confidence: 0.2
            };
        }
        
        // Score selectors based on confidence and reliability
        const scoredSelectors = workingSelectors.map(s => {
            const reliability = this.calculateSelectorReliability(s.selector, element);
            const score = s.confidence * 0.7 + reliability * 0.3;
            return { ...s, reliability, score };
        });
        
        // Return best scoring selector
        scoredSelectors.sort((a, b) => b.score - a.score);
        return scoredSelectors[0];
    }

    /**
     * Check if selector is unique (matches only one element)
     */
    isUniqueSelector(selector) {
        try {
            const elements = document.querySelectorAll(selector);
            return elements.length === 1;
        } catch (e) {
            return false;
        }
    }

    /**
     * Check if selector is reliable (not too broad, not too narrow)
     */
    isReliableSelector(selector, targetElement) {
        try {
            const elements = document.querySelectorAll(selector);
            const count = elements.length;
            
            // Too broad (matches too many elements)
            if (count > 20) return false;
            
            // Doesn't match target element
            if (!Array.from(elements).includes(targetElement)) return false;
            
            // Just right
            return count >= 1 && count <= 20;
        } catch (e) {
            return false;
        }
    }

    /**
     * Calculate reliability score for a selector
     */
    calculateSelectorReliability(selector, targetElement) {
        try {
            const elements = document.querySelectorAll(selector);
            const count = elements.length;
            
            if (count === 0) return 0;
            if (!Array.from(elements).includes(targetElement)) return 0;
            
            // Prefer selectors that match fewer elements (more specific)
            if (count === 1) return 1.0;
            if (count <= 3) return 0.9;
            if (count <= 5) return 0.8;
            if (count <= 10) return 0.6;
            if (count <= 20) return 0.4;
            
            return 0.2; // Too broad
        } catch (e) {
            return 0;
        }
    }

    // Helper methods for structural selectors
    getNthChildPosition(element) {
        const parent = element.parentElement;
        if (!parent) return null;
        
        const children = Array.from(parent.children);
        const index = children.indexOf(element);
        return index !== -1 ? index + 1 : null;
    }

    getNthOfTypePosition(element) {
        const parent = element.parentElement;
        if (!parent) return null;
        
        const siblings = Array.from(parent.children).filter(
            child => child.tagName === element.tagName
        );
        const index = siblings.indexOf(element);
        return index !== -1 ? index + 1 : null;
    }

    getSimpleParentSelector(parent) {
        if (!parent || parent === document.body) return null;
        
        const id = parent.id;
        if (id && !id.startsWith('v3-')) {
            return `#${id}`;
        }
        
        const classes = Array.from(parent.classList).filter(cls => !cls.startsWith('v3-'));
        if (classes.length > 0) {
            return `.${classes[0]}`;
        }
        
        return parent.tagName.toLowerCase();
    }

    generateHierarchicalPath(element, maxLevels = 3) {
        const path = [];
        let current = element;
        let levels = 0;
        
        while (current && current !== document.body && levels < maxLevels) {
            const tagName = current.tagName.toLowerCase();
            const classes = Array.from(current.classList).filter(cls => !cls.startsWith('v3-'));
            
            if (classes.length > 0) {
                path.unshift(`${tagName}.${classes[0]}`);
            } else {
                path.unshift(tagName);
            }
            
            current = current.parentElement;
            levels++;
        }
        
        return path.length > 1 ? path.join(' > ') : null;
    }
    
    generateRelativeSelector(element, container) {
        // Generate selector relative to container
        const containerElement = document.querySelector(container.selector);
        if (!containerElement || !containerElement.contains(element)) {
            return this.generateSelector(element);
        }
        
        const path = [];
        let current = element;
        
        while (current && current !== containerElement) {
            const tagName = current.tagName.toLowerCase();
            const classes = Array.from(current.classList).filter(cls => !cls.startsWith('v3-'));
            
            if (classes.length > 0) {
                path.unshift(`${tagName}.${classes.join('.')}`);
            } else {
                path.unshift(tagName);
            }
            
            current = current.parentElement;
        }
        
        return path.join(' > ');
    }
    
    findSimilarElements(targetElement) {
        console.log('🔍 Finding similar elements with enhanced validation...');
        
        // Use the hierarchical selector system
        const selector = this.generateSelector(targetElement);
        let elements = Array.from(document.querySelectorAll(selector))
            .filter(el => !this.isIgnoredElement(el));
        
        console.log(`Found ${elements.length} elements with primary selector: ${selector}`);
        
        // If primary selector gives poor results, try alternative strategies
        if (elements.length < 2 || elements.length > 50) {
            console.log('🔄 Primary selector results suboptimal, trying alternative strategies...');
            
            const fallbackSelectors = this.generateFallbackSelectors(targetElement);
            
            // Try each fallback selector until we get reasonable results
            for (const selectorObj of fallbackSelectors) {
                if (selectorObj.selector === selector) continue; // Skip the one we already tried
                
                try {
                    const candidateElements = Array.from(document.querySelectorAll(selectorObj.selector))
                        .filter(el => !this.isIgnoredElement(el));
                    
                    // Good range: 2-20 elements
                    if (candidateElements.length >= 2 && candidateElements.length <= 20) {
                        console.log(`✅ Using fallback selector: ${selectorObj.selector} (${candidateElements.length} elements)`);
                        elements = candidateElements;
                        break;
                    }
                } catch (e) {
                    console.debug(`Invalid selector: ${selectorObj.selector}`);
                }
            }
        }
        
        // Validate that target element is included
        if (!elements.includes(targetElement)) {
            console.warn('⚠️ Target element not found in similar elements, adding it');
            elements.unshift(targetElement);
        }
        
        // Additional filtering for quality
        const qualityElements = this.filterSimilarElementsByQuality(elements, targetElement);
        
        console.log(`✅ Final similar elements count: ${qualityElements.length}`);
        return qualityElements;
    }

    /**
     * Filter similar elements by quality and relevance
     */
    filterSimilarElementsByQuality(elements, targetElement) {
        if (elements.length <= 3) return elements; // Keep small sets as-is
        
        // Calculate similarity scores
        const scoredElements = elements.map(el => ({
            element: el,
            score: this.calculateElementSimilarity(el, targetElement)
        }));
        
        // Filter out elements with very low similarity
        const filtered = scoredElements
            .filter(item => item.score >= 0.3) // Minimum 30% similarity
            .sort((a, b) => b.score - a.score)
            .slice(0, 20) // Max 20 elements
            .map(item => item.element);
        
        return filtered;
    }

    /**
     * Calculate similarity score between two elements
     */
    calculateElementSimilarity(element1, element2) {
        let score = 0;
        let factors = 0;
        
        // Tag name similarity (30%)
        if (element1.tagName === element2.tagName) {
            score += 0.3;
        }
        factors += 0.3;
        
        // Class similarity (25%)
        const classes1 = Array.from(element1.classList).filter(c => !c.startsWith('v3-'));
        const classes2 = Array.from(element2.classList).filter(c => !c.startsWith('v3-'));
        const intersection = classes1.filter(c => classes2.includes(c));
        const union = [...new Set([...classes1, ...classes2])];
        
        if (union.length > 0) {
            score += 0.25 * (intersection.length / union.length);
        }
        factors += 0.25;
        
        // Text content similarity (20%)
        const text1 = element1.textContent.trim();
        const text2 = element2.textContent.trim();
        if (text1 && text2) {
            const lengthDiff = Math.abs(text1.length - text2.length);
            const maxLength = Math.max(text1.length, text2.length);
            score += 0.2 * (1 - lengthDiff / Math.max(maxLength, 1));
        }
        factors += 0.2;
        
        // Structure similarity (15%)
        const children1 = element1.children.length;
        const children2 = element2.children.length;
        if (children1 === children2) {
            score += 0.15;
        } else if (Math.abs(children1 - children2) <= 1) {
            score += 0.1; // Close enough
        }
        factors += 0.15;
        
        // Attributes similarity (10%)
        const attrs1 = Array.from(element1.attributes).map(a => a.name);
        const attrs2 = Array.from(element2.attributes).map(a => a.name);
        const attrIntersection = attrs1.filter(a => attrs2.includes(a));
        const attrUnion = [...new Set([...attrs1, ...attrs2])];
        
        if (attrUnion.length > 0) {
            score += 0.1 * (attrIntersection.length / attrUnion.length);
        }
        factors += 0.1;
        
        return factors > 0 ? score / factors : 0;
    }
    
    detectFieldType(element) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        const href = element.getAttribute('href');
        const src = element.getAttribute('src');
        
        if (tagName === 'img' || src) return 'image';
        if (tagName === 'a' || href) return 'link';
        if (text.match(/\$[\d,]+\.?\d*/)) return 'price';
        if (text.match(/[\w\.-]+@[\w\.-]+\.\w+/)) return 'email';
        if (text.match(/\(\d{3}\)\s*\d{3}-\d{4}/)) return 'phone';
        
        return 'text';
    }
    
    detectActionType(element) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim().toLowerCase();
        const type = element.getAttribute('type');
        
        if (tagName === 'button' || type === 'submit') return 'button';
        if (tagName === 'a') return 'link';
        if (text.includes('next') || text.includes('more')) return 'pagination';
        if (text.includes('load')) return 'load_more';
        
        return 'click';
    }
    
    generateContainerLabel(element) {
        const classes = Array.from(element.classList);
        if (classes.length > 0) {
            return classes[0].replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        return `${element.tagName.toLowerCase()} container`;
    }
    
    generateFieldLabel(element, fieldType) {
        const text = element.textContent.trim();
        if (text.length > 0 && text.length < 30) {
            return text.replace(/[^a-zA-Z0-9\s]/g, '').trim().toLowerCase().replace(/\s+/g, '_');
        }
        return fieldType;
    }
    
    generateActionLabel(element, actionType) {
        const text = element.textContent.trim();
        if (text.length > 0 && text.length < 30) {
            return text.toLowerCase().replace(/\s+/g, '_');
        }
        return actionType;
    }
    
    getSampleText(element) {
        const text = element.textContent.trim();
        return text.length > 50 ? text.substring(0, 50) + '...' : text;
    }
    
    highlightElement(element, color, label = '', persistent = false, elementId = null) {
        element.style.outline = `2px solid ${color}`;
        element.style.outlineOffset = '1px';
        
        // Only set background for non-persistent highlights (hover)
        if (!persistent) {
            element.style.backgroundColor = color;
        } else {
            // For persistent highlights, use a subtle box-shadow instead of background
            element.style.boxShadow = `inset 0 0 0 2px ${color}`;
        }
        
        if (persistent) {
            element.classList.add('v3-highlighted');
            if (elementId) {
                element.setAttribute('data-v3-element-id', elementId);
            }
        }
        
        if (label) {
            this.addElementLabel(element, label, color, elementId);
        }
    }
    
    addElementLabel(element, text, color, elementId = null) {
        const label = this.createElement('div', {
            textContent: text,
            style: `
                position: absolute;
                background: ${color.replace('0.3', '0.9')};
                color: white;
                padding: 2px 6px;
                font-size: 10px;
                border-radius: 3px;
                z-index: 1000001;
                pointer-events: none;
                font-family: monospace;
                font-weight: bold;
            `,
            class: 'v3-element-label'
        });
        
        if (elementId) {
            label.setAttribute('data-element-id', elementId);
            label.classList.add('v3-highlighted');
        }
        
        const rect = element.getBoundingClientRect();
        label.style.top = (rect.top + window.scrollY - 20) + 'px';
        label.style.left = (rect.left + window.scrollX) + 'px';
        
        document.body.appendChild(label);
    }
    
    clearHoverHighlight() {
        if (this.selectionBuffer.hoveredElement) {
            if (!this.selectionBuffer.hoveredElement.classList.contains('v3-highlighted')) {
                this.selectionBuffer.hoveredElement.style.outline = '';
                this.selectionBuffer.hoveredElement.style.backgroundColor = '';
                this.selectionBuffer.hoveredElement.style.boxShadow = '';
            }
        }
    }
    
    clearAllHighlights() {
        // Remove outlines from non-persistent highlights
        document.querySelectorAll('*').forEach(el => {
            if (!el.classList.contains('v3-highlighted')) {
                el.style.outline = '';
                el.style.backgroundColor = '';
                el.style.boxShadow = '';
            }
        });
        
        // Remove labels
        document.querySelectorAll('.v3-element-label').forEach(label => {
            label.remove();
        });
    }
    
    clearPreviewHighlights() {
        // Clear ALL highlights including persistent ones during preview toggle
        document.querySelectorAll('*').forEach(el => {
            el.style.outline = '';
            el.style.backgroundColor = '';
            el.style.boxShadow = '';
            // Don't remove v3-highlighted class as those are user-selected elements
        });
        
        // Remove all labels
        document.querySelectorAll('.v3-element-label').forEach(label => {
            label.remove();
        });
    }
    
    updateInspector(element) {
        if (!this.ui.inspector || this.ui.inspector.style.display === 'none') {
            this.ui.inspector.style.display = 'block';
        }
        
        const infoEl = this.ui.inspector.querySelector('#element-info');
        const pathEl = this.ui.inspector.querySelector('#element-path');
        const attrsEl = this.ui.inspector.querySelector('#element-attributes');
        
        // Element info
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        const id = element.id;
        const classes = Array.from(element.classList);
        
        infoEl.innerHTML = `
            <strong>${tagName.toUpperCase()}</strong>
            ${id ? `<span style="color: #007bff;">#${id}</span>` : ''}
            ${classes.length ? `<span style="color: #28a745;">.${classes.join('.')}</span>` : ''}
        `;
        
        // Element path
        pathEl.textContent = this.generateSelector(element);
        
        // Attributes
        const attrs = Array.from(element.attributes)
            .filter(attr => !attr.name.startsWith('style'))
            .map(attr => `${attr.name}="${attr.value}"`)
            .slice(0, 5);
        
        attrsEl.innerHTML = attrs.length ? 
            `<strong>Attributes:</strong><br>${attrs.join('<br>')}` : 
            '<em>No relevant attributes</em>';
        
        // Sample text
        if (text && text.length > 0) {
            const sampleEl = document.createElement('div');
            sampleEl.style.cssText = 'margin-top: 8px; font-size: 11px; color: #666;';
            sampleEl.innerHTML = `<strong>Text:</strong> ${text.length > 100 ? text.substring(0, 100) + '...' : text}`;
            attrsEl.appendChild(sampleEl);
        }
    }
    
    updateSidebar() {
        if (!this.ui.sidebar) return;
        
        // Update containers list
        const containersList = this.ui.sidebar.querySelector('#containers-list');
        if (this.state.containers.length === 0) {
            containersList.innerHTML = '<div style="color: #666; font-size: 12px; font-style: italic;">No containers added yet</div>';
        } else {
            containersList.innerHTML = this.state.containers.map((container, index) => `
                <div style="border: 1px solid #ddd; border-radius: 6px; padding: 8px; margin-bottom: 8px; background: #f8f9fa; position: relative;">
                    <button class="remove-container-btn" data-container-id="${container.id}" data-container-index="${index}" 
                            style="position: absolute; top: 4px; right: 4px; background: #dc3545; color: white; border: none; 
                                   border-radius: 50%; width: 18px; height: 18px; font-size: 10px; cursor: pointer; 
                                   display: flex; align-items: center; justify-content: center; font-weight: bold;
                                   line-height: 1; padding: 0;" title="Remove container">×</button>
                    <div style="font-weight: 500; color: #333; font-size: 13px; padding-right: 25px;">${container.label}</div>
                    <div style="font-size: 11px; color: #666; margin: 4px 0;">${container.count} items</div>
                    <div style="font-size: 10px; color: #999; font-family: monospace;">${container.selector}</div>
                    ${container.sub_elements.length > 0 ? `
                        <div style="margin-top: 6px; font-size: 11px;">
                            <strong>Fields:</strong> ${container.sub_elements.map(field => `
                                <span style="position: relative; display: inline-block; margin-right: 8px;">
                                    ${field.label}
                                    <button class="remove-field-btn" data-field-id="${field.id}" data-container-id="${container.id}"
                                            style="background: #dc3545; color: white; border: none; border-radius: 50%; 
                                                   width: 14px; height: 14px; font-size: 8px; cursor: pointer; margin-left: 3px;
                                                   display: inline-flex; align-items: center; justify-content: center; 
                                                   font-weight: bold; line-height: 1; padding: 0; vertical-align: middle;" 
                                            title="Remove field">×</button>
                                </span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
        
        // Update fields list
        const fieldsList = this.ui.sidebar.querySelector('#fields-list');
        const allFields = this.state.containers.flatMap(c => c.sub_elements);
        const standaloneFields = this.state.fields || [];
        const combinedFields = [...allFields, ...standaloneFields];
        
        if (combinedFields.length === 0) {
            fieldsList.innerHTML = '<div style="color: #666; font-size: 12px; font-style: italic;">No fields added yet</div>';
        } else {
            fieldsList.innerHTML = combinedFields.map(field => `
                <div style="border: 1px solid #ddd; border-radius: 6px; padding: 6px; margin-bottom: 6px; background: #f8f9fa; position: relative;">
                    <button class="remove-field-btn" data-field-id="${field.id}" 
                            style="position: absolute; top: 4px; right: 4px; background: #dc3545; color: white; border: none; 
                                   border-radius: 50%; width: 16px; height: 16px; font-size: 9px; cursor: pointer; 
                                   display: flex; align-items: center; justify-content: center; font-weight: bold;
                                   line-height: 1; padding: 0;" title="Remove field">×</button>
                    <div style="font-weight: 500; color: #333; font-size: 12px; padding-right: 20px;">${field.label}</div>
                    <div style="font-size: 10px; color: #666;">${field.element_type}</div>
                    ${field.sample_text ? `<div style="font-size: 9px; color: #999; font-style: italic;">"${field.sample_text}"</div>` : ''}
                </div>
            `).join('');
        }
        
        // Update actions list
        const actionsList = this.ui.sidebar.querySelector('#actions-list');
        if (this.state.actions.length === 0) {
            actionsList.innerHTML = '<div style="color: #666; font-size: 12px; font-style: italic;">No actions added yet</div>';
        } else {
            actionsList.innerHTML = this.state.actions.map((action, index) => `
                <div style="border: 1px solid #ddd; border-radius: 6px; padding: 6px; margin-bottom: 6px; background: #f8f9fa; position: relative;">
                    <button class="remove-action-btn" data-action-id="${action.id}" data-action-index="${index}" 
                            style="position: absolute; top: 4px; right: 4px; background: #dc3545; color: white; border: none; 
                                   border-radius: 50%; width: 16px; height: 16px; font-size: 9px; cursor: pointer; 
                                   display: flex; align-items: center; justify-content: center; font-weight: bold;
                                   line-height: 1; padding: 0;" title="Remove action">×</button>
                    <div style="font-weight: 500; color: #333; font-size: 12px; padding-right: 20px;">${action.label}</div>
                    <div style="font-size: 10px; color: #666;">${action.action_type}</div>
                </div>
            `).join('');
        }
    }
    
    showNotification(message, type = 'success') {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        const notification = this.createElement('div', {
            textContent: message,
            style: `
                position: fixed;
                top: 100px;
                right: 20px;
                background: ${colors[type] || colors.success};
                color: ${type === 'warning' ? 'black' : 'white'};
                padding: 12px 16px;
                border-radius: 6px;
                z-index: 1000002;
                font-size: 14px;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideIn 0.3s ease;
                max-width: 300px;
                word-wrap: break-word;
            `
        });
        
        // Add CSS animation if not already present
        if (!document.querySelector('#v3-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'v3-notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Log notification to console as well
        const logMethod = type === 'error' ? 'error' : type === 'warning' ? 'warn' : 'log';
        console[logMethod](`📢 Notification (${type}): ${message}`);
        
        setTimeout(() => {
            notification.remove();
        }, type === 'error' ? 5000 : 3000);
    }
    
    // Public API methods
    
    start() {
        this.state.isActive = true;
        this.ui.overlay.style.display = 'block';
        this.ui.sidebar.style.display = 'block';
        this.ui.realTimeLogger.style.display = 'block';
        this.setMode('container');
        
        this.logInteraction('OVERLAY_START', {
            timestamp: new Date().toISOString(),
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            url: window.location.href,
            userAgent: navigator.userAgent
        });
        
        console.log('🎯 V3 Interactive Overlay started');
        this.showNotification('Interactive mode activated! Select containers, fields, and actions.');
    }
    
    stop() {
        this.state.isActive = false;
        this.ui.overlay.style.display = 'none';
        this.clearAllHighlights();
        document.body.style.cursor = 'default';
        
        console.log('🎯 V3 Interactive Overlay stopped');
    }
    
    toggle() {
        if (this.state.isActive) {
            this.stop();
        } else {
            this.start();
        }
    }
    
    exit() {
        // Send exit signal to Python backend
        localStorage.setItem('v3-session-exit', JSON.stringify({
            timestamp: new Date().toISOString(),
            reason: 'user_exit'
        }));
        
        // Also try communication bridge if available
        if (window.v3CommunicationBridge && typeof window.v3CommunicationBridge.exitSession === 'function') {
            window.v3CommunicationBridge.exitSession();
        }
        
        this.stop();
        
        console.log('🚪 Exit signal sent to Python backend');
        this.showNotification('Exit signal sent - browser should close shortly', 'info');
    }
    
    reset() {
        this.state.containers = [];
        this.state.fields = [];
        this.state.actions = [];
        this.state.currentContainer = null;
        this.clearAllHighlights();
        this.updateSidebar();
        
        console.log('🔄 Template reset');
        this.showNotification('Template reset');
    }
    
    // Collapsible panel functionality
    toggleSidebar() {
        const content = document.getElementById('sidebar-content');
        const toggle = document.getElementById('sidebar-toggle');
        
        if (content && toggle) {
            const isCollapsed = content.style.display === 'none';
            
            if (isCollapsed) {
                content.style.display = 'block';
                toggle.textContent = '−';
                toggle.title = 'Collapse Template Builder';
            } else {
                content.style.display = 'none';
                toggle.textContent = '+';
                toggle.title = 'Expand Template Builder';
            }
        }
    }
    
    toggleInspector() {
        const content = this.ui.inspector.querySelector('.inspector-content');
        const toggle = document.getElementById('inspector-toggle');
        
        if (content && toggle) {
            const isCollapsed = content.style.display === 'none';
            
            if (isCollapsed) {
                content.style.display = 'block';
                toggle.textContent = '−';
                toggle.title = 'Collapse Element Inspector';
            } else {
                content.style.display = 'none';
                toggle.textContent = '+';
                toggle.title = 'Expand Element Inspector';
            }
        }
    }
    
    exportTemplate() {
        console.log('🚀 Starting template export process...');
        
        try {
            const template = this.buildTemplate();
            console.log('📦 Template built successfully:', template);
            
            // Enhanced logging for debugging
            console.log('📊 Template stats:', {
                containers: template.containers?.length || 0,
                totalFields: template.containers?.reduce((sum, c) => sum + (c.sub_elements?.length || 0), 0) || 0,
                actions: template.actions?.length || 0,
                url: template.url,
                version: template.version
            });
            
            // Check for export methods
            const hasPyodide = !!window.pyodide;
            const hasV3Python = !!window.exportToV3Python;
            const hasBridge = !!window.v3CommunicationBridge;
            
            console.log('🔍 Export methods available:', {
                pyodide: hasPyodide,
                v3Python: hasV3Python,
                bridge: hasBridge
            });
            
            let exportSuccess = false;
            
            // Try communication bridge first
            if (hasBridge) {
                console.log('📡 Using V3 Communication Bridge...');
                try {
                    window.v3CommunicationBridge.exportToV3Python(template);
                    exportSuccess = true;
                    console.log('✅ Bridge export successful');
                } catch (bridgeError) {
                    console.error('❌ Bridge export failed:', bridgeError);
                }
            }
            
            // Try direct Python export
            if (!exportSuccess && hasV3Python) {
                console.log('🐍 Using direct Python export...');
                try {
                    window.exportToV3Python(template);
                    exportSuccess = true;
                    console.log('✅ Direct Python export successful');
                } catch (pythonError) {
                    console.error('❌ Direct Python export failed:', pythonError);
                }
            }
            
            // Try Pyodide export
            if (!exportSuccess && hasPyodide) {
                console.log('🔬 Using Pyodide export...');
                try {
                    window.pyodide.globals.set('v3_template', template);
                    exportSuccess = true;
                    console.log('✅ Pyodide export successful');
                } catch (pyodideError) {
                    console.error('❌ Pyodide export failed:', pyodideError);
                }
            }
            
            // Fallback to JSON download
            if (!exportSuccess) {
                console.log('💾 Falling back to JSON download...');
                this.downloadJSON(template, `v3-template-${Date.now()}.json`);
                exportSuccess = true;
                console.log('✅ JSON download initiated');
            }
            
            // Store template locally for debugging
            try {
                localStorage.setItem('v3-last-exported-template', JSON.stringify(template));
                console.log('💿 Template stored in localStorage for debugging');
            } catch (storageError) {
                console.warn('⚠️ Could not store template in localStorage:', storageError);
            }
            
            this.showNotification('Template exported successfully!');
            console.log('🎉 Template export process completed successfully');
            
        } catch (error) {
            console.error('💥 Template export failed:', error);
            console.error('📍 Error stack:', error.stack);
            
            // Show detailed error to user
            this.showNotification(`Export failed: ${error.message}`, 'error');
            
            // Try to provide fallback information
            console.log('🔧 Debug info for troubleshooting:');
            console.log('- Current state:', this.state);
            console.log('- Available window methods:', Object.keys(window).filter(k => k.includes('v3') || k.includes('export')));
        }
    }
    
    buildTemplate() {
        // Auto-generate meaningful name using full domain
        const domain = this.extractFullDomain(window.location.href);
        const timestamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15); // YYYYMMDD_HHMMSS
        const defaultName = `${domain}_scraper_${timestamp}`;
        
        // Ensure we have some extractable content structure
        let containers = this.state.containers || [];
        let singleElements = [];
        
        // If no containers but we have fields, convert them to single_elements
        if (containers.length === 0 && this.state.fields && this.state.fields.length > 0) {
            singleElements = this.state.fields;
        }
        
        // Note: Per requirements, don't auto-create containers for empty selections
        
        return {
            version: '3.0', // Configurable version per requirements
            name: defaultName,
            url: window.location.href,
            created_at: new Date().toISOString(),
            containers: containers,
            single_elements: singleElements,
            fields: this.state.fields || [],  // Keep for backward compatibility
            actions: this.state.actions || [],
            flow: {
                navigation_type: this.determineNavigationType(),
                max_pages: 10
            },
            extraction_strategy: containers.length > 0 ? 'MULTI_PAGE' : 'SINGLE_PAGE'
        };
    }
    
    extractFullDomain(url) {
        try {
            const hostname = new URL(url).hostname;
            // Keep full domain but remove www prefix
            const domain = hostname.startsWith('www.') ? hostname.slice(4) : hostname;
            // Clean for filename usage
            return domain.replace(/[^a-zA-Z0-9.-_]/g, '') || 'unknown-site';
        } catch {
            return 'unknown-site';
        }
    }
    
    determineNavigationType() {
        const hasLoadMore = this.state.actions.some(a => a.action_type === 'load_more');
        const hasPagination = this.state.actions.some(a => a.action_type === 'pagination');
        
        if (hasLoadMore) return 'LOAD_MORE_BUTTON';
        if (hasPagination) return 'URL_PAGINATION';
        return 'NONE';
    }
    
    downloadJSON(data, filename) {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    previewTemplate() {
        // Toggle preview state
        if (this.state.isPreviewActive) {
            // Turn off preview - clear all persistent highlights and restore original state
            this.clearPreviewHighlights();
            this.state.isPreviewActive = false;
            this.showNotification('Template preview disabled');
            
            // Update button text if it exists
            const previewBtn = document.getElementById('preview-template');
            if (previewBtn) {
                previewBtn.textContent = '👁️ Preview';
                previewBtn.style.background = '#17a2b8';
            }
        } else {
            // Turn on preview
            const template = this.buildTemplate();
            console.log('👁️ Template preview:', template);
            
            // Show preview modal or highlight all selected elements
            this.clearAllHighlights();
            
            this.state.containers.forEach(container => {
                const elements = document.querySelectorAll(container.selector);
                elements.forEach(el => {
                    this.highlightElement(el, this.config.highlightColors.container, 'Container', true);
                    
                    container.sub_elements.forEach(field => {
                        const fieldEl = el.querySelector(field.selector);
                        if (fieldEl) {
                            this.highlightElement(fieldEl, this.config.highlightColors.field, field.label, true);
                        }
                    });
                });
            });
            
            this.state.actions.forEach(action => {
                const elements = document.querySelectorAll(action.selector);
                elements.forEach(el => {
                    this.highlightElement(el, this.config.highlightColors.action, action.label, true);
                });
            });
            
            this.state.isPreviewActive = true;
            this.showNotification('Template preview active - all elements highlighted');
            
            // Update button text if it exists
            const previewBtn = document.getElementById('preview-template');
            if (previewBtn) {
                previewBtn.textContent = '🛑 Stop Preview';
                previewBtn.style.background = '#dc3545';
            }
        }
    }
    
    testTemplate() {
        // Run a quick test extraction
        const results = [];
        
        this.state.containers.forEach(container => {
            const containerElements = document.querySelectorAll(container.selector);
            
            containerElements.forEach((el, index) => {
                if (index >= 3) return; // Test only first 3 items
                
                const item = {};
                
                container.sub_elements.forEach(field => {
                    const fieldEl = el.querySelector(field.selector);
                    if (fieldEl) {
                        if (field.element_type === 'link') {
                            item[field.label] = fieldEl.getAttribute('href');
                        } else if (field.element_type === 'image') {
                            item[field.label] = fieldEl.getAttribute('src');
                        } else {
                            item[field.label] = fieldEl.textContent.trim();
                        }
                    }
                });
                
                if (Object.keys(item).length > 0) {
                    results.push(item);
                }
            });
        });
        
        console.log('🧪 Template test results:', results);
        
        // Show results using the notification system instead of alerts
        if (results.length > 0) {
            this.showNotification(`Test successful! Extracted ${results.length} items. Check console for details.`, 'success');
            
            // Also create a visual display of results
            this.displayTestResults(results);
        } else {
            this.showNotification('Test failed - no data extracted. Check your selectors.', 'error');
        }
    }
    
    displayTestResults(results) {
        // Create a modal-style display for test results
        const modal = this.createElement('div', {
            style: `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                z-index: 1000005;
                max-width: 80%;
                max-height: 80%;
                overflow: auto;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `
        });
        
        modal.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #eee; padding-bottom: 16px;">
                <h3 style="margin: 0; color: #333;">🧪 Test Results (${results.length} items)</h3>
                <button id="close-test-results" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 8px 12px; cursor: pointer;">Close</button>
            </div>
            <div style="max-height: 400px; overflow-y: auto;">
                ${results.map((item, index) => `
                    <div style="border: 1px solid #ddd; border-radius: 4px; margin-bottom: 12px; padding: 12px; background: #f9f9f9;">
                        <h4 style="margin: 0 0 8px 0; color: #555;">Item ${index + 1}</h4>
                        ${Object.entries(item).map(([key, value]) => `
                            <div style="margin-bottom: 4px;">
                                <strong style="color: #333;">${key}:</strong> 
                                <span style="color: #666; word-break: break-word;">${value}</span>
                            </div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add close functionality
        modal.querySelector('#close-test-results').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        document.body.appendChild(modal);
        
        // Auto-close after 10 seconds
        setTimeout(() => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        }, 10000);
    }
    
    saveTemplate() {
        console.log('💾 Starting template save process...');
        
        try {
            // Build template with full logging
            const template = this.buildTemplate();
            console.log('📋 Template built for saving:', template);
            
            // Save to localStorage
            localStorage.setItem('v3-current-template', JSON.stringify(template));
            console.log('✅ Template saved to localStorage');
            
            // Also create timestamped backup
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const backupKey = `v3-template-backup-${timestamp}`;
            localStorage.setItem(backupKey, JSON.stringify(template));
            console.log(`🗄️ Backup created: ${backupKey}`);
            
            // Export the template
            this.exportTemplate();
            
        } catch (error) {
            console.error('❌ Save template failed:', error);
            this.showNotification(`Save failed: ${error.message}`, 'error');
        }
    }
    
    saveAndExportTemplate() {
        console.log('💾📤 Starting unified save and export process...');
        
        try {
            // Build template with full logging
            const template = this.buildTemplate();
            console.log('📋 Template built for save & export:', template);
            
            // Save to localStorage
            localStorage.setItem('v3-current-template', JSON.stringify(template));
            console.log('✅ Template saved to localStorage');
            
            // Also create timestamped backup
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const backupKey = `v3-template-backup-${timestamp}`;
            localStorage.setItem(backupKey, JSON.stringify(template));
            console.log(`🗄️ Backup created: ${backupKey}`);
            
            // Export the template
            this.exportTemplate();
            
            this.showNotification('Template saved and exported successfully!');
            
        } catch (error) {
            console.error('❌ Save and export failed:', error);
            this.showNotification(`Save & Export failed: ${error.message}`, 'error');
        }
    }
    
    loadTemplate(templateData) {
        // Load a template from data
        this.reset();
        
        if (templateData.containers) {
            this.state.containers = templateData.containers;
        }
        
        if (templateData.actions) {
            this.state.actions = templateData.actions;
        }
        
        this.updateSidebar();
        this.showNotification('Template loaded successfully');
    }
    
    // Integration with V3 async system
    integrateWithV3Session(sessionData) {
        console.log('🔗 Integrating with V3 session:', sessionData);
        
        // If we have cookie data, this could inform our selection
        if (sessionData && sessionData.cookies) {
            console.log('🍪 Session has cookie data');
        }
        
        // Update UI to show integration status
        this.showNotification('Integrated with V3 session');
    }
    
    // Real-time logging system
    logInteraction(type, data) {
        // Check if logging is enabled
        if (!this.logger.enabled) {
            return;
        }
        
        // Skip hover events if hover logging is disabled
        if (type === 'ELEMENT_HOVER' && this.logger.excludeHover) {
            return;
        }
        
        const timestamp = Date.now();
        const logEntry = {
            id: `log_${timestamp}`,
            type: type,
            data: data,
            timestamp: timestamp,
            relativeTime: timestamp - this.logger.startTime,
            url: window.location.href
        };
        
        // Add to logs array
        this.logger.logs.push(logEntry);
        
        // Keep only last N logs
        if (this.logger.logs.length > this.logger.maxLogs) {
            this.logger.logs.shift();
        }
        
        // Console logging with detailed info
        const timeStr = new Date(timestamp).toLocaleTimeString();
        const relativeStr = `+${Math.round(logEntry.relativeTime / 1000)}s`;
        
        console.group(`🎯 [${timeStr}] [${relativeStr}] ${type}`);
        console.log('📊 Data:', data);
        console.log('🌐 URL:', window.location.href);
        console.log('⚡ Current State:', {
            mode: this.state.mode,
            containers: this.state.containers.length,
            fields: this.state.fields.length,
            actions: this.state.actions.length,
            currentContainer: this.state.currentContainer?.label || 'None'
        });
        console.groupEnd();
        
        // Update real-time display
        this.updateRealTimeDisplay(logEntry);
        
        // Send to communication bridge if available
        if (window.v3CommunicationBridge) {
            try {
                window.v3CommunicationBridge.sendToPython({
                    type: 'interaction_log',
                    data: logEntry
                });
            } catch (e) {
                // Silent fail for bridge
            }
        }
    }
    
    updateRealTimeDisplay(logEntry) {
        const logContent = document.getElementById('log-content');
        if (!logContent) return;
        
        const logElement = document.createElement('div');
        logElement.style.cssText = `
            margin-bottom: 2px;
            padding: 2px 4px;
            border-left: 2px solid ${this.getLogColor(logEntry.type)};
            font-size: 10px;
            line-height: 1.2;
        `;
        
        const timeStr = new Date(logEntry.timestamp).toLocaleTimeString();
        const dataPreview = this.formatDataPreview(logEntry.data);
        
        logElement.innerHTML = `
            <span style="color: #888;">[${timeStr}]</span>
            <span style="color: ${this.getLogColor(logEntry.type)}; font-weight: bold;">${logEntry.type}</span>
            <span style="color: #ccc;">${dataPreview}</span>
        `;
        
        logContent.appendChild(logElement);
        logContent.scrollTop = logContent.scrollHeight;
        
        // Keep only last 50 visual entries
        while (logContent.children.length > 50) {
            logContent.removeChild(logContent.firstChild);
        }
    }
    
    getLogColor(type) {
        const colors = {
            'ELEMENT_CLICK': '#00ff00',
            'ELEMENT_HOVER': '#888888', // Dimmed for less visual noise
            'BUTTON_CLICK': '#ff6600',
            'TOOLBAR_CLICK': '#0099ff',
            'MODE_CHANGE': '#ff00ff',
            'CONTAINER_CREATED': '#00ffff',
            'FIELD_ADDED': '#99ff00',
            'ACTION_CREATED': '#ff9900',
            'TEMPLATE_SAVE': '#ff0066',
            'AUTO_DETECTION': '#9966ff',
            'ERROR': '#ff0000',
            'WARNING': '#ffaa00',
            'HOVER_LOGGING_DISABLED': '#e74c3c',
            'HOVER_LOGGING_ENABLED': '#27ae60',
            'LOGGING_RESUMED': '#27ae60'
        };
        return colors[type] || '#cccccc';
    }
    
    formatDataPreview(data) {
        if (!data) return '';
        
        if (data.element && data.element.tagName) {
            return ` → ${data.element.tagName}${data.element.className ? '.' + data.element.className.split(' ')[0] : ''}`;
        }
        
        if (data.mode) {
            return ` → Mode: ${data.mode}`;
        }
        
        if (data.type) {
            return ` → ${data.type}`;
        }
        
        if (data.container) {
            return ` → Container: ${data.container}`;
        }
        
        return ` → ${JSON.stringify(data).substring(0, 30)}...`;
    }
    
    getElementAttributes(element) {
        const attrs = {};
        for (let i = 0; i < element.attributes.length; i++) {
            const attr = element.attributes[i];
            attrs[attr.name] = attr.value;
        }
        return attrs;
    }
    
    clearLogs() {
        this.logger.logs = [];
        const logContent = document.getElementById('log-content');
        if (logContent) {
            logContent.innerHTML = '';
        }
        console.clear();
        if (this.logger.enabled) {
            this.logInteraction('LOGS_CLEARED', { reason: 'USER_ACTION' });
        }
    }
    
    toggleLogger() {
        const logContent = document.getElementById('log-content');
        const toggleBtn = document.getElementById('toggle-logger');
        
        if (logContent && toggleBtn) {
            const isCollapsed = logContent.style.display === 'none';
            
            if (isCollapsed) {
                logContent.style.display = 'block';
                toggleBtn.textContent = '−';
                this.ui.realTimeLogger.style.height = 'auto';
            } else {
                logContent.style.display = 'none';
                toggleBtn.textContent = '+';
                this.ui.realTimeLogger.style.height = '40px';
            }
            
            if (this.logger.enabled) {
                this.logInteraction('LOGGER_TOGGLE', { expanded: isCollapsed });
            }
        }
    }
    
    toggleLogging() {
        this.logger.enabled = !this.logger.enabled;
        const pauseBtn = document.getElementById('pause-logs');
        
        if (pauseBtn) {
            if (this.logger.enabled) {
                pauseBtn.textContent = 'Pause';
                pauseBtn.style.background = '#444';
                pauseBtn.title = 'Pause logging';
                console.log('🟢 Real-time logging resumed');
                this.logInteraction('LOGGING_RESUMED', { reason: 'USER_ACTION' });
            } else {
                pauseBtn.textContent = 'Resume';
                pauseBtn.style.background = '#f39c12';
                pauseBtn.title = 'Resume logging';
                console.log('⏸️ Real-time logging paused');
            }
        }
    }
    
    toggleHoverLogging() {
        this.logger.excludeHover = !this.logger.excludeHover;
        const hoverBtn = document.getElementById('toggle-hover-logs');
        
        if (hoverBtn) {
            if (this.logger.excludeHover) {
                hoverBtn.textContent = 'Hover OFF';
                hoverBtn.style.background = '#e74c3c';
                hoverBtn.title = 'Enable hover logging';
                if (this.logger.enabled) {
                    this.logInteraction('HOVER_LOGGING_DISABLED', { reason: 'USER_ACTION' });
                }
            } else {
                hoverBtn.textContent = 'Hover';
                hoverBtn.style.background = '#444';
                hoverBtn.title = 'Disable hover logging';
                if (this.logger.enabled) {
                    this.logInteraction('HOVER_LOGGING_ENABLED', { reason: 'USER_ACTION' });
                }
            }
        }
    }
    
    minimizeLogger() {
        const logger = this.ui.realTimeLogger;
        if (!logger) return;
        
        const logContent = document.getElementById('log-content');
        const minimizeBtn = document.getElementById('minimize-logger');
        const buttons = logger.querySelector('div').querySelectorAll('button:not(#minimize-logger)');
        
        const isMinimized = logger.classList.contains('minimized');
        
        if (isMinimized) {
            // Restore logger
            logger.classList.remove('minimized');
            if (logContent) logContent.style.display = 'block';
            buttons.forEach(btn => btn.style.display = 'inline-block');
            if (minimizeBtn) {
                minimizeBtn.textContent = '_';
                minimizeBtn.title = 'Minimize logger';
            }
            logger.style.height = 'auto';
            logger.style.width = '';
            if (this.logger.enabled) {
                this.logInteraction('LOGGER_RESTORED', { reason: 'USER_ACTION' });
            }
        } else {
            // Minimize logger
            logger.classList.add('minimized');
            if (logContent) logContent.style.display = 'none';
            buttons.forEach(btn => btn.style.display = 'none');
            if (minimizeBtn) {
                minimizeBtn.textContent = '□';
                minimizeBtn.title = 'Restore logger';
            }
            logger.style.height = '32px';
            logger.style.width = '200px';
            if (this.logger.enabled) {
                this.logInteraction('LOGGER_MINIMIZED', { reason: 'USER_ACTION' });
            }
        }
    }
    
    closeLogger() {
        const logger = this.ui.realTimeLogger;
        if (!logger) return;
        
        logger.style.display = 'none';
        
        if (this.logger.enabled) {
            this.logInteraction('LOGGER_CLOSED', { reason: 'USER_ACTION' });
        }
        
        // Show notification about how to reopen
        this.showNotification('Logger closed. Refresh page to reopen.', 'info');
        
        // Also log to console
        console.log('📊 Real-time logger closed. Refresh page to reopen.');
    }
}

// Initialize when DOM is ready
if (typeof window !== 'undefined') {
    // Make class globally available
    window.V3InteractiveOverlay = V3InteractiveOverlay;
    
    // Auto-initialize instance
    function initializeOverlay() {
        try {
            window.v3InteractiveOverlay = new V3InteractiveOverlay();
            console.log('🎯 V3 Interactive Overlay initialized');
        } catch (error) {
            console.error('Failed to initialize V3 Interactive Overlay:', error);
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeOverlay);
    } else {
        // DOM is already ready
        setTimeout(initializeOverlay, 100);
    }
    
    console.log('🎯 V3 Interactive Overlay module loaded');
    console.log('💡 Press Ctrl+Shift+I to start interactive mode');
    console.log('🔗 Use window.startV3Interactive() to activate programmatically');
}

// Export for module systems (only if in Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { V3InteractiveOverlay };
}