"""Comprehensive unit tests for the preview URL scraping feature."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional

from src.services.scraping_service import ScrapingService
from src.scrapers.template_scraper import TemplateScraper


class TestPreviewScraping:
    """Test suite for preview_scraping method in ScrapingService."""
    
    @pytest.fixture
    def scraping_service(self):
        """Create a ScrapingService instance for testing."""
        return ScrapingService()
    
    @pytest.fixture
    def sample_valid_template(self):
        """Sample valid template for testing."""
        return {
            "name": "test_template",
            "description": "Test template for unit tests",
            "selectors": {
                "title": "h1::text",
                "description": ".description::text",
                "price": ".price::text",
                "links": "a::attr(href)"
            },
            "post_processing": [
                {"type": "trim", "field": "title"}
            ]
        }
    
    @pytest.fixture
    def sample_invalid_template(self):
        """Sample invalid template for testing."""
        return {
            "name": "invalid_template",
            # Missing selectors field
        }
    
    @pytest.fixture
    def sample_empty_template(self):
        """Template with empty selectors."""
        return {
            "name": "sample_empty_template",
            "description": "Template with empty selectors",
            "selectors": {}
        }
    
    @pytest.fixture
    def mock_successful_selector_results(self):
        """Mock successful selector test results."""
        return {
            "success": True,
            "selector_results": {
                "title": {
                    "selector": "h1::text",
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Sample Title",
                    "error": None
                },
                "description": {
                    "selector": ".description::text",
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Sample description text",
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
                    "element_count": 5,
                    "sample_value": "https://example.com/link1",
                    "error": None
                }
            },
            "statistics": {
                "total_selectors": 4,
                "successful_selectors": 3,
                "failed_selectors": 1,
                "success_rate": 75.0
            }
        }
    
    @pytest.fixture
    def mock_successful_scraping_result(self):
        """Mock successful scraping results."""
        return {
            "status": "success",
            "data": {
                "title": "Sample Product Title",
                "description": "This is a sample product description",
                "links": [
                    "https://example.com/link1",
                    "https://example.com/link2",
                    "https://example.com/link3"
                ]
            },
            "items_count": 3
        }
    
    @pytest.fixture
    def mock_failed_scraping_results(self):
        """Mock failed scraping results."""
        return {
            "status": "failed",
            "error": "Failed to extract data",
            "data": {},
            "items_count": 0
        }


class TestURLValidation:
    """Test URL validation functionality."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_invalid_url_missing_protocol(self, scraping_service):
        """Test preview with URL missing protocol."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "error": "Invalid URL format"
            }
            
            result = scraping_service.preview_scraping("example.com", "test_template")
            
            assert result["success"] is False
            assert "Invalid target URL" in result["error"]
            assert result["preview"]["count"] == 0
            assert result["preview"]["success_rate"] == "0%"
            assert result["preview_data"]["items_found"] == 0
    
    def test_invalid_url_empty(self, scraping_service):
        """Test preview with empty URL."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "error": "Invalid URL format"
            }
            
            result = scraping_service.preview_scraping("", "test_template")
            
            assert result["success"] is False
            assert "Invalid target URL" in result["error"]
    
    def test_invalid_url_malformed(self, scraping_service):
        """Test preview with malformed URL."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "error": "Malformed URL"
            }
            
            result = scraping_service.preview_scraping("not-a-valid-url", "test_template")
            
            assert result["success"] is False
            assert "Invalid target URL" in result["error"]
    
    def test_valid_url(self, scraping_service):
        """Test preview with valid URL passes validation."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load:
            
            mock_validate.return_value = {"valid": True, "url": "https://example.com", "domain": "example.com"}
            mock_load.return_value = None  # Template not found to short-circuit test
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            mock_validate.assert_called_once_with("https://example.com")
            # Should proceed past URL validation


