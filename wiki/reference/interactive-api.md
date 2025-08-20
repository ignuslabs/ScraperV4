# Interactive Selection API Reference

Complete API documentation for ScraperV4's interactive element selection system, covering JavaScript components, Python services, configuration options, and event handlers.

## JavaScript Components API

### InteractiveOverlay Class

The main visual overlay component for element selection.

#### Constructor

```javascript
new InteractiveOverlay(options)
```

**Parameters:**
- `options` (Object): Configuration options
  - `targetDocument` (Document): Document to attach overlay to
  - `mode` (String): 'iframe' | 'window' | 'extension'
  - `theme` (String): 'light' | 'dark' | 'auto'
  - `zIndex` (Number): Base z-index for overlay (default: 2147483640)
  - `callbacks` (Object): Event callback functions

**Example:**
```javascript
const overlay = new InteractiveOverlay({
    targetDocument: document,
    mode: 'iframe',
    theme: 'auto',
    callbacks: {
        onElementSelected: (element, selector) => console.log(selector),
        onContainerFound: (container) => console.log('Container:', container),
        onSelectionComplete: (template) => console.log('Template:', template)
    }
});
```

#### Methods

##### `initialize()`
Initialize the overlay and attach event listeners.

```javascript
await overlay.initialize();
```

**Returns:** Promise<void>

##### `startSelection(type)`
Start element selection mode.

```javascript
overlay.startSelection('field');  // or 'container'
```

**Parameters:**
- `type` (String): 'field' | 'container' | 'pagination'

##### `addField(name, element, selector)`
Add a field to the current selection.

```javascript
overlay.addField('product_title', element, 'h2.title');
```

**Parameters:**
- `name` (String): Field name
- `element` (Element): DOM element
- `selector` (String): CSS selector

**Returns:** Object - Field configuration

##### `addContainer(name, element, selector)`
Add a container for repeating elements.

```javascript
overlay.addContainer('products', element, '.product-list .item');
```

**Parameters:**
- `name` (String): Container name
- `element` (Element): Container DOM element  
- `selector` (String): Container CSS selector

**Returns:** Object - Container configuration

##### `findSimilarElements(element)`
Find elements similar to the selected one.

```javascript
const similar = overlay.findSimilarElements(productElement);
```

**Parameters:**
- `element` (Element): Reference element

**Returns:** Array<Element> - Similar elements

##### `generateSelector(element, options)`
Generate optimized selector for element.

```javascript
const selector = overlay.generateSelector(element, {
    preferIds: true,
    maxDepth: 4,
    avoidNthChild: true
});
```

**Parameters:**
- `element` (Element): Target element
- `options` (Object): Generation options
  - `preferIds` (Boolean): Prefer ID selectors
  - `preferDataAttributes` (Boolean): Prefer data attributes
  - `maxDepth` (Number): Maximum selector depth
  - `avoidNthChild` (Boolean): Avoid positional selectors
  - `includeText` (Boolean): Include text content

**Returns:** String - Generated CSS selector

##### `testSelector(selector)`
Test selector against current page.

```javascript
const result = overlay.testSelector('.product-title');
```

**Parameters:**
- `selector` (String): CSS selector to test

**Returns:** Object
- `valid` (Boolean): Selector is valid
- `count` (Number): Number of matches
- `elements` (Array<Element>): Matched elements
- `quality` (Number): Selector quality score (0-100)

##### `exportTemplate()`
Export current selections as template.

```javascript
const template = overlay.exportTemplate();
```

**Returns:** Object - Template configuration

##### `destroy()`
Clean up overlay and remove event listeners.

```javascript
overlay.destroy();
```

### AutoDetector Class

AI-powered pattern recognition for automatic field detection.

#### Constructor

```javascript
new AutoDetector(options)
```

**Parameters:**
- `options` (Object): Configuration options
  - `confidence` (Number): Minimum confidence threshold (0-1)
  - `maxSuggestions` (Number): Maximum suggestions to return
  - `learningEnabled` (Boolean): Enable learning from corrections

#### Methods

##### `detectSiteType(document)`
Classify the type of website.

```javascript
const siteType = detector.detectSiteType(document);
```

**Parameters:**
- `document` (Document): Document to analyze

