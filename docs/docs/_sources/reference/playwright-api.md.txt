# Playwright Interactive Mode API Reference

Complete API documentation for ScraperV4's Playwright Interactive Mode, covering all endpoints, parameters, response formats, and integration patterns.

## Overview

The Playwright Interactive API provides programmatic access to browser-controlled template creation and element selection. Unlike traditional iframe-based approaches, this API uses real browser instances to bypass CORS restrictions and handle dynamic content.

**Base URL**: `http://localhost:8080/api/`  
**Protocol**: HTTP/WebSocket hybrid via Eel framework  
**Authentication**: Session-based (future: API key support)

## Core Concepts

### Session Management
Each interactive session represents a persistent browser instance with:
- Unique session ID for tracking
- Browser state and navigation history  
- Injected overlay for element selection
- Screenshot streaming capabilities

### Coordinate System
All coordinates are relative to the browser viewport:
- Origin (0,0) at top-left corner
- X-axis increases rightward
- Y-axis increases downward
- Coordinates scaled to match frontend display

## API Endpoints

### Session Management

#### `start_playwright_interactive(url, options)`

Initialize a new Playwright interactive session.

**Parameters:**
```typescript
interface StartSessionParams {
  url: string;                    // Target URL to load
  options?: {
    headless?: boolean;           // Run in headless mode (default: false)
    viewport?: {                  // Browser viewport size
      width: number;              // Viewport width (default: 1280)
      height: number;             // Viewport height (default: 720)
    };
    wait_until?: string;          // Page load strategy (default: "networkidle")
    timeout?: number;             // Navigation timeout in ms (default: 30000)
    stealth_mode?: boolean;       // Enable anti-detection (default: true)
    user_agent?: string;          // Custom user agent
    extra_headers?: object;       // Additional HTTP headers
  };
}
```

**Response:**
```typescript
interface StartSessionResponse {
  success: boolean;
  session_id?: string;            // Unique session identifier
  url?: string;                   // Loaded URL (may differ due to redirects)
  screenshot?: string;            // Base64 encoded initial screenshot
  viewport?: {                    // Actual viewport dimensions
    width: number;
    height: number;
  };
  page_info?: {                   // Page metadata
    title: string;
    domain: string;
    elements_count: number;
  };
  message?: string;               // Success message
  error?: string;                 // Error description if failed
}
```

**Example:**
```javascript
const result = await eel.start_playwright_interactive(
  'https://shop.example.com/products',
  {
    headless: false,
    viewport: { width: 1280, height: 720 },
    wait_until: 'networkidle',
    stealth_mode: true
  }
)();

if (result.success) {
  console.log('Session started:', result.session_id);
  displayScreenshot(result.screenshot);
}
```

#### `close_playwright_session(session_id)`

Close an active Playwright session and cleanup resources.

**Parameters:**
```typescript
interface CloseSessionParams {
  session_id: string;             // Session ID to close
}
```

**Response:**
```typescript
interface CloseSessionResponse {
  success: boolean;
  message?: string;               // Status message
  error?: string;                 // Error if failed
}
```

**Example:**
```javascript
const result = await eel.close_playwright_session('session_123')();
```

#### `get_active_sessions()`

List all active Playwright sessions.

**Response:**
```typescript
interface ActiveSessionsResponse {
  success: boolean;
  sessions: Array<{
    session_id: string;
    url: string;
    created_at: number;           // Unix timestamp
    last_activity: number;        // Unix timestamp
  }>;
}
```

### Screen Capture

#### `get_browser_screenshot(session_id, full_page)`

Capture current browser screenshot.

**Parameters:**
```typescript
interface ScreenshotParams {
  session_id: string;             // Target session
  full_page?: boolean;            // Capture full page vs viewport (default: false)
}
```

