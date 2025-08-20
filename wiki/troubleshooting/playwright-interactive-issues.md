# Playwright Interactive Mode Troubleshooting

This guide covers common issues specific to ScraperV4's Playwright Interactive Mode and provides detailed solutions for resolving them.

## Quick Diagnostics

### Issue: Playwright Interactive Mode Won't Launch
**Symptoms**: 
- Frontend shows error: "Error starting Playwright interactive mode: {}"
- Console logs show empty error objects
- Clicking interactive mode button produces no visible browser

### Root Cause Analysis

This issue typically occurs when the frontend JavaScript API methods are missing or incorrectly mapped to backend endpoints.

#### Diagnostic Steps

1. **Check Browser Console**:
   ```javascript
   // Open browser DevTools (F12) and check console for errors
   // Look for specific error messages like:
   // "window.api.startPlaywrightInteractive is not a function"
   ```

2. **Verify API Object**:
   ```javascript
   // In browser console, check if API methods exist:
   console.log(typeof window.api.startPlaywrightInteractive);
   // Should return "function", not "undefined"
   ```

3. **Test Backend Connectivity**:
   ```javascript
   // Test if backend is responding:
   await window.api.ping();
   // Should return success response
   ```

### The Missing API Methods Issue

#### Problem Description
The most common cause of Playwright Interactive Mode failure is missing frontend API methods in `/web/static/js/api.js`. The backend endpoints exist and are properly exposed via `@eel.expose`, but the frontend `ScraperAPI` class lacks the corresponding methods.

#### Symptoms
- Empty error objects `{}` in console
- "is not a function" errors
- Frontend button clicks with no backend calls
- Browser console shows: `TypeError: window.api.startPlaywrightInteractive is not a function`

#### Complete Solution

Add all missing Playwright methods to the `ScraperAPI` class in `/web/static/js/api.js`:

```javascript
// Add to ScraperAPI class before the utility methods section

// Playwright Interactive Mode Methods
async startPlaywrightInteractive(url, options = {}) {
    try {
        return await eel.start_playwright_interactive(url, options)();
    } catch (error) {
        console.error('Failed to start Playwright interactive mode:', error);
        throw error;
    }
}

async getBrowserScreenshot(sessionId, fullPage = false) {
    try {
        return await eel.get_browser_screenshot(sessionId, fullPage)();
    } catch (error) {
        console.error('Failed to get screenshot:', error);
        throw error;
    }
}

async startElementSelection(sessionId) {
    try {
        return await eel.start_element_selection(sessionId)();
    } catch (error) {
        console.error('Failed to start element selection:', error);
        throw error;
    }
}

async stopElementSelection(sessionId) {
    try {
        return await eel.stop_element_selection(sessionId)();
    } catch (error) {
        console.error('Failed to stop element selection:', error);
        throw error;
    }
}

async selectElementAtCoordinates(sessionId, x, y) {
    try {
        return await eel.select_element_at_coordinates(sessionId, x, y)();
    } catch (error) {
        console.error('Failed to select element:', error);
        throw error;
    }
}

async getSelectedElements(sessionId) {
    try {
        return await eel.get_selected_elements(sessionId)();
    } catch (error) {
        console.error('Failed to get selected elements:', error);
        throw error;
    }
}

async closePlaywrightSession(sessionId) {
    try {
        return await eel.close_playwright_session(sessionId)();
    } catch (error) {
        console.error('Failed to close session:', error);
        throw error;
    }
}

async getPageInfo(sessionId) {
    try {
        return await eel.get_page_info(sessionId)();
    } catch (error) {
        console.error('Failed to get page info:', error);
        throw error;
    }
}

async closeInteractiveSession(sessionId) {
    try {
        return await eel.close_interactive_session(sessionId)();
    } catch (error) {
        console.error('Failed to close interactive session:', error);
        throw error;
    }
}

async getActiveInteractiveSessions() {
    try {
        return await eel.get_active_interactive_sessions()();
    } catch (error) {
        console.error('Failed to get active sessions:', error);
        throw error;
    }
}

async createTemplateFromSelections(sessionId, templateName, templateDescription = "") {
    try {
        return await eel.create_template_from_selections(sessionId, templateName, templateDescription)();
    } catch (error) {
        console.error('Failed to create template from selections:', error);
        throw error;
    }
}
```

