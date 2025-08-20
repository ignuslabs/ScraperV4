# How to Create Templates Visually with Interactive Selection

This guide provides practical recipes for creating scraping templates using ScraperV4's visual interactive selection system. Each recipe addresses specific scenarios and challenges you'll encounter.

> **🆕 NEW: Playwright Interactive Mode Available!**  
> For universal compatibility without CORS restrictions, see our new [Playwright Template Creation Guide](playwright-template-creation.md). The Playwright mode works on all websites and provides better performance for modern sites.

## Prerequisites

- ScraperV4 with interactive selection feature enabled
- Understanding of basic template concepts
- Chrome, Firefox, or Edge browser
- Target website URL for scraping

## Overview

Visual template creation enables:
- **Point-and-click selection** without writing selectors
- **Automatic pattern recognition** across similar elements
- **Real-time testing** of selections
- **AI-assisted field detection** for common patterns
- **Learning system** that improves with use
- **Cross-site template reuse** for similar structures

## Recipe 1: Creating an E-commerce Product Template

### Goal
Extract product information from an online store including prices, titles, images, and availability.

### Steps

#### 1. Start Interactive Mode

```python
# Via UI
Navigate to Templates → Click "Interactive Mode"

# Via API
eel.start_interactive_mode("https://shop.example.com/products")
```

#### 2. Wait for Page Load

```javascript
// Ensure dynamic content is loaded
Settings → Wait Configuration:
{
  "wait_for": "networkidle",
  "timeout": 5000,
  "element_check": ".product-grid"
}
```

#### 3. Identify Product Container

```javascript
// Click "Add Container"
// Hover over a single product card
// Click when the entire product highlights

// Generated selector:
{
  "container": "div.product-grid > article.product-card"
}
```

#### 4. Select Product Fields

```javascript
// With container selected, click "Add Field" for each:

// Product Title
Click on product name → Name it "title"
// Result: "h3.product-title"

// Price
Click on price → Name it "price"  
// Result: "span.price-now, .price-was"

// Image
Click on product image → Name it "image"
// Result: "img.product-image::attr(src)"

// Link
Right-click product → Select "Extract Link" → Name it "url"
// Result: "a.product-link::attr(href)"
```

#### 5. Handle Special Cases

```javascript
// Sale prices (multiple price elements)
{
  "price_regular": ".price-was::text",
  "price_sale": ".price-now::text",
  "on_sale": ".sale-badge::exists"
}

// Stock status (text-based)
{
  "in_stock": {
    "selector": ".availability",
    "transform": "contains('In Stock')"
  }
}
```

#### 6. Test and Save

```javascript
// Click "Test" to see results
// Review extracted data
// Click "Save Template"

// Template configuration:
{
  "name": "Shop Product Listing",
  "url_pattern": "*/products/*",
  "pagination": {
    "next": "a.next-page"
  }
}
```

## Recipe 2: Scraping News Articles with Comments

### Goal
Extract article content, metadata, and user comments from news websites.

### Steps

#### 1. Detect Article Structure

```javascript
// Click "Auto-Detect"
// System identifies article pattern

// Auto-detected template:
{
  "type": "news_article",
  "headline": "h1.article-title",
  "author": ".author-name",
  "date": "time.published-date",
  "content": "div.article-body"
}
```

#### 2. Refine Content Selection

```javascript
// Remove ads and related articles from content
Click "Edit" on content field
Select "Exclude Elements":
- ".advertisement"
- ".related-articles"
- ".newsletter-signup"

// Refined selector:
{
  "content": "div.article-body > p:not(.ad-container)"
}
```

#### 3. Extract Comments Section

```javascript
// Add container for comments
{
  "comments": {
    "container": ".comment-list .comment",
    "fields": {
      "author": ".comment-author",
      "date": ".comment-date",
      "text": ".comment-text",
      "likes": ".like-count::number"
    }
  }
}
```

#### 4. Handle Lazy-Loaded Comments

```javascript
// Configure dynamic loading
{
  "comments_config": {
    "load_trigger": "button.load-more-comments",
    "max_clicks": 5,
    "wait_between": 2000
  }
}
```

## Recipe 3: Directory Listings with Detail Pages

### Goal
Scrape business directories with listing pages and detailed information pages.

### Steps

