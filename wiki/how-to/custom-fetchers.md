# How to Create Custom Fetcher Implementations

This guide covers creating custom fetcher implementations for specialized scraping needs beyond the built-in StealthFetcher capabilities.

## Prerequisites

- ScraperV4 installed and configured
- Understanding of HTTP requests and web protocols
- Python programming knowledge
- Familiarity with web scraping concepts
- Optional: Knowledge of browser automation tools

## Overview

Custom fetchers enable:
- **Specialized Protocols**: Support for custom APIs or non-HTTP protocols
- **Advanced Authentication**: Complex login flows and session management
- **Browser Automation**: Full browser control with JavaScript execution
- **Custom Headers/Cookies**: Specialized request manipulation
- **Protocol Extensions**: WebSocket, GraphQL, or other protocols
- **Legacy System Integration**: Support for older web technologies

## Fetcher Architecture

### 1. Base Fetcher Interface

```python
# src/fetchers/base_fetcher.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

@dataclass
class FetchResponse:
    """Standard response object for all fetchers."""
    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    response_time: float
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None

class BaseFetcher(ABC):
    """Base class for all custom fetchers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.session_data = {}
        self.request_count = 0
        self.last_request_time = 0
        
    @abstractmethod
    def fetch(self, url: str, **kwargs) -> FetchResponse:
        """Fetch content from URL."""
        pass
    
    def extract_data(self, response: FetchResponse, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using selectors."""
        from bs4 import BeautifulSoup
        
        if not response.success:
            return {'error': response.error}
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            extracted = {}
            
            for name, selector in selectors.items():
                if '::text' in selector:
                    base_selector = selector.replace('::text', '')
                    elements = soup.select(base_selector)
                    extracted[name] = [elem.get_text().strip() for elem in elements]
                elif '::attr(' in selector:
                    attr_name = selector.split('::attr(')[1].rstrip(')')
                    base_selector = selector.split('::attr(')[0]
                    elements = soup.select(base_selector)
                    extracted[name] = [elem.get(attr_name) for elem in elements if elem.get(attr_name)]
                else:
                    elements = soup.select(selector)
                    extracted[name] = [str(elem) for elem in elements]
            
            return extracted
            
        except Exception as e:
            return {'error': f'Data extraction failed: {str(e)}'}
    
    def apply_delay(self, custom_delay: Optional[float] = None):
        """Apply delay between requests."""
        delay = custom_delay or self.config.get('delay', 1.0)
        current_time = time.time()
        
        if self.last_request_time > 0:
            time_since_last = current_time - self.last_request_time
            if time_since_last < delay:
                time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def update_session_data(self, key: str, value: Any):
        """Update session data."""
        self.session_data[key] = value
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        return self.session_data.get(key, default)
    
    def reset_session(self):
        """Reset session data."""
        self.session_data.clear()
        self.request_count = 0
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources."""
        pass
```

## Custom Fetcher Implementations

### 1. API-Based Fetcher