#### Verification Steps

After adding the methods:

1. **Restart the Application**:
   ```bash
   # Stop ScraperV4 (Ctrl+C)
   # Restart
   python main.py
   ```

2. **Test in Browser Console**:
   ```javascript
   // Should now return "function"
   console.log(typeof window.api.startPlaywrightInteractive);
   
   // Test the method exists and can be called
   window.api.startPlaywrightInteractive("https://httpbin.org/html", {headless: true});
   ```

3. **Test Interactive Mode**:
   - Navigate to Templates → Create New Template
   - Choose "Playwright Interactive Mode"
   - Enter URL: `https://books.toscrape.com`
   - Click start - should now launch browser successfully

## Dependency Issues

### Issue: Playwright Not Installed

**Symptoms**:
- Backend errors about missing Playwright modules
- Import errors in Python logs

**Solution**:
```bash
# Install Playwright and browser binaries
source venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium

# Verify installation
python -c "from playwright.async_api import async_playwright; print('Playwright installed successfully')"
```

### Issue: Browser Binaries Missing

**Symptoms**:
- Playwright starts but fails to launch browser
- "Browser executable not found" errors

**Solution**:
```bash
# Install browser binaries
source venv/bin/activate
playwright install chromium

# For all browsers (optional)
playwright install

# Verify browser installation
playwright install --dry-run chromium
```

## Configuration Issues

### Issue: Service Registration Problems

**Symptoms**:
- Backend errors about missing PlaywrightInteractiveService
- Service container errors

**Diagnostic**:
```python
# Test service import and registration
python -c "
import sys
sys.path.append('.')
from src.services.playwright_interactive_service import PlaywrightInteractiveService
print('Service import successful')

from src.core.container import container
service = PlaywrightInteractiveService()
container.register_singleton(PlaywrightInteractiveService, service)
print('Service registration successful')
"
```

**Solution**:
Ensure the service is properly registered in the container and imported correctly in `api_routes.py`.

### Issue: Browser Launch Failures

**Symptoms**:
- Session starts but browser doesn't appear
- Timeout errors during browser launch

**Diagnostic Steps**:

1. **Test Browser Launch Manually**:
   ```python
   import asyncio
   from playwright.async_api import async_playwright
   
   async def test_browser():
       playwright = await async_playwright().start()
       browser = await playwright.chromium.launch(headless=False)
       page = await browser.new_page()
       await page.goto("https://example.com")
       print("Browser launched successfully")
       await browser.close()
       await playwright.stop()
   
   asyncio.run(test_browser())
   ```

2. **Check System Resources**:
   ```bash
   # Check available memory
   free -m  # Linux
   vm_stat  # macOS
   
   # Check running processes
   ps aux | grep chrome
   ps aux | grep playwright
   ```

**Solutions**:

**Solution A**: Increase Timeouts
```python
# In playwright_interactive_service.py
browser_options = {
    'headless': False,
    'slow_mo': 100,
    'timeout': 60000  # Increase timeout to 60 seconds
}
```

**Solution B**: Reduce Resource Usage
```python
# Configure for lower resource usage
browser_options = {
    'headless': True,  # Use headless mode
    'args': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security'
    ]
}
```

## Session Management Issues

### Issue: Sessions Not Closing Properly

**Symptoms**:
- Multiple browser instances remain open
- Memory usage increases over time
- "Too many sessions" errors

**Diagnostic**:
```python
# Check active sessions
import psutil
chrome_processes = [p for p in psutil.process_iter(['pid', 'name']) if 'chrome' in p.info['name'].lower()]
print(f"Active Chrome processes: {len(chrome_processes)}")
```

**Solution**:
```python
# Implement proper session cleanup
async def cleanup_all_sessions():
    """Clean up all Playwright sessions"""
    for session_id, session in self.sessions.items():
        try:
            await session['browser'].close()
            print(f"Closed browser for session: {session_id}")
        except Exception as e:
            print(f"Error closing session {session_id}: {e}")
    
    self.sessions.clear()
    
    if self.playwright:
        await self.playwright.stop()
        self.playwright = None
```