**Returns:** Object
- `type` (String): 'ecommerce' | 'news' | 'directory' | 'realestate' | 'unknown'
- `confidence` (Number): Confidence score (0-1)
- `indicators` (Array): Detected indicators

##### `detectContainers(document)`
Find repeating container elements.

```javascript
const containers = detector.detectContainers(document);
```

**Parameters:**
- `document` (Document): Document to analyze

**Returns:** Array<Object>
- `element` (Element): Container element
- `selector` (String): Container selector
- `items` (Number): Number of items
- `uniformity` (Number): Structural uniformity score
- `confidence` (Number): Detection confidence

##### `detectFields(container, siteType)`
Detect fields within a container.

```javascript
const fields = detector.detectFields(containerElement, 'ecommerce');
```

**Parameters:**
- `container` (Element): Container element
- `siteType` (String): Site type for context

**Returns:** Object - Field name to selector mapping

##### `detectPagination(document)`
Find pagination elements.

```javascript
const pagination = detector.detectPagination(document);
```

**Parameters:**
- `document` (Document): Document to analyze

**Returns:** Object
- `type` (String): 'numbered' | 'next_prev' | 'load_more' | 'infinite'
- `nextSelector` (String): Next page selector
- `prevSelector` (String): Previous page selector
- `pageNumbers` (String): Page number selector

##### `applyLearning(corrections)`
Apply learning from user corrections.

```javascript
detector.applyLearning({
    domain: 'example.com',
    corrections: [
        {
            wrong: '.subtitle',
            correct: '.title',
            type: 'product_name'
        }
    ]
});
```

**Parameters:**
- `corrections` (Object): Correction data

### SelectorGenerator Class

Advanced selector generation with multiple strategies.

#### Methods

##### `generate(element, strategy)`
Generate selector using specific strategy.

```javascript
const generator = new SelectorGenerator();
const selector = generator.generate(element, 'optimal');
```

**Parameters:**
- `element` (Element): Target element
- `strategy` (String): 'optimal' | 'robust' | 'readable' | 'minimal'

**Returns:** String - Generated selector

##### `generateWithFallbacks(element, count)`
Generate primary selector with fallbacks.

```javascript
const selectors = generator.generateWithFallbacks(element, 3);
```

**Parameters:**
- `element` (Element): Target element
- `count` (Number): Number of fallbacks

**Returns:** Array<String> - Primary and fallback selectors

## Python API

### InteractiveService

Main service for interactive template creation.

#### Methods

##### `analyze_page_structure(url: str) -> Dict[str, Any]`
Analyze page structure for interactive selection.

```python
from src.services.interactive_service import InteractiveService

service = InteractiveService()
analysis = service.analyze_page_structure("https://example.com")
```

**Parameters:**
- `url` (str): URL to analyze

**Returns:** Dict containing:
- `site_type`: Detected site type
- `containers`: Found container elements
- `suggested_fields`: Detected fields
- `pagination`: Pagination elements
- `statistics`: Page statistics

##### `suggest_selectors(html: str, element_info: Dict) -> List[str]`
Generate selector suggestions for an element.

```python
suggestions = service.suggest_selectors(
    html="<div class='product'>...</div>",
    element_info={
        'tag': 'div',
        'classes': ['product', 'item'],
        'id': None,
        'text': 'Product Name'
    }
)
```

**Parameters:**
- `html` (str): HTML content
- `element_info` (Dict): Element information

**Returns:** List[str] - Suggested selectors

##### `validate_selector(selector: str, html: str) -> Dict[str, Any]`
Validate selector against HTML.

```python
result = service.validate_selector(
    selector=".product-title",
    html=page_html
)
```

**Parameters:**
- `selector` (str): CSS selector
- `html` (str): HTML content

**Returns:** Dict containing:
- `valid`: Whether selector is valid
- `count`: Number of matches
- `samples`: Sample extracted data
- `quality`: Selector quality score

##### `generate_template_from_selection(selections: Dict) -> Dict[str, Any]`
Generate template from user selections.