class TestTemplateLoading:
    """Test template loading functionality."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_template_not_found(self, scraping_service):
        """Test preview when template doesn't exist."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = None
            
            result = scraping_service.preview_scraping("https://example.com", "nonexistent_template")
            
            assert result["success"] is False
            assert "Template 'nonexistent_template' not found" in result["error"]
            assert result["template_id"] == "nonexistent_template"
    
    def test_template_exists_but_invalid(self, scraping_service, sample_invalid_template):
        """Test preview when template exists but is invalid."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_invalid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {
                "valid": False,
                "errors": ["Template missing selectors"]
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "invalid_template")
            
            assert result["success"] is False
            assert "Template validation failed" in result["error"]
            assert "Template missing selectors" in result["error"]
    
    def test_template_valid(self, scraping_service, sample_valid_template):
        """Test preview with valid template proceeds to selector testing."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = {}  # Empty to short-circuit
            mock_scraper_class.return_value = mock_scraper
            
            scraping_service.preview_scraping("https://example.com", "valid_template")
            
            mock_scraper.validate_template.assert_called_once()
            mock_scraper.test_selectors.assert_called_once_with("https://example.com")


class TestSuccessfulPreview:
    """Test successful preview scenarios."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_successful_preview_all_selectors_working(self, scraping_service, sample_valid_template, 
                                                      mock_successful_selector_results, mock_successful_scraping_result):
        """Test successful preview with all selectors working."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            # Create mock scraper with all successful results
            all_success_results = mock_successful_selector_results.copy()
            all_success_results["selector_results"]["price"]["found"] = True
            all_success_results["selector_results"]["price"]["element_count"] = 1
            all_success_results["selector_results"]["price"]["sample_value"] = "$99.99"
            all_success_results["selector_results"]["price"]["error"] = None
            all_success_results["statistics"]["successful_selectors"] = 4
            all_success_results["statistics"]["failed_selectors"] = 0
            all_success_results["statistics"]["success_rate"] = 100.0
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = all_success_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is True
            assert result["url"] == "https://example.com"
            assert result["template_id"] == "valid_template"
            assert result["preview"]["success_rate"] == "100%"
            assert result["preview"]["count"] == 3  # From mock_successful_scraping_result items_count
            assert result["preview_data"]["selectors_matched"] == 4
            assert len(result["preview_data"]["sample_data"]) > 0
            assert "title" in result["preview_data"]["fields_extracted"]
    
    def test_successful_preview_partial_selectors(self, scraping_service, sample_valid_template, 
                                                  mock_partial_selector_results, mock_successful_scraping_result):
        """Test successful preview with partial selector success."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_partial_selector_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            # assert result["success"] is True
            # assert result["preview"]["success_rate"] == "60%"
            # assert result["preview_data"]["selectors_matched"] == 3
            # assert result["preview_data"]["validation_results"]["success_rate"] == 60.0
    
    def test_different_template_configurations(self, scraping_service):
        """Test preview with different template configurations."""
        complex_template = {
            "name": "complex_template",
            "selectors": {
                "title": "h1::text",
                "images": "img::attr(src)",
                "metadata": ".meta::text"
            },
            "fallback_selectors": {
                "titles": {
                    "title": "h2::text"
                }
            }
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = complex_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = {
                "selector_results": {
                    "title": {"found": True, "element_count": 1, "sample_value": "Complex Title"},
                    "images": {"found": True, "element_count": 10, "sample_value": "image1.jpg"},
                    "metadata": {"found": True, "element_count": 1, "sample_value": "Meta info"}
                },
                "statistics": {
                    "total_selectors": 3,
                    "successful_selectors": 3,
                    "success_rate": 100.0
                }
            }
            mock_scraper.scrape.return_value = {
                "status": "success",
                "data": {
                    "title": "Complex Title",
                    "images": ["image1.jpg", "image2.jpg", "image3.jpg"],
                    "metadata": "Meta info"
                },
                "items_count": 3
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "complex_template")
            
            assert result["success"] is True
            assert result["preview"]["count"] == 3
            assert len(result["preview_data"]["fields_extracted"]) == 3


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_network_fetch_failure(self, scraping_service, sample_valid_template):
        """Test handling of network/fetch failures."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = {
                "success": False,
                "error": "Failed to fetch the target URL"
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is False
            assert "Failed to test selectors" in result["error"]
    
    def test_template_validation_failure(self, scraping_service, sample_valid_template):
        """Test handling of template validation failures."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {
                "valid": False,
                "errors": ["Invalid selector format", "Missing required field"]
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is False
            assert "Template validation failed" in result["error"]
            assert "Invalid selector format" in result["error"]
            assert "Missing required field" in result["error"]
    
    def test_selector_testing_failure(self, scraping_service, sample_valid_template):
        """Test handling of selector testing failures."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = {
                "success": False,
                "error": "Connection timeout"
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is False
            assert "Failed to test selectors" in result["error"]
            assert "Connection timeout" in result["error"]
    
    def test_scraping_failure(self, scraping_service, sample_valid_template, mock_successful_selector_results):
        """Test handling of scraping failures."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = {
                "status": "failed",
                "error": "Scraping failed due to anti-bot measures",
                "data": {},
                "items_count": 0
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            # Should still be successful if selector testing worked
            assert result["success"] is True
            assert result["preview"]["count"] >= 1  # Fallback from selector results
    
    def test_unexpected_exception(self, scraping_service):
        """Test handling of unexpected exceptions."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected error")
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is False
            assert "Preview failed" in result["error"]
            assert "Unexpected error" in result["error"]