```python
# src/fetchers/api_fetcher.py
import requests
import json
from typing import Dict, Any, Optional
from .base_fetcher import BaseFetcher, FetchResponse

class APIFetcher(BaseFetcher):
    """Fetcher for REST APIs and JSON endpoints."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with API-specific configuration."""
        # Set default headers
        default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.config.get('user_agent', 'ScraperV4-API/1.0')
        }
        
        # Add custom headers
        custom_headers = self.config.get('headers', {})
        default_headers.update(custom_headers)
        
        self.session.headers.update(default_headers)
        
        # Setup authentication
        auth_config = self.config.get('authentication', {})
        if auth_config:
            self.setup_authentication(auth_config)
    
    def setup_authentication(self, auth_config: Dict[str, Any]):
        """Setup various authentication methods."""
        auth_type = auth_config.get('type')
        
        if auth_type == 'bearer_token':
            token = auth_config.get('token')
            self.session.headers['Authorization'] = f'Bearer {token}'
            
        elif auth_type == 'api_key':
            key_name = auth_config.get('key_name', 'X-API-Key')
            api_key = auth_config.get('api_key')
            self.session.headers[key_name] = api_key
            
        elif auth_type == 'basic_auth':
            username = auth_config.get('username')
            password = auth_config.get('password')
            self.session.auth = (username, password)
            
        elif auth_type == 'oauth2':
            self.setup_oauth2(auth_config)
    
    def setup_oauth2(self, oauth_config: Dict[str, Any]):
        """Setup OAuth2 authentication."""
        client_id = oauth_config.get('client_id')
        client_secret = oauth_config.get('client_secret')
        token_url = oauth_config.get('token_url')
        
        # Get access token
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        try:
            response = requests.post(token_url, data=token_data)
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if access_token:
                self.session.headers['Authorization'] = f'Bearer {access_token}'
                self.update_session_data('oauth_token', access_token)
                self.update_session_data('token_expires', time.time() + token_info.get('expires_in', 3600))
                
        except Exception as e:
            print(f"OAuth2 setup failed: {e}")
    
    def fetch(self, url: str, **kwargs) -> FetchResponse:
        """Fetch data from API endpoint."""
        self.apply_delay()
        start_time = time.time()
        
        try:
            # Check if OAuth token needs refresh
            if self.needs_token_refresh():
                self.refresh_oauth_token()
            
            # Prepare request parameters
            method = kwargs.get('method', 'GET')
            params = kwargs.get('params', {})
            data = kwargs.get('data')
            json_data = kwargs.get('json')
            timeout = kwargs.get('timeout', self.config.get('timeout', 30))
            
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            self.request_count += 1
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    time.sleep(int(retry_after))
                    return self.fetch(url, **kwargs)  # Retry once
            
            return FetchResponse(
                url=url,
                status_code=response.status_code,
                content=response.text,
                headers=dict(response.headers),
                cookies=dict(response.cookies),
                response_time=response_time,
                metadata={
                    'request_count': self.request_count,
                    'method': method,
                    'final_url': response.url
                },
                success=response.status_code < 400
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return FetchResponse(
                url=url,
                status_code=0,
                content='',
                headers={},
                cookies={},
                response_time=response_time,
                metadata={'request_count': self.request_count},
                success=False,
                error=str(e)
            )
    
    def needs_token_refresh(self) -> bool:
        """Check if OAuth token needs refresh."""
        token_expires = self.get_session_data('token_expires', 0)
        return time.time() > token_expires - 60  # Refresh 1 minute before expiry
    
    def refresh_oauth_token(self):
        """Refresh OAuth token."""
        oauth_config = self.config.get('authentication', {})
        if oauth_config.get('type') == 'oauth2':
            self.setup_oauth2(oauth_config)
    
    def extract_json_data(self, response: FetchResponse, json_paths: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from JSON response using JSONPath."""
        if not response.success:
            return {'error': response.error}
        
        try:
            json_data = json.loads(response.content)
            extracted = {}
            
            for name, path in json_paths.items():
                # Simple JSONPath implementation
                value = self.get_json_value(json_data, path)
                extracted[name] = value
            
            return extracted
            
        except Exception as e:
            return {'error': f'JSON extraction failed: {str(e)}'}
    
    def get_json_value(self, data: Any, path: str) -> Any:
        """Get value from JSON data using simple path notation."""
        try:
            # Handle simple paths like 'data.items[0].name'
            parts = path.replace('[', '.').replace(']', '').split('.')
            current = data
            
            for part in parts:
                if part.isdigit():
                    current = current[int(part)]
                elif part:
                    current = current[part]
            
            return current
            
        except (KeyError, IndexError, TypeError):
            return None
    
    def cleanup(self):
        """Cleanup session."""
        if self.session:
            self.session.close()

# Example usage
api_config = {
    'authentication': {
        'type': 'api_key',
        'key_name': 'X-API-Key',
        'api_key': 'your-api-key-here'
    },
    'headers': {
        'Accept-Language': 'en-US'
    },
    'delay': 0.5,
    'timeout': 15
}

api_fetcher = APIFetcher(api_config)
response = api_fetcher.fetch('https://api.example.com/data')

# Extract JSON data
json_paths = {
    'title': 'data.title',
    'items': 'data.items',
    'count': 'meta.total_count'
}

extracted_data = api_fetcher.extract_json_data(response, json_paths)
```

