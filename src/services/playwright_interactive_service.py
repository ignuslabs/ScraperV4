"""Playwright-based interactive service for visual template creation."""

import asyncio
import base64
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from .base_service import BaseService
from src.utils.logging_utils import get_logger

try:
    from playwright.async_api import async_playwright, Browser, Page, ElementHandle
except ImportError:
    async_playwright = None
    Browser = None
    Page = None
    ElementHandle = None

logger = get_logger(__name__)

class PlaywrightInteractiveService(BaseService):
    """Service for managing interactive template creation using Playwright."""
    
    def __init__(self):
        super().__init__()
        self.logger = logger
        self.playwright = None
        self.browser = None
        self.page = None
        self.sessions = {}  # Track multiple sessions
        self.overlay_script = self._load_overlay_script()
        
    def _load_overlay_script(self) -> str:
        """Load the interactive overlay JavaScript."""
        script_path = Path(__file__).parent / "interactive_overlay.js"
        if script_path.exists():
            return script_path.read_text()
        else:
            # Fallback inline script if file doesn't exist yet
            return self._get_inline_overlay_script()
    
    def _get_inline_overlay_script(self) -> str:
        """Inline interactive overlay script as fallback."""
        return """
        // ScraperV4 Interactive Mode Overlay
        (function() {
            if (window.scraperV4Interactive) return; // Already loaded
            
            window.scraperV4Interactive = {
                isSelecting: false,
                selectedElements: [],
                overlay: null,
                
                init: function() {
                    this.createOverlay();
                    this.bindEvents();
                    console.log('ScraperV4 Interactive Mode: Ready');
                },
                
                createOverlay: function() {
                    // Create overlay container
                    this.overlay = document.createElement('div');
                    this.overlay.id = 'scraperv4-overlay';
                    this.overlay.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        pointer-events: none;
                        z-index: 999999;
                    `;
                    document.body.appendChild(this.overlay);
                    
                    // Create highlight element
                    this.highlight = document.createElement('div');
                    this.highlight.id = 'scraperv4-highlight';
                    this.highlight.style.cssText = `
                        position: absolute;
                        border: 2px solid #007bff;
                        background: rgba(0, 123, 255, 0.1);
                        pointer-events: none;
                        z-index: 1000000;
                        display: none;
                    `;
                    document.body.appendChild(this.highlight);
                    
                    // Create selection info box
                    this.infoBox = document.createElement('div');
                    this.infoBox.id = 'scraperv4-info';
                    this.infoBox.style.cssText = `
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        background: #333;
                        color: white;
                        padding: 10px;
                        border-radius: 5px;
                        font-family: monospace;
                        font-size: 12px;
                        z-index: 1000001;
                        max-width: 300px;
                        word-wrap: break-word;
                    `;
                    this.infoBox.innerHTML = 'Hover over elements to inspect. Click to select.';
                    document.body.appendChild(this.infoBox);
                },
                
                bindEvents: function() {
                    document.addEventListener('mouseover', this.handleMouseOver.bind(this));
                    document.addEventListener('mouseout', this.handleMouseOut.bind(this));
                    document.addEventListener('click', this.handleClick.bind(this));
                    document.addEventListener('keydown', this.handleKeyDown.bind(this));
                },
                
                handleMouseOver: function(e) {
                    if (!this.isSelecting) return;
                    
                    const target = e.target;
                    if (target.id && target.id.startsWith('scraperv4-')) return; // Ignore our own elements
                    
                    const rect = target.getBoundingClientRect();
                    this.highlight.style.display = 'block';
                    this.highlight.style.left = (rect.left + window.scrollX) + 'px';
                    this.highlight.style.top = (rect.top + window.scrollY) + 'px';
                    this.highlight.style.width = rect.width + 'px';
                    this.highlight.style.height = rect.height + 'px';
                    
                    // Update info box
                    const selector = this.generateSelector(target);
                    this.infoBox.innerHTML = `
                        <strong>Tag:</strong> ${target.tagName.toLowerCase()}<br>
                        <strong>Class:</strong> ${target.className || 'none'}<br>
                        <strong>ID:</strong> ${target.id || 'none'}<br>
                        <strong>Selector:</strong> ${selector}<br>
                        <small>Click to select this element</small>
                    `;
                },
                
                handleMouseOut: function(e) {
                    if (!this.isSelecting) return;
                    this.highlight.style.display = 'none';
                },
                
                handleClick: function(e) {
                    if (!this.isSelecting) return;
                    
                    const target = e.target;
                    if (target.id && target.id.startsWith('scraperv4-')) return; // Ignore our own elements
                    
                    e.preventDefault();
                    e.stopPropagation();
                    
                    this.selectElement(target);
                },
                
                handleKeyDown: function(e) {
                    if (e.key === 'Escape') {
                        this.stopSelecting();
                    }
                },
                
                selectElement: function(element) {
                    const elementData = {
                        tag: element.tagName.toLowerCase(),
                        id: element.id || null,
                        classes: element.className ? element.className.split(' ').filter(c => c) : [],
                        text: element.textContent.trim().substring(0, 100),
                        selector: this.generateSelector(element),
                        xpath: this.generateXPath(element),
                        position: {
                            x: element.getBoundingClientRect().left,
                            y: element.getBoundingClientRect().top
                        }
                    };
                    
                    this.selectedElements.push(elementData);
                    
                    // Send to backend (if communication is established)
                    if (window.scraperV4Bridge) {
                        window.scraperV4Bridge.elementSelected(elementData);
                    }
                    
                    // Visual feedback
                    element.style.outline = '3px solid #28a745';
                    setTimeout(() => {
                        element.style.outline = '';
                    }, 2000);
                    
                    console.log('Element selected:', elementData);
                },
                
                generateSelector: function(element) {
                    // Generate CSS selector
                    if (element.id) {
                        return '#' + element.id;
                    }
                    
                    let selector = element.tagName.toLowerCase();
                    
                    if (element.className) {
                        const classes = element.className.split(' ').filter(c => c);
                        if (classes.length > 0) {
                            selector += '.' + classes.join('.');
                        }
                    }
                    
                    // Add position-based selector if needed
                    const parent = element.parentElement;
                    if (parent) {
                        const siblings = Array.from(parent.children);
                        const index = siblings.indexOf(element);
                        if (siblings.filter(s => s.tagName === element.tagName).length > 1) {
                            selector += `:nth-of-type(${index + 1})`;
                        }
                    }
                    
                    return selector;
                },
                
                generateXPath: function(element) {
                    // Generate XPath
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    
                    let path = '';
                    let current = element;
                    
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        let name = current.nodeName.toLowerCase();
                        let index = 1;
                        
                        // Count preceding siblings with same tag name
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.nodeName.toLowerCase() === name) {
                                index++;
                            }
                            sibling = sibling.previousElementSibling;
                        }
                        
                        path = `/${name}[${index}]${path}`;
                        current = current.parentElement;
                    }
                    
                    return path;
                },
                
                startSelecting: function() {
                    this.isSelecting = true;
                    document.body.style.cursor = 'crosshair';
                    this.infoBox.style.display = 'block';
                    console.log('ScraperV4: Selection mode started');
                },
                
                stopSelecting: function() {
                    this.isSelecting = false;
                    document.body.style.cursor = '';
                    this.highlight.style.display = 'none';
                    this.infoBox.style.display = 'none';
                    console.log('ScraperV4: Selection mode stopped');
                },
                
                getSelectedElements: function() {
                    return this.selectedElements;
                },
                
                clearSelections: function() {
                    this.selectedElements = [];
                },
                
                cleanup: function() {
                    if (this.overlay) this.overlay.remove();
                    if (this.highlight) this.highlight.remove();
                    if (this.infoBox) this.infoBox.remove();
                    document.removeEventListener('mouseover', this.handleMouseOver);
                    document.removeEventListener('mouseout', this.handleMouseOut);
                    document.removeEventListener('click', this.handleClick);
                    document.removeEventListener('keydown', this.handleKeyDown);
                    console.log('ScraperV4: Cleanup completed');
                }
            };
            
            // Initialize overlay
            window.scraperV4Interactive.init();
            
        })();
        """
    
    async def check_playwright_availability(self) -> bool:
        """Check if Playwright is available."""
        if async_playwright is None:
            self.logger.error("Playwright not installed. Run: pip install playwright")
            return False
        return True
    
    async def start_session(self, session_id: str, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a new interactive session."""
        if not await self.check_playwright_availability():
            return {
                'success': False,
                'error': 'Playwright not available. Please install with: pip install playwright'
            }
        
        try:
            # Default options
            browser_options = {
                'headless': False,  # We want to see the browser for interactive mode
                'slow_mo': 100,     # Slightly slow down for better user experience
            }
            
            # Viewport settings (applied to page, not browser)
            viewport_settings = {'width': 1280, 'height': 720}
            
            if options:
                # Separate viewport from browser options
                if 'viewport' in options:
                    viewport_settings.update(options.pop('viewport'))
                browser_options.update(options)
            
            # Launch Playwright
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # Launch browser
            browser = await self.playwright.chromium.launch(**browser_options)
            
            # Create new page with viewport
            page = await browser.new_page(viewport=viewport_settings)
            
            # Add extra stealth options
            await page.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock languages and plugins
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # Navigate to URL
            self.logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Inject interactive overlay
            await page.add_script_tag(content=self.overlay_script)
            
            # Wait for page to be ready
            await page.wait_for_load_state('domcontentloaded')
            
            # Store session
            self.sessions[session_id] = {
                'browser': browser,
                'page': page,
                'url': url,
                'created_at': asyncio.get_event_loop().time()
            }
            
            # Take initial screenshot
            screenshot = await self.take_screenshot(session_id)
            
            self.logger.info(f"Interactive session {session_id} started successfully")
            
            return {
                'success': True,
                'session_id': session_id,
                'url': url,
                'screenshot': screenshot,
                'viewport': viewport_settings,
                'message': 'Interactive session started. Page is ready for element selection.'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start interactive session: {e}")
            return {
                'success': False,
                'error': f'Failed to start session: {str(e)}'
            }
    
    async def take_screenshot(self, session_id: str, full_page: bool = False) -> Optional[str]:
        """Take a screenshot of the current page."""
        if session_id not in self.sessions:
            return None
        
        try:
            page = self.sessions[session_id]['page']
            screenshot_bytes = await page.screenshot(full_page=full_page, type='png')
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return f"data:image/png;base64,{screenshot_b64}"
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
    
    async def start_element_selection(self, session_id: str) -> Dict[str, Any]:
        """Start element selection mode."""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            page = self.sessions[session_id]['page']
            
            # Start selection mode
            await page.evaluate("window.scraperV4Interactive.startSelecting()")
            
            return {
                'success': True,
                'message': 'Element selection mode started. Click on elements to select them.'
            }
        except Exception as e:
            self.logger.error(f"Failed to start element selection: {e}")
            return {'success': False, 'error': str(e)}
    
    async def stop_element_selection(self, session_id: str) -> Dict[str, Any]:
        """Stop element selection mode."""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            page = self.sessions[session_id]['page']
            
            # Stop selection mode
            await page.evaluate("window.scraperV4Interactive.stopSelecting()")
            
            return {
                'success': True,
                'message': 'Element selection mode stopped.'
            }
        except Exception as e:
            self.logger.error(f"Failed to stop element selection: {e}")
            return {'success': False, 'error': str(e)}
    
    async def select_element_at_coordinates(self, session_id: str, x: int, y: int) -> Dict[str, Any]:
        """Select an element at specific coordinates."""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            page = self.sessions[session_id]['page']
            
            # Get element at coordinates
            element = await page.locator(f"*").locator(f"visible=true").first.element_handle_at_point(x, y)
            
            if not element:
                return {'success': False, 'error': 'No element found at coordinates'}
            
            # Get element data
            element_data = await page.evaluate("""
                (element) => {
                    if (!element) return null;
                    
                    return {
                        tag: element.tagName.toLowerCase(),
                        id: element.id || null,
                        classes: element.className ? element.className.split(' ').filter(c => c.trim()) : [],
                        text: element.textContent.trim().substring(0, 100),
                        attributes: Array.from(element.attributes).reduce((attrs, attr) => {
                            attrs[attr.name] = attr.value;
                            return attrs;
                        }, {}),
                        position: {
                            x: element.getBoundingClientRect().left,
                            y: element.getBoundingClientRect().top,
                            width: element.getBoundingClientRect().width,
                            height: element.getBoundingClientRect().height
                        }
                    };
                }
            """, element)
            
            if element_data:
                # Generate selectors
                css_selector = await self._generate_css_selector(page, element)
                xpath_selector = await self._generate_xpath_selector(page, element)
                
                element_data['css_selector'] = css_selector
                element_data['xpath_selector'] = xpath_selector
            
            return {
                'success': True,
                'element': element_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to select element: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_css_selector(self, page: Page, element: ElementHandle) -> str:
        """Generate optimized CSS selector for element."""
        try:
            selector = await page.evaluate("""
                (element) => {
                    // Generate CSS selector
                    if (element.id) {
                        return '#' + element.id;
                    }
                    
                    let selector = element.tagName.toLowerCase();
                    
                    // Add classes if available
                    if (element.className) {
                        const classes = element.className.split(' ').filter(c => c.trim());
                        if (classes.length > 0) {
                            selector += '.' + classes.join('.');
                        }
                    }
                    
                    // Check if selector is unique
                    const elements = document.querySelectorAll(selector);
                    if (elements.length === 1) {
                        return selector;
                    }
                    
                    // Add nth-child if needed
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
        except:
            return 'unknown'
    
    async def _generate_xpath_selector(self, page: Page, element: ElementHandle) -> str:
        """Generate XPath selector for element."""
        try:
            xpath = await page.evaluate("""
                (element) => {
                    // Generate XPath
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    
                    let path = '';
                    let current = element;
                    
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        let name = current.nodeName.toLowerCase();
                        let index = 1;
                        
                        // Count preceding siblings with same tag name
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.nodeName.toLowerCase() === name) {
                                index++;
                            }
                            sibling = sibling.previousElementSibling;
                        }
                        
                        path = `/${name}[${index}]${path}`;
                        current = current.parentElement;
                    }
                    
                    return path;
                }
            """, element)
            
            return xpath or 'unknown'
        except:
            return 'unknown'
    
    async def get_selected_elements(self, session_id: str) -> Dict[str, Any]:
        """Get all selected elements from the session."""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            page = self.sessions[session_id]['page']
            
            # Get selected elements from JavaScript
            selected_elements = await page.evaluate("window.scraperV4Interactive.getSelectedElements()")
            
            return {
                'success': True,
                'elements': selected_elements or []
            }
        except Exception as e:
            self.logger.error(f"Failed to get selected elements: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close an interactive session."""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            session = self.sessions[session_id]
            
            # Close browser
            await session['browser'].close()
            
            # Remove from sessions
            del self.sessions[session_id]
            
            self.logger.info(f"Interactive session {session_id} closed")
            
            return {
                'success': True,
                'message': 'Session closed successfully'
            }
        except Exception as e:
            self.logger.error(f"Failed to close session: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cleanup_all_sessions(self) -> None:
        """Clean up all active sessions."""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self.sessions.keys())
    
    async def get_page_info(self, session_id: str) -> Dict[str, Any]:
        """Get current page information."""
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        try:
            page = self.sessions[session_id]['page']
            
            info = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        domain: window.location.hostname,
                        elements_count: document.querySelectorAll('*').length,
                        forms_count: document.querySelectorAll('form').length,
                        links_count: document.querySelectorAll('a').length,
                        images_count: document.querySelectorAll('img').length
                    };
                }
            """)
            
            return {
                'success': True,
                'info': info
            }
        except Exception as e:
            self.logger.error(f"Failed to get page info: {e}")
            return {'success': False, 'error': str(e)}