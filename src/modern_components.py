"""
Modern UI Components for EasyCut v2.0
Professional, accessible, and beautiful widgets

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.4.0
"""

import tkinter as tk
from tkinter import ttk

from design_system import DesignTokens, Typography, Spacing, Icons
from icon_manager import get_ui_icon
from font_loader import LOADED_FONT_FAMILY

# ════════════════════════════════════════════════
# EMOJI FALLBACK MAP
# ════════════════════════════════════════════════

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
    "save": "💾",
    "copy": "📋",
    "edit": "✏️",
    "plus": "➕",
    "minus": "➖",
    "chevron-right": "›",
    "chevron-down": "⌄",
    "maximize": "⬜",
    "minimize": "▬",
}


# ════════════════════════════════════════════════
# MODERN BUTTON
# ════════════════════════════════════════════════

class ModernButton(ttk.Button):
    """Modern button with icon support, variants, and size options"""
    
    VARIANTS = {
        "primary": "TButton",
        "secondary": "Secondary.TButton",
        "outline": "Outline.TButton",
        "ghost": "Ghost.TButton",
        "danger": "Danger.TButton",
        "danger-filled": "DangerFilled.TButton",
        "success": "Success.TButton",
    }
    
    SIZE_STYLES = {
        "sm": "Small.TButton",
        "md": None,
        "lg": "Large.TButton",
    }
    
    def __init__(self, parent, text="", icon_name=None, variant="primary", 
                 size="md", command=None, width=None, **kwargs):
        self.icon = None
        emoji_prefix = ""
        
        if icon_name:
            icon_size = Icons.SIZE_SM if size == "sm" else Icons.SIZE_MD
            try:
                self.icon = get_ui_icon(icon_name, size=icon_size)
            except Exception:
                self.icon = None
            
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


# ════════════════════════════════════════════════
# SECTION HEADER — Page title with accent underline
# ════════════════════════════════════════════════

class SectionHeader(tk.Frame):
    """Section header with title, subtitle, and accent underline"""
    
    def __init__(self, parent, title="", subtitle="", dark_mode=True, **kwargs):
        self._design = DesignTokens(dark_mode=dark_mode)
        bg = self._design.get_color("bg_primary")
        
        super().__init__(parent, bg=bg, **kwargs)
        
        fg = self._design.get_color("fg_primary")
        fg_sec = self._design.get_color("fg_secondary")
        accent = self._design.get_color("accent_primary")
        
        # Title
        tk.Label(
            self, text=title, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold"),
            anchor="w"
        ).pack(fill=tk.X)
        
        # Subtitle
        if subtitle:
            tk.Label(
                self, text=subtitle, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
                anchor="w"
            ).pack(fill=tk.X, pady=(2, 0))
        
        # Accent underline — short bar
        underline_container = tk.Frame(self, bg=bg)
        underline_container.pack(fill=tk.X, pady=(Spacing.SM, 0))
        tk.Frame(
            underline_container, bg=accent, height=3, width=48
        ).pack(anchor="w")


# ════════════════════════════════════════════════
# MODERN CARD — Elevated with optional accent top border
# ════════════════════════════════════════════════

class ModernCard(tk.Frame):
    """Elevated card component with optional accent top border"""
    
    def __init__(self, parent, title=None, subtitle=None, padding=None,
                 dark_mode=None, accent_color=None, **kwargs):
        if dark_mode is None:
            dark_mode = True
        self._design = DesignTokens(dark_mode=dark_mode)
        
        bg = self._design.get_color("bg_tertiary")
        border_color = self._design.get_color("border")
        
        super().__init__(parent, bg=bg, highlightbackground=border_color,
                         highlightthickness=1, **kwargs)
        
        # Accent top border (colored strip at top of card)
        if accent_color:
            tk.Frame(self, bg=accent_color, height=3).pack(fill=tk.X)
        
        pad = padding or Spacing.CARD_PADDING
        self._inner = tk.Frame(self, bg=bg)
        self._inner.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)
        
        if title:
            fg = self._design.get_color("fg_primary")
            title_frame = tk.Frame(self._inner, bg=bg)
            title_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
            
            tk.Label(
                title_frame, text=title, bg=bg, fg=fg,
                font=(Typography.FONT_FAMILY, Typography.SIZE_H3, "bold"),
                anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X)
        
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


# ════════════════════════════════════════════════
# STATUS DOT — Colored indicator dot
# ════════════════════════════════════════════════

class StatusDot(tk.Canvas):
    """Small colored dot indicator (e.g., online/offline/busy)"""
    
    COLORS = {
        "online":  "#4ADE80",
        "offline": "#5C6278",
        "busy":    "#F87171",
        "warning": "#FBBF24",
        "info":    "#60A5FA",
        "accent":  "#6C8EEF",
    }
    
    def __init__(self, parent, status="offline", size=10, dark_mode=None, **kwargs):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, **kwargs)
        self._size = size
        self.set_status(status)
    
    def set_status(self, status):
        """Update dot color by status name or hex color"""
        color = self.COLORS.get(status, status)
        self.delete("all")
        pad = 1
        self.create_oval(pad, pad, self._size - pad, self._size - pad,
                         fill=color, outline="")


