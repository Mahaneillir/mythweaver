"""
Enhanced logging configuration for HTTP requests and application logs
"""
import logging
import sys
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Build colored log message
        formatted_message = (
            f"{color}[{timestamp}] "
            f"{record.levelname:8} | "
            f"{record.name:15} | "
            f"{record.getMessage()}{reset}"
        )
        
        return formatted_message


def setup_logging(log_level: str = "INFO", enable_json_logs: bool = False):
    """Setup application logging configuration"""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    if enable_json_logs:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredConsoleFormatter())
    
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    configure_logger("uvicorn.access", log_level)
    configure_logger("uvicorn.error", log_level) 
    configure_logger("sqlalchemy.engine", "WARNING")  # Reduce SQL query noise
    configure_logger("http_requests", log_level)
    configure_logger("app", log_level)
    
    logging.info("🎯 Logging configured successfully")


def configure_logger(logger_name: str, level: str):
    """Configure individual logger"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.propagate = True  # Allow messages to bubble up to root logger


def get_app_logger(name: str) -> logging.Logger:
    """Get application logger with consistent naming"""
    return logging.getLogger(f"app.{name}")


# HTTP Request ID for tracing (simple implementation)
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default='')

def generate_request_id() -> str:
    """Generate unique request ID"""
    return str(uuid.uuid4())[:8]

def set_request_id(request_id: str):
    """Set request ID in context"""
    request_id_var.set(request_id)

def get_request_id() -> str:
    """Get current request ID"""
    return request_id_var.get('')


class RequestIDFilter(logging.Filter):
    """Add request ID to log records"""
    
    def filter(self, record):
        record.request_id = get_request_id()
        return True