# How to Export Data in Different Formats

This guide covers exporting scraped data from ScraperV4 in various formats with customization options for different use cases.

## Prerequisites

- ScraperV4 installed and configured
- Completed scraping jobs with data to export
- Understanding of data formats (JSON, CSV, Excel)
- Optional: Excel viewer for XLSX files

## Overview

ScraperV4 supports multiple export formats with extensive customization:
- **JSON**: Structured data with metadata and nested objects
- **CSV**: Tabular format for spreadsheet applications
- **Excel (XLSX)**: Advanced formatting with multiple sheets and styling
- **Custom Formats**: Extensible export system for specialized needs

## Available Export Formats

### Supported Formats

1. **JSON** (.json): Hierarchical data with full metadata
2. **CSV** (.csv): Flat tabular data for analysis
3. **Excel** (.xlsx): Rich formatting with charts and formulas
4. **Text** (.txt): Simple text format for basic data

## Basic Export Operations

### 1. Using the API

```bash
# Export specific result in JSON format
curl -X POST http://localhost:8080/api/data/export \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": "job-12345",
    "format": "json",
    "options": {
      "include_metadata": true,
      "pretty_print": true
    }
  }'

# Export result in CSV format
curl -X POST http://localhost:8080/api/data/export \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": "job-12345",
    "format": "csv",
    "options": {
      "include_headers": true,
      "flatten_nested": true,
      "delimiter": ","
    }
  }'

# Export result in Excel format
curl -X POST http://localhost:8080/api/data/export \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": "job-12345",
    "format": "xlsx",
    "options": {
      "include_metadata": true,
      "separate_sheets": true,
      "apply_formatting": true
    }
  }'
```

### 2. Using Python API

```python
from src.services.data_service import DataService

# Initialize data service
data_service = DataService()

# Export as JSON
json_export = data_service.export_result_data(
    result_id="job-12345",
    format="json"
)

print(f"JSON export: {json_export}")

# Export as CSV with options
csv_export = data_service.export_result_data(
    result_id="job-12345", 
    format="csv"
)

print(f"CSV export: {csv_export}")

# Export as Excel with formatting
excel_export = data_service.export_result_data(
    result_id="job-12345",
    format="xlsx"
)

print(f"Excel export: {excel_export}")
```

## JSON Export Customization

### 1. Basic JSON Export

```python
# Standard JSON export
result = data_service.export_result_data(
    result_id="job-12345",
    format="json"
)

# Example output structure:
{
    "file_path": "/data/exports/result_job-12345_20241217_143022.json",
    "format": "json",
    "exported_at": "2024-12-17T14:30:22.123456",
    "success": True
}
```

### 2. Custom JSON Processing

```python
def export_json_with_processing(result_id, processing_rules=None):
    """Export JSON with custom processing rules."""
    
    # Get raw result data
    result = data_service.get_result(result_id)
    if not result:
        return {"error": "Result not found"}
    
    # Apply processing rules
    if processing_rules:
        processed_result = data_service.process_scraped_data(
            data=result.get('data', {}),
            processing_rules=processing_rules
        )
        result['data'] = processed_result['data']
    
    # Custom JSON formatting
    import json
    from pathlib import Path
    from datetime import datetime
    
    export_dir = Path("data/exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"processed_{result_id}_{timestamp}.json"
    file_path = export_dir / filename
    
    # Write with custom formatting
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    return {
        "file_path": str(file_path),
        "format": "json",
        "processing_applied": bool(processing_rules),
        "success": True
    }

# Example usage
processing_rules = {
    "text_cleaning": {
        "strip_whitespace": True,
        "remove_extra_spaces": True
    },
    "data_extraction": {
        "extract_numbers": ["price", "rating"],
        "extract_emails": ["contact"]
    }
}

result = export_json_with_processing("job-12345", processing_rules)
```

## CSV Export Options

### 1. Basic CSV Export

```python
# Export job results as CSV
from pathlib import Path

def export_job_to_csv(job_id, options=None):
    """Export complete job results to CSV."""
    
    options = options or {}
    
    # Get all results for the job
    results = data_service.get_job_results(job_id)
    
    if not results:
        return {"error": "No results found for job"}
    
    # Prepare CSV data
    csv_data = []
    headers = set()
    
    for result in results:
        if hasattr(result, 'data') and result.data:
            # Flatten nested data if requested
            if options.get('flatten_nested', True):
                flattened = flatten_dict(result.data)
                csv_data.append(flattened)
                headers.update(flattened.keys())
            else:
                csv_data.append(result.data)
                headers.update(result.data.keys())
    
    # Export to CSV
    export_path = data_service.export_job_results(job_id, format='csv')
    
    return {
        "file_path": str(export_path),
        "format": "csv",
        "rows_exported": len(csv_data),
        "columns": len(headers),
        "success": True
    }

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary for CSV export."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to comma-separated strings
            items.append((new_key, ', '.join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)

# Example usage
csv_result = export_job_to_csv("job-12345", {
    'flatten_nested': True,
    'include_metadata': True
})
```