**Response:**
```typescript
interface ScreenshotResponse {
  success: boolean;
  screenshot?: string;            // Base64 encoded PNG image
  timestamp?: number;             // Capture timestamp
  viewport?: {                    // Screenshot dimensions
    width: number;
    height: number;
  };
  error?: string;
}
```

**Example:**
```javascript
const screenshot = await eel.get_browser_screenshot('session_123', false)();
if (screenshot.success) {
  updateDisplay(screenshot.screenshot);
}
```

### Element Selection

#### `start_element_selection(session_id)`

Enable element selection mode in the browser.

**Parameters:**
```typescript
interface StartSelectionParams {
  session_id: string;
}
```

**Response:**
```typescript
interface StartSelectionResponse {
  success: boolean;
  message?: string;
  error?: string;
}
```

**Example:**
```javascript
await eel.start_element_selection('session_123')();
// User can now click elements in the browser
```

#### `stop_element_selection(session_id)`

Disable element selection mode.

**Parameters:**
```typescript
interface StopSelectionParams {
  session_id: string;
}
```

**Response:**
```typescript
interface StopSelectionResponse {
  success: boolean;
  message?: string;
  error?: string;
}
```

#### `select_element_at_coordinates(session_id, x, y)`

Select element at specific screen coordinates.

**Parameters:**
```typescript
interface SelectElementParams {
  session_id: string;
  x: number;                      // X coordinate in viewport
  y: number;                      // Y coordinate in viewport
}
```

**Response:**
```typescript
interface SelectElementResponse {
  success: boolean;
  element?: {
    tag: string;                  // HTML tag name
    id?: string;                  // Element ID
    classes: string[];            // CSS class list
    text: string;                 // Text content (trimmed)
    attributes: object;           // All element attributes
    css_selector: string;         // Generated CSS selector
    xpath_selector: string;       // Generated XPath selector
    position: {                   // Element position
      x: number;
      y: number;
      width: number;
      height: number;
    };
  };
  selector_quality?: number;      // Quality score 0-100
  alternatives?: string[];        // Alternative selectors
  error?: string;
}
```

**Example:**
```javascript
const element = await eel.select_element_at_coordinates('session_123', 400, 300)();
if (element.success) {
  addFieldToTemplate(element.element);
}
```

### Navigation and Interaction

#### `navigate_to_url(session_id, url)`

Navigate to a new URL within the session.

**Parameters:**
```typescript
interface NavigateParams {
  session_id: string;
  url: string;                    // Target URL
  wait_until?: string;            // Wait strategy (default: "networkidle")
  timeout?: number;               // Timeout in ms (default: 30000)
}
```

**Response:**
```typescript
interface NavigateResponse {
  success: boolean;
  url?: string;                   // Final URL after redirects
  title?: string;                 // Page title
  error?: string;
}
```

#### `click_element(session_id, selector)`

Click an element using CSS selector.

**Parameters:**
```typescript
interface ClickElementParams {
  session_id: string;
  selector: string;               // CSS selector for element
  wait_for_navigation?: boolean;  // Wait for page navigation (default: false)
  timeout?: number;               // Click timeout (default: 5000)
}
```

**Response:**
```typescript
interface ClickElementResponse {
  success: boolean;
  message?: string;
  navigation_occurred?: boolean;
  error?: string;
}
```

#### `fill_form_field(session_id, selector, value)`

Fill a form field with text.

**Parameters:**
```typescript
interface FillFieldParams {
  session_id: string;
  selector: string;               // CSS selector for input
  value: string;                  // Text to enter
  clear_first?: boolean;          // Clear existing text (default: true)
}
```

**Response:**
```typescript
interface FillFieldResponse {
  success: boolean;
  message?: string;
  error?: string;
}
```

#### `wait_for_element(session_id, selector, timeout)`

Wait for element to appear in DOM.

**Parameters:**
```typescript
interface WaitElementParams {
  session_id: string;
  selector: string;               // CSS selector to wait for
  timeout?: number;               // Wait timeout (default: 10000)
  state?: string;                 // Element state: "visible" | "hidden" | "attached"
}
```

