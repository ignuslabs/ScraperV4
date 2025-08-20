"""Eel application wrapper for ScraperV4."""

import eel
from pathlib import Path
from src.core.config import config
from src.core.container import container

class EelApp:
    """Eel application wrapper with ScraperV4 integration."""
    
    def __init__(self):
        self.config = config.eel
        self.web_folder = Path(self.config.web_folder)
        self.main_page = "index.html"  # Track the main page
        self._setup_eel()
    
    def _setup_eel(self):
        """Initialize Eel with configuration."""
        eel.init(str(self.web_folder))
    
    def start(self, start_url: str = "index.html", **kwargs):
        """Start the Eel application."""
        eel_kwargs = {
            'mode': 'chrome',
            'port': self.config.port,
            'close_callback': self._on_close,
            **kwargs
        }
        
        # Note: eel.start() doesn't have a debug parameter
        # Debug mode is handled differently in Eel
        
        eel.start(start_url, **eel_kwargs)
    
    def _on_close(self, page, sockets):
        """Handle application close event."""
        import sys
        import os
        import signal
        
        # Only terminate if the main window is closing
        # page contains the path of the closing page
        if page == self.main_page or page == f"/{self.main_page}":
            print("Main application window closed - terminating...")
            
            # Try graceful shutdown first
            try:
                # Clean up any resources if needed
                cleanup_method = getattr(self, 'cleanup', None)
                if cleanup_method:
                    cleanup_method()
            except:
                pass
            
            # Force terminate the process and all its children
            try:
                # Send SIGTERM to the entire process group
                os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
            except:
                pass
            
            # Final fallback - force exit
            os._exit(0)
        else:
            # Just log that a popup/secondary window was closed
            print(f"Secondary window closed: {page}")
    
    @staticmethod
    def expose(func):
        """Decorator to expose Python functions to JavaScript."""
        return eel.expose(func)