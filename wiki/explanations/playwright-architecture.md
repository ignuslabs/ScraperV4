# Playwright Interactive Architecture

This document explains the architectural design and technical decisions behind ScraperV4's Playwright Interactive Mode, providing the context needed to understand why the system works the way it does.

## The CORS Problem and Solution

### Traditional Browser-Based Interactive Selection

Traditional interactive web scraping tools rely on loading target websites within iframes in the scraping tool's interface. This approach has a fundamental limitation:

```
User Interface → iframe → Target Website
```

**The Problem:** Cross-Origin Resource Sharing (CORS) policies block most modern websites from being loaded in iframes, especially those with security-conscious headers like:

```http
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'
```

**The Impact:** Users see "Due to security restrictions" messages for the majority of websites, making interactive selection impossible.

### Playwright-Based Solution

ScraperV4's Playwright Interactive Mode completely eliminates this limitation by inverting the relationship:

```
Backend (Python) → Playwright Browser → Target Website
                ↓
            Screenshot/DOM
                ↓
Frontend (JavaScript) → User Interface
```

**Key Innovation:** Instead of loading websites in our interface, we launch a real browser instance that we control programmatically, then stream its visual representation to our interface.

## System Architecture

### High-Level Component Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │  Backend Service │    │  Playwright     │
│                 │    │                  │    │  Browser        │
│ • Element       │◄──►│ • Session Mgmt   │◄──►│                 │
│   Selection     │    │ • Screenshot     │    │ • Real Browser  │
│ • Visual        │    │ • DOM Analysis   │    │ • JavaScript    │
│   Feedback      │    │ • Selector Gen   │    │ • Full Rendering│
│ • Template      │    │ • API Endpoints  │    │ • Anti-Detection│
│   Building      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Component Responsibilities

#### 1. Frontend UI (`template-manager.js`)
- **Purpose**: Provide visual interface for element selection
- **Responsibilities**:
  - Display browser screenshots
  - Handle user click/hover interactions
  - Manage field and container selections
  - Coordinate with backend via API calls
  - Build and save templates

#### 2. Backend Service (`playwright_interactive_service.py`)
- **Purpose**: Bridge between UI and browser automation
- **Responsibilities**:
  - Manage Playwright browser sessions
  - Execute JavaScript injection
  - Capture and encode screenshots
  - Generate CSS selectors and XPath
  - Handle element selection at coordinates

#### 3. Playwright Browser (Automated Instance)
- **Purpose**: Provide real browser environment
- **Responsibilities**:
  - Load and render websites naturally
  - Execute injected JavaScript overlay
  - Handle dynamic content and JavaScript
  - Provide anti-detection capabilities

#### 4. Interactive Overlay (`interactive_overlay.js`)
- **Purpose**: Enable element selection within browser
- **Responsibilities**:
  - Highlight elements on hover
  - Track user selections
  - Generate optimal selectors
  - Provide visual feedback

## Data Flow Architecture

### Session Initialization Flow

```
1. User Request
   │
   ├─► Frontend: startPlaywrightInteractiveMode(url)
   │
   ├─► Backend: start_playwright_interactive(url, options)
   │   │
   │   ├─► Launch Playwright browser instance
   │   ├─► Navigate to target URL
   │   ├─► Inject interactive overlay script
   │   ├─► Take initial screenshot
   │   │
   │   └─► Return session data
   │
   └─► Frontend: Display interface with screenshot
```

### Element Selection Flow

```
1. User Hover/Click
   │
   ├─► Frontend: Convert screen coordinates to browser coordinates
   │
   ├─► API Call: select_element_at_coordinates(session_id, x, y)
   │   │
   │   ├─► Browser: element = page.elementAtPoint(x, y)
   │   ├─► Extract: element data (tag, classes, attributes, text)
   │   ├─► Generate: CSS selector + XPath
   │   ├─► Validate: selector uniqueness and quality
   │   │
   │   └─► Return: element data + selectors
   │
   └─► Frontend: Add to template + Visual feedback
```

### Screenshot Streaming

```
Continuous Loop:
┌─► Browser: page.screenshot()
├─► Encode: Base64 encoding
├─► Cache: Short-term screenshot cache
└─► API: get_browser_screenshot() → Frontend
```

## Technical Implementation Details

### Browser Session Management

```python
class PlaywrightInteractiveService:
    def __init__(self):
        self.playwright = None
        self.sessions = {}  # Track multiple concurrent sessions
        
    async def start_session(self, session_id: str, url: str):
        # Launch browser with stealth configuration
        browser = await self.playwright.chromium.launch(
            headless=False,  # Visible for debugging
            slow_mo=100,     # Slight delay for stability
        )
        
        # Create page with viewport configuration
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        
        # Inject anti-detection scripts
        await page.add_init_script(self.stealth_script)
        
        # Navigate and inject overlay
        await page.goto(url, wait_until='networkidle')
        await page.add_script_tag(content=self.overlay_script)
        
        # Store session for later use
        self.sessions[session_id] = {
            'browser': browser,
            'page': page,
            'url': url,
            'created_at': time.time()
        }
```