### 2. Browser Automation Fetcher

```python
# src/fetchers/browser_fetcher.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
from typing import Dict, Any, Optional, List
from .base_fetcher import BaseFetcher, FetchResponse

class BrowserFetcher(BaseFetcher):
    """Fetcher using browser automation for JavaScript-heavy sites."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup browser driver with configuration."""
        browser = self.config.get('browser', 'chrome')
        headless = self.config.get('headless', True)
        
        if browser == 'chrome':
            options = ChromeOptions()
            
            if headless:
                options.add_argument('--headless')
            
            # Performance optimizations
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Stealth options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Custom user agent
            user_agent = self.config.get('user_agent')
            if user_agent:
                options.add_argument(f'--user-agent={user_agent}')
            
            # Window size
            window_size = self.config.get('window_size', '1920,1080')
            options.add_argument(f'--window-size={window_size}')
            
            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e:
                print(f"Chrome driver setup failed: {e}")
                return
                
        elif browser == 'firefox':
            options = FirefoxOptions()
            
            if headless:
                options.add_argument('--headless')
            
            try:
                self.driver = webdriver.Firefox(options=options)
            except Exception as e:
                print(f"Firefox driver setup failed: {e}")
                return
        
        if self.driver:
            # Set timeouts
            self.driver.implicitly_wait(self.config.get('implicit_wait', 10))
            self.driver.set_page_load_timeout(self.config.get('page_load_timeout', 30))
            
            # Execute stealth script
            if browser == 'chrome':
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def fetch(self, url: str, **kwargs) -> FetchResponse:
        """Fetch page using browser automation."""
        if not self.driver:
            return FetchResponse(
                url=url,
                status_code=0,
                content='',
                headers={},
                cookies={},
                response_time=0,
                metadata={},
                success=False,
                error='Browser driver not initialized'
            )
        
        self.apply_delay()
        start_time = time.time()
        
        try:
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for page load conditions
            wait_config = kwargs.get('wait_config', {})
            self.wait_for_page_ready(wait_config)
            
            # Execute custom JavaScript if provided
            custom_js = kwargs.get('javascript')
            if custom_js:
                self.driver.execute_script(custom_js)
            
            # Handle authentication/login if needed
            auth_config = kwargs.get('authentication')
            if auth_config:
                self.handle_authentication(auth_config)
            
            # Get page source
            content = self.driver.page_source
            current_url = self.driver.current_url
            
            # Get cookies
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            response_time = time.time() - start_time
            self.request_count += 1
            
            return FetchResponse(
                url=url,
                status_code=200,  # Browser automation doesn't provide HTTP status
                content=content,
                headers={},
                cookies=cookies,
                response_time=response_time,
                metadata={
                    'request_count': self.request_count,
                    'final_url': current_url,
                    'page_title': self.driver.title
                },
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return FetchResponse(
                url=url,
                status_code=0,
                content='',
                headers={},
                cookies={},
                response_time=response_time,
                metadata={'request_count': self.request_count},
                success=False,
                error=str(e)
            )
    
    def wait_for_page_ready(self, wait_config: Dict[str, Any]):
        """Wait for page to be ready based on configuration."""
        wait_time = wait_config.get('timeout', 10)
        wait = WebDriverWait(self.driver, wait_time)
        
        # Wait for specific element
        element_selector = wait_config.get('element')
        if element_selector:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, element_selector)))
            except Exception:
                pass
        
        # Wait for JavaScript condition
        js_condition = wait_config.get('javascript_condition')
        if js_condition:
            try:
                wait.until(lambda driver: driver.execute_script(f"return {js_condition}"))
            except Exception:
                pass
        
        # Simple time-based wait
        time_wait = wait_config.get('time_wait')
        if time_wait:
            time.sleep(time_wait)
    
    def handle_authentication(self, auth_config: Dict[str, Any]):
        """Handle login/authentication flows."""
        auth_type = auth_config.get('type')
        
        if auth_type == 'form_login':
            self.handle_form_login(auth_config)
        elif auth_type == 'oauth_popup':
            self.handle_oauth_popup(auth_config)
    
    def handle_form_login(self, auth_config: Dict[str, Any]):
        """Handle form-based login."""
        try:
            username_selector = auth_config.get('username_selector')
            password_selector = auth_config.get('password_selector')
            submit_selector = auth_config.get('submit_selector')
            
            username = auth_config.get('username')
            password = auth_config.get('password')
            
            # Fill login form
            if username_selector and username:
                username_field = self.driver.find_element(By.CSS_SELECTOR, username_selector)
                username_field.clear()
                username_field.send_keys(username)
            
            if password_selector and password:
                password_field = self.driver.find_element(By.CSS_SELECTOR, password_selector)
                password_field.clear()
                password_field.send_keys(password)
            
            # Submit form
            if submit_selector:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_selector)
                submit_button.click()
            
            # Wait for login completion
            success_indicator = auth_config.get('success_indicator')
            if success_indicator:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, success_indicator)))
            
        except Exception as e:
            print(f"Form login failed: {e}")
    
    def handle_oauth_popup(self, auth_config: Dict[str, Any]):
        """Handle OAuth popup authentication."""
        # Implementation for OAuth popup handling
        pass
    
    def extract_data_with_js(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using JavaScript execution."""
        if not self.driver:
            return {'error': 'Browser driver not available'}
        
        try:
            extracted = {}
            
            for name, selector in selectors.items():
                # Use JavaScript to extract data
                js_script = f"""
                    var elements = document.querySelectorAll('{selector}');
                    var results = [];
                    for (var i = 0; i < elements.length; i++) {{
                        if ('{selector}'.includes('::text')) {{
                            results.push(elements[i].textContent.trim());
                        }} else if ('{selector}'.includes('::attr(')) {{
                            var attr = '{selector}'.match(/::attr\\((.+?)\\)/)[1];
                            results.push(elements[i].getAttribute(attr));
                        }} else {{
                            results.push(elements[i].outerHTML);
                        }}
                    }}
                    return results;
                """
                
                result = self.driver.execute_script(js_script)
                extracted[name] = result
            
            return extracted
            
        except Exception as e:
            return {'error': f'JavaScript extraction failed: {str(e)}'}
    
    def scroll_to_load_content(self, scroll_config: Dict[str, Any]):
        """Scroll page to load dynamic content."""
        scroll_type = scroll_config.get('type', 'bottom')
        scroll_count = scroll_config.get('count', 3)
        scroll_delay = scroll_config.get('delay', 2)
        
        for i in range(scroll_count):
            if scroll_type == 'bottom':
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif scroll_type == 'increment':
                scroll_amount = (i + 1) * (scroll_config.get('increment', 500))
                self.driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
            
            time.sleep(scroll_delay)
    
    def cleanup(self):
        """Cleanup browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

# Example usage
browser_config = {
    'browser': 'chrome',
    'headless': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'delay': 2.0,
    'implicit_wait': 10,
    'page_load_timeout': 30
}

browser_fetcher = BrowserFetcher(browser_config)

# Fetch with authentication
auth_config = {
    'type': 'form_login',
    'username_selector': '#username',
    'password_selector': '#password',
    'submit_selector': '#login-button',
    'username': 'your_username',
    'password': 'your_password',
    'success_indicator': '.dashboard'
}

response = browser_fetcher.fetch(
    'https://example.com/login',
    authentication=auth_config,
    wait_config={'element': '.main-content', 'timeout': 15}
)

# Extract data with JavaScript
data = browser_fetcher.extract_data_with_js({
    'titles': 'h2::text',
    'links': 'a::attr(href)',
    'images': 'img::attr(src)'
})

browser_fetcher.cleanup()
```

