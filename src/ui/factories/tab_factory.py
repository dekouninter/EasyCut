# -*- coding: utf-8 -*-
"""
Tab Screen Factory

Creates consistently-structured tab containers with scrollable content,
standard layout patterns, and common UI elements.

This eliminates the 6+ duplicated "create_*_tab" implementations.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional, List, Tuple

from ui.factories.widget_factory import CanvasScrollFactory
from theme import ThemeManager
from core.logger import get_logger

logger = get_logger(__name__)


class TabFactory:
    """Factory for creating tab screens with consistent structure"""
    
    @staticmethod
    def create_scrollable_tab(
        notebook: ttk.Notebook,
        tab_text: str,
        theme: Optional[ThemeManager] = None,
        icon_emoji: str = "",
        enable_scroll_handler: Optional[Callable] = None,
        **kwargs
    ) -> Dict[str, tk.Widget]:
        """
        Create a scrollable tab with standard structure
        
        This is the BASE pattern used by ALL tabs:
        1. ttk.Frame added to notebook
        2. Canvas + Scrollbar for scrolling
        3. Inner frame for content
        4. Mouse wheel scroll handler
        
        Args:
            notebook: ttk.Notebook parent
            tab_text: Tab label text
            theme: ThemeManager for colors
            icon_emoji: Emoji icon prefix
            enable_scroll_handler: Function to enable mouse wheel (from main app)
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with: {
                "frame": ttk.Frame (tab frame),
                "canvas": tk.Canvas,
                "scrollbar": ttk.Scrollbar,
                "content": ttk.Frame (content container)
            }
        """
        theme = theme or ThemeManager()
        
        # Create tab frame
        tab_frame = ttk.Frame(notebook)
        tab_label = f"{icon_emoji} {tab_text}" if icon_emoji else tab_text
        notebook.add(tab_frame, text=tab_label)
        
        logger.debug(f"Created tab: {tab_text}")
        
        # Create scrollable container
        scroll_data = CanvasScrollFactory.create_scrollable_container(
            tab_frame,
            theme=theme,
            **kwargs
        )
        
        # Enable mouse wheel scrolling if handler provided
        if enable_scroll_handler:
            enable_scroll_handler(scroll_data["canvas"], scroll_data["frame"])
            logger.debug(f"Enabled mouse wheel scroll for {tab_text}")
        
        return {
            "frame": tab_frame,
            "canvas": scroll_data["canvas"],
            "scrollbar": scroll_data["scrollbar"],
            "content": scroll_data["frame"]
        }
    
    @staticmethod
    def create_tab_header(
        parent: tk.Widget,
        title: str,
        subtitle: Optional[str] = None,
        icon_emoji: str = "",
        theme: Optional[ThemeManager] = None,
        **kwargs
    ) -> Dict[str, tk.Widget]:
        """
        Create a tab header with title and subtitle
        
        Args:
            parent: Parent widget
            title: Main title
            subtitle: Optional subtitle
            icon_emoji: Emoji icon
            theme: ThemeManager
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with: {"header": Frame, "title": Label, "subtitle": Label}
        """
        theme = theme or ThemeManager()
        
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=16, pady=12)
        
        # Title with icon
        title_text = f"{icon_emoji} {title}" if icon_emoji else title
        title_label = ttk.Label(
            header_frame,
            text=title_text,
            style="Title.TLabel"
        )
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = None
        if subtitle:
            subtitle_label = ttk.Label(
                header_frame,
                text=subtitle,
                style="Caption.TLabel"
            )
            subtitle_label.pack(anchor="w")
        
        logger.debug(f"Created tab header: {title}")
        
        return {
            "header": header_frame,
            "title": title_label,
            "subtitle": subtitle_label
        }
    
    @staticmethod
    def create_tab_section(
        parent: ttk.Frame,
        title: Optional[str] = None,
        theme: Optional[ThemeManager] = None,
        fill_expand: bool = True,
        **kwargs
    ) -> ttk.Frame:
        """
        Create a section within a tab
        
        Args:
            parent: Parent frame
            title: Section title
            theme: ThemeManager
            fill_expand: Pack with fill=BOTH, expand=True
            **kwargs: Additional arguments
        
        Returns:
            Configured frame for section content
        """
        theme = theme or ThemeManager()
        
        section = ttk.Frame(parent, **kwargs)
        pack_kwargs = {}
        if fill_expand:
            pack_kwargs = {"fill": tk.BOTH, "expand": True}
        section.pack(**pack_kwargs, padx=16, pady=12)
        
        # Add title if specified
        if title:
            title_label = ttk.Label(
                section,
                text=title,
                style="Subtitle.TLabel"
            )
            title_label.pack(anchor="w", pady=(0, 8))
            
            # Add separator
            separator = ttk.Separator(section, orient=tk.HORIZONTAL)
            separator.pack(fill=tk.X, pady=(0, 8))
        
        return section
    
    @staticmethod
    def create_action_row(
        parent: tk.Widget,
        actions: List[Dict],
        theme: Optional[ThemeManager] = None,
        spacing: int = 8,
        **kwargs
    ) -> ttk.Frame:
        """
        Create a row of action buttons
        
        Args:
            parent: Parent widget
            actions: List of action dicts:
                     [{"text": "Download", "command": func, "variant": "primary"}, ...]
            theme: ThemeManager
            spacing: Space between buttons
            **kwargs: Additional arguments
        
        Returns:
            Configured action row frame
        """
        from ..factories.widget_factory import ButtonFactory
        
        action_frame = ttk.Frame(parent, **kwargs)
        action_frame.pack(fill=tk.X, padx=16, pady=8)
        
        for action in actions:
            btn = ButtonFactory.create_button(
                action_frame,
                text=action.get("text", ""),
                command=action.get("command"),
                variant=action.get("variant", "primary"),
                icon=action.get("icon"),
                width=action.get("width")
            )
            btn.pack(side=tk.LEFT, padx=(0, spacing))
        
        return action_frame
    
    @staticmethod
    def create_log_display(
        parent: tk.Widget,
        theme: Optional[ThemeManager] = None,
        height: int = 6,
        **kwargs
    ) -> Dict[str, tk.Widget]:
        """
        Create a log/text display area with scrollbar
        
        Args:
            parent: Parent widget
            theme: ThemeManager
            height: Display height in lines
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with: {"log": Text, "scrollbar": Scrollbar, "container": Frame}
        """
        from ...ui_enhanced import LogWidget  # Avoid circular import
        
        theme = theme or ThemeManager()
        
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        
        log = LogWidget(container, theme=theme, height=height, **kwargs)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=log.yview)
        
        log.config(yscrollcommand=scrollbar.set)
        log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.debug("Created log display")
        
        return {
            "log": log,
            "scrollbar": scrollbar,
            "container": container
        }


# Convenience shortcuts

def create_tab(notebook, text, theme=None, icon="", on_scroll=None):
    """Shortcut to create scrollable tab"""
    return TabFactory.create_scrollable_tab(
        notebook, text, theme, icon, on_scroll
    )


def create_tab_header(parent, title, subtitle=None, icon="", theme=None):
    """Shortcut to create tab header"""
    return TabFactory.create_tab_header(
        parent, title, subtitle, icon, theme
    )


def create_tab_section(parent, title=None, theme=None):
    """Shortcut to create tab section"""
    return TabFactory.create_tab_section(parent, title, theme)
