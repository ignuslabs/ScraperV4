/**
 * V3 Learning Service for User Corrections
 * 
 * Stores and applies user corrections to improve detection accuracy
 * Features:
 * - Local storage of corrections per domain
 * - Pattern application to similar DOM structures
 * - Domain-specific learning patterns
 * - Correction confidence scoring
 */

class V3LearningService {
    constructor() {
        this.storageKey = 'v3_detection_corrections';
        this.maxCorrectionsPerDomain = 50; // Limit storage size
        this.confidenceThreshold = 0.7; // Minimum confidence to apply corrections
        
        console.log('🧠 V3 Learning Service initialized');
    }

    /**
     * Store a user correction for future learning
     */
    storeCorrection(correctionData) {
        try {
            const domain = this.extractDomain(window.location.href);
            const correction = {
                id: this.generateCorrectionId(),
                domain: domain,
                timestamp: Date.now(),
                ...correctionData
            };

            console.log('📚 Storing correction for domain:', domain, correction);

            const stored = this.getStoredCorrections();
            if (!stored[domain]) {
                stored[domain] = [];
            }

            // Add new correction
            stored[domain].unshift(correction);

            // Limit corrections per domain
            if (stored[domain].length > this.maxCorrectionsPerDomain) {
                stored[domain] = stored[domain].slice(0, this.maxCorrectionsPerDomain);
            }

            localStorage.setItem(this.storageKey, JSON.stringify(stored));
            
            console.log(`✅ Correction stored. Domain has ${stored[domain].length} corrections`);
            return correction.id;
        } catch (error) {
            console.error('❌ Failed to store correction:', error);
            return null;
        }
    }

    /**
     * Get learned patterns for current domain
     */
    getLearnedPatterns(domain = null) {
        try {
            domain = domain || this.extractDomain(window.location.href);
            const stored = this.getStoredCorrections();
            const domainCorrections = stored[domain] || [];

            console.log(`🔍 Found ${domainCorrections.length} learned patterns for domain: ${domain}`);
            
            return domainCorrections.filter(correction => {
                // Only return recent and confident corrections
                const age = Date.now() - correction.timestamp;
                const maxAge = 30 * 24 * 60 * 60 * 1000; // 30 days
                
                return age < maxAge && (correction.confidence || 0.8) >= this.confidenceThreshold;
            });
        } catch (error) {
            console.error('❌ Failed to get learned patterns:', error);
            return [];
        }
    }

    /**
     * Apply learned corrections to detected patterns
     */
    applyCorrections(detectedContainers, detectedFields) {
        const domain = this.extractDomain(window.location.href);
        const learnedPatterns = this.getLearnedPatterns(domain);
        
        if (learnedPatterns.length === 0) {
            console.log('📝 No learned patterns to apply');
            return { containers: detectedContainers, fields: detectedFields };
        }

        console.log(`🎯 Applying ${learnedPatterns.length} learned patterns...`);

        let improvedContainers = [...detectedContainers];
        let improvedFields = [...detectedFields];

        // Apply container corrections
        for (const pattern of learnedPatterns) {
            if (pattern.type === 'container_correction') {
                improvedContainers = this.applyContainerCorrection(improvedContainers, pattern);
            } else if (pattern.type === 'field_correction') {
                improvedFields = this.applyFieldCorrection(improvedFields, pattern);
            } else if (pattern.type === 'selector_improvement') {
                improvedFields = this.applySelectorImprovement(improvedFields, pattern);
            }
        }

        const improvementCount = (improvedContainers.length - detectedContainers.length) + 
                               (improvedFields.length - detectedFields.length);
        
        if (improvementCount > 0) {
            console.log(`✅ Learning applied: +${improvementCount} improved detections`);
        }

        return {
            containers: improvedContainers,
            fields: improvedFields,
            appliedPatterns: learnedPatterns.length
        };
    }

