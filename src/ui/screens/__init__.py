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
from .login_screen import LoginScreen
from .download_screen import DownloadScreen
from .batch_screen import BatchScreen
from .live_screen import LiveScreen
from .history_screen import HistoryScreen
from .about_screen import AboutScreen

__all__ = [
    "BaseScreen",
    "LoginScreen",
    "DownloadScreen",
    "BatchScreen",
    "LiveScreen",
    "HistoryScreen",
    "AboutScreen"
]
