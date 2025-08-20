/**
 * V3 Communication Bridge
 * 
 * Handles communication between JavaScript overlay and Python backend
 * Features:
 * - Template export to Python
 * - Progress reporting
 * - Error handling
 * - Data validation
 */

class V3CommunicationBridge {
    constructor() {
        this.pythonCallbacks = new Map();
        this.messageQueue = [];
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        // Create communication channel with Python
        this.setupPythonBridge();
        
        // Listen for overlay events
        this.setupOverlayIntegration();
        
        console.log('🔗 V3 Communication Bridge initialized');
    }
    
    setupPythonBridge() {
        // Expose bridge to global scope for Python access
        window.v3CommunicationBridge = this;
        window.exportToV3Python = (data) => this.exportToV3Python(data);
        
        // Create event listeners for Python communication
        window.addEventListener('v3-python-message', (event) => {
            this.handlePythonMessage(event.detail);
        });
        
        // Signal that bridge is ready
        window.dispatchEvent(new CustomEvent('v3-bridge-ready', {
            detail: { timestamp: new Date().toISOString() }
        }));
    }
    
    setupOverlayIntegration() {
        // Wait for overlay to be ready
        const checkOverlay = () => {
            const overlay = window.V3InteractiveOverlay || window.v3InteractiveOverlay;
            if (overlay) {
                this.integrateWithOverlay(overlay);
            } else {
                setTimeout(checkOverlay, 100);
            }
        };
        
        checkOverlay();
    }
    
    integrateWithOverlay(overlay) {
        // Validate overlay has required methods
        if (!overlay || typeof overlay !== 'object') {
            console.error('❌ Invalid overlay object provided to communication bridge');
            return;
        }
        
        // Override the overlay's exportTemplate method to use our bridge
        const originalExportTemplate = overlay.exportTemplate ? overlay.exportTemplate.bind(overlay) : null;
        
        overlay.exportTemplate = () => {
            const template = overlay.buildTemplate();
            this.exportToV3Python(template);
            
            // Show success message
            overlay.showNotification('Template sent to Python backend');
            console.log('📤 Template exported via V3 bridge:', template);
        };
        
        // Override saveTemplate to also use the bridge
        const originalSaveTemplate = overlay.saveTemplate ? overlay.saveTemplate.bind(overlay) : null;
        
        overlay.saveTemplate = () => {
            const template = overlay.buildTemplate();
            
            // Save locally and send to Python
            localStorage.setItem('v3-current-template', JSON.stringify(template));
            this.exportToV3Python(template);
            
            overlay.showNotification('Template saved and exported');
            console.log('💾 Template saved via V3 bridge:', template);
        };
        
        // Override saveAndExportTemplate to use the bridge
        const originalSaveAndExportTemplate = overlay.saveAndExportTemplate ? overlay.saveAndExportTemplate.bind(overlay) : null;
        
        overlay.saveAndExportTemplate = () => {
            const template = overlay.buildTemplate();
            
            // Save locally and send to Python
            localStorage.setItem('v3-current-template', JSON.stringify(template));
            
            // Also create timestamped backup
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const backupKey = `v3-template-backup-${timestamp}`;
            localStorage.setItem(backupKey, JSON.stringify(template));
            
            this.exportToV3Python(template);
            
            overlay.showNotification('Template saved and exported successfully!');
            console.log('💾📤 Template saved & exported via V3 bridge:', template);
        };
        
        console.log('🔗 Overlay integrated with communication bridge');
    }
    
