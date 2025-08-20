# Creating Your First Template

This interactive tutorial will guide you through creating and customizing powerful scraping templates in ScraperV4. You'll learn to build templates from scratch, understand advanced selectors, implement data processing, and handle complex scenarios.

## Learning Objectives

By completing this tutorial, you will:
- Master CSS and XPath selector syntax
- Understand template structure and components
- Implement data processing and validation rules
- Handle pagination and navigation
- Test and debug templates effectively
- Create reusable template patterns

## Prerequisites

- Completed the "Getting Started" tutorial
- Basic understanding of HTML structure
- ScraperV4 running on your system
- Browser developer tools familiarity

## Understanding Template Architecture

### Template Components

A ScraperV4 template consists of several key components:

```json
{
  "name": "Template Name",
  "description": "What this template does",
  "selectors": {
    "field_name": "CSS or XPath selector"
  },
  "post_processing": {
    "rule_type": "configuration"
  },
  "pagination": {
    "navigation_rules": "configuration"
  },
  "validation": {
    "data_quality_rules": "configuration"
  }
}
```

### Selector Types

**CSS Selectors**: Fast and intuitive
- `h1` - Selects all h1 elements
- `.class-name` - Selects by class
- `#element-id` - Selects by ID
- `[attribute="value"]` - Selects by attribute

**XPath Selectors**: More powerful and flexible
- `//h1` - Selects all h1 elements anywhere
- `//div[@class="content"]` - Selects div with specific class
- `//a[contains(@href, "product")]` - Contains match

## Step 1: Setting Up Your Template Workspace

### 1.1 Access Template Manager

1. Open ScraperV4 web interface (`http://localhost:8080`)
2. Navigate to **Templates**
3. Click **Create New Template**

### 1.2 Choose Your Target Website

For this tutorial, we'll create templates for different types of websites:

**Example 1**: E-commerce product pages
**Example 2**: News article sites  
**Example 3**: Directory listings

Let's start with an e-commerce template for demonstration purposes.

## Step 2: Building a Product Template

### 2.1 Template Metadata

Fill in the basic information:

```json
{
  "name": "E-commerce Product Scraper",
  "description": "Extracts product information including title, price, description, images, and reviews",
  "version": "1.0",
  "category": "e-commerce"
}
```

### 2.2 Basic Product Selectors

Start with essential product fields:

```json
{
  "selectors": {
    "title": "h1.product-title::text",
    "price": ".price-current .sr-only::text",
    "original_price": ".price-was::text",
    "description": ".product-description p::text",
    "sku": "[data-sku]::attr(data-sku)",
    "brand": ".product-brand::text"
  }
}
```

**Understanding the Syntax**:
- `::text` - Extracts text content
- `::attr(attribute)` - Extracts attribute value
- Multiple selectors can be separated by commas

### 2.3 Testing Basic Selectors

Before proceeding, test your selectors:

1. Enter a product URL in the **Test URL** field
2. Click **Test Selectors**
3. Review the extracted data

**Expected Output**:
```json
{
  "title": "Wireless Bluetooth Headphones",
  "price": "$99.99",
  "original_price": "$149.99",
  "description": "High-quality wireless headphones with noise cancellation",
  "sku": "WBH-001",
  "brand": "AudioTech"
}
```

## Step 3: Advanced Selector Techniques

### 3.1 Handling Multiple Elements

For elements that appear multiple times (like images or features):

```json
{
  "images": "img.product-image::attr(src)",
  "features": ".feature-list li::text",
  "categories": ".breadcrumb a::text",
  "color_options": ".color-selector [data-color]::attr(data-color)"
}
```

### 3.2 Conditional Selectors

Sometimes elements may not exist. Use fallback selectors:

```json
{
  "availability": ".stock-status::text, .availability-info::text, .in-stock::text",
  "rating": ".rating-stars::attr(data-rating), .star-rating .rating::text"
}
```

### 3.3 Complex XPath Selectors

For more complex extraction needs:

```json
{
  "specifications": "//table[@class='specs']//tr[td[1]]/td[2]/text()",
  "reviews_count": "//span[contains(text(), 'reviews')]/preceding-sibling::span/text()",
  "delivery_info": "//div[contains(@class, 'delivery')]//text()[normalize-space()]"
}
```

**XPath Functions**:
- `contains()` - Partial text matching
- `text()` - Text content
- `normalize-space()` - Removes extra whitespace
- `preceding-sibling::` - Navigate to sibling elements

## Step 4: Data Processing Rules

### 4.1 Text Cleaning

Clean up extracted text with processing rules:

