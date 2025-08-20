/**
 * Auto-Detector for ScraperV4 Interactive Selector
 * 
 * AI-powered pattern recognition for automatic element detection
 * Features:
 * - Site type detection
 * - Container pattern recognition
 * - Field type inference
 * - Multi-container validation
 */

class AutoDetector {
    constructor() {
        this.patternLibrary = this.loadPatternLibrary();
        this.detectedPatterns = [];
        this.siteType = null;
        this.confidence = 0;
    }
    
    /**
     * Load pattern library for common website structures
     */
    loadPatternLibrary() {
        return {
            'ecommerce': {
                indicators: ['product', 'price', 'cart', 'checkout', 'add to cart', 'buy now'],
                containers: [
                    { name: 'product_grid', selectors: ['.product-grid', '.products-list', '.product-listing', '[class*="product-grid"]'] },
                    { name: 'product_card', selectors: ['.product-card', '.product-item', '.product', '[class*="product-card"]'] },
                    { name: 'search_results', selectors: ['.search-results', '.results-list', '#search-results'] }
                ],
                fields: {
                    title: ['.product-title', '.product-name', 'h2.title', 'h3.name', '[itemprop="name"]'],
                    price: ['.price', '.product-price', '.cost', '[itemprop="price"]', '[class*="price"]'],
                    image: ['.product-image img', '.product-photo img', '[itemprop="image"]'],
                    rating: ['.rating', '.stars', '.review-rating', '[itemprop="ratingValue"]'],
                    description: ['.product-description', '.description', '[itemprop="description"]'],
                    availability: ['.availability', '.stock-status', '.in-stock', '[itemprop="availability"]']
                }
            },
            'news': {
                indicators: ['article', 'news', 'post', 'story', 'headline', 'byline'],
                containers: [
                    { name: 'article_list', selectors: ['.article-list', '.news-list', '.post-list', 'main article'] },
                    { name: 'article_card', selectors: ['article', '.article', '.post', '.news-item'] },
                    { name: 'headlines', selectors: ['.headlines', '.top-stories', '.featured-articles'] }
                ],
                fields: {
                    title: ['h1', 'h2.title', '.headline', '.article-title', '[itemprop="headline"]'],
                    author: ['.author', '.byline', '.writer', '[itemprop="author"]'],
                    date: ['.date', '.published', 'time', '[itemprop="datePublished"]'],
                    summary: ['.summary', '.excerpt', '.description', '[itemprop="description"]'],
                    category: ['.category', '.section', '.tag', '[itemprop="articleSection"]'],
                    image: ['.article-image img', '.featured-image img', '[itemprop="image"]']
                }
            },
            'directory': {
                indicators: ['listing', 'directory', 'business', 'contact', 'location', 'map'],
                containers: [
                    { name: 'listing_grid', selectors: ['.listings', '.directory-list', '.business-list'] },
                    { name: 'listing_card', selectors: ['.listing', '.business-card', '.directory-item'] }
                ],
                fields: {
                    name: ['.business-name', '.listing-title', 'h2.name', '[itemprop="name"]'],
                    address: ['.address', '.location', '[itemprop="address"]'],
                    phone: ['.phone', '.tel', '[itemprop="telephone"]', 'a[href^="tel:"]'],
                    email: ['.email', '[itemprop="email"]', 'a[href^="mailto:"]'],
                    website: ['.website', '.url', '[itemprop="url"]'],
                    rating: ['.rating', '.stars', '[itemprop="ratingValue"]'],
                    description: ['.description', '.about', '[itemprop="description"]']
                }
            },
            'real_estate': {
                indicators: ['property', 'listing', 'bedroom', 'bathroom', 'sqft', 'rent', 'sale'],
                containers: [
                    { name: 'property_grid', selectors: ['.property-grid', '.listings-grid', '.properties'] },
                    { name: 'property_card', selectors: ['.property-card', '.listing-card', '.property-item'] }
                ],
                fields: {
                    title: ['.property-title', '.listing-title', 'h2.title'],
                    price: ['.price', '.property-price', '.listing-price'],
                    address: ['.address', '.location', '.property-address'],
                    bedrooms: ['.bedrooms', '.beds', '[class*="bedroom"]'],
                    bathrooms: ['.bathrooms', '.baths', '[class*="bathroom"]'],
                    area: ['.area', '.sqft', '.size', '[class*="square"]'],
                    type: ['.property-type', '.listing-type'],
                    image: ['.property-image img', '.listing-photo img']
                }
            }
        };
    }
    
