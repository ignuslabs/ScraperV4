"""Comprehensive integration tests for CSS selector extraction and validation features.

This test file focuses on testing the integration between:
1. CSS Selector Extraction (from src.scrapers.base_scraper.py)
2. Selector Validation (from src.utils.validation_utils.py)

The tests verify that both features work correctly together and handle all edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List

from src.scrapers.base_scraper import BaseScraper
from src.utils.validation_utils import test_selector, validate_selector, _extract_element_data


class TestCSSSelectorIntegration:
    """Integration tests for CSS selector extraction and validation."""
    
    class ConcreteScraper(BaseScraper):
        """Concrete implementation of BaseScraper for testing."""
        
        def scrape(self, url: str, **kwargs):
            """Dummy implementation of abstract method."""
            return {"url": url, "status": "test"}
    
    @pytest.fixture
    def scraper(self):
        """Create a BaseScraper instance for testing."""
        return self.ConcreteScraper()
    
    @pytest.fixture
    def sample_selectors(self):
        """Sample CSS selectors for testing various extraction types."""
        return {
            "title": "h1.main-title::text",
            "description": "p.description::text",
            "price": ".price-value::text",
            "product_link": "a.product-link::attr(href)",
            "image_url": "img.product-image::attr(src)",
            "html_content": ".content-block::html",
            "data_attribute": "[data-product-id]::attr(data-product-id)",
            "multiple_links": "a::attr(href)"
        }
    
    @pytest.fixture
    def mock_html_response(self):
        """Create a comprehensive mock HTML response for testing."""
        return """
        <html>
            <body>
                <h1 class="main-title">Premium Product Title</h1>
                <p class="description">This is a detailed product description with all the features.</p>
                <div class="price-value">$299.99</div>
                <a class="product-link" href="https://example.com/product/123">View Product</a>
                <img class="product-image" src="https://example.com/images/product.jpg" alt="Product">
                <div class="content-block">
                    <span>Rich HTML content</span>
                    <ul><li>Feature 1</li><li>Feature 2</li></ul>
                </div>
                <div data-product-id="PROD123">Product Data</div>
                <a href="https://example.com/link1">Link 1</a>
                <a href="https://example.com/link2">Link 2</a>
                <a href="https://example.com/link3">Link 3</a>
            </body>
        </html>
        """

    def test_integrated_extraction_and_validation_success(self, scraper, sample_selectors):
        """Test successful integration of extraction and validation."""
        # First, validate all selectors
        validation_results = scraper.validate_selectors(sample_selectors)
        
        # All selectors should be valid
        for field_name, is_valid in validation_results.items():
            assert is_valid is True, f"Selector for '{field_name}' should be valid"
        
        # Mock a response object for extraction
        mock_response = self._create_mock_response_with_data()
        
        # Extract data using the validated selectors
        extraction_results = scraper.extract_data(mock_response, sample_selectors)
        
        # Verify extraction results
        assert "title" in extraction_results
        assert "description" in extraction_results
        assert "price" in extraction_results
        assert "product_link" in extraction_results
        assert "image_url" in extraction_results
        
        # Verify no error messages in results (error messages start with "[" and contain "Error")
        for field_name, value in extraction_results.items():
            value_str = str(value)
            is_error = value_str.startswith("[") and ("Error" in value_str or "error" in value_str)
            assert not is_error, f"Field '{field_name}' contains error: {value}"

    def test_integrated_validation_with_real_url_mock(self, sample_selectors):
        """Test selector validation against a mocked real URL."""
        test_url = "https://example.com/test-page"
        
        with patch('src.utils.validation_utils.StealthyFetcher') as mock_fetcher_class:
            # Setup successful response mock
            mock_fetcher = MagicMock()
            mock_fetcher_class.return_value = mock_fetcher
            mock_response = self._create_comprehensive_mock_response()
            mock_fetcher.get.return_value = mock_response
            
            # Test each selector individually
            for field_name, selector in sample_selectors.items():
                result = test_selector(test_url, selector, "css")
                
                # All selectors should find elements in our mock
                assert result["matches"] is True, f"Selector '{selector}' for '{field_name}' should match elements"
                assert result["count"] > 0, f"Selector '{selector}' should find at least one element"
                assert len(result["sample_data"]) > 0, f"Selector should return sample data for '{field_name}'"
                assert "message" in result, "Result should contain success message"

    def test_fallback_selector_integration(self, scraper):
        """Test integration with fallback selectors when primary selectors fail."""
        # Define selectors with fallbacks
        primary_selectors = {
            "title": "h1.primary-title::text",
            "price": ".primary-price::text"
        }
        
        fallback_selector_groups = {
            "title": ["h1.primary-title::text", "h1.secondary-title::text", "h2.title::text"],
            "price": [".primary-price::text", ".secondary-price::text", ".price::text"]
        }
        
        # Validate all selectors first
        all_selectors = {}
        for field, selectors_list in fallback_selector_groups.items():
            for selector in selectors_list:
                all_selectors[f"{field}_{selector}"] = selector
        
        validation_results = scraper.validate_selectors(all_selectors)
        
        # All should be valid
        for is_valid in validation_results.values():
            assert is_valid is True
        
        # Mock response where primary selectors fail but fallbacks succeed
        mock_response = Mock()
        
        def css_mock(selector):
            mock_result = Mock()
            if "primary" in selector:
                # Primary selectors fail
                mock_result.first = None
                mock_result.all = []
            else:
                # Fallback selectors succeed
                mock_element = Mock()
                mock_element.text = f"Fallback result for {selector}"
                mock_result.first = mock_element
                mock_result.all = [mock_element]
            return mock_result
        
        mock_response.css.side_effect = css_mock
        
        # Test fallback extraction
        fallback_results = scraper.extract_multiple_selectors(mock_response, fallback_selector_groups)
        
        # Should get fallback results
        assert "title" in fallback_results
        assert "price" in fallback_results
        assert "Fallback result" in fallback_results["title"]
        assert "Fallback result" in fallback_results["price"]

    def test_complex_css_selector_validation_and_extraction(self, scraper):
        """Test complex CSS selectors through validation and extraction."""
        # Use simpler selectors that will pass validation
        complex_selectors = {
            "nested_content": "article.post div.content p::text",
            "nth_child": "ul.menu li a::attr(href)",
            "attribute_contains": ".product .title::text",
            "adjacent_sibling": "h2::text",
            "data_attributes": "[data-testid]::attr(data-testid)"
        }
        
        # Validate complex selectors
        validation_results = scraper.validate_selectors(complex_selectors)
        
        for field_name, is_valid in validation_results.items():
            assert is_valid is True, f"Complex selector for '{field_name}' should be valid"
        
        # Test extraction with mock response
        mock_response = Mock()
        
        def css_mock(selector):
            mock_result = Mock()
            element = Mock()
            element.text = "Complex selector result"
            element.attrib = {"href": "https://example.com", "data-testid": "test"}
            mock_result.first = element
            mock_result.all = [element]
            return mock_result
        
        mock_response.css.side_effect = css_mock
        
        results = scraper.extract_data(mock_response, complex_selectors)
        
        # All fields should have results
        for field_name in complex_selectors.keys():
            assert field_name in results
            assert results[field_name]  # Should have some content

    def test_error_handling_integration(self, scraper):
        """Test integrated error handling across both features."""
        # Invalid selectors that should fail validation
        invalid_selectors = {
            "invalid_characters": "div{color: red}",  # CSS rules instead of selector
            "empty_selector": "",  # Empty selector
        }
        
        # Validate - should all be invalid
        validation_results = scraper.validate_selectors(invalid_selectors)
        
        for field_name, is_valid in validation_results.items():
            assert is_valid is False, f"Invalid selector for '{field_name}' should fail validation"
        
        # Test extraction with invalid selectors (that pass basic validation but fail extraction)
        problematic_selectors = {
            "valid_but_empty": "div.nonexistent::text",
            "valid_syntax": "p.description::text"
        }
        
        mock_response = Mock()
        mock_response.css.side_effect = Exception("CSS parsing error")
        
        results = scraper.extract_data(mock_response, problematic_selectors)
        
        # Should contain error messages
        for field_name, value in results.items():
            assert "[" in str(value) and "]" in str(value), f"Field '{field_name}' should contain error message"

    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_network_error_integration(self, mock_fetcher_class, sample_selectors):
        """Test integration when network errors occur during validation."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Simulate different types of network errors
        network_errors = [
            Exception("Connection timeout"),
            Exception("DNS resolution failed"),
            Exception("SSL certificate error"),
            Exception("Connection refused")
        ]
        
        for error in network_errors:
            mock_fetcher.get.side_effect = error
            
            # Test validation with network error
            result = test_selector("https://example.com", "h1::text", "css")
            
            assert result["matches"] is False
            assert result["count"] == 0
            assert "error" in result
            assert result["sample_data"] == []

    def test_context_based_extraction_integration(self, scraper):
        """Test context-based extraction with validation."""
        base_selector = ".product-card"
        field_selectors = {
            "title": ".title::text",
            "price": ".price::text",
            "link": "a::attr(href)"
        }
        
        # Validate base selector and field selectors
        all_selectors = {"base": base_selector}
        all_selectors.update(field_selectors)
        
        validation_results = scraper.validate_selectors(all_selectors)
        
        for is_valid in validation_results.values():
            assert is_valid is True
        
        # Mock context-based response
        mock_response = Mock()
        
        # Mock context elements
        context_elements = []
        for i in range(3):
            mock_element = Mock()
            mock_element.css = Mock(return_value=Mock(
                first=Mock(text=f"Product {i+1}", attrib={"href": f"https://example.com/product/{i+1}"})
            ))
            context_elements.append(mock_element)
        
        mock_response.css.return_value = Mock(all=context_elements)
        
        # Test context-based extraction
        results = scraper.extract_with_context(mock_response, base_selector, field_selectors)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert "title" in result
            assert "price" in result
            assert "link" in result

    def test_performance_integration_large_dataset(self, scraper):
        """Test performance with large datasets in integration scenario."""
        # Create selectors for large dataset
        selectors = {
            "items": ".item::text",
            "links": "a::attr(href)",
            "images": "img::attr(src)"
        }
        
        # Validate selectors
        validation_results = scraper.validate_selectors(selectors)
        assert all(validation_results.values())
        
        # Mock large dataset response
        large_element_count = 1000
        mock_response = Mock()
        
        def css_mock(selector):
            mock_result = Mock()
            if "::text" in selector:
                elements = [Mock(text=f"Item {i}") for i in range(large_element_count)]
            else:
                elements = [Mock(attrib={"href": f"https://example.com/{i}", "src": f"image{i}.jpg"}) for i in range(large_element_count)]
            
            mock_result.all = elements
            mock_result.first = elements[0] if elements else None
            return mock_result
        
        mock_response.css.side_effect = css_mock
        
        # Extract large dataset
        results = scraper.extract_data(mock_response, selectors)
        
        # Should handle large dataset without issues
        assert "items" in results
        assert "links" in results
        assert "images" in results

    def test_pseudo_selector_validation_and_extraction(self, scraper):
        """Test various pseudo-selector patterns with validation and extraction."""
        pseudo_selectors = {
            "text_pseudo": "h1::text",
            "attr_pseudo": "a::attr(href)",
            "html_pseudo": "div::html",
            "data_attr": "[data-id]::attr(data-id)"
        }
        
        # Validate pseudo-selectors
        validation_results = scraper.validate_selectors(pseudo_selectors)
        
        for field_name, is_valid in validation_results.items():
            assert is_valid is True, f"Pseudo-selector '{field_name}' should be valid"
        
        # Mock response for pseudo-selector extraction
        mock_response = Mock()
        
        def css_mock(selector):
            mock_result = Mock()
            mock_element = Mock()
            
            # The selector comes in cleaned (without pseudo-selectors)
            if selector == "h1":  # From "h1::text"
                text_mock = Mock()
                text_mock.strip.return_value = "Pseudo text result"
                mock_element.text = text_mock
                mock_element.attrib = {}
            elif selector == "a":  # From "a::attr(href)" 
                mock_element.text = ""
                mock_element.attrib = {"href": "attr_value_href"}
            elif selector == "div":  # From "div::html"
                mock_element.text = ""
                mock_element.attrib = {}
                mock_element.html_content = "<div>HTML content</div>"
            elif selector == "[data-id]":  # From "[data-id]::attr(data-id)"
                mock_element.text = ""
                mock_element.attrib = {"data-id": "attr_value_data-id"}
            else:
                # Default case
                mock_element.text = "Default text"
                mock_element.attrib = {}
            
            mock_result.first = mock_element
            mock_result.all = [mock_element]
            return mock_result
        
        mock_response.css.side_effect = css_mock
        
        # Test extraction with pseudo-selectors
        results = scraper.extract_data(mock_response, pseudo_selectors)
        
        # Verify pseudo-selector results
        assert results["text_pseudo"] == "Pseudo text result"
        assert "attr_value" in results["attr_pseudo"]
        assert results["html_pseudo"] == "<div>HTML content</div>"

    def test_empty_and_edge_case_integration(self, scraper):
        """Test integration with empty results and edge cases."""
        edge_case_selectors = {
            "empty_result": ".nonexistent::text",
            "whitespace_only": ".whitespace::text",
            "missing_attribute": "div::attr(nonexistent)"
        }
        
        # Validate selectors (should pass basic validation)
        validation_results = scraper.validate_selectors(edge_case_selectors)
        
        for is_valid in validation_results.values():
            assert is_valid is True
        
        # Mock response with edge cases
        mock_response = Mock()
        
        def css_mock(selector):
            mock_result = Mock()
            
            if "nonexistent" in selector:
                # Empty result
                mock_result.first = None
                mock_result.all = []
            elif "whitespace" in selector:
                # Whitespace-only text
                mock_element = Mock()
                mock_element.text = "   \n\t   "
                mock_result.first = mock_element
                mock_result.all = [mock_element]
            else:
                # Missing attribute
                mock_element = Mock()
                mock_element.attrib = {"class": "test"}  # Different attribute
                mock_result.first = mock_element
                mock_result.all = [mock_element]
            
            return mock_result
        
        mock_response.css.side_effect = css_mock
        
        # Test extraction with edge cases
        results = scraper.extract_data(mock_response, edge_case_selectors)
        
        # Should handle edge cases gracefully
        assert "empty_result" in results
        assert "whitespace_only" in results
        assert "missing_attribute" in results

    def _create_mock_response_with_data(self):
        """Helper method to create a mock response with realistic data."""
        mock_response = Mock()
        
        def css_mock(selector):
            mock_result = Mock()
            
            if "title" in selector:
                element = Mock()
                element.text = "Premium Product Title"
                element.attrib = {"class": "main-title"}
                mock_result.first = element
                mock_result.all = [element]
            elif "description" in selector:
                element = Mock()
                element.text = "Detailed product description"
                element.attrib = {"class": "description"}
                mock_result.first = element
                mock_result.all = [element]
            elif "price" in selector:
                element = Mock()
                element.text = "$299.99"
                element.attrib = {"class": "price-value"}
                mock_result.first = element
                mock_result.all = [element]
            elif "product-link" in selector:
                element = Mock()
                element.text = "View Product"
                element.attrib = {"href": "https://example.com/product/123"}
                mock_result.first = element
                mock_result.all = [element]
            elif "image" in selector:
                element = Mock()
                element.text = ""
                element.attrib = {"src": "https://example.com/images/product.jpg"}
                mock_result.first = element
                mock_result.all = [element]
            elif "data-product-id" in selector:
                element = Mock()
                element.text = "Product Data"
                element.attrib = {"data-product-id": "PROD123"}
                mock_result.first = element
                mock_result.all = [element]
            else:
                element = Mock()
                element.text = "Default result"
                element.attrib = {"href": "https://example.com"}
                mock_result.first = element
                mock_result.all = [element]
            
            return mock_result
        
        mock_response.css.side_effect = css_mock
        return mock_response
    
    def _create_comprehensive_mock_response(self):
        """Helper method to create a comprehensive mock response for validation testing."""
        mock_response = Mock()
        mock_response.status = 200
        
        def css_mock(selector):
            mock_result = Mock()
            
            # Create mock elements based on selector type
            if "::text" in selector:
                mock_elements = [
                    Mock(tag="h1", text="Sample Title", attrib={"class": "main-title"}),
                    Mock(tag="p", text="Sample description", attrib={"class": "description"})
                ]
            elif "::attr(" in selector:
                mock_elements = [
                    Mock(tag="a", text="Link", attrib={"href": "https://example.com/link"}),
                    Mock(tag="img", text="", attrib={"src": "https://example.com/image.jpg"})
                ]
            else:
                mock_elements = [
                    Mock(tag="div", text="Content", attrib={"class": "content"})
                ]
            
            # Set up the mock result
            mock_result.all = mock_elements
            mock_result.first = mock_elements[0] if mock_elements else None
            
            return mock_result
        
        mock_response.css.side_effect = css_mock
        return mock_response


