# Interactive Selection Architecture

This document provides a comprehensive explanation of ScraperV4's interactive element selection system architecture, design decisions, and implementation details. It covers the complete integration from the V3 system, pattern recognition algorithms, machine learning components, and the philosophy behind visual template creation.

## Architectural Overview

### System Philosophy

The interactive selection system transforms template creation from a code-writing exercise into a visual, intuitive process. This democratization of web scraping stems from several key principles:

1. **Visual First**: Humans naturally identify patterns visually before translating to code
2. **Learning System**: The tool should improve from user interactions
3. **Progressive Disclosure**: Simple tasks should be simple, complex tasks should be possible
4. **Fail Gracefully**: When automation fails, provide clear manual overrides
5. **Cross-Domain Intelligence**: Learning from one site should benefit similar sites

### High-Level Architecture

```
┌─────────────────── Interactive Selection System ──────────────────┐
│                                                                    │
│  ┌─ Frontend Layer ──────────────────┐                           │
│  │                                   │                           │
│  │  ┌─ Visual Components ─────┐     │     ┌─ User Events ────┐  │
│  │  │ • Interactive Overlay    │     │     │ • Click         │  │
│  │  │ • Element Highlighter    │────▶│◀────│ • Hover         │  │
│  │  │ • Selection Panel        │     │     │ • Drag          │  │
│  │  │ • Auto-Detect UI         │     │     │ • Contextmenu   │  │
│  │  └──────────────────────────┘     │     └─────────────────┘  │
│  │                                   │                           │
│  │  ┌─ Selector Engine ───────┐     │     ┌─ DOM Analysis ───┐  │
│  │  │ • CSS Generator         │     │     │ • Tree Walker    │  │
│  │  │ • XPath Builder         │◀────│────▶│ • Mutation Obs   │  │
│  │  │ • Similarity Scorer     │     │     │ • Shadow DOM     │  │
│  │  └──────────────────────────┘     │     └─────────────────┘  │
│  └────────────────────────────────────┘                           │
│                          │ Eel Bridge │                           │
│  ┌─ Backend Layer ───────▼────────────▼──────────────────────┐   │
│  │                                                            │   │
│  │  ┌─ InteractiveService ────┐    ┌─ Pattern Recognition ─┐ │   │
│  │  │ • Page Analysis         │    │ • Site Classifier     │ │   │
│  │  │ • Selector Validation   │◀──▶│ • Element Patterns    │ │   │
│  │  │ • Template Generation   │    │ • Field Detection     │ │   │
│  │  │ • Learning Application  │    │ • Container Finding   │ │   │
│  │  └──────────────────────────┘    └──────────────────────┘ │   │
│  │                                                            │   │
│  │  ┌─ Learning System ───────┐    ┌─ Template System ─────┐ │   │
│  │  │ • Correction Storage    │    │ • Template Manager    │ │   │
│  │  │ • Pattern Database      │───▶│ • Selector Validator  │ │   │
│  │  │ • Domain Profiles       │    │ • Adaptive Selectors  │ │   │
│  │  │ • Success Tracking      │    │ • Export/Import       │ │   │
│  │  └──────────────────────────┘    └──────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Interactive Overlay Component

The overlay is the primary visual interface for element selection, implemented as a transparent layer over the target website.

#### Design Decisions

**Injection Method**: The overlay can be injected via:
- **Iframe embedding**: For same-origin or CORS-permissive sites
- **Browser extension**: For cross-origin sites (future)
- **New window with postMessage**: Current cross-origin solution

**Z-Index Management**: 
```javascript
// Ensuring overlay stays on top
const Z_INDEX_LEVELS = {
    HIGHLIGHT: 2147483640,    // Near maximum
    OVERLAY: 2147483641,
    TOOLBAR: 2147483642,
    MODAL: 2147483647         // Maximum
};
```

#### Event Handling Architecture

```javascript
class InteractiveOverlay {
    constructor(targetDocument) {
        this.targetDoc = targetDocument;
        this.eventListeners = new Map();
        this.capturePhase = true; // Capture events before site handlers
        
        this.initializeEventCapture();
    }
    
