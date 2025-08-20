# Getting Started with ScraperV4

Welcome to ScraperV4! This comprehensive tutorial will guide you through your first successful scraping project, from installation to collecting data. By the end of this guide, you'll have ScraperV4 running and will have completed your first web scraping job.

## Learning Objectives

By completing this tutorial, you will:
- Install and configure ScraperV4
- Understand the web interface and core concepts
- Create your first scraping template
- Execute your first scraping job
- Export and analyze your results
- Understand basic troubleshooting

## Prerequisites

- Basic understanding of HTML and CSS selectors
- Python 3.8 or higher installed
- Basic command line knowledge
- Internet connection for installation and scraping

## Step 1: Installation and Setup

### 1.1 Download and Extract

First, obtain the ScraperV4 codebase and navigate to the project directory:

```bash
# Navigate to your project directory
cd /path/to/ScraperV4
```

### 1.2 Create Virtual Environment

Always use a virtual environment to avoid conflicts with other Python projects:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

**Verification**: Your command prompt should now show `(venv)` at the beginning.

### 1.3 Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

**Expected Output**: You should see packages being installed, including:
- scrapling>=0.2.9
- eel>=0.14.0
- pandas>=1.3.0
- aiohttp>=3.8.0
- beautifulsoup4>=4.10.0

### 1.4 Verify Installation

Test that everything is working:

```bash
python -c "import src.main; print('Installation successful!')"
```

**Expected Output**: `Installation successful!`

## Step 2: First Launch

### 2.1 Start the Application

Launch ScraperV4:

```bash
python -m src.main
```

**Expected Output**:
```
Starting ScraperV4...
Web interface available at: http://localhost:8080
Application ready!
```

### 2.2 Access the Web Interface

1. Open your web browser
2. Navigate to `http://localhost:8080`
3. You should see the ScraperV4 dashboard

**What You'll See**:
- Clean, modern interface
- Navigation menu with: Dashboard, Templates, Jobs, Export
- Welcome message and quick start options

### 2.3 Understanding the Interface

Take a moment to explore:

**Dashboard**: Overview of recent jobs and system status
**Templates**: Create and manage scraping templates
**Jobs**: Monitor active and completed scraping jobs
**Export**: Download your scraped data in various formats

## Step 3: Understanding Core Concepts

### 3.1 Templates

Templates define **what** to scrape from web pages. They contain:
- **Selectors**: CSS or XPath expressions that identify data elements
- **Processing Rules**: How to clean and format the extracted data
- **Pagination**: Instructions for handling multiple pages

### 3.2 Jobs

Jobs represent actual scraping operations. They combine:
- A template (what to scrape)
- A target URL (where to scrape)
- Configuration options (how to scrape)

### 3.3 Results

Results are the scraped data stored in various formats:
- JSON for programmatic access
- CSV for spreadsheet applications
- Excel for formatted reports

## Step 4: Your First Template

Let's create a simple template to scrape quotes from a test website.

### 4.1 Navigate to Templates

1. Click on **Templates** in the navigation menu
2. Click **Create New Template**

### 4.2 Template Configuration

Fill in the following information:

**Template Name**: `Quotes Scraper`
**Description**: `Extract quotes, authors, and tags from quotes.toscrape.com`

### 4.3 Define Selectors

In the selectors section, add these CSS selectors:

```json
{
  "quote": ".quote .text::text",
  "author": ".quote .author::text",
  "tags": ".quote .tags a::text"
}
```

**Understanding the Selectors**:
- `.quote`: Targets elements with class "quote"
- `.text::text`: Gets the text content of elements with class "text"
- `.author::text`: Gets the text content of author elements
- `.tags a::text`: Gets text from all anchor tags within tags elements

### 4.4 Configure Post-Processing

Add these processing rules:

```json
{
  "clean_text": true,
  "remove_quotes": ["quote"],
  "join_arrays": ["tags"]
}
```

### 4.5 Save the Template

Click **Save Template**. You should see a success message.

## Step 5: Test Your Template

Before running a full scraping job, let's test the template.

### 5.1 Template Testing

1. In the template editor, find the **Test Template** section
2. Enter the test URL: `http://quotes.toscrape.com/`
3. Click **Test Selectors**

**Expected Results**:
```json
{
  "quote": "The world as we have created it is a process of our thinking...",
  "author": "Albert Einstein",
  "tags": ["change", "deep-thoughts", "thinking", "world"]
}
```

### 5.2 Verify Results

Check that:
- Quote text appears without quotation marks
- Author name is correctly extracted
- Tags are properly formatted as an array

If selectors don't work, review the target website's HTML structure and adjust accordingly.

## Step 6: Your First Scraping Job

Now let's create and run a complete scraping job.

### 6.1 Create a New Job

1. Navigate to the **Jobs** section
2. Click **Create New Job**

### 6.2 Job Configuration

Fill in the details:

**Job Name**: `My First Quotes Scrape`
**Template**: Select "Quotes Scraper" from the dropdown
**Target URL**: `http://quotes.toscrape.com/`

