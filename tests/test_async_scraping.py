"""Tests for async scraping functionality with FetcherManager."""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from src.scrapers.fetcher_manager import FetcherManager, FetcherType
from src.scrapers.base_scraper import BaseScraper
from src.scrapers.template_scraper import TemplateScraper


class TestFetcherManager:
    """Test FetcherManager functionality."""
    
    def test_fetcher_type_determination(self):
        """Test automatic fetcher type determination."""
        manager = FetcherManager()
        
        # Test JavaScript required
        template_config = {'javascript_required': True}
        assert manager.determine_fetcher_type('http://example.com', template_config) == FetcherType.PLAYWRIGHT
        
        # Test anti-bot protection
        template_config = {'javascript_required': True, 'anti_bot_protection': True}
        assert manager.determine_fetcher_type('http://example.com', template_config) == FetcherType.STEALTH
        
        # Test stealth required
        template_config = {'stealth_required': True}
        assert manager.determine_fetcher_type('http://example.com', template_config) == FetcherType.STEALTH
        
        # Test concurrent scraping
        template_config = {'concurrent_scraping': True}
        assert manager.determine_fetcher_type('http://example.com', template_config) == FetcherType.ASYNC
        
        # Test default
        template_config = {}
        assert manager.determine_fetcher_type('http://example.com', template_config) == FetcherType.BASIC
    
    def test_config_management(self):
        """Test configuration management."""
        manager = FetcherManager()
        
        # Test custom config
        custom_config = {'timeout': 60, 'headless': False}
        manager.set_custom_config(FetcherType.STEALTH, custom_config)
        
        config = manager.get_config(FetcherType.STEALTH)
        assert config['timeout'] == 60
        assert config['headless'] == False
        
        # Test config overrides
        overrides = {'network_idle': False}
        config = manager.get_config(FetcherType.STEALTH, overrides)
        assert config['network_idle'] == False
    
    @patch('src.scrapers.fetcher_manager.Fetcher')
    def test_basic_fetch(self, mock_fetcher):
        """Test basic fetcher usage."""
        manager = FetcherManager()
        mock_response = Mock(status=200)
        mock_fetcher.fetch.return_value = mock_response
        
        result = manager.fetch('http://example.com', fetcher_type=FetcherType.BASIC)
        
        mock_fetcher.fetch.assert_called_once()
        assert result == mock_response
    
    @patch('src.scrapers.fetcher_manager.StealthyFetcher')
    def test_stealth_fetch(self, mock_stealth):
        """Test stealth fetcher usage."""
        manager = FetcherManager()
        mock_response = Mock(status=200)
        mock_stealth.fetch.return_value = mock_response
        
        result = manager.fetch('http://example.com', fetcher_type=FetcherType.STEALTH)
        
        mock_stealth.fetch.assert_called_once()
        assert result == mock_response
    
    @pytest.mark.asyncio
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_async_fetch(self, mock_async):
        """Test async fetcher usage."""
        manager = FetcherManager()
        mock_response = Mock(status=200)
        mock_async.fetch = AsyncMock(return_value=mock_response)
        
        result = await manager.fetch_async('http://example.com', fetcher_type=FetcherType.ASYNC)
        
        mock_async.fetch.assert_called_once()
        assert result == mock_response
    
    @pytest.mark.asyncio
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_fetch_multiple_async(self, mock_async):
        """Test fetching multiple URLs concurrently."""
        manager = FetcherManager()
        mock_response = Mock(status=200)
        mock_async.fetch = AsyncMock(return_value=mock_response)
        
        urls = ['http://example1.com', 'http://example2.com', 'http://example3.com']
        results = await manager.fetch_multiple_async(urls, fetcher_type=FetcherType.ASYNC, max_concurrent=2)
        
        assert len(results) == 3
        assert all(r == mock_response for r in results)
        assert mock_async.fetch.call_count == 3