```json
{
  "post_processing": {
    "clean_text": true,
    "remove_extra_spaces": true,
    "normalize_unicode": true,
    "remove_html_tags": true,
    "strip_whitespace": true
  }
}
```

### 4.2 Data Type Conversion

Convert data to appropriate types:

```json
{
  "data_conversion": {
    "extract_numbers": ["price", "original_price", "rating"],
    "extract_currency": ["price", "original_price"],
    "parse_dates": ["publish_date", "last_updated"],
    "boolean_fields": ["in_stock", "on_sale"]
  }
}
```

### 4.3 URL Processing

Handle relative URLs and normalize paths:

```json
{
  "url_processing": {
    "normalize_urls": ["images", "product_links"],
    "resolve_relative": true,
    "add_protocol": "https",
    "validate_urls": true
  }
}
```

### 4.4 Custom Processing Rules

Apply custom transformations:

```json
{
  "custom_processing": {
    "price": {
      "remove_currency_symbol": true,
      "convert_to_float": true
    },
    "features": {
      "join_with": ", ",
      "remove_empty": true
    },
    "categories": {
      "reverse_order": true,
      "join_with": " > "
    }
  }
}
```

## Step 5: Implementing Pagination

### 5.1 Basic Pagination

Handle multi-page results:

```json
{
  "pagination": {
    "enabled": true,
    "next_page_selector": ".pagination .next:not(.disabled)",
    "max_pages": 50,
    "wait_time": 2
  }
}
```

### 5.2 Advanced Pagination Strategies

**Numbered Pagination**:
```json
{
  "pagination": {
    "type": "numbered",
    "page_url_pattern": "https://example.com/products?page={page}",
    "start_page": 1,
    "max_pages": 100,
    "auto_detect_last_page": true
  }
}
```

**Infinite Scroll**:
```json
{
  "pagination": {
    "type": "infinite_scroll",
    "trigger_selector": ".load-more-button",
    "wait_for_selector": ".product-item",
    "max_scrolls": 20
  }
}
```

### 5.3 Pagination with Parameters

Handle URL parameters:

```json
{
  "pagination": {
    "type": "parameter_based",
    "parameters": {
      "offset": {
        "start": 0,
        "increment": 20
      },
      "limit": 20
    },
    "stop_condition": "no_new_items"
  }
}
```

## Step 6: Data Validation

### 6.1 Required Fields

Ensure critical data is present:

```json
{
  "validation": {
    "required_fields": ["title", "price"],
    "minimum_fields": 3,
    "skip_incomplete_items": true
  }
}
```

### 6.2 Data Type Validation

Validate data types and formats:

```json
{
  "field_validation": {
    "price": {
      "type": "number",
      "min": 0,
      "max": 10000
    },
    "email": {
      "type": "email",
      "required": false
    },
    "url": {
      "type": "url",
      "validate_accessible": false
    }
  }
}
```

### 6.3 Content Validation

Validate content quality:

```json
{
  "content_validation": {
    "title": {
      "min_length": 5,
      "max_length": 200,
      "no_placeholder_text": true
    },
    "description": {
      "min_words": 10,
      "max_words": 500
    }
  }
}
```

## Step 7: Template Testing and Debugging

### 7.1 Interactive Testing

Use the built-in template tester:

1. **Single URL Test**: Test against one specific page
2. **Multiple URL Test**: Test against several representative pages
3. **Pagination Test**: Test pagination logic

### 7.2 Debug Mode

Enable detailed debugging:

```json
{
  "debug_options": {
    "save_html": true,
    "log_selectors": true,
    "highlight_matches": true,
    "screenshot_pages": true
  }
}
```

### 7.3 Common Issues and Solutions

**Issue 1**: Selector returns no data
```json
// Solution: Add fallback selectors
"title": "h1.product-title::text, h1.title::text, .product-name::text"
```

**Issue 2**: Getting unwanted text
```json
// Solution: Use more specific selectors
"price": ".price-current .amount::text"  // Instead of ".price-current::text"
```

**Issue 3**: Pagination not working
```json
// Solution: Add wait conditions
"pagination": {
  "next_page_selector": ".next-page",
  "wait_for_load": ".product-list",
  "wait_time": 3
}
```

## Step 8: Hands-on Exercise

### Exercise 1: News Article Template

Create a template for news articles with these requirements:

**Target Site**: Any news website
**Required Fields**:
- Article title
- Author name
- Publication date
- Article content
- Tags/categories
- Related articles

**Advanced Requirements**:
- Handle different date formats
- Extract social media share counts
- Handle both single articles and article lists

