# -*- coding: utf-8 -*-
"""
Centralized Logging System for EasyCut

Provides structured logging throughout the application with:
- File and console output
- Multiple log levels
- Structured error messages
- Performance tracking

Usage:
    from core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Message")
    logger.error("Error", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured, readable log output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors and structure"""
        # Get color
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Format message
        if record.exc_info:
            message_text = f"{record.getMessage()}\n{self.formatException(record.exc_info)}"
        else:
            message_text = record.getMessage()
        
        # Build formatted string
        if sys.stdout.isatty():
            # Terminal output - use colors
            formatted = f"{timestamp} {color}[{record.levelname}]{reset} {record.name}: {message_text}"
        else:
            # File output - no colors
            formatted = f"{timestamp} [{record.levelname}] {record.name}: {message_text}"
        
        return formatted


class Logger:
    """Main logging interface for EasyCut"""
    
    _instance = None
    _loggers = {}
    _log_dir = None
    
    @classmethod
    def initialize(cls, log_dir: Optional[Path] = None, level: int = logging.INFO):
        """
        Initialize logging system
        
        Args:
            log_dir: Directory for log files (None = no file logging)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        cls._log_dir = log_dir
        
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(console_handler)
        
        # File handler
        if log_dir:
            log_file = log_dir / f"easycut_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(StructuredFormatter())
            root_logger.addHandler(file_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create logger for module"""
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]


# Convenience function
def get_logger(name: str) -> logging.Logger:
    """Get logger for a module
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        Configured logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Starting download...")
    """
    return Logger.get_logger(name)
