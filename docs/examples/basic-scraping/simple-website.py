#!/usr/bin/env python3
"""
Simple Website Scraping Example
===============================

This example demonstrates basic website scraping using ScraperV4's Python API.
It scrapes a simple quotes website to extract quote text, authors, and tags.

Prerequisites:
- ScraperV4 server running on localhost:5000
- requests library installed: pip install requests
"""

import requests
import json
import time

# ScraperV4 API configuration
API_BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

def create_simple_template():
    """Create a basic template for scraping quotes"""
    template = {
        "name": "Simple Quotes Scraper",
        "description": "Scrapes quotes from quotes.toscrape.com",
        "config": {
            "fetcher": {
                "type": "standard",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (compatible; ScraperV4/1.0)"
                }
            },
            "selectors": {
                "quote": {
                    "css": ".quote",
                    "multiple": True,
                    "fields": {
                        "text": {
                            "css": ".text",
                            "attribute": "text"
                        },
                        "author": {
                            "css": ".author",
                            "attribute": "text"
                        },
                        "tags": {
                            "css": ".tag",
                            "multiple": True,
                            "attribute": "text"
                        }
                    }
                }
            }
        }
    }
    
    # Create template via API
    response = requests.post(
        f"{API_BASE_URL}/templates",
        headers=HEADERS,
        json=template
    )
    
    if response.status_code == 201:
        template_id = response.json()["id"]
        print(f"✓ Template created with ID: {template_id}")
        return template_id
    else:
        print(f"✗ Failed to create template: {response.text}")
        return None

def start_scraping_job(template_id, url):
    """Start a scraping job using the template"""
    job_data = {
        "template_id": template_id,
        "url": url,
        "options": {
            "wait_time": 2,
            "timeout": 30
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/scrape",
        headers=HEADERS,
        json=job_data
    )
    
    if response.status_code == 202:
        job_id = response.json()["job_id"]
        print(f"✓ Scraping job started with ID: {job_id}")
        return job_id
    else:
        print(f"✗ Failed to start scraping job: {response.text}")
        return None

def monitor_job(job_id):
    """Monitor job progress until completion"""
    print("Monitoring job progress...")
    
    while True:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/status")
        
        if response.status_code == 200:
            status = response.json()
            print(f"Job status: {status['status']} - {status.get('progress', 0)}% complete")
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                return status
                
        time.sleep(2)

def get_results(job_id):
    """Retrieve and display scraping results"""
    response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/results")
    
    if response.status_code == 200:
        results = response.json()
        print("\n" + "="*50)
        print("SCRAPING RESULTS")
        print("="*50)
        
        quotes = results.get("data", {}).get("quote", [])
        
        for i, quote in enumerate(quotes, 1):
            print(f"\nQuote #{i}:")
            print(f"Text: {quote.get('text', 'N/A')}")
            print(f"Author: {quote.get('author', 'N/A')}")
            print(f"Tags: {', '.join(quote.get('tags', []))}")
        
        print(f"\nTotal quotes scraped: {len(quotes)}")
        return results
    else:
        print(f"✗ Failed to get results: {response.text}")
        return None

def export_to_csv(job_id, filename="quotes.csv"):
    """Export results to CSV format"""
    response = requests.get(
        f"{API_BASE_URL}/jobs/{job_id}/export",
        params={"format": "csv"}
    )
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✓ Results exported to {filename}")
    else:
        print(f"✗ Failed to export results: {response.text}")

def main():
    """Main execution function"""
    print("ScraperV4 Simple Website Scraping Example")
    print("="*45)
    
    # Target URL to scrape
    target_url = "http://quotes.toscrape.com/"
    
    try:
        # Step 1: Create template
        template_id = create_simple_template()
        if not template_id:
            return
        
        # Step 2: Start scraping job
        job_id = start_scraping_job(template_id, target_url)
        if not job_id:
            return
        
        # Step 3: Monitor job progress
        final_status = monitor_job(job_id)
        
        # Step 4: Get and display results
        if final_status["status"] == "completed":
            results = get_results(job_id)
            
            # Step 5: Export to CSV
            if results:
                export_to_csv(job_id)
        else:
            print(f"✗ Job failed: {final_status.get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to ScraperV4 API. Make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"✗ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()