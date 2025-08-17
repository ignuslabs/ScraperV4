"""Template management system with self-healing capabilities."""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from src.core.config import config

class TemplateManager:
    """Manages scraping templates with self-healing capabilities."""
    
    def __init__(self):
        self.templates_dir = Path(config.templates_folder)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load template from file or cache."""
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.json"
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found")
        
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        self._templates_cache[template_name] = template
        return template
    
    def save_template(self, template_name: str, template_data: Dict[str, Any]) -> None:
        """Save template to file and update cache."""
        template_path = self.templates_dir / f"{template_name}.json"
        
        with open(template_path, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        self._templates_cache[template_name] = template_data
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        return [f.stem for f in self.templates_dir.glob("*.json")]
    
    def create_default_template(self, name: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Create a default template structure."""
        template = {
            "name": name,
            "version": "1.0.0",
            "selectors": selectors,
            "validation_rules": {},
            "adaptive_selectors": True,
            "fallback_selectors": {},
            "post_processing": []
        }
        
        self.save_template(name, template)
        return template
    
    def update_template_selectors(self, template_name: str, new_selectors: Dict[str, str], 
                                 backup_old: bool = True) -> bool:
        """Update template selectors with self-healing capability."""
        try:
            template = self.load_template(template_name)
            
            if backup_old and template.get('selectors'):
                # Backup current selectors as fallback
                if 'fallback_selectors' not in template:
                    template['fallback_selectors'] = {}
                template['fallback_selectors'][f"backup_{len(template['fallback_selectors'])}"] = template['selectors']
            
            template['selectors'] = new_selectors
            template['version'] = self._increment_version(template.get('version', '1.0.0'))
            
            self.save_template(template_name, template)
            return True
            
        except Exception:
            return False
    
    def add_fallback_selectors(self, template_name: str, fallback_selectors: Dict[str, str]) -> bool:
        """Add fallback selectors for self-healing."""
        try:
            template = self.load_template(template_name)
            
            if 'fallback_selectors' not in template:
                template['fallback_selectors'] = {}
            
            template['fallback_selectors'].update(fallback_selectors)
            self.save_template(template_name, template)
            return True
            
        except Exception:
            return False
    
    def get_template_with_fallbacks(self, template_name: str) -> Dict[str, Any]:
        """Get template with all available fallback selectors."""
        template = self.load_template(template_name)
        
        # Merge primary and fallback selectors
        all_selectors = template.get('selectors', {}).copy()
        fallback_selectors = template.get('fallback_selectors', {})
        
        # Add fallback options for each field
        for field_name, primary_selector in all_selectors.items():
            fallback_options = []
            
            # Look for fallbacks in all fallback selector sets
            for fallback_set_name, fallback_set in fallback_selectors.items():
                if field_name in fallback_set:
                    fallback_options.append(fallback_set[field_name])
            
            if fallback_options:
                all_selectors[f"{field_name}_fallbacks"] = fallback_options
        
        template_with_fallbacks = template.copy()
        template_with_fallbacks['all_selectors'] = all_selectors
        return template_with_fallbacks
    
    def validate_template_structure(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template structure and requirements."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['name', 'selectors']
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate selectors
        selectors = template_data.get('selectors', {})
        if not isinstance(selectors, dict):
            errors.append("Selectors must be a dictionary")
        elif not selectors:
            warnings.append("No selectors defined")
        
        # Validate fallback selectors if present
        fallback_selectors = template_data.get('fallback_selectors', {})
        if fallback_selectors and not isinstance(fallback_selectors, dict):
            errors.append("Fallback selectors must be a dictionary")
        
        # Check for adaptive selector configuration
        if not template_data.get('adaptive_selectors', False):
            warnings.append("Adaptive selectors not enabled - self-healing capabilities limited")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_template_statistics(self, template_name: str) -> Dict[str, Any]:
        """Get usage and performance statistics for a template."""
        try:
            template = self.load_template(template_name)
            
            return {
                'name': template_name,
                'version': template.get('version', '1.0.0'),
                'selector_count': len(template.get('selectors', {})),
                'fallback_sets': len(template.get('fallback_selectors', {})),
                'has_validation_rules': bool(template.get('validation_rules')),
                'has_post_processing': bool(template.get('post_processing')),
                'adaptive_selectors_enabled': template.get('adaptive_selectors', False)
            }
            
        except Exception as e:
            return {
                'name': template_name,
                'error': str(e)
            }
    
    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._templates_cache.clear()
    
    def _increment_version(self, version: str) -> str:
        """Increment template version number."""
        try:
            parts = version.split('.')
            if len(parts) >= 3:
                parts[2] = str(int(parts[2]) + 1)
            else:
                parts.append('1')
            return '.'.join(parts)
        except Exception:
            return version