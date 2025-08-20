# Template Schema Reference

This document provides the complete JSON schema and configuration reference for ScraperV4 templates.

## Template Structure Overview

A ScraperV4 template is a JSON configuration file that defines how to extract data from web pages. Templates include selectors, fetcher configuration, validation rules, and processing instructions.

### Basic Template Structure

```json
{
  "name": "template_name",
  "description": "Template description",
  "version": "1.0.0",
  "selectors": { },
  "fetcher_config": { },
  "validation_rules": { },
  "post_processing": [ ],
  "adaptive_selectors": { },
  "fallback_selectors": { },
  "pagination": { },
  "requirements": { }
}
```

## Required Fields

### Template Metadata

**name** *(required)*
- **Type:** String
- **Pattern:** `^[a-zA-Z0-9_-]+$`
- **Max Length:** 100
- **Description:** Unique template identifier
- **Example:** `"advanced_product_scraper"`

**description** *(optional)*
- **Type:** String
- **Max Length:** 500
- **Description:** Human-readable template description
- **Example:** `"Comprehensive product data extraction with fallback selectors"`

**version** *(optional)*
- **Type:** String
- **Pattern:** `^\d+\.\d+\.\d+$`
- **Default:** `"1.0.0"`
- **Description:** Semantic version string
- **Example:** `"2.1.0"`

**selectors** *(required)*
- **Type:** Object
- **Description:** CSS selector configuration for data extraction
- **Min Properties:** 1

## Selector Configuration

### Basic Selector Object

```json
{
  "field_name": {
    "selector": "CSS_SELECTOR",
    "type": "EXTRACTION_TYPE",
    "auto_save": true,
    "fallback_selectors": ["FALLBACK_1", "FALLBACK_2"],
    "attribute": "ATTRIBUTE_NAME",
    "transform": "TRANSFORM_FUNCTION",
    "required": true,
    "default": "DEFAULT_VALUE"
  }
}
```

### Selector Properties

**selector** *(required)*
- **Type:** String
- **Description:** Primary CSS selector for data extraction
- **Examples:**
  - `"h1.product-title"`
  - `".price-current"`
  - `"[data-testid='product-name']"`
  - `"div.content > p:first-child"`

**type** *(required)*
- **Type:** String
- **Options:** `text`, `all`, `attribute`, `html`, `href`, `src`
- **Description:** Data extraction method
- **Examples:**
  - `"text"` - Extract text content
  - `"all"` - Extract all matching elements
  - `"attribute"` - Extract specific attribute value
  - `"html"` - Extract HTML content
  - `"href"` - Extract href attribute (shorthand)
  - `"src"` - Extract src attribute (shorthand)

**auto_save** *(optional)*
- **Type:** Boolean
- **Default:** `true`
- **Description:** Whether to include field in saved results
- **Example:** `true`

**fallback_selectors** *(optional)*
- **Type:** Array of Strings
- **Description:** Alternative selectors if primary fails
- **Example:** `[".product-name", "h1", "[itemprop='name']"]`

**attribute** *(optional)*
- **Type:** String
- **Description:** Attribute name to extract (when type is "attribute")
- **Examples:** `"href"`, `"src"`, `"data-price"`, `"title"`

**transform** *(optional)*
- **Type:** String
- **Options:** `strip`, `lowercase`, `uppercase`, `capitalize`, `extract_number`
- **Description:** Data transformation function
- **Example:** `"extract_number"`

**required** *(optional)*
- **Type:** Boolean
- **Default:** `false`
- **Description:** Whether field is required for successful extraction
- **Example:** `true`

**default** *(optional)*
- **Type:** Any
- **Description:** Default value if extraction fails
- **Examples:** `""`, `0`, `null`, `[]`

### Selector Examples

#### Text Extraction
```json
{
  "title": {
    "selector": "h1.product-title",
    "type": "text",
    "auto_save": true,
    "required": true,
    "fallback_selectors": [
      ".product-name",
      "h1",
      "[itemprop='name']"
    ]
  }
}
```

