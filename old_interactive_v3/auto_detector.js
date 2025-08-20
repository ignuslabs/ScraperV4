// src/interactive/v3/auto_detector.js

/**
 * V3 Auto-Detection System - Enhanced Version
 * Intelligent pattern recognition and auto-suggestion for web scraping
 * 
 * Features:
 * - Container similarity scoring with advanced algorithms
 * - Auto-pattern recognition for common layouts
 * - One-click application of suggestions
 * - Visual preview and interactive UI
 * - Site type detection (e-commerce, directory, news, etc.)
 * - Pattern library for common layouts
 */

// Enhanced Pattern Library for Common Layouts
const PATTERN_LIBRARY = {
    ecommerce: {
        containers: [
            { name: 'Product Grid', selectors: ['.product-item', '.product-card', '.product-tile', '[data-product]', '.item', '.product'] },
            { name: 'Search Results', selectors: ['.search-result', '.result-item', '.listing-item', '.search-item'] },
            { name: 'Category Items', selectors: ['.category-item', '.cat-item', '.category-product'] }
        ],
        fields: {
            title: ['.product-title', '.title', 'h1', 'h2', 'h3', '.name', '.product-name'],
            price: ['.price', '.cost', '.amount', '.product-price', '[data-price]', '.price-current'],
            image: ['img', '.product-image', '.image', '.photo', '.picture'],
            rating: ['.rating', '.stars', '.score', '.review-score', '[data-rating]'],
            link: ['a', '.product-link', '.item-link'],
            description: ['.description', '.summary', '.details', '.product-description']
        }
    },
    
    directory: {
        containers: [
            { name: 'People Cards', selectors: ['.person', '.profile', '.member', '.staff', '.team-member', '.professional'] },
            { name: 'Business Listings', selectors: ['.business', '.company', '.listing', '.directory-item'] },
            { name: 'Contact Cards', selectors: ['.contact', '.card', '.profile-card', '.member-card'] }
        ],
        fields: {
            name: ['.name', '.full-name', '.person-name', 'h1', 'h2', 'h3', '.title'],
            title: ['.title', '.position', '.job-title', '.role', '.designation'],
            email: ['.email', '[href^="mailto:"]', '.contact-email', '.email-link'],
            phone: ['.phone', '.tel', '[href^="tel:"]', '.contact-phone', '.phone-link'],
            bio: ['.bio', '.biography', '.description', '.about', '.profile-text'],
            image: ['img', '.photo', '.profile-image', '.headshot', '.avatar'],
            link: ['a', '.profile-link', '.view-profile', '.more-info', '.details-link'],
            location: ['.location', '.office', '.city', '.address', '.region'],
            company: ['.company', '.firm', '.organization', '.practice'],
            department: ['.department', '.practice-area', '.specialization', '.focus'],
            education: ['.education', '.degree', '.school', '.university', '.alma-mater'],
            experience: ['.experience', '.years', '.seniority', '.level']
        }
    },
    
    news: {
        containers: [
            { name: 'Article Cards', selectors: ['.article', '.post', '.news-item', '.story', '.content-item'] },
            { name: 'Blog Posts', selectors: ['.blog-post', '.entry', '.post-item', '.article-card'] }
        ],
        fields: {
            headline: ['.headline', '.title', 'h1', 'h2', 'h3', '.article-title', '.post-title'],
            author: ['.author', '.by', '.byline', '.writer', '.journalist'],
            date: ['.date', '.published', '.timestamp', '.time', '[datetime]'],
            summary: ['.summary', '.excerpt', '.lead', '.description', '.intro'],
            link: ['a', '.read-more', '.article-link', '.full-article'],
            category: ['.category', '.section', '.tag', '.topic']
        }
    },
    
    realestate: {
        containers: [
            { name: 'Property Cards', selectors: ['.property', '.listing', '.home', '.real-estate-item'] },
            { name: 'Search Results', selectors: ['.search-result', '.property-result', '.listing-result'] }
        ],
        fields: {
            address: ['.address', '.location', '.property-address', '.street'],
            price: ['.price', '.cost', '.amount', '.property-price'],
            bedrooms: ['.beds', '.bedrooms', '.bed-count', '[data-beds]'],
            bathrooms: ['.baths', '.bathrooms', '.bath-count', '[data-baths]'],
            sqft: ['.sqft', '.square-feet', '.area', '.size'],
            image: ['img', '.property-image', '.photo', '.listing-photo'],
            link: ['a', '.property-link', '.view-details', '.more-info']
        }
    }
};

class AutoDetector {
    constructor() {
        // Initialize learning service
        this.learningService = window.V3LearningService || null;
        if (this.learningService) {
            console.log('🧠 Learning service connected to AutoDetector');
        }
        // Legacy patterns - kept for backward compatibility
        this.patterns = {
            // Common container patterns
            containers: {
                card: {
                    selectors: ['.card', '.item', '.product', '.profile', '.listing'],
                    childPatterns: ['h2', 'h3', '.title', '.name', '.price']
                },
                grid: {
                    selectors: ['.grid-item', '.col', '.cell'],
                    parentPatterns: ['.grid', '.row', '.container']
                },
                list: {
                    selectors: ['li', '.list-item', 'tr'],
                    parentPatterns: ['ul', 'ol', '.list', 'tbody']
                },
                article: {
                    selectors: ['article', '.post', '.entry'],
                    childPatterns: ['.title', '.content', '.meta']
                }
            },
            
            // Pagination patterns
            pagination: {
                numeric: {
                    selectors: ['.pagination a', '.page-numbers', 'a[href*="page="]'],
                    patterns: [/\d+/, /next/i, /prev/i]
                },
                loadMore: {
                    selectors: ['button:contains("load more")', '.load-more', '[data-load-more]'],
                    patterns: [/load\s*more/i, /show\s*more/i]
                },
                infinite: {
                    indicators: ['[data-infinite-scroll]', '.infinite-scroll'],
                    scrollableContainers: ['.results', '.items', 'main']
                }
            },
            
            // Data field patterns
            fields: {
                title: {
                    selectors: ['h1', 'h2', 'h3', '.title', '.name', '.heading'],
                    scoring: { tagName: 0.3, className: 0.4, position: 0.3 }
                },
                price: {
                    selectors: ['.price', '.cost', '[class*="price"]'],
                    patterns: [/\$\d+/, /\d+\.\d{2}/, /USD|EUR|GBP/]
                },
                image: {
                    selectors: ['img', 'picture img', '.image img'],
                    attributes: ['src', 'data-src', 'data-lazy']
                },
                link: {
                    selectors: ['a[href]', '.link'],
                    scoring: { hasHref: 0.5, position: 0.3, text: 0.2 }
                }
            }
        };
        
        // Enhanced V3 properties
        this.isActive = false;
        this.suggestions = [];
        this.analysisResults = null;
        this.similarityThreshold = 0.7;
        this.minContainerCount = 3;
        this.cache = new Map();
        
        // Initialize UI
        this.setupEventListeners();
        this.setupUI();
    }
    
