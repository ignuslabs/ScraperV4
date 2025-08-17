"""Adaptive selector system for self-healing templates."""

from typing import Dict, Any, List, Optional, Tuple
import time

class AdaptiveSelector:
    """Self-healing selector system that adapts when selectors fail."""
    
    def __init__(self):
        self.fallback_attempts = {}
        self.success_history = {}
        self.learning_enabled = True
    
    def find_element_adaptive(self, page_content: Any, field_name: str, 
                            primary_selector: str, fallback_selectors: Optional[List[str]] = None) -> Dict[str, Any]:
        """Find element using adaptive selector strategy."""
        attempt_id = f"{field_name}_{int(time.time())}"
        selectors_tried = []
        
        # Try primary selector first
        result = self._try_selector(page_content, primary_selector, field_name)
        selectors_tried.append(primary_selector)
        
        if result['found']:
            self._record_success(field_name, primary_selector)
            return {
                'found': True,
                'value': result['value'],
                'selector_used': primary_selector,
                'attempt_id': attempt_id,
                'selectors_tried': selectors_tried
            }
        
        # Try fallback selectors if primary fails
        if fallback_selectors:
            for fallback_selector in fallback_selectors:
                result = self._try_selector(page_content, fallback_selector, field_name)
                selectors_tried.append(fallback_selector)
                
                if result['found']:
                    self._record_success(field_name, fallback_selector)
                    self._record_primary_failure(field_name, primary_selector)
                    
                    return {
                        'found': True,
                        'value': result['value'],
                        'selector_used': fallback_selector,
                        'primary_failed': True,
                        'attempt_id': attempt_id,
                        'selectors_tried': selectors_tried
                    }
        
        # Try intelligent fallback generation
        generated_selectors = self._generate_fallback_selectors(field_name, primary_selector)
        for generated_selector in generated_selectors:
            result = self._try_selector(page_content, generated_selector, field_name)
            selectors_tried.append(generated_selector)
            
            if result['found']:
                self._record_success(field_name, generated_selector)
                return {
                    'found': True,
                    'value': result['value'],
                    'selector_used': generated_selector,
                    'selector_generated': True,
                    'attempt_id': attempt_id,
                    'selectors_tried': selectors_tried
                }
        
        # No element found with any selector
        self._record_failure(field_name, selectors_tried)
        return {
            'found': False,
            'error': 'Element not found with any selector',
            'attempt_id': attempt_id,
            'selectors_tried': selectors_tried
        }
    
    def suggest_selector_improvements(self, field_name: str, failed_selector: str, 
                                    page_content: Any) -> List[Dict[str, Any]]:
        """Suggest improved selectors based on page analysis (stub implementation)."""
        suggestions = []
        
        # Analyze selector failure patterns
        failure_analysis = self._analyze_selector_failure(failed_selector, page_content)
        
        # Generate suggestions based on analysis
        if failure_analysis.get('likely_cause') == 'class_changed':
            suggestions.append({
                'selector': self._modify_selector_for_class_change(failed_selector),
                'reason': 'Adapted for potential class name changes',
                'confidence': 0.7
            })
        
        if failure_analysis.get('likely_cause') == 'structure_changed':
            suggestions.append({
                'selector': self._modify_selector_for_structure_change(failed_selector),
                'reason': 'Adapted for DOM structure changes',
                'confidence': 0.6
            })
        
        # Generic fallback suggestions
        suggestions.extend(self._generate_generic_fallbacks(failed_selector))
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)
    
    def learn_from_success(self, field_name: str, successful_selector: str, 
                          page_content: Any) -> None:
        """Learn from successful selector usage for future adaptations."""
        if not self.learning_enabled:
            return
        
        # Analyze why this selector worked
        success_features = self._extract_selector_features(successful_selector)
        
        # Store learning data
        if field_name not in self.success_history:
            self.success_history[field_name] = []
        
        self.success_history[field_name].append({
            'selector': successful_selector,
            'features': success_features,
            'timestamp': time.time(),
            'context': self._extract_page_context(page_content)
        })
        
        # Limit history size
        if len(self.success_history[field_name]) > 10:
            self.success_history[field_name] = self.success_history[field_name][-10:]
    
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get statistics about selector adaptations."""
        stats = {
            'total_fields_tracked': len(self.success_history),
            'fields_with_fallbacks': 0,
            'total_adaptations': 0,
            'success_rate': 0.0,
            'top_failing_selectors': [],
            'most_successful_patterns': []
        }
        
        # Calculate detailed statistics
        total_successes = 0
        total_attempts = 0
        
        for field_name, history in self.success_history.items():
            if len(history) > 1:
                stats['fields_with_fallbacks'] += 1
            
            total_successes += len(history)
            # Estimate total attempts (stub calculation)
            total_attempts += len(history) * 1.5
        
        if total_attempts > 0:
            stats['success_rate'] = total_successes / total_attempts
        
        return stats
    
    def _try_selector(self, page_content: Any, selector: str, field_name: str) -> Dict[str, Any]:
        """Try to find element with given selector using actual CSS extraction."""
        try:
            # Check if page_content has css method (Scrapling response)
            if not hasattr(page_content, 'css'):
                return {
                    'found': False,
                    'error': 'Invalid page content object'
                }
            
            # Try to extract using CSS selector
            elements = page_content.css(selector)
            
            if elements:
                # Extract text content from elements
                try:
                    # Handle pseudo-selectors
                    if selector.endswith('::text'):
                        # Get text content
                        if hasattr(elements, 'all'):
                            all_elements = elements.all
                            if all_elements:
                                value = ' '.join([elem.text for elem in all_elements if hasattr(elem, 'text')])
                            else:
                                value = ''
                        elif hasattr(elements, 'first'):
                            first = elements.first
                            value = first.text if first and hasattr(first, 'text') else ''
                        else:
                            value = str(elements)
                    else:
                        # Get first element's text by default
                        if hasattr(elements, 'first'):
                            first = elements.first
                            value = first.text if first and hasattr(first, 'text') else ''
                        elif hasattr(elements, 'all'):
                            all_elements = elements.all
                            if all_elements and len(all_elements) > 0:
                                value = all_elements[0].text if hasattr(all_elements[0], 'text') else str(all_elements[0])
                            else:
                                value = ''
                        else:
                            value = str(elements)
                    
                    if value:
                        return {
                            'found': True,
                            'value': value.strip() if isinstance(value, str) else value
                        }
                except Exception as e:
                    # Try to get some value even if text extraction fails
                    return {
                        'found': True,
                        'value': str(elements)
                    }
            
            return {
                'found': False,
                'error': 'No elements found'
            }
            
        except Exception as e:
            return {
                'found': False,
                'error': f'Selector failed: {str(e)}'
            }
    
    def _generate_fallback_selectors(self, field_name: str, original_selector: str) -> List[str]:
        """Generate intelligent fallback selectors."""
        fallbacks = []
        
        # Generate variations of the original selector
        if '.' in original_selector:
            # Try removing class specificity
            fallbacks.append(original_selector.split('.')[0])
        
        if ' ' in original_selector:
            # Try shorter paths
            parts = original_selector.split(' ')
            if len(parts) > 2:
                fallbacks.append(' '.join(parts[-2:]))
            if len(parts) > 1:
                fallbacks.append(parts[-1])
        
        # Try common patterns for the field name
        common_patterns = self._get_common_patterns_for_field(field_name)
        fallbacks.extend(common_patterns)
        
        return fallbacks[:5]  # Limit to top 5 fallbacks
    
    def _get_common_patterns_for_field(self, field_name: str) -> List[str]:
        """Get common selector patterns for field types."""
        patterns = {
            'title': ['h1', 'h2', '.title', '[data-title]', '.heading'],
            'price': ['.price', '.cost', '[data-price]', '.amount', '.value'],
            'description': ['.description', '.summary', '.content', 'p', '.text'],
            'image': ['img', '.image', '[data-image]', '.photo', '.picture'],
            'link': ['a', '.link', '[href]', '.url'],
            'date': ['.date', '.time', '[datetime]', '.published', '.created']
        }
        
        # Match field name to common patterns
        field_lower = field_name.lower()
        for pattern_type, selectors in patterns.items():
            if pattern_type in field_lower:
                return selectors
        
        return []
    
    def _record_success(self, field_name: str, selector: str) -> None:
        """Record successful selector usage."""
        if field_name not in self.success_history:
            self.success_history[field_name] = []
        
        # Update success record
        success_record = {
            'selector': selector,
            'timestamp': time.time(),
            'success': True
        }
        
        self.success_history[field_name].append(success_record)
    
    def _record_primary_failure(self, field_name: str, selector: str) -> None:
        """Record when primary selector fails."""
        # Track failure patterns for learning
        pass
    
    def _record_failure(self, field_name: str, selectors_tried: List[str]) -> None:
        """Record complete failure to find element."""
        # Track complete failures for analysis
        pass
    
    def _analyze_selector_failure(self, selector: str, page_content: Any) -> Dict[str, Any]:
        """Analyze why a selector might have failed (stub implementation)."""
        # DOM analysis logic can be enhanced with actual parsing if needed
        return {
            'likely_cause': 'structure_changed',
            'confidence': 0.6,
            'suggestions': []
        }
    
    def _modify_selector_for_class_change(self, selector: str) -> str:
        """Modify selector to handle class name changes."""
        # Remove class specificity, keep element type
        if '.' in selector:
            return selector.split('.')[0]
        return selector
    
    def _modify_selector_for_structure_change(self, selector: str) -> str:
        """Modify selector to handle DOM structure changes."""
        # Use descendant selector instead of child selector
        return selector.replace(' > ', ' ')
    
    def _generate_generic_fallbacks(self, selector: str) -> List[Dict[str, Any]]:
        """Generate generic fallback suggestions."""
        fallbacks = []
        
        # Try attribute-based selectors
        if '[' not in selector:
            fallbacks.append({
                'selector': f"{selector}[data-*]",
                'reason': 'Try attribute-based selection',
                'confidence': 0.4
            })
        
        return fallbacks
    
    def _extract_selector_features(self, selector: str) -> Dict[str, Any]:
        """Extract features from successful selectors for learning."""
        return {
            'has_id': '#' in selector,
            'has_class': '.' in selector,
            'has_attributes': '[' in selector,
            'depth': selector.count(' '),
            'specificity': len(selector)
        }
    
    def _extract_page_context(self, page_content: Any) -> Dict[str, Any]:
        """Extract context information from page for learning."""
        # Basic page context extraction - can be enhanced with deeper analysis
        return {
            'domain': 'unknown',
            'page_type': 'unknown',
            'content_length': 0
        }