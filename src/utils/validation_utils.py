"""URL and data validation utilities."""

import re
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse, urljoin
from scrapling.fetchers import StealthyFetcher
from src.core.config import config
import logging
logging.getLogger("scrapling").setLevel(logging.DEBUG)

def validate_url(url: str) -> Dict[str, Any]:
    """Validate URL format and accessibility."""
    if not url or not isinstance(url, str):
        return {
            "valid": False,
            "error": "URL must be a non-empty string"
        }
    
    url = url.strip()
    
    # Basic URL format validation
    if not url.startswith(('http://', 'https://')):
        return {
            "valid": False,
            "error": "URL must start with http:// or https://"
        }
    
    try:
        parsed = urlparse(url)
        
        if not parsed.netloc:
            return {
                "valid": False,
                "error": "URL must have a valid domain"
            }
        
        return {
            "valid": True,
            "url": url,
            "domain": parsed.netloc,
            "scheme": parsed.scheme,
            "path": parsed.path,
            "query": parsed.query,
            "fragment": parsed.fragment
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"URL parsing error: {str(e)}"
        }

def validate_selector(selector: str, selector_type: str = "css") -> Dict[str, Any]:
    """Validate CSS or XPath selector syntax."""
    if not selector or not isinstance(selector, str):
        return {
            "valid": False,
            "error": "Selector must be a non-empty string"
        }
    
    selector = selector.strip()
    
    if selector_type.lower() == "css":
        return _validate_css_selector(selector)
    elif selector_type.lower() == "xpath":
        return _validate_xpath_selector(selector)
    else:
        return {
            "valid": False,
            "error": f"Unsupported selector type: {selector_type}"
        }

