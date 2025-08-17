"""Test cases for scraping preview functionality."""

import pytest
from unittest.mock import Mock, patch
from src.services.scraping_service import ScrapingService


class TestScrapingPreview:
    """Test cases for preview_scraping method."""
    
    def setup_method(self):
        """Set up test environment."""
        self.scraping_service = ScrapingService()
    
    def test_preview_scraping_invalid_url(self):
        """Test preview with invalid URL."""
        result = self.scraping_service.preview_scraping("invalid-url", "test_template")
        
        assert result["success"] is False
        assert "Invalid target URL" in result["error"]
        assert result["url"] == "invalid-url"
        assert result["template_id"] == "test_template"
        assert result["preview"]["count"] == 0
        assert result["preview"]["success_rate"] == "0%"
        assert result["preview_data"]["items_found"] == 0
    
    def test_preview_scraping_template_not_found(self):
        """Test preview with non-existent template."""
        with patch.object(self.scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(self.scraping_service.template_manager, 'load_template') as mock_load:
                mock_load.return_value = None
                
                result = self.scraping_service.preview_scraping("https://example.com", "non_existent")
                
                assert result["success"] is False
                assert "Template 'non_existent' not found" in result["error"]
                assert result["preview"]["count"] == 0
                assert result["preview_data"]["selectors_matched"] == 0
    
    @patch('src.scrapers.template_scraper.TemplateScraper')
    def test_preview_scraping_success(self, mock_scraper_class):
        """Test successful preview scraping."""
        # Mock template data
        mock_template = {
            "name": "test_template",
            "selectors": {
                "title": "h1::text",
                "description": ".description::text"
            }
        }
        
        # Mock TemplateScraper instance
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock validation
        mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
        
        # Mock selector testing
        mock_scraper.test_selectors.return_value = {
            "success": True,
            "selector_results": {
                "title": {
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Test Title"
                },
                "description": {
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Test Description"
                }
            },
            "statistics": {
                "total_selectors": 2,
                "successful_selectors": 2,
                "success_rate": 100.0
            }
        }
        
        # Mock actual scraping
        mock_scraper.scrape.return_value = {
            "status": "success",
            "data": {
                "title": "Test Title",
                "description": "Test Description"
            },
            "items_count": 1
        }
        
        # Mock dependencies
        with patch.object(self.scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(self.scraping_service.template_manager, 'load_template') as mock_load:
                mock_load.return_value = mock_template
                
                result = self.scraping_service.preview_scraping("https://example.com", "test_template")
                
                # Verify success response
                assert result["success"] is True
                assert result["url"] == "https://example.com"
                assert result["template_id"] == "test_template"
                
                # Verify preview data
                assert result["preview"]["count"] == 1
                assert result["preview"]["success_rate"] == "100%"
                assert len(result["preview"]["sample_data"]) == 2
                
                # Verify preview_data
                assert result["preview_data"]["items_found"] == 1
                assert result["preview_data"]["selectors_matched"] == 2
                assert "title" in result["preview_data"]["fields_extracted"]
                assert "description" in result["preview_data"]["fields_extracted"]
                
                # Verify validation results
                validation = result["preview_data"]["validation_results"]
                assert validation["template_valid"] is True
                assert validation["selectors_working"] == 2
                assert validation["total_selectors"] == 2
                assert validation["success_rate"] == 100.0
    
    @patch('src.scrapers.template_scraper.TemplateScraper')
    def test_preview_scraping_partial_success(self, mock_scraper_class):
        """Test preview with some failing selectors."""
        mock_template = {
            "name": "test_template",
            "selectors": {
                "title": "h1::text",
                "missing": ".non-existent::text"
            }
        }
        
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        mock_scraper.validate_template.return_value = {"valid": True, "errors": []}
        
        # One selector works, one fails
        mock_scraper.test_selectors.return_value = {
            "success": False,  # Overall success is false because one selector failed
            "selector_results": {
                "title": {
                    "found": True,
                    "element_count": 1,
                    "sample_value": "Test Title"
                },
                "missing": {
                    "found": False,
                    "element_count": 0,
                    "sample_value": None
                }
            },
            "statistics": {
                "total_selectors": 2,
                "successful_selectors": 1,
                "success_rate": 50.0
            }
        }
        
        mock_scraper.scrape.return_value = {
            "status": "success",
            "data": {
                "title": "Test Title",
                "missing": ""
            },
            "items_count": 1
        }
        
        with patch.object(self.scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(self.scraping_service.template_manager, 'load_template') as mock_load:
                mock_load.return_value = mock_template
                
                result = self.scraping_service.preview_scraping("https://example.com", "test_template")
                
                # Should still be successful but with lower success rate
                assert result["success"] is True
                assert result["preview"]["success_rate"] == "50%"
                assert result["preview_data"]["selectors_matched"] == 1
                assert len(result["preview_data"]["fields_extracted"]) == 1  # Only title has data
    
    def test_preview_scraping_exception_handling(self):
        """Test exception handling in preview_scraping."""
        with patch.object(self.scraping_service, 'validate_scraping_target') as mock_validate:
            mock_validate.side_effect = Exception("Test exception")
            
            result = self.scraping_service.preview_scraping("https://example.com", "test_template")
            
            assert result["success"] is False
            assert "Preview failed: Test exception" in result["error"]
            assert result["preview"]["count"] == 0
            assert result["preview_data"]["validation_results"]["error"] == "Test exception"
    
    def test_preview_data_structure(self):
        """Test that preview response has correct structure."""
        result = self.scraping_service.preview_scraping("invalid-url", "test_template")
        
        # Check required top-level keys
        required_keys = ["url", "template_id", "success", "preview", "preview_data"]
        for key in required_keys:
            assert key in result
        
        # Check preview structure
        preview_keys = ["count", "success_rate", "sample_data"]
        for key in preview_keys:
            assert key in result["preview"]
        
        # Check preview_data structure
        preview_data_keys = [
            "title", "items_found", "selectors_matched", "sample_data",
            "fields_extracted", "validation_results"
        ]
        for key in preview_data_keys:
            assert key in result["preview_data"]