**Response:**
```typescript
interface WaitElementResponse {
  success: boolean;
  found: boolean;                 // Whether element was found
  timeout_occurred: boolean;
  error?: string;
}
```

### Data Extraction

#### `extract_data_with_selector(session_id, selector, attribute)`

Extract data using CSS selector.

**Parameters:**
```typescript
interface ExtractDataParams {
  session_id: string;
  selector: string;               // CSS selector
  attribute?: string;             // Attribute to extract (default: text content)
  multiple?: boolean;             // Extract from multiple elements (default: false)
}
```

**Response:**
```typescript
interface ExtractDataResponse {
  success: boolean;
  data?: string | string[];       // Extracted data
  count?: number;                 // Number of elements matched
  error?: string;
}
```

**Example:**
```javascript
// Extract product titles
const titles = await eel.extract_data_with_selector(
  'session_123',
  '.product-title',
  'textContent',
  true
)();
```

#### `test_selector_live(session_id, selector)`

Test selector against current page.

**Parameters:**
```typescript
interface TestSelectorParams {
  session_id: string;
  selector: string;               // CSS selector to test
}
```

**Response:**
```typescript
interface TestSelectorResponse {
  success: boolean;
  valid: boolean;                 // Selector is valid CSS
  count: number;                  // Number of matches
  samples?: string[];             // Sample extracted data
  quality_score: number;          // Selector quality 0-100
  suggestions?: string[];         // Alternative selectors
  error?: string;
}
```

### Template Management

#### `save_playwright_template(template_data)`

Save template created through Playwright interaction.

**Parameters:**
```typescript
interface SaveTemplateParams {
  name: string;                   // Template name
  description?: string;           // Template description
  url_pattern: string;            // URL pattern for auto-matching
  fields: {                       // Field definitions
    [field_name: string]: {
      selector: string;           // Primary CSS selector
      type?: string;              // Field type (text, price, image, etc.)
      attribute?: string;         // HTML attribute to extract
      fallback_selectors?: string[]; // Alternative selectors
      required?: boolean;         // Field is required
      validation?: object;        // Validation rules
    };
  };
  containers?: {                  // Container definitions
    [container_name: string]: {
      selector: string;           // Container CSS selector
      fields: object;             // Fields within container
    };
  };
  pagination?: {                  // Pagination configuration
    type: string;                 // Pagination type
    next_selector?: string;       // Next page selector
    max_pages?: number;           // Maximum pages to scrape
  };
  pre_actions?: Array<{           // Actions before scraping
    type: string;                 // Action type
    selector?: string;            // Target selector
    value?: string;               // Input value
    wait?: number;                // Wait duration
  }>;
  settings?: {                    // Advanced settings
    wait_strategy?: string;       // Page load wait strategy
    timeout?: number;             // Default timeout
    stealth_mode?: boolean;       // Anti-detection mode
    proxy_rotation?: boolean;     // Use proxy rotation
  };
}
```

**Response:**
```typescript
interface SaveTemplateResponse {
  success: boolean;
  template_id?: string;           // Saved template ID
  template_name?: string;         // Confirmed template name
  validation_results?: {          // Template validation
    valid: boolean;
    errors?: string[];
    warnings?: string[];
    quality_score?: number;
  };
  error?: string;
}
```

**Example:**
```javascript
const template = {
  name: "Product Scraper",
  description: "Extract product information",
  url_pattern: "shop.example.com/products*",
  fields: {
    title: {
      selector: ".product-title",
      type: "text",
      required: true
    },
    price: {
      selector: ".price",
      type: "price",
      fallback_selectors: [".cost", "[data-price]"]
    }
  }
};

const result = await eel.save_playwright_template(template)();
```

#### `load_playwright_template(template_id)`

Load existing template for editing.