    setupEventListeners() {
        // Auto-detect trigger (Ctrl+Shift+A)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                this.startV3AutoDetection();
            }
        });
        
        // Mouse hover for pattern preview
        document.addEventListener('mouseover', (e) => {
            if (this.isActive && window.V3InteractiveOverlay && window.V3InteractiveOverlay.state.isActive) {
                this.previewPattern(e.target);
            }
        });
        
        // Mouse leave to clear highlights
        document.addEventListener('mouseout', (e) => {
            if (this.isActive && window.V3InteractiveOverlay && window.V3InteractiveOverlay.state.isActive) {
                // Small delay to prevent flickering
                setTimeout(() => {
                    if (!e.relatedTarget || !e.relatedTarget.closest('.v3-autodetect-panel')) {
                        this.clearHighlights();
                    }
                }, 100);
            }
        });
    }
    
    setupUI() {
        // Create auto-detect panel
        this.panel = this.createAutoDetectPanel();
        document.body.appendChild(this.panel);
    }
    
    createAutoDetectPanel() {
        const panel = document.createElement('div');
        panel.id = 'v3-autodetect-panel';
        // Dynamic sizing based on screen dimensions
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const isSmallScreen = viewportWidth < 1400 || viewportHeight < 900;
        const padding = isSmallScreen ? 10 : 20;
        const panelWidth = isSmallScreen ? 280 : 300;
        const maxHeight = viewportHeight - (padding + 80);
        
        panel.style.cssText = `
            position: fixed;
            top: ${padding + 60}px;
            left: ${padding}px;
            width: ${panelWidth}px;
            max-height: ${maxHeight}px;
            background: white;
            border: 2px solid #007bff;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            z-index: 1000010;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: none;
            overflow: hidden;
        `;
        
        panel.innerHTML = `
            <div style="padding: 16px; border-bottom: 1px solid #eee; background: #f8f9fa; border-radius: 8px 8px 0 0; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 14px; font-weight: 600; color: #333;">🤖 Auto-Detection V3</h3>
                <div>
                    <button id="collapse-autodetect" style="border: none; background: none; font-size: 16px; cursor: pointer; color: #666; margin-right: 8px;" title="Collapse/Expand">−</button>
                    <button id="close-autodetect" style="border: none; background: none; font-size: 16px; cursor: pointer; color: #666;" title="Close">×</button>
                </div>
            </div>
            <div id="autodetect-content" style="padding: 16px; max-height: 400px; overflow-y: auto;">
                <div id="autodetect-status">Ready to analyze...</div>
                <div id="autodetect-suggestions"></div>
            </div>
            <div style="padding: 12px 16px; border-top: 1px solid #eee; background: #f8f9fa;">
                <button id="start-autodetect-v3" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 8px;">Analyze Page V3</button>
                <button id="legacy-analyze" style="background: #6c757d; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 8px;">Legacy Mode</button>
                <button id="apply-suggestions" style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 12px; display: none;">Apply All</button>
            </div>
        `;
        
        // Event listeners
        panel.querySelector('#close-autodetect').onclick = () => this.hidePanel();
        panel.querySelector('#collapse-autodetect').onclick = () => this.togglePanel();
        panel.querySelector('#start-autodetect-v3').onclick = () => this.startV3AutoDetection();
        panel.querySelector('#legacy-analyze').onclick = () => this.analyze();
        panel.querySelector('#apply-suggestions').onclick = () => this.applySuggestions();
        
        return panel;
    }
    
    showPanel() {
        // Hide any existing panels to prevent conflicts
        this.cleanupConflictingPanels();
        
        this.panel.style.display = 'block';
        this.isActive = true;
    }
    
    cleanupConflictingPanels() {
        // Remove any duplicate or conflicting panels
        const existingPanels = document.querySelectorAll('#v3-autodetect-panel');
        existingPanels.forEach((panel, index) => {
            if (index > 0) { // Keep only the first one
                panel.remove();
            }
        });
        
        // Clean up any corrupted UI elements
        const corruptedElements = document.querySelectorAll('[style*="undefined"], [style*="NaN"]');
        corruptedElements.forEach(el => {
            el.style.cssText = '';
        });
    }
    
    hidePanel() {
        this.panel.style.display = 'none';
        this.isActive = false;
        this.clearHighlights();
    }
    
    togglePanel() {
        const content = document.getElementById('autodetect-content');
        const toggle = document.getElementById('collapse-autodetect');
        
        if (content && toggle) {
            const isCollapsed = content.style.display === 'none';
            
            if (isCollapsed) {
                content.style.display = 'block';
                toggle.textContent = '−';
                toggle.title = 'Collapse Auto-Detection Panel';
            } else {
                content.style.display = 'none';
                toggle.textContent = '+';
                toggle.title = 'Expand Auto-Detection Panel';
            }
        }
    }
    
    async startV3AutoDetection() {
        this.showPanel();
        this.updateStatus('🔍 V3 Analysis: Detecting site type...');
        
        try {
            // Step 1: Detect site type
            const siteType = this.detectSiteType();
            this.updateStatus(`📋 Site type: ${siteType}`);
            
            // Step 2: Find container patterns using enhanced algorithm
            const containers = await this.findEnhancedContainerPatterns();
            this.updateStatus(`📦 Found ${containers.length} container patterns`);
            
            // Step 3: Analyze field patterns within containers
            let suggestions = await this.generateEnhancedSuggestions(containers, siteType);
            this.updateStatus(`💡 Generated ${suggestions.length} V3 suggestions`);
            
            // Step 4: Apply learning improvements
            if (this.learningService) {
                this.updateStatus('🧠 Applying learned improvements...');
                const improved = this.learningService.applyCorrections(containers, suggestions);
                suggestions = improved.fields;
                
                if (improved.appliedPatterns > 0) {
                    this.updateStatus(`✅ Applied ${improved.appliedPatterns} learned patterns`);
                }
            }
            
            // Step 5: Display enhanced suggestions
            this.displayEnhancedSuggestions(suggestions);
            
        } catch (error) {
            console.error('V3 Auto-detection error:', error);
            this.updateStatus('❌ V3 Auto-detection failed');
        }
    }
    
    detectSiteType() {
        const indicators = {
            ecommerce: ['.product', '.price', '.cart', '.add-to-cart', '.shop', '.store', '[data-product]'],
            directory: ['.person', '.profile', '.member', '.contact', '.directory', '.staff'],
            news: ['.article', '.post', '.news', '.blog', '.story', '.headline'],
            realestate: ['.property', '.listing', '.real-estate', '.home', '.house', '.apartment']
        };
        
        let scores = {};
        
        for (const [type, selectors] of Object.entries(indicators)) {
            scores[type] = 0;
            for (const selector of selectors) {
                scores[type] += document.querySelectorAll(selector).length;
            }
        }
        
        // Find the type with highest score
        const maxScore = Math.max(...Object.values(scores));
        if (maxScore === 0) return 'custom';
        
        return Object.keys(scores).find(key => scores[key] === maxScore) || 'custom';
    }
    
    async findEnhancedContainerPatterns() {
        console.log('🔍 Finding enhanced container patterns with sub-element richness scoring...');
        
        try {
            const containers = [];
            const allElements = Array.from(document.querySelectorAll('*'));
            
            // Group elements by their structure similarity
            const elementGroups = this.groupSimilarElements(allElements);
            console.log(`Found ${elementGroups.length} element groups for analysis`);
            
            for (const group of elementGroups) {
                try {
                    if (group.length >= this.minContainerCount) {
                        const similarity = this.calculateGroupSimilarity(group);
                        
                        if (similarity >= this.similarityThreshold) {
                            const selector = this.generateCommonSelector(group);
                            
                            // Calculate sub-element richness score
                            const subElementRichness = await this.calculateSubElementRichness(group);
                            
                            // Calculate visual layout score
                            const visualLayoutScore = this.calculateVisualLayoutScore(group);
                            
                            // Calculate overall container quality score
                            const qualityScore = this.calculateContainerQualityScore({
                                similarity: similarity,
                                subElementRichness: subElementRichness,
                                visualLayoutScore: visualLayoutScore,
                                containerCount: group.length
                            });
                            
                            // Only include containers that meet quality threshold
                            if (qualityScore >= 0.5) { // 50% minimum quality
                                containers.push({
                                    elements: group,
                                    selector: selector,
                                    count: group.length,
                                    similarity: similarity,
                                    subElementRichness: subElementRichness,
                                    visualLayoutScore: visualLayoutScore,
                                    qualityScore: qualityScore,
                                    pattern: this.analyzeElementPattern(group[0])
                                });
                                
                                console.log(`✅ Quality container: ${selector} (${group.length} elements, quality: ${(qualityScore * 100).toFixed(1)}%)`);
                            } else {
                                console.log(`❌ Low quality container filtered out: ${selector} (quality: ${(qualityScore * 100).toFixed(1)}%)`);
                            }
                        }
                    }
                } catch (groupError) {
                    // Continue processing other groups if one fails
                    console.warn('Auto-detector: Error processing element group', groupError);
                }
            }
            
            // Sort by quality score instead of just similarity
            const sortedContainers = containers.sort((a, b) => b.qualityScore - a.qualityScore);
            
            console.log(`🎯 Found ${sortedContainers.length} high-quality containers`);
            return sortedContainers;
        } catch (error) {
            console.error('Auto-detector: Error in findEnhancedContainerPatterns', error);
            return []; // Return empty array on error
        }
    }
    
    groupSimilarElements(elements) {
        const groups = [];
        const processed = new Set();
        
        for (const element of elements) {
            if (processed.has(element) || this.isIgnorableElement(element)) {
                continue;
            }
            
            const similarElements = this.findSimilarElements(element, elements);
            
            if (similarElements.length >= this.minContainerCount) {
                similarElements.forEach(el => processed.add(el));
                groups.push(similarElements);
            }
        }
        
        return groups;
    }

    /**
     * Calculate sub-element richness score for a container group
     * Evaluates diversity and meaningfulness of sub-elements
     */
    async calculateSubElementRichness(containerGroup) {
        if (!containerGroup || containerGroup.length === 0) return 0;
        
        // Analyze first few containers to get representative sample
        const sampleSize = Math.min(5, containerGroup.length);
        const sampleContainers = containerGroup.slice(0, sampleSize);
        
        let totalRichness = 0;
        
        for (const container of sampleContainers) {
            const richness = this.analyzeContainerRichness(container);
            totalRichness += richness;
        }
        
        return totalRichness / sampleSize;
    }

    /**
     * Analyze richness of a single container element
     */
    analyzeContainerRichness(container) {
        try {
            let richness = 0;
            const subElements = container.querySelectorAll('*');
            const fieldTypes = new Set();
            
            // Factor 1: Sub-element diversity (40% weight)
            const diversityScore = this.calculateSubElementDiversity(container, fieldTypes);
            richness += diversityScore * 0.4;
            
            // Factor 2: Semantic value (25% weight)
            const semanticScore = this.calculateSemanticValue(container);
            richness += semanticScore * 0.25;
            
            // Factor 3: Content depth (20% weight)
            const depthScore = this.calculateContentDepth(container);
            richness += depthScore * 0.2;
            
            // Factor 4: Interactive elements (15% weight)
            const interactivityScore = this.calculateInteractivityScore(container);
            richness += interactivityScore * 0.15;
            
            return Math.min(richness, 1.0);
        } catch (error) {
            console.warn('Auto-detector: Error in analyzeContainerRichness', error);
            return 0; // Return minimum richness score on error
        }
    }

    /**
     * Calculate diversity of sub-elements within container
     */
    calculateSubElementDiversity(container, fieldTypes) {
        try {
            const subElements = container.querySelectorAll('*');
            const detectedTypes = new Set();
            
            // Analyze each sub-element
            for (const element of subElements) {
                try {
                    const fieldType = this.determineFieldTypeEnhanced(element, '', []);
                    detectedTypes.add(fieldType);
                    
                    // Special detection for valuable field types
                    const text = element.textContent.trim();
                    const href = element.href || element.getAttribute('href');
                    
                    if (text.includes('@')) detectedTypes.add('email');
                    if (/[\d\-\(\)\s]{8,}/.test(text)) detectedTypes.add('phone');
                    if (/[\$€£¥]/.test(text)) detectedTypes.add('price');
                    if (href?.startsWith('mailto:')) detectedTypes.add('email');
                    if (href?.startsWith('tel:')) detectedTypes.add('phone');
                    if (element.tagName.match(/h[1-6]/i)) detectedTypes.add('text');
                } catch (elementError) {
                    // Continue processing other elements if one fails
                    console.warn('Auto-detector: Error processing sub-element', elementError);
                }
            }
            
            // Store detected types for reference
            fieldTypes.clear();
            detectedTypes.forEach(type => fieldTypes.add(type));
            
            // Score based on diversity (more types = higher score)
            const diversityTypes = detectedTypes.size;
            
            if (diversityTypes >= 5) return 1.0;
            if (diversityTypes >= 4) return 0.8;
            if (diversityTypes >= 3) return 0.6;
            if (diversityTypes >= 2) return 0.4;
            if (diversityTypes >= 1) return 0.2;
            
            return 0;
        } catch (error) {
            console.warn('Auto-detector: Error in calculateSubElementDiversity', error);
            return 0; // Return minimum score on error
        }
    }

    /**
     * Calculate semantic value of container content
     */
    calculateSemanticValue(container) {
        let value = 0;
        const text = container.textContent.trim();
        const textLength = text.length;
        
        // Text length indicates content richness
        if (textLength > 100) value += 0.4;
        else if (textLength > 50) value += 0.3;
        else if (textLength > 20) value += 0.2;
        else if (textLength > 5) value += 0.1;
        
        // Presence of meaningful patterns
        if (text.includes('@')) value += 0.2; // Email
        if (/[\$€£¥\d,]+/.test(text)) value += 0.2; // Price/number
        if (/\d{4}|\d{1,2}\/\d{1,2}/.test(text)) value += 0.1; // Date
        if (/\d{3}[-\s]\d{3}/.test(text)) value += 0.1; // Phone
        
        // Links and images add value
        const links = container.querySelectorAll('a[href]');
        const images = container.querySelectorAll('img[src]');
        
        if (links.length > 0) value += Math.min(links.length * 0.1, 0.2);
        if (images.length > 0) value += Math.min(images.length * 0.1, 0.2);
        
        return Math.min(value, 1.0);
    }

    /**
     * Calculate content depth (nested structure complexity)
     */
    calculateContentDepth(container) {
        const maxDepth = this.calculateElementDepth(container);
        const childCount = container.children.length;
        
        let score = 0;
        
        // Depth scoring (deeper structures often more complex/valuable)
        if (maxDepth >= 4) score += 0.4;
        else if (maxDepth >= 3) score += 0.3;
        else if (maxDepth >= 2) score += 0.2;
        else score += 0.1;
        
        // Child count scoring
        if (childCount >= 5) score += 0.3;
        else if (childCount >= 3) score += 0.2;
        else if (childCount >= 1) score += 0.1;
        
        // Balanced structure bonus
        const allElements = container.querySelectorAll('*');
        if (allElements.length >= 3 && allElements.length <= 20) {
            score += 0.3; // Sweet spot for content richness
        }
        
        return Math.min(score, 1.0);
    }

    /**
     * Calculate interactivity score (buttons, links, form elements)
     */
    calculateInteractivityScore(container) {
        let score = 0;
        
        // Count interactive elements
        const buttons = container.querySelectorAll('button, [role="button"], .btn, .button');
        const links = container.querySelectorAll('a[href]:not([href^="#"])');
        const inputs = container.querySelectorAll('input, select, textarea');
        
        if (buttons.length > 0) score += Math.min(buttons.length * 0.3, 0.4);
        if (links.length > 0) score += Math.min(links.length * 0.2, 0.4);
        if (inputs.length > 0) score += Math.min(inputs.length * 0.2, 0.3);
        
        return Math.min(score, 1.0);
    }

    /**
     * Calculate maximum depth of nested elements
     */
    calculateElementDepth(element, currentDepth = 0) {
        if (!element.children || element.children.length === 0) {
            return currentDepth;
        }
        
        let maxDepth = currentDepth;
        for (const child of element.children) {
            const childDepth = this.calculateElementDepth(child, currentDepth + 1);
            maxDepth = Math.max(maxDepth, childDepth);
        }
        
        return maxDepth;
    }

    /**
     * Calculate visual layout score for container group
     * Analyzes positioning, spacing, and visual alignment
     */
    calculateVisualLayoutScore(containerGroup) {
        if (!containerGroup || containerGroup.length < 2) return 0.5; // Default for single elements
        
        console.log(`🎨 Analyzing visual layout for ${containerGroup.length} containers`);
        
        // Get bounding rectangles for all containers
        const rects = containerGroup.map(element => {
            try {
                return element.getBoundingClientRect();
            } catch (e) {
                return { x: 0, y: 0, width: 0, height: 0, top: 0, left: 0 };
            }
        }).filter(rect => rect.width > 0 && rect.height > 0);
        
        if (rects.length < 2) return 0.3; // Not enough visible elements
        
        let layoutScore = 0;
        
        // Factor 1: Spacing consistency (40% of visual score)
        const spacingScore = this.calculateSpacingConsistency(rects);
        layoutScore += spacingScore * 0.4;
        
        // Factor 2: Alignment patterns (30% of visual score)
        const alignmentScore = this.calculateAlignmentScore(rects);
        layoutScore += alignmentScore * 0.3;
        
        // Factor 3: Size consistency (20% of visual score)
        const sizeScore = this.calculateSizeConsistency(rects);
        layoutScore += sizeScore * 0.2;
        
        // Factor 4: Visual grouping (10% of visual score)
        const groupingScore = this.calculateVisualGrouping(rects);
        layoutScore += groupingScore * 0.1;
        
        console.log(`✅ Visual layout score: ${(layoutScore * 100).toFixed(1)}%`);
        return Math.min(layoutScore, 1.0);
    }

    /**
     * Calculate spacing consistency between elements
     */
    calculateSpacingConsistency(rects) {
        if (rects.length < 2) return 0;
        
        const spacings = [];
        
        // Calculate vertical spacings (most common pattern)
        for (let i = 1; i < rects.length; i++) {
            const prevRect = rects[i - 1];
            const currRect = rects[i];
            
            // Only calculate spacing if elements seem to be in a sequence
            if (Math.abs(currRect.left - prevRect.left) < 100) { // Similar horizontal position
                const spacing = Math.abs(currRect.top - (prevRect.top + prevRect.height));
                spacings.push(spacing);
            }
        }
        
        if (spacings.length === 0) {
            // Try horizontal spacings
            for (let i = 1; i < rects.length; i++) {
                const prevRect = rects[i - 1];
                const currRect = rects[i];
                
                if (Math.abs(currRect.top - prevRect.top) < 50) { // Similar vertical position
                    const spacing = Math.abs(currRect.left - (prevRect.left + prevRect.width));
                    spacings.push(spacing);
                }
            }
        }
        
        if (spacings.length === 0) return 0.3; // No clear spacing pattern
        
        // Calculate consistency of spacings
        const avgSpacing = spacings.reduce((sum, s) => sum + s, 0) / spacings.length;
        const variance = spacings.reduce((sum, s) => sum + Math.pow(s - avgSpacing, 2), 0) / spacings.length;
        const stdDev = Math.sqrt(variance);
        
        // Lower variance = higher consistency
        const consistency = Math.max(0, 1 - (stdDev / Math.max(avgSpacing, 1)));
        return Math.min(consistency, 1.0);
    }

    /**
     * Calculate alignment score (elements aligned horizontally or vertically)
     */
    calculateAlignmentScore(rects) {
        if (rects.length < 2) return 0;
        
        let alignmentScore = 0;
        
        // Check horizontal alignment (left edges)
        const leftEdges = rects.map(r => r.left);
        const leftVariance = this.calculateVariance(leftEdges);
        const leftAlignment = Math.max(0, 1 - (leftVariance / 100)); // Lower variance = better alignment
        alignmentScore = Math.max(alignmentScore, leftAlignment);
        
        // Check vertical alignment (top edges)
        const topEdges = rects.map(r => r.top);
        const topVariance = this.calculateVariance(topEdges);
        const topAlignment = Math.max(0, 1 - (topVariance / 100));
        alignmentScore = Math.max(alignmentScore, topAlignment);
        
        // Check center alignment
        const centerX = rects.map(r => r.left + r.width / 2);
        const centerXVariance = this.calculateVariance(centerX);
        const centerXAlignment = Math.max(0, 1 - (centerXVariance / 100));
        alignmentScore = Math.max(alignmentScore, centerXAlignment);
        
        return Math.min(alignmentScore, 1.0);
    }

    /**
     * Calculate size consistency score
     */
    calculateSizeConsistency(rects) {
        if (rects.length < 2) return 1.0;
        
        // Calculate width consistency
        const widths = rects.map(r => r.width);
        const avgWidth = widths.reduce((sum, w) => sum + w, 0) / widths.length;
        const widthVariance = this.calculateVariance(widths);
        const widthConsistency = Math.max(0, 1 - (widthVariance / Math.pow(avgWidth, 2)));
        
        // Calculate height consistency
        const heights = rects.map(r => r.height);
        const avgHeight = heights.reduce((sum, h) => sum + h, 0) / heights.length;
        const heightVariance = this.calculateVariance(heights);
        const heightConsistency = Math.max(0, 1 - (heightVariance / Math.pow(avgHeight, 2)));
        
        // Return average of width and height consistency
        return (widthConsistency + heightConsistency) / 2;
    }

    /**
     * Calculate visual grouping score (elements appear to be grouped together)
     */
    calculateVisualGrouping(rects) {
        if (rects.length < 2) return 1.0;
        
        // Calculate average distance between elements
        let totalDistance = 0;
        let pairCount = 0;
        
        for (let i = 0; i < rects.length; i++) {
            for (let j = i + 1; j < rects.length; j++) {
                const rect1 = rects[i];
                const rect2 = rects[j];
                
                // Calculate center-to-center distance
                const centerX1 = rect1.left + rect1.width / 2;
                const centerY1 = rect1.top + rect1.height / 2;
                const centerX2 = rect2.left + rect2.width / 2;
                const centerY2 = rect2.top + rect2.height / 2;
                
                const distance = Math.sqrt(
                    Math.pow(centerX2 - centerX1, 2) + Math.pow(centerY2 - centerY1, 2)
                );
                
                totalDistance += distance;
                pairCount++;
            }
        }
        
        if (pairCount === 0) return 1.0;
        
        const avgDistance = totalDistance / pairCount;
        
        // Closer elements = better grouping (up to a point)
        const idealDistance = 200; // Reasonable distance for grouped elements
        const groupingScore = Math.max(0, 1 - Math.abs(avgDistance - idealDistance) / idealDistance);
        
        return Math.min(groupingScore, 1.0);
    }

    /**
     * Calculate variance of an array of numbers
     */
    calculateVariance(numbers) {
        if (numbers.length < 2) return 0;
        
        const avg = numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
        const variance = numbers.reduce((sum, n) => sum + Math.pow(n - avg, 2), 0) / numbers.length;
        
        return variance;
    }

    /**
     * Calculate overall container quality score
     * Combines multiple factors with weights from requirements
     */
    calculateContainerQualityScore(factors) {
        const {
            similarity,
            subElementRichness,
            visualLayoutScore,
            containerCount
        } = factors;
        
        // Weight factors according to requirements:
        // Sub-Element Diversity (40%), Semantic Value (25%), 
        // Structural Consistency (20%), Visual Layout (15%)
        
        let score = 0;
        
        // Sub-element richness (40% - most important factor)
        score += subElementRichness * 0.4;
        
        // Structural consistency (20%)
        score += similarity * 0.2;
        
        // Visual layout analysis (15%)
        score += (visualLayoutScore || 0.5) * 0.15;
        
        // Container count factor (10%)
        const countScore = Math.min(containerCount / 10, 1.0); // Normalize to 1.0
        score += countScore * 0.1;
        
        // Base quality bonus (15% - minimum viable threshold)
        const baseQuality = subElementRichness > 0.3 ? 0.15 : 0; // Minimum threshold
        score += baseQuality;
        
        return Math.min(score, 1.0);
    }

    /**
     * Record user correction for learning
     */
    recordUserCorrection(type, data) {
        if (!this.learningService) {
            console.log('📝 Learning service not available for recording correction');
            return;
        }

        console.log('📚 Recording user correction:', type, data);

        switch (type) {
            case 'container_added':
                this.learningService.recordContainerCorrection(
                    data.originalSelector || 'auto-detected',
                    data.correctedSelector,
                    data.element
                );
                break;
                
            case 'field_added':
                this.learningService.recordFieldCorrection(
                    data.containerSelector,
                    data.fieldLabel,
                    data.originalSelector || 'auto-detected', 
                    data.correctedSelector,
                    data.fieldType
                );
                break;
                
            case 'selector_improved':
                this.learningService.recordSelectorImprovement(
                    data.oldSelector,
                    data.newSelector,
                    data.fieldType,
                    data.reliability || 0.8
                );
                break;
                
            default:
                console.warn('Unknown correction type:', type);
        }
    }

    /**
     * Get learning statistics for display
     */
    getLearningStats() {
        if (!this.learningService) {
            return null;
        }
        
        return this.learningService.getLearningStats();
    }

    /**
     * Record when user manually selects a container
     */
    onContainerManuallySelected(element, selector) {
        this.recordUserCorrection('container_added', {
            correctedSelector: selector,
            element: element
        });
    }

    /**
     * Record when user manually adds a field
     */
    onFieldManuallyAdded(containerSelector, fieldLabel, fieldSelector, fieldType, element) {
        this.recordUserCorrection('field_added', {
            containerSelector: containerSelector,
            fieldLabel: fieldLabel,
            correctedSelector: fieldSelector,
            fieldType: fieldType
        });
    }

    /**
     * Record when user corrects a failing selector
     */
    onSelectorCorrected(oldSelector, newSelector, fieldType, reliability) {
        this.recordUserCorrection('selector_improved', {
            oldSelector: oldSelector,
            newSelector: newSelector,
            fieldType: fieldType,
            reliability: reliability
        });
    }
    
    updateStatus(message) {
        const statusEl = this.panel?.querySelector('#autodetect-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.style.color = message.includes('❌') ? '#dc3545' : 
                                   message.includes('✅') ? '#28a745' : '#333';
        }
    }
    
    previewPattern(element) {
        // Quick preview on hover
        this.clearHighlights();
        
        const similar = this.findSimilarElements(element, Array.from(document.querySelectorAll('*')));
        if (similar.length >= this.minContainerCount) {
            similar.forEach(el => {
                el.style.outline = '1px solid rgba(0, 123, 255, 0.5)';
            });
        }
    }
    
    clearHighlights() {
        // Remove all highlights
        document.querySelectorAll('*').forEach(el => {
            el.style.outline = '';
            el.style.outlineOffset = '';
        });
        
        // Remove labels
        document.querySelectorAll('.auto-detect-label').forEach(label => {
            label.remove();
        });
    }
    
    isIgnorableElement(element) {
        const tagName = element.tagName.toLowerCase();
        const ignoreTags = ['script', 'style', 'meta', 'head', 'title', 'link', 'br', 'hr'];
        
        if (ignoreTags.includes(tagName)) return true;
        if (element.offsetWidth === 0 || element.offsetHeight === 0) return true;
        if (element.classList.contains('scraper-')) return true; // Ignore our own elements
        if (element.id && element.id.includes('scraper-')) return true;
        
        return false;
    }
    
    // Enhanced V3 Methods
    
    findSimilarElements(targetElement, allElements) {
        const similar = [targetElement];
        const targetStructure = this.getElementStructure(targetElement);
        
        for (const element of allElements) {
            if (element === targetElement || this.isIgnorableElement(element)) {
                continue;
            }
            
            const elementStructure = this.getElementStructure(element);
            const similarity = this.calculateStructureSimilarity(targetStructure, elementStructure);
            
            if (similarity >= this.similarityThreshold) {
                similar.push(element);
            }
        }
        
        return similar;
    }
    
    calculateStructureSimilarity(struct1, struct2) {
        let score = 0;
        let factors = 0;
        
        // Tag name match
        if (struct1.tag === struct2.tag) score += 0.3;
        factors += 0.3;
        
        // Class similarity
        const classIntersection = struct1.classes.filter(cls => struct2.classes.includes(cls));
        const classUnion = [...new Set([...struct1.classes, ...struct2.classes])];
        if (classUnion.length > 0) {
            score += 0.25 * (classIntersection.length / classUnion.length);
        }
        factors += 0.25;
        
        // Child structure similarity
        const childSimilarity = this.calculateArraySimilarity(struct1.childTags, struct2.childTags);
        score += 0.2 * childSimilarity;
        factors += 0.2;
        
        // Content similarity
        const textLengthDiff = Math.abs(struct1.textLength - struct2.textLength);
        const maxTextLength = Math.max(struct1.textLength, struct2.textLength);
        if (maxTextLength > 0) {
            score += 0.15 * (1 - textLengthDiff / maxTextLength);
        }
        factors += 0.15;
        
        // Feature similarity (links, images)
        if (struct1.hasLinks === struct2.hasLinks) score += 0.05;
        if (struct1.hasImages === struct2.hasImages) score += 0.05;
        factors += 0.1;
        
        return factors > 0 ? Math.min(score / factors, 1.0) : 0;
    }
    
    calculateArraySimilarity(arr1, arr2) {
        const intersection = arr1.filter(item => arr2.includes(item));
        const union = [...new Set([...arr1, ...arr2])];
        return union.length > 0 ? intersection.length / union.length : 0;
    }
    
    generateCommonSelector(elements) {
        // Try to find the most specific common selector
        const commonClasses = this.findCommonClasses(elements);
        const tagName = elements[0].tagName.toLowerCase();
        
        if (commonClasses.length > 0) {
            return `${tagName}.${commonClasses.join('.')}`;
        }
        
        // Fallback to tag name with nth-child if necessary
        const parent = elements[0].parentElement;
        if (parent) {
            const siblings = Array.from(parent.children).filter(child => child.tagName === elements[0].tagName);
            if (siblings.length === elements.length) {
                return `${parent.tagName.toLowerCase()} > ${tagName}`;
            }
        }
        
        return tagName;
    }
    
    findCommonClasses(elements) {
        if (elements.length === 0) return [];
        
        let commonClasses = Array.from(elements[0].classList);
        
        for (let i = 1; i < elements.length; i++) {
            const elementClasses = Array.from(elements[i].classList);
            commonClasses = commonClasses.filter(cls => elementClasses.includes(cls));
        }
        
        return commonClasses;
    }
    
    calculateGroupSimilarity(group) {
        if (group.length < 2) return 0;
        
        let totalSimilarity = 0;
        let comparisons = 0;
        
        for (let i = 0; i < group.length; i++) {
            for (let j = i + 1; j < group.length; j++) {
                const struct1 = this.getElementStructure(group[i]);
                const struct2 = this.getElementStructure(group[j]);
                totalSimilarity += this.calculateStructureSimilarity(struct1, struct2);
                comparisons++;
            }
        }
        
        return comparisons > 0 ? totalSimilarity / comparisons : 0;
    }
    
    analyzeElementPattern(element) {
        return {
            hasText: element.textContent.trim().length > 0,
            hasLinks: element.querySelectorAll('a').length > 0,
            hasImages: element.querySelectorAll('img').length > 0,
            hasForm: element.querySelectorAll('input, select, textarea').length > 0,
            childCount: element.children.length,
            classes: Array.from(element.classList)
        };
    }
    
    async generateEnhancedSuggestions(containers, siteType) {
        const suggestions = [];
        
        for (const container of containers) {
            const containerSuggestion = {
                type: 'container',
                label: this.generateContainerLabel(container, siteType),
                selector: container.selector,
                confidence: container.similarity,
                count: container.count,
                fields: await this.suggestFields(container, siteType)
            };
            
            suggestions.push(containerSuggestion);
        }
        
        return suggestions;
    }
    
    generateContainerLabel(container, siteType) {
        const patterns = PATTERN_LIBRARY[siteType];
        
        if (patterns) {
            for (const pattern of patterns.containers) {
                for (const selector of pattern.selectors) {
                    if (container.selector.includes(selector.replace('.', ''))) {
                        return pattern.name.toLowerCase().replace(/\s+/g, '_');
                    }
                }
            }
        }
        
        // Fallback to generic naming
        const element = container.elements[0];
        const classList = Array.from(element.classList);
        
        if (classList.length > 0) {
            return classList[0].replace(/[-_]/g, '_');
        }
        
        return `${element.tagName.toLowerCase()}_container`;
    }
    
    async suggestFields(container, siteType) {
        console.log(`🔍 Enhanced field suggestion for ${container.elements.length} container instances`);
        
        const fields = [];
        const patterns = PATTERN_LIBRARY[siteType];
        
        // Phase 1: Pattern-based detection with multi-container validation
        if (patterns && patterns.fields) {
            for (const [fieldName, selectors] of Object.entries(patterns.fields)) {
                for (const selector of selectors) {
                    const validatedField = await this.validateFieldAcrossContainers(
                        container.elements, selector, fieldName, 'pattern'
                    );
                    
                    if (validatedField && validatedField.reliability >= 0.8) {
                        fields.push(validatedField);
                        break; // Move to next field type
                    }
                }
            }
        }
        
        // Phase 2: Semantic discovery with multi-container validation
        const additionalFields = await this.discoverAdditionalFieldsEnhanced(container, siteType);
        fields.push(...additionalFields);
        
        // Phase 3: Filter and rank by reliability
        const validatedFields = fields
            .filter(field => field.reliability >= 0.8)
            .sort((a, b) => b.confidence - a.confidence);
        
        console.log(`✅ Found ${validatedFields.length} validated fields across containers`);
        return validatedFields;
    }

    /**
     * Validate field selector across ALL container instances
     * Returns field object with reliability score or null if unreliable
     */
    async validateFieldAcrossContainers(containerElements, selector, fieldName, source = 'auto') {
        const validationResults = [];
        const samples = [];
        let totalMatches = 0;
        
        // Test selector against all container instances
        for (let i = 0; i < containerElements.length; i++) {
            const container = containerElements[i];
            const found = container.querySelector(selector);
            
            if (found) {
                totalMatches++;
                const sample = this.getSampleText(found);
                const semanticScore = this.calculateSemanticScore(found, fieldName);
                
                validationResults.push({
                    containerIndex: i,
                    found: true,
                    sample: sample,
                    semanticScore: semanticScore,
                    element: found
                });
                
                if (samples.length < 3) { // Collect up to 3 samples
                    samples.push(sample);
                }
            } else {
                validationResults.push({
                    containerIndex: i,
                    found: false
                });
            }
        }
        
        // Calculate reliability metrics
        const reliability = totalMatches / containerElements.length;
        const minReliabilityThreshold = 0.8; // 80% of containers must have this field
        
        if (reliability < minReliabilityThreshold) {
            console.log(`❌ Field '${fieldName}' failed reliability check: ${(reliability * 100).toFixed(1)}% (need ≥80%)`);
            return null;
        }
        
        // Calculate confidence based on multiple factors
        const avgSemanticScore = validationResults
            .filter(r => r.found)
            .reduce((sum, r) => sum + (r.semanticScore || 0.5), 0) / totalMatches;
        
        const consistencyScore = this.calculateSampleConsistency(samples);
        const baseConfidence = source === 'pattern' ? 0.9 : 0.7;
        
        const confidence = Math.min(
            baseConfidence * reliability * avgSemanticScore * consistencyScore,
            1.0
        );
        
        // Determine field type from best matched element
        const bestMatch = validationResults
            .filter(r => r.found)
            .sort((a, b) => (b.semanticScore || 0) - (a.semanticScore || 0))[0];
        
        const fieldType = this.determineFieldTypeEnhanced(bestMatch.element, fieldName, samples);
        
        console.log(`✅ Field '${fieldName}': ${(reliability * 100).toFixed(1)}% reliability, ${(confidence * 100).toFixed(1)}% confidence`);
        
        return {
            label: fieldName,
            selector: selector,
            element_type: fieldType,
            confidence: confidence,
            reliability: reliability,
            sample: samples[0] || '',
            samples: samples,
            source: source,
            validationResults: validationResults,
            consistencyScore: consistencyScore
        };
    }

    /**
     * Safely get className from any type of element
     * Handles SVG elements where className is SVGAnimatedString
     */
    getElementClassName(element) {
        try {
            // Try multiple approaches to get className
            if (typeof element.className === 'string') {
                return element.className.toLowerCase();
            } else if (element.classList && element.classList.length > 0) {
                return Array.from(element.classList).join(' ').toLowerCase();
            } else if (element.getAttribute) {
                return (element.getAttribute('class') || '').toLowerCase();
            }
            
            // Log warning for debugging
            console.warn('Auto-detector: Non-string className encountered', {
                tagName: element.tagName,
                classNameType: typeof element.className,
                element: element
            });
            
            return '';
        } catch (error) {
            console.warn('Auto-detector: Error accessing className', error);
            return '';
        }
    }

    /**
     * Calculate semantic relevance score for element-field pairing
     */
    calculateSemanticScore(element, fieldName) {
        let score = 0.5; // Base score
        
        const text = element.textContent.trim().toLowerCase();
        const className = this.getElementClassName(element);
        const id = element.id.toLowerCase();
        const tagName = element.tagName.toLowerCase();
        
        // Semantic hints from element attributes
        const fieldHints = fieldName.toLowerCase();
        if (className.includes(fieldHints) || id.includes(fieldHints)) {
            score += 0.3;
        }
        
        // Content-based semantic analysis
        switch (fieldName.toLowerCase()) {
            case 'email':
                if (text.includes('@') || element.href?.startsWith('mailto:')) score += 0.4;
                break;
            case 'phone':
                if (/[\d\-\(\)\s]{8,}/.test(text) || element.href?.startsWith('tel:')) score += 0.4;
                break;
            case 'price':
                if (/[\$€£¥\d,\.]+/.test(text)) score += 0.4;
                break;
            case 'title':
            case 'name':
                if (tagName.match(/h[1-6]/) || text.length > 5) score += 0.3;
                break;
            case 'image':
                if (tagName === 'img' || element.style.backgroundImage) score += 0.4;
                break;
            case 'link':
                if (tagName === 'a' || element.href) score += 0.4;
                break;
        }
        
        // Position-based relevance (elements higher in DOM often more important)
        const rect = element.getBoundingClientRect();
        if (rect.top < 500) score += 0.1; // Above fold bonus
        
        return Math.min(score, 1.0);
    }

    /**
     * Calculate consistency score across sample texts
     */
    calculateSampleConsistency(samples) {
        if (samples.length <= 1) return 1.0;
        
        const lengths = samples.map(s => s.length);
        const avgLength = lengths.reduce((sum, len) => sum + len, 0) / lengths.length;
        
        // Check length consistency
        const lengthVariance = lengths.reduce((sum, len) => sum + Math.pow(len - avgLength, 2), 0) / lengths.length;
        const lengthScore = Math.max(0.3, 1 - (lengthVariance / (avgLength + 1)));
        
        // Check pattern consistency (basic)
        const hasNumbers = samples.map(s => /\d/.test(s));
        const hasSymbols = samples.map(s => /[@$€£¥\-\(\)]/.test(s));
        
        const numberConsistency = hasNumbers.every(h => h === hasNumbers[0]) ? 1.0 : 0.7;
        const symbolConsistency = hasSymbols.every(h => h === hasSymbols[0]) ? 1.0 : 0.8;
        
        return (lengthScore + numberConsistency + symbolConsistency) / 3;
    }

    /**
     * Enhanced field type determination with semantic analysis
     */
    determineFieldTypeEnhanced(element, fieldHint, samples = []) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim().toLowerCase();
        const href = element.href || element.getAttribute('href');
        const className = this.getElementClassName(element);
        const id = element.id.toLowerCase();
        
        // Combine current element with sample patterns for better detection
        const allTexts = [text, ...samples.map(s => s.toLowerCase())];
        const combinedText = allTexts.join(' ');
        
        // Enhanced semantic field type detection
        
        // Link detection
        if (tagName === 'a' || href || className.includes('link') || className.includes('url')) {
            return 'link';
        }
        
        // Image detection
        if (tagName === 'img' || element.style.backgroundImage || 
            className.includes('image') || className.includes('photo') || className.includes('avatar')) {
            return 'image';
        }
        
        // Email detection (enhanced with samples)
        const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
        if (fieldHint.includes('email') || href?.startsWith('mailto:') || 
            emailPattern.test(combinedText) || className.includes('email')) {
            return 'email';
        }
        
        // Phone detection (enhanced with samples)
        const phonePattern = /[\+]?[\s]?[\(]?[\d\s\-\(\)\.]{7,}/;
        if (fieldHint.includes('phone') || fieldHint.includes('tel') || 
            href?.startsWith('tel:') || phonePattern.test(combinedText) || 
            className.includes('phone') || className.includes('tel')) {
            return 'phone';
        }
        
        // Price detection (enhanced with currency detection)
        const pricePattern = /[\$€£¥₹][\d,]+\.?\d*|[\d,]+\.?\d*\s*(?:USD|EUR|GBP|JPY|INR)|price|cost|amount/i;
        if (fieldHint.includes('price') || fieldHint.includes('cost') || fieldHint.includes('amount') ||
            pricePattern.test(combinedText) || className.includes('price') || className.includes('cost')) {
            return 'price';
        }
        
        // Date detection (enhanced with multiple formats)
        const datePattern = /\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}|january|february|march|april|may|june|july|august|september|october|november|december/i;
        if (fieldHint.includes('date') || fieldHint.includes('time') || 
            tagName === 'time' || element.hasAttribute('datetime') ||
            datePattern.test(combinedText) || className.includes('date') || className.includes('time')) {
            return 'date';
        }
        
        // Button detection
        if (tagName === 'button' || element.hasAttribute('role') && element.getAttribute('role') === 'button' ||
            className.includes('btn') || className.includes('button')) {
            return 'button';
        }
        
        // Title/Name detection (enhanced with heading tag detection)
        if (tagName.match(/h[1-6]/) || fieldHint.includes('title') || fieldHint.includes('name') ||
            fieldHint.includes('heading') || className.includes('title') || className.includes('name')) {
            return 'text';
        }
        
        // Default to text for everything else
        return 'text';
    }
    
    determineFieldType(element, hint = '') {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        const href = element.href || element.getAttribute('href');
        const className = this.getElementClassName(element);
        const id = element.id.toLowerCase();
        
        // Enhanced link detection
        if (tagName === 'a' || href || 
            className.includes('link') || 
            className.includes('url') ||
            id.includes('link') ||
            element.closest('a')) {
            return 'link';
        }
        
        // Image detection (including background images)
        if (tagName === 'img' || 
            element.style.backgroundImage ||
            className.includes('image') ||
            className.includes('photo') ||
            className.includes('avatar')) {
            return 'image';
        }
        
        // Enhanced price detection
        if (hint.includes('price') || hint.includes('cost') || hint.includes('amount') ||
            className.includes('price') || className.includes('cost') ||
            text.match(/\$[\d,]+\.?\d*|[\d,]+\.?\d*\s*USD|€[\d,]+\.?\d*|£[\d,]+\.?\d*|¥[\d,]+\.?\d*/)) {
            return 'text';
        }
        
        // Email detection
        if (hint.includes('email') || 
            href && href.startsWith('mailto:') ||
            text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
            return 'email';
        }
        
        // Phone detection
        if (hint.includes('phone') || hint.includes('tel') ||
            href && href.startsWith('tel:') ||
            text.match(/[\+]?[\s]?[\(]?[\d\s\-\(\)]{10,}/)) {
            return 'phone';
        }
        
        // Date detection
        if (hint.includes('date') || hint.includes('time') ||
            text.match(/\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}/)) {
            return 'date';
        }
        
        // Default to text for any other content
        return 'text';
    }
    
    /**
     * Enhanced field discovery within containers using multi-container validation
     */
    async discoverAdditionalFieldsEnhanced(container, siteType) {
        const additionalFields = [];
        
        // Enhanced common field patterns with better selectors
        const discoveryPatterns = [
            { selector: 'a[href]:not([href^="#"])', label: 'link', priority: 'high' },
            { selector: 'a[href^="mailto:"], [href^="mailto:"]', label: 'email', priority: 'high' },
            { selector: 'a[href^="tel:"], [href^="tel:"]', label: 'phone', priority: 'high' },
            { selector: 'img[src], [style*="background-image"]', label: 'image', priority: 'high' },
            { selector: '.btn, .button, [role="button"], button', label: 'button', priority: 'medium' },
            { selector: 'time, [datetime], .date, .time', label: 'date', priority: 'medium' },
            { selector: '.price, .cost, .amount, [class*="price"]', label: 'price', priority: 'high' },
            { selector: 'h1, h2, h3, .title, .name, .heading', label: 'title', priority: 'high' },
            { selector: '[data-id], [data-key], .id, .identifier', label: 'identifier', priority: 'low' },
            { selector: '.description, .summary, .content, p', label: 'description', priority: 'medium' },
            { selector: '.category, .tag, .label', label: 'category', priority: 'medium' },
            { selector: '.rating, .stars, .score', label: 'rating', priority: 'medium' }
        ];
        
        // Auto-discover additional meaningful elements
        const autoDiscoveredPatterns = await this.discoverDynamicPatterns(container.elements);
        discoveryPatterns.push(...autoDiscoveredPatterns);
        
        console.log(`🔍 Testing ${discoveryPatterns.length} discovery patterns across ${container.elements.length} containers`);
        
        // Test each pattern with multi-container validation
        for (const pattern of discoveryPatterns) {
            const validatedField = await this.validateFieldAcrossContainers(
                container.elements, 
                pattern.selector, 
                pattern.label, 
                'discovery'
            );
            
            if (validatedField && validatedField.reliability >= 0.8) {
                // Adjust confidence based on priority
                const priorityMultiplier = pattern.priority === 'high' ? 1.0 : 
                                         pattern.priority === 'medium' ? 0.9 : 0.8;
                validatedField.confidence *= priorityMultiplier;
                
                additionalFields.push(validatedField);
            }
        }
        
        console.log(`✅ Discovered ${additionalFields.length} additional validated fields`);
        return additionalFields;
    }

    /**
     * Dynamically discover patterns from container structure
     */
    async discoverDynamicPatterns(containerElements) {
        const patterns = [];
        const firstElement = containerElements[0];
        
        if (!firstElement) return patterns;
        
        // Find all unique selectors within first container
        const allElements = firstElement.querySelectorAll('*');
        const selectorCounts = new Map();
        
        // Analyze element patterns
        for (const el of allElements) {
            if (el.textContent && el.textContent.trim().length > 2) {
                const className = this.getElementClassName(el);
                const tagName = el.tagName.toLowerCase();
                
                // Generate potential selectors
                if (className && !className.includes('v3-')) {
                    const classes = className.split(' ').filter(c => c && !c.startsWith('v3-'));
                    if (classes.length > 0) {
                        const selector = `.${classes[0]}`;
                        selectorCounts.set(selector, (selectorCounts.get(selector) || 0) + 1);
                    }
                }
                
                // Tag-based selectors for meaningful content
                if (['span', 'div', 'p', 'strong', 'em'].includes(tagName)) {
                    const selector = tagName;
                    selectorCounts.set(selector, (selectorCounts.get(selector) || 0) + 1);
                }
            }
        }
        
        // Convert promising selectors to patterns
        for (const [selector, count] of selectorCounts) {
            if (count === 1) { // Unique elements are more likely to be meaningful
                const element = firstElement.querySelector(selector);
                if (element && element.textContent.trim().length > 2) {
                    patterns.push({
                        selector: selector,
                        label: this.generateFieldLabel(element, selector),
                        priority: 'medium'
                    });
                }
            }
        }
        
        return patterns.slice(0, 10); // Limit to top 10 dynamic patterns
    }

    /**
     * Generate meaningful field labels from elements
     */
    generateFieldLabel(element, selector) {
        const text = element.textContent.trim().toLowerCase();
        const className = this.getElementClassName(element);
        
        // Try to infer field type from content
        if (text.includes('@')) return 'email';
        if (/[\d\-\(\)\s]{8,}/.test(text)) return 'phone';
        if (/[\$€£¥]/.test(text)) return 'price';
        if (element.tagName.match(/h[1-6]/i)) return 'text';
        if (className.includes('date') || className.includes('time')) return 'date';
        if (element.tagName.toLowerCase() === 'img') return 'image';
        if (element.tagName.toLowerCase() === 'a') return 'link';
        
        // Generate from class name
        if (className) {
            const meaningfulClass = className.split(' ').find(c => 
                c.length > 3 && !c.startsWith('v3-') && !/\d/.test(c)
            );
            if (meaningfulClass) {
                return meaningfulClass.replace(/[-_]/g, ' ');
            }
        }
        
        // Generate from selector
        const cleanSelector = selector.replace(/[.#]/g, '').replace(/[-_]/g, ' ');
        return cleanSelector || 'content';
    }
    
    // Helper method to check if field is already suggested
    isFieldAlreadySuggested(label, existingFields) {
        return existingFields && existingFields.some(field => field.label === label);
    }
    
    getSampleText(element) {
        const text = element.textContent.trim();
        const maxLength = 50;
        
        if (text.length > maxLength) {
            return text.substring(0, maxLength) + '...';
        }
        
        return text || '[No text content]';
    }
    
    displayEnhancedSuggestions(suggestions) {
        const container = this.panel.querySelector('#autodetect-suggestions');
        container.innerHTML = '';
        
        this.suggestions = suggestions;
        
        for (const suggestion of suggestions) {
            const div = document.createElement('div');
            div.style.cssText = `
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 12px;
                background: #f9f9f9;
            `;
            
            div.innerHTML = `
                <div style="padding: 12px; border-bottom: 1px solid #eee; background: white; border-radius: 4px 4px 0 0;">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <strong style="color: #333; font-size: 13px;">📦 ${suggestion.label}</strong>
                        <span style="color: #666; font-size: 11px; margin-left: auto;">
                            ${suggestion.count} items • ${Math.min(Math.round(suggestion.confidence * 100), 100)}% confidence
                        </span>
                    </div>
                    <div style="font-size: 11px; color: #666; margin-top: 4px;">
                        ${suggestion.selector}
                    </div>
                </div>
                <div style="padding: 8px 12px;">
                    <div style="font-size: 11px; color: #666; margin-bottom: 8px;">Suggested fields:</div>
                    ${suggestion.fields.map(field => `
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 11px;">
                            <span style="color: #333;">${field.label}</span>
                            <span style="color: #666; font-style: italic;">${field.sample}</span>
                        </div>
                    `).join('')}
                </div>
                <div style="padding: 8px 12px; border-top: 1px solid #eee;">
                    <button class="preview-btn" data-index="${suggestions.indexOf(suggestion)}" 
                            style="background: #17a2b8; color: white; border: none; padding: 6px 12px; border-radius: 3px; cursor: pointer; font-size: 11px; margin-right: 8px;">
                        Preview
                    </button>
                    <button class="apply-btn" data-index="${suggestions.indexOf(suggestion)}" 
                            style="background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 3px; cursor: pointer; font-size: 11px;">
                        Apply
                    </button>
                </div>
            `;
            
            container.appendChild(div);
        }
        
        // Add event listeners
        container.querySelectorAll('.preview-btn').forEach(btn => {
            btn.onclick = () => this.previewSuggestion(parseInt(btn.dataset.index));
        });
        
        container.querySelectorAll('.apply-btn').forEach(btn => {
            btn.onclick = () => this.applySuggestionV3(parseInt(btn.dataset.index));
        });
        
        // Show apply all button if we have suggestions
        if (suggestions.length > 0) {
            this.panel.querySelector('#apply-suggestions').style.display = 'inline-block';
        }
    }
    
    previewSuggestion(index) {
        const suggestion = this.suggestions[index];
        this.clearHighlights();
        
        // Highlight container elements
        const elements = document.querySelectorAll(suggestion.selector);
        elements.forEach((element, i) => {
            if (i < 5) { // Only highlight first 5 for performance
                this.highlightElement(element, '#007bff', 'Container');
                
                // Highlight fields within container
                suggestion.fields.forEach(field => {
                    const fieldElement = element.querySelector(field.selector);
                    if (fieldElement) {
                        this.highlightElement(fieldElement, '#28a745', field.label);
                    }
                });
            }
        });
        
        // Auto-scroll to first element
        if (elements.length > 0) {
            elements[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    highlightElement(element, color, label) {
        element.style.outline = `2px solid ${color}`;
        element.style.outlineOffset = '1px';
        
        // Add label
        const labelEl = document.createElement('div');
        labelEl.textContent = label;
        labelEl.style.cssText = `
            position: absolute;
            background: ${color};
            color: white;
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
            z-index: 10000;
            pointer-events: none;
            font-family: monospace;
        `;
        
        // Position label
        const rect = element.getBoundingClientRect();
        labelEl.style.top = (rect.top + window.scrollY - 20) + 'px';
        labelEl.style.left = (rect.left + window.scrollX) + 'px';
        
        labelEl.className = 'auto-detect-label';
        document.body.appendChild(labelEl);
    }
    
    applySuggestionV3(index) {
        const suggestion = this.suggestions[index];
        
        // Integrate with V3 Interactive Overlay if available
        if (window.v3InteractiveOverlay) {
            const overlay = window.v3InteractiveOverlay;
            
            // Create container in V3 overlay
            const containerData = {
                id: `container_${Date.now()}`,
                label: suggestion.label,
                selector: suggestion.selector,
                element_type: 'container',
                count: suggestion.count,
                sub_elements: suggestion.fields.map(field => ({
                    id: `field_${Date.now()}_${field.label}`,
                    label: field.label,
                    selector: field.selector,
                    element_type: field.element_type,
                    is_required: true,
                    sample_text: field.sample || ''
                }))
            };
            
            // Add container to overlay state
            overlay.state.containers.push(containerData);
            overlay.state.currentContainer = containerData;
            
            // Highlight container elements
            const elements = document.querySelectorAll(suggestion.selector);
            elements.forEach(el => {
                overlay.highlightElement(el, overlay.config.highlightColors.container, 'container', true);
            });
            
            // Highlight field elements within containers
            suggestion.fields.forEach(field => {
                elements.forEach(containerEl => {
                    const fieldEl = containerEl.querySelector(field.selector);
                    if (fieldEl) {
                        overlay.highlightElement(fieldEl, overlay.config.highlightColors.field, 'field', true);
                    }
                });
            });
            
            // Update the template builder sidebar
            overlay.updateSidebar();
            
            // Visual feedback
            this.updateStatus(`✅ Applied: ${suggestion.label} with ${suggestion.fields.length} fields`);
            overlay.showNotification(`Container applied: ${suggestion.label} (${suggestion.count} items)`);
            
        } else if (window.ScraperModules && window.ScraperModules.stateManager) {
            // Fallback to V2 system
            const stateManager = window.ScraperModules.stateManager;
            
            const containerData = {
                label: suggestion.label,
                selector: suggestion.selector,
                selector_type: 'css',
                element_type: 'container',
                is_multiple: true,
                is_required: true,
                is_container: true,
                sub_elements: suggestion.fields.map(field => ({
                    label: field.label,
                    selector: field.selector,
                    element_type: field.element_type,
                    is_required: true
                }))
            };
            
            stateManager.addContainer(containerData);
            this.updateStatus(`✅ Applied: ${suggestion.label} with ${suggestion.fields.length} fields`);
            
        } else {
            // No overlay system available
            console.log('V3 Auto-detected container:', suggestion);
            this.updateStatus(`📋 Container data logged to console - no overlay system found`);
        }
    }
    
    markElementAsContainer(element) {
        element.style.border = '2px dashed #007bff';
        element.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
    }
    
    /**
     * Legacy analyze method - preserved for backward compatibility
     */
    analyze() {
        console.log('🔍 Starting intelligent auto-detection...');
        
        const analysis = {
            containers: this.detectContainers(),
            pagination: this.detectPagination(),
            dataStructure: this.analyzeDataStructure(),
            suggestions: []
        };
        
        // Generate suggestions based on analysis
        analysis.suggestions = this.generateSuggestions(analysis);
        
        console.log('📊 Analysis complete:', analysis);
        return analysis;
    }
    
    /**
     * Detect repeating container elements
     */
    detectContainers() {
        const candidates = new Map();
        
        // Check each pattern
        for (const [type, pattern] of Object.entries(this.patterns.containers)) {
            for (const selector of pattern.selectors) {
                const elements = document.querySelectorAll(selector);
                
                if (elements.length > 2) {  // Need at least 3 for pattern
                    const similarity = this.calculateSimilarity(elements);
                    
                    if (similarity > 0.8) {
                        candidates.set(selector, {
                            type,
                            count: elements.length,
                            similarity,
                            selector,
                            elements: Array.from(elements).slice(0, 3),  // Sample
                            structure: this.analyzeStructure(elements[0])
                        });
                    }
                }
            }
        }
        
        // Rank candidates by score
        const ranked = Array.from(candidates.values())
            .sort((a, b) => b.similarity * b.count - a.similarity * a.count)
            .slice(0, 5);
        
        return ranked;
    }
    
    /**
     * Calculate similarity between elements
     */
    calculateSimilarity(elements) {
        if (elements.length < 2) return 0;
        
        const structures = Array.from(elements).map(el => this.getElementStructure(el));
        const reference = structures[0];
        
        let totalScore = 0;
        for (let i = 1; i < structures.length; i++) {
            totalScore += this.compareStructures(reference, structures[i]);
        }
        
        return totalScore / (structures.length - 1);
    }
    
    /**
     * Get element structure for comparison
     */
    getElementStructure(element) {
        const structure = {
            tag: element.tagName.toLowerCase(),
            classes: Array.from(element.classList).sort(),
            childTags: Array.from(element.children).map(child => child.tagName.toLowerCase()),
            attributes: Array.from(element.attributes).map(attr => attr.name).sort(),
            depth: this.getElementDepth(element),
            textPattern: this.getTextPattern(element)
        };
        
        // Cache for performance
        const key = this.getElementKey(element);
        this.cache.set(key, structure);
        
        return structure;
    }
    
    /**
     * Compare two element structures
     */
    compareStructures(struct1, struct2) {
        let score = 0;
        
        // Tag match
        if (struct1.tag === struct2.tag) score += 0.3;
        
        // Class similarity
        const classIntersection = struct1.classes.filter(c => struct2.classes.includes(c));
        const classUnion = [...new Set([...struct1.classes, ...struct2.classes])];
        if (classUnion.length > 0) {
            score += 0.2 * (classIntersection.length / classUnion.length);
        }
        
        // Child structure similarity
        const childSimilarity = this.compareArrays(struct1.childTags, struct2.childTags);
        score += 0.3 * childSimilarity;
        
        // Attribute similarity
        const attrSimilarity = this.compareArrays(struct1.attributes, struct2.attributes);
        score += 0.1 * attrSimilarity;
        
        // Depth similarity
        if (struct1.depth === struct2.depth) score += 0.1;
        
        return score;
    }
    
    /**
     * Detect pagination patterns
     */
    detectPagination() {
        const detected = [];
        
        // Check numeric pagination
        for (const selector of this.patterns.pagination.numeric.selectors) {
            const elements = document.querySelectorAll(selector);
            const pageLinks = Array.from(elements).filter(el => {
                const text = el.textContent.trim();
                return /^\d+$/.test(text) || /next|prev/i.test(text);
            });
            
            if (pageLinks.length > 2) {
                detected.push({
                    type: 'numeric',
                    selector,
                    confidence: 0.9,
                    elements: pageLinks.slice(0, 5)
                });
            }
        }
        
        // Check load more buttons
        for (const selector of this.patterns.pagination.loadMore.selectors) {
            const button = document.querySelector(selector);
            if (button && button.offsetHeight > 0) {  // Visible
                detected.push({
                    type: 'load_more',
                    selector,
                    confidence: 0.85,
                    element: button
                });
            }
        }
        
        // Check infinite scroll indicators
        const hasInfiniteScroll = this.patterns.pagination.infinite.indicators.some(
            selector => document.querySelector(selector) !== null
        );
        
        if (hasInfiniteScroll) {
            detected.push({
                type: 'infinite_scroll',
                confidence: 0.7,
                indicators: this.patterns.pagination.infinite.indicators
            });
        }
        
        return detected;
    }
    
    /**
     * Analyze data structure within containers
     */
    analyzeDataStructure() {
        const containerCandidates = this.detectContainers();
        if (containerCandidates.length === 0) return null;
        
        const primaryContainer = containerCandidates[0];
        const sampleElement = primaryContainer.elements[0];
        
        const structure = {
            container: primaryContainer.selector,
            fields: []
        };
        
        // Detect common fields
        for (const [fieldType, pattern] of Object.entries(this.patterns.fields)) {
            for (const selector of pattern.selectors) {
                const fieldElement = sampleElement.querySelector(selector);
                if (fieldElement) {
                    const fieldData = {
                        type: fieldType,
                        selector,
                        relativeSelector: this.getRelativeSelector(fieldElement, sampleElement),
                        sample: this.getFieldSample(fieldElement, fieldType)
                    };
                    
                    // Verify field exists in other containers
                    const consistency = this.checkFieldConsistency(
                        primaryContainer.elements,
                        fieldData.relativeSelector
                    );
                    
                    if (consistency > 0.8) {
                        fieldData.confidence = consistency;
                        structure.fields.push(fieldData);
                    }
                }
            }
        }
        
        return structure;
    }
    
    /**
     * Generate smart suggestions
     */
    generateSuggestions(analysis) {
        const suggestions = [];
        
        // Container suggestions
        if (analysis.containers.length > 0) {
            const primary = analysis.containers[0];
            suggestions.push({
                type: 'container',
                message: `Found ${primary.count} repeating ${primary.type} elements`,
                selector: primary.selector,
                action: 'select_container',
                confidence: primary.similarity
            });
            
            // Suggest fields within container
            if (analysis.dataStructure && analysis.dataStructure.fields.length > 0) {
                analysis.dataStructure.fields.forEach(field => {
                    suggestions.push({
                        type: 'field',
                        message: `${field.type} field detected`,
                        selector: field.relativeSelector,
                        parent: primary.selector,
                        action: 'add_field',
                        confidence: field.confidence
                    });
                });
            }
        }
        
        // Pagination suggestions
        if (analysis.pagination.length > 0) {
            const pagination = analysis.pagination[0];
            suggestions.push({
                type: 'pagination',
                message: `${pagination.type} pagination detected`,
                selector: pagination.selector,
                action: `configure_${pagination.type}`,
                confidence: pagination.confidence
            });
        }
        
        // Sort by confidence
        suggestions.sort((a, b) => b.confidence - a.confidence);
        
        return suggestions;
    }
    
    /**
     * Helper methods
     */
    
    getElementDepth(element) {
        let depth = 0;
        let current = element;
        while (current.parentElement && depth < 20) {
            current = current.parentElement;
            depth++;
        }
        return depth;
    }
    
    getTextPattern(element) {
        const text = element.textContent.trim();
        if (text.length === 0) return 'empty';
        if (/^\d+$/.test(text)) return 'numeric';
        if (/^\$[\d,]+\.?\d*$/.test(text)) return 'price';
        if (/^[A-Z][a-z]+(\s[A-Z][a-z]+)*$/.test(text)) return 'name';
        if (text.length > 100) return 'long_text';
        return 'text';
    }
    
    compareArrays(arr1, arr2) {
        const set1 = new Set(arr1);
        const set2 = new Set(arr2);
        const intersection = new Set([...set1].filter(x => set2.has(x)));
        const union = new Set([...set1, ...set2]);
        return union.size > 0 ? intersection.size / union.size : 0;
    }
    
    getElementKey(element) {
        // Create unique key for caching
        const rect = element.getBoundingClientRect();
        return `${element.tagName}_${rect.top}_${rect.left}`;
    }
    
    getRelativeSelector(element, container) {
        // Generate selector relative to container
        const path = [];
        let current = element;
        
        while (current && current !== container) {
            let selector = current.tagName.toLowerCase();
            
            // Add class if unique among siblings
            if (current.className) {
                const classes = Array.from(current.classList);
                const uniqueClass = classes.find(cls => {
                    const siblings = current.parentElement ? 
                        current.parentElement.querySelectorAll(`.${cls}`) : [];
                    return siblings.length === 1;
                });
                
                if (uniqueClass) {
                    selector += `.${uniqueClass}`;
                }
            }
            
            // Add nth-child if needed
            if (current.parentElement && !selector.includes('.')) {
                const index = Array.from(current.parentElement.children).indexOf(current);
                if (index > 0) {
                    selector += `:nth-child(${index + 1})`;
                }
            }
            
            path.unshift(selector);
            current = current.parentElement;
        }
        
        return path.join(' > ');
    }
    
    getFieldSample(element, fieldType) {
        if (fieldType === 'image') {
            return element.getAttribute('src') || element.getAttribute('data-src');
        }
        if (fieldType === 'link') {
            return element.getAttribute('href');
        }
        return element.textContent.trim().substring(0, 50);
    }
    
    checkFieldConsistency(containers, selector) {
        let found = 0;
        
        for (const container of containers) {
            if (container.querySelector(selector)) {
                found++;
            }
        }
        
        return found / containers.length;
    }
    
    /**
     * Apply suggestions automatically
     */
    applySuggestions(suggestions, stateManager) {
        console.log('🤖 Applying auto-detected suggestions...');
        
        for (const suggestion of suggestions) {
            if (suggestion.confidence < 0.7) continue;  // Skip low confidence
            
            switch (suggestion.action) {
                case 'select_container':
                    this.applyContainerSuggestion(suggestion, stateManager);
                    break;
                    
                case 'add_field':
                    this.applyFieldSuggestion(suggestion, stateManager);
                    break;
                    
                case 'configure_numeric':
                case 'configure_load_more':
                case 'configure_infinite_scroll':
                    this.applyPaginationSuggestion(suggestion, stateManager);
                    break;
            }
        }
    }
    
    applyContainerSuggestion(suggestion, stateManager) {
        const element = document.querySelector(suggestion.selector);
        if (!element) return;
        
        console.log(`✅ Auto-selecting container: ${suggestion.selector}`);
        
        // Simulate container selection
        const containerData = {
            label: `auto_${suggestion.type}`,
            selector: suggestion.selector,
            selector_type: 'css',
            element_type: 'container',
            is_multiple: true,
            is_container: true,
            sub_elements: []
        };
        
        stateManager.addContainer(containerData);
        stateManager.setState({ currentContainer: containerData });
        
        // Highlight elements
        document.querySelectorAll(suggestion.selector).forEach(el => {
            el.classList.add('scraper-auto-detected');
        });
    }
    
    applyFieldSuggestion(suggestion, stateManager) {
        if (!stateManager.getState().currentContainer) return;
        
        console.log(`✅ Auto-adding field: ${suggestion.type}`);
        
        const fieldData = {
            label: suggestion.type,
            selector: suggestion.selector,
            element_type: this.getElementType(suggestion.type),
            is_required: false
        };
        
        // Add to current container
        const state = stateManager.getState();
        const containers = [...state.containers];
        const currentIndex = containers.findIndex(
            c => c.label === state.currentContainer.label
        );
        
        if (currentIndex >= 0) {
            containers[currentIndex].sub_elements.push(fieldData);
            stateManager.setState({ containers });
        }
    }
    
    applyPaginationSuggestion(suggestion, stateManager) {
        console.log(`✅ Auto-configuring pagination: ${suggestion.type}`);
        
        // Add pagination configuration
        const paginationConfig = {
            type: suggestion.type,
            selector: suggestion.selector,
            auto_detected: true
        };
        
        stateManager.setState({
            pagination: paginationConfig
        });
    }
    
    getElementType(fieldType) {
        const typeMap = {
            title: 'text',
            price: 'price',
            image: 'image',
            link: 'link',
            email: 'email',
            phone: 'phone',
            date: 'date',
            button: 'button'
        };
        return typeMap[fieldType] || 'text';
    }
    
    // Enhanced method for applying all V3 suggestions
    applySuggestions() {
        if (this.suggestions && this.suggestions.length > 0) {
            // Apply each suggestion
            for (let i = 0; i < this.suggestions.length; i++) {
                this.applySuggestionV3(i);
            }
            
            // Update status and notification
            this.updateStatus(`✅ Applied all ${this.suggestions.length} V3 suggestions`);
            
            if (window.v3InteractiveOverlay) {
                window.v3InteractiveOverlay.showNotification(`Auto-detection complete: ${this.suggestions.length} containers applied`);
            }
            
        } else {
            // Fallback to legacy suggestions
            const analysis = this.analyze();
            if (analysis && analysis.suggestions && window.ScraperModules?.stateManager) {
                super.applySuggestions?.(analysis.suggestions, window.ScraperModules.stateManager);
            } else {
                this.updateStatus('❌ No suggestions available to apply');
            }
        }
    }
    
    // Emergency cleanup method for display issues
    emergencyCleanup() {
        console.log('🧹 Emergency cleanup starting...');
        
        // Hide all auto-detect panels
        const panels = document.querySelectorAll('#v3-autodetect-panel');
        panels.forEach(panel => panel.style.display = 'none');
        
        // Remove duplicate panels
        for (let i = 1; i < panels.length; i++) {
            panels[i].remove();
        }
        
        // Clear all highlights
        this.clearHighlights();
        
        // Reset active state
        this.isActive = false;
        
        // Fix corrupted styles
        const corruptedElements = document.querySelectorAll('[style*="undefined"], [style*="NaN"], [style*="null"]');
        corruptedElements.forEach(el => {
            const cleanStyle = el.style.cssText.replace(/undefined|NaN|null/g, '');
            el.style.cssText = cleanStyle;
        });
        
        console.log('✅ Emergency cleanup complete');
        
        // Also fix any confidence scores over 100%
        this.fixConfidenceScores();
        
        return 'Cleanup complete - overlay should be fixed';
    }
    
    fixConfidenceScores() {
        // Fix confidence scores in suggestions
        if (this.suggestions) {
            this.suggestions.forEach(suggestion => {
                if (suggestion.confidence > 1.0) {
                    suggestion.confidence = 1.0;
                }
                if (suggestion.fields) {
                    suggestion.fields.forEach(field => {
                        if (field.confidence > 1.0) {
                            field.confidence = 1.0;
                        }
                    });
                }
            });
        }
        
        // Update display
        if (this.suggestions && this.suggestions.length > 0) {
            this.displayEnhancedSuggestions(this.suggestions);
        }
        
        console.log('✅ Fixed confidence scores - all capped at 100%');
    }
}

// Enhanced initialization for V3 Auto Detector
let v3AutoDetector;

if (typeof window !== 'undefined') {
    // Initialize immediately or on DOMContentLoaded
    function initializeAutoDetector() {
        v3AutoDetector = new AutoDetector();
        
        // Make it globally accessible (both legacy and V3 names)
        window.AutoDetector = AutoDetector;
        window.V3AutoDetector = v3AutoDetector;
        window.v3AutoDetector = v3AutoDetector;
        
        // Add to ScraperModules if it exists (V2 integration)
        if (window.ScraperModules) {
            window.ScraperModules.autoDetector = v3AutoDetector;
            window.ScraperModules.v3AutoDetector = v3AutoDetector;
        }
        
        console.log('🤖 V3 Auto-Detector Enhanced initialized.');
        console.log('💡 Press Ctrl+Shift+A for V3 auto-detection');
        console.log('🔧 Click "Legacy Mode" for backward compatibility');
        
        // Add global cleanup function
        window.v3CleanupOverlay = () => v3AutoDetector.emergencyCleanup();
    }
    
    // Initialize based on DOM state
    if (document.readyState === 'loading') {
        // DOM still loading
        window.addEventListener('DOMContentLoaded', initializeAutoDetector);
    } else {
        // DOM already loaded (script injected after page load)
        setTimeout(initializeAutoDetector, 100);
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AutoDetector };
}

// Export for ES6 modules (removed for browser compatibility)