class TestBaseScraper:
    """Test BaseScraper with async support."""
    
    class TestScraper(BaseScraper):
        """Concrete implementation for testing."""
        
        def scrape(self, url, **kwargs):
            page = self.fetch_page(url)
            return {'url': url, 'status': 'success', 'data': {}}
        
        async def scrape_async(self, url, **kwargs):
            page = await self.fetch_page_async(url)
            return {'url': url, 'status': 'success', 'data': {}}
    
    def test_initialization(self):
        """Test scraper initialization with fetcher configuration."""
        scraper = self.TestScraper(fetcher_type='stealth')
        assert scraper.fetcher_manager.default_type == FetcherType.STEALTH
        
        # Test with custom config
        custom_config = {
            'stealth': {'headless': False},
            'basic': {'timeout': 60}
        }
        scraper = self.TestScraper(fetcher_type='auto', fetcher_config=custom_config)
        assert scraper.fetcher_manager.default_type == FetcherType.AUTO
    
    @patch('src.scrapers.fetcher_manager.Fetcher')
    def test_fetch_page(self, mock_fetcher):
        """Test synchronous page fetching."""
        scraper = self.TestScraper()
        mock_response = Mock(status=200)
        mock_fetcher.fetch.return_value = mock_response
        
        result = scraper.fetch_page('http://example.com')
        assert result == mock_response
    
    @pytest.mark.asyncio
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_fetch_page_async(self, mock_async):
        """Test asynchronous page fetching."""
        scraper = self.TestScraper()
        mock_response = Mock(status=200)
        mock_async.fetch = AsyncMock(return_value=mock_response)
        
        result = await scraper.fetch_page_async('http://example.com')
        assert result == mock_response
    
    @patch('src.scrapers.fetcher_manager.Fetcher')
    def test_scrape_multiple(self, mock_fetcher):
        """Test scraping multiple URLs synchronously."""
        scraper = self.TestScraper()
        mock_response = Mock(status=200)
        mock_fetcher.fetch.return_value = mock_response
        
        urls = ['http://example1.com', 'http://example2.com']
        results = scraper.scrape_multiple(urls)
        
        assert len(results) == 2
        assert all(r['status'] == 'success' for r in results)
    
    @pytest.mark.asyncio
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_scrape_multiple_async(self, mock_async):
        """Test scraping multiple URLs asynchronously."""
        scraper = self.TestScraper()
        mock_response = Mock(status=200)
        mock_async.fetch = AsyncMock(return_value=mock_response)
        
        urls = ['http://example1.com', 'http://example2.com', 'http://example3.com']
        results = await scraper.scrape_multiple_async(urls, max_concurrent=2)
        
        assert len(results) == 3
        assert all(r['status'] == 'success' for r in results)
    
    def test_extract_with_css(self):
        """Test CSS extraction with fallbacks."""
        scraper = self.TestScraper()
        
        # Mock response
        mock_element = Mock()
        mock_element.text = 'Test Product'
        mock_response = Mock()
        mock_response.css.return_value = mock_element
        
        # Test basic extraction
        result = scraper._extract_with_css(mock_response, '.product')
        assert result == mock_element
        
        # Test with fallbacks
        mock_response.css.side_effect = [None, None, mock_element]
        result = scraper._extract_with_css(
            mock_response, '.missing', 
            fallback_selectors=['.also-missing', '.product']
        )
        assert result == mock_element
    
    def test_extract_data(self):
        """Test data extraction with selectors."""
        scraper = self.TestScraper()
        
        # Mock response
        mock_element = Mock()
        mock_element.text = Mock(strip=Mock(return_value='Test Product'))
        mock_response = Mock(status=200)
        mock_response.css.return_value = [mock_element]
        
        selectors = {
            'title': '.product-title',
            'price': {
                'selector': '.price',
                'type': 'text',
                'fallback_selectors': ['.cost']
            }
        }
        
        result = scraper.extract_data(mock_response, selectors)
        assert 'title' in result
        assert 'price' in result


