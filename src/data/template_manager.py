"""Template storage and management with file operations."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.core.config import config

class FileTemplateManager:
    """File-based template storage and management."""
    
    def __init__(self):
        self.templates_dir = Path(config.templates_folder)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates_cache: Dict[str, Dict[str, Any]] = {}
    
    def create_template(self, name: str, selectors: Dict[str, str], 
                       validation_rules: Optional[Dict[str, Any]] = None,
                       description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new template."""
        template_id = str(uuid.uuid4())
        template_data = {
            "id": template_id,
            "name": name,
            "description": description or "",
            "version": "1.0.0",
            "selectors": selectors,
            "validation_rules": validation_rules or {},
            "adaptive_selectors": True,
            "fallback_selectors": {},
            "post_processing": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "success_rate": 100.0,
            "usage_count": 0
        }
        
        template_file = self.templates_dir / f"{name}.json"
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        self._templates_cache[name] = template_data
        return template_data
    
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Load template from file or cache."""
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.json"
        if not template_path.exists():
            return None
        
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            self._templates_cache[template_name] = template
            return template
        except Exception:
            return None
    
    def save_template(self, template_name: str, template_data: Dict[str, Any]) -> bool:
        """Save template to file and update cache."""
        try:
            template_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            template_path = self.templates_dir / f"{template_name}.json"
            
            with open(template_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            self._templates_cache[template_name] = template_data
            return True
        except Exception:
            return False
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates with metadata."""
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                templates.append({
                    "name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", ""),
                    "version": template_data.get("version", "1.0.0"),
                    "is_active": template_data.get("is_active", True),
                    "success_rate": template_data.get("success_rate", 100.0),
                    "usage_count": template_data.get("usage_count", 0),
                    "created_at": template_data.get("created_at", ""),
                    "updated_at": template_data.get("updated_at", "")
                })
            except Exception:
                continue
        
        return sorted(templates, key=lambda x: x.get('updated_at', ''), reverse=True)
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template."""
        template_path = self.templates_dir / f"{template_name}.json"
        if template_path.exists():
            template_path.unlink()
            if template_name in self._templates_cache:
                del self._templates_cache[template_name]
            return True
        return False
    
    def update_template_stats(self, template_name: str, success: bool) -> bool:
        """Update template success rate and usage statistics."""
        template = self.load_template(template_name)
        if not template:
            return False
        
        usage_count = template.get("usage_count", 0) + 1
        current_success_rate = template.get("success_rate", 100.0)
        
        # Calculate new success rate using weighted average
        if success:
            new_success_rate = ((current_success_rate * (usage_count - 1)) + 100.0) / usage_count
        else:
            new_success_rate = ((current_success_rate * (usage_count - 1)) + 0.0) / usage_count
        
        template["usage_count"] = usage_count
        template["success_rate"] = round(new_success_rate, 2)
        
        return self.save_template(template_name, template)
    
    def get_template_names(self) -> List[str]:
        """Get list of template names."""
        return [f.stem for f in self.templates_dir.glob("*.json")]
    
    def clear_cache(self) -> None:
        """Clear the templates cache."""
        self._templates_cache.clear()