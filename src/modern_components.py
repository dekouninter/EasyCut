"""
Modern UI Components for EasyCut
Professional, accessible, and beautiful widgets

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

import tkinter as tk
from tkinter import ttk

from design_system import DesignTokens, Typography, Spacing, Icons
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
    "folder-plus": "📂",
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
    "login": "🔑",
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
    """Modern button with icon support, variants, and size options"""
    
    VARIANTS = {
        "primary": "TButton",
        "secondary": "Secondary.TButton",
        "outline": "Outline.TButton",
        "ghost": "Ghost.TButton",
        "danger": "Danger.TButton",
        "danger-filled": "DangerFilled.TButton",
    }
    
    SIZE_STYLES = {
        "sm": "Small.TButton",
        "md": None,  # default
        "lg": "Large.TButton",
    }
    
    def __init__(self, parent, text="", icon_name=None, variant="primary", 
                 size="md", command=None, width=None, **kwargs):
        # Load icon if specified
        self.icon = None
        emoji_prefix = ""
        
        if icon_name:
            icon_size = Icons.SIZE_SM if size == "sm" else Icons.SIZE_MD
            try:
                self.icon = get_ui_icon(icon_name, size=icon_size)
            except:
                self.icon = None
            
            # If icon failed to load, use emoji fallback
            if not self.icon and icon_name in EMOJI_ICONS:
                emoji_prefix = EMOJI_ICONS[icon_name] + " "
        
        # Resolve style
        base_style = self.VARIANTS.get(variant, "TButton")
        style = base_style
        
        size_style = self.SIZE_STYLES.get(size)
        if size_style and variant == "primary":
            style = size_style
        
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
        
        if self.icon:
            self.image = self.icon


class ModernCard(tk.Frame):
    """Elevated card component with optional title"""
    
    def __init__(self, parent, title=None, subtitle=None, padding=None, 
                 dark_mode=None, shadow=True, **kwargs):
        if dark_mode is None:
            dark_mode = True
        self._design = DesignTokens(dark_mode=dark_mode)
        
        bg = self._design.get_color("bg_tertiary")
        border_color = self._design.get_color("border")
        
        super().__init__(parent, bg=bg, highlightbackground=border_color, 
                         highlightthickness=1, **kwargs)
        
        pad = padding or Spacing.MD
        self._inner = tk.Frame(self, bg=bg)
        self._inner.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)
        
        if title:
            fg = self._design.get_color("fg_primary")
            tk.Label(
                self._inner, text=title, bg=bg, fg=fg,
                font=(Typography.FONT_FAMILY, Typography.SIZE_H3, "bold"),
                anchor="w"
            ).pack(fill=tk.X, pady=(0, Spacing.XS))
        
        if subtitle:
            fg_sec = self._design.get_color("fg_secondary")
            tk.Label(
                self._inner, text=subtitle, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
                anchor="w"
            ).pack(fill=tk.X, pady=(0, Spacing.SM))
    
    @property
    def body(self):
        """Access the inner body frame for adding content"""
        return self._inner


class Toast(tk.Frame):
    """Single toast notification"""
    
    VARIANTS = {
        "success": {"emoji": "✅", "color_key": "success"},
        "warning": {"emoji": "⚠️", "color_key": "warning"},
        "error":   {"emoji": "❌", "color_key": "error"},
        "info":    {"emoji": "ℹ️", "color_key": "info"},
    }
    
    def __init__(self, parent, title="", message="", variant="info", 
                 duration=4000, dark_mode=True, on_dismiss=None, **kwargs):
        self._design = DesignTokens(dark_mode=dark_mode)
        bg = self._design.get_color("bg_elevated")
        border_color = self._design.get_color("border")
        
        super().__init__(parent, bg=bg, highlightbackground=border_color,
                         highlightthickness=1, **kwargs)
        
        vdata = self.VARIANTS.get(variant, self.VARIANTS["info"])
        accent = self._design.get_color(vdata["color_key"])
        fg = self._design.get_color("fg_primary")
        fg_sec = self._design.get_color("fg_secondary")
        
        # Left color bar
        tk.Frame(self, width=4, bg=accent).pack(side=tk.LEFT, fill=tk.Y)
        
        content = tk.Frame(self, bg=bg)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.SM)
        
        # Top row: emoji + title + dismiss
        top = tk.Frame(content, bg=bg)
        top.pack(fill=tk.X)
        
        tk.Label(top, text=vdata["emoji"], bg=bg, font=("Segoe UI Emoji", 12)).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        if title:
            tk.Label(
                top, text=title, bg=bg, fg=fg,
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY, "bold"),
                anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        dismiss = tk.Label(top, text="✕", bg=bg, fg=fg_sec, cursor="hand2",
                          font=(Typography.FONT_FAMILY, 10))
        dismiss.pack(side=tk.RIGHT)
        dismiss.bind("<Button-1>", lambda e: self._dismiss(on_dismiss))
        
        if message:
            tk.Label(
                content, text=message, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
                anchor="w", wraplength=280, justify="left"
            ).pack(fill=tk.X, pady=(Spacing.XS, 0))
        
        self._timer = None
        if duration > 0:
            self._timer = self.after(duration, lambda: self._dismiss(on_dismiss))
    
    def _dismiss(self, callback=None):
        if self._timer:
            try:
                self.after_cancel(self._timer)
            except Exception:
                pass
        if callback:
            callback(self)
        self.destroy()


class ToastManager:
    """Manages toast notifications — top-right of content area"""
    
    def __init__(self, parent, dark_mode=True):
        self.parent = parent
        self.dark_mode = dark_mode
        self.toasts = []
        
        self.container = tk.Frame(parent, bg="", bd=0, highlightthickness=0)
        self.container.place(relx=1.0, rely=0.0, anchor="ne", x=-Spacing.LG, y=Spacing.LG)
    
    def show(self, title="", message="", variant="info", duration=4000):
        """Show a toast notification"""
        toast = Toast(
            self.container, title=title, message=message,
            variant=variant, duration=duration,
            dark_mode=self.dark_mode,
            on_dismiss=self._on_toast_dismiss
        )
        toast.pack(fill=tk.X, pady=(0, Spacing.XS))
        self.toasts.append(toast)
        
        if len(self.toasts) > 5:
            oldest = self.toasts.pop(0)
            try:
                oldest.destroy()
            except Exception:
                pass
    
    def success(self, title, message="", duration=4000):
        self.show(title, message, "success", duration)
    
    def warning(self, title, message="", duration=4000):
        self.show(title, message, "warning", duration)
    
    def error(self, title, message="", duration=4000):
        self.show(title, message, "error", duration)
    
    def info(self, title, message="", duration=4000):
        self.show(title, message, "info", duration)
    
    def _on_toast_dismiss(self, toast):
        if toast in self.toasts:
            self.toasts.remove(toast)