class TestTemplateScraper:
    """Test TemplateScraper with async support."""
    
    def test_template_initialization(self):
        """Test template scraper initialization."""
        template = {
            'name': 'test_template',
            'fetcher_config': {
                'type': 'stealth',
                'stealth': {'headless': False}
            },
            'selectors': {
                'title': '.product-title'
            }
        }
        
        scraper = TemplateScraper(template)
        assert scraper.template == template
        assert scraper.fetcher_manager.default_type == FetcherType.STEALTH
    
    def test_extract_fetcher_type(self):
        """Test fetcher type extraction from template."""
        scraper = TemplateScraper()
        
        # Test explicit type
        template = {'fetcher_config': {'type': 'playwright'}}
        assert scraper._extract_fetcher_type(template) == FetcherType.PLAYWRIGHT
        
        # Test invalid type
        template = {'fetcher_config': {'type': 'invalid'}}
        assert scraper._extract_fetcher_type(template) == FetcherType.AUTO
        
        # Test no config
        assert scraper._extract_fetcher_type({}) == FetcherType.AUTO
    
    def test_extract_fetcher_config(self):
        """Test fetcher configuration extraction from template."""
        scraper = TemplateScraper()
        
        # Test with stealth required
        template = {
            'stealth_required': True,
            'fetcher_config': {
                'stealth': {'timeout': 120}
            }
        }
        config = scraper._extract_fetcher_config(template)
        assert 'stealth' in config
        assert config['stealth']['timeout'] == 120
        
        # Test with JavaScript required
        template = {'javascript_required': True}
        config = scraper._extract_fetcher_config(template)
        assert 'playwright' in config
        assert config['playwright']['headless'] == True
    
    @patch('src.scrapers.fetcher_manager.StealthyFetcher')
    def test_scrape_with_template(self, mock_stealth):
        """Test scraping with template configuration."""
        template = {
            'name': 'test_template',
            'fetcher_config': {'type': 'stealth'},
            'selectors': {
                'title': '.product-title',
                'price': '.price'
            },
            'post_processing': [
                {'type': 'strip', 'field': 'title'}
            ],
            'validation_rules': {
                'required_fields': ['title']
            }
        }
        
        scraper = TemplateScraper(template)
        
        # Mock response
        mock_title = Mock()
        mock_title.text = Mock(strip=Mock(return_value='Test Product'))
        mock_price = Mock()
        mock_price.text = Mock(strip=Mock(return_value='$19.99'))
        
        mock_response = Mock(status=200)
        mock_response.css.side_effect = [[mock_title], [mock_price]]
        mock_stealth.fetch.return_value = mock_response
        
        result = scraper.scrape('http://example.com')
        
        assert result['status'] == 'success'
        assert result['template_name'] == 'test_template'
        assert 'data' in result
    
    @pytest.mark.asyncio
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_scrape_async_with_template(self, mock_async):
        """Test async scraping with template."""
        template = {
            'name': 'async_template',
            'fetcher_config': {'type': 'async'},
            'selectors': {'title': '.product-title'}
        }
        
        scraper = TemplateScraper(template)
        
        # Mock response
        mock_element = Mock()
        mock_element.text = Mock(strip=Mock(return_value='Test Product'))
        mock_response = Mock(status=200)
        mock_response.css.return_value = [mock_element]
        mock_async.fetch = AsyncMock(return_value=mock_response)
        
        result = await scraper.scrape_async('http://example.com')
        
        assert result['status'] == 'success'
        assert result['template_name'] == 'async_template'
    
    def test_post_processing(self):
        """Test post-processing functionality."""
        template = {
            'post_processing': [
                {'type': 'strip', 'field': 'title'},
                {'type': 'lowercase', 'field': 'category'},
                {'type': 'extract_number', 'field': 'price'}
            ]
        }
        
        scraper = TemplateScraper(template)
        
        data = {
            'title': '  Test Product  ',
            'category': 'ELECTRONICS',
            'price': 'Price: $19.99'
        }
        
        processed = scraper._apply_post_processing(data)
        
        assert processed['title'] == 'Test Product'
        assert processed['category'] == 'electronics'
        assert processed['price'] == 19.99
    
    def test_validation(self):
        """Test data validation functionality."""
        template = {
            'validation_rules': {
                'required_fields': ['title', 'price'],
                'field_types': {
                    'title': 'string',
                    'price': 'number'
                },
                'field_patterns': {
                    'email': r'^[\w\.-]+@[\w\.-]+\.\w+$'
                }
            }
        }
        
        scraper = TemplateScraper(template)
        
        # Test valid data
        data = {
            'title': 'Product',
            'price': 19.99,
            'email': 'test@example.com'
        }
        result = scraper._validate_data(data)
        assert result['valid'] == True
        
        # Test invalid data
        data = {
            'title': 'Product',
            'email': 'invalid-email'
        }
        result = scraper._validate_data(data)
        assert result['valid'] == False
        assert len(result['errors']) > 0


@pytest.mark.asyncio
class TestConcurrentScraping:
    """Test concurrent scraping scenarios."""
    
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_concurrent_fetching(self, mock_async):
        """Test concurrent URL fetching."""
        manager = FetcherManager()
        
        # Simulate varying response times
        async def delayed_response(url, **kwargs):
            await asyncio.sleep(0.1)
            return Mock(status=200, url=url)
        
        mock_async.fetch = delayed_response
        
        urls = [f'http://example{i}.com' for i in range(10)]
        
        start_time = asyncio.get_event_loop().time()
        results = await manager.fetch_multiple_async(urls, max_concurrent=5)
        end_time = asyncio.get_event_loop().time()
        
        # Should be faster than sequential (1 second total)
        assert (end_time - start_time) < 0.5
        assert len(results) == 10
    
    @patch('src.scrapers.fetcher_manager.AsyncFetcher')
    async def test_error_handling_in_concurrent(self, mock_async):
        """Test error handling in concurrent operations."""
        manager = FetcherManager()
        
        # Simulate some failures
        call_count = 0
        async def sometimes_fail(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:
                raise Exception("Network error")
            return Mock(status=200, url=url)
        
        mock_async.fetch = sometimes_fail
        
        urls = [f'http://example{i}.com' for i in range(9)]
        results = await manager.fetch_multiple_async(urls, max_concurrent=3)
        
        # Should handle failures gracefully
        assert len(results) == 6  # 3 failures out of 9


if __name__ == '__main__':
    pytest.main([__file__, '-v'])