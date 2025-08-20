"""Main application entry point for ScraperV4."""

import sys
import os
import signal
from pathlib import Path
from src.core.config import config
from src.core.container import container
from src.utils.logging_utils import setup_logging, get_logger
from src.web.eel_app import EelApp
from src.web.api_routes import register_api_routes

def signal_handler(sig, frame):
    """Handle interrupt signals."""
    print("\nShutting down gracefully...")
    os._exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def setup_application():
    """Set up application components."""
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    logger.info(f"Starting {config.app_name} v{config.version}")
    
    # Register services in container
    from src.services.scraping_service import ScrapingService
    from src.services.template_service import TemplateService
    from src.services.data_service import DataService
    
    container.register_singleton(ScrapingService, ScrapingService)
    container.register_singleton(TemplateService, TemplateService)
    container.register_singleton(DataService, DataService)
    
    logger.info("Services registered in container")
    logger.info("Application setup completed")

def main():
    """Main application entry point."""
    try:
        setup_application()
        
        # Create and start Eel application
        app = EelApp()
        register_api_routes()
        
        logger = get_logger(__name__)
        logger.info(f"Starting {config.app_name} on http://localhost:{config.eel.port}")
        print(f"Starting {config.app_name} on http://localhost:{config.eel.port}")
        
        app.start()
        
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Application failed to start: {e}")
        print(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()