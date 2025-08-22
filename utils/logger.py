import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

class AppLogger:
    """Centralized logging for the application."""
    
    def __init__(self, name: str = "SoftwareAutomation", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """Setup logging handlers."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file is None:
            log_file = Path(__file__).parent.parent / "app.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, file: str) -> None:
        """Log info message."""
        self.logger.info(f"[{file}] {message}")
    
    def debug(self, message: str, file: str) -> None:
        """Log debug message."""
        self.logger.debug(f"[{file}] {message}")
    
    def warning(self, message: str, file: str) -> None:
        """Log warning message."""
        self.logger.warning(f"[{file}] {message}")
    
    def error(self, message: str, file: str) -> None:
        """Log error message."""
        self.logger.error(f"[{file}] {message}")
    
    def critical(self, message: str, file: str) -> None:
        """Log critical message."""
        self.logger.critical(f"[{file}] {message}")
    
    def log_startup(self, file: str = Path(__file__).name) -> None:
        """Log application startup."""
        self.info(f"--- App started at {datetime.now()} ---", file=file)
    
    def log_mysql_connection(self, status: str, details: str = "", file: str = Path(__file__).name) -> None:
        """Log MySQL connection status."""
        if details:
            self.info(f"MySQL connection {status}: {details}", file=file)
        else:
            self.info(f"MySQL connection {status}", file=file)
    
    def log_task_execution(self, task_name: str, command: str, status: str, details: str = "", file: str = Path(__file__).name) -> None:
        """Log task execution details."""
        message = f"Task '{task_name}' ({command}): {status}"
        if details:
            message += f" - {details}"
        
        if status == "success":
            self.info(message, file=file)
        elif status == "failure":
            self.error(message, file=file)
        else:
            self.warning(message, file=file)

# Global logger instance
logger = AppLogger()