    exportToV3Python(templateData) {
        const message = {
            type: 'template_export',
            data: templateData,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        // Validate template data
        if (!this.validateTemplate(templateData)) {
            console.error('❌ Invalid template data:', templateData);
            return false;
        }
        
        // Send to Python via multiple channels
        this.sendToPython(message);
        
        return true;
    }
    
    validateTemplate(template) {
        // Auto-complete missing fields instead of rejecting
        if (!template || typeof template !== 'object') {
            return false;
        }
        
        // Auto-generate missing required fields
        if (!template.name) {
            const domain = this.extractFullDomain(template.url || window.location.href);
            const timestamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15); // YYYYMMDD_HHMMSS
            template.name = `${domain}_scraper_${timestamp}`;
            console.log(`🏷️ Auto-generated template name: ${template.name}`);
        }
        
        if (!template.url) {
            template.url = window.location.href;
            console.log(`🌐 Auto-set URL: ${template.url}`);
        }
        
        if (!template.version) {
            template.version = '3.0';
            console.log('📋 Auto-set version to 3.0');
        }
        
        // Accept templates with containers OR fields OR single_elements OR empty
        const hasContainers = template.containers && template.containers.length > 0;
        const hasFields = template.fields && template.fields.length > 0;
        const hasSingleElements = template.single_elements && template.single_elements.length > 0;
        
        if (!hasContainers && !hasFields && !hasSingleElements) {
            console.warn('⚠️ Template has no extractable content - empty template will be created');
        }
        
        // Validate containers if they exist
        if (template.containers && Array.isArray(template.containers)) {
            for (const container of template.containers) {
                if (!container.selector || !container.label) {
                    console.warn('Invalid container:', container);
                    // Don't reject, just warn
                }
            }
        }
        
        // Always return true after auto-completion
        return true;
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
    
    sendToPython(message) {
        // Method 1: Store in a known location for Python to read
        window.v3ExportData = message;
        
        // Method 2: Use localStorage as a communication channel
        localStorage.setItem('v3-python-message', JSON.stringify(message));
        
        // Method 3: Dispatch custom event
        window.dispatchEvent(new CustomEvent('v3-export-ready', {
            detail: message
        }));
        
        // Method 4: Console output with special marker for Python to detect
        console.log('V3_PYTHON_EXPORT:', JSON.stringify(message));
        
        // Method 5: Store with timestamp for Python polling
        const exportKey = `v3-export-${Date.now()}`;
        localStorage.setItem(exportKey, JSON.stringify(message));
        localStorage.setItem('v3-latest-export-key', exportKey);
        
        // Add to message queue
        this.messageQueue.push(message);
        
        console.log('📡 Message sent to Python via multiple channels:', message.type);
        console.log('🔑 Export key for Python polling:', exportKey);
    }
    
    handlePythonMessage(message) {
        switch (message.type) {
            case 'template_saved':
                this.onTemplateSaved(message.data);
                break;
            case 'error':
                this.onError(message.data);
                break;
            case 'status_update':
                this.onStatusUpdate(message.data);
                break;
            default:
                console.log('🐍 Python message:', message);
        }
    }
    
    onTemplateSaved(data) {
        const overlay = window.V3InteractiveOverlay || window.v3InteractiveOverlay;
        if (overlay) {
            overlay.showNotification(`Template saved: ${data.filename}`);
        }
        console.log('✅ Template saved by Python:', data);
    }
    
    onError(error) {
        const overlay = window.V3InteractiveOverlay || window.v3InteractiveOverlay;
        if (overlay) {
            overlay.showNotification(`Error: ${error.message}`, 'error');
        }
        console.error('❌ Python error:', error);
    }
    
    onStatusUpdate(status) {
        console.log('📊 Python status:', status);
    }
    
    // Public API for Python to call
    
    getLatestTemplate() {
        const overlay = window.V3InteractiveOverlay || window.v3InteractiveOverlay;
        if (overlay && overlay.buildTemplate) {
            return overlay.buildTemplate();
        }
        return null;
    }
    
    getMessageQueue() {
        return [...this.messageQueue];
    }
    
    clearMessageQueue() {
        this.messageQueue = [];
    }
    
    getOverlayState() {
        const overlay = window.V3InteractiveOverlay || window.v3InteractiveOverlay;
        if (overlay) {
            return {
                isActive: overlay.state.isActive,
                mode: overlay.state.mode,
                containers: overlay.state.containers.length,
                fields: overlay.state.containers.reduce((sum, c) => sum + c.sub_elements.length, 0),
                actions: overlay.state.actions.length
            };
        }
        return null;
    }
    
    // Helper methods for Python integration
    
    waitForData(timeout = 5000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            const checkData = () => {
                if (window.v3ExportData) {
                    resolve(window.v3ExportData);
                    return;
                }
                
                if (Date.now() - startTime > timeout) {
                    reject(new Error('Timeout waiting for data'));
                    return;
                }
                
                setTimeout(checkData, 100);
            };
            
            checkData();
        });
    }
    
    injectPythonHelpers() {
        // Helper functions for Python to use
        window.v3Python = {
            getTemplate: () => this.getLatestTemplate(),
            getState: () => this.getOverlayState(),
            waitForData: (timeout) => this.waitForData(timeout),
            sendMessage: (message) => this.handlePythonMessage(message)
        };
    }
}

// Auto-initialize when page loads
if (typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.v3Bridge = new V3CommunicationBridge();
        });
    } else {
        window.v3Bridge = new V3CommunicationBridge();
    }
    
    console.log('🔗 V3 Communication Bridge module loaded');
}

// Export for module systems (only if in Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { V3CommunicationBridge };
}