### 3. WebSocket Fetcher

```python
# src/fetchers/websocket_fetcher.py
import websocket
import json
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from .base_fetcher import BaseFetcher, FetchResponse

class WebSocketFetcher(BaseFetcher):
    """Fetcher for real-time WebSocket connections."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.ws = None
        self.messages = []
        self.is_connected = False
        self.message_handlers = {}
        
    def fetch(self, url: str, **kwargs) -> FetchResponse:
        """Connect to WebSocket and collect messages."""
        start_time = time.time()
        
        try:
            # Setup WebSocket connection
            self.setup_websocket(url, **kwargs)
            
            # Wait for connection
            timeout = kwargs.get('timeout', 30)
            connection_wait = 0
            while not self.is_connected and connection_wait < timeout:
                time.sleep(0.1)
                connection_wait += 0.1
            
            if not self.is_connected:
                raise Exception("WebSocket connection timeout")
            
            # Send initial messages if configured
            initial_messages = kwargs.get('initial_messages', [])
            for message in initial_messages:
                self.send_message(message)
            
            # Collect messages for specified duration
            collection_duration = kwargs.get('collection_duration', 10)
            time.sleep(collection_duration)
            
            response_time = time.time() - start_time
            
            # Compile collected messages
            content = json.dumps({
                'messages': self.messages,
                'connection_info': {
                    'connected_at': start_time,
                    'collection_duration': collection_duration,
                    'message_count': len(self.messages)
                }
            })
            
            return FetchResponse(
                url=url,
                status_code=200,
                content=content,
                headers={},
                cookies={},
                response_time=response_time,
                metadata={
                    'message_count': len(self.messages),
                    'connection_duration': collection_duration
                },
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return FetchResponse(
                url=url,
                status_code=0,
                content='',
                headers={},
                cookies={},
                response_time=response_time,
                metadata={},
                success=False,
                error=str(e)
            )
        finally:
            self.cleanup()
    
    def setup_websocket(self, url: str, **kwargs):
        """Setup WebSocket connection with callbacks."""
        def on_message(ws, message):
            try:
                # Parse JSON message
                parsed_message = json.loads(message)
                self.messages.append({
                    'timestamp': time.time(),
                    'data': parsed_message
                })
                
                # Call custom message handlers
                message_type = parsed_message.get('type')
                if message_type in self.message_handlers:
                    self.message_handlers[message_type](parsed_message)
                    
            except json.JSONDecodeError:
                # Store raw message if not JSON
                self.messages.append({
                    'timestamp': time.time(),
                    'data': message,
                    'raw': True
                })
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
            self.is_connected = False
        
        def on_close(ws, close_status_code, close_msg):
            self.is_connected = False
        
        def on_open(ws):
            self.is_connected = True
        
        # Setup headers if provided
        headers = kwargs.get('headers', {})
        
        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            url,
            header=headers,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Start WebSocket in separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
    
    def send_message(self, message: Dict[str, Any]):
        """Send message through WebSocket."""
        if self.ws and self.is_connected:
            self.ws.send(json.dumps(message))
    
    def add_message_handler(self, message_type: str, handler: Callable):
        """Add custom message handler for specific message types."""
        self.message_handlers[message_type] = handler
    
    def extract_realtime_data(self, response: FetchResponse, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from real-time messages."""
        if not response.success:
            return {'error': response.error}
        
        try:
            data = json.loads(response.content)
            messages = data.get('messages', [])
            
            extracted = {
                'total_messages': len(messages),
                'filtered_data': {},
                'statistics': {}
            }
            
            # Apply filters
            for filter_name, filter_config in filters.items():
                message_type = filter_config.get('message_type')
                field_path = filter_config.get('field_path')
                
                filtered_messages = []
                for msg in messages:
                    msg_data = msg.get('data', {})
                    
                    # Filter by message type
                    if message_type and msg_data.get('type') != message_type:
                        continue
                    
                    # Extract specific field
                    if field_path:
                        value = self.get_nested_value(msg_data, field_path)
                        if value is not None:
                            filtered_messages.append({
                                'timestamp': msg.get('timestamp'),
                                'value': value
                            })
                    else:
                        filtered_messages.append(msg)
                
                extracted['filtered_data'][filter_name] = filtered_messages
                extracted['statistics'][filter_name] = {
                    'count': len(filtered_messages),
                    'rate_per_second': len(filtered_messages) / data['connection_info']['collection_duration']
                }
            
            return extracted
            
        except Exception as e:
            return {'error': f'Real-time data extraction failed: {str(e)}'}
    
    def get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        try:
            keys = path.split('.')
            current = data
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def cleanup(self):
        """Cleanup WebSocket connection."""
        if self.ws:
            self.ws.close()
            self.is_connected = False
        self.messages.clear()

# Example usage
ws_config = {
    'delay': 0.1,  # Minimal delay for real-time
    'timeout': 30
}

ws_fetcher = WebSocketFetcher(ws_config)

# Add custom message handler
def handle_trade_update(message):
    print(f"Trade update: {message.get('price')} at {message.get('timestamp')}")

ws_fetcher.add_message_handler('trade_update', handle_trade_update)

# Fetch real-time data
response = ws_fetcher.fetch(
    'wss://api.example.com/trades',
    headers={'Authorization': 'Bearer your-token'},
    initial_messages=[
        {'type': 'subscribe', 'channel': 'trades'},
        {'type': 'subscribe', 'channel': 'orderbook'}
    ],
    collection_duration=30
)

# Extract specific data
filters = {
    'trades': {
        'message_type': 'trade_update',
        'field_path': 'price'
    },
    'orderbook': {
        'message_type': 'orderbook_update',
        'field_path': 'bids.0.price'
    }
}

extracted_data = ws_fetcher.extract_realtime_data(response, filters)
```

