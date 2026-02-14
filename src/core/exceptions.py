# -*- coding: utf-8 -*-
"""
Custom Exception Classes for EasyCut

Provides structured exception hierarchy for better error handling
and debugging throughout the application.
"""


class EasyCutException(Exception):
    """Base exception for all EasyCut errors"""
    
    def __init__(self, message: str, code: str = None, context: dict = None):
        """
        Initialize exception
        
        Args:
            message: Human-readable error message
            code: Error code for categorization
            context: Additional error context for debugging
        """
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.code}] {self.message}"
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "context": self.context
        }


class ConfigException(EasyCutException):
    """Raised when configuration loading/saving fails"""
    pass


class DownloadException(EasyCutException):
    """Raised when download operation fails"""
    pass


class AudioException(EasyCutException):
    """Raised when audio conversion fails"""
    pass


class AuthException(EasyCutException):
    """Raised when authentication fails"""
    pass


class ValidationException(EasyCutException):
    """Raised when input validation fails"""
    pass


class FileException(EasyCutException):
    """Raised when file operations fail"""
    pass


class NetworkException(EasyCutException):
    """Raised when network operations fail"""
    pass