### Issue: Screenshot Capture Failures

**Symptoms**:
- Screenshots return empty or null
- Frontend shows broken image icons

**Diagnostic**:
```python
# Test screenshot capture manually
async def test_screenshot():
    service = PlaywrightInteractiveService()
    session_id = "test_session"
    
    try:
        result = await service.start_session(session_id, "https://example.com")
        screenshot = await service.take_screenshot(session_id)
        print(f"Screenshot length: {len(screenshot) if screenshot else 'None'}")
    except Exception as e:
        print(f"Screenshot test failed: {e}")
```

**Solutions**:

**Solution A**: Verify Page Load
```python
# Ensure page is fully loaded before screenshot
await page.wait_for_load_state('networkidle')
await page.wait_for_timeout(2000)  # Additional wait
screenshot = await page.screenshot()
```

**Solution B**: Handle Screenshot Errors
```python
async def take_screenshot(self, session_id: str, full_page: bool = False) -> Optional[str]:
    try:
        if session_id not in self.sessions:
            return None
        
        page = self.sessions[session_id]['page']
        
        # Take screenshot with error handling
        screenshot_bytes = await page.screenshot(
            full_page=full_page,
            timeout=30000  # 30 second timeout
        )
        
        return base64.b64encode(screenshot_bytes).decode('utf-8')
        
    except Exception as e:
        self.logger.error(f"Screenshot failed for session {session_id}: {e}")
        return None
```

## Network and Connectivity Issues

### Issue: Page Load Failures

**Symptoms**:
- Sessions start but pages don't load
- Timeout errors during navigation

**Solution**:
```python
# Configure robust page loading
async def navigate_with_retry(page, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            await page.goto(url, 
                          wait_until='networkidle', 
                          timeout=30000)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### Issue: Overlay Script Injection Failures

**Symptoms**:
- Browser loads but element selection doesn't work
- No visual feedback when hovering elements

**Diagnostic**:
```javascript
// Check if overlay is loaded in browser console
console.log(typeof window.scraperV4Interactive);
// Should return "object", not "undefined"
```

**Solution**:
```python
# Ensure overlay script injection with retry
async def inject_overlay_with_retry(self, page, max_retries=3):
    for attempt in range(max_retries):
        try:
            await page.add_script_tag(content=self.overlay_script)
            
            # Verify injection worked
            result = await page.evaluate("typeof window.scraperV4Interactive")
            if result == "object":
                return True
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(1)
    
    return False
```

## Performance Optimization

### Issue: Slow Interactive Response

**Symptoms**:
- Delayed highlighting when hovering elements
- Slow screenshot updates

**Solutions**:

**Solution A**: Optimize Screenshot Caching
```python
class ScreenshotCache:
    def __init__(self, ttl=3):  # 3 second cache
        self.cache = {}
        self.ttl = ttl
    
    def get_cached_screenshot(self, session_id):
        if session_id in self.cache:
            screenshot, timestamp = self.cache[session_id]
            if time.time() - timestamp < self.ttl:
                return screenshot
        return None
    
    def cache_screenshot(self, session_id, screenshot):
        self.cache[session_id] = (screenshot, time.time())
```

**Solution B**: Reduce Browser Overhead
```python
# Configure for better performance
performance_config = {
    'headless': False,
    'args': [
        '--disable-extensions',
        '--disable-plugins',
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-renderer-backgrounding',
        '--disable-backgrounding-occluded-windows'
    ]
}
```

## Prevention and Monitoring

### Proactive Health Checks

```python
async def health_check_playwright():
    """Perform health check on Playwright system"""
    
    health_status = {
        'playwright_installed': False,
        'browser_available': False,
        'can_launch_browser': False,
        'api_methods_available': False
    }
    
    try:
        # Check Playwright installation
        from playwright.async_api import async_playwright
        health_status['playwright_installed'] = True
        
        # Check browser availability
        playwright = await async_playwright().start()
        browsers = await playwright.chromium.launch_persistent_context
        health_status['browser_available'] = True
        
        # Test browser launch
        browser = await playwright.chromium.launch(headless=True)
        await browser.close()
        health_status['can_launch_browser'] = True
        
        await playwright.stop()
        
    except Exception as e:
        print(f"Playwright health check failed: {e}")
    
    # Check frontend API methods
    # This would be checked via separate frontend test
    
    return health_status
