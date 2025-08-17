"""Shared pytest fixtures for test suite."""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_valid_template():
    """Sample valid template for testing across multiple test modules."""
    return {
        "name": "test_template",
        "description": "Test template for unit tests",
        "selectors": {
            "title": "h1::text",
            "description": ".description::text",
            "price": ".price::text",
            "links": "a::attr(href)",
            "images": "img::attr(src)"
        },
        "post_processing": [
            {"type": "trim", "field": "title"},
            {"type": "lowercase", "field": "description"}
        ],
        "stealth_mode": True
    }


@pytest.fixture
def sample_invalid_template():
    """Sample invalid template missing required fields."""
    return {
        "name": "invalid_template",
        "description": "Invalid template for testing"
        # Missing selectors field
    }


@pytest.fixture
def sample_empty_template():
    """Template with empty selectors."""
    return {
        "name": "empty_template",
        "description": "Template with empty selectors",
        "selectors": {}
    }


@pytest.fixture
def sample_complex_template():
    """Complex template with multiple selector types and configurations."""
    return {
        "name": "complex_template",
        "description": "Complex template with various selector types",
        "selectors": {
            "title": "h1::text",
            "subtitle": "h2::text",
            "content": ".content::text",
            "links": "a::attr(href)",
            "images": "img::attr(src)",
            "metadata": ".meta::attr(content)",
            "tags": ".tag::text"
        },
        "fallback_selectors": {
            "titles": {
                "title": "h2::text",
                "subtitle": "h3::text"
            }
        },
        "post_processing": [
            {"type": "trim", "field": "title"},
            {"type": "unique", "field": "links"},
            {"type": "limit", "field": "images", "max_items": 5}
        ],
        "stealth_mode": False
    }


@pytest.fixture
def mock_successful_selector_results():
    """Mock successful selector test results."""
    return {
        "success": True,
        "url": "https://example.com",
        "template_name": "test_template",
        "selector_results": {
            "title": {
                "selector": "h1::text",
                "found": True,
                "element_count": 1,
                "sample_value": "Sample Product Title",
                "error": None
            },
            "description": {
                "selector": ".description::text",
                "found": True,
                "element_count": 1,
                "sample_value": "This is a sample product description with some details",
                "error": None
            },
            "price": {
                "selector": ".price::text",
                "found": True,
                "element_count": 1,
                "sample_value": "$99.99",
                "error": None
            },
            "links": {
                "selector": "a::attr(href)",
                "found": True,
                "element_count": 5,
                "sample_value": "https://example.com/product/1",
                "error": None
            },
            "images": {
                "selector": "img::attr(src)",
                "found": True,
                "element_count": 3,
                "sample_value": "https://example.com/images/product1.jpg",
                "error": None
            }
        },
        "statistics": {
            "total_selectors": 5,
            "successful_selectors": 5,
            "failed_selectors": 0,
            "success_rate": 100.0
        },
        "errors": None
    }


@pytest.fixture
def mock_partial_selector_results():
    """Mock partially successful selector test results."""
    return {
        "success": False,
        "url": "https://example.com",
        "template_name": "test_template",
        "selector_results": {
            "title": {
                "selector": "h1::text",
                "found": True,
                "element_count": 1,
                "sample_value": "Sample Product Title",
                "error": None
            },
            "description": {
                "selector": ".description::text",
                "found": True,
                "element_count": 1,
                "sample_value": "Sample description",
                "error": None
            },
            "price": {
                "selector": ".price::text",
                "found": False,
                "element_count": 0,
                "sample_value": None,
                "error": "No elements found matching this selector"
            },
            "links": {
                "selector": "a::attr(href)",
                "found": True,
                "element_count": 2,
                "sample_value": "https://example.com/link1",
                "error": None
            },
            "images": {
                "selector": "img::attr(src)",
                "found": False,
                "element_count": 0,
                "sample_value": None,
                "error": "No elements found matching this selector"
            }
        },
        "statistics": {
            "total_selectors": 5,
            "successful_selectors": 3,
            "failed_selectors": 2,
            "success_rate": 60.0
        },
        "errors": ["Field 'price': No elements found matching this selector", 
                   "Field 'images': No elements found matching this selector"]
    }


@pytest.fixture
def mock_successful_scraping_result():
    """Mock successful scraping result."""
    return {
        "url": "https://example.com",
        "status": "success",
        "template_name": "test_template",
        "data": {
            "title": "Sample Product Title",
            "description": "This is a comprehensive product description with details about the item",
            "price": "$99.99",
            "links": [
                "https://example.com/product/1",
                "https://example.com/product/2",
                "https://example.com/category/products"
            ],
            "images": [
                "https://example.com/images/product1.jpg",
                "https://example.com/images/product2.jpg"
            ]
        },
        "items_count": 3
    }


