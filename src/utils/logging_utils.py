"""Logging utilities for ScraperV4."""

import logging
import logging.handlers
from pathlib import Path
from src.core.config import config

def setup_logging() -> None:
    """Set up logging configuration."""
    log_config = config.logging
    
    # Create logs directory
    log_path = Path(log_config.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.level),
        format=log_config.format,
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_config.file,
                maxBytes=log_config.max_bytes,
                backupCount=log_config.backup_count
            ),
            logging.StreamHandler()
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)

def log_scraping_activity(logger: logging.Logger, job_id: str, action: str, 
                         details: str = "", level: str = "INFO") -> None:
    """Log scraping activity with structured format."""
    log_message = f"[JOB:{job_id}] {action}"
    if details:
        log_message += f" - {details}"
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, log_message)

def log_template_activity(logger: logging.Logger, template_name: str, action: str, 
                         details: str = "", level: str = "INFO") -> None:
    """Log template-related activity."""
    log_message = f"[TEMPLATE:{template_name}] {action}"
    if details:
        log_message += f" - {details}"
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, log_message)

def log_service_activity(logger: logging.Logger, service_name: str, action: str, 
                        details: str = "", level: str = "INFO") -> None:
    """Log service-related activity."""
    log_message = f"[SERVICE:{service_name}] {action}"
    if details:
        log_message += f" - {details}"
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, log_message)

def create_performance_logger() -> logging.Logger:
    """Create a dedicated performance logger."""
    perf_logger = logging.getLogger('scraperv4.performance')
    
    # Create performance log file
    perf_log_path = Path(config.logging.file).parent / 'performance.log'
    
    perf_handler = logging.handlers.RotatingFileHandler(
        perf_log_path,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count
    )
    
    perf_formatter = logging.Formatter(
        '%(asctime)s - PERF - %(message)s'
    )
    perf_handler.setFormatter(perf_formatter)
    
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    
    return perf_logger

def create_error_logger() -> logging.Logger:
    """Create a dedicated error logger."""
    error_logger = logging.getLogger('scraperv4.errors')
    
    # Create error log file
    error_log_path = Path(config.logging.file).parent / 'errors.log'
    
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count
    )
    
    error_formatter = logging.Formatter(
        '%(asctime)s - ERROR - %(name)s - %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    
    error_logger.addHandler(error_handler)
    error_logger.setLevel(logging.ERROR)
    
    return error_logger