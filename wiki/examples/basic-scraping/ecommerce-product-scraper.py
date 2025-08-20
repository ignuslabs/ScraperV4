#!/usr/bin/env python3
"""
E-commerce Product Scraper Example

This example demonstrates scraping product data from e-commerce websites with
proper error handling, data validation, and anti-bot detection measures.

Features demonstrated:
- Product information extraction (title, price, description, images)
- Stock status monitoring
- Rating and review data extraction
- Price tracking capabilities
- Image URL collection and validation
- Robust error handling and retry mechanisms

Prerequisites:
- ScraperV4 installed and configured
- Understanding of e-commerce website structures
- Optional: proxy configuration for large-scale scraping

Usage:
    python ecommerce-product-scraper.py

Expected Output:
- Structured product data in JSON format
- Price and availability information
- Product images and ratings
- Export options for further analysis
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin, urlparse

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from services.scraping_service import ScrapingService
from services.template_service import TemplateService
from services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EcommerceProductScraper:
    """E-commerce product scraper with advanced features."""
    
    def __init__(self):
        """Initialize the scraper with required services."""
        self.scraping_service = ScrapingService()
        self.template_service = TemplateService()
        self.data_service = DataService()
        
    def create_ecommerce_template(self) -> Dict[str, Any]:
        """
        Create a comprehensive e-commerce product scraping template.
        
        This template demonstrates:
        - Product data extraction with fallback selectors
        - Price parsing and normalization
        - Image collection with validation
        - Stock status detection
        - Rating and review extraction
        - Structured data validation
        
        Returns:
            Dict containing the template configuration
        """
        template = {
            "name": "ecommerce_product_scraper",
            "description": "Comprehensive template for scraping e-commerce products",
            "version": "2.0.0",
            
            # Advanced fetcher configuration with stealth capabilities
            "fetcher_config": {
                "type": "stealth",
                "stealth": {
                    "headless": True,
                    "humanize": True,
                    "block_webrtc": True,
                    "spoof_canvas": True,
                    "os_randomization": True,
                    "network_idle": True,
                    "wait_for_selector": ".product-container",
                    "google_search": False,
                    "disable_ads": True
                },
                "basic": {
                    "timeout": 45,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1"
                    }
                }
            },
            
            # Comprehensive product selectors with fallbacks
            "selectors": {
                "title": {
                    "selector": "h1.product-title, h1.product-name, h1[itemprop='name'], .product-title, .product-name",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        "h1",
                        ".title",
                        "[data-testid='product-title']",
                        ".pdp-product-name",
                        "#product-title"
                    ]
                },
                
                "price": {
                    "selector": ".price-current, .price-now, [itemprop='price'], .product-price, .current-price",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".price",
                        ".cost",
                        ".amount",
                        "[data-testid='price']",
                        ".price-display",
                        ".selling-price"
                    ]
                },
                
                "original_price": {
                    "selector": ".price-original, .price-was, .original-price, .list-price",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".was-price",
                        ".regular-price",
                        ".msrp",
                        ".crossed-price"
                    ]
                },
                
                "description": {
                    "selector": ".product-description, [itemprop='description'], .product-details, .description",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".product-summary",
                        ".item-description",
                        ".product-info",
                        "#description"
                    ]
                },
                
                "images": {
                    "selector": ".product-images img, .gallery img, [itemprop='image'], .product-image img",
                    "type": "all",
                    "auto_save": True,
                    "attribute": "src",
                    "fallback_selectors": [
                        ".image-gallery img",
                        ".product-photos img",
                        ".item-images img",
                        ".carousel img"
                    ]
                },
                
                "availability": {
                    "selector": ".availability, .stock-status, [itemprop='availability'], .inventory-status",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".in-stock",
                        ".out-of-stock",
                        ".stock-info",
                        "[data-testid='availability']"
                    ]
                },
                
                "rating": {
                    "selector": ".rating-value, [itemprop='ratingValue'], .average-rating, .stars-rating",
                    "type": "text", 
                    "auto_save": True,
                    "fallback_selectors": [
                        ".rating",
                        ".score",
                        ".star-rating",
                        "[data-rating]"
                    ]
                },
                
                "review_count": {
                    "selector": ".review-count, [itemprop='reviewCount'], .reviews-count, .total-reviews",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".reviews",
                        ".review-total",
                        ".rating-count",
                        "[data-review-count]"
                    ]
                },
                
                "brand": {
                    "selector": ".brand, [itemprop='brand'], .product-brand, .manufacturer",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".brand-name",
                        ".vendor",
                        ".maker"
                    ]
                },
                
                "sku": {
                    "selector": ".sku, [itemprop='sku'], .product-sku, .item-number",
                    "type": "text",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".product-id",
                        ".item-id",
                        ".model-number"
                    ]
                },
                
                "variants": {
                    "selector": ".product-options option, .variant-selector option, .size-options option",
                    "type": "all",
                    "auto_save": True,
                    "fallback_selectors": [
                        ".product-variants option",
                        ".attribute-options option"
                    ]
                }
            },
            
            # No pagination for single product pages
            "pagination": {
                "enabled": False
            },
            
            # Advanced post-processing for e-commerce data
            "post_processing": [
                {
                    "type": "strip",
                    "field": "title"
                },
                {
                    "type": "strip",
                    "field": "description"
                },
                {
                    "type": "extract_price",
                    "field": "price"
                },
                {
                    "type": "extract_price", 
                    "field": "original_price"
                },
                {
                    "type": "extract_number",
                    "field": "rating"
                },
                {
                    "type": "extract_number",
                    "field": "review_count"
                },
                {
                    "type": "normalize_urls",
                    "field": "images"
                },
                {
                    "type": "normalize_availability",
                    "field": "availability"
                },
                {
                    "type": "strip",
                    "field": "brand"
                },
                {
                    "type": "strip",
                    "field": "sku"
                }
            ],
            
            # Comprehensive validation rules
            "validation_rules": {
                "required_fields": ["title", "price"],
                "field_types": {
                    "title": "string",
                    "price": "number",
                    "original_price": "number",
                    "description": "string",
                    "images": "list",
                    "availability": "string",
                    "rating": "number",
                    "review_count": "number",
                    "brand": "string",
                    "sku": "string",
                    "variants": "list"
                },
                "field_patterns": {
                    "availability": "^(in stock|out of stock|limited|available|unavailable|backorder)$"
                },
                "field_ranges": {
                    "rating": [0, 5],
                    "price": [0, 999999],
                    "review_count": [0, 1000000]
                }
            },
            
            "adaptive_selectors": {
                "enabled": True,
                "learning_mode": True,
                "similarity_threshold": 0.8
            },
            
            "fallback_selectors": {
                "enabled": True,
                "max_attempts": 3
            },
            
            "is_active": True
        }
        
        return template
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text string.
        
        Args:
            price_text: Raw price text from webpage
            
        Returns:
            Extracted price as float or None if not found
        """
        if not price_text:
            return None
            
        # Remove currency symbols and common text
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Assume last separator is decimal
            if cleaned.rfind('.') > cleaned.rfind(','):
                cleaned = cleaned.replace(',', '')
            else:
                cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Check if comma is likely decimal separator
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except (ValueError, InvalidOperation):
            return None
    
    def validate_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean product data.
        
        Args:
            data: Raw scraped product data
            
        Returns:
            Validated and cleaned product data
        """
        validated = {}
        
        # Required fields validation
        if not data.get('title'):
            raise ValueError("Product title is required")
            
        validated['title'] = str(data['title']).strip()
        
        # Price validation and conversion
        if data.get('price'):
            price = self.extract_price(str(data['price']))
            if price is not None and price > 0:
                validated['price'] = price
                validated['price_formatted'] = f"${price:.2f}"
            else:
                raise ValueError("Invalid price value")
        
        # Original price (optional)
        if data.get('original_price'):
            original_price = self.extract_price(str(data['original_price']))
            if original_price is not None and original_price > 0:
                validated['original_price'] = original_price
                validated['original_price_formatted'] = f"${original_price:.2f}"
                
                # Calculate discount
                if 'price' in validated:
                    discount = ((original_price - validated['price']) / original_price) * 100
                    validated['discount_percentage'] = round(discount, 2)
        
        # Description
        if data.get('description'):
            validated['description'] = str(data['description']).strip()[:1000]  # Limit length
        
        # Images validation
        if data.get('images'):
            images = data['images']
            if isinstance(images, list):
                validated_images = []
                for img in images:
                    if img and isinstance(img, str):
                        # Validate URL format
                        if img.startswith(('http://', 'https://', '//')):
                            validated_images.append(img)
                        elif img.startswith('/'):
                            # Relative URL - would need base URL to validate
                            validated_images.append(img)
                validated['images'] = validated_images
                validated['image_count'] = len(validated_images)
        
        # Availability normalization
        if data.get('availability'):
            availability = str(data['availability']).lower().strip()
            if any(word in availability for word in ['in stock', 'available', 'ready']):
                validated['availability'] = 'in_stock'
                validated['in_stock'] = True
            elif any(word in availability for word in ['out of stock', 'unavailable', 'sold out']):
                validated['availability'] = 'out_of_stock'
                validated['in_stock'] = False
            else:
                validated['availability'] = 'unknown'
                validated['in_stock'] = None
        
        # Rating validation
        if data.get('rating'):
            try:
                rating = float(str(data['rating']).strip())
                if 0 <= rating <= 5:
                    validated['rating'] = rating
                    validated['rating_stars'] = '★' * int(rating) + '☆' * (5 - int(rating))
            except (ValueError, TypeError):
                pass
        
        # Review count
        if data.get('review_count'):
            review_text = str(data['review_count'])
            review_numbers = re.findall(r'\d+', review_text)
            if review_numbers:
                validated['review_count'] = int(review_numbers[0])
        
        # Brand and SKU
        for field in ['brand', 'sku']:
            if data.get(field):
                validated[field] = str(data[field]).strip()
        
        # Variants
        if data.get('variants') and isinstance(data['variants'], list):
            validated['variants'] = [str(v).strip() for v in data['variants'] if v]
            validated['variant_count'] = len(validated['variants'])
        
        # Add metadata
        validated['scraped_at'] = asyncio.get_event_loop().time()
        validated['data_quality_score'] = self.calculate_data_quality(validated)
        
        return validated
    
    def calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score based on completeness and validity.
        
        Args:
            data: Validated product data
            
        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 0.0
        max_score = 0.0
        
        # Required fields (high weight)
        if data.get('title'):
            score += 0.3
        max_score += 0.3
        
        if data.get('price'):
            score += 0.3
        max_score += 0.3
        
        # Important fields (medium weight)
        for field in ['description', 'images', 'availability']:
            if data.get(field):
                score += 0.1
            max_score += 0.1
        
        # Nice-to-have fields (low weight)
        for field in ['rating', 'review_count', 'brand', 'sku']:
            if data.get(field):
                score += 0.05
            max_score += 0.05
        
        return score / max_score if max_score > 0 else 0.0
    
    async def scrape_product_urls(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape multiple product URLs.
        
        Args:
            urls: List of product URLs to scrape
            **kwargs: Additional configuration options
            
        Returns:
            List of scraped and validated product data
        """
        logger.info(f"Starting batch scraping of {len(urls)} product URLs")
        
        try:
            # Create and save template
            template = self.create_ecommerce_template()
            template_result = self.template_service.save_template(template)
            template_id = template_result.get("id")
            
            logger.info(f"Created template with ID: {template_id}")
            
            all_results = []
            
            for i, url in enumerate(urls):
                logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
                
                try:
                    # Create job configuration
                    job_config = {
                        "name": f"Product scrape: {urlparse(url).netloc}",
                        "template_id": template_id,
                        "target_url": url,
                        "config": {
                            "use_proxy": kwargs.get("use_proxy", False),
                            "stealth_mode": kwargs.get("stealth_mode", "medium"),
                            "delay_range": kwargs.get("delay_range", [2, 4]),
                            "retry_attempts": kwargs.get("retry_attempts", 3),
                            "timeout": kwargs.get("timeout", 45),
                            "enable_anti_bot_detection": True
                        }
                    }
                    
                    # Create and start job
                    job = self.scraping_service.create_job(**job_config)
                    job_id = await self.scraping_service.start_scraping_job(job.id)
                    
                    # Monitor progress
                    await self._monitor_job_progress(job_id)
                    
                    # Get results
                    final_status = self.scraping_service.get_job_status(job_id)
                    
                    if final_status["status"] == "completed":
                        raw_results = self.data_service.get_result_data(job_id)
                        
                        for raw_data in raw_results:
                            try:
                                validated_data = self.validate_product_data(raw_data)
                                validated_data['source_url'] = url
                                validated_data['job_id'] = job_id
                                all_results.append(validated_data)
                                logger.info(f"Successfully processed product: {validated_data.get('title', 'Unknown')}")
                            except ValueError as e:
                                logger.warning(f"Data validation failed for {url}: {e}")
                                continue
                    else:
                        logger.error(f"Scraping failed for {url}: {final_status.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")
                    continue
                
                # Respectful delay between URLs
                if i < len(urls) - 1:
                    delay = kwargs.get("batch_delay", 3)
                    logger.info(f"Waiting {delay} seconds before next URL...")
                    await asyncio.sleep(delay)
            
            logger.info(f"Batch scraping completed. Successfully processed {len(all_results)} products.")
            return all_results
            
        except Exception as e:
            logger.error(f"Error during batch scraping: {str(e)}")
            return []
    
    async def _monitor_job_progress(self, job_id: str) -> None:
        """Monitor job progress with real-time updates."""
        while True:
            status = self.scraping_service.get_job_status(job_id)
            
            if status["status"] in ["completed", "failed", "stopped"]:
                logger.info(f"Job {job_id} finished with status: {status['status']}")
                break
                
            logger.info(f"Job {job_id} - Progress: {status.get('progress', 0)}% - "
                       f"Items: {status.get('items_scraped', 0)} - "
                       f"Status: {status['status']}")
            
            await asyncio.sleep(3)
    
    def export_products(self, products: List[Dict[str, Any]], format: str = "json") -> str:
        """
        Export product data to specified format.
        
        Args:
            products: List of product data dictionaries
            format: Export format ('json', 'csv', 'xlsx')
            
        Returns:
            Path to exported file
        """
        import json
        import csv
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            file_path = export_dir / f"products_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False, default=str)
                
        elif format.lower() == "csv":
            file_path = export_dir / f"products_{timestamp}.csv"
            if products:
                fieldnames = list(products[0].keys())
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(products)
                    
        elif format.lower() == "xlsx":
            try:
                import pandas as pd
                file_path = export_dir / f"products_{timestamp}.xlsx"
                df = pd.DataFrame(products)
                df.to_excel(file_path, index=False)
            except ImportError:
                logger.error("pandas required for Excel export")
                return None
                
        logger.info(f"Products exported to: {file_path}")
        return str(file_path)