### 2. Advanced CSV Customization

```python
def export_csv_with_filters(job_id, filters=None, columns=None):
    """Export CSV with data filtering and column selection."""
    import csv
    from datetime import datetime
    
    # Get results
    results = data_service.get_job_results(job_id)
    
    # Apply filters
    if filters:
        filtered_results = []
        for result in results:
            data = result.data
            include = True
            
            # Apply each filter
            for field, condition in filters.items():
                if field in data:
                    if 'min_value' in condition and float(data[field]) < condition['min_value']:
                        include = False
                    if 'max_value' in condition and float(data[field]) > condition['max_value']:
                        include = False
                    if 'contains' in condition and condition['contains'] not in str(data[field]):
                        include = False
            
            if include:
                filtered_results.append(result)
        
        results = filtered_results
    
    # Prepare export
    export_dir = Path("data/exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"filtered_{job_id}_{timestamp}.csv"
    file_path = export_dir / filename
    
    # Determine columns
    if not columns and results:
        columns = list(results[0].data.keys())
    
    # Write CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        for result in results:
            # Extract only specified columns
            row = {col: result.data.get(col, '') for col in columns}
            writer.writerow(row)
    
    return {
        "file_path": str(file_path),
        "format": "csv",
        "rows_exported": len(results),
        "columns_exported": len(columns),
        "filters_applied": bool(filters),
        "success": True
    }

# Example usage
filters = {
    'price': {'min_value': 10, 'max_value': 100},
    'title': {'contains': 'Product'}
}

columns = ['title', 'price', 'description', 'url']

result = export_csv_with_filters("job-12345", filters, columns)
```

## Excel Export with Advanced Formatting

### 1. Basic Excel Export

```python
def export_to_excel_basic(job_id):
    """Export to Excel with basic formatting."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from datetime import datetime
    
    # Get results
    results = data_service.get_job_results(job_id)
    
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Job {job_id} Results"
    
    if results:
        # Headers
        headers = list(results[0].data.keys())
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Data rows
        for row, result in enumerate(results, 2):
            for col, header in enumerate(headers, 1):
                value = result.data.get(header, '')
                ws.cell(row=row, column=col, value=value)
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width
    
    # Save file
    export_dir = Path("data/exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"excel_{job_id}_{timestamp}.xlsx"
    file_path = export_dir / filename
    
    wb.save(file_path)
    
    return {
        "file_path": str(file_path),
        "format": "xlsx",
        "sheets": 1,
        "rows_exported": len(results),
        "success": True
    }

# Example usage
excel_result = export_to_excel_basic("job-12345")
```

### 2. Advanced Excel with Multiple Sheets