@pytest.fixture
def mock_failed_scraping_result():
    """Mock failed scraping result."""
    return {
        "url": "https://example.com",
        "status": "failed",
        "template_name": "test_template",
        "error": "Failed to extract data from the page",
        "data": {},
        "items_count": 0
    }


@pytest.fixture
def mock_empty_scraping_result():
    """Mock empty scraping result (successful but no data)."""
    return {
        "url": "https://example.com",
        "status": "success",
        "template_name": "test_template",
        "data": {},
        "items_count": 0
    }


@pytest.fixture
def mock_large_scraping_result():
    """Mock scraping result with large data for truncation testing."""
    return {
        "url": "https://example.com",
        "status": "success",
        "template_name": "test_template",
        "data": {
            "title": "Product Title",
            "long_description": "A" * 500,  # Very long description
            "content": "B" * 1000,  # Very long content
            "items": [f"item_{i}" for i in range(100)],  # Many items
            "tags": [f"tag_{i}" for i in range(50)]  # Many tags
        },
        "items_count": 100
    }


@pytest.fixture
def mock_response_object():
    """Mock response object for testing page fetching."""
    mock_response = Mock()
    mock_response.url = "https://example.com"
    mock_response.status_code = 200
    mock_response.status = 200
    
    # Mock CSS selector method
    def mock_css_selector(selector):
        mock_elements = Mock()
        
        # Simulate different selector behaviors
        if "h1" in selector:
            mock_element = Mock()
            mock_element.text = "Sample Title"
            mock_element.attrs = {"class": "title"}
            mock_elements.all = [mock_element]
            mock_elements.first = mock_element
            mock_elements.text = "Sample Title"
            return mock_elements
        elif "description" in selector:
            mock_element = Mock()
            mock_element.text = "Sample description"
            mock_elements.all = [mock_element]
            mock_elements.first = mock_element
            return mock_elements
        elif "a" in selector and "href" in selector:
            mock_elements_list = []
            for i in range(3):
                mock_element = Mock()
                mock_element.attrs = {"href": f"https://example.com/link{i+1}"}
                mock_elements_list.append(mock_element)
            mock_elements.all = mock_elements_list
            mock_elements.first = mock_elements_list[0] if mock_elements_list else None
            return mock_elements
        else:
            # Return empty results for other selectors
            mock_elements.all = []
            mock_elements.first = None
            return mock_elements
    
    mock_response.css = mock_css_selector
    return mock_response


@pytest.fixture
def mock_template_scraper():
    """Mock TemplateScraper instance with common behaviors."""
    mock_scraper = Mock()
    
    # Default successful validation
    mock_scraper.validate_template.return_value = {
        "valid": True,
        "errors": []
    }
    
    # Default successful selector testing
    mock_scraper.test_selectors.return_value = {
        "success": True,
        "selector_results": {
            "title": {"found": True, "element_count": 1, "sample_value": "Test Title"}
        },
        "statistics": {
            "total_selectors": 1,
            "successful_selectors": 1,
            "success_rate": 100.0
        }
    }
    
    # Default successful scraping
    mock_scraper.scrape.return_value = {
        "status": "success",
        "data": {"title": "Test Title"},
        "items_count": 1
    }
    
    return mock_scraper


@pytest.fixture
def mock_url_validation():
    """Mock URL validation results."""
    def _mock_validation(url: str, valid: bool = True, error: str = None):
        if valid:
            return {
                "valid": True,
                "url": url,
                "domain": url.split('/')[2] if '//' in url else url
            }
        else:
            return {
                "valid": False,
                "error": error or "Invalid URL format"
            }
    return _mock_validation


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return {
        "valid": [
            "https://example.com",
            "http://example.com",
            "https://subdomain.example.com/path?param=value",
            "https://example.com:8080/api/endpoint"
        ],
        "invalid": [
            "",
            "not-a-url",
            "example.com",  # Missing protocol
            "ftp://example.com",  # Wrong protocol
            "https://",  # Incomplete URL
            "javascript:alert('xss')"  # Potentially malicious
        ]
    }


@pytest.fixture(autouse=True)
def reset_mocks():
    """Automatically reset all mocks after each test."""
    yield
    # Any cleanup code can go here if needed


# Parametrized fixtures for testing multiple scenarios
@pytest.fixture(params=[
    {"success": True, "count": 5, "rate": 100.0},
    {"success": True, "count": 3, "rate": 75.0},
    {"success": False, "count": 1, "rate": 25.0},
    {"success": False, "count": 0, "rate": 0.0}
])
def selector_test_scenarios(request):
    """Parametrized fixture for different selector test scenarios."""
    return request.param


@pytest.fixture(params=[
    "https://example.com",
    "https://test.example.com/products",
    "https://api.example.com/v1/items?page=1"
])
def test_urls(request):
    """Parametrized fixture for different test URLs."""
    return request.param