```python
template = service.generate_template_from_selection({
    'name': 'Product Scraper',
    'url': 'https://shop.example.com',
    'fields': {
        'title': {
            'selector': 'h2.product-name',
            'type': 'text'
        },
        'price': {
            'selector': '.price',
            'type': 'price',
            'fallbacks': ['.cost', '[data-price]']
        }
    },
    'containers': {
        'products': {
            'selector': '.product-grid .item',
            'fields': {...}
        }
    }
})
```

**Parameters:**
- `selections` (Dict): User selections

**Returns:** Dict - Generated template

##### `apply_learning_corrections(corrections: Dict) -> bool`
Apply learning from user corrections.

```python
success = service.apply_learning_corrections({
    'domain': 'example.com',
    'url': 'https://example.com/products',
    'corrections': [
        {
            'field': 'title',
            'wrong_selector': '.subtitle',
            'correct_selector': '.main-title',
            'element_type': 'product_name'
        }
    ]
})
```

**Parameters:**
- `corrections` (Dict): Correction data

**Returns:** bool - Success status

### Eel API Endpoints

Exposed Python functions callable from JavaScript.

#### `start_interactive_mode(url: str) -> Dict[str, Any]`

Initialize interactive mode for URL.

```javascript
const result = await eel.start_interactive_mode('https://example.com')();
```

**Returns:**
- `success`: Operation success
- `analysis`: Page analysis results
- `error`: Error message if failed

#### `analyze_element(element_data: Dict) -> Dict[str, Any]`

Analyze selected element.

```javascript
const analysis = await eel.analyze_element({
    tag: 'div',
    classes: ['product'],
    id: 'product-123',
    attributes: {
        'data-price': '29.99'
    },
    text: 'Product Name',
    html: '<div>...</div>'
})();
```

**Returns:**
- `success`: Operation success
- `suggestions`: Selector suggestions
- `element_type`: Detected element type

#### `save_interactive_template(template_data: Dict) -> Dict[str, Any]`

Save template from interactive selection.

```javascript
const result = await eel.save_interactive_template({
    name: 'My Template',
    description: 'Product scraper',
    url: 'https://example.com',
    fields: {...},
    containers: {...}
})();
```

**Returns:**
- `success`: Operation success
- `template_name`: Saved template name
- `validation`: Validation results

#### `test_selector_live(selector: str, url: str) -> Dict[str, Any]`

Test selector on live URL.

```javascript
const result = await eel.test_selector_live(
    '.product-title',
    'https://example.com'
)();
```

**Returns:**
- `success`: Operation success
- `valid`: Selector validity
- `count`: Match count
- `samples`: Sample data
- `quality`: Quality score

#### `apply_learning_correction(correction_data: Dict) -> Dict[str, Any]`

Apply learning correction.

```javascript
const result = await eel.apply_learning_correction({
    domain: 'example.com',
    field: 'price',
    wrong_selector: '.old-price',
    correct_selector: '.current-price',
    context: {
        page_type: 'product_detail'
    }
})();
```

**Returns:**
- `success`: Operation success
- `message`: Status message

## Configuration Options

### Global Configuration

```javascript
// JavaScript configuration
window.InteractiveConfig = {
    // Visual settings
    ui: {
        theme: 'auto',  // 'light', 'dark', 'auto'
        position: 'top',  // Toolbar position
        animations: true,
        showTooltips: true,
        compactMode: false
    },
    
    // Selection behavior
    selection: {
        highlightColor: '#00CED1',  // Teal
        selectedColor: '#32CD32',   // Green
        containerColor: '#FFD700',  // Gold
        errorColor: '#DC143C',      // Crimson
        
        hoverDelay: 100,  // ms before highlighting
        clickDelay: 0,    // ms before selection
        
        autoDetect: true,  // Enable auto-detection
        autoSuggest: true, // Show suggestions
        
        multiSelect: true,  // Allow multiple selections
        smartGrouping: true // Group similar elements
    },
    
    // Selector generation
    selectors: {
        preferIds: true,
        preferDataAttributes: true,
        preferClasses: true,
        
        avoidNthChild: true,
        avoidComplexSelectors: true,
        
        maxDepth: 5,
        maxLength: 100,
        
        fallbackCount: 3,
        testOnGeneration: true
    },
    
    // Performance
    performance: {
        batchOperations: true,
        cacheSelectors: true,
        throttleHighlight: true,
        
        maxElements: 10000,  // Max elements to process
        maxDepth: 20,        // Max DOM depth
        
        debounceMs: 300,     // Debounce user input
        throttleMs: 100      // Throttle DOM operations
    },
    
    // Learning system
    learning: {
        enabled: true,
        autoSave: true,
        
        minConfidence: 0.7,
        maxCorrections: 100,
        
        shareLearning: false,  // Share with community
        importLearning: true   // Import community patterns
    }
};
```