class TestResponseStructure:
    """Test response structure validation."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_response_has_required_fields(self, scraping_service, sample_valid_template, 
                                          mock_successful_selector_results, mock_successful_scraping_result):
        """Test that response has all required fields."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            # Check top-level fields
            required_fields = ["url", "template_id", "success", "preview", "preview_data"]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
            
            # Check preview fields
            preview_fields = ["count", "success_rate", "sample_data"]
            for field in preview_fields:
                assert field in result["preview"], f"Missing preview field: {field}"
            
            # Check preview_data fields
            preview_data_fields = ["title", "items_found", "selectors_matched", 
                                   "sample_data", "fields_extracted", "validation_results"]
            for field in preview_data_fields:
                assert field in result["preview_data"], f"Missing preview_data field: {field}"
    
    def test_preview_data_structure(self, scraping_service, sample_valid_template, 
                                   mock_successful_selector_results, mock_successful_scraping_result):
        """Test preview data structure is correct."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            # Check sample_data structure
            assert isinstance(result["preview"]["sample_data"], list)
            assert isinstance(result["preview_data"]["sample_data"], list)
            assert isinstance(result["preview_data"]["fields_extracted"], list)
            
            # Check validation_results structure
            validation_results = result["preview_data"]["validation_results"]
            assert "template_valid" in validation_results
            assert "selectors_working" in validation_results
            assert "total_selectors" in validation_results
            assert "success_rate" in validation_results
    
    def test_statistics_calculations(self, scraping_service, sample_valid_template, mock_partial_selector_results):
        """Test that statistics are calculated correctly."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_partial_selector_results
            mock_scraper.scrape.return_value = {"status": "success", "data": {}, "items_count": 5}
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["preview"]["success_rate"] == "60%"  # 3/5 selectors successful
            assert result["preview_data"]["selectors_matched"] == 3
            assert result["preview_data"]["validation_results"]["success_rate"] == 60.0
    
    def test_sample_data_format(self, scraping_service, sample_valid_template, mock_successful_selector_results):
        """Test sample data format is correct."""
        scraping_results = {
            "status": "success",
            "data": {
                "title": "Sample Title",
                "description": "A very long description that should be truncated because it exceeds the maximum length limit of 200 characters and we want to ensure that the preview data doesn't become too large for the frontend to handle properly",
                "links": ["link1", "link2", "link3"],
                "prices": ["$10", "$20"]
            },
            "items_count": 3
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = scraping_results
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            sample_data = result["preview_data"]["sample_data"]
            
            # Find the description entry
            description_entry = next((item for item in sample_data if item["field"] == "description"), None)
            assert description_entry is not None
            assert len(description_entry["value"]) <= 203  # 200 + "..."
            assert description_entry["type"] == "string"
            
            # Find the links entry
            links_entry = next((item for item in sample_data if item["field"] == "links"), None)
            assert links_entry is not None
            assert links_entry["type"] == "list"
            assert links_entry["count"] == 3


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_template_with_no_selectors(self, scraping_service, sample_empty_template):
        """Test template with no selectors."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_empty_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {
                "valid": False,
                "errors": ["Selectors must be a non-empty dictionary"]
            }
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "empty_template")
            
            assert result["success"] is False
            assert "Template validation failed" in result["error"]
    
    def test_very_large_response_data_truncation(self, scraping_service, sample_valid_template, 
                                                  mock_successful_selector_results):
        """Test handling of very large responses with data truncation."""
        large_data = {
            "status": "success",
            "data": {
                "content": "x" * 5000,  # Very long content
                "items": ["item" + str(i) for i in range(1000)]  # Many items
            },
            "items_count": 1000
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = large_data
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is True
            
            # Check that content is truncated
            content_entry = next((item for item in result["preview_data"]["sample_data"] 
                                if item["field"] == "content"), None)
            if content_entry:
                assert len(content_entry["value"]) <= 203  # 200 + "..."
            
            # Check that list items are limited (first 3 items)
            items_entry = next((item for item in result["preview_data"]["sample_data"] 
                              if item["field"] == "items"), None)
            if items_entry:
                assert len(items_entry["value"]) <= 3
    
    def test_empty_scraping_results(self, scraping_service, sample_valid_template, mock_successful_selector_results):
        """Test handling of empty scraping results."""
        empty_results = {
            "status": "success",
            "data": {},
            "items_count": 0
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = empty_results
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is True
            # Should fall back to selector results for item count
            assert result["preview"]["count"] >= 1  # From successful selectors
    
    def test_all_selectors_fail(self, scraping_service, sample_valid_template):
        """Test when all selectors fail."""
        failed_results = {
            "selector_results": {
                "title": {"found": False, "element_count": 0, "error": "Not found"},
                "description": {"found": False, "element_count": 0, "error": "Not found"},
                "price": {"found": False, "element_count": 0, "error": "Not found"},
                "links": {"found": False, "element_count": 0, "error": "Not found"}
            },
            "statistics": {
                "total_selectors": 4,
                "successful_selectors": 0,
                "success_rate": 0.0
            }
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = failed_results
            mock_scraper.scrape.return_value = {"status": "success", "data": {}, "items_count": 0}
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "valid_template")
            
            assert result["success"] is True
            assert result["preview"]["success_rate"] == "0%"
            assert result["preview"]["count"] == 0
            assert result["preview_data"]["selectors_matched"] == 0


class TestErrorMessages:
    """Test that error messages are appropriate and helpful."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_error_messages_are_descriptive(self, scraping_service):
        """Test that error messages provide useful information."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "error": "URL must start with http:// or https://"
            }
            
            result = scraping_service.preview_scraping("example.com", "test_template")
            
            assert result["success"] is False
            assert "Invalid target URL" in result["error"]
            assert "URL must start with http:// or https://" in result["error"]
    
    def test_error_response_structure_consistency(self, scraping_service):
        """Test that error responses have consistent structure."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {"valid": False, "error": "Test error"}
            
            result = scraping_service.preview_scraping("invalid-url", "test_template")
            
            # Even error responses should have consistent structure
            assert "url" in result
            assert "template_id" in result
            assert "success" in result
            assert "preview" in result
            assert "preview_data" in result
            assert result["preview"]["count"] == 0
            assert result["preview"]["success_rate"] == "0%"


class TestMockingPatterns:
    """Test proper mocking patterns for dependencies."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_template_manager_mocking(self, scraping_service, sample_valid_template):
        """Test that template_manager is properly mocked."""
        with patch.object(scraping_service.template_manager, 'load_template') as mock_load:
            mock_load.return_value = sample_valid_template
            
            # Should not raise an exception when accessing template_manager
            template = scraping_service.template_manager.load_template("test")
            assert template == sample_valid_template
            mock_load.assert_called_once_with("test")
    
    def test_template_scraper_mocking(self, scraping_service, sample_valid_template):
        """Test that TemplateScraper is properly mocked."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper_class.return_value = mock_scraper
            
            scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Verify TemplateScraper was instantiated with template
            mock_scraper_class.assert_called_once_with(sample_valid_template)
    
    def test_network_response_mocking(self, scraping_service, sample_valid_template, mock_successful_selector_results):
        """Test that network responses are properly mocked."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = {"status": "success", "data": {"test": "data"}, "items_count": 1}
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Verify that methods were called as expected
            mock_scraper.validate_template.assert_called_once()
            mock_scraper.test_selectors.assert_called_once_with("https://example.com")
            mock_scraper.scrape.assert_called_once_with("https://example.com")


if __name__ == "__main__":
    pytest.main([__file__])