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
        """Suggest improved selectors based on page analysis."""
        suggestions = []
        
        # Analyze selector failure patterns
        failure_analysis = self._analyze_selector_failure(failed_selector, page_content)
        likely_cause = failure_analysis.get('likely_cause')
        analysis_suggestions = failure_analysis.get('suggestions', [])
        
        # Generate suggestions based on analysis
        if likely_cause == 'class_changed':
            modified_selector = self._modify_selector_for_class_change(failed_selector)
            suggestions.append({
                'selector': modified_selector,
                'reason': 'Adapted for potential class name changes',
                'confidence': 0.8
            })
            
            # Add suggestions from failure analysis
            for suggestion in analysis_suggestions:
                suggestions.append({
                    'selector': suggestion,
                    'reason': 'Similar class pattern found',
                    'confidence': 0.7
                })
        
        elif likely_cause == 'id_changed':
            # Add ID-based suggestions
            for suggestion in analysis_suggestions:
                suggestions.append({
                    'selector': suggestion,
                    'reason': 'Similar ID pattern found',
                    'confidence': 0.7
                })
        
        elif likely_cause == 'structure_changed':
            modified_selector = self._modify_selector_for_structure_change(failed_selector)
            suggestions.append({
                'selector': modified_selector,
                'reason': 'Adapted for DOM structure changes',
                'confidence': 0.6
            })
            
            # Add structural suggestions from analysis
            for suggestion in analysis_suggestions:
                suggestions.append({
                    'selector': suggestion,
                    'reason': 'Simplified selector path',
                    'confidence': 0.6
                })
        
        elif likely_cause == 'selector_too_specific':
            # Add simplified suggestions
            for suggestion in analysis_suggestions:
                suggestions.append({
                    'selector': suggestion,
                    'reason': 'Less specific selector',
                    'confidence': 0.7
                })
        
        elif likely_cause == 'element_removed':
            # Look for alternative patterns for this field type
            field_patterns = self._get_common_patterns_for_field(field_name)
            for pattern in field_patterns:
                suggestions.append({
                    'selector': pattern,
                    'reason': f'Common pattern for {field_name} fields',
                    'confidence': 0.5
                })
        
        # Add intelligent fallback suggestions based on field name
        intelligent_fallbacks = self._generate_intelligent_fallbacks(field_name, failed_selector, page_content)
        suggestions.extend(intelligent_fallbacks)
        
        # Generic fallback suggestions
        generic_fallbacks = self._generate_generic_fallbacks(failed_selector)
        suggestions.extend(generic_fallbacks)
        
        # Remove duplicates and sort by confidence
        unique_suggestions = []
        seen_selectors = set()
        for suggestion in suggestions:
            if suggestion['selector'] not in seen_selectors:
                unique_suggestions.append(suggestion)
                seen_selectors.add(suggestion['selector'])
        
        return sorted(unique_suggestions, key=lambda x: x['confidence'], reverse=True)[:10]  # Limit to top 10
    
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
    
    def _generate_intelligent_fallbacks(self, field_name: str, failed_selector: str, page_content: Any) -> List[Dict[str, Any]]:
        """Generate intelligent fallback suggestions based on field type and page content."""
        suggestions = []
        
        try:
            # Get field-specific patterns
            field_patterns = self._get_common_patterns_for_field(field_name)
            
            # Test each pattern against the current page
            for pattern in field_patterns:
                if hasattr(page_content, 'css'):
                    elements = page_content.css(pattern)
                    if elements:
                        # Calculate confidence based on number of matches and field relevance
                        confidence = min(0.8, 0.3 + (len(elements) * 0.1))
                        suggestions.append({
                            'selector': pattern,
                            'reason': f'Field-specific pattern for {field_name}',
                            'confidence': confidence
                        })
            
            # Try data attributes for the field
            data_attrs = [
                f'[data-{field_name}]',
                f'[data-testid*="{field_name}"]',
                f'[data-cy*="{field_name}"]',
                f'[id*="{field_name}"]',
                f'[class*="{field_name}"]'
            ]
            
            for attr in data_attrs:
                if hasattr(page_content, 'css'):
                    try:
                        elements = page_content.css(attr)
                        if elements:
                            suggestions.append({
                                'selector': attr,
                                'reason': f'Data attribute pattern for {field_name}',
                                'confidence': 0.6
                            })
                    except:
                        continue
        
        except Exception:
            # Return empty list if analysis fails
            pass
        
        return suggestions
    
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
        """Analyze why a selector might have failed."""
        try:
            # Check if we have valid page content to analyze
            if not hasattr(page_content, 'css'):
                return {
                    'likely_cause': 'invalid_page_content',
                    'confidence': 0.9,
                    'suggestions': ['Ensure page content is properly loaded']
                }
            
            # Parse the selector to understand what we're looking for
            suggestions = []
            
            # Class-based selector analysis
            if '.' in selector:
                class_name = selector.split('.')[-1].split(':')[0].split('[')[0]
                # Check for similar class names
                similar_classes = page_content.css(f'[class*="{class_name[:4]}"]')
                if similar_classes:
                    suggestions.append(f'Try: [class*="{class_name[:4]}"]')
                    return {
                        'likely_cause': 'class_changed',
                        'confidence': 0.8,
                        'suggestions': suggestions
                    }
            
            # ID-based selector analysis  
            if '#' in selector:
                element_id = selector.split('#')[-1].split(':')[0].split('[')[0]
                # Check for similar IDs
                similar_ids = page_content.css(f'[id*="{element_id[:4]}"]')
                if similar_ids:
                    suggestions.append(f'Try: [id*="{element_id[:4]}"]')
                    return {
                        'likely_cause': 'id_changed',
                        'confidence': 0.8,
                        'suggestions': suggestions
                    }
            
            # Element-based selector analysis
            element_type = selector.split('.')[0].split('#')[0].split(':')[0].split('[')[0].strip()
            if element_type and element_type.isalpha():
                # Check if elements of this type exist
                elements = page_content.css(element_type)
                if elements:
                    suggestions.append(f'Try: {element_type}')
                    return {
                        'likely_cause': 'selector_too_specific',
                        'confidence': 0.7,
                        'suggestions': suggestions
                    }
            
            # Check for common alternative patterns
            if selector.count(' ') > 2:
                # Try shorter paths
                parts = selector.split(' ')
                suggestions.append(' '.join(parts[-2:]))
                suggestions.append(parts[-1])
                return {
                    'likely_cause': 'structure_changed',
                    'confidence': 0.6,
                    'suggestions': suggestions
                }
            
            # Default case - element completely missing
            return {
                'likely_cause': 'element_removed',
                'confidence': 0.5,
                'suggestions': ['Element may no longer exist on the page']
            }
            
        except Exception as e:
            return {
                'likely_cause': 'analysis_error',
                'confidence': 0.3,
                'suggestions': [f'Analysis failed: {str(e)}']
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