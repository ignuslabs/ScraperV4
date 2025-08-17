"""Data processing service."""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import json
import csv
import re
from .base_service import BaseService

class ResultData:
    """Wrapper class to provide attribute access to result data."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def __getattr__(self, name):
        """Provide attribute-style access to dictionary keys."""
        return self._data.get(name)
    
    @property
    def id(self):
        return self._data.get('id', '')
    
    @property
    def source_url(self):
        return self._data.get('source_url', self._data.get('job_id', ''))
    
    @property
    def data(self):
        return self._data.get('data', {})
    
    @property
    def scraped_at(self):
        timestamp = self._data.get('scraped_at', self._data.get('created_at'))
        if timestamp:
            return datetime.fromisoformat(timestamp)
        return datetime.utcnow()
    
    @property
    def status(self):
        return self._data.get('status', 'completed')

class DataService(BaseService):
    """Service for data processing and management."""
    
    def __init__(self):
        super().__init__()
        self._allowed_export_formats = {'csv', 'json', 'xlsx', 'txt'}
    
    def _sanitize_filename_component(self, value: str, max_length: int = 50) -> str:
        """Sanitize filename component to prevent path traversal attacks.
        
        Args:
            value: The value to sanitize
            max_length: Maximum allowed length for the component
            
        Returns:
            Sanitized string safe for use in filenames
        """
        # Remove any characters that are not alphanumeric, underscore, or hyphen
        sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '', str(value))
        
        # Truncate to max length
        sanitized = sanitized[:max_length]
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            sanitized = 'unknown'
            
        return sanitized
    
    def _validate_export_format(self, format_str: str) -> str:
        """Validate and sanitize export format.
        
        Args:
            format_str: The format string to validate
            
        Returns:
            Validated format string
            
        Raises:
            ValueError: If format is not allowed
        """
        format_lower = str(format_str).lower().strip()
        
        # Check for dangerous patterns before sanitization
        dangerous_patterns = [
            '..',           # Path traversal
            '/',            # Directory separator
            '\\',           # Windows directory separator
            ';',            # Command separator
            '&',            # Command separator
            '|',            # Pipe operator
            '`',            # Command substitution
            '$',            # Variable expansion
            '<',            # Redirection
            '>',            # Redirection
            '*',            # Wildcard
            '?',            # Wildcard
        ]
        
        # Reject if contains dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in format_lower:
                raise ValueError(f"Unsupported export format: {format_str}. Contains dangerous pattern: {pattern}")
        
        # Remove any non-alphanumeric characters
        format_sanitized = re.sub(r'[^a-zA-Z0-9]', '', format_lower)
        
        # Check if format is empty after sanitization or not in allowed list
        if not format_sanitized or format_sanitized not in self._allowed_export_formats:
            raise ValueError(f"Unsupported export format: {format_str}. Allowed formats: {', '.join(self._allowed_export_formats)}")
        
        return format_sanitized
    
    def save_scraping_result(self, job_id: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save scraping results."""
        return self.result_storage.save_result(job_id, data, metadata)
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific result by ID."""
        return self.result_storage.get_result(result_id)
    
    def get_job_results(self, job_id: str, limit: int = 5, offset: int = 0) -> List[ResultData]:
        """Get results for a specific job with pagination support."""
        results = self.result_storage.get_results_by_job(str(job_id))
        
        # Apply pagination if limit is specified
        if limit is not None:
            results = results[offset:offset + limit]
        else:
            results = results[offset:] if offset > 0 else results
        
        # Wrap results in ResultData objects
        return [ResultData(result) for result in results]
    
    def get_job_results_count(self, job_id: str) -> int:
        """Get the total count of results for a specific job."""
        results = self.result_storage.get_results_by_job(job_id)
        return len(results) if results else 0
    
    def list_recent_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent results with metadata."""
        return self.result_storage.list_results(limit=limit)
    
    def export_result_data(self, result_id: str, format: str = "json") -> Optional[Dict[str, Any]]:
        """Export result data in specified format."""
        # Get raw data from storage
        result = self.result_storage.get_result(result_id)
        if result is None:
            return None
        
        # Import utils and validate format
        from src.utils import data_utils
        try:
            format = self._validate_export_format(format)
        except ValueError as e:
            return {"error": str(e)}
        
        # Map format to export function
        export_funcs = {
            'json': data_utils.export_to_json,
            'csv': data_utils.export_to_csv,
            'xlsx': data_utils.export_to_excel
        }
        
        # Execute export
        if format in export_funcs:
            try:
                # Prepare data for export
                export_data = result.get('data', {})
                filename = f"result_{result_id}_{self._get_current_timestamp()}"
                
                # Call appropriate export function
                file_path = export_funcs[format](
                    export_data,
                    filename=filename,
                    metadata={
                        'result_id': result_id,
                        'job_id': result.get('job_id'),
                        'exported_at': self._get_current_timestamp(),
                        'source_url': result.get('source_url')
                    }
                )
                
                return {
                    "file_path": str(file_path),
                    "format": format,
                    "exported_at": self._get_current_timestamp(),
                    "success": True
                }
            except Exception as e:
                return {
                    "error": f"Export failed: {str(e)}",
                    "format": format,
                    "success": False
                }
        
        return {"error": f"Unsupported format: {format}"}
    
    def process_scraped_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                           processing_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process scraped data according to rules."""
        # Import template scraper for processing logic
        from src.scrapers.template_scraper import TemplateScraper
        
        # Create temporary scraper instance for processing
        temp_template = {'post_processing': processing_rules or []}
        temp_scraper = TemplateScraper(template=temp_template)
        
        # Process each item if list, or single item
        try:
            if isinstance(data, list):
                processed_items = []
                for item in data:
                    # Use scraper's post-processing method
                    processed = temp_scraper._apply_post_processing(item)
                    processed_items.append(processed)
                processed_data = processed_items
            else:
                processed_data = temp_scraper._apply_post_processing(data)
            
            # Return processed results with metadata
            return {
                "processed": True,
                "item_count": len(processed_data) if isinstance(processed_data, list) else 1,
                "data": processed_data,
                "rules_applied": processing_rules or {},
                "processed_at": self._get_current_timestamp(),
                "success": True
            }
        except Exception as e:
            # Handle processing errors gracefully
            return {
                "processed": False,
                "item_count": len(data) if isinstance(data, list) else 1,
                "data": data,  # Return original data on error
                "rules_applied": processing_rules or {},
                "error": f"Processing failed: {str(e)}",
                "success": False
            }
    
    def validate_data_structure(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Validate scraped data structure."""
        if data is None:
            return {
                "valid": False,
                "error": "Data is None"
            }
        
        if isinstance(data, dict):
            return {
                "valid": True,
                "type": "object",
                "fields": list(data.keys()),
                "item_count": 1
            }
        elif isinstance(data, list):
            return {
                "valid": True,
                "type": "array",
                "item_count": len(data),
                "sample_fields": list(data[0].keys()) if data and isinstance(data[0], dict) else []
            }
        else:
            return {
                "valid": False,
                "error": f"Unsupported data type: {type(data)}"
            }
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get data storage statistics."""
        return self.result_storage.get_storage_stats()
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old data."""
        deleted_count = self.result_storage.cleanup_old_results(days_old)
        return {
            "deleted_results": deleted_count,
            "days_threshold": days_old
        }
    
    def export_job_results(self, job_id: str, format: str = 'csv') -> Path:
        """Export job results to file in specified format."""
        from src.core.config import config
        
        # SECURITY: Sanitize inputs to prevent path traversal attacks
        sanitized_job_id = self._sanitize_filename_component(job_id, max_length=32)
        validated_format = self._validate_export_format(format)
        
        # Get results for the job using original job_id for data retrieval
        results = self.result_storage.get_results_by_job(str(job_id))
        
        # Create export directory if it doesn't exist
        export_dir = Path(config.data_folder) / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate secure filename using sanitized components
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"job_{sanitized_job_id}_{timestamp}.{validated_format}"
        file_path = export_dir / filename
        
        if validated_format == 'csv':
            # Export as CSV
            if results and isinstance(results[0].get('data'), dict):
                # Get all unique keys from all results
                all_keys = set()
                for result in results:
                    if isinstance(result.get('data'), dict):
                        all_keys.update(result['data'].keys())
                
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    for result in results:
                        if isinstance(result.get('data'), dict):
                            writer.writerow(result['data'])
            else:
                # Write as simple CSV with result metadata
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['id', 'job_id', 'created_at', 'data'])
                    for result in results:
                        writer.writerow([
                            result.get('id'),
                            result.get('job_id'),
                            result.get('created_at'),
                            json.dumps(result.get('data'))
                        ])
        else:
            # Default to JSON export
            with open(file_path, 'w') as jsonfile:
                json.dump(results, jsonfile, indent=2, default=str)
        
        return file_path
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()