```python
# Python configuration
INTERACTIVE_CONFIG = {
    # Service settings
    'service': {
        'cache_enabled': True,
        'cache_ttl': 3600,
        'max_page_size': 10 * 1024 * 1024,  # 10MB
        'timeout': 30,
        'retry_count': 3
    },
    
    # Pattern recognition
    'recognition': {
        'min_confidence': 0.6,
        'max_suggestions': 10,
        'enable_ml': True,
        'model_path': 'models/pattern_recognition.pkl'
    },
    
    # Learning system
    'learning': {
        'enabled': True,
        'database_path': 'data/learning.db',
        'max_corrections_per_domain': 1000,
        'weight_decay': 0.95,
        'min_samples_for_pattern': 3
    },
    
    # Validation
    'validation': {
        'strict_mode': False,
        'test_all_fallbacks': True,
        'quality_threshold': 70,
        'sample_size': 5
    }
}
```

## Event System

### JavaScript Events

```javascript
// Listen for selection events
overlay.on('elementSelected', (event) => {
    console.log('Element selected:', event.detail);
});

overlay.on('containerFound', (event) => {
    console.log('Container found:', event.detail);
});

overlay.on('selectionComplete', (event) => {
    console.log('Selection complete:', event.detail);
});

overlay.on('error', (event) => {
    console.error('Error:', event.detail);
});

// Custom event example
overlay.on('selectorGenerated', (event) => {
    const { element, selector, quality } = event.detail;
    if (quality < 70) {
        console.warn('Low quality selector:', selector);
    }
});
```

### Event Types

#### `elementSelected`
Fired when an element is selected.

**Event Data:**
- `element`: Selected DOM element
- `selector`: Generated selector
- `type`: 'field' | 'container'
- `name`: Field/container name

#### `containerFound`
Fired when a container is identified.

**Event Data:**
- `element`: Container element
- `selector`: Container selector
- `items`: Number of items
- `uniformity`: Uniformity score

#### `selectionComplete`
Fired when selection is finished.

**Event Data:**
- `template`: Generated template
- `fields`: Selected fields
- `containers`: Selected containers

#### `autoDetectComplete`
Fired when auto-detection finishes.

**Event Data:**
- `siteType`: Detected site type
- `confidence`: Confidence score
- `suggestions`: Field suggestions

#### `learningApplied`
Fired when learning is applied.

**Event Data:**
- `corrections`: Applied corrections
- `domain`: Target domain
- `success`: Success status

## Error Handling

### JavaScript Error Handling

```javascript
try {
    const overlay = new InteractiveOverlay(options);
    await overlay.initialize();
} catch (error) {
    if (error.code === 'IFRAME_BLOCKED') {
        // Try alternative mode
        overlay.switchMode('window');
    } else if (error.code === 'SELECTOR_INVALID') {
        // Handle invalid selector
        console.error('Invalid selector:', error.selector);
    }
}

// Global error handler
window.addEventListener('interactiveError', (event) => {
    const { code, message, details } = event.detail;
    
    switch (code) {
        case 'ELEMENT_NOT_FOUND':
            // Handle missing element
            break;
        case 'TIMEOUT':
            // Handle timeout
            break;
        case 'NETWORK_ERROR':
            // Handle network issues
            break;
    }
});
```

### Python Error Handling

```python
from src.services.interactive_service import (
    InteractiveService,
    InteractiveError,
    SelectorError,
    ValidationError
)

try:
    service = InteractiveService()
    result = service.validate_selector(selector, html)
except SelectorError as e:
    # Handle selector-specific errors
    print(f"Selector error: {e.selector} - {e.message}")
except ValidationError as e:
    # Handle validation errors
    print(f"Validation failed: {e.errors}")
except InteractiveError as e:
    # Handle general interactive errors
    print(f"Interactive error: {e.code} - {e.message}")
```

