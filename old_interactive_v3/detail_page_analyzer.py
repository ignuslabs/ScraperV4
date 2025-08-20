"""
V3 Detail Page Analyzer

Handles headless analysis of detail pages for subpage extraction configuration.
Features:
- Headless browsing with Playwright
- Auto-detection of extractable elements
- Integration with existing auto-detection patterns
- Communication with JavaScript overlay
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import Browser, Page, async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


class V3DetailPageAnalyzer:
    """Analyzes detail pages to suggest extractable elements"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None

        # Pattern library for common detail page elements
        self.detail_patterns = {
            "title": {
                "selectors": [
                    "h1",
                    ".title",
                    ".product-title",
                    ".article-title",
                    ".name",
                    ".headline",
                ],
                "confidence_base": 0.9,
            },
            "price": {
                "selectors": [
                    ".price",
                    ".cost",
                    ".amount",
                    ".product-price",
                    "[data-price]",
                    ".price-current",
                ],
                "confidence_base": 0.95,
            },
            "description": {
                "selectors": [
                    ".description",
                    ".content",
                    ".details",
                    ".summary",
                    ".about",
                    ".product-description",
                ],
                "confidence_base": 0.8,
            },
            "image": {
                "selectors": [
                    "img.main-image",
                    ".product-image img",
                    ".hero-image",
                    ".featured-image",
                ],
                "confidence_base": 0.85,
            },
            "date": {
                "selectors": [
                    ".date",
                    ".published",
                    ".timestamp",
                    ".created",
                    "[datetime]",
                ],
                "confidence_base": 0.8,
            },
            "author": {
                "selectors": [".author", ".by", ".byline", ".writer", ".creator"],
                "confidence_base": 0.85,
            },
            "category": {
                "selectors": [
                    ".category",
                    ".section",
                    ".tag",
                    ".topic",
                    ".breadcrumb a:last-child",
                ],
                "confidence_base": 0.75,
            },
            "rating": {
                "selectors": [
                    ".rating",
                    ".stars",
                    ".score",
                    ".review-score",
                    "[data-rating]",
                ],
                "confidence_base": 0.9,
            },
            "availability": {
                "selectors": [".stock", ".availability", ".in-stock", ".status"],
                "confidence_base": 0.8,
            },
            "specifications": {
                "selectors": [
                    ".specs",
                    ".specifications",
                    ".features",
                    ".attributes",
                    ".properties",
                ],
                "confidence_base": 0.7,
            },
        }

    async def initialize_browser(self):
        """Initialize Playwright browser for headless analysis"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available for detail page analysis")

        if self.browser:
            return

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            logger.info("🌐 Playwright browser initialized for detail analysis")
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            raise

    async def analyze_detail_page(self, url: str) -> Dict[str, Any]:
        """
        Analyze a detail page and return extractable elements

        Args:
            url: URL of the detail page to analyze

        Returns:
            Dictionary containing analysis results
        """
        try:
            await self.initialize_browser()

            logger.info(f"🔍 Analyzing detail page: {url}")

            page = await self.browser.new_page()

            # Navigate to page with timeout
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for page to stabilize
            await asyncio.sleep(2)

            # Analyze page structure
            analysis_result = await self.extract_page_elements(page, url)

            await page.close()

            logger.info(
                f"✅ Detail page analysis complete: {len(analysis_result.get('suggestions', []))} elements found"
            )

            return {"success": True, "data": analysis_result}

        except Exception as e:
            logger.error(f"❌ Detail page analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def extract_page_elements(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract potential elements from the page"""

        suggestions = []
        page_info = {
            "url": url,
            "title": await page.title(),
            "domain": urlparse(url).netloc,
        }

        # Analyze each pattern type
        for field_type, pattern_config in self.detail_patterns.items():
            elements = await self.find_elements_by_pattern(
                page, field_type, pattern_config
            )
            suggestions.extend(elements)

        # Find additional elements using heuristics
        additional_elements = await self.find_additional_elements(page)
        suggestions.extend(additional_elements)

        # Sort by confidence score
        suggestions.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        # Limit to top suggestions to avoid overwhelming UI
        suggestions = suggestions[:20]

        return {
            "suggestions": suggestions,
            "page_info": page_info,
            "analysis_timestamp": time.time(),
        }

    async def find_elements_by_pattern(
        self, page: Page, field_type: str, pattern_config: Dict
    ) -> List[Dict]:
        """Find elements matching a specific pattern"""

        elements = []
        base_confidence = pattern_config["confidence_base"]

        for selector in pattern_config["selectors"]:
            try:
                # Find elements matching selector
                element_handles = await page.query_selector_all(selector)

                for i, element in enumerate(
                    element_handles[:3]
                ):  # Limit to first 3 matches
                    try:
                        # Get element properties
                        element_info = await self.get_element_info(element, selector)

                        if element_info and element_info.get("text_content"):
                            # Calculate confidence based on various factors
                            confidence = await self.calculate_confidence(
                                element, selector, field_type, base_confidence
                            )

                            suggestion = {
                                "label": self.generate_field_label(
                                    field_type, element_info, i
                                ),
                                "selector": selector,
                                "type": field_type,
                                "confidence": confidence,
                                "sample_text": element_info["text_content"][:100],
                                "element_info": element_info,
                            }

                            elements.append(suggestion)

                    except Exception as e:
                        logger.debug(f"Error processing element {selector}: {e}")
                        continue

            except Exception as e:
                logger.debug(f"Error finding elements for {selector}: {e}")
                continue

        return elements

    async def find_additional_elements(self, page: Page) -> List[Dict]:
        """Find additional elements using heuristics"""

        additional_elements = []

        # Look for elements with meaningful text content
        heuristic_selectors = [
            "p:not(:empty)",
            "span:not(:empty)",
            "div:not(:empty)",
            "td:not(:empty)",
            "li:not(:empty)",
        ]

        for selector in heuristic_selectors:
            try:
                elements = await page.query_selector_all(selector)

                for element in elements[:5]:  # Limit to avoid too many results
                    element_info = await self.get_element_info(element, selector)

                    if (
                        element_info
                        and element_info.get("text_content")
                        and 10 <= len(element_info["text_content"]) <= 200
                    ):

                        # Try to classify the element type
                        detected_type = self.detect_element_type(
                            element_info["text_content"]
                        )

                        suggestion = {
                            "label": f"Text Content ({detected_type})",
                            "selector": self.optimize_selector(selector, element_info),
                            "type": detected_type,
                            "confidence": 0.6,  # Lower confidence for heuristic matches
                            "sample_text": element_info["text_content"][:100],
                            "element_info": element_info,
                        }

                        additional_elements.append(suggestion)

            except Exception as e:
                logger.debug(f"Error in heuristic analysis for {selector}: {e}")
                continue

        return additional_elements

    async def get_element_info(self, element, selector: str) -> Optional[Dict]:
        """Get comprehensive information about an element"""

        try:
            # Get basic properties
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            text_content = await element.text_content()

            if not text_content or len(text_content.strip()) < 3:
                return None

            # Get additional attributes
            class_name = await element.get_attribute("class") or ""
            id_attr = await element.get_attribute("id") or ""

            # Get position and visibility info
            bounding_box = await element.bounding_box()
            is_visible = await element.is_visible()

            return {
                "tag_name": tag_name,
                "text_content": text_content.strip(),
                "class_name": class_name,
                "id": id_attr,
                "selector": selector,
                "bounding_box": bounding_box,
                "is_visible": is_visible,
            }

        except Exception as e:
            logger.debug(f"Error getting element info: {e}")
            return None

    async def calculate_confidence(
        self, element, selector: str, field_type: str, base_confidence: float
    ) -> float:
        """Calculate confidence score for an element match"""

        confidence = base_confidence

        try:
            # Boost confidence for specific selectors
            if any(
                indicator in selector.lower()
                for indicator in [field_type, f".{field_type}", f"#{field_type}"]
            ):
                confidence = min(confidence + 0.1, 1.0)

            # Check visibility
            is_visible = await element.is_visible()
            if not is_visible:
                confidence *= 0.5

            # Check position (elements higher on page often more important)
            bounding_box = await element.bounding_box()
            if bounding_box and bounding_box["y"] < 500:  # Above the fold
                confidence = min(confidence + 0.05, 1.0)

            # Check text length appropriateness
            text_content = await element.text_content()
            if text_content:
                text_len = len(text_content.strip())
                if field_type in ["title", "name"] and 10 <= text_len <= 100:
                    confidence = min(confidence + 0.05, 1.0)
                elif field_type == "description" and 50 <= text_len <= 500:
                    confidence = min(confidence + 0.05, 1.0)
                elif field_type == "price" and 3 <= text_len <= 20:
                    confidence = min(confidence + 0.1, 1.0)

        except Exception as e:
            logger.debug(f"Error calculating confidence: {e}")

        return round(confidence, 2)

    def generate_field_label(
        self, field_type: str, element_info: Dict, index: int
    ) -> str:
        """Generate a descriptive label for the field"""

        base_label = field_type.replace("_", " ").title()

        # Add specificity if multiple elements of same type
        if index > 0:
            base_label += f" {index + 1}"

        # Add context from class or id if available
        class_name = element_info.get("class_name", "")
        if class_name:
            # Extract meaningful class parts
            class_parts = [part for part in class_name.split() if len(part) > 2]
            if class_parts:
                context = class_parts[0].replace("-", " ").replace("_", " ").title()
                base_label += f" ({context})"

        return base_label

    def detect_element_type(self, text_content: str) -> str:
        """Detect element type based on text content patterns"""

        text = text_content.lower().strip()

        # Price patterns
        if any(
            symbol in text for symbol in ["$", "€", "£", "¥", "usd", "eur", "price"]
        ):
            return "price"

        # Date patterns
        if any(
            word in text
            for word in [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
                "2020",
                "2021",
                "2022",
                "2023",
                "2024",
                "2025",
            ]
        ):
            return "date"

        # Number patterns
        if text.replace(".", "").replace(",", "").isdigit():
            return "number"

        # Rating patterns
        if any(word in text for word in ["stars", "rating", "score", "review"]):
            return "rating"

        # Default to text
        return "text"

    def optimize_selector(self, base_selector: str, element_info: Dict) -> str:
        """Optimize selector to be more specific if needed"""

        # If element has a unique ID, use that
        if element_info.get("id"):
            return f"#{element_info['id']}"

        # If element has specific classes, use those
        class_name = element_info.get("class_name", "")
        if class_name:
            # Use first meaningful class
            classes = [cls for cls in class_name.split() if len(cls) > 2]
            if classes:
                return f".{classes[0]}"

        return base_selector

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🧹 Detail page analyzer cleanup complete")