    /**
     * Detect patterns on the current page
     */
    async detectPatterns(rootElement = document.body) {
        // Detect site type
        this.siteType = this.detectSiteType(rootElement);
        
        // Find containers
        const containers = this.detectContainers(rootElement);
        
        // Find fields
        const fields = this.detectFields(rootElement);
        
        // Validate and score patterns
        const validatedPatterns = this.validatePatterns(containers, fields);
        
        return {
            siteType: this.siteType,
            confidence: this.confidence,
            containers: validatedPatterns.containers,
            fields: validatedPatterns.fields,
            suggestions: this.generateSuggestions(validatedPatterns)
        };
    }
    
    /**
     * Detect the type of website
     */
    detectSiteType(rootElement) {
        const pageText = rootElement.textContent.toLowerCase();
        const pageHTML = rootElement.innerHTML.toLowerCase();
        let scores = {};
        
        for (const [type, config] of Object.entries(this.patternLibrary)) {
            scores[type] = 0;
            
            // Check for indicator words
            config.indicators.forEach(indicator => {
                if (pageText.includes(indicator)) {
                    scores[type] += 1;
                }
                if (pageHTML.includes(indicator)) {
                    scores[type] += 0.5;
                }
            });
            
            // Check for typical selectors
            config.containers.forEach(container => {
                container.selectors.forEach(selector => {
                    if (rootElement.querySelector(selector)) {
                        scores[type] += 2;
                    }
                });
            });
        }
        
        // Find the highest scoring type
        let maxScore = 0;
        let detectedType = 'general';
        
        for (const [type, score] of Object.entries(scores)) {
            if (score > maxScore) {
                maxScore = score;
                detectedType = type;
            }
        }
        
        this.confidence = Math.min(maxScore / 10, 1); // Normalize confidence
        return detectedType;
    }
    
    /**
     * Detect container elements
     */
    detectContainers(rootElement) {
        const containers = [];
        const patterns = this.patternLibrary[this.siteType] || this.patternLibrary.general;
        
        if (!patterns || !patterns.containers) return containers;
        
        patterns.containers.forEach(containerPattern => {
            containerPattern.selectors.forEach(selector => {
                const elements = rootElement.querySelectorAll(selector);
                
                if (elements.length >= 2) {
                    // Analyze similarity
                    const similarity = this.analyzeContainerSimilarity(Array.from(elements));
                    
                    if (similarity.score > 0.7) {
                        containers.push({
                            name: containerPattern.name,
                            selector: selector,
                            count: elements.length,
                            similarity: similarity.score,
                            quality: this.calculateContainerQuality(elements[0], similarity),
                            subElements: similarity.commonElements
                        });
                    }
                }
            });
        });
        
        // Sort by quality score
        containers.sort((a, b) => b.quality - a.quality);
        
        return containers;
    }
    
    /**
     * Analyze similarity between container elements
     */
    analyzeContainerSimilarity(elements) {
        if (elements.length < 2) {
            return { score: 0, commonElements: [] };
        }
        
        // Get structure of first element as reference
        const referenceStructure = this.getElementStructure(elements[0]);
        let totalScore = 0;
        let commonElements = new Set();
        
        // Compare all elements to reference
        for (let i = 1; i < elements.length; i++) {
            const structure = this.getElementStructure(elements[i]);
            const similarity = this.compareStructures(referenceStructure, structure);
            totalScore += similarity.score;
            
            // Track common sub-elements
            similarity.commonTags.forEach(tag => commonElements.add(tag));
        }
        
        const averageScore = totalScore / (elements.length - 1);
        
        return {
            score: averageScore,
            commonElements: Array.from(commonElements)
        };
    }
    
    /**
     * Get element structure for comparison
     */
    getElementStructure(element) {
        const structure = {
            tag: element.tagName.toLowerCase(),
            classes: Array.from(element.classList),
            childTags: [],
            textLength: element.textContent.trim().length,
            hasLinks: false,
            hasImages: false,
            depth: 0
        };
        
        // Analyze children
        const children = element.children;
        for (let child of children) {
            structure.childTags.push(child.tagName.toLowerCase());
            
            if (child.tagName === 'A') structure.hasLinks = true;
            if (child.tagName === 'IMG') structure.hasImages = true;
        }
        
        // Calculate depth
        structure.depth = this.calculateDepth(element);
        
        return structure;
    }
    
