"""Integration tests for service layer connections."""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.data_service import DataService
from src.services.template_service import TemplateService
from src.services.scraping_service import ScrapingService
from src.scrapers.template_scraper import TemplateScraper


class TestDataServiceIntegration:
    """Test DataService integration with utils."""
    
    @pytest.fixture
    def data_service(self):
        """Create DataService instance."""
        return DataService()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {
            "title": "Test Product",
            "price": "$29.99",
            "description": "A test product description",
            "items": [
                {"name": "Item 1", "value": 10},
                {"name": "Item 2", "value": 20}
            ]
        }
    
    def test_export_result_data_json(self, data_service, sample_data, tmp_path):
        """Test export_result_data connects to export_to_json."""
        # Mock result storage
        with patch.object(data_service.result_storage, 'get_result') as mock_get:
            mock_get.return_value = {
                'id': 'test123',
                'data': sample_data,
                'job_id': 'job456',
                'source_url': 'http://example.com'
            }
            
            # Mock export_to_json
            with patch('src.services.data_service.data_utils.export_to_json') as mock_export:
                mock_export.return_value = tmp_path / "result.json"
                
                # Execute export
                result = data_service.export_result_data('test123', 'json')
                
                # Verify connection
                assert result['success'] == True
                assert result['format'] == 'json'
                assert 'file_path' in result
                mock_export.assert_called_once()
    
    def test_export_result_data_csv(self, data_service, sample_data, tmp_path):
        """Test export_result_data connects to export_to_csv."""
        with patch.object(data_service.result_storage, 'get_result') as mock_get:
            mock_get.return_value = {'id': 'test123', 'data': sample_data}
            
            with patch('src.services.data_service.data_utils.export_to_csv') as mock_export:
                mock_export.return_value = tmp_path / "result.csv"
                
                result = data_service.export_result_data('test123', 'csv')
                
                assert result['success'] == True
                assert result['format'] == 'csv'
                mock_export.assert_called_once()
    
    def test_export_result_data_excel(self, data_service, sample_data, tmp_path):
        """Test export_result_data connects to export_to_excel."""
        with patch.object(data_service.result_storage, 'get_result') as mock_get:
            mock_get.return_value = {'id': 'test123', 'data': sample_data}
            
            with patch('src.services.data_service.data_utils.export_to_excel') as mock_export:
                mock_export.return_value = tmp_path / "result.xlsx"
                
                result = data_service.export_result_data('test123', 'xlsx')
                
                assert result['success'] == True
                assert result['format'] == 'xlsx'
                mock_export.assert_called_once()
    
    def test_process_scraped_data(self, data_service, sample_data):
        """Test process_scraped_data uses TemplateScraper."""
        processing_rules = [
            {"field": "price", "operation": "remove_currency"},
            {"field": "title", "operation": "uppercase"}
        ]
        
        with patch('src.services.data_service.TemplateScraper') as mock_scraper_class:
            mock_scraper = Mock()
            mock_scraper._apply_post_processing.return_value = sample_data
            mock_scraper_class.return_value = mock_scraper
            
            result = data_service.process_scraped_data(sample_data, processing_rules)
            
            assert result['processed'] == True
            assert result['success'] == True
            assert 'data' in result
            mock_scraper._apply_post_processing.assert_called_with(sample_data)


class TestTemplateServiceIntegration:
    """Test TemplateService integration with TemplateScraper."""
    
    @pytest.fixture
    def template_service(self):
        """Create TemplateService instance."""
        return TemplateService()
    
    @pytest.fixture
    def sample_template(self):
        """Sample template for testing."""
        return {
            "name": "test_template",
            "selectors": {
                "title": "h1.product-title",
                "price": ".price-tag",
                "description": ".product-description"
            }
        }
    
    def test_test_template_integration(self, template_service, sample_template):
        """Test test_template connects to TemplateScraper.test_selectors."""
        # Mock template manager
        with patch.object(template_service.template_manager, 'load_template') as mock_load:
            mock_load.return_value = sample_template
            
            # Mock TemplateScraper
            with patch('src.services.template_service.TemplateScraper') as mock_scraper_class:
                mock_scraper = Mock()
                mock_scraper.test_selectors.return_value = {
                    'success_rate': 0.8,
                    'field_results': {
                        'title': {'found': True, 'count': 1},
                        'price': {'found': True, 'count': 1},
                        'description': {'found': False, 'count': 0}
                    },
                    'sample_data': {'title': 'Test Product', 'price': '$29.99'}
                }
                mock_scraper_class.return_value = mock_scraper
                
                # Execute test
                result = template_service.test_template('test_template', 'http://example.com')
                
                # Verify integration
                assert result['success'] == True
                assert result['success_rate'] == 0.8
                assert 'field_results' in result
                assert 'sample_data' in result
                mock_scraper.test_selectors.assert_called_once_with('http://example.com')