    /**
     * Record when user manually adds/corrects a container
     */
    recordContainerCorrection(originalSelector, correctedSelector, element) {
        const structureSignature = this.generateStructureSignature(element);
        
        this.storeCorrection({
            type: 'container_correction',
            originalSelector: originalSelector,
            correctedSelector: correctedSelector,
            structureSignature: structureSignature,
            confidence: 0.9,
            elementContext: this.getElementContext(element)
        });
    }

    /**
     * Record when user manually adds/corrects a field
     */
    recordFieldCorrection(containerSelector, fieldLabel, originalSelector, correctedSelector, fieldType) {
        this.storeCorrection({
            type: 'field_correction',
            containerSelector: containerSelector,
            fieldLabel: fieldLabel,
            originalSelector: originalSelector,
            correctedSelector: correctedSelector,
            fieldType: fieldType,
            confidence: 0.85
        });
    }

    /**
     * Record when user improves a selector that was failing
     */
    recordSelectorImprovement(oldSelector, newSelector, fieldType, reliability) {
        this.storeCorrection({
            type: 'selector_improvement',
            oldSelector: oldSelector,
            newSelector: newSelector,
            fieldType: fieldType,
            reliability: reliability,
            confidence: Math.min(reliability, 0.9)
        });
    }

    /**
     * Apply container correction pattern
     */
    applyContainerCorrection(containers, pattern) {
        // Look for containers with similar structure
        const improved = [...containers];
        
        for (const container of containers) {
            if (container.selector === pattern.originalSelector) {
                // Direct match - apply correction
                container.selector = pattern.correctedSelector;
                container.learningApplied = true;
                console.log(`🔧 Applied container correction: ${pattern.originalSelector} → ${pattern.correctedSelector}`);
            } else if (this.isStructurallySimilar(container, pattern)) {
                // Similar structure - suggest improvement
                container.suggestedSelector = pattern.correctedSelector;
                container.learningSuggestion = true;
                console.log(`💡 Suggested container improvement based on learning`);
            }
        }

        return improved;
    }

    /**
     * Apply field correction pattern
     */
    applyFieldCorrection(fields, pattern) {
        const improved = [...fields];
        
        for (const field of fields) {
            if (field.selector === pattern.originalSelector && 
                field.label === pattern.fieldLabel) {
                // Direct match - apply correction
                field.selector = pattern.correctedSelector;
                field.element_type = pattern.fieldType;
                field.learningApplied = true;
                field.confidence = Math.min(field.confidence + 0.1, 1.0);
                console.log(`🔧 Applied field correction: ${pattern.fieldLabel}`);
            }
        }

        return improved;
    }

    /**
     * Apply selector improvement pattern
     */
    applySelectorImprovement(fields, pattern) {
        const improved = [...fields];
        
        for (const field of fields) {
            if (field.selector === pattern.oldSelector && 
                field.element_type === pattern.fieldType) {
                // Apply learned selector improvement
                field.selector = pattern.newSelector;
                field.confidence = Math.min(field.confidence * 1.1, 1.0);
                field.learningApplied = true;
                console.log(`🔧 Applied selector improvement: ${pattern.oldSelector} → ${pattern.newSelector}`);
            }
        }

        return improved;
    }

    /**
     * Generate structure signature for similarity matching
     */
    generateStructureSignature(element) {
        const tagName = element.tagName.toLowerCase();
        const classes = Array.from(element.classList).filter(c => !c.startsWith('v3-'));
        const childCount = element.children.length;
        const textLength = element.textContent.trim().length;
        
        return {
            tagName: tagName,
            classes: classes.slice(0, 3), // Top 3 classes
            childCount: childCount,
            textLength: Math.floor(textLength / 10) * 10, // Rounded to nearest 10
            depth: this.calculateElementDepth(element)
        };
    }

    /**
     * Get element context for pattern matching
     */
    getElementContext(element) {
        const parent = element.parentElement;
        return {
            parentTag: parent ? parent.tagName.toLowerCase() : null,
            parentClasses: parent ? Array.from(parent.classList).slice(0, 2) : [],
            siblingCount: parent ? parent.children.length : 0,
            position: parent ? Array.from(parent.children).indexOf(element) : 0
        };
    }