    /**
     * Compare two element structures
     */
    compareStructures(struct1, struct2) {
        let score = 0;
        let factors = 0;
        
        // Tag match
        if (struct1.tag === struct2.tag) {
            score += 0.3;
        }
        factors += 0.3;
        
        // Class similarity
        const classIntersection = struct1.classes.filter(c => struct2.classes.includes(c));
        const classUnion = [...new Set([...struct1.classes, ...struct2.classes])];
        if (classUnion.length > 0) {
            score += (classIntersection.length / classUnion.length) * 0.2;
        }
        factors += 0.2;
        
        // Child structure similarity
        const childIntersection = struct1.childTags.filter(t => struct2.childTags.includes(t));
        const childUnion = [...new Set([...struct1.childTags, ...struct2.childTags])];
        if (childUnion.length > 0) {
            score += (childIntersection.length / childUnion.length) * 0.25;
        }
        factors += 0.25;
        
        // Content type match
        if (struct1.hasLinks === struct2.hasLinks) score += 0.1;
        if (struct1.hasImages === struct2.hasImages) score += 0.1;
        factors += 0.2;
        
        // Depth similarity
        if (Math.abs(struct1.depth - struct2.depth) <= 1) {
            score += 0.05;
        }
        factors += 0.05;
        
        return {
            score: factors > 0 ? score / factors : 0,
            commonTags: childIntersection
        };
    }
    
    /**
     * Calculate element depth
     */
    calculateDepth(element, maxDepth = 5) {
        let depth = 0;
        let current = element;
        
        while (current.children.length > 0 && depth < maxDepth) {
            current = current.children[0];
            depth++;
        }
        
        return depth;
    }
    
    /**
     * Calculate container quality score
     */
    calculateContainerQuality(element, similarity) {
        let quality = 0;
        
        // Sub-element richness (40%)
        const richness = this.calculateSubElementRichness(element);
        quality += richness * 0.4;
        
        // Structural consistency (20%)
        quality += similarity.score * 0.2;
        
        // Visual layout score (15%)
        const layoutScore = this.calculateVisualLayoutScore(element);
        quality += layoutScore * 0.15;
        
        // Container count factor (10%)
        const countFactor = Math.min(similarity.commonElements.length / 10, 1);
        quality += countFactor * 0.1;
        
        // Base quality threshold (15%)
        quality += 0.15;
        
        return quality;
    }
    
    /**
     * Calculate sub-element richness
     */
    calculateSubElementRichness(element) {
        const factors = {
            diversity: 0,
            semanticValue: 0,
            contentDepth: 0,
            interactivity: 0
        };
        
        // Diversity of element types
        const uniqueTags = new Set();
        element.querySelectorAll('*').forEach(el => {
            uniqueTags.add(el.tagName.toLowerCase());
        });
        factors.diversity = Math.min(uniqueTags.size / 10, 1);
        
        // Semantic value
        const semanticTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'time', 'address'];
        const hasSemanticTags = semanticTags.some(tag => element.querySelector(tag));
        factors.semanticValue = hasSemanticTags ? 1 : 0.5;
        
        // Content depth
        const textContent = element.textContent.trim();
        factors.contentDepth = Math.min(textContent.length / 500, 1);
        
        // Interactivity
        const hasLinks = element.querySelector('a') !== null;
        const hasButtons = element.querySelector('button') !== null;
        const hasInputs = element.querySelector('input, select, textarea') !== null;
        factors.interactivity = (hasLinks ? 0.4 : 0) + (hasButtons ? 0.3 : 0) + (hasInputs ? 0.3 : 0);
        