## Integration with ScraperV4

### 1. Fetcher Manager

```python
# src/fetchers/fetcher_manager.py
from typing import Dict, Any, Optional, Type
from .base_fetcher import BaseFetcher
from .api_fetcher import APIFetcher
from .browser_fetcher import BrowserFetcher
from .websocket_fetcher import WebSocketFetcher

class FetcherManager:
    """Manage and coordinate different fetcher implementations."""
    
    def __init__(self):
        self.fetcher_registry = {
            'api': APIFetcher,
            'browser': BrowserFetcher,
            'websocket': WebSocketFetcher
        }
        self.active_fetchers = {}
    
    def register_fetcher(self, name: str, fetcher_class: Type[BaseFetcher]):
        """Register custom fetcher implementation."""
        self.fetcher_registry[name] = fetcher_class
    
    def get_fetcher(self, fetcher_type: str, config: Optional[Dict[str, Any]] = None) -> BaseFetcher:
        """Get fetcher instance by type."""
        if fetcher_type not in self.fetcher_registry:
            raise ValueError(f"Unknown fetcher type: {fetcher_type}")
        
        fetcher_class = self.fetcher_registry[fetcher_type]
        fetcher_id = f"{fetcher_type}_{id(config)}"
        
        if fetcher_id not in self.active_fetchers:
            self.active_fetchers[fetcher_id] = fetcher_class(config)
        
        return self.active_fetchers[fetcher_id]
    
    def cleanup_all_fetchers(self):
        """Cleanup all active fetchers."""
        for fetcher in self.active_fetchers.values():
            try:
                fetcher.cleanup()
            except Exception as e:
                print(f"Fetcher cleanup error: {e}")
        
        self.active_fetchers.clear()
    
    def get_fetcher_for_url(self, url: str, config: Dict[str, Any]) -> BaseFetcher:
        """Auto-select fetcher based on URL and requirements."""
        
        # WebSocket URLs
        if url.startswith(('ws://', 'wss://')):
            return self.get_fetcher('websocket', config)
        
        # API endpoints (JSON responses)
        if config.get('expect_json', False) or '/api/' in url:
            return self.get_fetcher('api', config)
        
        # JavaScript-heavy sites
        if config.get('requires_javascript', False):
            return self.get_fetcher('browser', config)
        
        # Default to browser for complex sites
        return self.get_fetcher('browser', config)

# Global fetcher manager instance
fetcher_manager = FetcherManager()
```

