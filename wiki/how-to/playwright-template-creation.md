# How-To: Create Templates with Playwright Interactive Mode

This guide provides practical recipes for creating scraping templates using ScraperV4's Playwright Interactive Mode. Each recipe addresses specific real-world scenarios and challenges.

## Prerequisites

- ScraperV4 with Playwright dependencies installed
- Basic understanding of web scraping concepts
- Target websites to scrape

## Overview

Playwright Interactive Mode enables:
- **Universal compatibility** - works on all websites without CORS restrictions
- **Real browser automation** - handles JavaScript, dynamic content, and complex interactions
- **Visual element selection** - point-and-click interface with live feedback
- **Anti-detection capabilities** - built-in stealth features for protected sites
- **Advanced interactions** - form filling, pagination, authentication flows

## Recipe 1: E-commerce Product Catalog

### Goal
Extract comprehensive product information from online stores including dynamic pricing and availability.

### Steps

#### 1. Initialize Playwright Session

```javascript
// Navigate to Template Manager → Playwright Interactive Mode
URL: "https://shop.example.com/catalog"
Config: {
  "headless": false,
  "viewport": {"width": 1280, "height": 720},
  "wait_strategy": "networkidle",
  "stealth_mode": true
}
```

#### 2. Handle Dynamic Loading

```javascript
// Wait for product grid to load
Advanced Settings → Dynamic Content:
{
  "wait_for_element": ".product-grid",
  "wait_timeout": 10000,
  "mutation_observer": true,
  "network_idle_timeout": 2000
}
```

#### 3. Select Product Container

```javascript
// Container mode selection
1. Click "Container Mode"
2. Hover over product card until orange highlight appears
3. Click to select
4. Name: "products"
5. Verify pattern recognition shows correct count

// Generated container selector:
{
  "container": "div.product-grid article.product-card",
  "items_detected": 24,
  "uniformity_score": 0.95
}
```

#### 4. Extract Core Product Fields

```javascript
// Field selection within container
Fields to select:

// Product name
{
  "name": "title",
  "selector": "h3.product-name a",
  "type": "text",
  "required": true
}

// Current price
{
  "name": "price_current",
  "selector": ".price-current, .price",
  "type": "price",
  "fallback": [".cost", "[data-price]"]
}

// Original price (if on sale)
{
  "name": "price_original", 
  "selector": ".price-original, .price-was",
  "type": "price",
  "optional": true
}

// Product image
{
  "name": "image_url",
  "selector": "img.product-image",
  "type": "image",
  "attribute": "src",
  "fallback_attribute": "data-src"
}

// Product URL
{
  "name": "product_url",
  "selector": "a.product-link",
  "type": "url", 
  "attribute": "href"
}

// Availability status
{
  "name": "in_stock",
  "selector": ".stock-status",
  "type": "boolean",
  "transform": "contains('In Stock')"
}
```

#### 5. Handle Special Cases

```javascript
// Deal with sale indicators
{
  "name": "on_sale",
  "selector": ".sale-badge, .discount-label",
  "type": "boolean",
  "transform": "exists"
}

// Extract rating if available
{
  "name": "rating",
  "selector": ".rating-stars",
  "type": "rating",
  "attribute": "data-rating",
  "fallback": ".stars::count"
}

// Category information
{
  "name": "category",
  "selector": ".breadcrumb li:last-child, .category-tag",
  "type": "text"
}
```

#### 6. Add Pagination Support

```javascript
// Pagination configuration
1. Click "Pagination Mode"
2. Select next button
3. Configure:

{
  "pagination": {
    "type": "next_button",
    "next_selector": "a.next-page, button[aria-label='Next']",
    "max_pages": 50,
    "wait_after_click": 3000,
    "end_detection": ".pagination-end, .no-more-results"
  }
}
```

## Recipe 2: News Articles with Comments

### Goal
Extract article content, metadata, and user-generated comments from news websites.