```python
def export_to_excel_advanced(job_id, sheet_config=None):
    """Export to Excel with multiple sheets and advanced formatting."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import BarChart, Reference
    from datetime import datetime
    
    # Default sheet configuration
    sheet_config = sheet_config or {
        'data_sheet': True,
        'summary_sheet': True,
        'charts': True,
        'metadata_sheet': True
    }
    
    # Get results and metadata
    results = data_service.get_job_results(job_id)
    job_stats = data_service.get_job_results_count(job_id)
    
    # Create workbook
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet
    
    # Data sheet
    if sheet_config.get('data_sheet', True):
        ws_data = wb.create_sheet("Data")
        
        if results:
            headers = list(results[0].data.keys())
            
            # Style headers
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            for col, header in enumerate(headers, 1):
                cell = ws_data.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            
            # Add data with alternating row colors
            for row, result in enumerate(results, 2):
                for col, header in enumerate(headers, 1):
                    value = result.data.get(header, '')
                    cell = ws_data.cell(row=row, column=col, value=value)
                    
                    # Alternating row colors
                    if row % 2 == 0:
                        cell.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    
    # Summary sheet
    if sheet_config.get('summary_sheet', True):
        ws_summary = wb.create_sheet("Summary")
        
        summary_data = [
            ["Job ID", job_id],
            ["Total Records", len(results)],
            ["Export Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
            ["", ""],
            ["Field Statistics", ""],
        ]
        
        # Add field statistics
        if results:
            field_stats = {}
            for result in results:
                for field, value in result.data.items():
                    if field not in field_stats:
                        field_stats[field] = {'count': 0, 'non_empty': 0}
                    field_stats[field]['count'] += 1
                    if value and str(value).strip():
                        field_stats[field]['non_empty'] += 1
            
            for field, stats in field_stats.items():
                completion_rate = (stats['non_empty'] / stats['count']) * 100
                summary_data.append([field, f"{completion_rate:.1f}% complete"])
        
        # Write summary data
        for row, (label, value) in enumerate(summary_data, 1):
            ws_summary.cell(row=row, column=1, value=label).font = Font(bold=True)
            ws_summary.cell(row=row, column=2, value=value)
    
    # Metadata sheet
    if sheet_config.get('metadata_sheet', True):
        ws_meta = wb.create_sheet("Metadata")
        
        # Get job metadata if available
        job_result = data_service.get_result(job_id)
        if job_result:
            metadata = job_result.get('metadata', {})
            
            meta_rows = [
                ["Job Information", ""],
                ["Job ID", job_id],
                ["Source URL", metadata.get('source_url', 'N/A')],
                ["Scraped At", metadata.get('scraped_at', 'N/A')],
                ["Template Used", metadata.get('template_id', 'N/A')],
                ["", ""],
                ["Export Information", ""],
                ["Export Date", datetime.utcnow().isoformat()],
                ["Export Format", "Excel (XLSX)"],
                ["Records Exported", len(results)]
            ]
            
            for row, (label, value) in enumerate(meta_rows, 1):
                ws_meta.cell(row=row, column=1, value=label).font = Font(bold=True)
                ws_meta.cell(row=row, column=2, value=value)
    
    # Save file
    export_dir = Path("data/exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"advanced_{job_id}_{timestamp}.xlsx"
    file_path = export_dir / filename
    
    wb.save(file_path)
    
    return {
        "file_path": str(file_path),
        "format": "xlsx",
        "sheets": len(wb.sheetnames),
        "sheet_names": wb.sheetnames,
        "rows_exported": len(results),
        "features": list(sheet_config.keys()),
        "success": True
    }

# Example usage
advanced_result = export_to_excel_advanced("job-12345", {
    'data_sheet': True,
    'summary_sheet': True,
    'charts': False,
    'metadata_sheet': True
})
```

## Batch Export Operations

### 1. Export Multiple Jobs

```python
def batch_export_jobs(job_ids, format='csv', output_dir=None):
    """Export multiple jobs in batch."""
    from pathlib import Path
    import shutil
    from datetime import datetime
    
    output_dir = Path(output_dir or "data/exports/batch")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for job_id in job_ids:
        try:
            if format == 'csv':
                export_path = data_service.export_job_results(job_id, format='csv')
            else:
                export_result = data_service.export_result_data(job_id, format=format)
                export_path = export_result.get('file_path')
            
            if export_path:
                # Move to batch directory
                dest_path = output_dir / Path(export_path).name
                shutil.copy2(export_path, dest_path)
                
                results.append({
                    'job_id': job_id,
                    'status': 'success',
                    'file_path': str(dest_path)
                })
            else:
                results.append({
                    'job_id': job_id,
                    'status': 'failed',
                    'error': 'Export failed'
                })
                
        except Exception as e:
            results.append({
                'job_id': job_id,
                'status': 'failed', 
                'error': str(e)
            })
    
    # Create batch summary
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    summary_file = output_dir / f"batch_summary_{timestamp}.json"
    
    import json
    with open(summary_file, 'w') as f:
        json.dump({
            'batch_export': {
                'timestamp': timestamp,
                'format': format,
                'total_jobs': len(job_ids),
                'successful_exports': len([r for r in results if r['status'] == 'success']),
                'failed_exports': len([r for r in results if r['status'] == 'failed']),
                'results': results
            }
        }, f, indent=2)
    
    return {
        'batch_directory': str(output_dir),
        'summary_file': str(summary_file),
        'total_jobs': len(job_ids),
        'successful': len([r for r in results if r['status'] == 'success']),
        'failed': len([r for r in results if r['status'] == 'failed']),
        'results': results
    }

# Example usage
job_ids = ["job-12345", "job-12346", "job-12347"]
batch_result = batch_export_jobs(job_ids, format='xlsx')
```

### 2. Scheduled Export

