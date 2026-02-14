# -*- coding: utf-8 -*-
"""
UI Factories Package
Factory functions for creating consistently-styled widgets and containers
"""

from .widget_factory import (
    ButtonFactory,
    FrameFactory,
    CanvasScrollFactory,
    DialogFactory,
    InputFactory,
    create_button,
    create_container,
    create_scrollable
)

from .tab_factory import (
    TabFactory,
    create_tab,
    create_tab_header,
    create_tab_section
)

__all__ = [
    # Factories
    "ButtonFactory",
    "FrameFactory",
    "CanvasScrollFactory",
    "DialogFactory",
    "InputFactory",
    "TabFactory",
    
    # Shortcuts
    "create_button",
    "create_container",
    "create_scrollable",
    "create_tab",
    "create_tab_header",
    "create_tab_section",
]