#### Attribute Extraction
```json
{
  "product_image": {
    "selector": ".product-gallery img",
    "type": "attribute",
    "attribute": "src",
    "auto_save": true,
    "fallback_selectors": [
      ".hero-image img",
      ".main-image"
    ]
  }
}
```

#### Multiple Elements
```json
{
  "features": {
    "selector": ".feature-list li",
    "type": "all",
    "auto_save": true,
    "transform": "strip",
    "default": []
  }
}
```

#### HTML Content
```json
{
  "description": {
    "selector": ".product-description",
    "type": "html",
    "auto_save": true,
    "fallback_selectors": [
      ".description",
      "[itemprop='description']"
    ]
  }
}
```

## Fetcher Configuration

### Fetcher Types

**type** *(optional)*
- **Type:** String
- **Options:** `auto`, `basic`, `async`, `stealth`, `playwright`
- **Default:** `"auto"`
- **Description:** Fetcher engine to use

### Auto Fetcher
```json
{
  "fetcher_config": {
    "type": "auto",
    "preference_order": ["stealth", "async", "basic"]
  }
}
```

### Basic Fetcher
```json
{
  "fetcher_config": {
    "type": "basic",
    "timeout": 30,
    "headers": {
      "Accept": "text/html,application/xhtml+xml",
      "Accept-Language": "en-US,en;q=0.9",
      "Cache-Control": "no-cache"
    },
    "follow_redirects": true,
    "max_redirects": 5
  }
}
```

### Async Fetcher
```json
{
  "fetcher_config": {
    "type": "async",
    "timeout": 30,
    "follow_redirects": true,
    "max_redirects": 5,
    "retry_attempts": 3,
    "retry_delay": [1, 3],
    "headers": {
      "User-Agent": "ScraperV4/1.0",
      "Accept": "text/html,application/xhtml+xml"
    }
  }
}
```

### Stealth Fetcher
```json
{
  "fetcher_config": {
    "type": "stealth",
    "headless": true,
    "humanize": true,
    "block_webrtc": true,
    "spoof_canvas": true,
    "os_randomization": true,
    "network_idle": true,
    "wait_for_selector": ".product-container",
    "wait_for_timeout": 10,
    "google_search": true,
    "disable_ads": true,
    "screenshot": false,
    "full_page_screenshot": false
  }
}
```

### Playwright Fetcher
```json
{
  "fetcher_config": {
    "type": "playwright",
    "headless": true,
    "network_idle": true,
    "wait_for_selector": ".product-list",
    "wait_for_timeout": 30,
    "block_resources": ["image", "font", "media"],
    "viewport": {
      "width": 1920,
      "height": 1080
    },
    "extra_headers": {
      "Accept-Language": "en-US"
    },
    "geolocation": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }
}
```

## Validation Rules

### Field Validation

```json
{
  "validation_rules": {
    "required_fields": ["title", "price"],
    "field_types": {
      "title": "string",
      "price": "number",
      "description": "string",
      "images": "list",
      "availability": "string",
      "rating": "number",
      "reviews_count": "number",
      "is_featured": "boolean"
    },
    "field_patterns": {
      "availability": "^(in stock|out of stock|limited|available)$",
      "email": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$",
      "phone": "^\\+?[1-9]\\d{1,14}$"
    },
    "field_ranges": {
      "price": [0, 10000],
      "rating": [0, 5],
      "reviews_count": [0, null]
    },
    "custom_validators": [
      {
        "name": "price_validation",
        "field": "price",
        "function": "validate_price_format"
      }
    ]
  }
}
```

### Validation Properties

**required_fields** *(optional)*
- **Type:** Array of Strings
- **Description:** Fields that must have values
- **Example:** `["title", "price", "description"]`

