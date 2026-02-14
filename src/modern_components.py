"""
Modern UI Components for EasyCut
Professional, accessible, and beautiful widgets

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, List
from pathlib import Path

from design_system import ModernTheme, DesignTokens, Typography, Spacing, Icons
from icon_manager import get_ui_icon
from font_loader import LOADED_FONT_FAMILY

# Emoji fallback mapping for icons
EMOJI_ICONS = {
    "download": "⬇️",
    "upload": "⬆️",
    "search": "🔍",
    "verify": "✓",
    "settings": "⚙️",
    "folder": "📁",
    "music": "🎵",
    "video": "🎬",
    "globe": "🌐",
    "moon": "🌙",
    "sun": "☀️",
    "heart": "❤️",
    "star": "⭐",
    "check-circle": "✅",
    "x-circle": "❌",
    "clear": "✖️",
    "alert-triangle": "⚠️",
    "info": "ℹ️",
    "log-in": "🔑",
    "log-out": "🚪",
    "refresh": "🔄",
    "trash-2": "🗑️",
    "delete": "🗑️",
    "clock": "🕐",
    "history": "📜",
    "calendar": "📅",
    "github": "🐙",
    "coffee": "☕",
    "play-circle": "▶️",
    "stop-circle": "⏹️",
    "stop": "⏹️",
    "record": "⏺️",
    "circle": "⏺️",
    "radio": "📻",
    "layers": "📚",
    "batch": "📦",
    "clipboard": "📋",
    "paste": "📋",
    "external-link": "🔗",
    "sliders": "🎚️",
    "loader": "⏳",
    "theme_dark": "🌙",
    "theme_light": "☀️",
    "language": "🌐",
}


class ModernButton(ttk.Button):
    """Modern button with icon support and variants"""
    
    def __init__(self, parent, text="", icon_name=None, variant="primary", 
                 command=None, width=None, **kwargs):
        """
        Create a modern button
        
        Args:
            parent: Parent widget
            text: Button text
            icon_name: Icon name from icon_manager
            variant: "primary", "secondary", or "outline"
            command: Callback function
            width: Button width
        """
        # Load icon if specified
        self.icon = None
        emoji_prefix = ""
        
        if icon_name:
            icon_size = Icons.SIZE_SM if width and width < 15 else Icons.SIZE_MD
            try:
                self.icon = get_ui_icon(icon_name, size=icon_size)
            except:
                self.icon = None
            
            # If icon failed to load, use emoji fallback
            if not self.icon and icon_name in EMOJI_ICONS:
                emoji_prefix = EMOJI_ICONS[icon_name] + " "
        
        # Apply style variant
        style_map = {
            "primary": "TButton",
            "secondary": "Secondary.TButton",
            "outline": "Outline.TButton",
        }
        style = style_map.get(variant, "TButton")
        
        # Create button with icon or emoji
        button_text = f"{emoji_prefix}{text}"
        
        super().__init__(
            parent,
            text=button_text,
            image=self.icon if self.icon else None,
            compound="left" if self.icon else "none",
            command=command,
            width=width,
            style=style,
            **kwargs
        )
        
        # Keep reference to prevent garbage collection
        if self.icon:
            self.image = self.icon


class ModernCard(ttk.Frame):
    """Card component for grouping content"""
    
    def __init__(self, parent, title=None, padding=None, **kwargs):
        """
        Create a modern card
        
        Args:
            parent: Parent widget
            title: Optional card title
            padding: Custom padding (default: comfortable)
        """
        # Force Card.TFrame style
        if "style" not in kwargs:
            kwargs["style"] = "Card.TFrame"
        
        super().__init__(parent, **kwargs)
        
        # Use comfortable padding by default
        pad = padding or Spacing.PADDING_COMFORTABLE
        self.configure(padding=pad)
        
        # Add title if specified
        if title:
            title_label = ttk.Label(
                self,
                text=title,
                style="Subtitle.TLabel"
            )
            title_label.pack(anchor="w", pady=(0, Spacing.MD))


class ModernInput(ttk.Frame):
    """Input field with label and optional icon"""
    
    def __init__(self, parent, label=None, placeholder="", icon_name=None,
                 width=None, **kwargs):
        """
        Create a modern input field
        
        Args:
            parent: Parent widget
            label: Input label
            placeholder: Placeholder text
            icon_name: Optional icon name
            width: Entry width
        """
        super().__init__(parent)
        
        # Label
        if label:
            label_widget = ttk.Label(self, text=label)
            label_widget.pack(anchor="w", pady=(0, Spacing.XS))
        
        # Input container
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x")
        
        # Icon
        if icon_name:
            icon = get_ui_icon(icon_name, size=Icons.SIZE_SM)
            if icon:
                icon_label = ttk.Label(input_frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side="left", padx=(0, Spacing.SM))
        
        # Entry field
        self.entry = ttk.Entry(input_frame, width=width, **kwargs)
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Placeholder support
        if placeholder:
            self._placeholder = placeholder
            self._setup_placeholder()
    
    def _setup_placeholder(self):
        """Setup placeholder text"""
        self.entry.insert(0, self._placeholder)
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
    
    def _clear_placeholder(self, event):
        """Clear placeholder on focus"""
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, "end")
    
    def _restore_placeholder(self, event):
        """Restore placeholder if empty"""
        if not self.entry.get():
            self.entry.insert(0, self._placeholder)
    
    def get(self):
        """Get entry value"""
        value = self.entry.get()
        return "" if value == self._placeholder else value
    
    def set(self, value):
        """Set entry value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class ModernSwitch(ttk.Checkbutton):
    """Modern switch/toggle component"""
    
    def __init__(self, parent, text="", command=None, **kwargs):
        """
        Create a modern switch
        
        Args:
            parent: Parent widget
            text: Switch text
            command: Callback function
        """
        self.var = tk.BooleanVar()
        
        super().__init__(
            parent,
            text=text,
            variable=self.var,
            command=command,
            **kwargs
        )
    
    def get(self):
        """Get switch state"""
        return self.var.get()
    
    def set(self, value):
        """Set switch state"""
        self.var.set(value)


