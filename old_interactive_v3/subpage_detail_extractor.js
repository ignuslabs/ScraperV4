/**
 * V3 Subpage Detail Extractor
 * 
 * Handles configuration of detail page extraction for link actions
 * Features:
 * - Headless page analysis for detail pages
 * - Auto-detection of extractable elements
 * - Modal interface for user selection
 * - Integration with existing V3 overlay system
 */

class V3SubpageDetailExtractor {
    constructor(overlay) {
        this.overlay = overlay;
        this.currentAction = null;
        this.detailPageData = null;
        this.selectedDetailFields = [];
        
        this.init();
    }
    
    init() {
        console.log('🔗 V3 Subpage Detail Extractor initialized');
    }
    
    /**
     * Show detail configuration modal for a link action
     */
    configureDetailExtraction(action) {
        this.currentAction = action;
        this.selectedDetailFields = action.detail_template?.fields || [];
        
        // First, try to fetch and analyze a sample detail page
        this.analyzeDetailPage(action)
            .then(() => {
                this.showDetailConfigModal();
            })
            .catch(error => {
                console.error('❌ Failed to analyze detail page:', error);
                this.showManualConfigModal();
            });
    }
    
    /**
     * Headlessly fetch and analyze a sample detail page
     */
    async analyzeDetailPage(action) {
        this.overlay.showNotification('Analyzing detail page...', 'info');
        
        try {
            // Get sample URL to analyze
            const sampleUrl = await this.getSampleDetailUrl(action);
            if (!sampleUrl) {
                throw new Error('No sample URL found');
            }
            
            console.log('🔍 Analyzing detail page:', sampleUrl);
            
            // Send request to Python backend for headless analysis
            const analysisData = await this.requestDetailPageAnalysis(sampleUrl);
            
            if (analysisData && analysisData.success) {
                this.detailPageData = analysisData.data;
                console.log('✅ Detail page analysis complete:', this.detailPageData);
            } else {
                throw new Error(analysisData?.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('❌ Detail page analysis failed:', error);
            throw error;
        }
    }
    
    /**
     * Get sample URL for detail page analysis
     */
    async getSampleDetailUrl(action) {
        // Find first element matching the action selector
        const linkElement = document.querySelector(action.selector);
        
        if (!linkElement) {
            throw new Error('No link element found for action selector');
        }
        
        // Extract URL from href or data attributes
        let sampleUrl = linkElement.href || 
                       linkElement.getAttribute('data-href') ||
                       linkElement.getAttribute('data-url');
        
        if (!sampleUrl) {
            throw new Error('No URL found in link element');
        }
        
        // Convert relative URLs to absolute
        if (!sampleUrl.startsWith('http')) {
            sampleUrl = new URL(sampleUrl, window.location.href).href;
        }
        
        return sampleUrl;
    }
    
    /**
     * Request detail page analysis from Python backend
     */
    async requestDetailPageAnalysis(url) {
        return new Promise((resolve) => {
            // Store request data for Python to pick up
            const requestData = {
                type: 'detail_page_analysis',
                url: url,
                timestamp: Date.now(),
                requestId: `detail_${Date.now()}`
            };
            
            // Multiple communication channels
            window.v3DetailAnalysisRequest = requestData;
            localStorage.setItem('v3-detail-analysis-request', JSON.stringify(requestData));
            
            // Dispatch event for Python to detect
            window.dispatchEvent(new CustomEvent('v3-detail-analysis-request', {
                detail: requestData
            }));
            
            console.log('📡 Detail analysis request sent:', requestData);
            
            // Poll for response
            this.pollForAnalysisResponse(requestData.requestId, resolve);
        });
    }
    
    /**
     * Poll for analysis response from Python backend
     */
    pollForAnalysisResponse(requestId, resolve) {
        const maxAttempts = 30; // 15 seconds timeout
        let attempts = 0;
        
        const checkResponse = () => {
            attempts++;
            
            // Check for response
            const responseKey = `v3-detail-analysis-response-${requestId}`;
            const response = localStorage.getItem(responseKey);
            
            if (response) {
                try {
                    const responseData = JSON.parse(response);
                    localStorage.removeItem(responseKey); // Clean up
                    resolve(responseData);
                    return;
                } catch (error) {
                    console.error('❌ Failed to parse analysis response:', error);
                }
            }
            
            if (attempts >= maxAttempts) {
                resolve({ success: false, error: 'Analysis timeout' });
                return;
            }
            
            setTimeout(checkResponse, 500);
        };
        
        checkResponse();
    }
    
    /**
     * Show detail configuration modal with analyzed data
     */
    showDetailConfigModal() {
        const modal = this.createDetailConfigModal();
        this.populateAnalyzedElements(modal);
        this.showModal(modal);
    }
    
    /**
     * Show manual configuration modal (fallback)
     */
    showManualConfigModal() {
        const modal = this.createManualConfigModal();
        this.showModal(modal);
    }
    
    /**
     * Create detail configuration modal
     */
    createDetailConfigModal() {
        const modal = document.createElement('div');
        modal.id = 'v3-detail-config-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000010;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; width: 80%; max-width: 800px; max-height: 80%; 
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden;">
                
                <div style="padding: 20px; border-bottom: 1px solid #eee; background: #f8f9fa;">
                    <h3 style="margin: 0; color: #333;">Configure Detail Page Extraction</h3>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                        Select what data to extract from linked detail pages
                    </p>
                </div>
                
                <div id="detail-elements-container" style="padding: 20px; max-height: 400px; overflow-y: auto;">
                    <div id="loading-indicator" style="text-align: center; padding: 40px; color: #666;">
                        <div style="font-size: 16px;">🔍 Analyzing detail page...</div>
                        <div style="font-size: 12px; margin-top: 8px;">Finding extractable elements</div>
                    </div>
                </div>
                
                <div style="padding: 20px; border-top: 1px solid #eee; display: flex; justify-content: space-between;">
                    <button id="cancel-detail-config" style="background: #6c757d; color: white; border: none; 
                            border-radius: 6px; padding: 10px 20px; cursor: pointer;">
                        Cancel
                    </button>
                    <div>
                        <button id="manual-detail-config" style="background: #ffc107; color: black; border: none; 
                                border-radius: 6px; padding: 10px 20px; cursor: pointer; margin-right: 10px;">
                            Manual Config
                        </button>
                        <button id="save-detail-config" style="background: #28a745; color: white; border: none; 
                                border-radius: 6px; padding: 10px 20px; cursor: pointer;">
                            Save Configuration
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        modal.querySelector('#cancel-detail-config').addEventListener('click', () => {
            this.closeModal(modal);
        });
        
        modal.querySelector('#manual-detail-config').addEventListener('click', () => {
            this.closeModal(modal);
            this.showManualConfigModal();
        });
        
        modal.querySelector('#save-detail-config').addEventListener('click', () => {
            this.saveDetailConfiguration();
            this.closeModal(modal);
        });
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });
        
        return modal;
    }
    