### Error Codes

| Code | Description | Recovery Action |
|------|-------------|----------------|
| `IFRAME_BLOCKED` | Cannot embed site in iframe | Use window mode |
| `SELECTOR_INVALID` | Invalid CSS selector | Regenerate selector |
| `ELEMENT_NOT_FOUND` | Element doesn't exist | Check page loaded |
| `TIMEOUT` | Operation timed out | Retry with longer timeout |
| `NETWORK_ERROR` | Network request failed | Check connectivity |
| `PERMISSION_DENIED` | No permission to access | Check CORS/CSP |
| `LEARNING_FAILED` | Learning update failed | Retry or disable |
| `TEMPLATE_INVALID` | Invalid template generated | Review selections |

## TypeScript Definitions

```typescript
// types/interactive.d.ts

interface InteractiveOverlayOptions {
    targetDocument: Document;
    mode: 'iframe' | 'window' | 'extension';
    theme?: 'light' | 'dark' | 'auto';
    zIndex?: number;
    callbacks?: OverlayCallbacks;
}

interface OverlayCallbacks {
    onElementSelected?: (element: Element, selector: string) => void;
    onContainerFound?: (container: ContainerInfo) => void;
    onSelectionComplete?: (template: Template) => void;
    onError?: (error: InteractiveError) => void;
}

interface ContainerInfo {
    element: Element;
    selector: string;
    items: number;
    uniformity: number;
    fields?: FieldMap;
}

interface FieldMap {
    [fieldName: string]: {
        selector: string;
        type?: string;
        fallbacks?: string[];
    };
}

interface Template {
    name: string;
    description?: string;
    url?: string;
    selectors: FieldMap;
    containers?: {
        [containerName: string]: ContainerInfo;
    };
    pagination?: PaginationInfo;
}

interface PaginationInfo {
    type: 'numbered' | 'next_prev' | 'load_more' | 'infinite';
    nextSelector?: string;
    prevSelector?: string;
    pageNumbers?: string;
}

interface InteractiveError extends Error {
    code: string;
    details?: any;
}

declare class InteractiveOverlay {
    constructor(options: InteractiveOverlayOptions);
    initialize(): Promise<void>;
    startSelection(type: 'field' | 'container'): void;
    addField(name: string, element: Element, selector: string): FieldInfo;
    addContainer(name: string, element: Element, selector: string): ContainerInfo;
    findSimilarElements(element: Element): Element[];
    generateSelector(element: Element, options?: SelectorOptions): string;
    testSelector(selector: string): SelectorTestResult;
    exportTemplate(): Template;
    destroy(): void;
    on(event: string, handler: EventHandler): void;
    off(event: string, handler: EventHandler): void;
}

declare class AutoDetector {
    constructor(options?: DetectorOptions);
    detectSiteType(document: Document): SiteTypeResult;
    detectContainers(document: Document): ContainerInfo[];
    detectFields(container: Element, siteType: string): FieldMap;
    detectPagination(document: Document): PaginationInfo;
    applyLearning(corrections: Corrections): void;
}
```

## Usage Examples

### Complete Interactive Session

```javascript
// Initialize interactive mode
async function startInteractiveSession(url) {
    // Start backend analysis
    const analysis = await eel.start_interactive_mode(url)();
    
    // Create overlay
    const overlay = new InteractiveOverlay({
        targetDocument: document,
        mode: 'iframe',
        callbacks: {
            onElementSelected: handleElementSelection,
            onContainerFound: handleContainerFound,
            onSelectionComplete: handleComplete
        }
    });
    
    // Initialize overlay
    await overlay.initialize();
    
    // Auto-detect if confident
    if (analysis.site_type.confidence > 0.8) {
        const detector = new AutoDetector();
        const containers = detector.detectContainers(document);
        
        if (containers.length > 0) {
            // Use first container
            overlay.addContainer('items', containers[0].element, containers[0].selector);
            
            // Detect fields
            const fields = detector.detectFields(containers[0].element, analysis.site_type.type);
            
            for (const [name, selector] of Object.entries(fields)) {
                overlay.addField(name, document.querySelector(selector), selector);
            }
        }
    }
    
    // Start manual selection
    overlay.startSelection('field');
}

// Handle selections
function handleElementSelection(element, selector) {
    // Validate selector
    eel.test_selector_live(selector, window.location.href)()
        .then(result => {
            if (result.quality < 70) {
                console.warn('Low quality selector, generating alternatives...');
                // Generate better selector
            }
        });
}

// Save template
async function saveTemplate(overlay) {
    const template = overlay.exportTemplate();
    
    const result = await eel.save_interactive_template(template)();
    
    if (result.success) {
        console.log('Template saved:', result.template_name);
    } else {
        console.error('Failed to save:', result.error);
    }
}
```

