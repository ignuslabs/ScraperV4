"""Tests for selector validation implementation."""

import pytest
from unittest.mock import patch, MagicMock
from src.utils.validation_utils import test_selector, _extract_element_data


class TestSelectorValidation:
    """Test cases for the test_selector function."""

    def test_invalid_url(self):
        """Test selector validation with invalid URL."""
        result = test_selector("not-a-url", "h1")
        assert result["matches"] is False
        assert result["count"] == 0
        assert "Invalid URL" in result["error"]
        assert result["sample_data"] == []

    def test_invalid_selector_syntax(self):
        """Test selector validation with invalid CSS selector."""
        result = test_selector("https://example.com", "h1[unclosed")
        assert result["matches"] is False
        assert result["count"] == 0
        assert "Invalid selector" in result["error"]
        assert result["sample_data"] == []

    def test_unsupported_selector_type(self):
        """Test selector validation with unsupported selector type."""
        result = test_selector("https://example.com", "//h1", "xpath")
        assert result["matches"] is False
        assert result["count"] == 0
        assert "not supported" in result["error"]
        assert result["sample_data"] == []

    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_network_error(self, mock_fetcher_class):
        """Test selector validation with network error."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_fetcher.get.side_effect = Exception("Connection refused")
        
        result = test_selector("https://example.com", "h1")
        assert result["matches"] is False
        assert result["count"] == 0
        assert "Network error" in result["error"] or "Error testing selector" in result["error"]
        assert result["sample_data"] == []

    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_http_error(self, mock_fetcher_class):
        """Test selector validation with HTTP error."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_response = MagicMock()
        mock_response.status = 404
        mock_fetcher.get.return_value = mock_response
        
        result = test_selector("https://example.com", "h1")
        assert result["matches"] is False
        assert result["count"] == 0
        assert "HTTP 404" in result["error"]
        assert result["sample_data"] == []

    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_no_elements_found(self, mock_fetcher_class):
        """Test selector validation when no elements are found."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.css.return_value = None  # No elements found
        mock_fetcher.get.return_value = mock_response
        
        result = test_selector("https://example.com", ".non-existent")
        assert result["matches"] is False
        assert result["count"] == 0
        assert "no elements were found" in result["message"]
        assert result["sample_data"] == []

    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_single_element_found(self, mock_fetcher_class):
        """Test selector validation when single element is found."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_response = MagicMock()
        mock_response.status = 200
        
        # Mock single element
        mock_element = MagicMock()
        mock_element.tag = "h1"
        mock_element.text = "Test Heading"
        mock_element.attrib = {"class": "main-heading"}
        mock_element.html_content = '<h1 class="main-heading">Test Heading</h1>'
        
        mock_elements = MagicMock()
        mock_elements.first = mock_element
        mock_response.css.return_value = mock_elements
        mock_fetcher.get.return_value = mock_response
        
        # Configure elements to not have 'all' attribute but have 'first'
        del mock_elements.all  # Remove 'all' attribute
        
        result = test_selector("https://example.com", "h1")
        assert result["matches"] is True
        assert result["count"] == 1
        assert "found 1 matching element" in result["message"]
        assert len(result["sample_data"]) == 1
        assert result["sample_data"][0]["tag"] == "h1"
        assert result["sample_data"][0]["text"] == "Test Heading"

    @patch('src.utils.validation_utils.StealthyFetcher')
    def test_multiple_elements_found(self, mock_fetcher_class):
        """Test selector validation when multiple elements are found."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_response = MagicMock()
        mock_response.status = 200
        
        # Mock multiple elements
        mock_elements_list = []
        for i in range(5):
            mock_element = MagicMock()
            mock_element.tag = "div"
            mock_element.text = f"Content {i+1}"
            mock_element.attrib = {"class": f"item-{i+1}"}
            mock_element.html_content = f'<div class="item-{i+1}">Content {i+1}</div>'
            mock_elements_list.append(mock_element)
        
        mock_elements = MagicMock()
        mock_elements.all = mock_elements_list
        mock_response.css.return_value = mock_elements
        mock_fetcher.get.return_value = mock_response
        
        result = test_selector("https://example.com", "div")
        assert result["matches"] is True
        assert result["count"] == 5
        assert "found 5 matching elements" in result["message"]
        assert len(result["sample_data"]) == 3  # Should return first 3 elements
        assert result["sample_data"][0]["text"] == "Content 1"
        assert result["sample_data"][1]["text"] == "Content 2"
        assert result["sample_data"][2]["text"] == "Content 3"


class TestElementDataExtraction:
    """Test cases for the _extract_element_data function."""

    def test_extract_complete_element_data(self):
        """Test extracting data from a complete element."""
        mock_element = MagicMock()
        mock_element.tag = "a"
        mock_element.text = "Click here for more information"
        mock_element.attrib = {
            "href": "https://example.com/page",
            "class": "link primary-link",
            "id": "main-link",
            "title": "Main navigation link"
        }
        mock_element.html_content = '<a href="https://example.com/page" class="link primary-link" id="main-link">Click here</a>'
        
        result = _extract_element_data(mock_element)
        
        assert result["tag"] == "a"
        assert result["text"] == "Click here for more information"
        assert result["attributes"]["href"] == "https://example.com/page"
        assert result["attributes"]["class"] == "link primary-link"
        assert result["attributes"]["id"] == "main-link"
        assert result["attributes"]["title"] == "Main navigation link"
        assert "Click here" in result["html"]

    def test_extract_minimal_element_data(self):
        """Test extracting data from element with minimal attributes."""
        mock_element = MagicMock()
        mock_element.tag = "span"
        mock_element.text = "Simple text"
        mock_element.attrib = {}
        mock_element.html_content = "<span>Simple text</span>"
        
        result = _extract_element_data(mock_element)
        
        assert result["tag"] == "span"
        assert result["text"] == "Simple text"
        assert result["attributes"] == {}
        assert result["html"] == "<span>Simple text</span>"

    def test_extract_element_data_with_long_content(self):
        """Test that content is properly truncated for long text."""
        mock_element = MagicMock()
        mock_element.tag = "p"
        mock_element.text = "A" * 300  # Long text
        mock_element.attrib = {"class": "B" * 150}  # Long attribute
        mock_element.html_content = "C" * 400  # Long HTML
        
        result = _extract_element_data(mock_element)
        
        assert len(result["text"]) == 200  # Should be truncated
        assert len(result["attributes"]["class"]) == 100  # Should be truncated
        assert len(result["html"]) == 300  # Should be truncated

    def test_extract_element_data_error_handling(self):
        """Test error handling when element data extraction fails."""
        # Create a mock that doesn't have the expected attributes
        mock_element = object()  # Basic object with no attributes
        
        result = _extract_element_data(mock_element)
        
        # When getattr fails, it should return "unknown" or empty values
        assert result["tag"] == "unknown"
        assert result["text"] == ""
        assert result["attributes"] == {}
        assert result["html"] == ""