class ModernBadge(ttk.Label):
    """Badge component for status indicators"""
    
    def __init__(self, parent, text="", variant="default", **kwargs):
        """
        Create a badge
        
        Args:
            parent: Parent widget
            text: Badge text
            variant: "default", "success", "warning", "error", "info"
        """
        super().__init__(parent, text=text, style="Caption.TLabel", **kwargs)
        
        # Style based on variant (would need custom styling)
        self.variant = variant


class ModernAlert(tk.Frame):  # Changed from ttk.Frame to tk.Frame
    """Alert/notification component"""
    
    def __init__(self, parent, message="", variant="info", dismissible=True, **kwargs):
        """
        Create an alert
        
        Args:
            parent: Parent widget
            message: Alert message
            variant: "info", "success", "warning", "error"
            dismissible: Whether alert can be dismissed
        """
        # Get design before calling super().__init__
        design = DesignTokens()
        
        # Call super with background color to prevent style inheritance
        super().__init__(parent, bg=design.get_color("bg_primary"), **kwargs)
        self.configure(
            bg=design.get_color("bg_primary"),
            highlightthickness=0,
            relief="flat"
        )
        
        color_map = {
            "info": design.get_color("info"),           # Use theme color
            "success": design.get_color("success"),     # Use theme color
            "warning": design.get_color("warning"),     # Use theme color
            "error": design.get_color("error")          # Use theme color
        }
        
        # Emoji icons based on variant
        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        alert_color = color_map.get(variant, color_map["info"])
        
        # Colored border on the left
        border = tk.Frame(self, width=4, bg=alert_color)
        border.pack(side="left", fill="y", padx=(0, Spacing.MD))
        
        # Use tk.Frame (not ttk.Frame) to avoid inheriting ttk style colors
        content_frame = tk.Frame(self, bg=design.get_color("bg_primary"))
        content_frame.pack(fill="x", expand=True)
        
        # Emoji icon
        emoji = emoji_map.get(variant, "ℹ️")
        emoji_label = tk.Label(
            content_frame, 
            text=emoji, 
            font=("Segoe UI Emoji", 16),
            bg=design.get_color("bg_primary"),
            fg=alert_color,
            borderwidth=0
        )
        emoji_label.pack(side="left", padx=(0, Spacing.MD))
        
        # Message with color (adaptive to theme)
        msg_label = tk.Label(
            content_frame, 
            text=message,
            font=(LOADED_FONT_FAMILY, 12),
            bg=design.get_color("bg_primary"),
            fg=design.get_color("fg_primary"),
            wraplength=600,
            justify="left"
        )
        msg_label.pack(side="left", fill="x", expand=True)
        
        # Dismiss button
        if dismissible:
            dismiss_btn = tk.Label(
                content_frame,
                text="✖",
                font=("Segoe UI", 14),
                bg=design.get_color("bg_primary"),
                fg=design.get_color("fg_tertiary"),
                cursor="hand2",
                padx=Spacing.SM
            )
            dismiss_btn.pack(side="right")
            dismiss_btn.bind("<Button-1>", lambda e: self.destroy())


