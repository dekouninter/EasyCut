# -*- coding: utf-8 -*-
"""
EasyCut Core Module
Centralized configuration, constants, logging and exceptions

This module provides the foundation for the entire application:
- Unified configuration management
- Global constants and translations
- Centralized logging system
- Custom exception definitions

Author: Deko Costa
License: MIT
"""

from .config import ConfigManager
from .constants import Constants, TranslationKeys
from .logger import Logger, get_logger
from .exceptions import (
    EasyCutException,
    ConfigException,
    DownloadException,
    AuthException,
    ValidationException
)

__all__ = [
    "ConfigManager",
    "Constants",
    "TranslationKeys",
    "Logger",
    "get_logger",
    "EasyCutException",
    "ConfigException",
    "DownloadException",
    "AuthException",
    "ValidationException"
]
