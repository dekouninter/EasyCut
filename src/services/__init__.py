# -*- coding: utf-8 -*-
"""
Services Module
Business logic layer

All services inherit from BaseService and implement:
- validate(): Input validation
- execute(): Business logic
- cleanup(): Resource cleanup
"""

from .base_service import BaseService, ServiceResult

__all__ = ["BaseService", "ServiceResult"]
