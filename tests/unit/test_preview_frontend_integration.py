"""Tests to ensure preview scraping responses match frontend expectations."""

import pytest
from unittest.mock import patch, Mock
from src.services.scraping_service import ScrapingService


class TestPreviewFrontendIntegration:
    """Test that preview responses match what the frontend expects."""
    
    @pytest.fixture
    def scraping_service(self):
        return ScrapingService()
    
    def test_preview_response_schema_validation(self, scraping_service, sample_valid_template, 
                                                mock_successful_selector_results, 
                                                mock_successful_scraping_result):
        """Test that preview response matches expected schema for frontend."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            # Execute preview
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Validate response structure matches frontend expectations
            self._validate_preview_response_schema(result)
    
    def test_preview_success_response_fields(self, scraping_service, sample_valid_template, 
                                            mock_successful_selector_results, 
                                            mock_successful_scraping_result):
        """Test successful preview response has all required fields."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Success response validation
            assert result["success"] is True
            assert "error" not in result or result.get("error") is None
            
            # Validate preview field structure
            preview = result["preview"]
            assert isinstance(preview["count"], int)
            assert isinstance(preview["success_rate"], str)
            assert preview["success_rate"].endswith("%")
            assert isinstance(preview["sample_data"], list)
            
            # Validate preview_data field structure
            preview_data = result["preview_data"]
            assert isinstance(preview_data["title"], str)
            assert isinstance(preview_data["items_found"], int)
            assert isinstance(preview_data["selectors_matched"], int)
            assert isinstance(preview_data["sample_data"], list)
            assert isinstance(preview_data["fields_extracted"], list)
            assert isinstance(preview_data["validation_results"], dict)
    
    def test_preview_error_response_fields(self, scraping_service):
        """Test error preview response has all required fields."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate:
            # Force validation failure
            mock_validate.return_value = {
                "valid": False,
                "error": "Invalid URL format"
            }
            
            result = scraping_service.preview_scraping("invalid-url", "test_template")
            
            # Error response validation
            assert result["success"] is False
            assert "error" in result
            assert isinstance(result["error"], str)
            assert len(result["error"]) > 0
            
            # Validate that even error responses have consistent structure
            self._validate_preview_response_schema(result)
            
            # Validate error response defaults
            assert result["preview"]["count"] == 0
            assert result["preview"]["success_rate"] == "0%"
            assert result["preview"]["sample_data"] == []
            assert result["preview_data"]["items_found"] == 0
            assert result["preview_data"]["selectors_matched"] == 0
    
    def test_sample_data_structure_for_frontend(self, scraping_service, sample_valid_template, 
                                               mock_successful_selector_results):
        """Test that sample data structure is appropriate for frontend display."""
        # Create detailed scraping result with various data types
        detailed_scraping_result = {
            "status": "success",
            "data": {
                "title": "Product Name",
                "description": "A detailed description of the product with multiple sentences and information.",
                "price": "$123.45",
                "tags": ["electronics", "gadgets", "tech", "mobile"],
                "specifications": ["Spec 1", "Spec 2", "Spec 3", "Spec 4", "Spec 5"],
                "url": "https://example.com/product/123",
                "rating": "4.5 stars",
                "availability": "In Stock"
            },
            "items_count": 8
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = detailed_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Validate sample data structure for frontend consumption
            sample_data = result["preview_data"]["sample_data"]
            assert isinstance(sample_data, list)
            assert len(sample_data) > 0
            
            # Check each sample data entry structure
            for entry in sample_data:
                assert "field" in entry
                assert "value" in entry
                assert isinstance(entry["field"], str)
                
                # Frontend expects specific structure based on data type
                if "type" in entry:
                    if entry["type"] == "list":
                        assert "count" in entry
                        assert isinstance(entry["count"], int)
                        # Value should be truncated list or single item for display
                        assert isinstance(entry["value"], (list, str))
                        if isinstance(entry["value"], list):
                            assert len(entry["value"]) <= 3  # Max 3 items for preview
                    elif entry["type"] == "string":
                        assert isinstance(entry["value"], str)
                        # Long strings should be truncated
                        assert len(entry["value"]) <= 203  # 200 + "..."
    
    def test_validation_results_structure_for_frontend(self, scraping_service, sample_valid_template, 
                                                       mock_partial_selector_results, 
                                                       mock_successful_scraping_result):
        """Test validation results structure is suitable for frontend display."""
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_partial_selector_results
            mock_scraper.scrape.return_value = mock_successful_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Validate validation_results structure
            validation_results = result["preview_data"]["validation_results"]
            
            # Required fields for frontend display
            assert "template_valid" in validation_results
            assert "selectors_working" in validation_results
            assert "total_selectors" in validation_results
            assert "success_rate" in validation_results
            assert "detailed_results" in validation_results
            
            # Type validations for frontend consumption
            assert isinstance(validation_results["template_valid"], bool)
            assert isinstance(validation_results["selectors_working"], int)
            assert isinstance(validation_results["total_selectors"], int)
            assert isinstance(validation_results["success_rate"], (int, float))
            assert isinstance(validation_results["detailed_results"], dict)
            
            # Detailed results should be suitable for frontend table/list display
            detailed_results = validation_results["detailed_results"]
            for field_name, result in detailed_results.items():
                assert isinstance(field_name, str)
                assert isinstance(result, dict)
                assert "found" in result
                assert "element_count" in result
                assert "sample_value" in result
                assert isinstance(result["found"], bool)
                assert isinstance(result["element_count"], int)
    
    def test_success_rate_formatting(self, scraping_service, sample_valid_template, 
                                    mock_successful_scraping_result):
        """Test that success rate is properly formatted for frontend display."""
        # Test different success rates
        test_cases = [
            {"successful": 0, "total": 4, "expected": "0%"},
            {"successful": 1, "total": 4, "expected": "25%"},
            {"successful": 2, "total": 4, "expected": "50%"},
            {"successful": 3, "total": 4, "expected": "75%"},
            {"successful": 4, "total": 4, "expected": "100%"},
            {"successful": 2, "total": 3, "expected": "67%"},  # Test rounding
        ]
        
        for test_case in test_cases:
            selector_results = {
                "selector_results": {
                    f"field_{i}": {
                        "found": i < test_case["successful"],
                        "element_count": 1 if i < test_case["successful"] else 0
                    }
                    for i in range(test_case["total"])
                },
                "statistics": {
                    "total_selectors": test_case["total"],
                    "successful_selectors": test_case["successful"],
                    "success_rate": (test_case["successful"] / test_case["total"]) * 100 if test_case["total"] > 0 else 0
                }
            }
            
            with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
                 patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
                 patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
                
                # Setup mocks
                mock_validate.return_value = {"valid": True}
                mock_load.return_value = sample_valid_template
                
                mock_scraper = Mock()
                mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
                mock_scraper.test_selectors.return_value = selector_results
                mock_scraper.scrape.return_value = mock_successful_scraping_result
                mock_scraper_class.return_value = mock_scraper
                
                result = scraping_service.preview_scraping("https://example.com", "test_template")
                
                # Verify success rate formatting
                assert result["preview"]["success_rate"] == test_case["expected"]
    
    def test_title_extraction_priority(self, scraping_service, sample_valid_template, 
                                      mock_successful_selector_results):
        """Test that title extraction follows correct priority for frontend display."""
        # Test title extraction from scraped data
        scraping_result_with_title = {
            "status": "success",
            "data": {
                "title": "Product Title from Scraping",
                "name": "Product Name from Scraping",
                "heading": "Heading from Scraping",
                "other_field": "Other data"
            },
            "items_count": 1
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = scraping_result_with_title
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Should prioritize 'title' field
            assert result["preview_data"]["title"] == "Product Title from Scraping"
    
    def test_fallback_title_from_selectors(self, scraping_service, sample_valid_template, 
                                          mock_successful_scraping_result):
        """Test title fallback from selector results when scraping doesn't provide title."""
        # Scraping result without title fields
        scraping_without_title = {
            "status": "success",
            "data": {
                "description": "Product description",
                "price": "$99.99"
            },
            "items_count": 1
        }
        
        # Selector results with title
        selector_results_with_title = {
            "selector_results": {
                "title": {
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Title from Selector Test",
                    "error": None
                },
                "description": {
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Description sample"
                }
            },
            "statistics": {
                "total_selectors": 2,
                "successful_selectors": 2,
                "success_rate": 100.0
            }
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = selector_results_with_title
            mock_scraper.scrape.return_value = scraping_without_title
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Should use title from selector results
            assert result["preview_data"]["title"] == "Title from Selector Test"
    
    def test_items_count_calculation_logic(self, scraping_service, sample_valid_template):
        """Test items count calculation logic for frontend display."""
        # Test case where scraping provides items_count
        scraping_with_count = {
            "status": "success",
            "data": {"title": "Test"},
            "items_count": 15
        }
        
        selector_results = {
            "selector_results": {
                "title": {"found": True, "element_count": 1}
            },
            "statistics": {"total_selectors": 1, "successful_selectors": 1, "success_rate": 100.0}
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = selector_results
            mock_scraper.scrape.return_value = scraping_with_count
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            # Should use items_count from scraping result
            assert result["preview"]["count"] == 15
            assert result["preview_data"]["items_found"] == 15
    
    def test_fields_extracted_list_accuracy(self, scraping_service, sample_valid_template, 
                                           mock_successful_selector_results):
        """Test that fields_extracted list accurately reflects scraped fields."""
        detailed_scraping_result = {
            "status": "success",
            "data": {
                "title": "Product Title",
                "description": "Product Description",
                "empty_field": "",  # Should not be included
                "null_field": None,  # Should not be included
                "price": "$99.99",
                "tags": ["tag1", "tag2"],
                "empty_list": [],  # Should not be included
                "specifications": ["spec1", "spec2", "spec3"]
            },
            "items_count": 3
        }
        
        with patch.object(scraping_service, 'validate_scraping_target') as mock_validate, \
             patch.object(scraping_service.template_manager, 'load_template') as mock_load, \
             patch('src.scrapers.template_scraper.TemplateScraper') as mock_scraper_class:
            
            # Setup mocks
            mock_validate.return_value = {"valid": True}
            mock_load.return_value = sample_valid_template
            
            mock_scraper = Mock()
            mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
            mock_scraper.test_selectors.return_value = mock_successful_selector_results
            mock_scraper.scrape.return_value = detailed_scraping_result
            mock_scraper_class.return_value = mock_scraper
            
            result = scraping_service.preview_scraping("https://example.com", "test_template")
            
            fields_extracted = result["preview_data"]["fields_extracted"]
            
            # Should only include fields with actual data
            expected_fields = {"title", "description", "price", "tags", "specifications"}
            assert set(fields_extracted) == expected_fields
            
            # Should not include empty/null fields
            assert "empty_field" not in fields_extracted
            assert "null_field" not in fields_extracted
            assert "empty_list" not in fields_extracted
    
    def _validate_preview_response_schema(self, response):
        """Helper method to validate preview response schema."""
        # Top-level required fields
        required_top_level = ["url", "template_id", "success", "preview", "preview_data"]
        for field in required_top_level:
            assert field in response, f"Missing top-level field: {field}"
        
        # Preview object validation
        preview = response["preview"]
        assert isinstance(preview, dict)
        required_preview_fields = ["count", "success_rate", "sample_data"]
        for field in required_preview_fields:
            assert field in preview, f"Missing preview field: {field}"
        
        # Preview data validation
        preview_data = response["preview_data"]
        assert isinstance(preview_data, dict)
        required_preview_data_fields = [
            "title", "items_found", "selectors_matched", 
            "sample_data", "fields_extracted", "validation_results"
        ]
        for field in required_preview_data_fields:
            assert field in preview_data, f"Missing preview_data field: {field}"
        
        # Type validations
        assert isinstance(response["url"], str)
        assert isinstance(response["template_id"], str)
        assert isinstance(response["success"], bool)
        assert isinstance(preview["count"], int)
        assert isinstance(preview["success_rate"], str)
        assert isinstance(preview["sample_data"], list)
        assert isinstance(preview_data["title"], str)
        assert isinstance(preview_data["items_found"], int)
        assert isinstance(preview_data["selectors_matched"], int)
        assert isinstance(preview_data["sample_data"], list)
        assert isinstance(preview_data["fields_extracted"], list)
        assert isinstance(preview_data["validation_results"], dict)