```python
def setup_scheduled_export(job_ids, schedule_config):
    """Setup scheduled exports for ongoing jobs."""
    import schedule
    import time
    from threading import Thread
    
    def export_job_routine():
        for job_id in job_ids:
            try:
                # Check if job has new data
                current_count = data_service.get_job_results_count(job_id)
                
                # Export if configured format
                if schedule_config.get('format') == 'excel':
                    export_to_excel_advanced(job_id)
                else:
                    data_service.export_job_results(job_id, format=schedule_config.get('format', 'csv'))
                
                print(f"Scheduled export completed for job {job_id}")
                
            except Exception as e:
                print(f"Scheduled export failed for job {job_id}: {e}")
    
    # Schedule based on configuration
    interval = schedule_config.get('interval', 'daily')
    time_spec = schedule_config.get('time', '02:00')
    
    if interval == 'hourly':
        schedule.every().hour.do(export_job_routine)
    elif interval == 'daily':
        schedule.every().day.at(time_spec).do(export_job_routine)
    elif interval == 'weekly':
        day = schedule_config.get('day', 'monday')
        getattr(schedule.every(), day).at(time_spec).do(export_job_routine)
    
    # Run scheduler in background thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    return {
        'scheduled': True,
        'interval': interval,
        'time': time_spec,
        'job_count': len(job_ids)
    }

# Example usage
schedule_config = {
    'interval': 'daily',
    'time': '03:00',
    'format': 'excel'
}

scheduled_result = setup_scheduled_export(["job-12345"], schedule_config)
```

## Custom Export Formats

### 1. Create Custom Exporter

```python
class CustomExporter:
    """Base class for custom export formats."""
    
    def __init__(self, format_name, file_extension):
        self.format_name = format_name
        self.file_extension = file_extension
    
    def export(self, data, file_path, options=None):
        """Override this method to implement custom export logic."""
        raise NotImplementedError
    
    def validate_data(self, data):
        """Validate data before export."""
        return isinstance(data, (dict, list))

class XMLExporter(CustomExporter):
    """Export data to XML format."""
    
    def __init__(self):
        super().__init__("xml", ".xml")
    
    def export(self, data, file_path, options=None):
        import xml.etree.ElementTree as ET
        
        root = ET.Element("scraped_data")
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                item_elem = ET.SubElement(root, f"item_{i}")
                self._dict_to_xml(item, item_elem)
        else:
            self._dict_to_xml(data, root)
        
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        
        return str(file_path)
    
    def _dict_to_xml(self, data, parent):
        for key, value in data.items():
            # Clean key name for XML
            clean_key = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(key))
            elem = ET.SubElement(parent, clean_key)
            
            if isinstance(value, dict):
                self._dict_to_xml(value, elem)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_elem = ET.SubElement(elem, f"item_{i}")
                    if isinstance(item, dict):
                        self._dict_to_xml(item, item_elem)
                    else:
                        item_elem.text = str(item)
            else:
                elem.text = str(value)

# Register custom exporter
def export_custom_format(job_id, format_name, options=None):
    """Export using custom format."""
    
    exporters = {
        'xml': XMLExporter()
    }
    
    if format_name not in exporters:
        return {'error': f'Unknown format: {format_name}'}
    
    exporter = exporters[format_name]
    
    # Get data
    results = data_service.get_job_results(job_id)
    data = [result.data for result in results]
    
    # Export
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"custom_{job_id}_{timestamp}{exporter.file_extension}"
    file_path = Path("data/exports") / filename
    
    try:
        exported_path = exporter.export(data, file_path, options)
        return {
            'file_path': exported_path,
            'format': format_name,
            'success': True
        }
    except Exception as e:
        return {
            'error': str(e),
            'format': format_name,
            'success': False
        }

# Example usage
xml_result = export_custom_format("job-12345", "xml")
```

## Export Performance Optimization

### 1. Memory-Efficient Large Dataset Export

```python
def export_large_dataset(job_id, format='csv', chunk_size=1000):
    """Export large datasets in chunks to manage memory."""
    
    total_count = data_service.get_job_results_count(job_id)
    
    if total_count <= chunk_size:
        # Small dataset, export normally
        return data_service.export_job_results(job_id, format=format)
    
    # Large dataset, export in chunks
    from datetime import datetime
    import csv
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"large_{job_id}_{timestamp}.{format}"
    file_path = Path("data/exports") / filename
    
    if format == 'csv':
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = None
            headers_written = False
            
            for offset in range(0, total_count, chunk_size):
                # Get chunk of results
                chunk_results = data_service.get_job_results(
                    job_id, 
                    limit=chunk_size, 
                    offset=offset
                )
                
                for result in chunk_results:
                    if not headers_written and result.data:
                        # Write headers on first chunk
                        writer = csv.DictWriter(csvfile, fieldnames=result.data.keys())
                        writer.writeheader()
                        headers_written = True
                    
                    if writer and result.data:
                        writer.writerow(result.data)
                
                # Progress indicator
                progress = min((offset + chunk_size) / total_count * 100, 100)
                print(f"Export progress: {progress:.1f}%")
    
    return {
        'file_path': str(file_path),
        'format': format,
        'total_records': total_count,
        'chunk_size': chunk_size,
        'success': True
    }

# Example usage
large_export = export_large_dataset("job-12345", format='csv', chunk_size=500)
```