    initializeEventCapture() {
        // Prevent site from interfering with selection
        this.interceptedEvents = [
            'click', 'dblclick', 'mousedown', 'mouseup',
            'contextmenu', 'dragstart', 'selectstart'
        ];
        
        this.interceptedEvents.forEach(eventType => {
            this.targetDoc.addEventListener(eventType, (e) => {
                if (this.isSelectionMode) {
                    e.stopPropagation();
                    e.preventDefault();
                    this.handleInterceptedEvent(e);
                }
            }, true); // Use capture phase
        });
    }
}
```

### Selector Generation Engine

The selector generator creates robust, maintainable CSS selectors from DOM elements.

#### Algorithm Design

```javascript
class SelectorGenerator {
    generateSelector(element, options = {}) {
        const strategies = [
            this.generateIdSelector,
            this.generateDataAttributeSelector,
            this.generateClassSelector,
            this.generateSemanticSelector,
            this.generateHierarchicalSelector
        ];
        
        const selectors = [];
        for (const strategy of strategies) {
            const selector = strategy.call(this, element, options);
            if (selector) {
                const quality = this.evaluateSelectorQuality(selector, element);
                selectors.push({ selector, quality, strategy: strategy.name });
            }
        }
        
        return this.selectBestSelector(selectors, element);
    }
    
    evaluateSelectorQuality(selector, targetElement) {
        const doc = targetElement.ownerDocument;
        const matches = doc.querySelectorAll(selector);
        
        // Quality factors
        const uniqueness = matches.length === 1 ? 1.0 : 1.0 / matches.length;
        const specificity = this.calculateSpecificity(selector);
        const robustness = this.calculateRobustness(selector);
        const readability = this.calculateReadability(selector);
        
        // Weighted quality score
        return {
            score: (uniqueness * 0.4) + (robustness * 0.3) + 
                   (specificity * 0.2) + (readability * 0.1),
            factors: { uniqueness, specificity, robustness, readability }
        };
    }
}
```

#### Selector Strategies

**ID-Based Selection**:
```javascript
generateIdSelector(element) {
    if (element.id && this.isValidId(element.id)) {
        return `#${CSS.escape(element.id)}`;
    }
    return null;
}
```

**Data Attribute Selection**:
```javascript
generateDataAttributeSelector(element) {
    const dataAttrs = ['data-test-id', 'data-qa', 'data-testid', 
                       'data-cy', 'data-test'];
    
    for (const attr of dataAttrs) {
        if (element.hasAttribute(attr)) {
            const value = element.getAttribute(attr);
            return `[${attr}="${CSS.escape(value)}"]`;
        }
    }
    
    // Generic data attributes
    const allDataAttrs = Array.from(element.attributes)
        .filter(attr => attr.name.startsWith('data-'));
    
    if (allDataAttrs.length > 0) {
        const bestAttr = this.selectBestDataAttribute(allDataAttrs);
        return `[${bestAttr.name}="${CSS.escape(bestAttr.value)}"]`;
    }
    
    return null;
}
```

### Pattern Recognition System

The auto-detector uses pattern recognition to identify common web page structures.

#### Site Classification

```javascript
class SiteClassifier {
    constructor() {
        this.patterns = {
            ecommerce: {
                indicators: [
                    { selector: '[class*="price"]', weight: 0.3 },
                    { selector: '[class*="cart"]', weight: 0.3 },
                    { selector: '[class*="product"]', weight: 0.2 },
                    { text: /\$\d+\.\d{2}/, weight: 0.2 }
                ],
                threshold: 0.7
            },
            news: {
                indicators: [
                    { selector: 'article', weight: 0.3 },
                    { selector: '[class*="author"]', weight: 0.2 },
                    { selector: 'time, [datetime]', weight: 0.2 },
                    { selector: '[class*="headline"]', weight: 0.3 }
                ],
                threshold: 0.6
            },
            directory: {
                indicators: [
                    { selector: '[class*="listing"]', weight: 0.3 },
                    { selector: '[class*="result"]', weight: 0.3 },
                    { repeating: true, minCount: 5, weight: 0.4 }
                ],
                threshold: 0.65
            }
        };
    }
    