### Steps

#### 1. Article Content Extraction

```javascript
// Main article content
{
  "name": "headline",
  "selector": "h1.article-title, h1[itemprop='headline']",
  "type": "text",
  "required": true
}

{
  "name": "author",
  "selector": ".author-name, [rel='author'], .byline",
  "type": "text"
}

{
  "name": "publish_date",
  "selector": "time[datetime], .publish-date",
  "type": "date",
  "attribute": "datetime",
  "fallback": "text"
}

{
  "name": "article_body",
  "selector": ".article-content, .post-content",
  "type": "html",
  "exclude": [".advertisement", ".related-articles"]
}
```

#### 2. Handle Lazy-Loaded Comments

```javascript
// Configure dynamic comment loading
Pre-Actions:
{
  "load_comments": {
    "trigger": "button.load-comments, #load-more-comments",
    "max_clicks": 10,
    "wait_between": 2000,
    "stop_when": ".no-more-comments"
  }
}

// Comments container
{
  "container": "comments",
  "selector": ".comment-list .comment-item",
  "dynamic_loading": true
}

// Comment fields
{
  "comment_author": ".comment-author",
  "comment_date": ".comment-timestamp",
  "comment_text": ".comment-body",
  "comment_likes": ".like-count::number",
  "comment_replies": ".reply-count::number"
}
```

## Recipe 3: Social Media Posts

### Goal
Extract posts, engagement metrics, and metadata from social platforms.

### Steps

#### 1. Handle Infinite Scroll

```javascript
// Infinite scroll configuration
{
  "infinite_scroll": {
    "enabled": true,
    "method": "scroll_to_bottom",
    "scroll_pause": 2000,
    "max_scrolls": 20,
    "new_content_selector": ".post-item[data-loaded='false']",
    "loading_indicator": ".loading-spinner"
  }
}
```

#### 2. Extract Post Content

```javascript
// Post container
{
  "container": "posts",
  "selector": "[data-testid='post'], .post-wrapper",
  "dynamic": true
}

// Post fields
{
  "post_text": ".post-content p",
  "author_name": ".author-link",
  "author_handle": ".username",
  "post_time": "time[datetime]",
  "like_count": "[data-testid='like-count']::number",
  "share_count": "[data-testid='share-count']::number",
  "reply_count": "[data-testid='reply-count']::number"
}
```

#### 3. Extract Media Content

```javascript
// Handle images
{
  "name": "images",
  "selector": ".post-images img",
  "type": "image_list",
  "attribute": "src",
  "multiple": true
}

// Handle videos
{
  "name": "video_url",
  "selector": "video source",
  "type": "url",
  "attribute": "src",
  "optional": true
}
```

## Recipe 4: Real Estate Listings

### Goal
Extract property details, pricing, and contact information from real estate sites.

### Steps

#### 1. Property Listings Grid

```javascript
// Property container
{
  "container": "properties",
  "selector": ".property-card, .listing-item"
}

// Basic property info
{
  "address": ".property-address",
  "price": ".price-display",
  "bedrooms": ".beds::number", 
  "bathrooms": ".baths::number",
  "square_feet": ".sqft::number",
  "property_type": ".property-type"
}
```

#### 2. Follow to Detail Pages

```javascript
// Configure link following
{
  "detail_extraction": {
    "follow_field": "property_url",
    "selector": ".property-link",
    "new_page_fields": {
      "description": ".property-description",
      "amenities": ".amenities-list li::text[]",
      "agent_name": ".agent-info .name",
      "agent_phone": ".agent-phone",
      "mls_number": ".mls-id",
      "lot_size": ".lot-size::number"
    }
  }
}
```

#### 3. Handle Map Integration

```javascript
// Extract coordinates from map
{
  "latitude": "[data-lat]::attr(data-lat)",
  "longitude": "[data-lng]::attr(data-lng)",
  "map_url": ".map-link::attr(href)"
}
```