#### 1. Create Listing Page Template

```javascript
// Select business cards container
{
  "listings": {
    "container": ".business-listing",
    "fields": {
      "name": "h2.business-name",
      "category": ".category-tag",
      "rating": ".star-rating::attr(data-rating)",
      "detail_url": "a.view-details::attr(href)"
    }
  }
}
```

#### 2. Follow to Detail Pages

```javascript
// Click "Follow Links" on detail_url field
// Interactive mode opens detail page

// Select additional fields:
{
  "detail_page": {
    "phone": ".contact-phone",
    "address": ".full-address",
    "hours": ".business-hours",
    "description": ".business-description",
    "amenities": "ul.amenities li::text[]"
  }
}
```

#### 3. Create Combined Template

```javascript
{
  "listing_extraction": {
    "url_pattern": "*/directory/search*",
    "data": "{{listings}}"
  },
  "detail_extraction": {
    "follow_field": "detail_url",
    "data": "{{detail_page}}",
    "merge_with": "listing"
  }
}
```

## Recipe 4: Handling Single Page Applications (SPAs)

### Goal
Create templates for JavaScript-heavy sites with dynamic content loading.

### Steps

#### 1. Configure for SPA

```javascript
// Settings → Advanced → SPA Mode
{
  "spa_mode": true,
  "wait_strategy": "dom_stable",
  "history_api": true
}
```

#### 2. Wait for Content Rendering

```javascript
// Add explicit waits for elements
{
  "before_selection": {
    "wait_for_element": "[data-loaded='true']",
    "timeout": 10000
  }
}
```

#### 3. Handle Route Changes

```javascript
// Monitor URL changes without page reload
{
  "route_detection": {
    "watch_url": true,
    "patterns": {
      "listing": "/products",
      "detail": "/product/*",
      "cart": "/cart"
    }
  }
}
```

#### 4. Extract Dynamic Data

```javascript
// Use attribute selectors for React/Vue components
{
  "product_id": "[data-product-id]::attr(data-product-id)",
  "component_state": "[data-state]::attr(data-state)",
  "lazy_image": "img[data-src]::attr(data-src)"
}
```

## Recipe 5: Creating Reusable Cross-Site Templates

### Goal
Build templates that work across multiple similar websites.

### Steps

#### 1. Identify Common Patterns

```javascript
// Use generic selectors
{
  "title": "h1, h2, [class*='title'], [class*='heading']",
  "price": "[class*='price'], [data-price], .cost, .amount",
  "description": "[class*='description'], [class*='summary'], .content"
}
```

#### 2. Add Intelligent Fallbacks

```javascript
// Multiple fallback strategies
{
  "fields": {
    "price": {
      "selectors": [
        ".price-now",           // Specific
        "[data-price]",         // Data attribute
        "[class*='price']",     // Class contains
        "span:contains('$')"    // Content-based
      ],
      "extract": "first_match"
    }
  }
}
```

#### 3. Use Pattern Scoring

```javascript
// Enable scoring for best match
{
  "adaptive_selection": true,
  "scoring": {
    "prefer": ["data-attributes", "semantic-html"],
    "avoid": ["deep-nesting", "nth-child"],
    "confidence_threshold": 0.7
  }
}
```

## Recipe 6: Training the AI for Better Detection

### Goal
Improve automatic detection accuracy for your specific use cases.

### Steps

#### 1. Provide Corrections

```javascript
// When auto-detection is wrong:
1. Click "Incorrect" on misidentified field
2. Select correct element
3. Choose correct type:
   - Product Title
   - Price
   - Image
   - Description
   - Custom: [specify]
```

#### 2. Save Domain Patterns

```javascript
// System learns and saves:
{
  "domain": "example.com",
  "corrections": [
    {
      "wrong": ".product-subtitle",
      "correct": ".product-title",
      "type": "title"
    }
  ],
  "patterns": {
    "price": "Always inside .price-wrapper",
    "images": "Use data-src not src"
  }
}
```

#### 3. Export Learning Data

```javascript
// Export for reuse across instances
{
  "export_learning": true,
  "include": ["patterns", "corrections", "success_rates"],
  "format": "json"
}
```

## Recipe 7: Handling Complex Forms and Filters

### Goal
Create templates that interact with search forms and filters before scraping.

