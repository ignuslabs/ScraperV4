# ScraperV4 Examples
==================

This directory contains comprehensive code examples and templates demonstrating ScraperV4's capabilities across different use cases and deployment scenarios.

## 📁 Directory Structure

### 🔰 **basic-scraping/**
Simple, beginner-friendly examples to get started quickly:
- `simple-website.py` - Basic website scraping with API
- `with-pagination.py` - Handling pagination automatically
- `multiple-pages.py` - Scraping multiple pages efficiently
- `css-selectors.py` - Advanced CSS selector techniques
- `xpath-examples.py` - XPath selector examples and patterns

### 🚀 **advanced-templates/**
Production-ready JSON templates for complex scraping scenarios:
- `ecommerce-template.json` - Complete e-commerce product scraper
- `news-template.json` - News article extraction with metadata
- `directory-template.json` - Business directory scraping
- `dynamic-content.json` - JavaScript-heavy sites
- `multi-page-template.json` - Complex multi-page workflows

### 🔌 **api-clients/**
Client libraries and integration examples:
- `python-client.py` - Complete Python client with async support
- `javascript-client.js` - Node.js/browser JavaScript client
- `automation-script.py` - Automated scraping workflows
- `webhook-integration.py` - Webhook and callback implementations
- `batch-processing.py` - High-volume processing examples

### 🐳 **deployment-configs/**
Production deployment configurations:
- `docker-compose.yml` - Complete Docker production setup
- `systemd-service.conf` - Linux systemd service configuration
- `nginx-proxy.conf` - Reverse proxy with SSL termination
- `kubernetes-deployment.yaml` - Kubernetes manifests
- `aws-cloudformation.yaml` - AWS infrastructure template

## 🚀 Quick Start

### 1. Basic Usage
```bash
# Run the simple website example
cd basic-scraping/
python simple-website.py
```

### 2. Using Templates
```bash
# Test an advanced template
curl -X POST http://localhost:5000/api/templates/test \
  -H "Content-Type: application/json" \
  -d @advanced-templates/ecommerce-template.json
```

### 3. Production Deployment
```bash
# Deploy with Docker Compose
cd deployment-configs/
cp .env.example .env  # Configure your environment
docker-compose up -d
```

## 📚 Example Categories

### **Learning Path**
1. **Beginners** → Start with `basic-scraping/simple-website.py`
2. **Intermediate** → Try `advanced-templates/ecommerce-template.json`
3. **Advanced** → Implement `api-clients/python-client.py`
4. **Production** → Deploy with `deployment-configs/docker-compose.yml`

### **By Use Case**
- **E-commerce** → `ecommerce-template.json`, pagination examples
- **News/Media** → `news-template.json`, content extraction
- **Data Mining** → Batch processing, high-volume examples
- **Integration** → API clients, webhook examples
- **DevOps** → Deployment configs, monitoring setup

### **By Technology**
- **Python** → All Python client examples and scripts
- **JavaScript** → Node.js clients and browser integration
- **Docker** → Containerized deployment examples
- **Kubernetes** → Cloud-native deployment manifests
- **Monitoring** → Prometheus, Grafana, ELK stack

## 🔧 Prerequisites

### **Software Requirements**
- ScraperV4 server running (see main documentation)
- Python 3.8+ with required packages
- Docker and Docker Compose (for deployment examples)
- Node.js 14+ (for JavaScript examples)

### **Python Dependencies**
```bash
pip install requests aiohttp pandas openpyxl
```

### **JavaScript Dependencies**
```bash
npm install axios puppeteer cheerio
```

## 📖 Running Examples

### **Basic Examples**
```bash
# Simple scraping
python basic-scraping/simple-website.py

# Pagination handling
python basic-scraping/with-pagination.py

# CSS selectors
python basic-scraping/css-selectors.py
```

### **Template Testing**
```bash
# Test e-commerce template
python -c "
import json
import requests

with open('advanced-templates/ecommerce-template.json') as f:
    template = json.load(f)

response = requests.post(
    'http://localhost:5000/api/templates/test',
    json={'template': template, 'url': 'https://example-shop.com'}
)
print(response.json())
"
```

### **Client Libraries**
```bash
# Python client example
cd api-clients/
python python-client.py

# JavaScript client example
node javascript-client.js
```

### **Production Deployment**
```bash
# Docker Compose deployment
cd deployment-configs/
cp docker-compose.yml /your/production/path/
# Edit environment variables
docker-compose up -d

# Kubernetes deployment
kubectl apply -f kubernetes-deployment.yaml
```

## 🎯 Example Use Cases

### **1. E-commerce Price Monitoring**
```python
# Using the advanced e-commerce template
from api_clients.python_client import ScraperV4Client

client = ScraperV4Client()
template_id = client.create_template_from_file('advanced-templates/ecommerce-template.json')

# Monitor multiple product pages
urls = [
    'https://shop.example.com/product1',
    'https://shop.example.com/product2'
]

job_ids = []
for url in urls:
    job_id = client.start_job(template_id, url)
    job_ids.append(job_id)

# Collect all results
results = client.monitor_batch_jobs(job_ids)
```

### **2. News Aggregation**
```python
# Scrape multiple news sources
news_template = 'advanced-templates/news-template.json'
news_sources = [
    'https://news.example.com',
    'https://another-news.com'
]

# Process in parallel
import asyncio
async_client = AsyncScraperV4Client()

async def scrape_news():
    tasks = []
    for source in news_sources:
        task = async_client.start_job_async(template_id, source)
        tasks.append(task)
    
    job_ids = await asyncio.gather(*tasks)
    return job_ids

job_ids = asyncio.run(scrape_news())
```

### **3. Business Directory Extraction**
```bash
# Using the directory template with pagination
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "template_file": "advanced-templates/directory-template.json",
    "url": "https://business-directory.com/category/restaurants",
    "options": {
      "max_pages": 100,
      "export_format": "csv"
    }
  }'
```

## 🔍 Template Customization

### **Modifying Templates**
All JSON templates can be customized by editing:
- **Selectors** → CSS/XPath selectors for data extraction
- **Fetcher Options** → Stealth mode, proxy settings, headers
- **Post-processing** → Data cleaning and transformation rules
- **Pagination** → Page navigation and stopping conditions
- **Export Options** → Output formats and custom fields

### **Template Testing**
Before using templates in production:
1. Test with the `/api/templates/test` endpoint
2. Validate selectors on target websites
3. Check data quality and completeness
4. Adjust stealth settings if needed

## 🚨 Best Practices

### **Development**
- Start with simple examples and gradually increase complexity
- Test templates thoroughly before production use
- Use proper error handling in client code
- Implement rate limiting and respectful scraping practices

### **Production**
- Use Docker Compose for scalable deployments
- Implement monitoring with Prometheus/Grafana
- Set up log aggregation with ELK stack
- Configure proper backup strategies for data
- Use environment variables for sensitive configuration

### **Performance**
- Batch multiple jobs for efficiency
- Use async clients for high-throughput scenarios
- Configure appropriate proxy rotation
- Monitor resource usage and scale accordingly

## 🤝 Contributing Examples

To contribute new examples:
1. Follow the existing directory structure
2. Include comprehensive documentation and comments
3. Test examples thoroughly
4. Add usage instructions in this README
5. Submit a pull request with your improvements

## 📞 Support

For questions about these examples:
- Check the main ScraperV4 documentation
- Review the troubleshooting guides
- Open an issue on the project repository
- Join the community discussion forums

---

**Note**: All examples assume ScraperV4 is running on `localhost:5000`. Adjust URLs and configurations for your specific deployment.