## Recipe 5: Job Listings

### Goal
Extract job postings with requirements, benefits, and application details.

### Steps

#### 1. Search Results Page

```javascript
// Job listings container
{
  "container": "job_listings",
  "selector": ".job-card, .position-item"
}

// Job summary fields  
{
  "job_title": ".job-title",
  "company_name": ".company-name",
  "location": ".job-location", 
  "salary_range": ".salary-info",
  "job_type": ".employment-type",
  "post_date": ".posted-date"
}
```

#### 2. Job Detail Extraction

```javascript
// Follow to full job description
{
  "detail_page": {
    "follow_link": ".job-title a",
    "fields": {
      "job_description": ".job-description",
      "requirements": ".requirements ul li::text[]",
      "benefits": ".benefits-list li::text[]",
      "company_description": ".company-info",
      "application_deadline": ".deadline-date",
      "remote_options": ".remote-work-info"
    }
  }
}
```

## Recipe 6: Forums and Community Sites

### Goal
Extract discussions, posts, and user interactions from forum platforms.

### Steps

#### 1. Thread Listings

```javascript
// Forum threads
{
  "container": "threads",
  "selector": ".thread-row, .topic-item"
}

{
  "thread_title": ".thread-title a",
  "author": ".thread-author",
  "reply_count": ".reply-count::number",
  "last_post_date": ".last-post-time",
  "thread_url": ".thread-title a::attr(href)"
}
```

#### 2. Thread Content

```javascript
// Individual posts within thread
{
  "container": "posts",
  "selector": ".post-item",
  "follow_from": "thread_url"
}

{
  "post_content": ".post-body",
  "post_author": ".post-author",
  "post_date": ".post-timestamp",
  "user_title": ".user-title",
  "post_number": ".post-number::number"
}
```

## Recipe 7: Restaurant Menus and Reviews

### Goal
Extract menu items, prices, and customer reviews from restaurant websites.

### Steps

#### 1. Menu Extraction

```javascript
// Menu categories
{
  "container": "menu_sections",
  "selector": ".menu-category"
}

{
  "category_name": ".category-title",
  "items_container": {
    "selector": ".menu-item",
    "fields": {
      "item_name": ".item-name", 
      "description": ".item-description",
      "price": ".item-price::price",
      "dietary_info": ".dietary-tags .tag::text[]"
    }
  }
}
```

#### 2. Review Extraction

```javascript
// Customer reviews
{
  "container": "reviews",
  "selector": ".review-item"
}

{
  "reviewer_name": ".reviewer-name",
  "rating": ".star-rating::attr(data-rating)",
  "review_text": ".review-content",
  "review_date": ".review-date",
  "helpful_votes": ".helpful-count::number"
}
```

## Advanced Techniques

### Authentication Flow

```javascript
// Handle login before scraping
{
  "pre_actions": [
    {
      "type": "navigate",
      "url": "https://site.com/login"
    },
    {
      "type": "fill_field",
      "selector": "#username",
      "value": "${ENV:USERNAME}"
    },
    {
      "type": "fill_field", 
      "selector": "#password",
      "value": "${ENV:PASSWORD}"
    },
    {
      "type": "click",
      "selector": "button[type='submit']"
    },
    {
      "type": "wait_for_navigation",
      "timeout": 5000
    }
  ]
}
```

### Form Interactions

```javascript
// Search form automation
{
  "search_automation": {
    "form_selector": "#search-form",
    "fields": {
      "query": "#search-input",
      "category": "select#category",
      "price_min": "#price-from",
      "price_max": "#price-to"
    },
    "submit": "button#search-btn",
    "wait_for_results": ".results-container"
  }
}
```

### Modal and Popup Handling

```javascript
// Dismiss popups automatically
{
  "popup_handling": {
    "dismiss_selectors": [
      ".modal-close",
      ".popup-overlay",
      "[aria-label='Close']",
      ".cookie-banner .accept"
    ],
    "check_interval": 2000,
    "max_attempts": 5
  }
}
```