### Python Usage

```python
from src.services.interactive_service import InteractiveService
from src.core.container import container

# Register service
container.register_singleton(InteractiveService, InteractiveService)

# Use in route
@eel.expose
def create_visual_template(url: str) -> Dict[str, Any]:
    """Create template using visual selection."""
    
    service = container.get(InteractiveService)
    
    # Analyze page
    analysis = service.analyze_page_structure(url)
    
    # Return analysis for frontend
    return {
        'success': True,
        'analysis': analysis,
        'suggestions': service.get_field_suggestions(analysis['site_type'])
    }

# Apply learning
@eel.expose  
def correct_selection(correction: Dict[str, Any]) -> Dict[str, Any]:
    """Apply correction to improve detection."""
    
    service = container.get(InteractiveService)
    
    success = service.apply_learning_corrections(correction)
    
    if success:
        # Get improved suggestions
        new_suggestions = service.suggest_selectors(
            correction['html'],
            correction['element_info']
        )
        
        return {
            'success': True,
            'improved_suggestions': new_suggestions
        }
    
    return {'success': False, 'error': 'Failed to apply learning'}
```

## Performance Guidelines

1. **Batch DOM Operations**: Group multiple DOM queries
2. **Cache Selectors**: Reuse validated selectors
3. **Throttle Events**: Limit event frequency
4. **Lazy Load**: Load components on demand
5. **Optimize Selectors**: Prefer IDs and classes
6. **Limit Depth**: Restrict selector depth
7. **Use Web Workers**: Offload heavy computations

## Security Best Practices

1. **Sanitize Selectors**: Prevent XSS through selectors
2. **Validate URLs**: Check URL safety before loading
3. **CSP Headers**: Configure Content Security Policy
4. **CORS Handling**: Properly handle cross-origin requests
5. **Input Validation**: Validate all user inputs
6. **Rate Limiting**: Limit API call frequency
7. **Authentication**: Secure sensitive endpoints

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Basic Selection | ✅ 80+ | ✅ 75+ | ✅ 14+ | ✅ 88+ |
| Shadow DOM | ✅ 53+ | ✅ 63+ | ✅ 10+ | ✅ 79+ |
| Mutation Observer | ✅ 18+ | ✅ 14+ | ✅ 6+ | ✅ 12+ |
| CSS.escape | ✅ 46+ | ✅ 32+ | ✅ 10.1+ | ✅ 79+ |
| Custom Events | ✅ All | ✅ All | ✅ All | ✅ All |

## Migration Guide

### From Manual Templates

```python
# Old: Manual template creation
template = {
    "selectors": {
        "title": "h1.product-title",
        "price": ".price-now"
    }
}

# New: Interactive creation
from src.services.interactive_service import InteractiveService

service = InteractiveService()
analysis = service.analyze_page_structure(url)
# Use frontend to visually select elements
# Template generated automatically
```

### From V3 System

```javascript
// V3: Old interactive system
oldInteractive.selectElement(element);
oldInteractive.generateTemplate();

// V4: New integrated system  
const overlay = new InteractiveOverlay(options);
overlay.addField('title', element, selector);
const template = overlay.exportTemplate();
await eel.save_interactive_template(template)();
```

---

For more information, see:
- [Interactive Selection Tutorial](/docs/tutorials/interactive-selection.md)
- [Visual Template Creation Guide](/docs/how-to/visual-template-creation.md)
- [Architecture Documentation](/docs/explanations/interactive-architecture.md)