**Parameters:**
```typescript
interface LoadTemplateParams {
  template_id: string;            // Template ID to load
}
```

**Response:**
```typescript
interface LoadTemplateResponse {
  success: boolean;
  template?: object;              // Full template configuration
  error?: string;
}
```

### Page Analysis

#### `analyze_page_structure(session_id)`

Analyze page structure for automatic pattern detection.

**Parameters:**
```typescript
interface AnalyzePageParams {
  session_id: string;
}
```

**Response:**
```typescript
interface AnalyzePageResponse {
  success: boolean;
  analysis?: {
    page_type: string;            // Detected page type (ecommerce, news, etc.)
    confidence: number;           // Detection confidence 0-1
    containers: Array<{           // Detected container elements
      selector: string;
      element_count: number;
      uniformity_score: number;
      suggested_fields: object;
    }>;
    pagination: {                 // Detected pagination
      type?: string;
      next_selector?: string;
      page_numbers?: string;
    };
    common_elements: {            // Common page elements
      navigation?: string;
      header?: string;
      footer?: string;
      sidebar?: string;
    };
  };
  error?: string;
}
```

### Performance and Debugging

#### `get_session_metrics(session_id)`

Get performance metrics for session.

**Parameters:**
```typescript
interface GetMetricsParams {
  session_id: string;
}
```

**Response:**
```typescript
interface SessionMetricsResponse {
  success: boolean;
  metrics?: {
    session_duration: number;     // Duration in seconds
    pages_visited: number;        // Number of page navigations
    elements_selected: number;    // Elements selected count
    screenshots_taken: number;    // Screenshot count
    memory_usage: number;         // Memory usage in MB
    cpu_usage: number;            // CPU usage percentage
    network_requests: number;     // HTTP requests made
    javascript_errors: number;    // JS errors encountered
  };
  error?: string;
}
```

#### `enable_debug_mode(session_id, debug_options)`

Enable debugging features for session.

**Parameters:**
```typescript
interface DebugModeParams {
  session_id: string;
  debug_options: {
    console_logging?: boolean;    // Log browser console
    network_logging?: boolean;    // Log network requests
    performance_monitoring?: boolean; // Monitor performance
    screenshot_on_error?: boolean; // Capture on errors
    element_highlighting?: boolean; // Highlight selections
  };
}
```

**Response:**
```typescript
interface DebugModeResponse {
  success: boolean;
  debug_enabled: boolean;
  active_features: string[];
  error?: string;
}
```

## WebSocket Events

Real-time events for live updates during interactive sessions.

### Connection

```javascript
// Eel automatically handles WebSocket connection
// No manual connection required
```

### Event Types

#### `element_highlighted`
Fired when user hovers over elements.

```typescript
interface ElementHighlightedEvent {
  session_id: string;
  element: {
    tag: string;
    classes: string[];
    text: string;
    selector: string;
  };
  coordinates: { x: number; y: number; };
}
```

#### `element_selected`
Fired when user selects an element.

```typescript
interface ElementSelectedEvent {
  session_id: string;
  element: object;                // Full element data
  selector: string;
  selection_type: string;         // 'field' | 'container' | 'link'
}
```

#### `page_navigation`
Fired when page navigation occurs.

```typescript
interface PageNavigationEvent {
  session_id: string;
  from_url: string;
  to_url: string;
  navigation_type: string;        // 'link' | 'redirect' | 'programmatic'
}
```

#### `session_error`
Fired when session encounters errors.

```typescript
interface SessionErrorEvent {
  session_id: string;
  error_type: string;
  error_message: string;
  recovery_possible: boolean;
  timestamp: number;
}
```

### Event Handling

```javascript
// Listen for real-time events
eel.expose(handleElementSelected);
function handleElementSelected(event) {
  console.log('Element selected:', event);
  updateTemplateField(event.element);
}

eel.expose(handlePageNavigation);
function handlePageNavigation(event) {
  console.log('Page changed:', event.to_url);
  refreshScreenshot();
}
```

