"""Job management with file-based storage."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.core.config import config

class JobManager:
    """Manages scraping jobs using file storage."""
    
    def __init__(self):
        self.jobs_dir = Path(config.data_folder) / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_job(self, name: str, template_name: str, target_url: str,
                   job_config: Optional[Dict[str, Any]] = None,
                   parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new scraping job."""
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "name": name,
            "template_name": template_name,
            "target_url": target_url,
            "config": job_config or {},
            "parameters": parameters or {},
            "status": "pending",
            "progress": 0,
            "items_scraped": 0,
            "items_failed": 0,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "retry_count": 0
        }
        
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return job_data
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            with open(job_file, 'r') as f:
                return json.load(f)
        return None
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job data."""
        job_data = self.get_job(job_id)
        if job_data:
            job_data.update(updates)
            job_file = self.jobs_dir / f"{job_id}.json"
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            return True
        return False
    
    def list_jobs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all jobs with optional status filter."""
        jobs = []
        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                if not status or job_data.get('status') == status:
                    jobs.append(job_data)
            except Exception:
                continue
        
        return sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            job_file.unlink()
            return True
        return False
    
    def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None) -> bool:
        """Update job status and timestamps."""
        updates = {"status": status}
        
        if status == "running":
            updates["started_at"] = datetime.now().isoformat()
        elif status in ["completed", "failed"]:
            updates["completed_at"] = datetime.utcnow().isoformat()
        
        if error_message:
            updates["error_message"] = error_message
        
        return self.update_job(job_id, updates)
    
    def update_job_progress(self, job_id: str, progress: int, items_scraped: int = 0, items_failed: int = 0) -> bool:
        """Update job progress metrics."""
        updates = {
            "progress": progress,
            "items_scraped": items_scraped,
            "items_failed": items_failed
        }
        return self.update_job(job_id, updates)