#!/usr/bin/env python3
"""Test template API functionality"""

import requests
import json

def test_get_templates():
    """Test getting all templates"""
    print("Testing get_templates API...")
    
    # This won't work with direct HTTP since we need eel WebSocket connection
    # Let's test via Python directly
    
    import sys
    sys.path.append('.')
    
    from src.core.container import container
    from src.services.template_service import TemplateService
    from src.utils.logging_utils import setup_logging, get_logger
    
    setup_logging()
    logger = get_logger(__name__)
    
    try:
        template_service = container.resolve(TemplateService)
        templates = template_service.get_all_templates()
        
        print(f"Found {len(templates)} templates:")
        for template in templates:
            print(f"  - ID: {template.id}, Name: {template.name}")
            print(f"    Description: {template.description}")
            print(f"    Selectors: {template.selectors}")
            print(f"    Version: {template.version}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_templates()