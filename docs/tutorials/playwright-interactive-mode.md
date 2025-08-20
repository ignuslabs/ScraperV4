# Tutorial: Getting Started with Playwright Interactive Mode

This hands-on tutorial will teach you how to use ScraperV4's Playwright Interactive Mode to create templates by visually selecting elements on websites - without CORS restrictions or security limitations.

## What You'll Learn

By the end of this tutorial, you'll be able to:
- Launch Playwright interactive sessions for any website
- Visually select elements using the browser overlay
- Create and save functional scraping templates
- Handle dynamic content and JavaScript-heavy sites
- Debug and optimize your selections

## Prerequisites

- ScraperV4 installed with Playwright dependencies
- Basic understanding of web scraping concepts
- Chrome, Firefox, or Edge browser (automated by Playwright)

## What is Playwright Interactive Mode?

Playwright Interactive Mode solves the fundamental limitation of traditional browser-based interactive selection: **CORS restrictions**. Instead of loading websites in an iframe (which fails for many sites), it uses Playwright to launch a real browser instance that ScraperV4 controls programmatically.

**Key Advantages:**
- ✅ Works on **all websites** (no CORS restrictions)
- ✅ Handles JavaScript and dynamic content perfectly
- ✅ Real browser environment with full rendering
- ✅ Anti-detection capabilities built-in
- ✅ Visual element selection with real-time feedback

## Step 1: Launch Your First Interactive Session

### 1.1 Start ScraperV4

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python main.py
```

Open your browser and navigate to `http://localhost:8080`

### 1.2 Open Template Manager

1. Click **"Templates"** in the navigation menu
2. Click **"Create New Template"**
3. Choose **"Playwright Interactive Mode"**

### 1.3 Enter Target URL

For this tutorial, we'll scrape a product page:

```
Target URL: https://books.toscrape.com/
```

**Configuration:**
- Headless: `False` (so you can see the browser)
- Wait timeout: `5000ms`
- Browser: `Chromium`

Click **"Start Interactive Session"**

### 1.4 What Happens Next

ScraperV4 will:
1. Launch a Playwright browser instance
2. Navigate to your target URL
3. Inject the interactive overlay JavaScript
4. Display a live screenshot in your interface
5. Enable element selection mode

## Step 2: Understanding the Interface

### 2.1 The Browser View

You'll see:
- **Live Screenshot**: Real-time view of the browser
- **Element Selector**: Green overlay highlighting elements
- **Selection Toolbar**: Controls for different selection modes
- **Field Manager**: List of selected fields and containers

### 2.2 Selection Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **Element Selection** | Select individual data fields | Product titles, prices, descriptions |
| **Container Selection** | Select repeating elements | Product cards, article lists |
| **Link Following** | Extract and follow links | Product detail pages |
| **Action Recording** | Record user interactions | Form filling, navigation |

### 2.3 Visual Feedback

- **Green Highlight**: Element under cursor
- **Blue Outline**: Selected element
- **Orange Box**: Container element
- **Red Border**: Invalid/problematic element

## Step 3: Selecting Your First Elements

### 3.1 Select a Container

Containers are repeating elements that hold similar data structures.

1. Click **"Container Mode"** in the toolbar
2. Hover over a product card until it highlights in orange
3. Click to select it
4. Name it: `"products"`

**What you've done:** Told ScraperV4 that each product card contains fields you want to extract.

### 3.2 Select Individual Fields

Now we'll select fields within each product:

#### Product Title
1. Click **"Field Mode"**
2. Hover over a product title until it highlights
3. Click to select
4. Name it: `"title"`
5. Field type: `"text"`

#### Product Price
1. Hover over a price element
2. Click to select
3. Name it: `"price"`
4. Field type: `"price"` (automatic number parsing)

#### Product Image
1. Hover over a product image
2. Click to select
3. Name it: `"image_url"`
4. Field type: `"image"` (extracts src attribute)

### 3.3 Review Your Selections

In the Field Manager, you should see:
```
Container: products
├── title (text)
├── price (price)  
└── image_url (image)
```

## Step 4: Testing Your Template

### 4.1 Test Individual Fields

1. Click the **"Test"** button next to any field
2. View the extracted data preview
3. Check that the data looks correct

### 4.2 Test the Complete Template

1. Click **"Test Template"** at the bottom
2. ScraperV4 will extract data from all visible products
3. Review the results in JSON format

**Sample Output:**
```json
{
  "products": [
    {
      "title": "A Light in the Attic",
      "price": "£51.77",
      "image_url": "media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"
    },
    {
      "title": "Tipping the Velvet", 
      "price": "£53.74",
      "image_url": "media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg"
    }
  ]
}
```

## Step 5: Handling Advanced Scenarios

### 5.1 Adding Pagination

Many sites have multiple pages of results.

1. Click **"Pagination Mode"**
2. Hover over the "Next" button
3. Click to select
4. Choose pagination type: `"Next/Previous"`

### 5.2 Following Detail Links

To extract more information from product detail pages:

1. Select a product link using **"Link Mode"**
2. Name it: `"detail_url"`
3. Choose **"Follow this link"**
4. ScraperV4 will navigate to the detail page
5. Select additional fields (description, reviews, etc.)

