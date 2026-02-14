# -*- coding: utf-8 -*-
"""
UI Screens Module
Tab screen implementations

Each screen represents a tab in the application.
All screens inherit from BaseScreen and implement:
- build(): Create UI
- bind_events(): Connect event handlers
- get_data(): Return current state
"""

from .base_screen import BaseScreen

__all__ = ["BaseScreen"]
