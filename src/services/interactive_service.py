"""Interactive service for visual template creation."""

from typing import Dict, Any, List, Optional
import re
from bs4 import BeautifulSoup
from .base_service import BaseService
from src.scrapers.template_scraper import TemplateScraper
from src.templates.template_validator import TemplateValidator
from src.utils.logging_utils import get_logger

class InteractiveService(BaseService):
    """Service for managing interactive template creation."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.validator = TemplateValidator()
        self.learning_data = {}  # Domain-specific learning data
        
    def analyze_page_structure(self, url: str) -> Dict[str, Any]:
        """
        Analyze page structure for pattern detection.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with page structure analysis
        """
        try:
            # Use template scraper to fetch page
            scraper = TemplateScraper()
            html = scraper.fetch_page(url)
            
            if not html:
                return {
                    'success': False,
                    'error': 'Failed to fetch page'
                }
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyze structure
            analysis = {
                'success': True,
                'url': url,
                'title': soup.title.string if soup.title else 'Untitled',
                'meta_description': self._get_meta_description(soup),
                'structure': {
                    'total_elements': len(soup.find_all()),
                    'links': len(soup.find_all('a')),
                    'images': len(soup.find_all('img')),
                    'forms': len(soup.find_all('form')),
                    'tables': len(soup.find_all('table')),
                    'lists': len(soup.find_all(['ul', 'ol']))
                },
                'patterns': self._detect_patterns(soup),
                'containers': self._find_containers(soup),
                'suggested_fields': self._suggest_fields(soup)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze page structure: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_selectors(self, html: str, element_info: Dict) -> List[str]:
        """
        Suggest CSS selectors for an element.
        
        Args:
            html: HTML content
            element_info: Information about the selected element
            
        Returns:
            List of suggested selectors
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            selectors = []
            
            # Primary selector with ID
            if element_info.get('id'):
                selectors.append(f"#{element_info['id']}")
            
            # Class-based selectors
            if element_info.get('classes'):
                classes = element_info['classes']
                if isinstance(classes, list):
                    # Single class selector
                    for cls in classes:
                        selectors.append(f".{cls}")
                    # Combined class selector
                    if len(classes) > 1:
                        selectors.append('.' + '.'.join(classes))
            
            # Tag with attributes
            tag = element_info.get('tag', 'div')
            if element_info.get('attributes'):
                for attr, value in element_info['attributes'].items():
                    if attr not in ['class', 'id']:
                        selectors.append(f"{tag}[{attr}='{value}']")
            
            # Contextual selectors
            if element_info.get('parent_class'):
                parent_class = element_info['parent_class']
                selectors.append(f".{parent_class} {tag}")
                if element_info.get('classes'):
                    selectors.append(f".{parent_class} .{element_info['classes'][0]}")
            
            # Remove duplicates and return
            return list(dict.fromkeys(selectors))
            
        except Exception as e:
            self.logger.error(f"Failed to suggest selectors: {e}")
            return []
    
    def validate_selector(self, selector: str, html: str) -> Dict[str, Any]:
        """
        Validate a CSS selector against HTML content.
        
        Args:
            selector: CSS selector to validate
            html: HTML content to test against
            
        Returns:
            Validation results
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to find elements with selector
            try:
                elements = soup.select(selector)
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Invalid selector syntax: {e}',
                    'count': 0
                }
            
            # Analyze results
            result = {
                'valid': len(elements) > 0,
                'count': len(elements),
                'selector': selector,
                'samples': []
            }
            
            # Get sample data from first 3 elements
            for elem in elements[:3]:
                sample = {
                    'text': elem.get_text(strip=True)[:100],
                    'tag': elem.name,
                    'classes': elem.get('class', []),
                    'attributes': dict(elem.attrs)
                }
                result['samples'].append(sample)
            
            # Calculate selector quality
            quality = self._calculate_selector_quality(selector, elements)
            result['quality'] = quality
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate selector: {e}")
            return {
                'valid': False,
                'error': str(e),
                'count': 0
            }
    
    def generate_template_from_selection(self, selections: Dict) -> Dict[str, Any]:
        """
        Generate a template from user selections.
        
        Args:
            selections: Dictionary containing selected elements
            
        Returns:
            Generated template
        """
        try:
            template = {
                'name': selections.get('name', f'template_{self._generate_timestamp()}'),
                'description': selections.get('description', 'Template created with Interactive Selector'),
                'version': '1.0.0',
                'selectors': {},
                'fetcher_config': {
                    'type': selections.get('fetcher_type', 'auto')
                },
                'validation_rules': {
                    'required_fields': []
                },
                'post_processing': []
            }
            
            # Process standalone fields
            if 'fields' in selections:
                for field in selections['fields']:
                    field_name = self._sanitize_field_name(field.get('label', 'field'))
                    template['selectors'][field_name] = {
                        'selector': field['selector'],
                        'type': 'text',
                        'auto_save': True,
                        'required': field.get('is_required', False)
                    }
                    
                    if field.get('is_required'):
                        template['validation_rules']['required_fields'].append(field_name)
                    
                    # Add fallback selectors if available
                    if field.get('fallback_selectors'):
                        template['selectors'][field_name]['fallback_selectors'] = field['fallback_selectors']
            
            # Process containers
            if 'containers' in selections:
                for container in selections['containers']:
                    container_name = self._sanitize_field_name(container.get('label', 'container'))
                    template['selectors'][container_name] = {
                        'selector': container['selector'],
                        'type': 'all',
                        'auto_save': True
                    }
                    
                    # Add sub-elements
                    if container.get('sub_elements'):
                        sub_selectors = {}
                        for sub_field in container['sub_elements']:
                            sub_name = self._sanitize_field_name(sub_field.get('label', 'field'))
                            sub_selectors[sub_name] = {
                                'selector': sub_field['selector'],
                                'type': 'text'
                            }
                        template['selectors'][container_name]['sub_elements'] = sub_selectors
            
            # Process actions (pagination)
            if 'actions' in selections:
                for action in selections['actions']:
                    if action.get('action_type') == 'pagination':
                        template['pagination'] = {
                            'enabled': True,
                            'next_selector': action['selector'],
                            'max_pages': 10
                        }
            
            # Add post-processing rules based on field types
            field_types = set()
            for field_data in selections.get('fields', []):
                field_types.add(field_data.get('element_type', 'text'))
            
            if 'price' in field_types:
                template['post_processing'].append({
                    'type': 'extract_number',
                    'field': 'price'
                })
            
            if 'date' in field_types:
                template['post_processing'].append({
                    'type': 'parse_date',
                    'field': 'date'
                })
            
            # Validate template
            validation = self.validator.validate_template(template)
            template['validation'] = validation
            
            return {
                'success': True,
                'template': template,
                'validation': validation
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate template: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_learning_corrections(self, corrections: Dict) -> bool:
        """
        Apply user corrections to improve future detection.
        
        Args:
            corrections: Dictionary of corrections
            
        Returns:
            Success status
        """
        try:
            domain = corrections.get('domain', 'general')
            
            if domain not in self.learning_data:
                self.learning_data[domain] = {
                    'corrections': [],
                    'patterns': {},
                    'confidence_adjustments': {}
                }
            
            # Store correction
            correction_entry = {
                'timestamp': self._generate_timestamp(),
                'type': corrections.get('type'),
                'original': corrections.get('original'),
                'corrected': corrections.get('corrected'),
                'context': corrections.get('context', {})
            }
            
            self.learning_data[domain]['corrections'].append(correction_entry)
            
            # Update patterns
            if corrections.get('type') == 'selector':
                pattern_key = corrections.get('pattern_key')
                if pattern_key:
                    self.learning_data[domain]['patterns'][pattern_key] = corrections.get('corrected')
            
            # Adjust confidence
            if corrections.get('confidence_adjustment'):
                element_type = corrections.get('element_type')
                adjustment = corrections.get('confidence_adjustment')
                self.learning_data[domain]['confidence_adjustments'][element_type] = adjustment
            
            self.logger.info(f"Applied learning correction for domain: {domain}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply learning corrections: {e}")
            return False
    
    def get_learning_suggestions(self, domain: str, context: Dict) -> List[Dict]:
        """
        Get suggestions based on learned patterns.
        
        Args:
            domain: Domain to get suggestions for
            context: Current context
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        if domain in self.learning_data:
            data = self.learning_data[domain]
            
            # Apply learned patterns
            for pattern_key, selector in data.get('patterns', {}).items():
                suggestions.append({
                    'type': 'learned_pattern',
                    'selector': selector,
                    'confidence': 0.8,
                    'source': 'user_correction'
                })
            
            # Apply confidence adjustments
            for element_type, adjustment in data.get('confidence_adjustments', {}).items():
                suggestions.append({
                    'type': 'confidence_adjustment',
                    'element_type': element_type,
                    'adjustment': adjustment
                })
        
        return suggestions
    
    # Helper methods
    
    def _get_meta_description(self, soup) -> str:
        """Extract meta description from soup."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        return ''
    
    def _detect_patterns(self, soup) -> Dict[str, Any]:
        """Detect common patterns in the page."""
        patterns = {
            'has_navigation': bool(soup.find(['nav', '[role="navigation"]'])),
            'has_header': bool(soup.find(['header', '[role="banner"]'])),
            'has_footer': bool(soup.find(['footer', '[role="contentinfo"]'])),
            'has_sidebar': bool(soup.find(['aside', '[role="complementary"]'])),
            'has_main_content': bool(soup.find(['main', '[role="main"]', 'article'])),
            'uses_semantic_html': False,
            'uses_microdata': bool(soup.find(attrs={'itemscope': True})),
            'uses_schema_org': bool(soup.find(attrs={'itemtype': re.compile('schema.org')}))
        }
        
        # Check for semantic HTML5 elements
        semantic_elements = ['article', 'section', 'nav', 'aside', 'header', 'footer', 'main']
        patterns['uses_semantic_html'] = any(soup.find(tag) for tag in semantic_elements)
        
        return patterns
    
    def _find_containers(self, soup) -> List[Dict]:
        """Find potential container elements."""
        containers = []
        
        # Common container patterns
        container_patterns = [
            {'selector': '[class*="grid"]', 'type': 'grid'},
            {'selector': '[class*="list"]', 'type': 'list'},
            {'selector': '[class*="container"]', 'type': 'container'},
            {'selector': '[class*="row"]', 'type': 'row'},
            {'selector': '[class*="items"]', 'type': 'items'},
            {'selector': 'ul li', 'type': 'list_items'},
            {'selector': 'article', 'type': 'article'},
            {'selector': '.product', 'type': 'product'},
            {'selector': '.card', 'type': 'card'}
        ]
        
        for pattern in container_patterns:
            elements = soup.select(pattern['selector'])
            if len(elements) >= 2:  # At least 2 similar elements
                containers.append({
                    'selector': pattern['selector'],
                    'type': pattern['type'],
                    'count': len(elements),
                    'sample': str(elements[0])[:200] if elements else ''
                })
        
        return containers
    
    def _suggest_fields(self, soup) -> List[Dict]:
        """Suggest potential data fields."""
        suggestions = []
        
        # Common field patterns
        field_patterns = [
            {'selector': 'h1, h2, h3', 'type': 'title', 'name': 'title'},
            {'selector': '[class*="price"]', 'type': 'price', 'name': 'price'},
            {'selector': '[class*="description"]', 'type': 'text', 'name': 'description'},
            {'selector': 'img', 'type': 'image', 'name': 'image'},
            {'selector': 'a[href]', 'type': 'link', 'name': 'link'},
            {'selector': 'time, [class*="date"]', 'type': 'date', 'name': 'date'},
            {'selector': '[class*="rating"]', 'type': 'rating', 'name': 'rating'},
            {'selector': '[class*="author"]', 'type': 'text', 'name': 'author'}
        ]
        
        for pattern in field_patterns:
            elements = soup.select(pattern['selector'])
            if elements:
                suggestions.append({
                    'selector': pattern['selector'],
                    'type': pattern['type'],
                    'name': pattern['name'],
                    'count': len(elements),
                    'sample': elements[0].get_text(strip=True)[:100] if elements else ''
                })
        
        return suggestions
    
    def _calculate_selector_quality(self, selector: str, elements: list) -> float:
        """Calculate quality score for a selector."""
        quality = 0.5  # Base quality
        
        # Bonus for specific selectors
        if '#' in selector:  # ID selector
            quality += 0.3
        elif '.' in selector:  # Class selector
            quality += 0.2
        elif '[' in selector:  # Attribute selector
            quality += 0.15
        
        # Penalty for too many elements
        if len(elements) > 100:
            quality -= 0.2
        elif len(elements) > 50:
            quality -= 0.1
        
        # Bonus for reasonable element count
        if 1 <= len(elements) <= 20:
            quality += 0.1
        
        return min(max(quality, 0), 1)  # Clamp between 0 and 1
    
    def _sanitize_field_name(self, name: str) -> str:
        """Sanitize field name for template."""
        # Remove special characters and spaces
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Convert to lowercase
        return sanitized.lower()
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp string."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')