class ModernDialog(tk.Toplevel):
    """Modern modal dialog"""
    
    def __init__(self, parent, title="", width=500, height=None, **kwargs):
        """
        Create a modern dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width
            height: Dialog height (auto if None)
        """
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Size and position
        if height:
            self.geometry(f"{width}x{height}")
        else:
            self.geometry(f"{width}x400")
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Main container
        self.main_frame = ttk.Frame(self, padding=Spacing.PADDING_COMFORTABLE)
        self.main_frame.pack(fill="both", expand=True)
        
        # Result
        self.result = None
    
    def add_header(self, title, subtitle=None):
        """Add header to dialog"""
        header = ttk.Frame(self.main_frame)
        header.pack(fill="x", pady=(0, Spacing.XL))
        
        title_label = ttk.Label(header, text=title, style="Title.TLabel")
        title_label.pack(anchor="w")
        
        if subtitle:
            subtitle_label = ttk.Label(header, text=subtitle, style="Caption.TLabel")
            subtitle_label.pack(anchor="w", pady=(Spacing.XS, 0))
        
        return header
    
    def add_footer(self, buttons: List[Dict]):
        """
        Add footer with buttons
        
        Args:
            buttons: List of button configs [{"text": "OK", "command": func, "variant": "primary"}]
        """
        footer = ttk.Frame(self.main_frame)
        footer.pack(fill="x", pady=(Spacing.XL, 0), side="bottom")
        
        # Right-align buttons
        btn_container = ttk.Frame(footer)
        btn_container.pack(side="right")
        
        for btn_config in buttons:
            btn = ModernButton(
                btn_container,
                text=btn_config.get("text", ""),
                icon_name=btn_config.get("icon"),
                variant=btn_config.get("variant", "primary"),
                command=btn_config.get("command"),
                width=btn_config.get("width", 12)
            )
            btn.pack(side="left", padx=(Spacing.SM, 0))
        
        return footer


class ModernTooltip:
    """Tooltip component"""
    
    def __init__(self, widget, text):
        """
        Create tooltip
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    
    def show(self, event=None):
        """Show tooltip"""
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tooltip_window,
            text=self.text,
            style="Caption.TLabel",
            padding=(Spacing.SM, Spacing.XS)
        )
        label.pack()
    
    def hide(self, event=None):
        """Hide tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ModernProgressIndicator(ttk.Frame):
    """Progress indicator with label"""
    
    def __init__(self, parent, text="", maximum=100, **kwargs):
        """
        Create progress indicator
        
        Args:
            parent: Parent widget
            text: Progress label
            maximum: Maximum progress value
        """
        super().__init__(parent, **kwargs)
        
        # Label
        self.label = ttk.Label(self, text=text, style="Caption.TLabel")
        self.label.pack(anchor="w", pady=(0, Spacing.XS))
        
        # Progress bar
        self.progress = ttk.Progressbar(self, maximum=maximum, mode="determinate")
        self.progress.pack(fill="x")
        
        # Percentage label
        self.percent_label = ttk.Label(self, text="0%", style="Caption.TLabel")
        self.percent_label.pack(anchor="e", pady=(Spacing.XS, 0))
    
    def set(self, value):
        """Set progress value"""
        self.progress["value"] = value
        percent = int((value / self.progress["maximum"]) * 100)
        self.percent_label.configure(text=f"{percent}%")
    
    def set_indeterminate(self):
        """Set to indeterminate mode"""
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self.percent_label.configure(text="")
    
    def stop(self):
        """Stop indeterminate progress"""
        self.progress.stop()
        self.progress.configure(mode="determinate")