        // Calculate weighted average
        return (factors.diversity + factors.semanticValue + factors.contentDepth + factors.interactivity) / 4;
    }
    
    /**
     * Calculate visual layout score
     */
    calculateVisualLayoutScore(element) {
        const rect = element.getBoundingClientRect();
        let score = 0;
        
        // Size consistency
        if (rect.width > 100 && rect.height > 50) {
            score += 0.3;
        }
        
        // Visibility
        if (rect.top >= 0 && rect.left >= 0) {
            score += 0.3;
        }
        
        // Aspect ratio (not too thin)
        const aspectRatio = rect.width / rect.height;
        if (aspectRatio > 0.5 && aspectRatio < 5) {
            score += 0.2;
        }
        
        // Has content
        if (element.children.length > 0) {
            score += 0.2;
        }
        
        return score;
    }
    
    /**
     * Detect field elements
     */
    detectFields(rootElement) {
        const fields = [];
        const patterns = this.patternLibrary[this.siteType] || {};
        
        if (!patterns.fields) return fields;
        
        for (const [fieldType, selectors] of Object.entries(patterns.fields)) {
            selectors.forEach(selector => {
                const elements = rootElement.querySelectorAll(selector);
                
                if (elements.length > 0) {
                    // Take the first matching element as representative
                    const element = elements[0];
                    const confidence = this.calculateFieldConfidence(element, fieldType);
                    
                    if (confidence > 0.5) {
                        fields.push({
                            type: fieldType,
                            selector: selector,
                            count: elements.length,
                            confidence: confidence,
                            sampleText: element.textContent.trim().substring(0, 100)
                        });
                    }
                }
            });
        }
        
        // Sort by confidence
        fields.sort((a, b) => b.confidence - a.confidence);
        
        return fields;
    }
    
    /**
     * Calculate field confidence
     */
    calculateFieldConfidence(element, fieldType) {
        let confidence = 0.5; // Base confidence
        
        const text = element.textContent.toLowerCase();
        const classes = element.className.toLowerCase();
        const id = element.id.toLowerCase();
        
        // Check if field type is mentioned in attributes
        if (classes.includes(fieldType) || id.includes(fieldType)) {
            confidence += 0.3;
        }
        
        // Check content patterns
        switch (fieldType) {
            case 'price':
                if (text.match(/[\$€£¥]/)) confidence += 0.3;
                if (text.match(/\d+[.,]\d{2}/)) confidence += 0.2;
                break;
                
            case 'date':
                if (text.match(/\d{4}[-/]\d{2}[-/]\d{2}/)) confidence += 0.4;
                if (text.match(/jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec/i)) confidence += 0.2;
                break;
                
            case 'email':
                if (text.match(/[\w.-]+@[\w.-]+\.\w+/)) confidence += 0.5;
                break;
                
            case 'phone':
                if (text.match(/\+?\d[\d\s()-]+\d/)) confidence += 0.4;
                break;
                
            case 'rating':
                if (text.match(/\d(\.\d)?\/5|\d(\.\d)? stars?/i)) confidence += 0.4;
                if (element.querySelector('.star, .rating')) confidence += 0.2;
                break;
        }
        
        // Check for semantic HTML
        if (element.getAttribute('itemprop') === fieldType) {
            confidence += 0.3;
        }
        
        return Math.min(confidence, 1);
    }
    
    /**
     * Validate detected patterns
     */
    validatePatterns(containers, fields) {
        const validatedContainers = [];
        const validatedFields = [];
        
        // Validate containers
        containers.forEach(container => {
            if (container.quality > 0.5 && container.count >= 2) {
                validatedContainers.push(container);
            }
        });
        
        // Validate fields
        fields.forEach(field => {
            if (field.confidence > 0.6) {
                validatedFields.push(field);
            }
        });
        
        return {
            containers: validatedContainers,
            fields: validatedFields
        };
    }
    
    /**
     * Generate suggestions for template creation
     */
    generateSuggestions(patterns) {
        const suggestions = [];
        
        // Suggest best container
        if (patterns.containers.length > 0) {
            const bestContainer = patterns.containers[0];
            suggestions.push({
                type: 'container',
                message: `Found ${bestContainer.count} similar items using selector "${bestContainer.selector}"`,
                selector: bestContainer.selector,
                confidence: bestContainer.quality,
                action: 'add_container'
            });
        }
        
        // Suggest high-confidence fields
        patterns.fields.slice(0, 5).forEach(field => {
            suggestions.push({
                type: 'field',
                message: `Detected ${field.type} field: "${field.sampleText.substring(0, 30)}..."`,
                selector: field.selector,
                fieldType: field.type,
                confidence: field.confidence,
                action: 'add_field'
            });
        });
        
        // Add recommendation
        if (suggestions.length > 0) {
            suggestions.unshift({
                type: 'recommendation',
                message: `Detected ${this.siteType} website pattern with ${Math.round(this.confidence * 100)}% confidence`,
                siteType: this.siteType,
                confidence: this.confidence
            });
        }
        
        return suggestions;
    }
    
    /**
     * Apply suggestions to the interactive overlay
     */
    applySuggestionsToOverlay(overlay, suggestions) {
        suggestions.forEach(suggestion => {
            if (suggestion.action === 'add_container') {
                const elements = document.querySelectorAll(suggestion.selector);
                if (elements.length > 0) {
                    overlay.addContainer(elements[0]);
                }
            } else if (suggestion.action === 'add_field') {
                const element = document.querySelector(suggestion.selector);
                if (element) {
                    overlay.addField(element);
                }
            }
        });
    }
}

// Export for use in other modules
window.AutoDetector = AutoDetector;