"""Template-based scraper with async support and fetcher configuration."""

import asyncio
import time
from typing import Dict, Any, List, Optional
from .base_scraper import BaseScraper
from .fetcher_manager import FetcherType
from src.templates.adaptive_selector import AdaptiveSelector
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class TemplateScraper(BaseScraper):
    """Template-based scraper with configurable fetcher support."""
    
    def __init__(self, template: Optional[Dict[str, Any]] = None):
        """Initialize the template scraper.
        
        Args:
            template: Scraping template with configuration
        """
        self.template = template
        self.adaptive_selector = AdaptiveSelector()
        
        # Extract fetcher configuration from template
        fetcher_config = self._extract_fetcher_config(template)
        fetcher_type = self._extract_fetcher_type(template)
        
        # Initialize base scraper with fetcher configuration
        super().__init__(fetcher_type=fetcher_type, fetcher_config=fetcher_config)
    
    def _extract_fetcher_type(self, template: Optional[Dict[str, Any]]) -> FetcherType:
        """Extract fetcher type from template.
        
        Args:
            template: Template dictionary
            
        Returns:
            FetcherType enum value
        """
        if not template:
            return FetcherType.AUTO
        
        fetcher_config = template.get('fetcher_config', {})
        fetcher_type_str = fetcher_config.get('type', 'auto')
        
        try:
            return FetcherType(fetcher_type_str)
        except ValueError:
            logger.warning(f"Invalid fetcher type '{fetcher_type_str}' in template, using AUTO")
            return FetcherType.AUTO
    
    def _get_template_name(self) -> str:
        """Get template name safely.
        
        Returns:
            Template name or 'unknown' if template is None or has no name
        """
        return self.template.get('name', 'unknown') if self.template else 'unknown'
    
    def _extract_fetcher_config(self, template: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract fetcher configuration from template.
        
        Args:
            template: Template dictionary
            
        Returns:
            Fetcher configuration dictionary
        """
        if not template:
            return None
        
        fetcher_config = template.get('fetcher_config', {})
        
        # Build configuration for each fetcher type
        config = {}
        
        # Basic fetcher config
        if 'basic' in fetcher_config:
            config['basic'] = fetcher_config['basic']
        
        # Async fetcher config
        if 'async' in fetcher_config:
            config['async'] = fetcher_config['async']
        
        # Stealth fetcher config
        if 'stealth' in fetcher_config:
            config['stealth'] = fetcher_config['stealth']
        elif template.get('stealth_required', False) or template.get('anti_bot_protection', False):
            # Auto-configure stealth if required
            config['stealth'] = {
                'headless': True,
                'humanize': True,
                'block_webrtc': True,
                'spoof_canvas': True,
                'os_randomization': True,
                'network_idle': True
            }
        
        # Playwright fetcher config
        if 'playwright' in fetcher_config:
            config['playwright'] = fetcher_config['playwright']
        elif template.get('javascript_required', False):
            # Auto-configure playwright for JavaScript
            config['playwright'] = {
                'headless': True,
                'network_idle': True,
                'wait_for_selector': template.get('wait_for_selector'),
                'block_resources': ['image', 'font', 'media']
            }
        
        return config if config else None
    
    def set_template(self, template: Dict[str, Any]) -> None:
        """Set or update the scraping template.
        
        Args:
            template: New template configuration
        """
        self.template = template
        
        # Update fetcher configuration
        fetcher_config = self._extract_fetcher_config(template)
        fetcher_type = self._extract_fetcher_type(template)
        
        # Reinitialize fetcher manager
        from .fetcher_manager import FetcherManager
        self.fetcher_manager = FetcherManager(default_type=fetcher_type)
        
        if fetcher_config:
            for ft in FetcherType:
                if ft.value in fetcher_config:
                    self.fetcher_manager.set_custom_config(ft, fetcher_config[ft.value])
    
    def _fetch_page(self, url: str) -> Any:
        """Wrapper method for fetch_page for test compatibility.
        
        Args:
            url: URL to fetch
            
        Returns:
            Scrapling response object
        """
        return self.fetch_page(url)
    
    def extract_data_adaptive(self, response, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using adaptive selectors with self-healing capabilities.
        
        Args:
            response: Scrapling response object
            selectors: Dictionary of field names to CSS selectors
            
        Returns:
            Dictionary of extracted data
        """
        if not self.validate_response(response):
            return {}
        
        extracted_data = {}
        fallback_selectors = self.template.get('fallback_selectors', {}) if self.template else {}
        
        for field_name, selector_config in selectors.items():
            try:
                # Get primary selector
                if isinstance(selector_config, str):
                    primary_selector = selector_config
                elif isinstance(selector_config, dict):
                    primary_selector = selector_config.get('selector', '')
                else:
                    continue
                
                # Get fallback selectors for this field
                field_fallbacks = []
                if field_name in fallback_selectors:
                    fb = fallback_selectors[field_name]
                    if isinstance(fb, list):
                        field_fallbacks = fb
                    elif isinstance(fb, str):
                        field_fallbacks = [fb]
                
                # Use adaptive selector to find element
                result = self.adaptive_selector.find_element_adaptive(
                    response, field_name, primary_selector, field_fallbacks
                )
                
                if result['found']:
                    extracted_data[field_name] = result['value']
                    
                    # Learn from successful selector
                    if result.get('selector_used') != primary_selector:
                        self.adaptive_selector.learn_from_success(
                            field_name, result['selector_used'], response
                        )
                
            except Exception as e:
                logger.error(f"Failed to extract field '{field_name}': {e}")
        
        return extracted_data
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Synchronously scrape URL using the configured template.
        
        Args:
            url: URL to scrape
            **kwargs: Additional arguments
            
        Returns:
            Scraped data dictionary
        """
        if not self.template:
            return {
                'url': url,
                'status': 'failed',
                'error': 'No template configured'
            }
        
        try:
            # Fetch the page using centralized fetcher
            page = self.fetch_page(url)
            
            if not self.validate_response(page):
                return {
                    'url': url,
                    'status': 'failed',
                    'error': f'Invalid response: status={getattr(page, "status", "unknown")}'
                }
            
            # Extract selectors from template
            selectors = self.template.get('selectors', {})
            
            # Extract data using enhanced extraction with auto-save
            if self.template.get('adaptive_selectors', False):
                extracted_data = self.extract_data_adaptive(page, selectors)
            else:
                extracted_data = self.extract_data(page, selectors)
            
            # Apply post-processing if defined
            if 'post_processing' in self.template:
                extracted_data = self._apply_post_processing(extracted_data)
            
            # Apply validation if defined
            if 'validation_rules' in self.template:
                validation_result = self._validate_data(extracted_data)
                if not validation_result['valid']:
                    return {
                        'url': url,
                        'status': 'partial',
                        'data': extracted_data,
                        'validation_errors': validation_result['errors']
                    }
            
            # Update template statistics for successful scrape
            template_name = self._get_template_name()
            if template_name != 'unknown':
                try:
                    from src.data.template_manager import FileTemplateManager
                    tm = FileTemplateManager()
                    tm.update_template_stats(template_name, success=True)
                except Exception as e:
                    logger.debug(f"Failed to update template stats: {e}")
            
            return {
                'url': url,
                'status': 'success',
                'data': extracted_data,
                'items_count': len(extracted_data),
                'template_name': template_name,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape {url} with template: {e}")
            
            # Update template statistics for failed scrape
            template_name = self._get_template_name()
            if template_name != 'unknown':
                try:
                    from src.data.template_manager import FileTemplateManager
                    tm = FileTemplateManager()
                    tm.update_template_stats(template_name, success=False)
                except Exception as stats_error:
                    logger.debug(f"Failed to update template stats: {stats_error}")
            
            return {
                'url': url,
                'status': 'failed',
                'error': str(e),
                'template_name': template_name
            }
    
    async def scrape_async(self, url: str, **kwargs) -> Dict[str, Any]:
        """Asynchronously scrape URL using the configured template.
        
        Args:
            url: URL to scrape
            **kwargs: Additional arguments
            
        Returns:
            Scraped data dictionary
        """
        if not self.template:
            return {
                'url': url,
                'status': 'failed',
                'error': 'No template configured'
            }
        
        try:
            # Fetch the page asynchronously
            page = await self.fetch_page_async(url)
            
            if not self.validate_response(page):
                return {
                    'url': url,
                    'status': 'failed',
                    'error': f'Invalid response: status={getattr(page, "status", "unknown")}'
                }
            
            # Extract selectors from template
            selectors = self.template.get('selectors', {})
            
            # Extract data (this part is synchronous as it's just parsing)
            extracted_data = self.extract_data(page, selectors)
            
            # Apply post-processing if defined
            if 'post_processing' in self.template:
                extracted_data = self._apply_post_processing(extracted_data)
            
            # Apply validation if defined
            if 'validation_rules' in self.template:
                validation_result = self._validate_data(extracted_data)
                if not validation_result['valid']:
                    return {
                        'url': url,
                        'status': 'partial',
                        'data': extracted_data,
                        'validation_errors': validation_result['errors']
                    }
            
            # Update template statistics for successful scrape
            template_name = self._get_template_name()
            if template_name != 'unknown':
                try:
                    from src.data.template_manager import FileTemplateManager
                    tm = FileTemplateManager()
                    tm.update_template_stats(template_name, success=True)
                except Exception as e:
                    logger.debug(f"Failed to update template stats: {e}")
            
            return {
                'url': url,
                'status': 'success',
                'data': extracted_data,
                'items_count': len(extracted_data),
                'template_name': template_name,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to async scrape {url} with template: {e}")
            return {
                'url': url,
                'status': 'failed',
                'error': str(e),
                'template_name': self._get_template_name()
            }
    
    def scrape_with_pagination(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape multiple pages following pagination links.
        
        Args:
            url: Starting URL
            **kwargs: Additional arguments including max_pages
            
        Returns:
            Combined results from all pages
        """
        max_pages = kwargs.get('max_pages', 10)
        all_results = []
        current_url = url
        
        for page_num in range(max_pages):
            result = self.scrape(current_url)
            
            if result.get('status') != 'success':
                break
            
            all_results.append(result)
            
            # Look for next page link
            page_data = result.get('data', {})
            next_url = page_data.get('next_page_url')
            
            if not next_url:
                # Try to find pagination in template
                pagination_config = self.template.get('pagination', {}) if self.template else {}
                next_selector = pagination_config.get('next_selector')
                
                if next_selector:
                    # Re-fetch and look for next link
                    page = self.fetch_page(current_url)
                    next_elem = page.css(next_selector) if page else None
                    next_url = next_elem.get('href') if next_elem and hasattr(next_elem, 'get') else None
            
            if not next_url:
                break
            
            current_url = next_url
            
            # Add delay between pages
            if page_num < max_pages - 1:
                time.sleep(self._calculate_delay())
        
        # Combine all results
        total_items = sum(result.get('items_count', 0) for result in all_results if result.get('status') == 'success')
        
        return {
            'url': url,
            'status': 'success',
            'pages_scraped': len(all_results),
            'total_items': total_items,
            'results': all_results,
            'template_name': self._get_template_name()
        }
    
    async def scrape_with_pagination_async(self, url: str, **kwargs) -> Dict[str, Any]:
        """Asynchronously scrape multiple pages following pagination.
        
        Args:
            url: Starting URL
            **kwargs: Additional arguments
            
        Returns:
            Combined results from all pages
        """
        max_pages = kwargs.get('max_pages', 10)
        all_results = []
        current_url = url
        
        for page_num in range(max_pages):
            result = await self.scrape_async(current_url)
            
            if result.get('status') != 'success':
                break
            
            all_results.append(result)
            
            # Look for next page link
            page_data = result.get('data', {})
            next_url = page_data.get('next_page_url')
            
            if not next_url:
                # Try to find pagination in template
                pagination_config = self.template.get('pagination', {}) if self.template else {}
                next_selector = pagination_config.get('next_selector')
                
                if next_selector:
                    page = await self.fetch_page_async(current_url)
                    next_elem = page.css(next_selector) if page else None
                    next_url = next_elem.get('href') if next_elem and hasattr(next_elem, 'get') else None
            
            if not next_url:
                break
            
            current_url = next_url
            
            # Add delay between pages
            if page_num < max_pages - 1:
                await asyncio.sleep(self._calculate_delay())
        
        total_items = sum(result.get('items_count', 0) for result in all_results if result.get('status') == 'success')
        
        return {
            'url': url,
            'status': 'success',
            'pages_scraped': len(all_results),
            'total_items': total_items,
            'results': all_results,
            'template_name': self._get_template_name()
        }
    
    def _apply_post_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply post-processing rules from template.
        
        Args:
            data: Raw extracted data
            
        Returns:
            Processed data
        """
        if not self.template or 'post_processing' not in self.template:
            return data
        
        processing_rules = self.template.get('post_processing', [])
        processed_data = data.copy()
        
        for rule in processing_rules:
            try:
                rule_type = rule.get('type')
                field_name = rule.get('field')
                
                if not field_name or field_name not in processed_data:
                    continue
                
                value = processed_data[field_name]
                
                if rule_type == 'strip':
                    if isinstance(value, str):
                        processed_data[field_name] = value.strip()
                    elif isinstance(value, list):
                        processed_data[field_name] = [v.strip() if isinstance(v, str) else v for v in value]
                
                elif rule_type == 'lowercase':
                    if isinstance(value, str):
                        processed_data[field_name] = value.lower()
                    elif isinstance(value, list):
                        processed_data[field_name] = [v.lower() if isinstance(v, str) else v for v in value]
                
                elif rule_type == 'uppercase':
                    if isinstance(value, str):
                        processed_data[field_name] = value.upper()
                    elif isinstance(value, list):
                        processed_data[field_name] = [v.upper() if isinstance(v, str) else v for v in value]
                
                elif rule_type == 'replace':
                    pattern = rule.get('pattern')
                    replacement = rule.get('replacement', '')
                    if pattern and isinstance(value, str):
                        import re
                        processed_data[field_name] = re.sub(pattern, replacement, value)
                
                elif rule_type == 'extract_number':
                    if isinstance(value, str):
                        import re
                        numbers = re.findall(r'\d+\.?\d*', value)
                        if numbers:
                            processed_data[field_name] = float(numbers[0])
                
                elif rule_type == 'split':
                    separator = rule.get('separator', ',')
                    if isinstance(value, str):
                        processed_data[field_name] = value.split(separator)
                
                elif rule_type == 'join':
                    separator = rule.get('separator', ', ')
                    if isinstance(value, list):
                        processed_data[field_name] = separator.join(str(v) for v in value)
                        
            except Exception as e:
                logger.error(f"Failed to apply post-processing rule {rule}: {e}")
        
        return processed_data
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against template rules.
        
        Args:
            data: Extracted data
            
        Returns:
            Validation result with 'valid' bool and 'errors' list
        """
        if not self.template or 'validation_rules' not in self.template:
            return {'valid': True, 'errors': []}
        
        validation_rules = self.template.get('validation_rules', {})
        errors = []
        
        # Check required fields
        required_fields = validation_rules.get('required_fields', [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Required field '{field}' is missing or empty")
        
        # Check field types
        field_types = validation_rules.get('field_types', {})
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                value = data[field]
                
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field '{field}' should be string, got {type(value).__name__}")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field}' should be number, got {type(value).__name__}")
                elif expected_type == 'list' and not isinstance(value, list):
                    errors.append(f"Field '{field}' should be list, got {type(value).__name__}")
                elif expected_type == 'dict' and not isinstance(value, dict):
                    errors.append(f"Field '{field}' should be dict, got {type(value).__name__}")
        
        # Check patterns
        field_patterns = validation_rules.get('field_patterns', {})
        for field, pattern in field_patterns.items():
            if field in data and data[field]:
                value = str(data[field])
                import re
                if not re.match(pattern, value):
                    errors.append(f"Field '{field}' does not match pattern '{pattern}'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_template(self) -> Dict[str, Any]:
        """Validate template structure and selectors."""
        if not self.template:
            return {'valid': False, 'errors': ['No template configured']}
        
        errors = []
        
        # Check required fields
        if 'selectors' not in self.template or not self.template['selectors']:
            errors.append('Template must have selectors defined')
        
        # Validate selector format
        selectors = self.template.get('selectors', {})
        for field, selector_config in selectors.items():
            if isinstance(selector_config, str):
                if not selector_config.strip():
                    errors.append(f'Empty selector for field: {field}')
            elif isinstance(selector_config, dict):
                if not selector_config.get('selector'):
                    errors.append(f'Missing selector in config for field: {field}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def test_selectors(self, url: str) -> Dict[str, Any]:
        """Test template selectors against a URL."""
        if not self.template or not self.template.get('selectors'):
            return {
                'error': 'No selectors to test',
                'statistics': {'total_selectors': 0, 'successful_selectors': 0, 'success_rate': 0}
            }
        
        try:
            page = self.fetch_page(url)
            if not self.validate_response(page):
                return {
                    'error': 'Failed to fetch page for testing',
                    'statistics': {'total_selectors': 0, 'successful_selectors': 0, 'success_rate': 0}
                }
            
            selectors = self.template['selectors']
            results = {}
            successful = 0
            
            for field_name, selector_config in selectors.items():
                selector = ''  # Initialize selector to avoid unbound variable
                try:
                    selector = selector_config if isinstance(selector_config, str) else selector_config.get('selector', '')
                    elements = page.css(selector) if selector else None
                    
                    if elements:
                        # Get element count and sample value
                        element_list = list(elements)
                        element_count = len(element_list)
                        sample_value = element_list[0].text.strip() if element_list and hasattr(element_list[0], 'text') else ''
                        
                        results[field_name] = {
                            'found': True,
                            'element_count': element_count,
                            'sample_value': sample_value[:100],
                            'selector': selector
                        }
                        successful += 1
                    else:
                        results[field_name] = {
                            'found': False,
                            'element_count': 0,
                            'sample_value': '',
                            'selector': selector
                        }
                except Exception as e:
                    results[field_name] = {
                        'found': False,
                        'error': str(e),
                        'selector': selector
                    }
            
            total = len(selectors)
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                'selector_results': results,
                'statistics': {
                    'total_selectors': total,
                    'successful_selectors': successful,
                    'success_rate': success_rate
                }
            }
            
        except Exception as e:
            return {
                'error': f'Testing failed: {str(e)}',
                'statistics': {'total_selectors': 0, 'successful_selectors': 0, 'success_rate': 0}
            }