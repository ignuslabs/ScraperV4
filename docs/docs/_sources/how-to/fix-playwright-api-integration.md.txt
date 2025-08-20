# How to Fix Playwright API Integration Issues

This guide provides step-by-step instructions for resolving the most common Playwright Interactive Mode integration issue: missing frontend API methods that prevent the feature from launching.

## Problem Overview

The Playwright Interactive Mode relies on proper communication between:
1. **Frontend JavaScript** (`template-manager.js`) calling API methods
2. **API Layer** (`api.js`) wrapping Eel calls 
3. **Backend Python** (`api_routes.py`) exposing Eel endpoints
4. **Service Layer** (`playwright_interactive_service.py`) implementing functionality

When any layer is missing or incorrectly configured, the integration fails.

## The Missing Frontend API Methods Issue

### Symptoms
- Frontend error: "Error starting Playwright interactive mode: {}"
- Browser console shows: `TypeError: window.api.startPlaywrightInteractive is not a function`
- Interactive mode button clicks produce no backend calls
- Empty error objects `{}` in logs

### Root Cause
The `ScraperAPI` class in `/web/static/js/api.js` is missing the Playwright-related methods, even though the backend endpoints exist and are properly exposed.

## Step-by-Step Fix

### Step 1: Verify the Problem

Before making changes, confirm this is the issue:

1. **Open Browser Developer Tools** (F12)
2. **Go to Console tab**
3. **Test API method existence**:
   ```javascript
   console.log(typeof window.api.startPlaywrightInteractive);
   ```
   
   **Expected**: `"function"`  
   **Actual**: `"undefined"` (confirms the issue)

### Step 2: Locate the API File

Navigate to the frontend API file:
```
/web/static/js/api.js
```

This file contains the `ScraperAPI` class that wraps all backend communication.

### Step 3: Find the Insertion Point

Look for the section in the `ScraperAPI` class before the "Utility Methods" comment:

```javascript
class ScraperAPI {
    // ... existing methods ...
    
    // Utility Methods  <-- Insert BEFORE this section
    async validateUrl(url) {
        // ...
    }
}
```

### Step 4: Add the Missing Methods

Insert all Playwright-related methods **before** the "Utility Methods" section:

```javascript
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

    // Utility Methods (existing section)
```

### Step 5: Verify the Backend Endpoints

Ensure all corresponding backend endpoints exist in `/src/web/api_routes.py`. Look for these `@eel.expose` functions:

```python
@eel.expose
def start_playwright_interactive(url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

@eel.expose 
def get_browser_screenshot(session_id: str, full_page: bool = False) -> Dict[str, Any]:

@eel.expose
def start_element_selection(session_id: str) -> Dict[str, Any]:

@eel.expose
def stop_element_selection(session_id: str) -> Dict[str, Any]:

@eel.expose
def select_element_at_coordinates(session_id: str, x: int, y: int) -> Dict[str, Any]:

@eel.expose
def get_selected_elements(session_id: str) -> Dict[str, Any]:

@eel.expose
def close_interactive_session(session_id: str) -> Dict[str, Any]:

@eel.expose
def get_page_info(session_id: str) -> Dict[str, Any]:

@eel.expose
def get_active_interactive_sessions() -> Dict[str, Any]:

@eel.expose
def create_template_from_selections(session_id: str, template_name: str, template_description: str = "") -> Dict[str, Any]:
```

If any are missing, they need to be implemented in the backend.

### Step 6: Test the Fix

1. **Save the `api.js` file**

2. **Restart ScraperV4**:
   ```bash
   # Stop the application (Ctrl+C)
   # Restart
   python main.py
   ```

3. **Test in browser console**:
   ```javascript
   // Should now return "function"
   console.log(typeof window.api.startPlaywrightInteractive);
   ```

4. **Test full functionality**:
   - Navigate to Templates → Create New Template
   - Choose "Playwright Interactive Mode"
   - Enter test URL: `https://books.toscrape.com`
   - Click start - browser should now launch successfully

## Advanced Verification

### Check All Methods Are Present