**Starter Template**:
```json
{
  "name": "News Article Scraper",
  "selectors": {
    "title": "h1, .article-title, .headline",
    "author": ".author, .byline, [rel='author']",
    "date": ".publish-date, .article-date, time[datetime]",
    "content": ".article-content p, .story-body p",
    "tags": ".tags a, .categories a"
  },
  "post_processing": {
    "clean_text": true,
    "join_content": {
      "field": "content",
      "separator": "\n\n"
    },
    "parse_dates": ["date"]
  }
}
```

### Exercise 2: Directory Listing Template

Create a template for business directories:

**Required Fields**:
- Business name
- Address
- Phone number
- Website URL
- Business hours
- Rating

**Challenges**:
- Handle incomplete listings
- Parse structured data (JSON-LD)
- Extract coordinates from map links

## Step 9: Advanced Template Patterns

### 9.1 Dynamic Content Templates

Handle JavaScript-loaded content:

```json
{
  "dynamic_content": {
    "wait_for_selector": ".dynamic-content",
    "max_wait_time": 10,
    "scroll_to_load": true,
    "execute_js": "window.scrollTo(0, document.body.scrollHeight);"
  }
}
```

### 9.2 Multi-Step Templates

Navigate through multiple pages:

```json
{
  "navigation_steps": [
    {
      "action": "click",
      "selector": ".view-details",
      "wait_for": ".product-details"
    },
    {
      "action": "scroll",
      "direction": "down",
      "pixels": 500
    }
  ]
}
```

### 9.3 Conditional Logic

Apply different rules based on page content:

```json
{
  "conditional_selectors": {
    "price": {
      "if_exists": ".sale-price",
      "then": ".sale-price::text",
      "else": ".regular-price::text"
    }
  }
}
```

## Step 10: Template Optimization

### 10.1 Performance Optimization

Optimize for speed and reliability:

```json
{
  "performance": {
    "minimize_requests": true,
    "cache_selectors": true,
    "parallel_extraction": true,
    "timeout_per_page": 30
  }
}
```

### 10.2 Error Handling

Robust error handling:

```json
{
  "error_handling": {
    "skip_on_error": true,
    "retry_failed_selectors": 2,
    "fallback_values": {
      "price": "N/A",
      "availability": "Unknown"
    }
  }
}
```

### 10.3 Template Versioning

Manage template versions:

```json
{
  "version_info": {
    "version": "2.1",
    "changelog": "Added fallback selectors for price field",
    "compatibility": ["ScraperV4 >= 1.0"],
    "last_tested": "2024-01-15"
  }
}
```

## Template Best Practices

### Selector Best Practices

1. **Be Specific**: Use class names and IDs when possible
2. **Use Fallbacks**: Always provide alternative selectors
3. **Avoid Position-based**: Don't rely on element position numbers
4. **Test Thoroughly**: Test on multiple pages and layouts

### Data Quality Best Practices

1. **Validate Everything**: Check data types and formats
2. **Handle Nulls**: Plan for missing data
3. **Clean Data**: Remove unwanted characters and formatting
4. **Normalize**: Ensure consistent data formats

### Maintenance Best Practices

1. **Document Selectors**: Comment complex selectors
2. **Version Control**: Track template changes
3. **Regular Testing**: Periodically verify templates still work
4. **Monitor Changes**: Watch for website structure changes

## Common Template Patterns

### E-commerce Product
```json
{
  "name": "Product Template",
  "selectors": {
    "title": "h1, .product-title",
    "price": ".price, .cost, .amount",
    "images": "img[src*='product']::attr(src)",
    "description": ".description, .details",
    "specifications": ".specs tr td:nth-child(2)"
  }
}
```

### Blog Post
```json
{
  "name": "Blog Template",
  "selectors": {
    "title": "h1, .post-title, .entry-title",
    "content": ".post-content, .entry-content, article",
    "author": ".author, .byline",
    "date": ".date, .published, time[datetime]"
  }
}
```

### Contact Directory
```json
{
  "name": "Directory Template",
  "selectors": {
    "name": ".name, .title",
    "email": "a[href^='mailto:']::attr(href)",
    "phone": ".phone, .tel",
    "address": ".address, .location"
  }
}
```

## Summary

You've now learned to create sophisticated scraping templates with:

1. **Advanced Selectors**: CSS and XPath for precise data extraction
2. **Data Processing**: Cleaning, validation, and transformation
3. **Pagination**: Handling multi-page navigation
4. **Error Handling**: Robust templates that handle edge cases
5. **Optimization**: Performance and maintenance considerations

### Next Steps

- Explore the **Advanced Scraping** tutorial for stealth techniques
- Learn **API Integration** for programmatic template management
- Check the **Troubleshooting Guide** for complex scenarios

Your templates are now ready for production scraping with ScraperV4's advanced features!