### Interactive Overlay Injection

The overlay JavaScript is injected into every page to enable element selection:

```javascript
window.scraperV4Interactive = {
    isSelecting: false,
    selectedElements: [],
    
    init: function() {
        this.createOverlay();
        this.bindEvents();
    },
    
    handleClick: function(e) {
        if (!this.isSelecting) return;
        
        const elementData = {
            tag: e.target.tagName.toLowerCase(),
            classes: Array.from(e.target.classList),
            id: e.target.id,
            text: e.target.textContent.trim(),
            selector: this.generateSelector(e.target),
            xpath: this.generateXPath(e.target)
        };
        
        // Send to backend via bridge
        if (window.scraperV4Bridge) {
            window.scraperV4Bridge.elementSelected(elementData);
        }
    }
}
```

### Selector Generation Strategy

The system uses multiple strategies to generate robust selectors:

```python
async def _generate_css_selector(self, page: Page, element: ElementHandle) -> str:
    """Generate optimized CSS selector for element."""
    selector = await page.evaluate("""
        (element) => {
            // Strategy 1: Use ID if available and unique
            if (element.id) {
                return '#' + element.id;
            }
            
            // Strategy 2: Use classes + tag
            let selector = element.tagName.toLowerCase();
            if (element.className) {
                const classes = element.className.split(' ').filter(c => c.trim());
                if (classes.length > 0) {
                    selector += '.' + classes.join('.');
                }
            }
            
            // Strategy 3: Check uniqueness
            const elements = document.querySelectorAll(selector);
            if (elements.length === 1) {
                return selector;
            }
            
            // Strategy 4: Add position if needed
            const parent = element.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children);
                const index = siblings.indexOf(element) + 1;
                selector += `:nth-child(${index})`;
            }
            
            return selector;
        }
    """, element)
    
    return selector or 'unknown'
```

## Security and Anti-Detection

### Browser Fingerprint Randomization

```python
async def _apply_stealth_config(self, page: Page):
    """Apply anti-detection measures."""
    await page.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock realistic navigator properties
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],  // Mock plugin count
        });
    """)
```

### Request Header Rotation

```python
# Dynamic header configuration
headers = {
    'User-Agent': self.get_random_user_agent(),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

## Performance Optimizations

### Screenshot Caching Strategy

```python
class ScreenshotCache:
    def __init__(self, ttl=5):  # 5 second cache
        self.cache = {}
        self.ttl = ttl
    
    def get_screenshot(self, session_id: str):
        now = time.time()
        if session_id in self.cache:
            screenshot, timestamp = self.cache[session_id]
            if now - timestamp < self.ttl:
                return screenshot
        
        # Generate new screenshot
        screenshot = self._capture_screenshot(session_id)
        self.cache[session_id] = (screenshot, now)
        return screenshot
```

### Selector Quality Scoring

```python
def calculate_selector_quality(self, selector: str, element_count: int) -> float:
    """Calculate selector quality score (0-100)."""
    score = 100
    
    # Penalize over-specific selectors
    if selector.count('>') > 3:
        score -= 20
    
    # Penalize nth-child usage
    if ':nth-child(' in selector:
        score -= 15
    
    # Reward ID and data attribute usage
    if selector.startswith('#'):
        score += 10
    if '[data-' in selector:
        score += 5
    
    # Penalize multiple matches
    if element_count > 1:
        score -= min(element_count * 5, 50)
    
    return max(0, min(100, score))
```

## Scalability Considerations

### Session Management

```python
class SessionManager:
    def __init__(self, max_sessions=10, session_timeout=3600):
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.sessions = {}
    
    async def cleanup_expired_sessions(self):
        """Remove expired sessions to free resources."""
        now = time.time()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session['created_at'] > self.session_timeout
        ]
        
        for session_id in expired:
            await self.close_session(session_id)