```

### Automated Diagnostics

```python
def run_playwright_diagnostics():
    """Run comprehensive Playwright diagnostics"""
    
    print("=== Playwright Interactive Mode Diagnostics ===")
    
    # 1. Check Python dependencies
    try:
        import playwright
        print("✓ Playwright Python package installed")
    except ImportError:
        print("✗ Playwright Python package missing")
        return False
    
    # 2. Check browser installation
    import subprocess
    try:
        result = subprocess.run(['playwright', 'install', '--dry-run', 'chromium'], 
                              capture_output=True, text=True)
        if 'chromium' in result.stdout:
            print("✓ Chromium browser available")
        else:
            print("✗ Chromium browser not installed")
    except Exception:
        print("✗ Could not check browser installation")
    
    # 3. Check service files
    import os
    service_file = 'src/services/playwright_interactive_service.py'
    overlay_file = 'src/services/interactive_overlay.js'
    
    if os.path.exists(service_file):
        print("✓ Playwright service file exists")
    else:
        print("✗ Playwright service file missing")
    
    if os.path.exists(overlay_file):
        print("✓ Interactive overlay file exists")
    else:
        print("✗ Interactive overlay file missing")
    
    # 4. Check API routes
    api_file = 'src/web/api_routes.py'
    if os.path.exists(api_file):
        with open(api_file, 'r') as f:
            content = f.read()
            if 'start_playwright_interactive' in content:
                print("✓ Backend API endpoints exist")
            else:
                print("✗ Backend API endpoints missing")
    
    # 5. Check frontend API
    frontend_api = 'web/static/js/api.js'
    if os.path.exists(frontend_api):
        with open(frontend_api, 'r') as f:
            content = f.read()
            if 'startPlaywrightInteractive' in content:
                print("✓ Frontend API methods exist")
            else:
                print("✗ Frontend API methods missing - THIS IS THE LIKELY ISSUE")
                print("  Solution: Add Playwright methods to ScraperAPI class")
    
    print("\n=== Diagnostic Complete ===")
    return True

# Run diagnostics
run_playwright_diagnostics()
```

## Quick Reference

### Essential Commands
```bash
# Install Playwright
pip install playwright playwright-stealth
playwright install chromium

# Test installation
python -c "from playwright.async_api import async_playwright; print('OK')"

# Check running browsers
ps aux | grep chrome

# View logs
tail -f logs/scraperv4.log
```

### Key Files to Check
- `/web/static/js/api.js` - Frontend API methods
- `/src/web/api_routes.py` - Backend endpoints
- `/src/services/playwright_interactive_service.py` - Service implementation
- `/src/services/interactive_overlay.js` - Browser overlay script

### Frontend API Method Checklist
Ensure these methods exist in the `ScraperAPI` class:
- [ ] `startPlaywrightInteractive(url, options)`
- [ ] `getBrowserScreenshot(sessionId, fullPage)`
- [ ] `startElementSelection(sessionId)`
- [ ] `stopElementSelection(sessionId)`
- [ ] `selectElementAtCoordinates(sessionId, x, y)`
- [ ] `getSelectedElements(sessionId)`
- [ ] `closePlaywrightSession(sessionId)`
- [ ] `getPageInfo(sessionId)`
- [ ] `closeInteractiveSession(sessionId)`
- [ ] `getActiveInteractiveSessions()`
- [ ] `createTemplateFromSelections(sessionId, templateName, templateDescription)`

If any methods are missing, add them following the pattern shown in the complete solution above.

---

**Next Steps**: If you're still experiencing issues after following this guide, check the [main troubleshooting guide](../tutorials/troubleshooting.md) or consult the [Playwright Architecture documentation](../explanations/playwright-architecture.md) for deeper technical details.