# Template Endpoints Reference

This document provides complete reference for all template management API endpoints in ScraperV4.

## Template Retrieval

### Get All Templates

**Function:** `get_templates()`

Retrieves all available scraping templates with their metadata.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "templates": [
    {
      "id": "advanced_product_scraper",
      "name": "Advanced Product Scraper",
      "description": "Comprehensive product data extraction",
      "version": "2.0.0",
      "usage_count": 25,
      "success_rate": 92.5,
      "created_at": "2024-01-01T00:00:00Z",
      "selectors": {
        "title": {
          "selector": "h1.product-title",
          "type": "text"
        }
      },
      "fetcher_config": {
        "type": "stealth",
        "timeout": 30
      }
    }
  ]
}
```

**Template Metadata Fields:**
- `id`: Unique template identifier
- `name`: Human-readable template name
- `description`: Template purpose description
- `version`: Template version string
- `usage_count`: Number of times used
- `success_rate`: Success percentage (0-100)
- `created_at`: ISO timestamp of creation
- `selectors`: CSS selector configuration
- `fetcher_config`: Fetcher-specific settings

**Example:**
```javascript
const templates = await eel.get_templates()();
if (templates.success) {
  templates.templates.forEach(template => {
    console.log(`${template.name}: ${template.success_rate}% success`);
  });
}
```

### Get Specific Template

**Function:** `get_template(template_id)`

Retrieves detailed configuration for a specific template.

**Parameters:**
- `template_id` (str): Template identifier or name

**Returns:**
```json
{
  "success": true,
  "template": {
    "id": "advanced_product_scraper",
    "name": "Advanced Product Scraper",
    "description": "Comprehensive product data extraction",
    "selectors": {
      "title": {
        "selector": "h1.product-title",
        "type": "text",
        "auto_save": true,
        "fallback_selectors": [
          ".product-name",
          "h1",
          "[itemprop='name']"
        ]
      },
      "price": {
        "selector": ".price-now",
        "type": "text",
        "auto_save": true,
        "fallback_selectors": [
          ".product-price",
          "[itemprop='price']"
        ]
      }
    },
    "fetcher_config": {
      "type": "auto",
      "stealth": {
        "headless": true,
        "humanize": true,
        "block_webrtc": true
      }
    },
    "validation_rules": {
      "required_fields": ["title", "price"],
      "field_types": {
        "title": "string",
        "price": "number"
      }
    },
    "post_processing": [
      {
        "type": "strip",
        "field": "title"
      },
      {
        "type": "extract_number",
        "field": "price"
      }
    ],
    "adaptive_selectors": {
      "enabled": true,
      "learning_mode": true,
      "similarity_threshold": 0.85
    },
    "fallback_selectors": {
      "enabled": true,
      "max_attempts": 3
    },
    "version": "2.0.0",
    "usage_count": 25,
    "success_rate": 92.5,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Selector Configuration:**
- `selector`: Primary CSS selector
- `type`: Data extraction type (`text`, `all`, `attribute`)
- `auto_save`: Whether to automatically save extracted data
- `fallback_selectors`: Alternative selectors if primary fails

**Fetcher Types:**
- `auto`: Automatically choose best fetcher
- `basic`: Simple HTTP requests
- `async`: Asynchronous HTTP with advanced features
- `stealth`: Browser-based with anti-detection
- `playwright`: Full browser automation

**Example:**
```javascript
const template = await eel.get_template("product_scraper")();
if (template.success) {
  console.log(`Template: ${template.template.name}`);
  console.log(`Selectors: ${Object.keys(template.template.selectors).join(", ")}`);
}
```

## Template Management

### Create Template

**Function:** `create_template(template_data)`

Creates a new scraping template with the specified configuration.

**Parameters:**
- `template_data` (Dict[str, Any]): Template configuration object
  - `name` (str): Template name (required)
  - `description` (str): Template description
  - `selectors` (Dict): CSS selector configuration (required)
  - `fetcher_config` (Dict): Fetcher-specific settings
  - `validation_rules` (Dict): Data validation rules

**Selector Types:**
- `text`: Extract text content from element
- `all`: Extract all matching elements
- `attribute`: Extract specific attribute value
- `html`: Extract HTML content

**Returns:**
```json
{
  "success": true,
  "template_id": "new_template_id",
  "message": "Template created successfully"
}
```

**Example:**
```javascript
const newTemplate = {
  name: "Blog Post Scraper",
  description: "Extract blog post content and metadata",
  selectors: {
    title: {
      selector: "h1.post-title",
      type: "text",
      auto_save: true
    },
    content: {
      selector: ".post-content",
      type: "text",
      auto_save: true
    },
    author: {
      selector: ".author-name",
      type: "text",
      auto_save: true
    }
  },
  fetcher_config: {
    type: "basic",
    timeout: 30
  },
  validation_rules: {
    required_fields: ["title", "content"],
    field_types: {
      title: "string",
      content: "string",
      author: "string"
    }
  }
};

const result = await eel.create_template(newTemplate)();
```

### Update Template

**Function:** `update_template(template_id, template_data)`

Updates an existing template with new configuration.

**Parameters:**
- `template_id` (int): Template identifier to update
- `template_data` (Dict[str, Any]): Updated template configuration

**Updatable Fields:**
- `name`: Template name
- `description`: Template description  
- `selectors`: CSS selector configuration
- `fetcher_config`: Fetcher settings
- `validation_rules`: Validation rules
- `post_processing`: Data processing rules
- `adaptive_selectors`: Adaptive selector settings

**Returns:**
```json
{
  "success": true,
  "message": "Template updated successfully"
}
```

**Example:**
```javascript
const updates = {
  description: "Updated description",
  selectors: {
    ...existingSelectors,
    new_field: {
      selector: ".new-element",
      type: "text",
      auto_save: true
    }
  }
};

const result = await eel.update_template(123, updates)();
```

### Delete Template

**Function:** `delete_template(template_id)`

Permanently deletes a template and all associated data.

**Parameters:**
- `template_id` (int): Template identifier to delete

**Returns:**
```json
{
  "success": true,
  "message": "Template deleted successfully"
}
```

**Warning:** This action is irreversible. All jobs using this template will lose their template reference.

**Example:**
```javascript
const confirmation = confirm("Are you sure you want to delete this template?");
if (confirmation) {
  const result = await eel.delete_template(123)();
}
```

## Template Validation

Templates are automatically validated when created or updated. Validation checks include:

### Selector Validation
- Valid CSS selector syntax
- Required selector fields present
- Proper data type specifications

### Configuration Validation
- Valid fetcher configuration
- Proper validation rule syntax
- Correct post-processing rule format

### Field Type Validation
Supported field types:
- `string`: Text data
- `number`: Numeric data (integer or float)
- `boolean`: True/false values
- `list`: Array of values
- `object`: Complex nested data

### Post-Processing Rules

Available post-processing operations:

**Text Operations:**
- `strip`: Remove leading/trailing whitespace
- `lowercase`: Convert to lowercase
- `uppercase`: Convert to uppercase
- `capitalize`: Capitalize first letter

**Numeric Operations:**
- `extract_number`: Extract numeric value from text
- `parse_float`: Convert to floating-point number
- `parse_int`: Convert to integer

**List Operations:**
- `unique`: Remove duplicate values
- `flatten`: Flatten nested lists
- `sort`: Sort list elements

**Example Post-Processing:**
```json
{
  "post_processing": [
    {
      "type": "strip",
      "field": "title"
    },
    {
      "type": "extract_number",
      "field": "price"
    },
    {
      "type": "lowercase",
      "field": "category"
    }
  ]
}
```

## Advanced Features

### Adaptive Selectors

Adaptive selectors automatically learn and improve selector performance:

```json
{
  "adaptive_selectors": {
    "enabled": true,
    "learning_mode": true,
    "similarity_threshold": 0.85,
    "confidence_threshold": 0.90
  }
}
```

**Configuration Options:**
- `enabled`: Enable adaptive selector learning
- `learning_mode`: Allow automatic selector updates
- `similarity_threshold`: Minimum similarity for selector matching
- `confidence_threshold`: Minimum confidence for automatic updates

### Fallback Selectors

Fallback selectors provide alternatives when primary selectors fail:

```json
{
  "title": {
    "selector": "h1.main-title",
    "fallback_selectors": [
      "h1.page-title",
      "h1",
      ".title",
      "[itemprop='name']"
    ]
  }
}
```

### Pagination Support

Templates can include pagination configuration for multi-page scraping:

```json
{
  "pagination": {
    "enabled": true,
    "next_selector": "a.next-page",
    "max_pages": 10,
    "delay_between_pages": [1, 3],
    "stop_conditions": [
      "no_new_data",
      "duplicate_detection"
    ]
  }
}
```

## Error Handling

Template operations return consistent error responses:

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

**Common Template Errors:**
- `Template not found`: Invalid template_id
- `Invalid selector syntax`: Malformed CSS selector
- `Missing required fields`: Required configuration missing
- `Validation failed`: Template configuration invalid
- `Duplicate template name`: Template name already exists

## See Also

- [Scraping Endpoints](scraping-endpoints.md) - Using templates for scraping
- [Template Schema](../configuration/template-schema.md) - Complete template configuration reference
- [Services Reference](../classes/services.md) - TemplateService class documentation