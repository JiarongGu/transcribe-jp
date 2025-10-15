"""Standardized logging utility for the application"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class AppLogger:
    """Centralized logging with standardized levels and formatting"""

    # Logging levels
    DEBUG = logging.DEBUG       # 10 - Detailed information for debugging
    INFO = logging.INFO         # 20 - General informational messages
    WARNING = logging.WARNING   # 30 - Warning messages
    ERROR = logging.ERROR       # 40 - Error messages
    CRITICAL = logging.CRITICAL # 50 - Critical error messages

    def __init__(self, log_dir: str = "transcripts/logs", name: str = "transcribe-jp"):
        """
        Initialize application logger

        Args:
            log_dir: Directory to store log files (default: "transcripts/logs")
            name: Logger name (default: "transcribe-jp")
        """
        self.log_dir = log_dir
        self.name = name
        self._handlers_setup = False

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Capture all levels

    def _ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def _setup_handlers(self):
        """Setup file and console handlers with formatters (lazy initialization)"""
        if self._handlers_setup:
            return

        # Ensure log directory exists before creating handlers
        self._ensure_log_dir()

        # File handler - logs everything to file
        log_file = os.path.join(
            self.log_dir,
            f"{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler - logs WARNING and above to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        self._handlers_setup = True

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._setup_handlers()
        if context:
            message = f"{message} | Context: {context}"
        self.logger.debug(message)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._setup_handlers()
        if context:
            message = f"{message} | Context: {context}"
        self.logger.info(message)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._setup_handlers()
        if context:
            message = f"{message} | Context: {context}"
        self.logger.warning(message)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._setup_handlers()
        if context:
            message = f"{message} | Context: {context}"
        self.logger.error(message)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self._setup_handlers()
        if context:
            message = f"{message} | Context: {context}"
        self.logger.critical(message)

    def log_json_decode_error(
        self,
        error: Exception,
        raw_response: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a JSON decode error with full details in a dedicated error file

        Args:
            error: The JSONDecodeError exception
            raw_response: The raw LLM response that failed to parse
            prompt: The prompt sent to the LLM
            context: Additional context (stage, batch_num, segment_num, etc.)

        Returns:
            Path to the created error detail file
        """
        # Ensure handlers are set up and log directory exists
        self._setup_handlers()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        timestamp_readable = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log to main log file
        error_msg = f"JSONDecodeError in {context.get('stage', 'unknown')} stage"
        self.error(error_msg, context)

        # Create detailed error file
        error_filename = f"{timestamp}_json_error.log"
        error_path = os.path.join(self.log_dir, error_filename)

        with open(error_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"JSON DECODE ERROR - DETAILED LOG\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Timestamp: {timestamp_readable}\n")
            f.write(f"Error Type: {type(error).__name__}\n")
            f.write(f"Error Message: {str(error)}\n\n")

            # Error details
            f.write("-" * 80 + "\n")
            f.write("ERROR DETAILS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Message: {getattr(error, 'msg', str(error))}\n")
            lineno = getattr(error, 'lineno', None)
            colno = getattr(error, 'colno', None)
            if lineno:
                f.write(f"Line: {lineno}, Column: {colno}\n")
            pos = getattr(error, 'pos', None)
            if pos:
                f.write(f"Position: {pos}\n")
            f.write("\n")

            # Context
            if context:
                f.write("-" * 80 + "\n")
                f.write("CONTEXT\n")
                f.write("-" * 80 + "\n")
                for key, value in context.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")

            # Raw response
            f.write("-" * 80 + "\n")
            f.write(f"RAW LLM RESPONSE ({len(raw_response)} characters)\n")
            f.write("-" * 80 + "\n")
            f.write(raw_response)
            f.write("\n\n")

            # Prompt
            f.write("-" * 80 + "\n")
            f.write(f"PROMPT SENT TO LLM ({len(prompt)} characters)\n")
            f.write("-" * 80 + "\n")
            f.write(prompt)
            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("END OF LOG\n")
            f.write("=" * 80 + "\n")

        # Log the detailed file location
        self.info(f"Detailed error log saved: {error_filename}")

        return error_path

    def log_exception(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        level: int = ERROR
    ) -> str:
        """
        Log an exception with full details in a dedicated error file

        Args:
            error: The exception
            operation: Description of the operation that failed
            context: Additional context
            level: Logging level (default: ERROR)

        Returns:
            Path to the created error detail file
        """
        # Ensure handlers are set up and log directory exists
        self._setup_handlers()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        timestamp_readable = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log to main log file
        error_msg = f"Exception during {operation}: {type(error).__name__} - {str(error)}"
        if level == self.CRITICAL:
            self.critical(error_msg, context)
        elif level == self.ERROR:
            self.error(error_msg, context)
        elif level == self.WARNING:
            self.warning(error_msg, context)
        else:
            self.info(error_msg, context)

        # Create detailed error file
        error_filename = f"{timestamp}_exception.log"
        error_path = os.path.join(self.log_dir, error_filename)

        with open(error_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"EXCEPTION - DETAILED LOG\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Timestamp: {timestamp_readable}\n")
            f.write(f"Operation: {operation}\n")
            f.write(f"Error Type: {type(error).__name__}\n")
            f.write(f"Error Message: {str(error)}\n\n")

            # Context
            if context:
                f.write("-" * 80 + "\n")
                f.write("CONTEXT\n")
                f.write("-" * 80 + "\n")
                for key, value in context.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")

            # Traceback if available
            import traceback
            tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            f.write("-" * 80 + "\n")
            f.write("TRACEBACK\n")
            f.write("-" * 80 + "\n")
            f.write(tb)
            f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("END OF LOG\n")
            f.write("=" * 80 + "\n")

        # Log the detailed file location
        self.info(f"Detailed exception log saved: {error_filename}")

        return error_path


# Global logger instance
_app_logger = None


def get_logger(log_dir: str = "transcripts/logs", name: str = "transcribe-jp") -> AppLogger:
    """
    Get global logger instance

    Args:
        log_dir: Directory to store log files (default: "transcripts/logs")
        name: Logger name (default: "transcribe-jp")

    Returns:
        AppLogger instance
    """
    global _app_logger
    if _app_logger is None:
        _app_logger = AppLogger(log_dir, name)
    return _app_logger