    classifySite(document) {
        const scores = {};
        
        for (const [type, pattern] of Object.entries(this.patterns)) {
            scores[type] = this.calculatePatternScore(document, pattern);
        }
        
        const bestMatch = Object.entries(scores)
            .sort(([,a], [,b]) => b - a)[0];
        
        return {
            type: bestMatch[0],
            confidence: bestMatch[1],
            allScores: scores
        };
    }
}
```

#### Container Detection Algorithm

```javascript
class ContainerDetector {
    findContainers(document) {
        const candidates = this.identifyCandidateContainers(document);
        const scored = candidates.map(container => ({
            element: container,
            score: this.scoreContainer(container),
            items: this.extractContainerItems(container)
        }));
        
        return scored
            .filter(c => c.score > 0.6 && c.items.length > 1)
            .sort((a, b) => b.score - a.score);
    }
    
    scoreContainer(element) {
        const factors = {
            // Uniform children structure
            childUniformity: this.calculateChildUniformity(element),
            // Semantic HTML usage
            semanticScore: this.calculateSemanticScore(element),
            // Visual alignment (requires rendered page)
            visualAlignment: this.calculateVisualAlignment(element),
            // Class/attribute patterns
            patternConsistency: this.calculatePatternConsistency(element)
        };
        
        // Weighted scoring
        return (factors.childUniformity * 0.4) +
               (factors.semanticScore * 0.2) +
               (factors.visualAlignment * 0.2) +
               (factors.patternConsistency * 0.2);
    }
    
    calculateChildUniformity(container) {
        const children = Array.from(container.children);
        if (children.length < 2) return 0;
        
        const signatures = children.map(child => 
            this.generateStructureSignature(child)
        );
        
        // Count matching signatures
        const signatureCounts = {};
        signatures.forEach(sig => {
            signatureCounts[sig] = (signatureCounts[sig] || 0) + 1;
        });
        
        const maxCount = Math.max(...Object.values(signatureCounts));
        return maxCount / children.length;
    }
    
    generateStructureSignature(element) {
        // Create a signature representing element structure
        const signature = [];
        const walk = (el, depth = 0) => {
            if (depth > 3) return; // Limit depth
            
            signature.push(`${el.tagName}:${el.className.split(' ')[0] || ''}`);
            
            for (const child of el.children) {
                walk(child, depth + 1);
            }
        };
        
        walk(element);
        return signature.join('>');
    }
}
```

### Similarity Scoring Engine

Finding similar elements is crucial for container-based extraction.

```javascript
class SimilarityScorer {
    calculateSimilarity(element1, element2) {
        const scores = {
            structure: this.structuralSimilarity(element1, element2),
            style: this.styleSimilarity(element1, element2),
            content: this.contentSimilarity(element1, element2),
            position: this.positionalSimilarity(element1, element2)
        };
        
        // Weighted combination
        return (scores.structure * 0.4) +
               (scores.style * 0.3) +
               (scores.content * 0.2) +
               (scores.position * 0.1);
    }
    
    structuralSimilarity(el1, el2) {
        // Compare DOM structure
        const depth1 = this.getElementDepth(el1);
        const depth2 = this.getElementDepth(el2);
        const depthSim = 1 - Math.abs(depth1 - depth2) / Math.max(depth1, depth2);
        
        const children1 = el1.children.length;
        const children2 = el2.children.length;
        const childSim = children1 === children2 ? 1 : 
            1 - Math.abs(children1 - children2) / Math.max(children1, children2);
        
        const tag1 = el1.tagName;
        const tag2 = el2.tagName;
        const tagSim = tag1 === tag2 ? 1 : 0;
        
        return (depthSim + childSim + tagSim) / 3;
    }
    