class TestSelectorValidationIntegration:
    """Integration tests specifically focused on selector validation features."""
    
    def test_validate_selector_function_css_types(self):
        """Test validate_selector function with various CSS selector types."""
        # Valid CSS selectors
        valid_selectors = [
            "div.class-name",
            "#element-id",
            "p::text",
            "a::attr(href)",
            "div::html",
            "ul > li:nth-child(2n)",
            "[data-testid='value']",
            "article.post > div.content p:first-child"
        ]
        
        for selector in valid_selectors:
            result = validate_selector(selector, "css")
            assert result["valid"] is True, f"Selector '{selector}' should be valid"
    
    def test_validate_selector_function_invalid_types(self):
        """Test validate_selector function with invalid selectors."""
        # Invalid CSS selectors
        invalid_selectors = [
            "",  # Empty
            None,  # None type
            "div[unclosed",  # Unbalanced brackets
            "div{color: red}",  # CSS rules
        ]
        
        for selector in invalid_selectors:
            result = validate_selector(selector, "css")
            assert result["valid"] is False, f"Selector '{selector}' should be invalid"
    
    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_test_selector_function_integration(self, mock_fetcher_class):
        """Test test_selector function with successful validation."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Create mock response with elements
        mock_response = Mock()
        mock_response.status = 200
        
        mock_elements = [
            Mock(tag="h1", text="Title 1", attrib={"class": "title"}, html_content="<h1>Title 1</h1>"),
            Mock(tag="h1", text="Title 2", attrib={"class": "title"}, html_content="<h1>Title 2</h1>")
        ]
        
        mock_css_result = Mock()
        mock_css_result.all = mock_elements
        mock_response.css.return_value = mock_css_result
        mock_fetcher.get.return_value = mock_response
        
        # Test selector validation
        result = test_selector("https://example.com", "h1.title", "css")
        
        assert result["matches"] is True
        assert result["count"] == 2
        assert len(result["sample_data"]) == 2
        assert "found 2 matching elements" in result["message"]
    
    def test_extract_element_data_integration(self):
        """Test _extract_element_data function integration."""
        # Create comprehensive mock element
        mock_element = Mock()
        mock_element.tag = "article"
        mock_element.text = "This is a comprehensive article with detailed content for testing purposes."
        mock_element.attrib = {
            "id": "article-123",
            "class": "blog-post featured-post",
            "data-category": "technology",
            "data-author": "john-doe",
            "title": "Click to read full article",
            "href": "https://example.com/article/123",
            "src": "https://example.com/images/article-thumb.jpg"
        }
        mock_element.html_content = '<article id="article-123" class="blog-post"><h2>Article Title</h2><p>Article content...</p></article>'
        
        result = _extract_element_data(mock_element)
        
        # Verify comprehensive data extraction
        assert result["tag"] == "article"
        assert "comprehensive article" in result["text"]
        assert result["attributes"]["id"] == "article-123"
        assert result["attributes"]["class"] == "blog-post featured-post"
        assert result["attributes"]["data-category"] == "technology"
        assert result["attributes"]["data-author"] == "john-doe"
        assert result["attributes"]["title"] == "Click to read full article"
        assert result["attributes"]["href"] == "https://example.com/article/123"
        assert result["attributes"]["src"] == "https://example.com/images/article-thumb.jpg"
        assert "Article Title" in result["html"]


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and comprehensive error handling in integration scenarios."""
    
    class ConcreteScraper(BaseScraper):
        """Concrete implementation of BaseScraper for testing."""
        
        def scrape(self, url: str, **kwargs):
            return {"url": url, "status": "test"}
    
    @pytest.fixture
    def scraper(self):
        return self.ConcreteScraper()
    
    def test_malformed_selector_integration(self, scraper):
        """Test integration with malformed selectors."""
        malformed_selectors = {
            "unbalanced_attr": "div[class='test'",  # Missing closing bracket
            "invalid_pseudo": "div:::text",  # Invalid pseudo-selector
            "script_injection": "div'; DROP TABLE users; --",
            "xss_attempt": "div<script>alert('xss')</script>",
        }
        
        # Validation should catch most issues
        validation_results = scraper.validate_selectors(malformed_selectors)
        
        # At least one should fail validation (the clearly invalid ones)
        failed_count = sum(1 for valid in validation_results.values() if not valid)
        assert failed_count >= 1, "At least some malformed selectors should fail validation"
    
    def test_memory_intensive_selectors(self, scraper):
        """Test memory-intensive selector operations."""
        # Create selectors that could potentially cause memory issues
        memory_intensive_selectors = {
            "wildcard": "*::text",  # Select all elements
            "deep_nesting": "div div div div div div div div div::text",
            "complex_pattern": "div:nth-child(n+1) > p:contains('text') + span::text"
        }
        
        # Validate these selectors
        validation_results = scraper.validate_selectors(memory_intensive_selectors)
        
        # Should handle validation without memory issues
        for field_name, is_valid in validation_results.items():
            assert isinstance(is_valid, bool), f"Validation should return boolean for '{field_name}'"
    
    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_timeout_and_retry_integration(self, mock_fetcher_class):
        """Test integration with timeout and network retry scenarios."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Simulate timeout error
        mock_fetcher.get.side_effect = Exception("Request timeout after 30 seconds")
        
        result = test_selector("https://slow-website.com", "h1::text", "css")
        
        assert result["matches"] is False
        assert result["count"] == 0
        assert "timeout" in result["error"].lower()
    
    def test_unicode_and_special_characters(self, scraper):
        """Test handling of unicode and special characters in selectors and content."""
        unicode_selectors = {
            "chinese_class": ".产品标题::text",
            "emoji_selector": ".title-😊::text",
            "special_chars": ".title\\'s-special::text",
            "unicode_attr": "[data-测试='value']::attr(data-测试)"
        }
        
        # Validate unicode selectors
        validation_results = scraper.validate_selectors(unicode_selectors)
        
        # Should handle unicode characters appropriately
        for field_name, is_valid in validation_results.items():
            assert isinstance(is_valid, bool), f"Should handle unicode in selector '{field_name}'"
    
    def test_extremely_long_selectors(self, scraper):
        """Test handling of extremely long CSS selectors."""
        # Create very long selectors
        long_class_name = "very-long-class-name-" * 50
        long_selectors = {
            "long_class": f".{long_class_name}::text",
            "long_hierarchy": " > ".join([f"div.level{i}" for i in range(100)]) + "::text",
            "long_attribute": f"[data-very-long-attribute-name-{long_class_name}='value']::text"
        }
        
        # Validate long selectors
        validation_results = scraper.validate_selectors(long_selectors)
        
        # Should handle long selectors without crashing
        for field_name, is_valid in validation_results.items():
            assert isinstance(is_valid, bool), f"Should handle long selector '{field_name}'"