    /**
     * Check if container is structurally similar to learned pattern
     */
    isStructurallySimilar(container, pattern) {
        if (!pattern.structureSignature || !container.elements || container.elements.length === 0) {
            return false;
        }

        const element = container.elements[0];
        const currentSignature = this.generateStructureSignature(element);
        const learnedSignature = pattern.structureSignature;

        // Calculate similarity score
        let similarity = 0;
        let factors = 0;

        // Tag name match (30%)
        if (currentSignature.tagName === learnedSignature.tagName) {
            similarity += 0.3;
        }
        factors += 0.3;

        // Class similarity (25%)
        const classIntersection = currentSignature.classes.filter(c => 
            learnedSignature.classes.includes(c)
        );
        const classUnion = [...new Set([...currentSignature.classes, ...learnedSignature.classes])];
        if (classUnion.length > 0) {
            similarity += 0.25 * (classIntersection.length / classUnion.length);
        }
        factors += 0.25;

        // Child count similarity (20%)
        const childDiff = Math.abs(currentSignature.childCount - learnedSignature.childCount);
        const maxChildren = Math.max(currentSignature.childCount, learnedSignature.childCount, 1);
        similarity += 0.2 * (1 - childDiff / maxChildren);
        factors += 0.2;

        // Text length similarity (15%)
        const textDiff = Math.abs(currentSignature.textLength - learnedSignature.textLength);
        const maxText = Math.max(currentSignature.textLength, learnedSignature.textLength, 1);
        similarity += 0.15 * (1 - textDiff / maxText);
        factors += 0.15;

        // Depth similarity (10%)
        const depthDiff = Math.abs(currentSignature.depth - learnedSignature.depth);
        similarity += 0.1 * (depthDiff <= 1 ? 1 : 0.5);
        factors += 0.1;

        const finalSimilarity = factors > 0 ? similarity / factors : 0;
        return finalSimilarity >= 0.7; // 70% similarity threshold
    }

    /**
     * Helper method to calculate element depth
     */
    calculateElementDepth(element) {
        let depth = 0;
        let current = element;
        while (current.parentElement && current !== document.body) {
            depth++;
            current = current.parentElement;
        }
        return depth;
    }

    /**
     * Get all stored corrections
     */
    getStoredCorrections() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('❌ Failed to get stored corrections:', error);
            return {};
        }
    }

    /**
     * Extract domain from URL
     */
    extractDomain(url) {
        try {
            return new URL(url).hostname.replace('www.', '');
        } catch (error) {
            return 'unknown';
        }
    }

    /**
     * Generate unique correction ID
     */
    generateCorrectionId() {
        return `correction_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get learning statistics
     */
    getLearningStats() {
        const stored = this.getStoredCorrections();
        const domains = Object.keys(stored);
        let totalCorrections = 0;
        
        for (const domain of domains) {
            totalCorrections += stored[domain].length;
        }

        return {
            totalDomains: domains.length,
            totalCorrections: totalCorrections,
            currentDomain: this.extractDomain(window.location.href),
            currentDomainCorrections: stored[this.extractDomain(window.location.href)]?.length || 0
        };
    }

    /**
     * Clear learning data (for testing/reset)
     */
    clearLearningData(domain = null) {
        try {
            if (domain) {
                const stored = this.getStoredCorrections();
                delete stored[domain];
                localStorage.setItem(this.storageKey, JSON.stringify(stored));
                console.log(`🗑️ Cleared learning data for domain: ${domain}`);
            } else {
                localStorage.removeItem(this.storageKey);
                console.log('🗑️ Cleared all learning data');
            }
        } catch (error) {
            console.error('❌ Failed to clear learning data:', error);
        }
    }
}

// Create global instance
window.V3LearningService = new V3LearningService();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = V3LearningService;
}