    styleSimilarity(el1, el2) {
        const style1 = window.getComputedStyle(el1);
        const style2 = window.getComputedStyle(el2);
        
        const importantProps = [
            'display', 'position', 'float',
            'width', 'height', 'margin', 'padding'
        ];
        
        let matches = 0;
        importantProps.forEach(prop => {
            if (style1[prop] === style2[prop]) matches++;
        });
        
        return matches / importantProps.length;
    }
}
```

## Backend Architecture

### InteractiveService Design

The backend service orchestrates template generation, validation, and learning.

```python
class InteractiveService(BaseService):
    """Central service for interactive template creation."""
    
    def __init__(self):
        super().__init__()
        self.pattern_recognizer = PatternRecognizer()
        self.selector_validator = SelectorValidator()
        self.learning_system = LearningSystem()
        self.template_generator = TemplateGenerator()
        
    def analyze_page_structure(self, url: str) -> Dict[str, Any]:
        """Comprehensive page analysis for interactive selection."""
        
        # Fetch page content
        page_content = self.fetch_page(url)
        
        # Parse HTML
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Classify site type
        site_type = self.pattern_recognizer.classify_site(soup)
        
        # Detect containers
        containers = self.pattern_recognizer.find_containers(soup)
        
        # Identify common fields
        fields = self.pattern_recognizer.detect_fields(soup, site_type)
        
        # Check for pagination
        pagination = self.pattern_recognizer.find_pagination(soup)
        
        return {
            'url': url,
            'site_type': site_type,
            'containers': self.serialize_containers(containers),
            'suggested_fields': fields,
            'pagination': pagination,
            'statistics': {
                'total_elements': len(soup.find_all()),
                'interactive_elements': len(soup.find_all(['a', 'button', 'input'])),
                'images': len(soup.find_all('img')),
                'forms': len(soup.find_all('form'))
            }
        }