    /**
     * Populate modal with analyzed elements
     */
    populateAnalyzedElements(modal) {
        const container = modal.querySelector('#detail-elements-container');
        
        if (!this.detailPageData || !this.detailPageData.suggestions) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #dc3545;">
                    <div style="font-size: 16px;">❌ Analysis failed</div>
                    <div style="font-size: 12px; margin-top: 8px;">Please use manual configuration</div>
                </div>
            `;
            return;
        }
        
        const suggestions = this.detailPageData.suggestions;
        
        container.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #333; margin-bottom: 10px;">📋 Available Fields</h4>
                <p style="color: #666; font-size: 12px; margin-bottom: 15px;">
                    Found ${suggestions.length} extractable elements. Select which ones to include:
                </p>
            </div>
            
            <div id="suggestions-list">
                ${suggestions.map((suggestion, index) => this.createSuggestionItem(suggestion, index)).join('')}
            </div>
            
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;">
                <button id="select-all-suggestions" style="background: #17a2b8; color: white; border: none; 
                        border-radius: 4px; padding: 6px 12px; cursor: pointer; font-size: 12px; margin-right: 10px;">
                    Select All
                </button>
                <button id="clear-all-suggestions" style="background: #6c757d; color: white; border: none; 
                        border-radius: 4px; padding: 6px 12px; cursor: pointer; font-size: 12px;">
                    Clear All
                </button>
            </div>
        `;
        
        // Add event listeners for select/clear all
        container.querySelector('#select-all-suggestions').addEventListener('click', () => {
            this.selectAllSuggestions(true);
        });
        
        container.querySelector('#clear-all-suggestions').addEventListener('click', () => {
            this.selectAllSuggestions(false);
        });
    }
    