```javascript
// Run in browser console to verify all methods exist
const playwrightMethods = [
    'startPlaywrightInteractive',
    'getBrowserScreenshot', 
    'startElementSelection',
    'stopElementSelection',
    'selectElementAtCoordinates',
    'getSelectedElements',
    'closePlaywrightSession',
    'getPageInfo',
    'closeInteractiveSession',
    'getActiveInteractiveSessions',
    'createTemplateFromSelections'
];

const missingMethods = playwrightMethods.filter(method => 
    typeof window.api[method] !== 'function'
);

if (missingMethods.length === 0) {
    console.log('✅ All Playwright API methods are present');
} else {
    console.log('❌ Missing methods:', missingMethods);
}
```

### Test Backend Connectivity

```javascript
// Test backend connection
async function testBackendConnection() {
    try {
        await window.api.ping();
        console.log('✅ Backend connection working');
        
        // Test Playwright-specific endpoint
        const result = await window.api.startPlaywrightInteractive('https://httpbin.org/html', {
            headless: true,
            viewport: { width: 1280, height: 720 }
        });
        
        if (result.success) {
            console.log('✅ Playwright backend working');
            // Remember to close the test session
            await window.api.closeInteractiveSession(result.session_id);
        } else {
            console.log('❌ Playwright backend issue:', result.error);
        }
        
    } catch (error) {
        console.log('❌ Connection failed:', error);
    }
}

testBackendConnection();
```

## Common Pitfalls to Avoid

### 1. Method Naming Mismatches

**Problem**: Frontend method name doesn't match backend endpoint name.

**Example**:
```javascript
// Wrong - method name doesn't match backend
async closePlaywrightSession(sessionId) {
    return await eel.close_interactive_session(sessionId)();  // Mismatch!
}

// Correct - names should match
async closeInteractiveSession(sessionId) {
    return await eel.close_interactive_session(sessionId)();
}
```

### 2. Missing Error Handling

**Problem**: Methods without proper error handling cause silent failures.

**Correct Pattern**:
```javascript
async methodName(param) {
    try {
        return await eel.backend_method(param)();
    } catch (error) {
        console.error('Failed to execute method:', error);
        throw error;  // Re-throw so caller can handle
    }
}
```

### 3. Incorrect Parameter Passing

**Problem**: Parameter order or types don't match backend expectations.

**Solution**: Check backend method signatures and ensure frontend calls match exactly.

### 4. Forgetting to Restart Application

**Problem**: Changes to `api.js` aren't reflected without restart.

**Solution**: Always restart ScraperV4 after modifying JavaScript files.

## Testing Different Scenarios

### Test with Real Website
```javascript
// Test with actual website
const result = await window.api.startPlaywrightInteractive('https://books.toscrape.com', {
    headless: false,
    viewport: { width: 1280, height: 720 }
});

console.log('Session result:', result);
```

### Test Screenshot Capture
```javascript
// After starting a session
const screenshot = await window.api.getBrowserScreenshot(sessionId, false);
console.log('Screenshot captured:', screenshot.success);
```

### Test Element Selection
```javascript
// After starting element selection mode
const element = await window.api.selectElementAtCoordinates(sessionId, 400, 300);
console.log('Element selected:', element);
```

## Maintenance and Updates

### Adding New Methods

When adding new Playwright functionality:

1. **Add backend endpoint** in `api_routes.py` with `@eel.expose`
2. **Add frontend method** in `api.js` following the established pattern
3. **Test thoroughly** with console verification
4. **Document in reference** materials

### Pattern to Follow

```javascript
async newPlaywrightMethod(param1, param2 = defaultValue) {
    try {
        return await eel.new_playwright_backend_method(param1, param2)();
    } catch (error) {
        console.error('Failed to execute new method:', error);
        throw error;
    }
}
```

## Related Documentation

- [Playwright Interactive Mode Troubleshooting](../troubleshooting/playwright-interactive-issues.md) - Comprehensive troubleshooting
- [Playwright API Reference](../reference/playwright-api.md) - Complete API documentation  
- [Playwright Architecture](../explanations/playwright-architecture.md) - Technical design details
- [Frontend API Reference](../reference/api/frontend-api.md) - ScraperAPI class documentation

## Summary

The missing frontend API methods issue is the most common cause of Playwright Interactive Mode failures. By following this guide:

1. You can quickly identify the problem
2. Add all required methods systematically  
3. Verify the integration works properly
4. Avoid common pitfalls
5. Test thoroughly

After implementing this fix, Playwright Interactive Mode should launch reliably and provide the expected browser-controlled template creation experience.