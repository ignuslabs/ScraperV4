"""Results storage with file operations."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from src.core.config import config

class ResultStorage:
    """File-based storage for scraping results."""
    
    def __init__(self):
        self.results_dir = Path(config.data_folder) / "results"
        self.exports_dir = Path(config.data_folder) / "exports"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    def save_result(self, job_id: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save scraping result with metadata."""
        result_id = str(uuid.uuid4())
        result_data = {
            "id": result_id,
            "job_id": job_id,
            "data": data,
            "metadata": metadata or {},
            "item_count": len(data) if isinstance(data, list) else 1,
            "created_at": datetime.utcnow().isoformat(),
            "file_size": 0  # Will be calculated after saving
        }
        
        result_file = self.results_dir / f"{result_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        # Update file size
        result_data["file_size"] = result_file.stat().st_size
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        return result_id
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get result by ID."""
        result_file = self.results_dir / f"{result_id}.json"
        if result_file.exists():
            try:
                with open(result_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    def get_results_by_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all results for a specific job."""
        results = []
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                if result_data.get("job_id") == job_id:
                    results.append(result_data)
            except Exception:
                continue
        
        return sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def list_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all results with optional limit."""
        results = []
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                # Only include metadata for listing
                results.append({
                    "id": result_data.get("id"),
                    "job_id": result_data.get("job_id"),
                    "item_count": result_data.get("item_count", 0),
                    "file_size": result_data.get("file_size", 0),
                    "created_at": result_data.get("created_at"),
                    "metadata": result_data.get("metadata", {})
                })
            except Exception:
                continue
        
        results = sorted(results, key=lambda x: x.get('created_at', ''), reverse=True)
        return results[:limit] if limit else results
    
    def delete_result(self, result_id: str) -> bool:
        """Delete a result."""
        result_file = self.results_dir / f"{result_id}.json"
        if result_file.exists():
            result_file.unlink()
            return True
        return False
    
    def delete_results_by_job(self, job_id: str) -> int:
        """Delete all results for a specific job. Returns count of deleted results."""
        deleted_count = 0
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                if result_data.get("job_id") == job_id:
                    result_file.unlink()
                    deleted_count += 1
            except Exception:
                continue
        
        return deleted_count
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total_results = 0
        total_size = 0
        total_items = 0
        
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                total_results += 1
                total_size += result_data.get("file_size", 0)
                total_items += result_data.get("item_count", 0)
            except Exception:
                continue
        
        return {
            "total_results": total_results,
            "total_size_bytes": total_size,
            "total_items": total_items,
            "results_directory": str(self.results_dir),
            "exports_directory": str(self.exports_dir)
        }
    
    def export_result_data(self, result_id: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """Export just the data portion of a result."""
        result = self.get_result(result_id)
        if result:
            return result.get("data")
        return None
    
    def cleanup_old_results(self, days_old: int = 30) -> int:
        """Clean up results older than specified days. Returns count of deleted results."""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        deleted_count = 0
        
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                
                created_at = datetime.fromisoformat(result_data.get("created_at", ""))
                if created_at < cutoff_date:
                    result_file.unlink()
                    deleted_count += 1
            except Exception:
                continue
        
        return deleted_count