```

### Resource Limits

```python
# Browser resource configuration
BROWSER_CONFIG = {
    'max_memory': 2 * 1024 * 1024 * 1024,  # 2GB RAM limit
    'max_open_pages': 5,                   # Concurrent page limit
    'max_session_duration': 3600,          # 1 hour timeout
    'screenshot_cache_ttl': 5,             # 5 second cache
    'cleanup_interval': 300                # 5 minute cleanup
}
```

## Error Handling and Recovery

### Graceful Degradation

```python
async def select_element_at_coordinates(self, session_id: str, x: int, y: int):
    """Select element with comprehensive error handling."""
    try:
        page = self.sessions[session_id]['page']
        element = await page.locator("*").element_handle_at_point(x, y)
        
        if not element:
            return {'success': False, 'error': 'No element at coordinates'}
        
        # Generate selectors with fallbacks
        css_selector = await self._generate_css_selector(page, element)
        xpath_selector = await self._generate_xpath_selector(page, element)
        
        return {
            'success': True,
            'element': {
                'css_selector': css_selector,
                'xpath_selector': xpath_selector,
                # ... other data
            }
        }
        
    except Exception as e:
        logger.error(f"Element selection failed: {e}")
        return {
            'success': False, 
            'error': f'Selection failed: {str(e)}',
            'recovery_suggestions': [
                'Try clicking slightly to the side',
                'Wait for page to load completely',
                'Refresh the session if problem persists'
            ]
        }
```

### Session Recovery

```python
async def recover_session(self, session_id: str):
    """Attempt to recover a failed session."""
    if session_id in self.sessions:
        session = self.sessions[session_id]
        
        try:
            # Test if page is still responsive
            await session['page'].evaluate('document.title')
        except:
            # Page is dead, recreate session
            await self.close_session(session_id)
            return await self.start_session(session_id, session['url'])
    
    return {'success': False, 'error': 'Session not recoverable'}
```

## Design Trade-offs and Decisions

### Browser Visibility Choice

**Decision**: Run browsers in non-headless mode by default

**Rationale**:
- **Debugging**: Users can see what's happening in real-time
- **Site Compatibility**: Some sites behave differently in headless mode
- **Trust Building**: Visible browsers increase user confidence
- **Development**: Easier to debug template creation

**Trade-off**: Higher resource usage vs better usability

### Screenshot vs. Live Preview

**Decision**: Use screenshot streaming instead of live iframe embedding

**Rationale**:
- **Security**: Bypasses all CORS restrictions
- **Compatibility**: Works with all websites
- **Control**: Full programmatic control over browser
- **Performance**: Can optimize screenshot frequency

**Trade-off**: Slight latency vs universal compatibility

### Session Architecture

**Decision**: Persistent sessions with manual cleanup

**Rationale**:
- **Performance**: Avoid browser startup costs
- **State Preservation**: Maintain authentication and navigation state
- **User Experience**: Fast response times
- **Resource Management**: Controlled resource usage

**Trade-off**: Memory usage vs performance

## Future Architecture Considerations

### Distributed Browser Management

For scaling beyond single-machine deployments:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Manager   │    │   Browser   │
│             │◄──►│   Service   │◄──►│   Cluster   │
│ • UI        │    │             │    │             │
│ • Templates │    │ • Load Bal  │    │ • Browsers  │
│             │    │ • Sessions  │    │ • Workers   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Machine Learning Integration

Future enhancements could include:

```python
class AIElementDetector:
    """ML-powered element classification."""
    
    async def classify_element(self, element_data: Dict) -> Dict:
        """Use ML to predict element type and optimal selector."""
        features = self.extract_features(element_data)
        
        # Predict element type (title, price, image, etc.)
        element_type = self.classifier.predict(features)
        
        # Generate selector using learned patterns
        optimal_selector = self.selector_generator.generate(
            element_data, element_type
        )
        
        return {
            'type': element_type,
            'confidence': confidence_score,
            'selector': optimal_selector
        }
```

## Conclusion

The Playwright Interactive Architecture represents a fundamental shift in how web scraping tools handle the CORS problem. By moving from iframe-based embedding to programmatic browser control, ScraperV4 achieves:

1. **Universal Compatibility**: Works on all websites
2. **Better Performance**: Real browser rendering and JavaScript execution
3. **Enhanced Security**: Bypass anti-scraping measures
4. **Superior User Experience**: Visual feedback and real-time interaction

This architectural approach enables ScraperV4 to be the first truly universal interactive web scraping platform, removing the traditional barriers that have limited similar tools.

The design prioritizes user experience and compatibility while maintaining performance and scalability, making it suitable for both individual users and enterprise deployments.

---

**Related Documentation:**
- [Tutorial: Getting Started with Playwright Mode](../tutorials/playwright-interactive-mode.md)
- [How-To: Create Templates with Playwright](../how-to/playwright-template-creation.md)
- [API Reference: Playwright Endpoints](../reference/playwright-api.md)
- [Troubleshooting: Playwright Issues](../troubleshooting/playwright-interactive-issues.md)
- [Frontend API Integration Guide](../how-to/fix-playwright-api-integration.md)
- [Frontend API Reference](../reference/api/frontend-api.md)