## Error Handling

### Standard Error Format

```typescript
interface APIError {
  success: false;
  error: string;                  // Human-readable error message
  error_code?: string;            // Machine-readable error code
  details?: object;               // Additional error context
  recovery_suggestions?: string[]; // Suggested recovery actions
}
```

### Common Error Codes

| Code | Description | Recovery Action |
|------|-------------|----------------|
| `SESSION_NOT_FOUND` | Session ID doesn't exist | Create new session |
| `BROWSER_CRASHED` | Browser instance crashed | Restart session |
| `NAVIGATION_TIMEOUT` | Page load timed out | Retry with longer timeout |
| `ELEMENT_NOT_FOUND` | Element not found at coordinates | Try different coordinates |
| `SELECTOR_INVALID` | CSS selector syntax error | Fix selector syntax |
| `NETWORK_ERROR` | Network connectivity issue | Check connection |
| `PERMISSION_DENIED` | Missing browser permissions | Check browser settings |
| `MEMORY_LIMIT` | Browser memory limit reached | Close other sessions |

### Error Recovery Patterns

```javascript
async function robustElementSelection(sessionId, x, y, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const result = await eel.select_element_at_coordinates(sessionId, x, y)();
      if (result.success) return result;
      
      if (result.error_code === 'ELEMENT_NOT_FOUND') {
        // Try slightly different coordinates
        x += Math.random() * 10 - 5;
        y += Math.random() * 10 - 5;
        continue;
      }
      
      if (result.error_code === 'SESSION_NOT_FOUND') {
        // Recreate session
        sessionId = await recreateSession();
        continue;
      }
      
      throw new Error(result.error);
    } catch (error) {
      if (i === retries - 1) throw error;
      await sleep(1000 * (i + 1)); // Exponential backoff
    }
  }
}
```

## Rate Limiting and Quotas

### Default Limits

| Operation | Limit | Window | Notes |
|-----------|-------|--------|-------|
| `start_session` | 10 | 1 minute | Prevent resource exhaustion |
| `get_screenshot` | 60 | 1 minute | Cache reduces actual captures |
| `select_element` | 100 | 1 minute | Normal interactive usage |
| `navigate_to_url` | 30 | 1 minute | Prevent rapid navigation |
| `save_template` | 20 | 1 minute | Template creation limit |

### Rate Limit Headers

```typescript
interface RateLimitInfo {
  'X-RateLimit-Limit': number;     // Requests per window
  'X-RateLimit-Remaining': number; // Remaining requests
  'X-RateLimit-Reset': number;     // Reset timestamp
  'X-RateLimit-Window': number;    // Window duration in seconds
}
```

## Authentication and Security

### Session Security

```typescript
interface SecurityConfig {
  session_timeout: number;        // Auto-logout timeout
  max_concurrent_sessions: number; // Per-user limit
  secure_cookies: boolean;        // HTTPS-only cookies
  csrf_protection: boolean;       // CSRF token validation
}
```

### API Key Authentication (Future)

```typescript
interface APIKeyAuth {
  headers: {
    'Authorization': 'Bearer your_api_key_here';
    'X-API-Version': '1.0';
  };
}
```

## SDK Integration Examples

### Python SDK

```python
from scraperv4_sdk import PlaywrightClient

client = PlaywrightClient(base_url="http://localhost:8080")

# Start session
session = await client.start_session("https://example.com")

# Select elements
element = await session.select_element_at(400, 300)

# Build template
template = session.build_template({
    'title': element.css_selector,
    'price': '.price'
})

# Save template
await client.save_template(template)
```

### JavaScript SDK