class TestScrapingServiceIntegration:
    """Test ScrapingService integration with scrapers."""
    
    @pytest.fixture
    def scraping_service(self):
        """Create ScrapingService instance."""
        return ScrapingService()
    
    @pytest.fixture
    def sample_job(self):
        """Sample job for testing."""
        return {
            'id': 'job123',
            'template_name': 'test_template',
            'target_url': 'http://example.com',
            'job_config': {'max_pages': 1},
            'parameters': {}
        }
    
    @pytest.mark.asyncio
    async def test_execute_job_async_integration(self, scraping_service, sample_job):
        """Test execute_job_async uses TemplateScraper for real scraping."""
        template = {
            'name': 'test_template',
            'selectors': {'title': 'h1', 'price': '.price'}
        }
        
        # Mock job manager
        with patch.object(scraping_service.job_manager, 'get_job') as mock_get_job:
            mock_get_job.return_value = sample_job
            
            with patch.object(scraping_service.job_manager, 'update_job_status'):
                with patch.object(scraping_service.job_manager, 'update_job'):
                    
                    # Mock template manager
                    with patch.object(scraping_service.template_manager, 'load_template') as mock_load:
                        mock_load.return_value = template
                        
                        # Mock TemplateScraper
                        with patch('src.services.scraping_service.TemplateScraper') as mock_scraper_class:
                            mock_scraper = Mock()
                            mock_scraper.scrape.return_value = {
                                'status': 'success',
                                'data': {'title': 'Test', 'price': '$29.99'}
                            }
                            mock_scraper_class.return_value = mock_scraper
                            
                            # Mock DataService
                            with patch('src.services.scraping_service.DataService') as mock_data_class:
                                mock_data_service = Mock()
                                mock_data_service.save_scraping_result.return_value = 'result123'
                                mock_data_class.return_value = mock_data_service
                                
                                # Execute job
                                await scraping_service.execute_job_async('job123')
                                
                                # Verify scraper was used
                                mock_scraper.scrape.assert_called_once_with('http://example.com')
                                mock_data_service.save_scraping_result.assert_called_once()
    
    def test_preview_scraping_integration(self, scraping_service):
        """Test preview_scraping uses TemplateScraper.test_selectors."""
        template = {
            'name': 'test_template',
            'selectors': {'title': 'h1', 'content': '.content'}
        }
        
        # Mock template manager
        with patch.object(scraping_service.template_manager, 'load_template') as mock_load:
            mock_load.return_value = template
            
            # Mock TemplateScraper
            with patch('src.services.scraping_service.TemplateScraper') as mock_scraper_class:
                mock_scraper = Mock()
                mock_scraper.validate_template.return_value = {'valid': True}
                mock_scraper.test_selectors.return_value = {
                    'success_rate': 1.0,
                    'field_results': {
                        'title': {'found': True, 'count': 1, 'sample_value': 'Test Title'},
                        'content': {'found': True, 'count': 3, 'sample_value': 'Content...'}
                    }
                }
                mock_scraper_class.return_value = mock_scraper
                
                # Execute preview
                result = scraping_service.preview_scraping('http://example.com', 'test_template')
                
                # Verify integration
                assert result['success'] == True
                assert result['preview_data']['items_found'] > 0
                assert result['preview_data']['selectors_matched'] > 0
                mock_scraper.test_selectors.assert_called_once()


class TestProxyRotatorIntegration:
    """Test ProxyRotator integration with StealthFetcher."""
    
    def test_proxy_rotator_in_stealth_fetcher(self):
        """Test ProxyRotator is properly integrated in StealthFetcher."""
        from src.scrapers.stealth_fetcher import StealthFetcher
        
        fetcher = StealthFetcher()
        proxy_list = ['http://proxy1.com:8080', 'http://proxy2.com:8080']
        
        result = fetcher.configure_proxy_rotation(proxy_list)
        
        assert result['enabled'] == True
        assert result['proxy_count'] == 2
        assert fetcher.proxy_rotator is not None
        assert len(fetcher.proxy_rotator.proxies) == 2


class TestBroadcastIntegration:
    """Test real-time progress broadcasting."""
    
    def test_broadcast_job_progress(self):
        """Test _broadcast_job_progress method exists and handles errors."""
        from src.services.scraping_service import ScrapingService
        
        service = ScrapingService()
        
        # Should not raise error even if eel is not initialized
        service._broadcast_job_progress('job123', 50, 10, 2)
        
        # Verify method exists and is callable
        assert hasattr(service, '_broadcast_job_progress')
        assert callable(service._broadcast_job_progress)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])