### 2. Template Integration

```python
# Enhanced template to support custom fetchers
custom_template = {
    "name": "Multi-Fetcher Template",
    "fetcher_config": {
        "type": "browser",  # or "api", "websocket"
        "config": {
            "browser": "chrome",
            "headless": True,
            "authentication": {
                "type": "form_login",
                "username_selector": "#username",
                "password_selector": "#password",
                "submit_selector": "#login",
                "username": "user@example.com",
                "password": "password123"
            }
        }
    },
    "selectors": {
        "title": "h1::text",
        "content": ".content::text",
        "links": "a::attr(href)"
    },
    "post_processing": {
        "clean_text": True,
        "extract_numbers": ["price"],
        "normalize_urls": ["links"]
    }
}

# Usage in scraping service
def create_custom_scraping_job(template, target_url):
    """Create scraping job with custom fetcher."""
    fetcher_config = template.get('fetcher_config', {})
    fetcher_type = fetcher_config.get('type', 'browser')
    fetcher_settings = fetcher_config.get('config', {})
    
    # Get appropriate fetcher
    fetcher = fetcher_manager.get_fetcher(fetcher_type, fetcher_settings)
    
    # Execute scraping
    response = fetcher.fetch(target_url)
    
    if response.success:
        # Extract data using template selectors
        selectors = template.get('selectors', {})
        extracted_data = fetcher.extract_data(response, selectors)
        
        # Apply post-processing
        processed_data = apply_post_processing(extracted_data, template.get('post_processing', {}))
        
        return {
            'status': 'success',
            'data': processed_data,
            'metadata': {
                'fetcher_type': fetcher_type,
                'response_time': response.response_time,
                'url': response.url
            }
        }
    else:
        return {
            'status': 'failed',
            'error': response.error,
            'metadata': {
                'fetcher_type': fetcher_type,
                'url': target_url
            }
        }
```