### 2. Parallel Export Processing

```python
def parallel_export_multiple_formats(job_id, formats=['json', 'csv', 'xlsx']):
    """Export in multiple formats simultaneously."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time
    
    def export_format(format_name):
        start_time = time.time()
        try:
            if format_name == 'xlsx':
                result = export_to_excel_advanced(job_id)
            else:
                result = data_service.export_result_data(job_id, format=format_name)
            
            result['export_time'] = time.time() - start_time
            result['format'] = format_name
            return result
        except Exception as e:
            return {
                'format': format_name,
                'error': str(e),
                'export_time': time.time() - start_time,
                'success': False
            }
    
    # Export in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=len(formats)) as executor:
        future_to_format = {executor.submit(export_format, fmt): fmt for fmt in formats}
        
        for future in as_completed(future_to_format):
            format_name = future_to_format[future]
            try:
                result = future.result()
                results[format_name] = result
            except Exception as e:
                results[format_name] = {'error': str(e), 'success': False}
    
    return {
        'job_id': job_id,
        'formats_exported': len([r for r in results.values() if r.get('success')]),
        'total_formats': len(formats),
        'results': results,
        'parallel_export': True
    }

# Example usage
parallel_result = parallel_export_multiple_formats("job-12345")
```

## Troubleshooting Export Issues

### 1. Diagnose Export Problems

```python
def diagnose_export_issues(job_id, format='csv'):
    """Diagnose common export issues."""
    
    diagnosis = {
        'job_id': job_id,
        'format': format,
        'issues_found': [],
        'recommendations': []
    }
    
    # Check if job exists
    results = data_service.get_job_results(job_id, limit=1)
    if not results:
        diagnosis['issues_found'].append('No results found for job')
        diagnosis['recommendations'].append('Verify job ID and ensure scraping completed')
        return diagnosis
    
    # Check data structure
    sample_data = results[0].data if results else None
    if not sample_data:
        diagnosis['issues_found'].append('Empty data in results')
        diagnosis['recommendations'].append('Check scraping template and selectors')
        return diagnosis
    
    # Check data types
    problematic_fields = []
    for field, value in sample_data.items():
        if isinstance(value, (dict, list)) and format == 'csv':
            problematic_fields.append(field)
    
    if problematic_fields:
        diagnosis['issues_found'].append(f'Nested data in CSV export: {problematic_fields}')
        diagnosis['recommendations'].append('Use flatten_nested option or export as JSON/Excel')
    
    # Check memory requirements
    total_count = data_service.get_job_results_count(job_id)
    if total_count > 10000:
        diagnosis['issues_found'].append(f'Large dataset ({total_count} records)')
        diagnosis['recommendations'].append('Use chunked export for large datasets')
    
    # Check disk space
    import shutil
    free_space = shutil.disk_usage("data/exports").free
    if free_space < 100 * 1024 * 1024:  # Less than 100MB
        diagnosis['issues_found'].append('Low disk space')
        diagnosis['recommendations'].append('Free up disk space before exporting')
    
    return diagnosis

# Example usage
diagnosis = diagnose_export_issues("job-12345", "csv")
print(f"Issues: {diagnosis['issues_found']}")
print(f"Recommendations: {diagnosis['recommendations']}")
```

## Expected Outcomes

After implementing data export capabilities:

1. **Multiple Format Support**: Export data in JSON, CSV, Excel, and custom formats
2. **Customization Options**: Flexible formatting and processing options
3. **Batch Operations**: Efficient export of multiple jobs
4. **Performance Optimization**: Memory-efficient handling of large datasets
5. **Error Handling**: Robust error detection and recovery
6. **Integration Ready**: API endpoints for automated export workflows

## Success Criteria

- [ ] All major export formats working (JSON, CSV, Excel)
- [ ] Custom formatting and processing options functional
- [ ] Batch export capabilities implemented
- [ ] Large dataset handling optimized
- [ ] API integration completed
- [ ] Error handling and diagnostics working
- [ ] Documentation and examples provided