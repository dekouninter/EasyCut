# -*- coding: utf-8 -*-
"""
UI Component Factories

Provides factory functions for creating consistently-styled UI components
across the application. This eliminates code duplication and ensures
consistency throughout the app.

Usage:
    from ui.factories import ButtonFactory, FrameFactory
    
    btn = ButtonFactory.create_primary_button(parent, "Download")
    btn.pack()
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any

from ..theme import ThemeManager
from ..core.logger import get_logger

logger = get_logger(__name__)


class ButtonFactory:
    """Factory for creating consistently-styled buttons"""
    
    @staticmethod
    def create_button(
        parent: tk.Widget,
        text: str = "",
        command: Optional[Callable] = None,
        variant: str = "primary",
        icon: Optional[tk.PhotoImage] = None,
        width: Optional[int] = None,
        **kwargs
    ) -> ttk.Button:
        """
        Create a styled button
        
        Args:
            parent: Parent widget
            text: Button text
            command: Click callback
            variant: "primary", "secondary", "outline"
            icon: PhotoImage icon
            width: Button width in characters
            **kwargs: Additional ttk.Button arguments
        
        Returns:
            Configured ttk.Button
        """
        # Add default style mapping
        style_map = {
            "primary": "TButton",
            "secondary": "Secondary.TButton",
            "outline": "Outline.TButton"
        }
        
        btn_style = style_map.get(variant, "TButton")
        
        button = ttk.Button(
            parent,
            text=(text if not icon else ""),
            image=icon,
            compound="left" if icon and text else None,
            command=command,
            width=width,
            style=btn_style,
            **kwargs
        )
        
        # Keep image reference to prevent garbage collection
        if icon:
            button.image = icon
        
        return button
    
    @staticmethod
    def create_action_button(
        parent: tk.Widget,
        text: str,
        command: Callable,
        icon: Optional[tk.PhotoImage] = None,
        **kwargs
    ) -> ttk.Button:
        """Create action button (primary variant)"""
        return ButtonFactory.create_button(
            parent, text, command, variant="primary", icon=icon, **kwargs
        )
    
    @staticmethod
    def create_secondary_button(
        parent: tk.Widget,
        text: str,
        command: Callable,
        icon: Optional[tk.PhotoImage] = None,
        **kwargs
    ) -> ttk.Button:
        """Create secondary button"""
        return ButtonFactory.create_button(
            parent, text, command, variant="secondary", icon=icon, **kwargs
        )


class FrameFactory:
    """Factory for creating consistently-structured frames and containers"""
    
    @staticmethod
    def create_container(
        parent: tk.Widget,
        padding: int = 12,
        bg_color: Optional[str] = None,
        **kwargs
    ) -> ttk.Frame:
        """
        Create a container frame
        
        Args:
            parent: Parent widget
            padding: Internal padding
            bg_color: Background color
            **kwargs: Additional ttk.Frame arguments
        
        Returns:
            Configured ttk.Frame
        """
        return ttk.Frame(
            parent,
            padding=padding,
            **kwargs
        )
    
    @staticmethod
    def create_button_group(
        parent: tk.Widget,
        orientation: str = "horizontal",
        spacing: int = 8,
        **kwargs
    ) -> ttk.Frame:
        """
        Create a button group container
        
        Args:
            parent: Parent widget
            orientation: "horizontal" or "vertical"
            spacing: Space between buttons
            **kwargs: Additional arguments
        
        Returns:
            Configured frame
        """
        frame = ttk.Frame(parent, **kwargs)
        frame.pack_info = lambda side=tk.LEFT, **kw: None  # For layout tracking
        frame._orientation = orientation
        frame._spacing = spacing
        return frame
    
    @staticmethod
    def create_section(
        parent: tk.Widget,
        title: Optional[str] = None,
        theme: Optional[ThemeManager] = None,
        **kwargs
    ) -> ttk.Frame:
        """
        Create a titled section container
        
        Args:
            parent: Parent widget
            title: Section title (None = no title)
            theme: ThemeManager for colors
            **kwargs: Additional arguments
        
        Returns:
            Frame with optional title label
        """
        container = ttk.Frame(parent, **kwargs)
        
        if title:
            # Create title label
            title_label = ttk.Label(
                container,
                text=title,
                style="Subtitle.TLabel"
            )
            title_label.pack(anchor="w", pady=(0, 8))
        
        return container


class CanvasScrollFactory:
    """Factory for creating scrollable canvas containers (used in tabs)"""
    
    @staticmethod
    def create_scrollable_container(
        parent: tk.Widget,
        theme: Optional[ThemeManager] = None,
        **kwargs
    ) -> Dict[str, tk.Widget]:
        """
        Create scrollable canvas container
        
        Args:
            parent: Parent widget
            theme: ThemeManager for colors
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with: {"canvas": Canvas, "scrollbar": Scrollbar, "frame": Frame}
        """
        theme = theme or ThemeManager()
        
        # Create canvas
        canvas = tk.Canvas(
            parent,
            bg=theme.get_color("bg_primary"),
            highlightthickness=0,
            **kwargs
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=canvas.yview
        )
        
        # Create inner frame
        inner_frame = ttk.Frame(canvas)
        
        # Configure canvas
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", on_frame_configure)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.debug("Created scrollable container")
        
        return {
            "canvas": canvas,
            "scrollbar": scrollbar,
            "frame": inner_frame,
            "parent": parent
        }


class DialogFactory:
    """Factory for creating consistent dialogs"""
    
    @staticmethod
    def create_message_dialog(
        parent: tk.Widget,
        title: str,
        message: str,
        dialog_type: str = "info",
        **kwargs
    ) -> tk.Toplevel:
        """
        Create a message dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message
            dialog_type: "info", "warning", "error", "success"
            **kwargs: Additional arguments
        
        Returns:
            Configured Toplevel dialog
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Message label
        message_label = ttk.Label(
            dialog,
            text=message,
            wraplength=300
        )
        message_label.pack(padx=20, pady=20)
        
        # Close button
        close_btn = ttk.Button(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        close_btn.pack(pady=10)
        
        return dialog


class InputFactory:
    """Factory for creating input fields with consistent styling"""
    
    @staticmethod
    def create_labeled_input(
        parent: tk.Widget,
        label_text: str = "",
        placeholder: str = "",
        **kwargs
    ) -> Dict[str, tk.Widget]:
        """
        Create labeled input field
        
        Args:
            parent: Parent widget
            label_text: Label text
            placeholder: Placeholder text
            **kwargs: Additional ttk.Entry arguments
        
        Returns:
            Dictionary with: {"label": Label, "entry": Entry, "container": Frame}
        """
        container = ttk.Frame(parent)
        
        if label_text:
            label = ttk.Label(container, text=label_text)
            label.pack(anchor="w", pady=(0, 4))
        
        entry = ttk.Entry(container, **kwargs)
        entry.pack(fill=tk.X)
        
        if placeholder:
            entry.insert(0, placeholder)
        
        return {
            "container": container,
            "label": label if label_text else None,
            "entry": entry
        }


# Convenience shortcuts
def create_button(parent, text, command, **kwargs):
    """Shortcut to create primary button"""
    return ButtonFactory.create_action_button(parent, text, command, **kwargs)


def create_container(parent, **kwargs):
    """Shortcut to create container frame"""
    return FrameFactory.create_container(parent, **kwargs)


def create_scrollable(parent, theme=None, **kwargs):
    """Shortcut to create scrollable container"""
    return CanvasScrollFactory.create_scrollable_container(parent, theme, **kwargs)