class ModernIconButton(ttk.Button):
    """Icon-only button"""
    
    def __init__(self, parent, icon_name, command=None, tooltip=None, size=Icons.SIZE_MD, **kwargs):
        """
        Create icon button
        
        Args:
            parent: Parent widget
            icon_name: Icon name
            command: Callback function
            tooltip: Tooltip text
            size: Icon size
        """
        try:
            self.icon = get_ui_icon(icon_name, size=size)
        except:
            self.icon = None
        
        # Fallback to emoji if icon failed
        button_text = ""
        if not self.icon and icon_name in EMOJI_ICONS:
            button_text = EMOJI_ICONS[icon_name]
        
        super().__init__(
            parent,
            text=button_text if not self.icon else "",
            image=self.icon if self.icon else None,
            command=command,
            width=4 if not button_text else None,
            **kwargs
        )
        
        if self.icon:
            self.image = self.icon
        
        if tooltip:
            ModernTooltip(self, tooltip)


class ModernTabHeader(tk.Frame):
    """Professional tab header with icon"""
    
    def __init__(self, parent, title, icon_name=None, subtitle=None, actions=None, **kwargs):
        """
        Create tab header
        
        Args:
            parent: Parent widget
            title: Header title
            icon_name: Optional icon
            subtitle: Optional subtitle
            actions: List of action buttons [{"icon": "name", "command": func, "tooltip": "text"}]
        """
        # Get colors from design system BEFORE super init
        design = DesignTokens()
        bg_color = design.get_color("bg_primary")
        fg_color = design.get_color("fg_primary")
        
        super().__init__(parent, bg=bg_color, **kwargs)
        self.configure(bg=bg_color, highlightthickness=0, relief="flat")
        self.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        
        # Left side (icon + text)
        left_frame = tk.Frame(self, bg=bg_color)
        left_frame.pack(side="left", fill="x", expand=True)
        
        # Icon or emoji
        if icon_name:
            try:
                icon = get_ui_icon(icon_name, size=Icons.SIZE_XL)
            except:
                icon = None
            
            if icon:
                icon_label = ttk.Label(left_frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side="left", padx=(0, Spacing.MD))
            elif icon_name in EMOJI_ICONS:
                emoji_label = tk.Label(left_frame, text=EMOJI_ICONS[icon_name], 
                                     font=("Segoe UI Emoji", 24),
                                     bg=bg_color, fg=fg_color,
                                     borderwidth=0, highlightthickness=0)
                emoji_label.pack(side="left", padx=(0, Spacing.MD))
        
        # Text
        text_frame = tk.Frame(left_frame, bg=bg_color)
        text_frame.pack(side="left", fill="x", expand=True)
        
        title_label = tk.Label(text_frame, text=title,
                              font=(LOADED_FONT_FAMILY, 24, "bold"),
                              bg=bg_color, fg=fg_color,
                              borderwidth=0, highlightthickness=0)
        title_label.pack(anchor="w")
        
        if subtitle:
            subtitle_label = tk.Label(text_frame, text=subtitle,
                                     font=(LOADED_FONT_FAMILY, 11),
                                     bg=bg_color, fg=design.get_color("fg_tertiary"),
                                     borderwidth=0, highlightthickness=0)
            subtitle_label.pack(anchor="w")
        
        # Right side (actions)
        if actions:
            right_frame = tk.Frame(self, bg=bg_color)
            right_frame.pack(side="right")
            
            for action in actions:
                btn = ModernIconButton(
                    right_frame,
                    icon_name=action.get("icon"),
                    command=action.get("command"),
                    tooltip=action.get("tooltip")
                )
                btn.pack(side="left", padx=(Spacing.SM, 0))
