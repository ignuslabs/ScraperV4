"""Base scraper class with centralized fetcher management and async support."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from .fetcher_manager import FetcherManager, FetcherType
from src.core.config import config
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class BaseScraper(ABC):
    """Base scraper class with centralized fetcher management."""
    
    def __init__(self, 
                 fetcher_type: Union[FetcherType, str] = FetcherType.AUTO,
                 fetcher_config: Optional[Dict[str, Any]] = None):
        """Initialize the base scraper.
        
        Args:
            fetcher_type: Type of fetcher to use (or 'auto' for automatic selection)
            fetcher_config: Custom fetcher configuration
        """
        self.scraping_config = config.scrapling
        
        # Convert string to FetcherType if needed
        if isinstance(fetcher_type, str):
            try:
                fetcher_type = FetcherType(fetcher_type)
            except ValueError:
                logger.warning(f"Invalid fetcher type '{fetcher_type}', using AUTO")
                fetcher_type = FetcherType.AUTO
        
        # Initialize fetcher manager
        self.fetcher_manager = FetcherManager(default_type=fetcher_type)
        
        # Apply custom configuration if provided
        if fetcher_config:
            for ft in FetcherType:
                if ft.value in fetcher_config:
                    self.fetcher_manager.set_custom_config(ft, fetcher_config[ft.value])
    
    def fetch_page(self, 
                   url: str, 
                   fetcher_type: Optional[FetcherType] = None,
                   config_overrides: Optional[Dict[str, Any]] = None) -> Any:
        """Fetch a page using the centralized fetcher manager.
        
        Args:
            url: URL to fetch
            fetcher_type: Optional specific fetcher type
            config_overrides: Optional configuration overrides
            
        Returns:
            Scrapling Adaptor response object
        """
        return self.fetcher_manager.fetch(
            url, 
            fetcher_type=fetcher_type,
            config_overrides=config_overrides,
            template_config=getattr(self, 'template', None)
        )
    
    async def fetch_page_async(self,
                              url: str,
                              fetcher_type: Optional[FetcherType] = None,
                              config_overrides: Optional[Dict[str, Any]] = None) -> Any:
        """Asynchronously fetch a page.
        
        Args:
            url: URL to fetch
            fetcher_type: Optional specific fetcher type
            config_overrides: Optional configuration overrides
            
        Returns:
            Scrapling Adaptor response object
        """
        return await self.fetcher_manager.fetch_async(
            url,
            fetcher_type=fetcher_type,
            config_overrides=config_overrides,
            template_config=getattr(self, 'template', None)
        )
    
    @abstractmethod
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Synchronous scraping method to be implemented by subclasses.
        
        Args:
            url: URL to scrape
            **kwargs: Additional arguments
            
        Returns:
            Scraped data dictionary
        """
        pass
    
    @abstractmethod
    async def scrape_async(self, url: str, **kwargs) -> Dict[str, Any]:
        """Asynchronous scraping method to be implemented by subclasses.
        
        Args:
            url: URL to scrape
            **kwargs: Additional arguments
            
        Returns:
            Scraped data dictionary
        """
        pass
    
    def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Synchronously scrape multiple URLs with delay between requests.
        
        Args:
            urls: List of URLs to scrape
            **kwargs: Additional arguments passed to scrape()
            
        Returns:
            List of scraped data dictionaries
        """
        results = []
        for i, url in enumerate(urls):
            try:
                result = self.scrape(url, **kwargs)
                results.append(result)
                
                # Add delay between requests (except for last URL)
                if i < len(urls) - 1:
                    delay = self._calculate_delay()
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    async def scrape_multiple_async(self,
                                   urls: List[str],
                                   max_concurrent: int = 10,
                                   **kwargs) -> List[Dict[str, Any]]:
        """Asynchronously scrape multiple URLs concurrently.
        
        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum concurrent scraping operations
            **kwargs: Additional arguments passed to scrape_async()
            
        Returns:
            List of scraped data dictionaries
        """
        # Use semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_limit(url: str):
            async with semaphore:
                try:
                    return await self.scrape_async(url, **kwargs)
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return {
                        'url': url,
                        'error': str(e),
                        'status': 'failed'
                    }
        
        # Create tasks for all URLs
        tasks = [scrape_with_limit(url) for url in urls]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        return results
    
    def _calculate_delay(self) -> float:
        """Calculate delay between requests."""
        import random
        min_delay, max_delay = self.scraping_config.delay_range
        return random.uniform(min_delay, max_delay)
    
    def validate_response(self, page) -> bool:
        """Validate scraping response.
        
        Args:
            page: Scrapling Adaptor response object
            
        Returns:
            True if response is valid
        """
        return (page is not None and 
                hasattr(page, 'status') and 
                page.status == 200 and
                hasattr(page, 'css'))
    
    def _extract_with_css(self, response, selector: str, extract_type: str = 'auto', 
                         auto_save: bool = False, fallback_selectors: Optional[List[str]] = None) -> Any:
        """Enhanced CSS selector extraction with auto-save and fallbacks.
        
        Args:
            response: Scrapling response object
            selector: CSS selector string
            extract_type: Type of extraction - 'text', 'attr', 'html', 'first', 'all', or 'auto'
            auto_save: Enable auto-save for resilient scraping
            fallback_selectors: List of fallback selectors to try
            
        Returns:
            Extracted data in appropriate format
        """
        # Comprehensive validation of response object
        if response is None:
            raise ValueError("Response object cannot be None")
        
        if not hasattr(response, 'css'):
            raise AttributeError(f"Response object of type {type(response).__name__} does not have 'css' method")
        
        # Validate selector parameter
        if not isinstance(selector, str):
            raise TypeError(f"Selector must be a string, got {type(selector).__name__}")
        
        if not selector.strip():
            raise ValueError("Selector cannot be empty or whitespace-only")
        
        # Validate extract_type parameter
        valid_extract_types = {'auto', 'text', 'attr', 'html', 'first', 'all'}
        if not isinstance(extract_type, str):
            raise TypeError(f"Extract type must be a string, got {type(extract_type).__name__}")
        
        if extract_type not in valid_extract_types:
            raise ValueError(f"Invalid extract_type '{extract_type}'. Must be one of: {', '.join(sorted(valid_extract_types))}")
        
        # Validate fallback_selectors if provided
        if fallback_selectors is not None:
            if not isinstance(fallback_selectors, list):
                raise TypeError(f"Fallback selectors must be a list, got {type(fallback_selectors).__name__}")
            
            for i, fallback in enumerate(fallback_selectors):
                if not isinstance(fallback, str):
                    raise TypeError(f"Fallback selector at index {i} must be a string, got {type(fallback).__name__}")
                
                if not fallback.strip():
                    raise ValueError(f"Fallback selector at index {i} cannot be empty or whitespace-only")
        
        # Try main selector first
        try:
            elements = response.css(selector, auto_save=auto_save)
            
            if elements:
                return self._process_elements(elements, extract_type, selector)
                
        except Exception as e:
            logger.debug(f"Primary selector '{selector}' failed: {e}")
        
        # Try fallback selectors if provided
        if fallback_selectors:
            for fallback in fallback_selectors:
                try:
                    elements = response.css(fallback, auto_save=auto_save)
                    if elements:
                        logger.info(f"Used fallback selector: {fallback}")
                        return self._process_elements(elements, extract_type, fallback)
                except Exception as e:
                    logger.debug(f"Fallback selector '{fallback}' failed: {e}")
        
        # Return None if no selectors worked
        return None
    
    def _process_elements(self, elements, extract_type: str, selector: str) -> Any:
        """Process extracted elements based on extract type.
        
        Args:
            elements: Scrapling elements
            extract_type: Type of extraction
            selector: Original selector (for pseudo-selector processing)
            
        Returns:
            Processed data
        """
        # Handle pseudo-selectors
        if selector.endswith('::text'):
            return self._extract_text_content(elements)
        elif '::attr(' in selector and selector.endswith(')'):
            attr_start = selector.find('::attr(')
            attr_name = selector[attr_start + 7:-1]
            return self._extract_attribute_values(elements, attr_name)
        elif selector.endswith('::html'):
            return self._extract_html_content(elements)
        
        # Handle extract types
        if extract_type == 'text':
            return self._extract_text_content(elements)
        elif extract_type == 'html':
            return self._extract_html_content(elements)
        elif extract_type == 'first':
            return self._get_first_element(elements)
        elif extract_type == 'all':
            return self._get_all_elements(elements)
        else:  # auto
            return self._extract_auto_format(elements)
    
    def _extract_text_content(self, elements) -> Union[str, List[str]]:
        """Extract text content from elements."""
        try:
            # Check if elements is iterable
            element_list = list(elements)
            if len(element_list) == 1:
                return element_list[0].text.strip() if hasattr(element_list[0], 'text') else ''
            else:
                return [elem.text.strip() if hasattr(elem, 'text') else '' for elem in element_list]
        except (TypeError, AttributeError):
            # Single element
            return elements.text.strip() if hasattr(elements, 'text') else ''
    
    def _extract_attribute_values(self, elements, attr_name: str) -> Union[str, List[str]]:
        """Extract attribute values from elements."""
        try:
            element_list = list(elements)
            if len(element_list) == 1:
                elem = element_list[0]
                return elem.get(attr_name, '') if hasattr(elem, 'get') else ''
            else:
                return [elem.get(attr_name, '') if hasattr(elem, 'get') else '' 
                       for elem in element_list]
        except (TypeError, AttributeError):
            # Single element
            return elements.get(attr_name, '') if hasattr(elements, 'get') else ''
    
    def _extract_html_content(self, elements) -> Union[str, List[str]]:
        """Extract HTML content from elements."""
        try:
            element_list = list(elements)
            if len(element_list) == 1:
                return element_list[0].html if hasattr(element_list[0], 'html') else ''
            else:
                return [elem.html if hasattr(elem, 'html') else '' for elem in element_list]
        except (TypeError, AttributeError):
            return elements.html if hasattr(elements, 'html') else ''
    
    def _get_first_element(self, elements):
        """Get the first element."""
        try:
            element_list = list(elements)
            return element_list[0] if element_list else None
        except (TypeError, AttributeError):
            return elements
    
    def _get_all_elements(self, elements):
        """Get all elements as a list."""
        try:
            return list(elements)
        except (TypeError, AttributeError):
            return [elements] if elements else []
    
    def _extract_auto_format(self, elements):
        """Auto-detect format based on element count."""
        try:
            element_list = list(elements)
            if len(element_list) == 1:
                return element_list[0]
            return element_list
        except (TypeError, AttributeError):
            return elements
    
    def extract_data(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from response using selectors with auto-save support.
        
        Args:
            response: Scrapling response object
            selectors: Dictionary of field names to CSS selectors or configs
            
        Returns:
            Dictionary of extracted data
        """
        if not self.validate_response(response):
            return {}
        
        extracted_data = {}
        
        for field_name, selector_config in selectors.items():
            try:
                # Handle both string selectors and config dictionaries
                if isinstance(selector_config, str):
                    # Simple string selector
                    value = self._extract_with_css(response, selector_config, auto_save=True)
                    
                elif isinstance(selector_config, dict):
                    # Advanced configuration
                    selector = selector_config.get('selector', '')
                    extract_type = selector_config.get('type', 'auto')
                    auto_save = selector_config.get('auto_save', True)
                    fallback_selectors = selector_config.get('fallback_selectors', [])
                    
                    value = self._extract_with_css(
                        response, selector, extract_type, 
                        auto_save=auto_save, 
                        fallback_selectors=fallback_selectors
                    )
                else:
                    value = None
                
                if value is not None:
                    extracted_data[field_name] = value
                    
            except Exception as e:
                logger.error(f"Failed to extract '{field_name}': {e}")
                extracted_data[field_name] = None
        
        return extracted_data