### Steps

#### 1. Define Pre-Scraping Actions

```javascript
// Configure form interactions
{
  "pre_actions": [
    {
      "type": "fill_form",
      "selector": "input#search",
      "value": "laptops"
    },
    {
      "type": "select_dropdown",
      "selector": "select#category",
      "value": "electronics"
    },
    {
      "type": "click",
      "selector": "button#search-submit"
    },
    {
      "type": "wait",
      "duration": 2000
    }
  ]
}
```

#### 2. Apply Filters

```javascript
// Set filter combinations
{
  "filters": [
    {
      "price_range": {
        "min": "input#price-min",
        "max": "input#price-max",
        "values": ["0", "1000"]
      }
    },
    {
      "checkboxes": {
        "selector": "input[type='checkbox'][name='brand']",
        "values": ["Apple", "Dell", "HP"]
      }
    }
  ]
}
```

## Advanced Techniques

### Handling Infinite Scroll

```javascript
{
  "infinite_scroll": {
    "enabled": true,
    "trigger": "scroll_to_bottom",
    "wait_for": ".loading-indicator:hidden",
    "max_scrolls": 10,
    "scroll_pause": 1500
  }
}
```

### Extracting Structured Data

```javascript
// For tables
{
  "table_data": {
    "selector": "table.data-table",
    "headers": "thead th::text",
    "rows": "tbody tr",
    "cells": "td::text",
    "output": "structured"
  }
}
```

### Handling Authentication

```javascript
// Login before scraping
{
  "auth": {
    "required": true,
    "type": "form",
    "steps": [
      {"fill": {"#username": "user@example.com"}},
      {"fill": {"#password": "secure_password"}},
      {"click": "button#login"},
      {"wait_for": ".dashboard"}
    ]
  }
}
```

## Performance Optimization

### Selector Efficiency

```javascript
// Optimize selector performance
{
  "optimization": {
    "cache_containers": true,
    "limit_depth": 4,
    "prefer_ids": true,
    "avoid_pseudo": true
  }
}
```

### Batch Processing

```javascript
// Process multiple pages efficiently
{
  "batch_config": {
    "concurrent_pages": 3,
    "reuse_session": true,
    "share_cookies": true
  }
}
```

## Debugging Templates

### Enable Debug Mode

```javascript
{
  "debug": {
    "enabled": true,
    "log_selections": true,
    "show_metrics": true,
    "save_screenshots": true
  }
}
```

### Test Individual Selectors

```javascript
// Test selectors in console
await eel.test_selector_live(
  "div.product-card .price",
  "https://example.com/products"
)
```

### Monitor Success Rates

```javascript
// Track template performance
{
  "monitoring": {
    "track_success": true,
    "alert_threshold": 0.8,
    "sample_size": 100
  }
}
```

## Troubleshooting

### Problem: Elements Not Highlighting

**Solution**:
```javascript
// Check z-index conflicts
Settings → Advanced → Overlay Z-Index: 999999

// Disable site CSS temporarily
Settings → Debug → Disable Site Styles
```

### Problem: Selectors Too Fragile

**Solution**:
```javascript
// Use data attributes when available
"[data-test-id='product-price']"

// Combine multiple attributes
"div[class*='product'][data-type='listing']"

// Use text content matching
"button:contains('Add to Cart')"
```

### Problem: Dynamic Content Not Captured

**Solution**:
```javascript
// Increase wait times
{
  "dynamic_content": {
    "wait": 5000,
    "retry_count": 3,
    "mutation_observer": true
  }
}
```

## Best Practices

1. **Start Simple**: Begin with basic fields, then add complexity
2. **Test Immediately**: Verify each selection works before proceeding
3. **Use Containers**: Group related fields in containers
4. **Add Fallbacks**: Provide alternative selectors for critical fields
5. **Document Patterns**: Note site-specific quirks in template description
6. **Version Templates**: Track changes with semantic versioning
7. **Monitor Performance**: Review success rates regularly
8. **Share Learning**: Export and share patterns with team

## Next Steps

- Explore [Interactive Architecture](/docs/explanations/interactive-architecture.md) for technical details
- Read [API Reference](/docs/reference/interactive-api.md) for programmatic access
- Join community forums to share templates and patterns
- Contribute improvements to the auto-detection system