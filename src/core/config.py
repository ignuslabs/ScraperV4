"""Configuration management for ScraperV4."""

import os
from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StorageConfig(BaseModel):
    """File storage configuration settings."""
    data_folder: str = "data"
    jobs_folder: str = "data/jobs"
    results_folder: str = "data/results"
    templates_folder: str = "templates"

class ScrapingConfig(BaseModel):
    """General scraping configuration settings."""
    default_delay: float = 2.0
    max_retries: int = 3
    timeout: int = 30
    stealth_mode: bool = True
    concurrent_jobs: int = 3
    user_agent: str = "ScraperV4/1.0"

class ScraplingConfig(BaseModel):
    """Scrapling scraper configuration."""
    stealth_mode: bool = True
    user_agent: str = "ScraperV4/1.0"
    timeout: int = 30
    max_retries: int = 3
    delay_range: tuple = (1, 3)
    
    @field_validator('delay_range', mode='before')
    @classmethod
    def parse_delay_range(cls, v):
        if isinstance(v, str):
            parts = v.split(',')
            return (int(parts[0]), int(parts[1]))
        return v

class EelConfig(BaseModel):
    """Eel web interface configuration."""
    port: int = 8080
    debug: bool = True
    web_folder: str = "web"
    allowed_extensions: List[str] = ['.html', '.css', '.js', '.png', '.jpg', '.gif']

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    file: str = "logs/scraperv4.log"
    max_bytes: int = 10_000_000  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class AppConfig(BaseModel):
    """Main application configuration."""
    app_name: str = "ScraperV4"
    version: str = "1.0.0"
    data_folder: str = "data"
    templates_folder: str = "templates"
    
    # Sub-configurations
    storage: StorageConfig = StorageConfig()
    scraping: ScrapingConfig = ScrapingConfig()
    scrapling: ScraplingConfig = ScraplingConfig()
    eel: EelConfig = EelConfig()
    logging: LoggingConfig = LoggingConfig()
    
    @field_validator('data_folder', 'templates_folder')
    @classmethod
    def ensure_folder_exists(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

# Global configuration instance
config = AppConfig()