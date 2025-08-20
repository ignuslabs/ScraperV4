# Interactive Template Creation Tutorial

This comprehensive tutorial will guide you through using ScraperV4's powerful interactive element selection feature to create scraping templates visually. You'll learn to point-and-click your way to sophisticated templates without writing code.

## Learning Objectives

By completing this tutorial, you will:
- Master the interactive overlay interface for visual element selection
- Leverage AI-powered auto-detection to identify patterns automatically
- Create complex templates through point-and-click interactions
- Train the system to improve pattern recognition over time
- Handle dynamic sites and single-page applications
- Export templates for reuse across similar sites

## Prerequisites

- ScraperV4 installed and running
- Modern web browser (Chrome, Firefox, or Edge recommended)
- Basic understanding of web page structure
- Completed the "Getting Started" tutorial

## Part 1: Understanding Interactive Mode

### What is Interactive Mode?

Interactive Mode transforms template creation from a technical task into a visual experience. Instead of manually writing CSS selectors, you:

1. **Navigate** to the target website
2. **Click** on elements you want to extract
3. **Review** auto-generated selectors
4. **Save** your template automatically

### Key Components

**Interactive Overlay**: A visual layer that highlights selectable elements
**Auto-Detector**: AI that recognizes patterns and suggests similar elements
**Selector Generator**: Creates robust, self-healing selectors
**Learning System**: Improves pattern recognition from your corrections

## Part 2: Starting Your First Interactive Session

### Step 1: Access Interactive Mode

1. Open ScraperV4 interface (`http://localhost:8080`)
2. Navigate to **Templates** section
3. Click the **Interactive Mode** button (green button with pointer icon)

### Step 2: Choose Target Website

Enter the URL of the website you want to scrape:

```
https://example-shop.com/products
```

You have two options:
- **Embedded Mode**: Opens site in an iframe (works for most sites)
- **New Window Mode**: Opens in separate window (for sites with CORS restrictions)

### Step 3: Understanding the Interface

Once Interactive Mode loads, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│  Interactive Selector Toolbar                           │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │ Add Field│Add Container│ Auto   │ Settings │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                                                         │
│              Target Website (Interactive)               │
│                                                         │
│   [Elements highlight on hover in teal]                │
│   [Selected elements show green border]                │
│   [Container elements show dashed border]              │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Selection Panel                                        │
│  ├─ Container: product-list                            │
│  │  ├─ Field: title (h2.product-name)                  │
│  │  ├─ Field: price (span.price)                       │
│  │  └─ Field: image (img.product-img)                  │
│  └─ Actions: [Test] [Save] [Export]                    │
└─────────────────────────────────────────────────────────┘
```

## Part 3: Selecting Elements

### Basic Element Selection

#### Selecting a Single Field

1. Click **Add Field** button
2. Hover over elements - they'll highlight in teal
3. Click on the element you want to extract
4. Name your field in the popup dialog

**Example**: Selecting a product title
```javascript
// Auto-generated selector
{
  "title": "h2.product-title"
}
```

#### Selecting Multiple Similar Elements

1. Select one example element
2. The auto-detector finds similar elements
3. Review highlighted suggestions
4. Click **Accept All** or refine selection

### Container Selection for Repeating Elements

Containers are crucial for scraping lists or grids of items.

#### Step 1: Identify the Container

1. Click **Add Container** button
2. Hover to find the repeating element wrapper
3. Click when the entire item is highlighted

#### Step 2: Define Fields Within Container

1. With container selected, click **Add Field**
2. Click elements within ONE example item
3. System automatically applies to all items

**Example**: Product listing container
```json
{
  "container": ".product-grid .product-item",
  "fields": {
    "title": ".product-title",
    "price": ".price-tag",
    "image": "img.product-photo",
    "link": "a.product-link::attr(href)"
  }
}
```

### Advanced Selection Techniques

#### Using Auto-Detection

1. Click **Auto-Detect** button
2. System analyzes page structure
3. Review suggested template:

```json
{
  "detected_type": "e-commerce",
  "confidence": 0.92,
  "suggested_fields": {
    "products": {
      "container": "div.products-container article",
      "fields": {
        "name": "h3.product-name",
        "price": "span[data-price]",
        "availability": ".stock-status",
        "rating": ".rating-stars"
      }
    },
    "pagination": {
      "next": "a.next-page",
      "page_numbers": ".pagination a"
    }
  }
}
```

#### Handling Dynamic Content

For JavaScript-rendered content:

1. Wait for page to fully load
2. Click **Settings** → **Wait for Dynamic Content**
3. Set wait time or element to wait for
4. Continue selection after content loads

## Part 4: Refining Selectors

### Understanding Selector Quality

The system rates each selector:

**Quality Indicators**:
- 🟢 **Excellent** (90-100%): Unique, stable selector
- 🟡 **Good** (70-89%): Works but may need fallbacks
- 🔴 **Poor** (< 70%): Too generic or fragile

### Improving Selectors

#### Manual Refinement

1. Click the selector in the selection panel
2. Choose refinement option:
   - **Make More Specific**: Add parent context
   - **Make More Generic**: Remove specific classes
   - **Add Attribute**: Include data attributes
   - **Use Text Content**: Match by text

**Example Refinement**:
```javascript
// Original (fragile)
"div:nth-child(3) > span"