async def main():
    """
    Main function demonstrating e-commerce product scraping.
    
    This example shows:
    1. Creating an e-commerce scraper
    2. Scraping product data with validation
    3. Batch processing multiple URLs
    4. Data quality assessment
    5. Multiple export formats
    """
    
    scraper = EcommerceProductScraper()
    
    # Example product URLs (replace with actual e-commerce URLs)
    product_urls = [
        "https://example-store.com/product/laptop-123",
        "https://example-store.com/product/smartphone-456", 
        "https://example-store.com/product/headphones-789"
    ]
    
    print(f"\n{'='*60}")
    print("ScraperV4 E-commerce Product Scraping Example")
    print(f"{'='*60}")
    
    try:
        # Configure scraping options
        scraping_options = {
            "use_proxy": False,  # Enable for production scraping
            "stealth_mode": "high",
            "delay_range": [2, 5],
            "retry_attempts": 3,
            "timeout": 45,
            "batch_delay": 3
        }
        
        # Scrape products
        print(f"\n🛒 Scraping {len(product_urls)} products...")
        products = await scraper.scrape_product_urls(product_urls, **scraping_options)
        
        if products:
            print(f"\n✅ Successfully scraped {len(products)} products!")
            
            # Display results summary
            total_value = sum(p.get('price', 0) for p in products)
            avg_rating = sum(p.get('rating', 0) for p in products if p.get('rating', 0) > 0) / len([p for p in products if p.get('rating', 0) > 0])
            in_stock_count = sum(1 for p in products if p.get('in_stock'))
            
            print(f"\n📊 Scraping Summary:")
            print(f"   Total Products: {len(products)}")
            print(f"   Total Value: ${total_value:.2f}")
            print(f"   Average Rating: {avg_rating:.1f}/5.0" if avg_rating > 0 else "   Average Rating: N/A")
            print(f"   In Stock: {in_stock_count}/{len(products)}")
            
            # Show sample products
            print(f"\n🔍 Sample Products:")
            for i, product in enumerate(products[:3]):
                print(f"\n   Product {i+1}:")
                print(f"   📦 {product.get('title', 'Unknown')}")
                print(f"   💰 ${product.get('price', 0):.2f}")
                if product.get('original_price'):
                    print(f"   🏷️  Was: ${product.get('original_price'):.2f} (Save {product.get('discount_percentage', 0):.0f}%)")
                print(f"   📍 {product.get('availability', 'Unknown').replace('_', ' ').title()}")
                if product.get('rating'):
                    print(f"   ⭐ {product.get('rating')}/5.0 ({product.get('review_count', 0)} reviews)")
                print(f"   📊 Quality Score: {product.get('data_quality_score', 0):.1%}")
            
            # Export results
            print(f"\n📁 Exporting results...")
            
            # Export as JSON
            json_file = scraper.export_products(products, "json")
            if json_file:
                print(f"   📄 JSON: {json_file}")
            
            # Export as CSV
            csv_file = scraper.export_products(products, "csv")
            if csv_file:
                print(f"   📊 CSV: {csv_file}")
            
            # Export as Excel (if pandas available)
            try:
                xlsx_file = scraper.export_products(products, "xlsx")
                if xlsx_file:
                    print(f"   📈 Excel: {xlsx_file}")
            except Exception as e:
                print(f"   ⚠️  Excel export skipped: {e}")
            
        else:
            print("❌ No products were successfully scraped")
            
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    asyncio.run(main())