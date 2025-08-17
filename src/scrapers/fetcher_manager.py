"""Centralized fetcher management for Scrapling library integration.

Key Features:
- StealthyFetcher and PlayWrightFetcher support async operations via async_fetch()
- Both return Playwright Page objects that can be manipulated with page_action callbacks
- AsyncFetcher uses httpx for high-performance concurrent HTTP requests
- Basic Fetcher is synchronous only but can be wrapped in an executor for async

Example page_action for browser automation:
    from playwright.async_api import Page
    
    async def scroll_and_click(page: Page) -> Page:
        await page.mouse.wheel(0, 500)  # Scroll down
        await page.wait_for_timeout(1000)
        button = page.locator('button.load-more')
        if await button.is_visible():
            await button.click()
        return page
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher
from src.core.config import config
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class FetcherType(Enum):
    """Enumeration of available fetcher types."""
    BASIC = "basic"  # Fetcher - Fast, static content
    ASYNC = "async"  # AsyncFetcher - Concurrent operations
    STEALTH = "stealth"  # StealthyFetcher - Anti-bot protection
    PLAYWRIGHT = "playwright"  # PlayWrightFetcher - Dynamic content
    AUTO = "auto"  # Automatic selection based on requirements


class FetcherManager:
    """Manages fetcher selection and configuration for web scraping."""
    
    # Default configurations for each fetcher type
    DEFAULT_CONFIGS = {
        FetcherType.BASIC: {
            'timeout': 30,
            'follow_redirects': True,
            'headers': None,
            'cookies': None
        },
        FetcherType.ASYNC: {
            'timeout': 30,
            'follow_redirects': True,
            'headers': None,
            'cookies': None
        },
        FetcherType.STEALTH: {
            'headless': True,
            'block_images': False,
            'block_webrtc': True,
            'humanize': True,
            'network_idle': True,
            'wait_for_selector': None,
            'os_randomization': True,
            'spoof_canvas': True,
            'spoof_webgl': True,
            'disable_ads': True,
            'google_search': True,
            'timeout': 60,
            'page_action': None  # Optional async function for Page manipulation
        },
        FetcherType.PLAYWRIGHT: {
            'headless': True,
            'block_resources': ['image', 'font', 'media'],
            'wait_for_selector': None,
            'wait_for_timeout': 30,
            'network_idle': True,
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'en-US',
            'timezone': 'America/New_York',
            'stealth': False,
            'real_chrome': False,
            'timeout': 60,
            'page_action': None  # Optional async function for Page manipulation
        }
    }
    
    def __init__(self, default_type: FetcherType = FetcherType.AUTO):
        """Initialize the fetcher manager.
        
        Args:
            default_type: Default fetcher type to use
        """
        self.default_type = default_type
        self.custom_configs = {}
        self._setup_global_config()
    
    def _setup_global_config(self):
        """Setup global configuration for all fetchers."""
        # Always enable auto-match for StealthyFetcher and PlayWrightFetcher
        # This leverages Scrapling's auto-match capabilities for better resilience
        StealthyFetcher.auto_match = True
        PlayWrightFetcher.auto_match = True
        
        # Configure global Fetcher settings with auto-match enabled
        Fetcher.auto_match = True
        
        # Set match threshold and retry settings from config if available
        scrapling_config = config.scrapling
        
        # Configure match threshold (default to 0.85 if not specified)
        match_threshold = getattr(scrapling_config, 'match_threshold', 0.85)
        # Use setattr to avoid type checker complaints about unknown attributes
        if hasattr(Fetcher, 'match_threshold'):
            setattr(Fetcher, 'match_threshold', match_threshold)
            setattr(StealthyFetcher, 'match_threshold', match_threshold)
            setattr(PlayWrightFetcher, 'match_threshold', match_threshold)
        
        # Configure retry settings
        max_retries = getattr(scrapling_config, 'max_retries', 3)
        retry_delay = getattr(scrapling_config, 'retry_delay', 1.0)
        
        # Set global encoding preference
        encoding = getattr(scrapling_config, 'encoding', 'utf-8')
        # Use setattr to avoid type checker complaints about unknown attributes
        if hasattr(Fetcher, 'default_encoding'):
            setattr(Fetcher, 'default_encoding', encoding)
        
        logger.info(
            f"Global Scrapling configuration: auto_match=True, "
            f"threshold={match_threshold}, retries={max_retries}, "
            f"encoding={encoding}"
        )
            
    def set_custom_config(self, fetcher_type: FetcherType, config: Dict[str, Any]):
        """Set custom configuration for a specific fetcher type.
        
        Args:
            fetcher_type: Type of fetcher to configure
            config: Configuration dictionary
        """
        if fetcher_type not in self.custom_configs:
            self.custom_configs[fetcher_type] = {}
        self.custom_configs[fetcher_type].update(config)
    
    def get_config(self, fetcher_type: FetcherType, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get configuration for a specific fetcher type.
        
        Args:
            fetcher_type: Type of fetcher
            overrides: Optional configuration overrides
            
        Returns:
            Merged configuration dictionary
        """
        # Start with default config
        config = self.DEFAULT_CONFIGS.get(fetcher_type, {}).copy()
        
        # Apply custom configs
        if fetcher_type in self.custom_configs:
            config.update(self.custom_configs[fetcher_type])
        
        # Apply overrides
        if overrides:
            config.update(overrides)
            
        return config
    
    def determine_fetcher_type(self, 
                              url: str,
                              template_config: Optional[Dict[str, Any]] = None) -> FetcherType:
        """Automatically determine the best fetcher type based on requirements.
        
        Args:
            url: Target URL
            template_config: Template configuration with requirements
            
        Returns:
            Recommended fetcher type
        """
        if template_config:
            # Check explicit fetcher type in template
            if 'fetcher_type' in template_config:
                fetcher_str = template_config['fetcher_type'].lower()
                try:
                    return FetcherType(fetcher_str)
                except ValueError:
                    logger.warning(f"Invalid fetcher type '{fetcher_str}', using auto selection")
            
            # Check requirements to auto-select
            if template_config.get('javascript_required', False):
                # Need JavaScript execution
                if template_config.get('anti_bot_protection', False):
                    return FetcherType.STEALTH
                else:
                    return FetcherType.PLAYWRIGHT
                    
            if template_config.get('stealth_required', False):
                return FetcherType.STEALTH
                
            if template_config.get('concurrent_scraping', False):
                return FetcherType.ASYNC
        
        # Default to basic fetcher for simple cases
        return FetcherType.BASIC
    
    def fetch(self, 
              url: str,
              fetcher_type: Optional[FetcherType] = None,
              config_overrides: Optional[Dict[str, Any]] = None,
              template_config: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch a URL using the appropriate fetcher.
        
        Args:
            url: URL to fetch
            fetcher_type: Specific fetcher type to use (or auto-detect)
            config_overrides: Configuration overrides
            template_config: Template configuration for auto-selection
            
        Returns:
            Scrapling Adaptor response object
        """
        # Determine fetcher type
        if fetcher_type is None:
            if self.default_type == FetcherType.AUTO:
                fetcher_type = self.determine_fetcher_type(url, template_config)
            else:
                fetcher_type = self.default_type
        
        # Get configuration
        fetch_config = self.get_config(fetcher_type, config_overrides)
        
        # Log the fetcher being used
        logger.info(f"Fetching {url} with {fetcher_type.value} fetcher")
        
        try:
            if fetcher_type == FetcherType.BASIC:
                return Fetcher.get(url, **fetch_config)
                
            elif fetcher_type == FetcherType.STEALTH:
                return StealthyFetcher.fetch(url, **fetch_config)
                
            elif fetcher_type == FetcherType.PLAYWRIGHT:
                return PlayWrightFetcher.fetch(url, **fetch_config)
                
            elif fetcher_type == FetcherType.ASYNC:
                try:
                    # Check if we're already in an async context
                    loop = asyncio.get_running_loop()
                    # We're in an async context, this shouldn't be called
                    raise RuntimeError("Use fetch_async() instead of fetch() in async context")
                except RuntimeError:
                    # No running loop, safe to create new one
                    return asyncio.run(AsyncFetcher.get(url, **fetch_config))
                    
            else:
                raise ValueError(f"Unsupported fetcher type: {fetcher_type}")
                
        except Exception as e:
            logger.error(f"Failed to fetch {url} with {fetcher_type.value}: {e}")
            raise
    
    async def fetch_async(self,
                         url: str,
                         fetcher_type: Optional[FetcherType] = None,
                         config_overrides: Optional[Dict[str, Any]] = None,
                         template_config: Optional[Dict[str, Any]] = None,
                         page_action: Optional[Any] = None) -> Any:
        """Asynchronously fetch a URL with optional page automation.
        
        Both StealthyFetcher and PlayWrightFetcher support async operations and
        return Playwright Page objects that can be manipulated with page_action.
        
        Args:
            url: URL to fetch
            fetcher_type: Specific fetcher type to use
            config_overrides: Configuration overrides
            template_config: Template configuration
            page_action: Optional async function to manipulate the Playwright Page
                        Example: async def scroll_page(page: Page) -> Page
            
        Returns:
            Scrapling Adaptor response object (which wraps a Playwright Page for
            StealthyFetcher and PlayWrightFetcher)
        """
        # Determine fetcher type
        if fetcher_type is None:
            if self.default_type == FetcherType.AUTO:
                fetcher_type = self.determine_fetcher_type(url, template_config)
            else:
                fetcher_type = self.default_type
        
        # Get configuration
        fetch_config = self.get_config(fetcher_type, config_overrides)
        
        # Add page_action if provided and fetcher supports it
        if page_action and fetcher_type in [FetcherType.STEALTH, FetcherType.PLAYWRIGHT]:
            fetch_config['page_action'] = page_action
        
        logger.info(f"Async fetching {url} with {fetcher_type.value} fetcher")
        
        try:
            if fetcher_type == FetcherType.ASYNC:
                # AsyncFetcher uses httpx
                return await AsyncFetcher.get(url, **fetch_config)
                
            elif fetcher_type == FetcherType.STEALTH:
                # StealthyFetcher supports async and returns a Page object
                return await StealthyFetcher.async_fetch(url, **fetch_config)
                
            elif fetcher_type == FetcherType.PLAYWRIGHT:
                # PlayWrightFetcher supports async and returns a Page object
                return await PlayWrightFetcher.async_fetch(url, **fetch_config)
                
            elif fetcher_type == FetcherType.BASIC:
                # Basic fetcher doesn't have native async, run in executor
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    Fetcher.get,
                    url,
                    **fetch_config
                )
            else:
                raise ValueError(f"Unsupported fetcher type for async: {fetcher_type}")
                
        except Exception as e:
            logger.error(f"Async fetch failed for {url} with {fetcher_type.value}: {e}")
            raise
    
    async def fetch_multiple_async(self,
                                  urls: List[str],
                                  fetcher_type: Optional[FetcherType] = None,
                                  config_overrides: Optional[Dict[str, Any]] = None,
                                  template_config: Optional[Dict[str, Any]] = None,
                                  max_concurrent: int = 10) -> List[Any]:
        """Fetch multiple URLs concurrently.
        
        Args:
            urls: List of URLs to fetch
            fetcher_type: Fetcher type to use
            config_overrides: Configuration overrides
            template_config: Template configuration
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of Scrapling Adaptor response objects
        """
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_limit(url: str):
            async with semaphore:
                try:
                    return await self.fetch_async(
                        url, fetcher_type, config_overrides, template_config
                    )
                except Exception as e:
                    logger.error(f"Failed to fetch {url}: {e}")
                    return None
        
        # Create tasks for all URLs
        tasks = [fetch_with_limit(url) for url in urls]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Filter out None results (failed fetches)
        return [r for r in results if r is not None]
    
    def create_from_template(self, template: Dict[str, Any]) -> 'FetcherManager':
        """Create a configured FetcherManager instance from a template.
        
        Args:
            template: Template with fetcher configuration
            
        Returns:
            Configured FetcherManager instance
        """
        # Extract fetcher configuration from template
        fetcher_config = template.get('fetcher_config', {})
        fetcher_type_str = fetcher_config.get('type', 'auto')
        
        try:
            fetcher_type = FetcherType(fetcher_type_str)
        except ValueError:
            fetcher_type = FetcherType.AUTO
        
        # Create new manager with template settings
        manager = FetcherManager(default_type=fetcher_type)
        
        # Apply template-specific configurations
        for ft in FetcherType:
            type_config = fetcher_config.get(ft.value, {})
            if type_config:
                manager.set_custom_config(ft, type_config)
        
        return manager