```

### Pattern Recognition Implementation

```python
class PatternRecognizer:
    """Advanced pattern recognition for web pages."""
    
    def __init__(self):
        self.site_patterns = self.load_site_patterns()
        self.field_patterns = self.load_field_patterns()
        
    def classify_site(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Classify website type using pattern matching."""
        
        scores = {}
        
        # E-commerce indicators
        ecommerce_score = 0
        if soup.find_all(class_=re.compile(r'price|cost|amount')):
            ecommerce_score += 0.3
        if soup.find_all(class_=re.compile(r'cart|basket|buy')):
            ecommerce_score += 0.3
        if soup.find_all(class_=re.compile(r'product|item')):
            ecommerce_score += 0.2
        if re.search(r'\$\d+\.\d{2}', soup.get_text()):
            ecommerce_score += 0.2
        scores['ecommerce'] = min(ecommerce_score, 1.0)
        
        # News site indicators
        news_score = 0
        if soup.find_all('article'):
            news_score += 0.3
        if soup.find_all(class_=re.compile(r'author|byline')):
            news_score += 0.25
        if soup.find_all(['time', '[datetime]']):
            news_score += 0.25
        if soup.find_all(class_=re.compile(r'headline|title')):
            news_score += 0.2
        scores['news'] = min(news_score, 1.0)
        
        # Directory indicators
        directory_score = 0
        listing_elements = soup.find_all(class_=re.compile(r'listing|result|item'))
        if len(listing_elements) > 5:
            directory_score += 0.4
        if soup.find_all(class_=re.compile(r'address|location')):
            directory_score += 0.3
        if soup.find_all(class_=re.compile(r'phone|contact')):
            directory_score += 0.3
        scores['directory'] = min(directory_score, 1.0)
        
        # Real estate indicators
        realestate_score = 0
        if soup.find_all(class_=re.compile(r'bedroom|bathroom|sqft')):
            realestate_score += 0.4
        if soup.find_all(class_=re.compile(r'listing|property')):
            realestate_score += 0.3
        if re.search(r'\b\d+\s*(bed|bath|sqft)\b', soup.get_text(), re.I):
            realestate_score += 0.3
        scores['realestate'] = min(realestate_score, 1.0)
        
        # Determine best match
        best_type = max(scores.items(), key=lambda x: x[1])
        
        return {
            'type': best_type[0],
            'confidence': best_type[1],
            'all_scores': scores
        }
    
    def find_containers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Detect repeating container elements."""
        
        containers = []
        
        # Find elements with multiple similar children
        for element in soup.find_all():
            if len(element.children) < 2:
                continue
                
            children = [child for child in element.children 
                       if hasattr(child, 'name')]
            
            if len(children) < 2:
                continue
            
            # Check if children have similar structure
            uniformity = self.calculate_uniformity(children)
            
            if uniformity > 0.7:
                containers.append({
                    'element': element,
                    'selector': self.generate_selector(element),
                    'uniformity': uniformity,
                    'item_count': len(children),
                    'sample_item': self.extract_item_structure(children[0])
                })
        
        # Sort by quality score
        containers.sort(key=lambda x: x['uniformity'] * x['item_count'], 
                       reverse=True)
        
        return containers[:5]  # Return top 5 containers
```

### Learning System Architecture

The learning system improves pattern recognition through user corrections.

```python
class LearningSystem:
    """Machine learning component for pattern improvement."""
    
    def __init__(self):
        self.corrections_db = self.load_corrections_database()
        self.pattern_weights = self.load_pattern_weights()
        self.domain_profiles = {}
        
    def apply_correction(self, correction: Dict[str, Any]) -> bool:
        """Learn from user corrections."""
        
        domain = self.extract_domain(correction['url'])
        
        # Store correction
        if domain not in self.corrections_db:
            self.corrections_db[domain] = []
        
        self.corrections_db[domain].append({
            'timestamp': datetime.now().isoformat(),
            'wrong_selector': correction['wrong_selector'],
            'correct_selector': correction['correct_selector'],
            'element_type': correction['element_type'],
            'context': correction.get('context', {})
        })
        
        # Update pattern weights
        self.update_pattern_weights(correction)
        
        # Update domain profile
        self.update_domain_profile(domain, correction)
        
        # Persist changes
        self.save_corrections_database()
        self.save_pattern_weights()
        
        return True
    
    def update_pattern_weights(self, correction: Dict[str, Any]):
        """Adjust pattern recognition weights based on corrections."""
        
        element_type = correction['element_type']
        
        # Analyze what went wrong
        wrong_features = self.extract_selector_features(
            correction['wrong_selector']
        )
        correct_features = self.extract_selector_features(
            correction['correct_selector']
        )
        
        # Adjust weights
        for feature in wrong_features:
            if feature not in correct_features:
                # This feature led to wrong selection
                self.pattern_weights[element_type][feature] *= 0.9
        
        for feature in correct_features:
            if feature not in wrong_features:
                # This feature indicates correct selection
                self.pattern_weights[element_type][feature] *= 1.1
        
        # Normalize weights
        self.normalize_weights(element_type)
    
    def get_learned_patterns(self, domain: str) -> Dict[str, Any]:
        """Retrieve learned patterns for a domain."""
        
        if domain not in self.domain_profiles:
            return {}
        
        profile = self.domain_profiles[domain]
        
        return {
            'selectors': profile.get('reliable_selectors', {}),
            'avoid_patterns': profile.get('avoid_patterns', []),
            'prefer_patterns': profile.get('prefer_patterns', []),
            'field_locations': profile.get('field_locations', {}),
            'success_rate': profile.get('success_rate', 0)
        }
```

### Template Generation and Validation

```python
class TemplateGenerator:
    """Generate templates from interactive selections."""
    
    def generate_template(self, selections: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete template from user selections."""
        
        template = {
            'name': selections.get('name', 'Interactive Template'),
            'description': selections.get('description', ''),
            'version': '1.0.0',
            'created_by': 'Interactive Selector',
            'created_at': datetime.now().isoformat(),
            'source_url': selections.get('url', ''),
            'selectors': {},
            'containers': {},
            'pagination': {},
            'processing_rules': {},
            'validation_rules': {}
        }
        
        # Process field selections
        for field_name, field_data in selections.get('fields', {}).items():
            selector = field_data['selector']
            
            # Add primary selector
            template['selectors'][field_name] = selector
            
            # Add fallbacks if provided
            if 'fallbacks' in field_data:
                if 'fallback_selectors' not in template:
                    template['fallback_selectors'] = {}
                template['fallback_selectors'][field_name] = field_data['fallbacks']
        
        # Process containers
        for container_name, container_data in selections.get('containers', {}).items():
            template['containers'][container_name] = {
                'selector': container_data['selector'],
                'fields': container_data['fields'],
                'min_items': container_data.get('min_items', 1),
                'max_items': container_data.get('max_items', None)
            }
        
        # Add validation rules based on field types
        template['validation_rules'] = self.generate_validation_rules(
            selections.get('field_types', {})
        )
        
        # Add processing rules
        template['processing_rules'] = self.generate_processing_rules(
            selections.get('field_types', {})
        )
        
        # Enable adaptive selectors by default
        template['adaptive_selectors'] = True
        
        return template
    
    def generate_validation_rules(self, field_types: Dict[str, str]) -> Dict[str, Any]:
        """Generate validation rules based on field types."""
        
        rules = {}
        
        for field_name, field_type in field_types.items():
            if field_type == 'price':
                rules[field_name] = {
                    'type': 'number',
                    'min': 0,
                    'pattern': r'[\d,]+\.?\d*'
                }
            elif field_type == 'email':
                rules[field_name] = {
                    'type': 'email',
                    'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                }
            elif field_type == 'phone':
                rules[field_name] = {
                    'type': 'phone',
                    'pattern': r'[\d\s\-\(\)\+]+'
                }
            elif field_type == 'date':
                rules[field_name] = {
                    'type': 'date',
                    'format': 'auto'  # Try multiple date formats
                }
            elif field_type == 'url':
                rules[field_name] = {
                    'type': 'url',
                    'resolve_relative': True
                }
        
        return rules
```

## Integration Points

### Eel Bridge Communication

The system uses Eel for bidirectional communication between Python and JavaScript.

```python
# Python side (api_routes.py)
@eel.expose
def start_interactive_mode(url: str) -> Dict[str, Any]:
    """Initialize interactive mode for a URL."""
    interactive_service = container.get(InteractiveService)
    analysis = interactive_service.analyze_page_structure(url)
    return {'success': True, 'analysis': analysis}

@eel.expose
def validate_selector_batch(selectors: List[str], html: str) -> Dict[str, Any]:
    """Validate multiple selectors against HTML."""
    results = {}
    for selector in selectors:
        results[selector] = validate_single_selector(selector, html)
    return results
```

```javascript
// JavaScript side
async function initializeInteractiveMode(url) {
    const result = await eel.start_interactive_mode(url)();
    if (result.success) {
        this.applyPageAnalysis(result.analysis);
        this.enableInteractiveSelection();
    }
}

async function validateSelectors(selectors) {
    const html = document.documentElement.outerHTML;
    const results = await eel.validate_selector_batch(selectors, html)();
    return results;
}
```

### Template System Integration

Interactive selections integrate seamlessly with the existing template system.

```python
class TemplateService(BaseService):
    """Extended with interactive template support."""
    
    def create_interactive_template(self, 
                                   selections: Dict[str, Any]) -> ScrapingTemplate:
        """Create template from interactive selections."""
        
        # Generate template structure
        template_data = self.template_generator.generate_template(selections)
        
        # Validate generated template
        validation_result = self.template_validator.validate_template(template_data)
        
        if not validation_result['valid']:
            raise ValueError(f"Invalid template: {validation_result['errors']}")
        
        # Save to template manager
        template = self.template_manager.create_template(
            name=template_data['name'],
            selectors=template_data['selectors'],
            validation_rules=template_data.get('validation_rules'),
            description=template_data.get('description')
        )
        
        # Store additional metadata
        self.store_interactive_metadata(template.id, selections)
        
        return template
```

## Performance Considerations

### DOM Traversal Optimization

```javascript
class DOMOptimizer {
    constructor() {
        // Cache frequently accessed elements
        this.elementCache = new WeakMap();
        
        // Batch DOM operations
        this.pendingOperations = [];
        this.rafId = null;
    }
    
    batchOperation(operation) {
        this.pendingOperations.push(operation);
        
        if (!this.rafId) {
            this.rafId = requestAnimationFrame(() => {
                this.executeBatch();
            });
        }
    }
    
    executeBatch() {
        // Execute all pending operations in single frame
        const operations = this.pendingOperations.splice(0);
        operations.forEach(op => op());
        this.rafId = null;
    }
}
```

### Selector Caching Strategy

```python
class SelectorCache:
    """LRU cache for validated selectors."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        
    def get(self, selector: str, html_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached validation result."""
        key = f"{selector}:{html_hash}"
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, selector: str, html_hash: str, result: Dict[str, Any]):
        """Cache validation result."""
        key = f"{selector}:{html_hash}"
        self.cache[key] = result
        
        # Evict least recently used if over capacity
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
```

## Security Considerations

### XSS Prevention

```javascript
class SecurityManager {
    sanitizeSelector(selector) {
        // Prevent XSS through selector injection
        const dangerous = ['<script', 'javascript:', 'onerror=', 'onclick='];
        
        for (const pattern of dangerous) {
            if (selector.toLowerCase().includes(pattern)) {
                throw new Error('Potentially dangerous selector detected');
            }
        }
        
        // Escape special characters
        return CSS.escape(selector);
    }
    
    validateURL(url) {
        // Ensure URL is safe to load
        const parsed = new URL(url);
        
        if (!['http:', 'https:'].includes(parsed.protocol)) {
            throw new Error('Only HTTP(S) URLs are allowed');
        }
        
        // Check against blacklist
        if (this.isBlacklisted(parsed.hostname)) {
            throw new Error('Domain is blacklisted');
        }
        
        return true;
    }
}
```

### Content Security Policy

```python
def configure_csp_headers() -> Dict[str, str]:
    """Configure Content Security Policy for interactive mode."""
    return {
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Required for Eel
            "style-src 'self' 'unsafe-inline'; "
            "img-src * data:; "
            "connect-src *; "  # Allow API calls
            "frame-src *; "  # Allow iframe embedding
        )
    }
```

## Future Enhancements

### Planned Features

1. **Browser Extension**: Native extension for enhanced cross-origin support
2. **AI Model Integration**: Deep learning for improved pattern recognition
3. **Collaborative Learning**: Share learned patterns across users
4. **Visual Regression Testing**: Detect when templates break
5. **Mobile Support**: Responsive scraping for mobile sites
6. **API Mocking**: Test templates without hitting live sites

### Architecture Extensions

```python
# Planned: Plugin architecture for custom recognizers
class RecognizerPlugin(ABC):
    @abstractmethod
    def recognize(self, soup: BeautifulSoup) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_patterns(self) -> List[Pattern]:
        pass

# Planned: Real-time collaboration
class CollaborativeSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.participants = []
        self.selections = {}
        
    async def broadcast_selection(self, selection: Dict[str, Any]):
        """Share selection with all participants."""
        pass
```

## Summary

The interactive selection architecture represents a paradigm shift in web scraping, moving from code-centric to visual-centric template creation. Through careful integration of frontend visualization, intelligent pattern recognition, and machine learning, the system makes web scraping accessible to non-programmers while providing power users with advanced capabilities.

The architecture's key strengths:

1. **Modularity**: Clear separation between visual layer, logic layer, and data layer
2. **Extensibility**: Plugin architecture for custom recognizers and validators  
3. **Learning**: Continuous improvement through user corrections
4. **Robustness**: Multiple fallback strategies and self-healing selectors
5. **Performance**: Optimized DOM operations and intelligent caching
6. **Security**: Comprehensive XSS prevention and content validation

This foundation enables ScraperV4 to adapt to the ever-changing landscape of web technologies while maintaining ease of use and reliability.