### 5.3 Handling Dynamic Content

For JavaScript-heavy sites:

1. Click **"Advanced Settings"**
2. Enable **"Wait for Dynamic Content"**
3. Set wait strategy: `"Network Idle"`
4. Increase timeout if needed: `10000ms`

## Step 6: Saving Your Template

### 6.1 Template Configuration

Before saving, configure your template:

```javascript
{
  "name": "Books to Scrape - Product Listing",
  "description": "Extract book information including titles, prices, and images",
  "url_pattern": "books.toscrape.com/*",
  "category": "E-commerce",
  "tags": ["books", "products", "ecommerce"]
}
```

### 6.2 Validation

ScraperV4 automatically validates your template:

- ✅ **Selector Quality**: Checks selector robustness
- ✅ **Data Consistency**: Verifies extracted data format
- ✅ **Coverage**: Ensures all products are captured
- ✅ **Performance**: Estimates extraction speed

### 6.3 Save and Deploy

1. Click **"Save Template"**
2. Choose deployment options:
   - **Test Mode**: Run once for verification
   - **Scheduled**: Set up automatic runs
   - **API**: Make available via REST API

## Step 7: Running Your Template

### 7.1 Manual Execution

1. Navigate to **"Jobs"** → **"New Job"**
2. Select your saved template
3. Configure execution:
   - Pages to scrape: `5`
   - Export format: `JSON`
   - Stealth mode: `Enabled`
4. Click **"Start Job"**

### 7.2 Monitor Progress

Watch real-time progress:
- Pages scraped: `3 / 5`
- Items extracted: `60 products`
- Success rate: `100%`
- Estimated completion: `2 minutes`

### 7.3 Export Results

Once complete, download your data:
- JSON: Raw structured data
- CSV: Spreadsheet-friendly format
- Excel: Formatted spreadsheet with multiple sheets

## Common Challenges and Solutions

### Challenge 1: Element Not Highlighting

**Problem**: Hovering over elements doesn't show the green highlight.

**Solutions:**
1. Check browser console for JavaScript errors
2. Refresh the interactive session
3. Try different element nearby
4. Check if the site blocks overlays

### Challenge 2: Extracted Data is Empty

**Problem**: Template runs but extracts no data.

**Solutions:**
1. Verify the website loaded completely
2. Check if selectors are too specific
3. Look for dynamic content loading
4. Test individual selectors first

### Challenge 3: Inconsistent Results

**Problem**: Some products missing data or different structure.

**Solutions:**
1. Add fallback selectors for critical fields
2. Use more robust container selection
3. Handle optional fields gracefully
4. Add data validation rules

### Challenge 4: Site Blocking Detection

**Problem**: Website detects automation and blocks access.

**Solutions:**
1. Enable **Stealth Mode** in advanced settings
2. Add random delays between actions
3. Use residential proxy rotation
4. Randomize browser fingerprints

## Next Steps

Now that you've mastered the basics:

1. **Explore Advanced Features**: Try form interactions, infinite scroll, authentication
2. **Optimize Performance**: Learn about selector optimization and batch processing
3. **Scale Operations**: Set up scheduled jobs and monitoring
4. **Custom Extensions**: Build custom field types and extractors

## Related Tutorials

- [Advanced Template Techniques](advanced-templates.md) - Complex scenarios and patterns
- [Handling Anti-Bot Protection](anti-bot-handling.md) - Stealth and evasion techniques
- [API Integration](api-integration.md) - Programmatic template management

## Troubleshooting

### Common Issues

#### Issue: Playwright Interactive Mode Won't Launch
**Symptoms**: Error message "Error starting Playwright interactive mode: {}"

**Quick Fix**: This is typically caused by missing frontend API methods. 

**Solution**: See the [Playwright Troubleshooting Guide](../troubleshooting/playwright-interactive-issues.md) for the complete fix.

#### Issue: Browser Dependencies Missing
**Symptoms**: Backend errors about missing Playwright modules

**Solution**:
```bash
source venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium
```

### Logs and Debugging

Enable debug mode for detailed information:

```python
# In ScraperV4 settings
DEBUG_MODE = True
PLAYWRIGHT_DEBUG = True
```

Check logs in:
- `logs/playwright_interactive.log`
- Browser DevTools Console
- ScraperV4 Debug Panel

### Getting Help

- **Troubleshooting**: Check the [Playwright Troubleshooting Guide](../troubleshooting/playwright-interactive-issues.md)
- **Documentation**: Check the [Reference Guide](../reference/playwright-api.md)
- **API Integration**: See [Frontend API Integration Guide](../how-to/fix-playwright-api-integration.md)
- **Community**: Join our Discord or GitHub Discussions
- **Issues**: Report bugs on GitHub with debug logs

---

**Congratulations!** You've successfully learned how to create templates using Playwright Interactive Mode. This powerful feature eliminates the traditional limitations of browser-based scraping and opens up possibilities for extracting data from any website.

The visual selection approach means you can create robust, accurate templates without writing a single line of selector code - while still having full control over the extraction process.