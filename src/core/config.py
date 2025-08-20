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
    
    @field_validator('default_delay')
    @classmethod
    def validate_default_delay(cls, v):
        if v < 0:
            raise ValueError("default_delay must be non-negative")
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        return v
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("timeout must be positive")
        return v
    
    @field_validator('concurrent_jobs')
    @classmethod
    def validate_concurrent_jobs(cls, v):
        if v < 1:
            raise ValueError("concurrent_jobs must be at least 1")
        return v

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
            if len(parts) != 2:
                raise ValueError("delay_range must contain exactly two values separated by comma")
            try:
                return (float(parts[0]), float(parts[1]))
            except ValueError:
                raise ValueError("delay_range values must be numeric")
        return v
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("timeout must be positive")
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        return v

class EelConfig(BaseModel):
    """Eel web interface configuration."""
    port: int = 8080
    debug: bool = True
    web_folder: str = "web"
    allowed_extensions: List[str] = ['.html', '.css', '.js', '.png', '.jpg', '.gif']
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if v < 0 or v > 65535:
            raise ValueError("port must be between 0 and 65535")
        return v

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    file: str = "logs/scraperv4.log"
    max_bytes: int = 10_000_000  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @field_validator('max_bytes')
    @classmethod
    def validate_max_bytes(cls, v):
        if v < 0:
            raise ValueError("max_bytes must be non-negative")
        return v
    
    @field_validator('backup_count')
    @classmethod
    def validate_backup_count(cls, v):
        if v < 0:
            raise ValueError("backup_count must be non-negative")
        return v

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