// Refined (robust)
"[data-testid='price'] span.amount"
```

#### Adding Fallback Selectors

1. Click **Add Fallback** next to field
2. Select alternative element
3. System tries fallbacks if primary fails

```json
{
  "price": {
    "primary": ".price-now",
    "fallbacks": [
      ".product-price",
      "[data-price]",
      "span.cost"
    ]
  }
}
```

## Part 5: Testing Your Template

### Live Testing

1. Click **Test** button in selection panel
2. System extracts data using your selectors
3. Review extracted data:

```json
{
  "extracted_data": [
    {
      "title": "Premium Widget",
      "price": "$29.99",
      "image": "https://example.com/widget.jpg"
    },
    {
      "title": "Deluxe Gadget",
      "price": "$49.99",
      "image": "https://example.com/gadget.jpg"
    }
  ],
  "success_rate": 100,
  "errors": []
}
```

### Validation and Corrections

If extraction fails:

1. Failed fields show in red
2. Click **Fix** next to failed field
3. Re-select the correct element
4. System learns from your correction

## Part 6: Training the AI

### Making Corrections

When the auto-detector makes mistakes:

1. Click **Correct** on misidentified element
2. Select the correct element type:
   - Product Title
   - Price
   - Description
   - Image
   - Link
   - Custom...

3. System updates its pattern recognition

### Domain-Specific Learning

The system learns patterns for specific domains:

```json
{
  "domain": "example-shop.com",
  "learned_patterns": {
    "price": "Always in .price-tag with $ symbol",
    "title": "H2 or H3 within product container",
    "availability": "Text content contains 'in stock' or 'out of stock'"
  }
}
```

## Part 7: Saving and Exporting

### Save Your Template

1. Click **Save Template** button
2. Provide template details:

```json
{
  "name": "Example Shop Products",
  "description": "Extracts product listings from Example Shop",
  "tags": ["e-commerce", "products", "prices"],
  "test_url": "https://example-shop.com/products"
}
```

### Export Options

**For Current Site Only**:
```json
{
  "url_pattern": "https://example-shop.com/products/*",
  "exact_match": false
}
```

**For Similar Sites**:
```json
{
  "pattern_type": "e-commerce",
  "adaptable": true,
  "confidence_threshold": 0.8
}
```

## Part 8: Advanced Features

### Handling Pagination

1. Identify pagination elements
2. Click **Add Pagination**
3. Select:
   - Next button
   - Page numbers
   - Load more button
   - Infinite scroll trigger

```json
{
  "pagination": {
    "type": "next_button",
    "selector": "a.next-page",
    "max_pages": 10,
    "wait_between": 2000
  }
}
```

### Extracting Nested Data

For detail pages linked from listings:

1. Select the item link
2. Click **Follow Link**
3. Interactive mode opens detail page
4. Select additional fields
5. System creates multi-level template

```json
{
  "listing_page": {
    "container": ".product-item",
    "fields": {
      "title": ".title",
      "price": ".price",
      "detail_url": "a::attr(href)"
    }
  },
  "detail_page": {
    "follow": "detail_url",
    "fields": {
      "description": ".full-description",
      "specifications": ".specs-table",
      "images": ".gallery img::attr(src)"
    }
  }
}
```

### Working with Shadow DOM

For web components:

1. Enable **Shadow DOM Support** in settings
2. Click through shadow boundaries
3. System generates pierce selectors

```javascript
// Piercing shadow DOM
"custom-element::shadow .internal-element"
```

## Part 9: Tips and Best Practices

### Selection Strategy

1. **Start with containers** for repeating elements
2. **Use data attributes** when available (`data-testid`, `data-name`)
3. **Avoid position-based** selectors (`:nth-child`)
4. **Test immediately** after selecting
5. **Add fallbacks** for critical fields

### Performance Optimization

- Limit selector depth (< 5 levels)
- Use ID and class selectors over complex paths
- Avoid universal selectors (`*`)
- Cache container selections

### Maintenance

- **Version your templates** with semantic versioning
- **Document special cases** in description
- **Test regularly** against live sites
- **Monitor success rates** in production

## Part 10: Troubleshooting

### Common Issues

#### Elements Not Selectable

**Problem**: Clicking doesn't select element
**Solution**: 
- Check if element is in iframe
- Disable ad blockers
- Try New Window mode
- Wait for dynamic content

#### Auto-Detection Fails

**Problem**: AI doesn't recognize patterns
**Solution**:
- Manually select 2-3 examples
- Use domain-specific training
- Check if site uses non-standard markup

#### Selectors Break on Different Pages

**Problem**: Template works on one page but not others
**Solution**:
- Use more generic selectors
- Add multiple fallbacks
- Create page-specific templates

### Getting Help

**In-App Help**:
- Hover over any button for tooltips
- Click **?** icon for contextual help
- Check selector quality indicators

**Community Resources**:
- Template library with examples
- Forum discussions
- Video tutorials

## Practice Exercises

### Exercise 1: Basic Product Scraper

Create a template for an e-commerce site that extracts:
- Product name
- Price
- Image URL
- Availability status

### Exercise 2: News Article Extractor

Build a template for news sites capturing:
- Article title
- Author
- Publication date
- Article content
- Related articles

### Exercise 3: Multi-Page Directory

Create a template that:
- Extracts business listings
- Follows pagination
- Captures detail page information
- Handles missing fields gracefully

## Summary

You've learned to:
- ✅ Navigate the interactive selector interface
- ✅ Select elements visually without writing code
- ✅ Use AI auto-detection for pattern recognition
- ✅ Create robust, self-healing selectors
- ✅ Handle complex scenarios like pagination and nested data
- ✅ Train the system to improve over time
- ✅ Export templates for reuse

## Next Steps

- Read [Visual Template Creation Guide](/docs/how-to/visual-template-creation.md) for advanced techniques
- Explore [Interactive Architecture](/docs/explanations/interactive-architecture.md) to understand the internals
- Check [API Reference](/docs/reference/interactive-api.md) for programmatic access
- Share your templates with the community

---

Congratulations! You're now equipped to create sophisticated scraping templates through visual interaction. The combination of human intuition and AI assistance makes template creation faster and more accessible than ever.