## Testing Custom Fetchers

### 1. Fetcher Testing Framework

```python
# src/fetchers/testing.py
import unittest
from typing import Dict, Any
from .base_fetcher import BaseFetcher, FetchResponse

class FetcherTestCase(unittest.TestCase):
    """Base test case for fetcher implementations."""
    
    def setUp(self):
        self.fetcher = None
        self.test_config = {}
    
    def tearDown(self):
        if self.fetcher:
            self.fetcher.cleanup()
    
    def test_basic_fetch(self):
        """Test basic fetch functionality."""
        self.assertIsNotNone(self.fetcher, "Fetcher not initialized")
        
        # Test with a reliable URL
        response = self.fetcher.fetch('https://httpbin.org/get')
        
        self.assertIsInstance(response, FetchResponse)
        self.assertTrue(response.success, f"Fetch failed: {response.error}")
        self.assertGreater(len(response.content), 0, "Empty response content")
        self.assertGreater(response.response_time, 0, "Invalid response time")
    
    def test_error_handling(self):
        """Test error handling for invalid URLs."""
        response = self.fetcher.fetch('https://invalid-url-that-does-not-exist.com')
        
        self.assertIsInstance(response, FetchResponse)
        self.assertFalse(response.success, "Expected fetch to fail for invalid URL")
        self.assertIsNotNone(response.error, "Error message should be provided")
    
    def test_data_extraction(self):
        """Test data extraction functionality."""
        # Test with a page that has predictable structure
        response = self.fetcher.fetch('https://httpbin.org/html')
        
        if response.success:
            selectors = {
                'title': 'title::text',
                'headings': 'h1::text'
            }
            
            extracted = self.fetcher.extract_data(response, selectors)
            self.assertIsInstance(extracted, dict)
            self.assertIn('title', extracted)

class APIFetcherTest(FetcherTestCase):
    """Test cases for API fetcher."""
    
    def setUp(self):
        super().setUp()
        from .api_fetcher import APIFetcher
        
        self.test_config = {
            'timeout': 15,
            'delay': 0.1
        }
        self.fetcher = APIFetcher(self.test_config)
    
    def test_json_extraction(self):
        """Test JSON data extraction."""
        response = self.fetcher.fetch('https://httpbin.org/json')
        
        if response.success:
            json_paths = {
                'slideshow_title': 'slideshow.title',
                'slide_count': 'slideshow.slides'
            }
            
            extracted = self.fetcher.extract_json_data(response, json_paths)
            self.assertIsInstance(extracted, dict)

class BrowserFetcherTest(FetcherTestCase):
    """Test cases for browser fetcher."""
    
    def setUp(self):
        super().setUp()
        from .browser_fetcher import BrowserFetcher
        
        self.test_config = {
            'browser': 'chrome',
            'headless': True,
            'timeout': 15
        }
        
        try:
            self.fetcher = BrowserFetcher(self.test_config)
        except Exception as e:
            self.skipTest(f"Browser setup failed: {e}")
    
    def test_javascript_execution(self):
        """Test JavaScript execution capability."""
        response = self.fetcher.fetch(
            'https://httpbin.org/html',
            javascript='document.title = "Modified Title";'
        )
        
        self.assertTrue(response.success)

# Run tests
if __name__ == '__main__':
    unittest.main()
```

