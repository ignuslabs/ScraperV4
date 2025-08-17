"""Template CRUD operations service."""

from typing import Dict, Any, List, Optional
from .base_service import BaseService

class TemplateData:
    """Simple wrapper class to provide attribute access to template data."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
    def __getattr__(self, name):
        """Provide attribute-style access to dictionary keys."""
        return self._data.get(name, '')
    
    @property
    def id(self):
        """Return id or use name as fallback."""
        return self._data.get('id', self._data.get('name', ''))
    
    @property
    def name(self):
        return self._data.get('name', '')
    
    @property
    def description(self):
        return self._data.get('description', '')
    
    @property
    def version(self):
        return self._data.get('version', '1.0.0')
    
    @property
    def usage_count(self):
        return self._data.get('usage_count', 0)
    
    @property
    def success_rate(self):
        return self._data.get('success_rate', 100.0)
    
    @property
    def created_at(self):
        return self._data.get('created_at', '')
    
    @property
    def selectors(self):
        return self._data.get('selectors', {})
    
    @property
    def validation_rules(self):
        return self._data.get('validation_rules', {})
    
    @property
    def post_processing(self):
        return self._data.get('post_processing', [])
    
    @property
    def adaptive_selectors(self):
        return self._data.get('adaptive_selectors', True)
    
    @property
    def fallback_selectors(self):
        return self._data.get('fallback_selectors', {})

class TemplateService(BaseService):
    """Service for managing scraping templates."""
    
    def __init__(self):
        super().__init__()
    
    def create_template(self, name: str, selectors: Dict[str, str], 
                       description: Optional[str] = None,
                       validation_rules: Optional[Dict[str, Any]] = None,
                       **kwargs) -> TemplateData:
        """Create a new scraping template."""
        template_dict = self.template_manager.create_template(
            name=name,
            selectors=selectors,
            description=description,
            validation_rules=validation_rules
        )
        return TemplateData(template_dict)
    
    def get_template(self, template_name: str) -> Optional[TemplateData]:
        """Get a template by name."""
        template_dict = self.template_manager.load_template(template_name)
        if template_dict:
            return TemplateData(template_dict)
        return None
    
    def update_template(self, template_name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template."""
        template = self.template_manager.load_template(template_name)
        if template:
            template.update(updates)
            return self.template_manager.save_template(template_name, template)
        return False
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template."""
        return self.template_manager.delete_template(template_name)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates."""
        return self.template_manager.list_templates()
    
    def get_all_templates(self) -> List[TemplateData]:
        """Get all templates with full details (alias for list_templates for API compatibility)."""
        templates = self.list_templates()
        return [TemplateData(template) for template in templates]
    
    def validate_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template structure (stub implementation)."""
        # Basic validation stub
        required_fields = ["name", "selectors"]
        missing_fields = [field for field in required_fields if field not in template_data]
        
        if missing_fields:
            return {
                "valid": False,
                "errors": [f"Missing required field: {field}" for field in missing_fields]
            }
        
        if not isinstance(template_data.get("selectors"), dict):
            return {
                "valid": False,
                "errors": ["Selectors must be a dictionary"]
            }
        
        return {
            "valid": True,
            "errors": []
        }
    
    def test_template(self, template_name: str, test_url: str) -> Dict[str, Any]:
        """Test a template against a URL."""
        # Get template from storage
        template = self.template_manager.load_template(template_name)
        if not template:
            return {
                "success": False,
                "error": "Template not found"
            }
        
        # Create TemplateScraper instance
        from src.scrapers.template_scraper import TemplateScraper
        
        try:
            # Initialize scraper with template
            scraper = TemplateScraper(template=template)
            
            # Call scraper's test_selectors method
            test_results = scraper.test_selectors(test_url)
            
            # Update template statistics based on results
            if test_results.get('success_rate', 0) > 0:
                # Update success stats for the template
                self.template_manager.update_template_stats(
                    template_name, 
                    success=test_results.get('success_rate', 0) > 0.5
                )
            
            # Return comprehensive test results
            return {
                "success": True,
                "template": template_name,
                "test_url": test_url,
                "results": test_results,
                "success_rate": test_results.get('success_rate', 0),
                "field_results": test_results.get('field_results', {}),
                "sample_data": test_results.get('sample_data', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Template testing failed: {str(e)}",
                "template": template_name,
                "test_url": test_url
            }