# ════════════════════════════════════════════════
# TOOLTIP — Hover tooltip for any widget
# ════════════════════════════════════════════════

class Tooltip:
    """Hover tooltip that appears near a widget"""
    
    def __init__(self, widget, text, delay=500, dark_mode=True):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._design = DesignTokens(dark_mode=dark_mode)
        self._tip_window = None
        self._timer = None
        
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._cancel, add="+")
        widget.bind("<ButtonPress>", self._cancel, add="+")
    
    def _schedule(self, event=None):
        self._cancel()
        self._timer = self.widget.after(self.delay, self._show)
    
    def _cancel(self, event=None):
        if self._timer:
            self.widget.after_cancel(self._timer)
            self._timer = None
        self._hide()
    
    def _show(self):
        if self._tip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        bg = self._design.get_color("bg_elevated")
        fg = self._design.get_color("fg_primary")
        border = self._design.get_color("border_hover")
        
        self._tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Tooltip frame
        frame = tk.Frame(tw, bg=bg, highlightbackground=border,
                         highlightthickness=1)
        frame.pack()
        
        tk.Label(
            frame, text=self.text, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            padx=Spacing.SM, pady=Spacing.XS,
            justify=tk.LEFT, wraplength=250
        ).pack()
    
    def _hide(self):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


# ════════════════════════════════════════════════
# BADGE — Pill-shaped status label
# ════════════════════════════════════════════════

class Badge(tk.Label):
    """Pill-shaped badge/tag label"""
    
    PRESETS = {
        "success":  {"bg": "#132B1F", "fg": "#4ADE80"},
        "warning":  {"bg": "#2B2211", "fg": "#FBBF24"},
        "error":    {"bg": "#2B1515", "fg": "#F87171"},
        "info":     {"bg": "#15202B", "fg": "#60A5FA"},
        "accent":   {"bg": "#1A1E38", "fg": "#6C8EEF"},
        "neutral":  {"bg": "#262A38", "fg": "#8B92A8"},
    }
    
    def __init__(self, parent, text="", preset="neutral", **kwargs):
        colors = self.PRESETS.get(preset, self.PRESETS["neutral"])
        
        super().__init__(
            parent, text=f"  {text}  ",
            bg=colors["bg"], fg=colors["fg"],
            font=(Typography.FONT_FAMILY, Typography.SIZE_TINY, "bold"),
            padx=Spacing.SM, pady=2,
            **kwargs
        )


# ════════════════════════════════════════════════
# DIVIDER — Horizontal divider with optional label
# ════════════════════════════════════════════════

class Divider(tk.Frame):
    """Horizontal divider line with optional centered label"""
    
    def __init__(self, parent, text=None, dark_mode=True, **kwargs):
        self._design = DesignTokens(dark_mode=dark_mode)
        bg = self._design.get_color("bg_primary")
        border = self._design.get_color("border")
        
        super().__init__(parent, bg=bg, **kwargs)
        
        if text:
            fg_sec = self._design.get_color("fg_tertiary")
            # Line — label — line
            tk.Frame(self, bg=border, height=1).pack(
                side=tk.LEFT, fill=tk.X, expand=True, pady=Spacing.SM
            )
            tk.Label(
                self, text=f"  {text}  ", bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
            ).pack(side=tk.LEFT)
            tk.Frame(self, bg=border, height=1).pack(
                side=tk.LEFT, fill=tk.X, expand=True, pady=Spacing.SM
            )
        else:
            tk.Frame(self, bg=border, height=1).pack(
                fill=tk.X, pady=Spacing.SM
            )


# ════════════════════════════════════════════════
# TOAST — Notification system
# ════════════════════════════════════════════════

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
        border_color = self._design.get_color("border_hover")
        
        super().__init__(parent, bg=bg, highlightbackground=border_color,
                         highlightthickness=1, **kwargs)
        
        vdata = self.VARIANTS.get(variant, self.VARIANTS["info"])
        accent = self._design.get_color(vdata["color_key"])
        fg = self._design.get_color("fg_primary")
        fg_sec = self._design.get_color("fg_secondary")
        
        # Left color bar (accent stripe)
        tk.Frame(self, width=4, bg=accent).pack(side=tk.LEFT, fill=tk.Y)
        
        content = tk.Frame(self, bg=bg)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.SM)
        
        # Top row: emoji + title + dismiss
        top = tk.Frame(content, bg=bg)
        top.pack(fill=tk.X)
        
        tk.Label(
            top, text=vdata["emoji"], bg=bg,
            font=(Typography.FONT_EMOJI, 12)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        if title:
            tk.Label(
                top, text=title, bg=bg, fg=fg,
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY, "bold"),
                anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        dismiss = tk.Label(
            top, text="✕", bg=bg, fg=fg_sec, cursor="hand2",
            font=(Typography.FONT_FAMILY, 10)
        )
        dismiss.pack(side=tk.RIGHT)
        dismiss.bind("<Button-1>", lambda e: self._dismiss(on_dismiss))
        
        if message:
            tk.Label(
                content, text=message, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
                anchor="w", wraplength=300, justify="left"
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
