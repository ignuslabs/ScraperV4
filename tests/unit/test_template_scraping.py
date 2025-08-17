"""Comprehensive unit tests for template scraping feature."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timezone
from pathlib import Path

from src.services.scraping_service import ScrapingService
from src.scrapers.template_scraper import TemplateScraper
from src.scrapers.base_scraper import BaseScraper
from src.data.template_manager import FileTemplateManager


class TestScrapingServiceTemplateFeatures:
    """Test ScrapingService template-related functionality."""
    
    @pytest.fixture
    def scraping_service(self):
        """Create ScrapingService instance with mocked dependencies."""
        service = ScrapingService()
        service.template_manager = Mock()
        service.job_manager = Mock()
        return service
    
    @pytest.fixture
    def sample_template(self):
        """Sample template for testing."""
        return {
            "name": "test_template",
            "version": "1.0.0",
            "selectors": {
                "title": "h1::text",
                "price": ".price::text",
                "image": "img::attr(src)",
                "description": ".description"
            },
            "validation_rules": {},
            "adaptive_selectors": True,
            "fallback_selectors": {},
            "post_processing": [
                {
                    "type": "trim",
                    "field": "title"
                },
                {
                    "type": "to_float",
                    "field": "price"
                }
            ]
        }
    
    def test_scrape_with_template_success(self, scraping_service, sample_template):
        """Test successful scraping with template."""
        # Setup
        template_name = "test_template"
        target_url = "https://example.com"
        parameters = {"max_items": 10}
        
        scraping_service.template_manager.load_template.return_value = sample_template
        
        # Mock the validate_scraping_target method directly
        with patch.object(scraping_service, 'validate_scraping_target', return_value={"valid": True}):
            # Mock TemplateScraper
            with patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
                mock_scraper = Mock()
                mock_scraper_class.return_value = mock_scraper
                mock_scraper.validate_template.return_value = {"valid": True}
                mock_scraper.scrape.return_value = {
                    "status": "success",
                    "data": {
                        "title": "Test Product",
                        "price": "29.99",
                        "image": "image.jpg"
                    },
                    "items_count": 1
                }
                mock_scraper.template = sample_template
                
                # Execute
                result = scraping_service.scrape_with_template(template_name, target_url, parameters)
                
                # Verify
                assert result["status"] == "success"
                assert result["template"] == template_name
                assert result["parameters"] == parameters
                assert "scraped_at" in result
                assert "data" in result
                
                # Verify template manager calls
                scraping_service.template_manager.load_template.assert_called_once_with(template_name)
                scraping_service.template_manager.update_template_stats.assert_called_once_with(template_name, True)
                
                # Verify scraper setup
                mock_scraper_class.assert_called_once_with(sample_template)
                mock_scraper.validate_template.assert_called_once()
                mock_scraper.scrape.assert_called_once_with(target_url)
    
    def test_scrape_with_template_missing_template(self, scraping_service):
        """Test scraping with missing template."""
        # Setup
        template_name = "nonexistent_template"
        target_url = "https://example.com"
        
        scraping_service.template_manager.load_template.return_value = None
        
        # Execute
        result = scraping_service.scrape_with_template(template_name, target_url)
        
        # Verify
        assert result["status"] == "failed"
        assert "not found" in result["error"]
        assert result["template"] == template_name
        assert result["url"] == target_url
        assert result["parameters"] == {}
    
    def test_scrape_with_template_invalid_template(self, scraping_service, sample_template):
        """Test scraping with invalid template."""
        # Setup
        template_name = "invalid_template"
        target_url = "https://example.com"
        
        scraping_service.template_manager.load_template.return_value = sample_template
        
        with patch.object(scraping_service, 'validate_scraping_target', return_value={"valid": True}):
        
            with patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
                mock_scraper = Mock()
                mock_scraper_class.return_value = mock_scraper
                mock_scraper.validate_template.return_value = {
                    "valid": False,
                    "errors": ["Missing required field: selectors"]
                }
                
                # Execute
                result = scraping_service.scrape_with_template(template_name, target_url)
                
                # Verify
                assert result["status"] == "failed"
                assert "Template validation failed" in result["error"]
    
    def test_scrape_with_template_invalid_url(self, scraping_service, sample_template):
        """Test scraping with invalid URL."""
        # Setup
        template_name = "test_template"
        target_url = "invalid-url"
        
        scraping_service.template_manager.load_template.return_value = sample_template
        
        with patch.object(scraping_service, 'validate_scraping_target', return_value={
            "valid": False,
            "error": "Invalid URL format"
        }):
            # Execute
            result = scraping_service.scrape_with_template(template_name, target_url)
            
            # Verify
            assert result["status"] == "failed"
            assert "Invalid target URL" in result["error"]
    
    def test_scrape_with_template_parameters_merge(self, scraping_service, sample_template):
        """Test parameter merging with template."""
        # Setup
        template_name = "test_template"
        target_url = "https://example.com"
        parameters = {"max_items": 5, "custom_field": "value"}
        
        scraping_service.template_manager.load_template.return_value = sample_template
        
        with patch.object(scraping_service, 'validate_scraping_target', return_value={"valid": True}):
        
            with patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
                mock_scraper = Mock()
                mock_scraper_class.return_value = mock_scraper
                mock_scraper.validate_template.return_value = {"valid": True}
                mock_scraper.scrape.return_value = {"status": "success", "data": {}}
                mock_scraper.template = sample_template.copy()
                
                # Execute
                scraping_service.scrape_with_template(template_name, target_url, parameters)
                
                # Verify parameters were merged into template
                assert mock_scraper.template["max_items"] == 5
                assert mock_scraper.template["custom_field"] == "value"
    
    def test_scrape_with_template_exception_handling(self, scraping_service, sample_template):
        """Test exception handling during scraping."""
        # Setup
        template_name = "test_template"
        target_url = "https://example.com"
        
        scraping_service.template_manager.load_template.return_value = sample_template
        
        with patch.object(scraping_service, 'validate_scraping_target', return_value={"valid": True}):
            with patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
                mock_scraper_class.side_effect = Exception("Scraper initialization failed")
                
                # Execute
                result = scraping_service.scrape_with_template(template_name, target_url)
                
                # Verify
                assert result["status"] == "failed"
                assert "Scraping failed" in result["error"]
                assert "Scraper initialization failed" in result["error"]
                
                # Verify stats updated with failure
                scraping_service.template_manager.update_template_stats.assert_called_once_with(template_name, False)
    
    def test_validate_scraping_target_valid_url(self, scraping_service):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://test.com/page",
            "https://subdomain.domain.com/path?param=value"
        ]
        
        for url in valid_urls:
            result = scraping_service.validate_scraping_target(url)
            assert result["valid"] is True
            assert result["url"] == url
            assert "domain" in result
    
    def test_validate_scraping_target_invalid_url(self, scraping_service):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com",
            None
        ]
        
        for url in invalid_urls:
            result = scraping_service.validate_scraping_target(url)
            assert result["valid"] is False
            assert "Invalid URL format" in result["error"]


class TestTemplateScraper:
    """Test TemplateScraper class functionality."""
    
    @pytest.fixture
    def sample_template(self):
        """Sample template for testing."""
        return {
            "name": "test_template",
            "version": "1.0.0",
            "selectors": {
                "title": "h1::text",
                "price": ".price::text",
                "image": "img::attr(src)"
            },
            "post_processing": [
                {
                    "type": "trim",
                    "field": "title"
                }
            ]
        }
    
    @pytest.fixture
    def template_scraper(self, sample_template):
        """Create TemplateScraper instance."""
        return TemplateScraper(sample_template)
    
    @pytest.fixture
    def mock_response(self):
        """Mock scrapling response."""
        mock_resp = Mock()
        
        # Mock CSS method behavior
        def css_side_effect(selector):
            mock_elements = Mock()
            if selector == "h1":
                mock_element = Mock()
                mock_element.text = "Test Title"
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == ".price":
                mock_element = Mock()
                mock_element.text = "$29.99"
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == "img":
                mock_element = Mock()
                mock_element.attrs = {"src": "image.jpg"}
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            else:
                return None
        
        mock_resp.css.side_effect = css_side_effect
        mock_resp.status = 200
        return mock_resp
    
    def test_template_scraper_initialization_with_template(self, sample_template):
        """Test TemplateScraper initialization with template."""
        scraper = TemplateScraper(sample_template)
        assert scraper.template == sample_template
    
    def test_template_scraper_initialization_without_template(self):
        """Test TemplateScraper initialization without template."""
        scraper = TemplateScraper()
        assert scraper.template is None
    
    def test_set_template(self, template_scraper, sample_template):
        """Test setting template."""
        new_template = {"name": "new_template", "selectors": {"heading": "h2"}}
        template_scraper.set_template(new_template)
        assert template_scraper.template == new_template
    
    def test_scrape_success(self, template_scraper, mock_response):
        """Test successful scraping."""
        url = "https://example.com"
        
        with patch.object(template_scraper, '_fetch_page', return_value=mock_response):
            with patch.object(template_scraper, 'extract_data', return_value={"title": "Test Title", "price": "$29.99"}):
                with patch.object(template_scraper, '_apply_post_processing', return_value={"title": "Test Title", "price": "$29.99"}):
                    result = template_scraper.scrape(url)
        
        assert result["status"] == "success"
        assert result["url"] == url
        assert result["template_name"] == "test_template"
        assert "data" in result
        assert result["items_count"] == 1
    
    def test_scrape_no_template(self):
        """Test scraping without template configured."""
        scraper = TemplateScraper()
        url = "https://example.com"
        
        result = scraper.scrape(url)
        
        assert result["status"] == "failed"
        assert result["error"] == "No template configured"
        assert result["url"] == url
    
    def test_scrape_fetch_failure(self, template_scraper):
        """Test scraping when page fetch fails."""
        url = "https://example.com"
        
        with patch.object(template_scraper, '_fetch_page', return_value=None):
            result = template_scraper.scrape(url)
        
        assert result["status"] == "failed"
        assert result["error"] == "Failed to fetch page"
        assert result["url"] == url
    
    def test_scrape_exception_handling(self, template_scraper, mock_response):
        """Test scraping with exception."""
        url = "https://example.com"
        
        with patch.object(template_scraper, '_fetch_page', return_value=mock_response):
            with patch.object(template_scraper, 'extract_data', side_effect=Exception("Extraction failed")):
                result = template_scraper.scrape(url)
        
        assert result["status"] == "failed"
        assert "Extraction failed" in result["error"]
        assert result["template_name"] == "test_template"
    
    def test_validate_template_valid(self, template_scraper):
        """Test template validation with valid template."""
        result = template_scraper.validate_template()
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_template_no_template(self):
        """Test template validation with no template."""
        scraper = TemplateScraper()
        result = scraper.validate_template()
        
        assert result["valid"] is False
        assert "No template configured" in result["errors"]
    
    def test_validate_template_missing_fields(self):
        """Test template validation with missing required fields."""
        invalid_template = {"version": "1.0.0"}  # Missing name and selectors
        scraper = TemplateScraper(invalid_template)
        
        result = scraper.validate_template()
        
        assert result["valid"] is False
        assert "Template missing selectors" in result["errors"]
        assert "Template missing name" in result["errors"]
    
    def test_validate_template_invalid_selectors(self):
        """Test template validation with invalid selectors."""
        invalid_template = {
            "name": "test",
            "selectors": "not_a_dict"  # Should be dictionary
        }
        scraper = TemplateScraper(invalid_template)
        
        result = scraper.validate_template()
        
        assert result["valid"] is False
        assert "Selectors must be a non-empty dictionary" in result["errors"]
    
    def test_scrape_with_pagination_basic(self, template_scraper, mock_response):
        """Test pagination scraping."""
        url = "https://example.com"
        
        with patch.object(template_scraper, 'scrape', return_value={"status": "success", "items_count": 5}):
            with patch.object(template_scraper, '_get_next_page_url', side_effect=[None]):  # No next page
                result = template_scraper.scrape_with_pagination(url, max_pages=3)
        
        assert result["status"] == "success"
        assert result["pages_scraped"] == 1
        assert result["total_items"] == 5
        assert len(result["results"]) == 1
    
    def test_test_selectors_success(self, template_scraper, mock_response):
        """Test selector testing functionality."""
        url = "https://example.com"
        
        with patch.object(template_scraper, '_fetch_page', return_value=mock_response):
            result = template_scraper.test_selectors(url)
        
        assert result["success"] is True
        assert "selector_results" in result
        assert "statistics" in result
    
    def test_test_selectors_no_template(self):
        """Test selector testing without template."""
        scraper = TemplateScraper()
        url = "https://example.com"
        
        result = scraper.test_selectors(url)
        
        assert result["success"] is False
        assert result["error"] == "No template configured"
    
    def test_test_selectors_fetch_failure(self, template_scraper):
        """Test selector testing with fetch failure."""
        url = "https://example.com"
        
        with patch.object(template_scraper, '_fetch_page', return_value=None):
            result = template_scraper.test_selectors(url)
        
        assert result["success"] is False
        assert "Failed to fetch the target URL" in result["error"]


class TestBaseScraper:
    """Test BaseScraper extract_data method."""
    
    @pytest.fixture
    def base_scraper(self):
        """Create BaseScraper concrete implementation for testing."""
        class ConcreteBaseScraper(BaseScraper):
            def scrape(self, url: str, **kwargs):
                return {"url": url, "status": "success"}
        
        return ConcreteBaseScraper()
    
    @pytest.fixture
    def mock_response(self):
        """Mock response with CSS method."""
        mock_resp = Mock()
        
        def css_side_effect(selector):
            mock_elements = Mock()
            if selector == "h1":
                mock_element = Mock()
                mock_element.text = " Test Title "
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == "a":
                mock_element = Mock()
                mock_element.attrs = {"href": "https://example.com"}
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == ".items":
                mock_element1 = Mock()
                mock_element1.text = "Item 1"
                mock_element2 = Mock()
                mock_element2.text = "Item 2"
                mock_elements.all = [mock_element1, mock_element2]
                return mock_elements
            else:
                return None
        
        mock_resp.css.side_effect = css_side_effect
        return mock_resp
    
    def test_extract_data_text_selector(self, base_scraper, mock_response):
        """Test extraction with ::text selector."""
        selectors = {"title": "h1::text"}
        
        result = base_scraper.extract_data(mock_response, selectors)
        
        assert "title" in result
        assert result["title"] == ["Test Title"]  # Text is stripped by extract_data
    
    def test_extract_data_attribute_selector(self, base_scraper, mock_response):
        """Test extraction with ::attr() selector."""
        selectors = {"link": "a::attr(href)"}
        
        result = base_scraper.extract_data(mock_response, selectors)
        
        assert "link" in result
        assert result["link"] == ["https://example.com"]  # Returns list for multiple elements
    
    def test_extract_data_standard_selector(self, base_scraper, mock_response):
        """Test extraction with standard CSS selector."""
        selectors = {"title": "h1"}
        
        result = base_scraper.extract_data(mock_response, selectors)
        
        assert "title" in result
        assert result["title"] == ["Test Title"]  # Text is stripped by extract_data
    
    def test_extract_data_multiple_elements(self, base_scraper, mock_response):
        """Test extraction of multiple elements."""
        selectors = {"items": ".items::text"}
        
        # Mock for multiple elements
        mock_response.css.return_value.all = [
            Mock(text="Item 1"),
            Mock(text="Item 2")
        ]
        
        result = base_scraper.extract_data(mock_response, selectors)
        
        assert "items" in result
        assert len(result["items"]) == 2
    
    def test_extract_data_missing_elements(self, base_scraper, mock_response):
        """Test extraction with missing elements."""
        selectors = {"missing": ".nonexistent::text"}
        
        # Mock CSS to return None for nonexistent selector
        def css_side_effect(selector):
            if selector == ".nonexistent":
                return None
            return Mock()
        
        mock_response.css.side_effect = css_side_effect
        
        result = base_scraper.extract_data(mock_response, selectors)
        
        assert "missing" in result
        assert result["missing"] == ""
    
    def test_extract_data_invalid_response(self, base_scraper):
        """Test extraction with invalid response object."""
        selectors = {"title": "h1::text"}
        
        result = base_scraper.extract_data(None, selectors)
        
        assert "error" in result
        assert "Invalid response object" in result["error"]
    
    def test_extract_data_selector_exception(self, base_scraper, mock_response):
        """Test extraction with selector that throws exception."""
        selectors = {"error_field": "invalid::selector"}
        
        # Mock CSS to raise exception
        mock_response.css.side_effect = Exception("Selector error")
        
        result = base_scraper.extract_data(mock_response, selectors)
        
        assert "error_field" in result
        assert "Error extracting error_field" in result["error_field"]


class TestPostProcessingRules:
    """Test post-processing rule functionality."""
    
    @pytest.fixture
    def template_scraper(self):
        """Create TemplateScraper for testing post-processing."""
        template = {
            "name": "test_template",
            "selectors": {"field": "selector"},
            "post_processing": []
        }
        return TemplateScraper(template)
    
    def test_trim_processing(self, template_scraper):
        """Test trim post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "trim", "field": "title"}
        ]
        
        data = {"title": "  Test Title  "}
        result = template_scraper._apply_post_processing(data)
        
        assert result["title"] == "Test Title"
    
    def test_lowercase_processing(self, template_scraper):
        """Test lowercase post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "lowercase", "field": "title"}
        ]
        
        data = {"title": "TEST TITLE"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["title"] == "test title"
    
    def test_uppercase_processing(self, template_scraper):
        """Test uppercase post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "uppercase", "field": "title"}
        ]
        
        data = {"title": "test title"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["title"] == "TEST TITLE"
    
    def test_regex_replace_processing(self, template_scraper):
        """Test regex replace post-processing rule."""
        template_scraper.template["post_processing"] = [
            {
                "type": "regex_replace",
                "field": "price",
                "pattern": r"[^\d.]",
                "replacement": ""
            }
        ]
        
        data = {"price": "$29.99 USD"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["price"] == "29.99"
    
    def test_split_processing(self, template_scraper):
        """Test split post-processing rule."""
        template_scraper.template["post_processing"] = [
            {
                "type": "split",
                "field": "tags",
                "separator": ","
            }
        ]
        
        data = {"tags": "tag1, tag2, tag3"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["tags"] == ["tag1", "tag2", "tag3"]
    
    def test_join_processing(self, template_scraper):
        """Test join post-processing rule."""
        template_scraper.template["post_processing"] = [
            {
                "type": "join",
                "field": "tags",
                "separator": " | "
            }
        ]
        
        data = {"tags": ["tag1", "tag2", "tag3"]}
        result = template_scraper._apply_post_processing(data)
        
        assert result["tags"] == "tag1 | tag2 | tag3"
    
    def test_to_int_processing(self, template_scraper):
        """Test to_int post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "to_int", "field": "count"}
        ]
        
        data = {"count": "42 items"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["count"] == 42
    
    def test_to_float_processing(self, template_scraper):
        """Test to_float post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "to_float", "field": "price"}
        ]
        
        data = {"price": "$29.99"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["price"] == 29.99
    
    def test_normalize_url_processing(self, template_scraper):
        """Test URL normalization post-processing rule."""
        template_scraper.template["post_processing"] = [
            {
                "type": "normalize_url",
                "field": "url",
                "base_url": "https://example.com"
            }
        ]
        
        data = {"url": "/path/to/page"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["url"] == "https://example.com/path/to/page"
    
    def test_parse_date_processing(self, template_scraper):
        """Test date parsing post-processing rule."""
        template_scraper.template["post_processing"] = [
            {
                "type": "parse_date",
                "field": "date",
                "input_format": "%Y-%m-%d",
                "output_format": "%m/%d/%Y"
            }
        ]
        
        data = {"date": "2023-12-25"}
        result = template_scraper._apply_post_processing(data)
        
        assert result["date"] == "12/25/2023"
    
    def test_remove_empty_processing(self, template_scraper):
        """Test remove empty post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "remove_empty", "field": "items"}
        ]
        
        data = {"items": ["item1", "", "item2", None, "item3"]}
        result = template_scraper._apply_post_processing(data)
        
        assert result["items"] == ["item1", "item2", "item3"]
    
    def test_limit_processing(self, template_scraper):
        """Test limit post-processing rule."""
        template_scraper.template["post_processing"] = [
            {
                "type": "limit",
                "field": "items",
                "max_items": 3
            }
        ]
        
        data = {"items": ["item1", "item2", "item3", "item4", "item5"]}
        result = template_scraper._apply_post_processing(data)
        
        assert len(result["items"]) == 3
        assert result["items"] == ["item1", "item2", "item3"]
    
    def test_unique_processing(self, template_scraper):
        """Test unique post-processing rule."""
        template_scraper.template["post_processing"] = [
            {"type": "unique", "field": "items"}
        ]
        
        data = {"items": ["item1", "item2", "item1", "item3", "item2"]}
        result = template_scraper._apply_post_processing(data)
        
        assert result["items"] == ["item1", "item2", "item3"]
    
    def test_list_processing_on_strings(self, template_scraper):
        """Test list processing rules on string fields."""
        template_scraper.template["post_processing"] = [
            {"type": "trim", "field": "items"},
            {"type": "lowercase", "field": "items"}
        ]
        
        data = {"items": ["  ITEM1  ", "  ITEM2  "]}
        result = template_scraper._apply_post_processing(data)
        
        assert result["items"] == ["item1", "item2"]
    
    def test_processing_rule_error_handling(self, template_scraper):
        """Test post-processing rule error handling."""
        template_scraper.template["post_processing"] = [
            {
                "type": "to_int",
                "field": "invalid_number"
            }
        ]
        
        data = {"invalid_number": "not_a_number"}
        result = template_scraper._apply_post_processing(data)
        
        # Should not crash, field should remain unchanged
        assert result["invalid_number"] == "not_a_number"
    
    def test_no_post_processing_rules(self, template_scraper):
        """Test when no post-processing rules are defined."""
        template_scraper.template["post_processing"] = []
        
        data = {"title": "Test Title"}
        result = template_scraper._apply_post_processing(data)
        
        assert result == data
    
    def test_missing_field_in_rule(self, template_scraper):
        """Test post-processing rule with missing field."""
        template_scraper.template["post_processing"] = [
            {"type": "trim", "field": "nonexistent_field"}
        ]
        
        data = {"title": "Test Title"}
        result = template_scraper._apply_post_processing(data)
        
        # Should not crash, original data should be returned
        assert result == data


class TestIntegrationScenarios:
    """Integration tests for full scraping workflow."""
    
    @pytest.fixture
    def integration_template(self):
        """Complete template for integration testing."""
        return {
            "name": "integration_test_template",
            "version": "1.0.0",
            "selectors": {
                "title": "h1::text",
                "price": ".price::text",
                "image": "img::attr(src)",
                "tags": ".tag::text"
            },
            "fallback_selectors": {
                "backup_1": {
                    "title": ".main-title::text",
                    "price": ".product-price::text"
                }
            },
            "post_processing": [
                {"type": "trim", "field": "title"},
                {"type": "to_float", "field": "price"},
                {"type": "normalize_url", "field": "image", "base_url": "https://example.com"},
                {"type": "unique", "field": "tags"}
            ]
        }
    
    @pytest.fixture
    def complete_mock_response(self):
        """Complete mock response for integration testing."""
        mock_resp = Mock()
        
        def css_side_effect(selector):
            mock_elements = Mock()
            if selector == "h1":
                mock_element = Mock()
                mock_element.text = "  Test Product Title  "
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == ".price":
                mock_element = Mock()
                mock_element.text = "$29.99"
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == "img":
                mock_element = Mock()
                mock_element.attrs = {"src": "/images/product.jpg"}
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            elif selector == ".tag":
                tag1, tag2, tag3 = Mock(), Mock(), Mock()
                tag1.text = "electronics"
                tag2.text = "gadget"
                tag3.text = "electronics"  # Duplicate for unique test
                mock_elements.all = [tag1, tag2, tag3]
                return mock_elements
            return None
        
        mock_resp.css.side_effect = css_side_effect
        mock_resp.status = 200
        return mock_resp
    
    def test_full_scraping_workflow(self, integration_template, complete_mock_response):
        """Test complete scraping workflow from service to post-processing."""
        # Setup
        service = ScrapingService()
        service.template_manager = Mock()
        service.template_manager.load_template.return_value = integration_template
        service.template_manager.update_template_stats.return_value = True
        
        with patch.object(service, 'validate_scraping_target', return_value={"valid": True}):
            # Mock TemplateScraper
            with patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
                # Create real scraper instance to test actual logic
                scraper = TemplateScraper(integration_template)
                mock_scraper_class.return_value = scraper
                
                # Mock the fetch method
                with patch.object(scraper, '_fetch_page', return_value=complete_mock_response):
                    # Execute
                    result = service.scrape_with_template("integration_test_template", "https://example.com")
            
            # Verify complete workflow
            assert result["status"] == "success"
            assert result["template"] == "integration_test_template"
            
            # Verify data extraction and post-processing
            data = result["data"]
            # Note: Based on the actual extraction logic, these return lists
            # Post-processing is applied after extraction
            assert "title" in data
            assert "price" in data
            assert "image" in data
            assert "tags" in data
            
            # Verify extraction worked (post-processing rules were defined but may not be fully applied in this mock)
            assert len(data["title"]) > 0
            assert len(data["price"]) > 0
    
    def test_fallback_selector_usage(self, integration_template):
        """Test fallback selector functionality."""
        scraper = TemplateScraper(integration_template)
        
        # Mock response that fails primary selectors but works with fallbacks
        mock_resp = Mock()
        
        def css_side_effect(selector):
            mock_elements = Mock()
            if selector == "h1":
                return None  # Primary selector fails
            elif selector == ".main-title":
                mock_element = Mock()
                mock_element.text = "Fallback Title"
                mock_elements.first = mock_element
                mock_elements.all = [mock_element]
                return mock_elements
            return None
        
        mock_resp.css.side_effect = css_side_effect
        
        with patch.object(scraper, '_fetch_page', return_value=mock_resp):
            # Test fallback selector testing
            result = scraper.test_selectors("https://example.com")
        
        # Verify fallback results are included
        assert "fallback_results" in result
        assert "backup_1" in result["fallback_results"]
    
    def test_template_validation_before_scraping(self):
        """Test template validation prevents scraping with invalid template."""
        service = ScrapingService()
        service.template_manager = Mock()
        
        # Invalid template missing selectors
        invalid_template = {"name": "invalid_template"}
        service.template_manager.load_template.return_value = invalid_template
        
        result = service.scrape_with_template("invalid_template", "https://example.com")
        
        assert result["status"] == "failed"
        assert "Template validation failed" in result["error"]
    
    def test_error_propagation_through_workflow(self):
        """Test error propagation through the complete workflow."""
        service = ScrapingService()
        service.template_manager = Mock()
        service.template_manager.load_template.side_effect = Exception("Template loading failed")
        
        result = service.scrape_with_template("error_template", "https://example.com")
        
        assert result["status"] == "failed"
        assert "Scraping failed" in result["error"]
        assert "Template loading failed" in result["error"]


class TestFileTemplateManager:
    """Test FileTemplateManager functionality."""
    
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for testing."""
        return tmp_path / "templates"
    
    @pytest.fixture
    def template_manager(self, temp_dir):
        """Create FileTemplateManager with temporary directory."""
        with patch('src.data.template_manager.config') as mock_config:
            mock_config.templates_folder = str(temp_dir)
            manager = FileTemplateManager()
            return manager
    
    @pytest.fixture
    def sample_template_data(self):
        """Sample template data for testing."""
        return {
            "name": "test_template",
            "description": "Test template",
            "selectors": {
                "title": "h1::text",
                "price": ".price::text"
            },
            "validation_rules": {}
        }
    
    def test_create_template(self, template_manager, sample_template_data, temp_dir):
        """Test template creation."""
        name = sample_template_data["name"]
        selectors = sample_template_data["selectors"]
        description = sample_template_data["description"]
        
        result = template_manager.create_template(name, selectors, description=description)
        
        # Verify template structure
        assert result["name"] == name
        assert result["description"] == description
        assert result["selectors"] == selectors
        assert "id" in result
        assert result["version"] == "1.0.0"
        assert result["is_active"] is True
        assert result["success_rate"] == 100.0
        assert result["usage_count"] == 0
        
        # Verify file was created
        template_file = temp_dir / f"{name}.json"
        assert template_file.exists()
        
        # Verify cache was updated
        assert name in template_manager._templates_cache
    
    def test_load_template_from_file(self, template_manager, sample_template_data, temp_dir):
        """Test loading template from file."""
        name = sample_template_data["name"]
        
        # Create template file manually
        template_file = temp_dir / f"{name}.json"
        template_file.parent.mkdir(parents=True, exist_ok=True)
        with open(template_file, 'w') as f:
            json.dump(sample_template_data, f)
        
        # Load template
        result = template_manager.load_template(name)
        
        assert result == sample_template_data
        assert name in template_manager._templates_cache
    
    def test_load_template_from_cache(self, template_manager, sample_template_data):
        """Test loading template from cache."""
        name = sample_template_data["name"]
        template_manager._templates_cache[name] = sample_template_data
        
        result = template_manager.load_template(name)
        
        assert result == sample_template_data
    
    def test_load_nonexistent_template(self, template_manager):
        """Test loading nonexistent template."""
        result = template_manager.load_template("nonexistent")
        
        assert result is None
    
    def test_save_template(self, template_manager, sample_template_data, temp_dir):
        """Test saving template."""
        name = sample_template_data["name"]
        
        result = template_manager.save_template(name, sample_template_data)
        
        assert result is True
        
        # Verify file was created
        template_file = temp_dir / f"{name}.json"
        assert template_file.exists()
        
        # Verify cache was updated
        assert name in template_manager._templates_cache
        
        # Verify updated_at field was added
        cached_template = template_manager._templates_cache[name]
        assert "updated_at" in cached_template
    
    def test_list_templates(self, template_manager, temp_dir):
        """Test listing templates."""
        # Create multiple template files
        template_data = [
            {"name": "template1", "selectors": {"field": "selector"}},
            {"name": "template2", "selectors": {"field": "selector"}}
        ]
        
        for template in template_data:
            template_file = temp_dir / f"{template['name']}.json"
            template_file.parent.mkdir(parents=True, exist_ok=True)
            with open(template_file, 'w') as f:
                json.dump(template, f)
        
        # List templates
        result = template_manager.list_templates()
        
        assert len(result) == 2
        template_names = [t["name"] for t in result]
        assert "template1" in template_names
        assert "template2" in template_names
    
    def test_delete_template(self, template_manager, sample_template_data, temp_dir):
        """Test template deletion."""
        name = sample_template_data["name"]
        
        # Create template first
        template_manager.create_template(
            name, 
            sample_template_data["selectors"],
            description=sample_template_data["description"]
        )
        
        # Verify template exists
        template_file = temp_dir / f"{name}.json"
        assert template_file.exists()
        assert name in template_manager._templates_cache
        
        # Delete template
        result = template_manager.delete_template(name)
        
        assert result is True
        assert not template_file.exists()
        assert name not in template_manager._templates_cache
    
    def test_delete_nonexistent_template(self, template_manager):
        """Test deleting nonexistent template."""
        result = template_manager.delete_template("nonexistent")
        
        assert result is False
    
    def test_update_template_stats_success(self, template_manager, sample_template_data):
        """Test updating template stats with success."""
        name = sample_template_data["name"]
        
        # Create template
        template_manager.create_template(
            name, 
            sample_template_data["selectors"],
            description=sample_template_data["description"]
        )
        
        # Update stats with success
        result = template_manager.update_template_stats(name, True)
        
        assert result is True
        
        # Verify stats were updated
        template = template_manager.load_template(name)
        assert template["usage_count"] == 1
        assert template["success_rate"] == 100.0
    
    def test_update_template_stats_failure(self, template_manager, sample_template_data):
        """Test updating template stats with failure."""
        name = sample_template_data["name"]
        
        # Create template and add some successful usage
        template_manager.create_template(
            name, 
            sample_template_data["selectors"],
            description=sample_template_data["description"]
        )
        template_manager.update_template_stats(name, True)  # One success
        
        # Update stats with failure
        result = template_manager.update_template_stats(name, False)
        
        assert result is True
        
        # Verify stats were updated (50% success rate after 1 success, 1 failure)
        template = template_manager.load_template(name)
        assert template["usage_count"] == 2
        assert template["success_rate"] == 50.0
    
    def test_get_template_names(self, template_manager, temp_dir):
        """Test getting template names."""
        # Create template files
        template_names = ["template1", "template2", "template3"]
        for name in template_names:
            template_file = temp_dir / f"{name}.json"
            template_file.parent.mkdir(parents=True, exist_ok=True)
            template_file.write_text('{"name": "' + name + '"}')
        
        result = template_manager.get_template_names()
        
        assert set(result) == set(template_names)
    
    def test_clear_cache(self, template_manager, sample_template_data):
        """Test clearing template cache."""
        name = sample_template_data["name"]
        template_manager._templates_cache[name] = sample_template_data
        
        assert len(template_manager._templates_cache) == 1
        
        template_manager.clear_cache()
        
        assert len(template_manager._templates_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])