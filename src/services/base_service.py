# -*- coding: utf-8 -*-
"""
Base Service Class

Provides common interface and functionality for all service implementations.
Services encapsulate business logic separate from UI.

Best Practices:
- Validate inputs in validate()
- Execute business logic in execute()
- Handle errors gracefully
- Clean up resources in cleanup()
- Log all significant operations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.logger import get_logger
from core.exceptions import EasyCutException

logger = get_logger(__name__)


class ServiceResult:
    """Standard result object for service operations"""
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """
        Initialize result
        
        Args:
            success: Operation succeeded
            data: Result data
            error: Error message
            error_code: Error categorization
            context: Additional context for debugging
        """
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code or ("OK" if success else "ERROR")
        self.context = context or {}
    
    def __bool__(self):
        return self.success
    
    def __repr__(self):
        return f"ServiceResult(success={self.success}, code={self.error_code})"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
            "context": self.context
        }


class BaseService(ABC):
    """
    Base class for all services
    
    Services contain business logic and are independent from UI.
    They return ServiceResult objects with consistent structure.
    """
    
    def __init__(self):
        """Initialize service"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """
        Validate input parameters
        
        Args:
            **kwargs: Parameters to validate
        
        Returns:
            True if valid, raises ValidationException otherwise
        
        Raises:
            ValidationException: If validation fails
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ServiceResult:
        """
        Execute service operation
        
        Args:
            **kwargs: Operation parameters
        
        Returns:
            ServiceResult with operation result
        """
        pass
    
    def cleanup(self) -> None:
        """
        Cleanup resources after service execution
        
        Override if service uses resources that need cleanup:
        - File handles
        - Thread pools
        - Temporary files
        - Database connections
        """
        self.logger.debug("Cleanup (no-op)")
    
    # Convenience methods
    
    def success(self, data: Any = None, **context) -> ServiceResult:
        """Create success result"""
        return ServiceResult(
            success=True,
            data=data,
            context=context
        )
    
    def error(
        self,
        message: str,
        code: str = "ERROR",
        **context
    ) -> ServiceResult:
        """Create error result"""
        return ServiceResult(
            success=False,
            error=message,
            error_code=code,
            context=context
        )
    
    def __enter__(self):
        """Context manager enter"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        self.cleanup()
        if exc_type:
            self.logger.error(
                f"Service error: {exc_type.__name__}: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        return False  # Don't suppress exceptions
    
    def __repr__(self):
        return f"<{self.__class__.__name__}>"


# Example service implementation:

class ExampleService(BaseService):
    """Example service showing best practices"""
    
    def validate(self, url: str = None, **kwargs) -> bool:
        """Validate inputs"""
        from ..core.exceptions import ValidationException
        
        if not url:
            raise ValidationException("URL is required", "INVALID_URL")
        
        if not url.startswith("http"):
            raise ValidationException("Invalid URL format", "INVALID_FORMAT")
        
        return True
    
    def execute(self, url: str, **kwargs) -> ServiceResult:
        """Execute operation"""
        try:
            # Validate first
            self.validate(url=url, **kwargs)
            
            # Executive operation
            self.logger.info(f"Processing: {url}")
            
            # Simulate work
            result_data = {
                "url": url,
                "status": "processed"
            }
            
            self.logger.info("Operation completed successfully")
            return self.success(data=result_data)
        
        except EasyCutException as e:
            self.logger.error(f"Validation failed: {e}")
            return self.error(str(e), e.code)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return self.error(str(e), "INTERNAL_ERROR")