    /**
     * Create suggestion item HTML
     */
    createSuggestionItem(suggestion, index) {
        const isSelected = this.selectedDetailFields.some(field => 
            field.selector === suggestion.selector
        );
        
        return `
            <div class="suggestion-item" data-index="${index}" style="border: 1px solid #ddd; 
                 border-radius: 6px; padding: 12px; margin-bottom: 10px; cursor: pointer;
                 transition: all 0.2s; ${isSelected ? 'background: #e3f2fd; border-color: #2196f3;' : 'background: #f8f9fa;'}">
                
                <div style="display: flex; align-items: flex-start;">
                    <input type="checkbox" class="suggestion-checkbox" data-index="${index}" 
                           ${isSelected ? 'checked' : ''} style="margin-right: 10px; margin-top: 2px;">
                    
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: #333; margin-bottom: 4px;">
                            ${suggestion.label}
                        </div>
                        <div style="font-size: 11px; color: #666; margin-bottom: 6px;">
                            Type: ${suggestion.type} | Confidence: ${Math.round(suggestion.confidence * 100)}%
                        </div>
                        <div style="font-size: 10px; color: #999; font-family: monospace; margin-bottom: 6px;">
                            ${suggestion.selector}
                        </div>
                        ${suggestion.sample_text ? `
                            <div style="font-size: 11px; color: #555; font-style: italic; background: #fff; 
                                 padding: 4px 8px; border-radius: 3px; border: 1px solid #eee;">
                                "${suggestion.sample_text}"
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create manual configuration modal
     */
    createManualConfigModal() {
        const modal = document.createElement('div');
        modal.id = 'v3-manual-detail-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000010;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; width: 600px; max-height: 80%; 
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden;">
                
                <div style="padding: 20px; border-bottom: 1px solid #eee; background: #f8f9fa;">
                    <h3 style="margin: 0; color: #333;">Manual Detail Configuration</h3>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                        Define selectors for detail page extraction
                    </p>
                </div>
                
                <div style="padding: 20px; max-height: 400px; overflow-y: auto;">
                    <div id="manual-fields-container">
                        <!-- Dynamic fields will be added here -->
                    </div>
                    
                    <button id="add-manual-field" style="background: #17a2b8; color: white; border: none; 
                            border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 12px; margin-top: 10px;">
                        + Add Field
                    </button>
                </div>
                
                <div style="padding: 20px; border-top: 1px solid #eee; display: flex; justify-content: space-between;">
                    <button id="cancel-manual-config" style="background: #6c757d; color: white; border: none; 
                            border-radius: 6px; padding: 10px 20px; cursor: pointer;">
                        Cancel
                    </button>
                    <button id="save-manual-config" style="background: #28a745; color: white; border: none; 
                            border-radius: 6px; padding: 10px 20px; cursor: pointer;">
                        Save Configuration
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        modal.querySelector('#cancel-manual-config').addEventListener('click', () => {
            this.closeModal(modal);
        });
        
        modal.querySelector('#save-manual-config').addEventListener('click', () => {
            this.saveManualConfiguration();
            this.closeModal(modal);
        });
        
        modal.querySelector('#add-manual-field').addEventListener('click', () => {
            this.addManualFieldRow();
        });
        
        // Initialize with existing fields or one empty field
        this.initializeManualFields();
        
        return modal;
    }
    
    /**
     * Show modal
     */
    showModal(modal) {
        document.body.appendChild(modal);
        
        // Add event listeners for checkboxes (if any)
        modal.addEventListener('change', (e) => {
            if (e.target.classList.contains('suggestion-checkbox')) {
                this.toggleSuggestionSelection(e.target);
            }
        });
        
        // Add click handlers for suggestion items
        modal.addEventListener('click', (e) => {
            const suggestionItem = e.target.closest('.suggestion-item');
            if (suggestionItem && !e.target.matches('input[type="checkbox"]')) {
                const checkbox = suggestionItem.querySelector('.suggestion-checkbox');
                checkbox.checked = !checkbox.checked;
                this.toggleSuggestionSelection(checkbox);
            }
        });
    }
    
    /**
     * Close modal
     */
    closeModal(modal) {
        if (modal && modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    }
    
    /**
     * Toggle suggestion selection
     */
    toggleSuggestionSelection(checkbox) {
        const index = parseInt(checkbox.getAttribute('data-index'));
        const suggestion = this.detailPageData.suggestions[index];
        const suggestionItem = checkbox.closest('.suggestion-item');
        
        if (checkbox.checked) {
            // Add to selected fields
            this.selectedDetailFields.push({
                id: `detail_field_${Date.now()}_${index}`,
                label: suggestion.label,
                selector: suggestion.selector,
                element_type: suggestion.type,
                confidence: suggestion.confidence,
                sample_text: suggestion.sample_text
            });
            
            // Update visual style
            suggestionItem.style.background = '#e3f2fd';
            suggestionItem.style.borderColor = '#2196f3';
        } else {
            // Remove from selected fields
            this.selectedDetailFields = this.selectedDetailFields.filter(
                field => field.selector !== suggestion.selector
            );
            
            // Update visual style
            suggestionItem.style.background = '#f8f9fa';
            suggestionItem.style.borderColor = '#ddd';
        }
        
        console.log('📋 Selected detail fields:', this.selectedDetailFields);
    }
    
    /**
     * Select/deselect all suggestions
     */
    selectAllSuggestions(selectAll) {
        const checkboxes = document.querySelectorAll('.suggestion-checkbox');
        checkboxes.forEach(checkbox => {
            if (checkbox.checked !== selectAll) {
                checkbox.checked = selectAll;
                this.toggleSuggestionSelection(checkbox);
            }
        });
    }
    
    /**
     * Save detail configuration
     */
    saveDetailConfiguration() {
        if (this.selectedDetailFields.length === 0) {
            this.overlay.showNotification('Please select at least one field', 'warning');
            return;
        }
        
        // Update action with detail template
        this.currentAction.detail_template = {
            fields: this.selectedDetailFields,
            navigation_type: 'click',
            extraction_strategy: 'auto'
        };
        
        // Update action type to indicate it has detail extraction
        this.currentAction.action_type = 'navigation_with_detail';
        
        // Update the overlay
        this.overlay.updateSidebar();
        
        this.overlay.showNotification(
            `Detail extraction configured: ${this.selectedDetailFields.length} fields`
        );
        
        console.log('✅ Detail configuration saved:', this.currentAction);
    }
    
    /**
     * Initialize manual fields interface
     */
    initializeManualFields() {
        const container = document.querySelector('#manual-fields-container');
        if (!container) return;
        
        // Add existing fields or one empty field
        if (this.selectedDetailFields.length > 0) {
            this.selectedDetailFields.forEach(field => {
                this.addManualFieldRow(field);
            });
        } else {
            this.addManualFieldRow();
        }
    }
    
    /**
     * Add manual field row
     */
    addManualFieldRow(field = null) {
        const container = document.querySelector('#manual-fields-container');
        if (!container) return;
        
        const fieldId = field?.id || `manual_field_${Date.now()}`;
        const rowIndex = container.children.length;
        
        const row = document.createElement('div');
        row.className = 'manual-field-row';
        row.setAttribute('data-field-id', fieldId);
        row.style.cssText = `
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            background: #f8f9fa;
        `;
        
        row.innerHTML = `
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <input type="text" class="field-label" placeholder="Field Label" 
                       value="${field?.label || ''}" 
                       style="flex: 1; margin-right: 10px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                <select class="field-type" style="margin-right: 10px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;">
                    <option value="text" ${field?.element_type === 'text' ? 'selected' : ''}>Text</option>
                    <option value="link" ${field?.element_type === 'link' ? 'selected' : ''}>Link</option>
                    <option value="image" ${field?.element_type === 'image' ? 'selected' : ''}>Image</option>
                    <option value="date" ${field?.element_type === 'date' ? 'selected' : ''}>Date</option>
                    <option value="number" ${field?.element_type === 'number' ? 'selected' : ''}>Number</option>
                </select>
                <button class="remove-field-btn" style="background: #dc3545; color: white; border: none; 
                        border-radius: 4px; padding: 6px 8px; cursor: pointer; font-size: 12px;">×</button>
            </div>
            <input type="text" class="field-selector" placeholder="CSS Selector (e.g., .price, h1, .description)" 
                   value="${field?.selector || ''}" 
                   style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; font-size: 11px;">
        `;
        
        // Add remove handler
        row.querySelector('.remove-field-btn').addEventListener('click', () => {
            row.remove();
        });
        
        container.appendChild(row);
    }
    
    /**
     * Save manual configuration
     */
    saveManualConfiguration() {
        const rows = document.querySelectorAll('.manual-field-row');
        const manualFields = [];
        
        rows.forEach(row => {
            const label = row.querySelector('.field-label').value.trim();
            const selector = row.querySelector('.field-selector').value.trim();
            const type = row.querySelector('.field-type').value;
            
            if (label && selector) {
                manualFields.push({
                    id: row.getAttribute('data-field-id'),
                    label: label,
                    selector: selector,
                    element_type: type
                });
            }
        });
        
        if (manualFields.length === 0) {
            this.overlay.showNotification('Please add at least one field', 'warning');
            return;
        }
        
        this.selectedDetailFields = manualFields;
        this.saveDetailConfiguration();
    }
}

// Auto-initialize when overlay is available
if (typeof window !== 'undefined') {
    window.V3SubpageDetailExtractor = V3SubpageDetailExtractor;
    console.log('🔗 V3 Subpage Detail Extractor module loaded');
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { V3SubpageDetailExtractor };
}