### 6.3 Advanced Options

Expand the **Advanced Options** section:

**Basic Settings**:
- Delay between requests: `2` seconds
- Max pages to scrape: `3`
- Enable stealth mode: `Yes`

**Proxy Settings** (optional):
- Use proxy rotation: `No` (for this first test)

### 6.4 Start the Job

Click **Start Scraping Job**

## Step 7: Monitor Progress

### 7.1 Real-time Monitoring

Watch the job progress:
- Job status will change from "Queued" to "Running"
- Progress bar shows completion percentage
- Items scraped counter increases in real-time

**Expected Timeline**: The job should complete in 30-60 seconds.

### 7.2 View Live Updates

The interface updates automatically showing:
- Current page being scraped
- Number of items collected
- Any errors encountered

**Success Indicators**:
- Status: "Completed"
- Items scraped: ~30-60 quotes
- No errors in the log

## Step 8: Export and Analyze Results

### 8.1 Access Results

1. Navigate to the **Export** section
2. Find your completed job in the results list
3. Click **View Data** to preview results

### 8.2 Preview Your Data

You should see a table with columns:
- Quote
- Author  
- Tags

**Sample Data**:
```
Quote: "The world as we have created it is a process..."
Author: "Albert Einstein"
Tags: "change, deep-thoughts, thinking, world"
```

### 8.3 Export Options

Try different export formats:

**JSON Export**:
1. Click **Export as JSON**
2. File downloads to your browser's download folder
3. Open the file to see structured data

**CSV Export**:
1. Click **Export as CSV**
2. Open in Excel or Google Sheets
3. Data appears in spreadsheet format

**Excel Export**:
1. Click **Export as Excel**
2. Open the .xlsx file
3. Notice formatting and metadata sheets

## Step 9: Understanding Your Results

### 9.1 Data Structure

Open the JSON export to understand the structure:

```json
{
  "job_metadata": {
    "job_id": "quotes-scraper-001",
    "timestamp": "2024-01-15T10:30:00Z",
    "pages_scraped": 3,
    "total_items": 30
  },
  "data": [
    {
      "quote": "The world as we have created it...",
      "author": "Albert Einstein",
      "tags": ["change", "deep-thoughts", "thinking", "world"]
    }
  ]
}
```

### 9.2 Quality Assessment

Check your data quality:
- Are quotes complete and readable?
- Are author names correctly extracted?
- Are tags properly separated?
- Are there any duplicate entries?

## Step 10: Practice Exercise

To reinforce your learning, try this exercise:

### Exercise: Book Catalog Scraper

Create a new template to scrape book information from `http://books.toscrape.com/`:

**Required Fields**:
- Book title
- Price
- Star rating
- Availability

**Hints**:
- Use browser developer tools to inspect the HTML
- Look for CSS classes like `.product_pod`
- Price is in elements with class `.price_color`
- Rating is in the `star-rating` class

**Expected Selectors**:
```json
{
  "title": ".product_pod h3 a::attr(title)",
  "price": ".product_pod .price_color::text",
  "rating": ".product_pod .star-rating::attr(class)",
  "availability": ".product_pod .instock::text"
}
```

## Common First-Time Issues

### Issue 1: Template Test Fails

**Symptoms**: No data returned when testing template
**Solution**: 
1. Check the target website in your browser
2. Use browser developer tools to verify selectors
3. Ensure the website is accessible

### Issue 2: Job Stays in "Queued" Status

**Symptoms**: Job doesn't start running
**Solution**:
1. Check that no other jobs are running
2. Restart the application
3. Check system resources (memory/CPU)

### Issue 3: No Data Exported

**Symptoms**: Export files are empty
**Solution**:
1. Verify the job completed successfully
2. Check job logs for errors
3. Test template selectors again

### Issue 4: Application Won't Start

**Symptoms**: Error when running `python -m src.main`
**Solution**:
1. Verify virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (must be 3.8+)

## Next Steps

Congratulations! You've successfully:
- Installed and configured ScraperV4
- Created your first template
- Executed a scraping job
- Exported results in multiple formats

### Recommended Next Tutorials

1. **First Template Tutorial**: Learn advanced template features
2. **Advanced Scraping Tutorial**: Explore stealth mode and proxy rotation
3. **API Integration Tutorial**: Use ScraperV4 programmatically
4. **Troubleshooting Guide**: Handle complex scraping challenges

### Additional Resources

- **Template Examples**: Check `/templates/examples/` for more template samples
- **API Documentation**: See `/docs/api/` for programmatic usage
- **Community Forum**: Join discussions and get help

## Summary

You've learned the complete ScraperV4 workflow:

1. **Setup**: Virtual environment and dependency installation
2. **Interface**: Web-based control panel navigation
3. **Templates**: Defining what data to extract
4. **Jobs**: Executing scraping operations
5. **Results**: Exporting and analyzing data

You're now ready to tackle more complex scraping projects with ScraperV4's advanced features!