# Communication bridge for JavaScript integration
class DetailAnalysisRequestHandler:
    """Handles requests from JavaScript for detail page analysis"""

    def __init__(self):
        self.analyzer = V3DetailPageAnalyzer()
        self.running = False

    async def start_monitoring(self):
        """Start monitoring for analysis requests"""
        self.running = True
        logger.info("👂 Detail analysis request handler started")

        try:
            while self.running:
                await self.check_for_requests()
                await asyncio.sleep(1)  # Check every second
        except Exception as e:
            logger.error(f"❌ Error in request monitoring: {e}")
        finally:
            await self.analyzer.cleanup()

    async def check_for_requests(self):
        """Check for pending analysis requests"""
        try:
            # This would typically check localStorage or a communication channel
            # For now, we'll implement a simple file-based approach
            import os
            import tempfile

            request_file = os.path.join(
                tempfile.gettempdir(), "v3_detail_analysis_request.json"
            )

            if os.path.exists(request_file):
                with open(request_file, "r") as f:
                    request_data = json.load(f)

                # Remove request file to prevent duplicate processing
                os.remove(request_file)

                # Process the request
                await self.process_analysis_request(request_data)

        except Exception as e:
            logger.debug(f"No pending requests or error checking: {e}")

    async def process_analysis_request(self, request_data: Dict):
        """Process a detail page analysis request"""
        try:
            request_id = request_data.get("requestId")
            url = request_data.get("url")

            logger.info(
                f"📥 Processing detail analysis request: {request_id} for {url}"
            )

            # Perform analysis
            result = await self.analyzer.analyze_detail_page(url)

            # Store response for JavaScript to pick up
            await self.store_analysis_response(request_id, result)

            logger.info(f"📤 Analysis complete for request: {request_id}")

        except Exception as e:
            logger.error(f"❌ Error processing analysis request: {e}")
            await self.store_analysis_response(
                request_data.get("requestId"), {"success": False, "error": str(e)}
            )

    async def store_analysis_response(self, request_id: str, result: Dict):
        """Store analysis response for JavaScript to retrieve"""
        try:
            import os
            import tempfile

            response_file = os.path.join(
                tempfile.gettempdir(), f"v3_detail_analysis_response_{request_id}.json"
            )

            with open(response_file, "w") as f:
                json.dump(result, f)

            logger.debug(f"📁 Analysis response stored: {response_file}")

        except Exception as e:
            logger.error(f"❌ Error storing analysis response: {e}")

    def stop_monitoring(self):
        """Stop monitoring for requests"""
        self.running = False
        logger.info("🛑 Detail analysis request handler stopped")


# Example usage
async def main():
    """Example of how to use the detail page analyzer"""
    analyzer = V3DetailPageAnalyzer()

    try:
        # Example analysis
        url = "https://example.com/product/123"
        result = await analyzer.analyze_detail_page(url)

        print("Analysis Result:")
        print(json.dumps(result, indent=2))

    finally:
        await analyzer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