**field_types** *(optional)*
- **Type:** Object
- **Description:** Expected data types for fields
- **Supported Types:** `string`, `number`, `integer`, `boolean`, `list`, `object`

**field_patterns** *(optional)*
- **Type:** Object
- **Description:** Regular expression patterns for field validation
- **Example:** `{"email": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"}`

**field_ranges** *(optional)*
- **Type:** Object
- **Description:** Numeric range validation for fields
- **Format:** `[min_value, max_value]` (use `null` for unbounded)

**custom_validators** *(optional)*
- **Type:** Array of Objects
- **Description:** Custom validation functions
- **Properties:**
  - `name`: Validator identifier
  - `field`: Target field name
  - `function`: Validation function name

## Post-Processing Rules

### Processing Operations

```json
{
  "post_processing": [
    {
      "type": "strip",
      "field": "title"
    },
    {
      "type": "extract_number",
      "field": "price",
      "options": {
        "decimal_places": 2,
        "currency_symbol": "$"
      }
    },
    {
      "type": "lowercase",
      "field": "availability"
    },
    {
      "type": "unique",
      "field": "tags"
    },
    {
      "type": "custom",
      "field": "description",
      "function": "clean_html_tags"
    }
  ]
}
```

### Available Processing Types

#### Text Operations
- **strip**: Remove leading/trailing whitespace
- **lowercase**: Convert to lowercase
- **uppercase**: Convert to uppercase
- **capitalize**: Capitalize first letter
- **trim**: Remove specific characters
- **replace**: Replace text patterns

#### Numeric Operations
- **extract_number**: Extract numeric value from text
- **parse_float**: Convert to floating-point number
- **parse_int**: Convert to integer
- **round**: Round to specified decimal places
- **format_currency**: Format as currency

#### List Operations
- **unique**: Remove duplicate values
- **flatten**: Flatten nested lists
- **sort**: Sort list elements
- **filter**: Filter by criteria
- **limit**: Limit number of items

#### Validation Operations
- **validate_email**: Email format validation
- **validate_url**: URL format validation
- **validate_phone**: Phone number validation

#### Custom Operations
- **custom**: Apply custom processing function

## Advanced Features

### Adaptive Selectors

```json
{
  "adaptive_selectors": {
    "enabled": true,
    "learning_mode": true,
    "similarity_threshold": 0.85,
    "confidence_threshold": 0.90,
    "max_attempts": 3,
    "fallback_strategy": "closest_match"
  }
}
```

**Properties:**
- **enabled**: Enable adaptive selector learning
- **learning_mode**: Allow automatic selector updates
- **similarity_threshold**: Minimum similarity for selector matching (0.0-1.0)
- **confidence_threshold**: Minimum confidence for automatic updates (0.0-1.0)
- **max_attempts**: Maximum adaptation attempts
- **fallback_strategy**: Strategy when adaptation fails

### Fallback Selectors

```json
{
  "fallback_selectors": {
    "enabled": true,
    "max_attempts": 3,
    "cascade_mode": true,
    "similarity_check": true,
    "confidence_threshold": 0.8
  }
}
```

### Pagination Support

```json
{
  "pagination": {
    "enabled": true,
    "next_selector": "a.next-page",
    "max_pages": 10,
    "delay_between_pages": [1, 3],
    "stop_conditions": [
      "no_new_data",
      "duplicate_detection",
      "max_pages_reached"
    ],
    "url_pattern": "https://example.com/page/{page}",
    "page_parameter": "page",
    "start_page": 1
  }
}
```

## Requirements Configuration

```json
{
  "requirements": {
    "javascript_required": false,
    "stealth_required": false,
    "anti_bot_protection": false,
    "concurrent_scraping": true,
    "min_scrapling_version": "2.0.0",
    "supported_fetchers": ["stealth", "async", "basic"],
    "blocked_domains": ["example-blocked.com"],
    "allowed_domains": ["example.com", "*.example.org"]
  }
}
```

## Template Metadata