## Performance Optimization

### 1. Fetcher Performance Monitoring

```python
# src/fetchers/performance_monitor.py
import time
from typing import Dict, Any, List
from collections import defaultdict, deque

class FetcherPerformanceMonitor:
    """Monitor and optimize fetcher performance."""
    
    def __init__(self, history_size=100):
        self.metrics = defaultdict(lambda: {
            'response_times': deque(maxlen=history_size),
            'success_count': 0,
            'error_count': 0,
            'total_requests': 0
        })
    
    def record_request(self, fetcher_type: str, response_time: float, success: bool):
        """Record request metrics."""
        metrics = self.metrics[fetcher_type]
        
        metrics['response_times'].append(response_time)
        metrics['total_requests'] += 1
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1
    
    def get_performance_stats(self, fetcher_type: str) -> Dict[str, Any]:
        """Get performance statistics for fetcher type."""
        metrics = self.metrics[fetcher_type]
        
        if not metrics['response_times']:
            return {'error': 'No data available'}
        
        response_times = list(metrics['response_times'])
        
        return {
            'total_requests': metrics['total_requests'],
            'success_rate': metrics['success_count'] / metrics['total_requests'],
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'recent_requests': len(response_times)
        }
    
    def get_recommendations(self, fetcher_type: str) -> List[str]:
        """Get performance recommendations."""
        stats = self.get_performance_stats(fetcher_type)
        recommendations = []
        
        if 'error' in stats:
            return recommendations
        
        if stats['success_rate'] < 0.9:
            recommendations.append('Low success rate - check error handling and retry logic')
        
        if stats['avg_response_time'] > 10:
            recommendations.append('High response times - consider connection pooling or faster proxies')
        
        if stats['max_response_time'] > 30:
            recommendations.append('Very slow requests detected - increase timeout or implement request optimization')
        
        return recommendations

# Global performance monitor
performance_monitor = FetcherPerformanceMonitor()
```

## Expected Outcomes

After implementing custom fetchers:

1. **Specialized Scraping**: Handle complex authentication, JavaScript, and APIs
2. **Protocol Support**: WebSocket, GraphQL, and custom protocols
3. **Enhanced Reliability**: Robust error handling and recovery
4. **Performance Optimization**: Optimized for specific use cases
5. **Extensibility**: Easy to add new fetcher types
6. **Integration**: Seamless integration with existing ScraperV4 features

## Success Criteria

- [ ] Base fetcher interface implemented
- [ ] Multiple custom fetcher types working (API, Browser, WebSocket)
- [ ] Integration with template system completed
- [ ] Testing framework functional
- [ ] Performance monitoring operational
- [ ] Documentation and examples provided
- [ ] Error handling and recovery robust

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "create-how-to-dir", "content": "Create the docs/how-to/ directory structure", "status": "completed"}, {"id": "configure-proxies", "content": "Create configure-proxies.md - Setting up proxy rotation and management", "status": "completed"}, {"id": "handle-anti-bot", "content": "Create handle-anti-bot.md - Bypassing anti-bot protection systems", "status": "completed"}, {"id": "export-data", "content": "Create export-data.md - Different data export formats and customization", "status": "completed"}, {"id": "optimize-performance", "content": "Create optimize-performance.md - Memory, speed, and resource optimization", "status": "completed"}, {"id": "deploy-production", "content": "Create deploy-production.md - Production deployment with monitoring", "status": "completed"}, {"id": "debug-failures", "content": "Create debug-failures.md - Diagnosing and fixing failed scraping operations", "status": "completed"}, {"id": "scale-operations", "content": "Create scale-operations.md - Handling high-volume scraping efficiently", "status": "completed"}, {"id": "custom-fetchers", "content": "Create custom-fetchers.md - Creating custom fetcher implementations", "status": "completed"}]