```javascript
import { PlaywrightClient } from 'scraperv4-sdk';

const client = new PlaywrightClient('http://localhost:8080');

// Interactive session
const session = await client.startSession('https://example.com');

// Element selection with event handling
session.on('elementSelected', (element) => {
  console.log('Selected:', element.css_selector);
});

// Template building
const template = new TemplateBuilder()
  .addField('title', '.product-title')
  .addField('price', '.price')
  .setPagination('.next-page')
  .build();

await client.saveTemplate(template);
```

## Performance Guidelines

### Optimization Best Practices

1. **Screenshot Caching**: Don't request screenshots more than once per 5 seconds
2. **Session Reuse**: Reuse sessions for multiple operations on same domain
3. **Batch Operations**: Group related API calls when possible
4. **Resource Cleanup**: Always close sessions when done
5. **Error Handling**: Implement proper retry logic with exponential backoff

### Resource Management

```javascript
class SessionManager {
  constructor(maxSessions = 5) {
    this.sessions = new Map();
    this.maxSessions = maxSessions;
  }
  
  async createSession(url) {
    if (this.sessions.size >= this.maxSessions) {
      // Close oldest session
      const oldestSession = this.sessions.values().next().value;
      await this.closeSession(oldestSession.id);
    }
    
    const session = await eel.start_playwright_interactive(url)();
    this.sessions.set(session.session_id, {
      id: session.session_id,
      created: Date.now(),
      lastUsed: Date.now()
    });
    
    return session;
  }
  
  async cleanup() {
    for (const session of this.sessions.values()) {
      await eel.close_playwright_session(session.id)();
    }
    this.sessions.clear();
  }
}
```

## Testing and Validation

### Unit Testing API Calls

```javascript
describe('Playwright API', () => {
  let sessionId;
  
  beforeEach(async () => {
    const result = await eel.start_playwright_interactive('https://example.com')();
    sessionId = result.session_id;
  });
  
  afterEach(async () => {
    await eel.close_playwright_session(sessionId)();
  });
  
  test('should select element at coordinates', async () => {
    const result = await eel.select_element_at_coordinates(sessionId, 400, 300)();
    expect(result.success).toBe(true);
    expect(result.element).toBeDefined();
    expect(result.element.css_selector).toBeTruthy();
  });
});
```

### Integration Testing

```javascript
// Full workflow test
test('complete template creation workflow', async () => {
  // Start session
  const session = await eel.start_playwright_interactive('https://shop.example.com')();
  
  // Select elements
  const title = await eel.select_element_at_coordinates(session.session_id, 200, 100)();
  const price = await eel.select_element_at_coordinates(session.session_id, 200, 150)();
  
  // Build template
  const template = {
    name: 'Test Template',
    fields: {
      title: { selector: title.element.css_selector },
      price: { selector: price.element.css_selector }
    }
  };
  
  // Save template
  const saved = await eel.save_playwright_template(template)();
  expect(saved.success).toBe(true);
  
  // Cleanup
  await eel.close_playwright_session(session.session_id)();
});
```

## Migration from Legacy API

### V3 to V4 Migration

```javascript
// V3 Legacy approach
const session = await eel.start_interactive_mode(url)();
const element = await eel.select_element(selector)();

// V4 Playwright approach
const session = await eel.start_playwright_interactive(url)();
const element = await eel.select_element_at_coordinates(session.session_id, x, y)();
```

### Breaking Changes

1. **Session Management**: Explicit session IDs required
2. **Element Selection**: Coordinate-based instead of selector-based
3. **Screenshot API**: Unified screenshot endpoint
4. **Error Format**: Standardized error response structure

---

**Related Documentation:**
- [Getting Started Tutorial](../tutorials/playwright-interactive-mode.md)
- [How-To Guide](../how-to/playwright-template-creation.md)
- [Architecture Overview](../explanations/playwright-architecture.md)
- [Troubleshooting Guide](../troubleshooting/playwright-interactive-issues.md)
- [Frontend API Integration Fix](../how-to/fix-playwright-api-integration.md)
- [Frontend API Reference](api/frontend-api.md)