### Automatic Fields
These fields are automatically managed by ScraperV4:

```json
{
  "is_active": true,
  "usage_count": 25,
  "success_rate": 94.5,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_used": "2024-01-20T15:45:00Z",
  "performance_metrics": {
    "average_extraction_time": 1.2,
    "average_success_rate": 94.5,
    "total_runs": 150,
    "recent_failures": 3
  }
}
```

## Complete Template Example

```json
{
  "name": "advanced_product_scraper",
  "description": "Comprehensive product data extraction with anti-bot protection",
  "version": "2.1.0",
  
  "fetcher_config": {
    "type": "stealth",
    "headless": true,
    "humanize": true,
    "block_webrtc": true,
    "wait_for_selector": ".product-container",
    "google_search": true,
    "disable_ads": true
  },
  
  "requirements": {
    "javascript_required": true,
    "stealth_required": true,
    "anti_bot_protection": true,
    "concurrent_scraping": false
  },
  
  "selectors": {
    "title": {
      "selector": "h1.product-title",
      "type": "text",
      "auto_save": true,
      "required": true,
      "fallback_selectors": [
        ".product-name",
        "h1",
        "[itemprop='name']"
      ]
    },
    "price": {
      "selector": ".price-current .sr-only",
      "type": "text",
      "auto_save": true,
      "required": true,
      "transform": "extract_number",
      "fallback_selectors": [
        ".price-now",
        "[itemprop='price']",
        ".cost"
      ]
    },
    "description": {
      "selector": ".product-description",
      "type": "html",
      "auto_save": true,
      "fallback_selectors": [
        ".description",
        "[itemprop='description']"
      ]
    },
    "images": {
      "selector": ".product-images img",
      "type": "attribute",
      "attribute": "src",
      "auto_save": true,
      "default": []
    },
    "availability": {
      "selector": ".availability-status",
      "type": "text",
      "auto_save": true,
      "transform": "lowercase",
      "default": "unknown"
    },
    "rating": {
      "selector": ".rating-value",
      "type": "text",
      "auto_save": true,
      "transform": "extract_number",
      "default": 0
    }
  },
  
  "pagination": {
    "enabled": true,
    "next_selector": "a.pagination-next",
    "max_pages": 5,
    "delay_between_pages": [2, 4]
  },
  
  "post_processing": [
    {
      "type": "strip",
      "field": "title"
    },
    {
      "type": "extract_number",
      "field": "price",
      "options": {
        "decimal_places": 2
      }
    },
    {
      "type": "validate_url",
      "field": "images"
    }
  ],
  
  "validation_rules": {
    "required_fields": ["title", "price"],
    "field_types": {
      "title": "string",
      "price": "number",
      "description": "string",
      "images": "list",
      "availability": "string",
      "rating": "number"
    },
    "field_patterns": {
      "availability": "^(in stock|out of stock|limited|available|unknown)$"
    },
    "field_ranges": {
      "price": [0, null],
      "rating": [0, 5]
    }
  },
  
  "adaptive_selectors": {
    "enabled": true,
    "learning_mode": true,
    "similarity_threshold": 0.85
  },
  
  "fallback_selectors": {
    "enabled": true,
    "max_attempts": 3
  }
}
```

## Schema Validation

ScraperV4 automatically validates templates against this schema:

### Validation Levels
- **Error**: Critical issues that prevent template usage
- **Warning**: Non-critical issues that may affect performance
- **Info**: Suggestions for optimization

### Common Validation Errors
- Missing required fields (`name`, `selectors`)
- Invalid CSS selector syntax
- Unsupported fetcher configuration
- Invalid field type specifications
- Malformed regex patterns

## See Also

- [Environment Variables](environment-variables.md) - Global configuration options
- [Template Endpoints](../api/template-endpoints.md) - Template management API
- [Scraping Endpoints](../api/scraping-endpoints.md) - Using templates for scraping
- [Services Reference](../classes/services.md) - TemplateService implementation