### Data Transformation

```javascript
// Advanced field processing
{
  "price_field": {
    "selector": ".price",
    "type": "price",
    "transform": [
      "extract_numbers",
      "currency_to_float",
      {"multiply": 100}  // Convert to cents
    ]
  },
  
  "date_field": {
    "selector": ".date",
    "type": "date",
    "format": "MM/DD/YYYY",
    "output_format": "ISO8601"
  }
}
```

## Performance Optimization

### Selector Efficiency

```javascript
// Optimize selectors for speed
{
  "optimization": {
    "prefer_ids": true,
    "avoid_deep_nesting": true,
    "cache_frequent_selectors": true,
    "batch_extractions": true
  }
}
```

### Resource Management

```javascript
// Browser resource limits
{
  "browser_config": {
    "max_memory": "2GB",
    "max_tabs": 5,
    "disable_images": false,  // Set true for faster loading
    "disable_css": false,
    "block_ads": true
  }
}
```

## Error Handling and Debugging

### Robust Selectors

```javascript
// Multiple fallback strategies
{
  "title_field": {
    "selectors": [
      "h1.main-title",        // Primary
      "h1[data-title]",       // Fallback 1  
      "h1:first-child",       // Fallback 2
      ".title-container h1"   // Fallback 3
    ],
    "required": true,
    "validation": {
      "min_length": 3,
      "not_empty": true
    }
  }
}
```

### Debug Mode

```javascript
// Enable comprehensive debugging
{
  "debug": {
    "enabled": true,
    "screenshot_on_error": true,
    "log_selector_performance": true,
    "save_html_snapshots": true,
    "track_element_changes": true
  }
}
```

### Error Recovery

```javascript
// Automatic error recovery
{
  "error_handling": {
    "retry_failed_selectors": true,
    "retry_count": 3,
    "retry_delay": 1000,
    "fallback_to_alternative": true,
    "continue_on_partial_failure": true
  }
}
```

## Best Practices

### 1. Start Simple, Then Enhance
- Begin with basic field extraction
- Add complexity incrementally
- Test each addition thoroughly

### 2. Use Robust Selectors
- Prefer data attributes and IDs
- Avoid position-based selectors
- Always provide fallbacks for critical fields

### 3. Handle Dynamic Content
- Configure appropriate wait strategies
- Use mutation observers for content changes
- Set realistic timeouts

### 4. Respect Website Performance
- Implement appropriate delays
- Don't overwhelm servers
- Use concurrent limits

### 5. Plan for Scale
- Design templates for long-term use
- Document site-specific quirks
- Version control your templates

## Troubleshooting

### Common Issues

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **CORS Still Blocking** | Cannot load page | Check Playwright is enabled, not iframe mode |
| **Slow Performance** | Long extraction times | Optimize selectors, reduce wait times |
| **Missing Elements** | Empty data fields | Check for dynamic loading, add waits |
| **Inconsistent Results** | Variable data quality | Add fallback selectors, improve validation |
| **Memory Issues** | Browser crashes | Reduce concurrent sessions, limit pages |

### Debug Tools

```bash
# Enable Playwright debug logs
export DEBUG=pw:*

# Run with verbose output
python main.py --debug --verbose

# Check specific logs
tail -f logs/playwright_interactive.log
```

## Next Steps

- **Master Advanced Patterns**: Learn complex authentication and multi-step flows
- **Optimize Performance**: Implement efficient selectors and resource management
- **Scale Operations**: Set up distributed scraping with multiple browser instances
- **Build Custom Extensions**: Create reusable components for specific site types

---

**Related Documentation:**
- [Playwright API Reference](../reference/playwright-api.md)
- [Interactive Architecture](../explanations/playwright-architecture.md)
- [Troubleshooting Guide](../reference/troubleshooting.md)