def validate_scraping_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate scraping configuration parameters."""
    errors = []
    warnings = []
    
    # Validate timeout
    timeout = config.get('timeout')
    if timeout is not None:
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("Timeout must be a positive number")
    
    # Validate max_retries
    max_retries = config.get('max_retries')
    if max_retries is not None:
        if not isinstance(max_retries, int) or max_retries < 0:
            errors.append("Max retries must be a non-negative integer")
    
    # Validate delay_range
    delay_range = config.get('delay_range')
    if delay_range is not None:
        if not isinstance(delay_range, (list, tuple)) or len(delay_range) != 2:
            errors.append("Delay range must be a tuple/list of two numbers")
        elif not all(isinstance(x, (int, float)) for x in delay_range):
            errors.append("Delay range values must be numbers")
        elif delay_range[0] >= delay_range[1]:
            errors.append("Delay range minimum must be less than maximum")
    
    # Validate user_agent
    user_agent = config.get('user_agent')
    if user_agent is not None:
        if not isinstance(user_agent, str) or not user_agent.strip():
            errors.append("User agent must be a non-empty string")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_template_data(template: Dict[str, Any]) -> Dict[str, Any]:
    """Validate template data structure."""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['name', 'selectors']
    for field in required_fields:
        if field not in template:
            errors.append(f"Missing required field: {field}")
    
    # Validate name
    name = template.get('name')
    if name and not isinstance(name, str):
        errors.append("Template name must be a string")
    elif name and not name.strip():
        errors.append("Template name cannot be empty")
    
    # Validate selectors
    selectors = template.get('selectors')
    if selectors is not None:
        if not isinstance(selectors, dict):
            errors.append("Selectors must be a dictionary")
        elif not selectors:
            warnings.append("No selectors defined")
        else:
            for field_name, selector in selectors.items():
                if not isinstance(selector, str):
                    errors.append(f"Selector for '{field_name}' must be a string")
                elif not selector.strip():
                    errors.append(f"Selector for '{field_name}' cannot be empty")
    
    # Validate fallback_selectors if present
    fallback_selectors = template.get('fallback_selectors')
    if fallback_selectors is not None:
        if not isinstance(fallback_selectors, dict):
            errors.append("Fallback selectors must be a dictionary")
    
    # Validate validation_rules if present
    validation_rules = template.get('validation_rules')
    if validation_rules is not None:
        if not isinstance(validation_rules, dict):
            errors.append("Validation rules must be a dictionary")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def validate_job_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate job parameters."""
    errors = []
    warnings = []
    
    # Validate max_pages if present
    max_pages = parameters.get('max_pages')
    if max_pages is not None:
        if not isinstance(max_pages, int) or max_pages <= 0:
            errors.append("Max pages must be a positive integer")
    
    # Validate custom_headers if present
    custom_headers = parameters.get('custom_headers')
    if custom_headers is not None:
        if not isinstance(custom_headers, dict):
            errors.append("Custom headers must be a dictionary")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    if not filename:
        return "untitled"
    
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove excessive dots and spaces
    sanitized = re.sub(r'\.{2,}', '.', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Trim and ensure reasonable length
    sanitized = sanitized.strip()[:255]
    
    return sanitized or "untitled"

def validate_data_structure(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Validate scraped data structure."""
    if data is None:
        return {
            "valid": False,
            "error": "Data is None"
        }
    
    if isinstance(data, dict):
        return {
            "valid": True,
            "type": "object",
            "fields": list(data.keys()),
            "field_count": len(data),
            "item_count": 1
        }
    elif isinstance(data, list):
        if not data:
            return {
                "valid": True,
                "type": "array",
                "item_count": 0,
                "fields": []
            }
        
        # Analyze first item to determine structure
        first_item = data[0]
        if isinstance(first_item, dict):
            all_fields = set()
            for item in data:
                if isinstance(item, dict):
                    all_fields.update(item.keys())
            
            return {
                "valid": True,
                "type": "array",
                "item_count": len(data),
                "fields": list(all_fields),
                "field_count": len(all_fields),
                "consistent_structure": all(isinstance(item, dict) for item in data)
            }
        else:
            return {
                "valid": True,
                "type": "array",
                "item_count": len(data),
                "fields": [],
                "item_types": list(set(type(item).__name__ for item in data))
            }
    else:
        return {
            "valid": False,
            "error": f"Unsupported data type: {type(data).__name__}"
        }

def _validate_css_selector(selector: str) -> Dict[str, Any]:
    """Validate CSS selector syntax."""
    # Basic CSS selector validation
    invalid_patterns = [
        r'[{}]',  # Curly braces
        r'^\s*$', # Empty or whitespace only
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, selector):
            return {
                "valid": False,
                "error": "Invalid CSS selector syntax"
            }
    
    # Check for balanced brackets
    if selector.count('[') != selector.count(']'):
        return {
            "valid": False,
            "error": "Unbalanced brackets in CSS selector"
        }
    
    if selector.count('(') != selector.count(')'):
        return {
            "valid": False,
            "error": "Unbalanced parentheses in CSS selector"
        }
    
    return {"valid": True}

def _validate_xpath_selector(selector: str) -> Dict[str, Any]:
    """Validate XPath selector syntax."""
    # Basic XPath validation
    if not selector.startswith(('/', './/', '@')):
        return {
            "valid": False,
            "error": "XPath selector must start with '/', './/', or '@'"
        }
    
    # Check for balanced brackets
    if selector.count('[') != selector.count(']'):
        return {
            "valid": False,
            "error": "Unbalanced brackets in XPath selector"
        }
    
    if selector.count('(') != selector.count(')'):
        return {
            "valid": False,
            "error": "Unbalanced parentheses in XPath selector"
        }
    
    return {"valid": True}

def test_selector(url: str, selector: str, selector_type: str = "css") -> Dict[str, Any]:
    """Test a selector against a URL by fetching the content and testing the selector.
    
    Args:
        url: URL to fetch and test the selector against
        selector: CSS or XPath selector to test
        selector_type: Type of selector ("css" or "xpath")
        
    Returns:
        Dictionary containing validation results:
        - matches: Whether selector found any elements
        - count: Number of matching elements
        - sample_data: Sample data from matched elements (first 3)
        - error: Any error encountered
        - message: Success or informational message
    """
    # First validate the URL format
    url_validation = validate_url(url)
    if not url_validation["valid"]:
        return {
            "matches": False,
            "count": 0,
            "error": f"Invalid URL: {url_validation.get('error')}",
            "sample_data": []
        }
    
    # Validate the selector syntax
    selector_validation = validate_selector(selector, selector_type)
    if not selector_validation["valid"]:
        return {
            "matches": False,
            "count": 0,
            "error": f"Invalid selector: {selector_validation.get('error')}",
            "sample_data": []
        }
    
    # Only CSS selectors are fully supported with Scrapling
    if selector_type.lower() != "css":
        return {
            "matches": False,
            "count": 0,
            "error": f"Selector type '{selector_type}' is not supported. Only 'css' selectors are supported.",
            "sample_data": []
        }
    
    try:
        # Fetch the URL using StealthyFetcher's static fetch method
        response = StealthyFetcher.fetch(
            url,
            timeout=config.scrapling.timeout,
            headless=True,
            network_idle=True
        )
        
        if not response:
            return {
                "matches": False,
                "count": 0,
                "error": "Failed to fetch URL - no response received",
                "sample_data": []
            }
        
        # Check response status
        if hasattr(response, 'status') and response.status != 200:
            return {
                "matches": False,
                "count": 0,
                "error": f"HTTP {response.status} error when fetching URL",
                "sample_data": []
            }
        
        # Test the CSS selector
        elements = response.css(selector)
        
        if not elements:
            return {
                "matches": False,
                "count": 0,
                "sample_data": [],
                "message": "Selector is valid but no elements were found on the page"
            }
        
        # Get element count
        element_count = 0
        sample_data = []
        
        # Check if elements is iterable (multiple elements)
        try:
            # Try to iterate through elements
            element_list = list(elements)
            element_count = len(element_list)
            
            # Extract sample data from first 3 elements
            for elem in element_list[:3]:
                sample_element = _extract_element_data(elem)
                if sample_element:
                    sample_data.append(sample_element)
                    
        except (TypeError, AttributeError):
            # Single element or special case
            element_count = 1
            sample_element = _extract_element_data(elements)
            if sample_element:
                sample_data.append(sample_element)
        
        return {
            "matches": element_count > 0,
            "count": element_count,
            "sample_data": sample_data,
            "message": f"Successfully tested selector and found {element_count} matching element{'s' if element_count != 1 else ''}"
        }
            
    except Exception as e:
        # Handle various error types with specific messages
        error_msg = str(e)
        
        if "timeout" in error_msg.lower():
            error_msg = f"Request timeout - unable to fetch URL within {config.scrapling.timeout} seconds"
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            error_msg = "Network error - unable to connect to URL"
        elif "dns" in error_msg.lower() or "resolve" in error_msg.lower():
            error_msg = "DNS resolution error - unable to resolve domain name"
        elif "ssl" in error_msg.lower() or "certificate" in error_msg.lower():
            error_msg = "SSL certificate error - unable to establish secure connection"
        elif "css" in error_msg.lower() and "selector" in error_msg.lower():
            error_msg = f"Invalid CSS selector syntax: {error_msg}"
        else:
            error_msg = f"Error testing selector: {error_msg}"
        
        return {
            "matches": False,
            "count": 0,
            "error": error_msg,
            "sample_data": []
        }


def _extract_element_data(element) -> Optional[Dict[str, Any]]:
    """Extract data from a single element for sample data.
    
    Args:
        element: Scrapling element object
        
    Returns:
        Dictionary with element data or None if extraction fails
    """
    try:
        element_data = {
            "tag": getattr(element, 'tag', 'unknown'),
            "text": "",
            "attributes": {},
            "html": ""
        }
        
        # Extract text content
        if hasattr(element, 'text') and element.text:
            element_data["text"] = element.text.strip()[:200]  # Limit text length
        
        # Extract attributes
        if hasattr(element, 'attrib') and element.attrib:
            # Limit attributes to common useful ones and truncate values
            common_attrs = ['id', 'class', 'href', 'src', 'alt', 'title', 'data-*']
            for attr, value in element.attrib.items():
                if (attr in ['id', 'class', 'href', 'src', 'alt', 'title'] or 
                    attr.startswith('data-')):
                    element_data["attributes"][attr] = str(value)[:100]  # Limit attribute value length
        
        # Extract HTML content (limited)
        if hasattr(element, 'html_content'):
            html_content = element.html_content
            if html_content:
                element_data["html"] = str(html_content)[:300]  # Limit HTML length
        
        return element_data
        
    except Exception:
        # Return minimal data if extraction fails
        return {
            "tag": "unknown",
            "text": "",
            "attributes": {},
            "html": "",
            "error": "Failed to extract element data"
        }