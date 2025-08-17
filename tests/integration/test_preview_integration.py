"""Integration test for preview scraping functionality."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock
from src.services.scraping_service import ScrapingService


class TestPreviewIntegration:
    """Integration tests for the full preview pipeline."""
    
    @pytest.fixture
    def temp_template_dir(self, tmp_path):
        """Create temporary template directory."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        # Create a test template file
        test_template = {
            "id": "test-template-123",
            "name": "test_template",
            "description": "Test template for news articles",
            "version": "1.0.0",
            "selectors": {
                "title": "h1::text",
                "description": ".article-summary::text",
                "author": ".author-name::text",
                "date": ".publish-date::text"
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
                    "type": "trim",
                    "field": "description"
                }
            ],
            "created_at": "2025-01-01T00:00:00.000Z",
            "updated_at": "2025-01-01T00:00:00.000Z",
            "is_active": True,
            "success_rate": 95.0,
            "usage_count": 10
        }
        
        template_file = template_dir / "test_template.json"
        with open(template_file, 'w') as f:
            json.dump(test_template, f, indent=2)
        
        return template_dir
    
    def test_full_preview_integration_success(self, temp_template_dir):
        """Test complete preview functionality from end to end."""
        # Mock the response object from Scrapling
        mock_response = Mock()
        mock_response.status = 200
        mock_response.css = Mock()
        
        # Mock CSS selector responses for each field
        def mock_css_response(selector):
            mock_elements = Mock()
            
            if selector == "h1":
                mock_elements.all = [Mock(text="Breaking News: Major Discovery")]
                mock_elements.first = Mock(text="Breaking News: Major Discovery")
                return mock_elements
            elif selector == ".article-summary":
                mock_elements.all = [Mock(text="Scientists have made a groundbreaking discovery...")]
                mock_elements.first = Mock(text="Scientists have made a groundbreaking discovery...")
                return mock_elements
            elif selector == ".author-name":
                mock_elements.all = [Mock(text="John Reporter")]
                mock_elements.first = Mock(text="John Reporter")
                return mock_elements
            elif selector == ".publish-date":
                mock_elements.all = [Mock(text="2025-01-06")]
                mock_elements.first = Mock(text="2025-01-06")
                return mock_elements
            else:
                # Return empty result for unknown selectors
                mock_elements.all = []
                mock_elements.first = None
                return None
        
        mock_response.css.side_effect = mock_css_response
        
        # Create service with patched template directory
        with patch('src.core.config.config.templates_folder', str(temp_template_dir)):
            scraping_service = ScrapingService()
            
            # Patch fetch_page, test_selectors, and scrape methods
            with patch('src.scrapers.template_scraper.TemplateScraper.fetch_page') as mock_fetch, \
                 patch('src.scrapers.template_scraper.TemplateScraper.test_selectors') as mock_test, \
                 patch('src.scrapers.template_scraper.TemplateScraper.scrape') as mock_scrape:
                    
                mock_fetch.return_value = mock_response
                    
                # Mock the selector test results
                mock_test.return_value = {
                    'selector_results': {
                        'title': {
                            'found': True,
                            'element_count': 1,
                            'sample_value': 'Breaking News: Major Discovery',
                            'selector': 'h1::text'
                        },
                        'description': {
                            'found': True,
                            'element_count': 1,
                            'sample_value': 'Scientists have made a groundbreaking discovery...',
                            'selector': '.article-summary::text'
                        },
                        'author': {
                            'found': True,
                            'element_count': 1,
                            'sample_value': 'John Reporter',
                            'selector': '.author-name::text'
                        },
                        'date': {
                            'found': True,
                            'element_count': 1,
                            'sample_value': '2025-01-06',
                            'selector': '.publish-date::text'
                        }
                    },
                    'statistics': {
                        'total_selectors': 4,
                        'successful_selectors': 4,
                        'success_rate': 100.0
                    }
                }
                
                # Mock the actual scraping result
                mock_scrape.return_value = {
                    'status': 'success',
                    'data': {
                        'title': 'Breaking News: Major Discovery',
                        'description': 'Scientists have made a groundbreaking discovery...',
                        'author': 'John Reporter',
                        'date': '2025-01-06'
                    },
                    'items_count': 4,
                    'template_name': 'test_template',
                    'timestamp': 1234567890
                }
                    
                # Test the preview functionality
                result = scraping_service.preview_scraping(
                    url="https://news-example.com/article/123",
                    template_id="test_template"
                )
            
            # Verify successful response structure
            assert result["success"] is True
            assert result["url"] == "https://news-example.com/article/123"
            assert result["template_id"] == "test_template"
            
            # Verify preview data
            preview = result["preview"]
            assert preview["count"] >= 1
            assert preview["success_rate"] == "100%"  # All selectors should work
            assert len(preview["sample_data"]) == 4  # All fields should have data
            
            # Check specific sample data
            sample_data = {item["field"]: item["value"] for item in preview["sample_data"]}
            assert "title" in sample_data
            assert "Breaking News: Major Discovery" in sample_data["title"]
            assert "description" in sample_data
            assert "Scientists have made" in sample_data["description"]
            assert "author" in sample_data
            assert sample_data["author"] == "John Reporter"
            
            # Verify preview_data details
            preview_data = result["preview_data"]
            assert preview_data["items_found"] >= 1
            assert preview_data["selectors_matched"] == 4
            assert len(preview_data["fields_extracted"]) == 4
            assert "title" in preview_data["fields_extracted"]
            assert "description" in preview_data["fields_extracted"]
            assert "author" in preview_data["fields_extracted"]
            assert "date" in preview_data["fields_extracted"]
            
            # Verify validation results
            validation = preview_data["validation_results"]
            assert validation["template_valid"] is True
            assert validation["selectors_working"] == 4
            assert validation["total_selectors"] == 4
            assert validation["success_rate"] == 100.0
            
            # Check title extraction
            assert "Breaking News" in preview_data["title"]
    
    def test_partial_selector_success_integration(self, temp_template_dir):
        """Test preview with some selectors working and some failing."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.css = Mock()
        
        # Mock CSS selector responses - some work, some don't
        def mock_css_response(selector):
            mock_elements = Mock()
            
            if selector == "h1":
                # Title selector works
                mock_elements.all = [Mock(text="Working Title")]
                mock_elements.first = Mock(text="Working Title")
                return mock_elements
            elif selector == ".article-summary":
                # Description selector works
                mock_elements.all = [Mock(text="This description works")]
                mock_elements.first = Mock(text="This description works")
                return mock_elements
            else:
                # Author and date selectors fail
                return None
        
        mock_response.css.side_effect = mock_css_response
        
        with patch('src.core.config.config.templates_folder', str(temp_template_dir)):
            scraping_service = ScrapingService()
            
            with patch('src.scrapers.template_scraper.TemplateScraper.fetch_page') as mock_fetch, \
                 patch('src.scrapers.template_scraper.TemplateScraper.test_selectors') as mock_test, \
                 patch('src.scrapers.template_scraper.TemplateScraper.scrape') as mock_scrape:
                     
                mock_fetch.return_value = mock_response
                     
                # Mock the selector test results with partial success
                mock_test.return_value = {
                    'selector_results': {
                        'title': {
                            'found': True,
                            'element_count': 1,
                            'sample_value': 'Working Title',
                            'selector': 'h1::text'
                        },
                        'description': {
                            'found': True,
                            'element_count': 1,
                            'sample_value': 'This description works',
                            'selector': '.article-summary::text'
                        },
                        'author': {
                            'found': False,
                            'element_count': 0,
                            'sample_value': '',
                            'selector': '.author-name::text'
                        },
                        'date': {
                            'found': False,
                            'element_count': 0,
                            'sample_value': '',
                            'selector': '.publish-date::text'
                        }
                    },
                    'statistics': {
                        'total_selectors': 4,
                        'successful_selectors': 2,
                        'success_rate': 50.0
                    }
                }
                
                # Mock the actual scraping result with partial data
                mock_scrape.return_value = {
                    'status': 'success',
                    'data': {
                        'title': 'Working Title',
                        'description': 'This description works'
                        # author and date are missing
                    },
                    'items_count': 2,
                    'template_name': 'test_template',
                    'timestamp': 1234567890
                }
                
                result = scraping_service.preview_scraping(
                    url="https://partial-example.com/article/456",
                    template_id="test_template"
                )
            
            # Should still be successful overall
            assert result["success"] is True
            
            # But success rate should be lower
            preview = result["preview"]
            assert preview["success_rate"] == "50%"  # 2 out of 4 selectors work
            
            preview_data = result["preview_data"]
            assert preview_data["selectors_matched"] == 2
            assert len(preview_data["fields_extracted"]) == 2  # Only fields with data
            assert "title" in preview_data["fields_extracted"]
            assert "description" in preview_data["fields_extracted"]
            assert "author" not in preview_data["fields_extracted"]
            assert "date" not in preview_data["fields_extracted"]
    
    def test_template_not_found_integration(self):
        """Test preview with non-existent template."""
        scraping_service = ScrapingService()
        
        result = scraping_service.preview_scraping(
            url="https://example.com",
            template_id="non_existent_template"
        )
        
        assert result["success"] is False
        assert "Template 'non_existent_template' not found" in result["error"]
        assert result["preview"]["count"] == 0
        assert result["preview"]["success_rate"] == "0%"
        assert result["preview_data"]["selectors_matched"] == 0
    
    def test_invalid_url_integration(self):
        """Test preview with invalid URL."""
        scraping_service = ScrapingService()
        
        result = scraping_service.preview_scraping(
            url="not-a-valid-url",
            template_id="any_template"
        )
        
        assert result["success"] is False
        assert "Invalid target URL" in result["error"]
        assert result["url"] == "not-a-valid-url"
        assert result["template_id"] == "any_template"
    
    def test_network_failure_handling(self, temp_template_dir):
        """Test preview when network request fails."""
        with patch('src.core.config.config.templates_folder', str(temp_template_dir)):
            scraping_service = ScrapingService()
            
            # Mock test_selectors to simulate network failure
            with patch('src.scrapers.template_scraper.TemplateScraper.test_selectors') as mock_test:
                mock_test.return_value = {
                    'error': 'Failed to fetch page for testing',
                    'statistics': {
                        'total_selectors': 0,
                        'successful_selectors': 0,
                        'success_rate': 0
                    }
                }
                
                result = scraping_service.preview_scraping(
                    url="https://unreachable-site.com",
                    template_id="test_template"
                )
            
            # Should handle the error gracefully
            assert result["success"] is False
            assert "Failed to test selectors" in result["error"]
            assert result["preview"]["count"] == 0
            assert result["preview_data"]["validation_results"]["error"] is not None