"""Comprehensive tests for CSS selector extraction functionality."""

import pytest
from unittest.mock import Mock, MagicMock
from src.scrapers.base_scraper import BaseScraper


class MockElement:
    """Mock element class for testing."""
    
    def __init__(self, text="", attrib=None, html_content=""):
        self.text = text
        self.attrib = attrib or {}
        self.html_content = html_content


class MockResponse:
    """Mock response class for testing."""
    
    def __init__(self, elements=None, first_element=None, all_elements=None):
        self.elements = elements
        self.first_element = first_element
        self.all_elements = all_elements or []
        
    def css(self, selector):
        """Mock CSS selector method."""
        mock_result = Mock()
        
        if self.first_element:
            mock_result.first = self.first_element
            
        if self.all_elements:
            mock_result.all = self.all_elements
            
        # Handle direct element access
        if self.elements:
            for attr, value in self.elements.items():
                setattr(mock_result, attr, value)
                
        return mock_result


class TestBaseScraper:
    """Test class for BaseScraper CSS selector extraction."""
    
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
    def mock_response_single(self):
        """Mock response with single element."""
        element = MockElement(text="Test Text", attrib={"href": "https://example.com"})
        return MockResponse(first_element=element, all_elements=[element])
    
    @pytest.fixture
    def mock_response_multiple(self):
        """Mock response with multiple elements."""
        elements = [
            MockElement(text="Item 1", attrib={"id": "item1"}),
            MockElement(text="Item 2", attrib={"id": "item2"}),
            MockElement(text="Item 3", attrib={"id": "item3"})
        ]
        return MockResponse(all_elements=elements)
    
    def test_extract_with_css_text_pseudo_selector(self, scraper, mock_response_single):
        """Test text extraction using ::text pseudo-selector."""
        result = scraper._extract_with_css(mock_response_single, "div.test::text")
        assert result == "Test Text"
    
    def test_extract_with_css_attribute_pseudo_selector(self, scraper, mock_response_single):
        """Test attribute extraction using ::attr() pseudo-selector."""
        result = scraper._extract_with_css(mock_response_single, "a.link::attr(href)")
        assert result == "https://example.com"
    
    def test_extract_with_css_html_pseudo_selector(self, scraper):
        """Test HTML content extraction using ::html pseudo-selector."""
        element = MockElement(html_content="<span>Inner HTML</span>")
        mock_response = MockResponse(first_element=element)
        
        result = scraper._extract_with_css(mock_response, "div::html")
        assert result == "<span>Inner HTML</span>"
    
    def test_extract_with_css_multiple_elements_text(self, scraper, mock_response_multiple):
        """Test text extraction from multiple elements."""
        result = scraper._extract_with_css(mock_response_multiple, "li.item::text")
        assert result == ["Item 1", "Item 2", "Item 3"]
    
    def test_extract_with_css_multiple_elements_attributes(self, scraper, mock_response_multiple):
        """Test attribute extraction from multiple elements."""
        result = scraper._extract_with_css(mock_response_multiple, "li.item::attr(id)")
        assert result == ["item1", "item2", "item3"]
    
    def test_extract_with_css_auto_format_single(self, scraper, mock_response_single):
        """Test auto format extraction with single element."""
        result = scraper._extract_with_css(mock_response_single, "div.test", "auto")
        assert result == "Test Text"
    
    def test_extract_with_css_auto_format_multiple(self, scraper, mock_response_multiple):
        """Test auto format extraction with multiple elements."""
        result = scraper._extract_with_css(mock_response_multiple, "li.item", "auto")
        assert result == ["Item 1", "Item 2", "Item 3"]
    
    def test_extract_with_css_first_element(self, scraper, mock_response_multiple):
        """Test extracting first element specifically."""
        result = scraper._extract_with_css(mock_response_multiple, "li.item", "first")
        assert result.text == "Item 1"
    
    def test_extract_with_css_all_elements(self, scraper, mock_response_multiple):
        """Test extracting all elements."""
        result = scraper._extract_with_css(mock_response_multiple, "li.item", "all")
        assert len(result) == 3
        assert result[0].text == "Item 1"
    
    def test_extract_with_css_empty_result(self, scraper):
        """Test extraction with no matching elements."""
        mock_response = MockResponse()
        result = scraper._extract_with_css(mock_response, "div.nonexistent::text")
        assert result == ""
    
    def test_extract_with_css_invalid_response(self, scraper):
        """Test extraction with invalid response object."""
        with pytest.raises(AttributeError, match="Invalid response object"):
            scraper._extract_with_css(None, "div.test")
    
    def test_extract_with_css_empty_selector(self, scraper, mock_response_single):
        """Test extraction with empty selector."""
        with pytest.raises(ValueError, match="Selector must be a non-empty string"):
            scraper._extract_with_css(mock_response_single, "")
    
    def test_extract_with_css_invalid_attribute_selector(self, scraper, mock_response_single):
        """Test extraction with invalid attribute selector."""
        with pytest.raises(ValueError, match="Empty attribute name"):
            scraper._extract_with_css(mock_response_single, "div::attr()")
    
    def test_extract_data_multiple_selectors(self, scraper):
        """Test extract_data method with multiple selectors."""
        mock_response = Mock()
        mock_response.css.return_value = Mock(first=MockElement(text="Test"))
        
        selectors = {
            "title": "h1::text",
            "description": "p.desc::text",
            "link": "a::attr(href)"
        }
        
        result = scraper.extract_data(mock_response, selectors)
        
        assert "title" in result
        assert "description" in result
        assert "link" in result
    
    def test_extract_data_with_errors(self, scraper):
        """Test extract_data method error handling."""
        mock_response = Mock()
        mock_response.css.side_effect = Exception("CSS error")
        
        selectors = {"title": "h1::text"}
        result = scraper.extract_data(mock_response, selectors)
        
        assert "Error processing selector" in result["title"]
    
    def test_extract_multiple_selectors_fallback(self, scraper):
        """Test extract_multiple_selectors with fallback support."""
        mock_response = Mock()
        
        # First selector fails, second succeeds
        def css_side_effect(selector):
            if selector == ".primary":
                return Mock(first=None)
            else:
                return Mock(first=MockElement(text="Fallback Text"))
        
        mock_response.css.side_effect = css_side_effect
        
        selector_groups = {
            "title": [".primary::text", ".secondary::text", ".tertiary::text"]
        }
        
        result = scraper.extract_multiple_selectors(mock_response, selector_groups)
        assert result["title"] == "Fallback Text"
    
    def test_extract_with_context(self, scraper):
        """Test extract_with_context for structured data extraction."""
        mock_response = Mock()
        
        # Mock context elements
        context_elements = [
            MockElement(text="Context 1"),
            MockElement(text="Context 2")
        ]
        
        mock_base_result = Mock()
        mock_base_result.all = context_elements
        
        # Mock each context element to have css method
        for element in context_elements:
            element.css = Mock(return_value=Mock(first=MockElement(text=f"Field for {element.text}")))
        
        mock_response.css.return_value = mock_base_result
        
        base_selector = ".product"
        field_selectors = {"name": ".title::text"}
        
        result = scraper.extract_with_context(mock_response, base_selector, field_selectors)
        
        assert len(result) == 2
        assert result[0]["name"] == "Field for Context 1"
        assert result[1]["name"] == "Field for Context 2"
    
    def test_validate_selectors_valid(self, scraper):
        """Test selector validation with valid selectors."""
        selectors = {
            "title": "h1.main-title",
            "description": "p::text",
            "link": "a::attr(href)",
            "content": "div.content::html"
        }
        
        result = scraper.validate_selectors(selectors)
        
        for field in selectors:
            assert result[field] is True
    
    def test_validate_selectors_invalid(self, scraper):
        """Test selector validation with invalid selectors."""
        selectors = {
            "empty": "",
            "none": None,
            "invalid_attr": "div::attr()",
            "invalid_chars": "div<script>",
            "malformed_attr": "div::attr(href"
        }
        
        result = scraper.validate_selectors(selectors)
        
        for field in selectors:
            assert result[field] is False
    
    def test_extract_text_content_edge_cases(self, scraper):
        """Test _extract_text_content with edge cases."""
        # Empty elements
        result = scraper._extract_text_content(None)
        assert result == ""
        
        # Element with empty text
        element = MockElement(text="")
        mock_elements = Mock(first=element)
        result = scraper._extract_text_content(mock_elements)
        assert result == ""
        
        # Elements with whitespace only
        element = MockElement(text="   ")
        mock_elements = Mock(first=element)
        result = scraper._extract_text_content(mock_elements)
        assert result == ""
    
    def test_extract_attribute_values_edge_cases(self, scraper):
        """Test _extract_attribute_values with edge cases."""
        # Missing attribute
        element = MockElement(attrib={"class": "test"})
        mock_elements = Mock(first=element)
        result = scraper._extract_attribute_values(mock_elements, "id")
        assert result == ""
        
        # Empty attribute value
        element = MockElement(attrib={"id": ""})
        mock_elements = Mock(first=element)
        result = scraper._extract_attribute_values(mock_elements, "id")
        assert result == ""
    
    def test_complex_css_selectors(self, scraper):
        """Test complex CSS selector patterns."""
        mock_response = Mock()
        mock_response.css.return_value = Mock(first=MockElement(text="Complex Result"))
        
        # Test various complex selectors
        complex_selectors = [
            "div.container > ul.list li:nth-child(2n+1)::text",
            "article[data-category='news'] h2::text",
            "form input[type='email']::attr(placeholder)",
            ".sidebar .widget:last-child a::attr(href)",
            "table tbody tr:hover td:first-child::html"
        ]
        
        for selector in complex_selectors:
            result = scraper._extract_with_css(mock_response, selector)
            assert result == "Complex Result"
    
    def test_performance_with_large_data(self, scraper):
        """Test performance with large datasets."""
        # Create mock response with many elements
        large_element_list = [MockElement(text=f"Item {i}") for i in range(1000)]
        mock_response = MockResponse(all_elements=large_element_list)
        
        result = scraper._extract_with_css(mock_response, ".item::text")
        
        assert len(result) == 1000
        assert result[0] == "Item 0"
        assert result[-1] == "Item 999"
    
    def test_nested_selector_extraction(self, scraper):
        """Test extraction with nested selectors."""
        mock_response = Mock()
        
        # Mock nested structure
        inner_element = MockElement(text="Nested Content")
        outer_element = Mock()
        outer_element.css = Mock(return_value=Mock(first=inner_element))
        
        mock_response.css.return_value = Mock(first=outer_element)
        
        # This would be handled in extract_with_context for real nested scenarios
        result = scraper._extract_with_css(mock_response, ".outer .inner::text")
        # Since we're mocking the response.css method, it returns our mock
        assert hasattr(result, 'css')