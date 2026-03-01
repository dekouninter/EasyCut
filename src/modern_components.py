"""
Modern UI Components for EasyCut v2.0
Premium, animated, accessible widget library

Provides:
- ScrollableFrame: Reusable canvas-based scrollable container
- SectionHeader: Consistent section title + subtitle + optional action
- ModernButton: Enhanced button with icon support and variants
- ModernCard: Elevated card with depth simulation and hover effects
- ModernEntry: Input with placeholder text support
- Badge: Colored tag/pill component
- Tooltip: Hover tooltip for any widget
- ToggleSwitch: Custom animated on/off switch
- AnimatedPanel: Collapsible panel with smooth animation
- Separator: Styled horizontal rule
- InfoBanner: Alert/info banner with dismiss
- IconLabel: Icon + text composite label
- EmptyState: Placeholder for empty content areas

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, List, Tuple

from design_system import (
    ModernTheme, DesignTokens, Typography, Spacing, Icons,
    Animation, ColorPalette, Elevation
)
from icon_manager import get_ui_icon
from font_loader import LOADED_FONT_FAMILY

# ── Optional: high-quality SVG icon renderer ──────────────────
try:
    from icon_renderer import (
        render_feather_icon, create_gradient_image,
        create_glow_border, clear_icon_cache
    )
    HAS_ICON_RENDERER = True
except ImportError:
    HAS_ICON_RENDERER = False
    def render_feather_icon(*a, **kw): return None
    def create_gradient_image(*a, **kw): return None
    def create_glow_border(*a, **kw): return None
    def clear_icon_cache(): pass

# ═══════════════════════════════════════════════════════════════════
#  EMOJI ICON FALLBACK MAP
# ═══════════════════════════════════════════════════════════════════

EMOJI_ICONS = {
    "download": "⬇️", "upload": "⬆️", "search": "🔍", "verify": "✓",
    "settings": "⚙️", "folder": "📁", "plus": "➕", "x": "✕",
    "check": "✓", "edit": "✏️", "delete": "🗑️", "home": "🏠",
    "menu": "☰", "play": "▶", "pause": "⏸", "stop-circle": "⏹",
    "stop": "⏹", "record": "⏺", "circle": "●", "radio": "📻",
    "layers": "📚", "batch": "📦", "clipboard": "📋", "paste": "📋",
    "external-link": "🔗", "sliders": "🎚️", "loader": "⏳",
    "theme_dark": "🌙", "theme_light": "☀️", "language": "🌐",
    "chevron-down": "▾", "chevron-right": "▸", "chevron-left": "◂",
    "chevron-up": "▴", "info": "ℹ", "alert-circle": "⚠",
    "check-circle": "✔", "x-circle": "✖", "clock": "🕐",
    "heart": "♥", "star": "★", "eye": "👁", "eye-off": "◌",
    "copy": "📄", "trash-2": "🗑", "refresh-cw": "↻", "refresh": "↻",
    "maximize-2": "⤢", "minimize-2": "⤡", "volume-2": "🔊",
    "volume-x": "🔇", "scissors": "✂", "film": "🎬",
    "monitor": "🖥", "rss": "📡", "users": "👥", "user": "👤",
    "save": "💾", "link": "🔗", "arrow-right": "→",
    "arrow-left": "←", "arrow-up": "↑", "arrow-down": "↓",
    "folder-open": "📂", "file": "📄", "music": "🎵",
    "video": "🎬", "image": "🖼", "zap": "⚡",
    # Tab / section icons
    "live": "📡", "following": "📺", "history": "📋", "about": "ℹ️",
    "clear": "✕", "donate": "☕", "github": "🔗",
}


# ═══════════════════════════════════════════════════════════════════
#  SCROLLABLE FRAME — Reusable scroll container
# ═══════════════════════════════════════════════════════════════════

class ScrollableFrame(tk.Frame):
    """Canvas-based scrollable frame. Replaces 10+ instances of scroll boilerplate.
    
    Usage:
        scroll = ScrollableFrame(parent, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        # Add widgets to scroll.interior
        tk.Label(scroll.interior, text="Content here")
    
    Scroll approach: a single global <MouseWheel> handler walks up the widget
    parent chain to find the nearest ScrollableFrame and scrolls its canvas.
    This works regardless of which child widget the mouse is over.
    """
    
    _global_bound = False  # True once the root-level handler is installed
    
    def __init__(self, parent, design: DesignTokens = None, 
                 show_scrollbar: bool = True, **kwargs):
        bg = design.get_color("bg_primary") if design else "#121418"
        super().__init__(parent, bg=bg, **kwargs)
        self._design = design
        
        # Canvas
        self.canvas = tk.Canvas(
            self, bg=bg, 
            highlightthickness=0, 
            borderwidth=0
        )
        
        # Scrollbar
        self._show_scrollbar = show_scrollbar
        if show_scrollbar:
            self.scrollbar = ttk.Scrollbar(
                self, orient=tk.VERTICAL, 
                command=self.canvas.yview
            )
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Interior frame
        self.interior = ttk.Frame(self.canvas)
        self._window_id = self.canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )
        
        # Bindings
        self.interior.bind("<Configure>", self._on_interior_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Install a single global handler the first time any ScrollableFrame is created
        if not ScrollableFrame._global_bound:
            root = self.winfo_toplevel()
            root.bind_all("<MouseWheel>", ScrollableFrame._global_scroll_handler)
            root.bind_all("<Button-4>", ScrollableFrame._global_scroll_handler)
            root.bind_all("<Button-5>", ScrollableFrame._global_scroll_handler)
            ScrollableFrame._global_bound = True
    
    @staticmethod
    def _global_scroll_handler(event):
        """Walk up the widget parent chain to find the nearest ScrollableFrame."""
        widget = event.widget
        try:
            while widget:
                if isinstance(widget, ScrollableFrame):
                    widget._on_mousewheel(event)
                    return "break"
                widget = widget.master
        except Exception:
            pass

    def _on_interior_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self._window_id, width=event.width)
    
    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(3, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-3, "units")
        return "break"
    
    def scroll_to_top(self):
        """Scroll to top of content"""
        self.canvas.yview_moveto(0)
    
    def update_colors(self, design: DesignTokens):
        """Update colors for theme change"""
        bg = design.get_color("bg_primary")
        self.configure(bg=bg)
        self.canvas.configure(bg=bg)


# ═══════════════════════════════════════════════════════════════════
#  SECTION HEADER — Consistent title + subtitle + action
# ═══════════════════════════════════════════════════════════════════

class SectionHeader(tk.Frame):
    """Section header with title, optional subtitle, and optional action widget.
    Now with SVG icons and gradient accent line.
    
    Usage:
        header = SectionHeader(parent, design=self.design,
                              title="Downloads", subtitle="Manage your downloads",
                              icon="download")
        header.pack(fill=tk.X, pady=(0, Spacing.LG))
    """
    
    # Map section names to icon colors for variety
    ICON_COLOR_MAP = {
        "download": "icon_accent",
        "layers": "icon_purple",
        "radio": "icon_red",
        "eye": "icon_cyan",
        "clipboard": "icon_orange",
        "settings": "icon_muted",
        "info": "icon_accent",
        "rss": "icon_red",
        "users": "icon_purple",
        "scissors": "icon_orange",
        "film": "icon_rose",
        "search": "icon_accent",
        "clock": "icon_cyan",
        "heart": "icon_rose",
        "star": "icon_orange",
    }
    
    def __init__(self, parent, design: DesignTokens, title: str,
                 subtitle: str = None, icon: str = None, 
                 action_widget: tk.Widget = None, 
                 gradient: bool = True, **kwargs):
        bg = design.get_color("bg_primary")
        super().__init__(parent, bg=bg, **kwargs)
        self._gradient_refs = []  # prevent GC
        
        # Left side — icon + text
        left = tk.Frame(self, bg=bg)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Title row
        title_row = tk.Frame(left, bg=bg)
        title_row.pack(fill=tk.X)
        
        icon_placed = False
        if icon and HAS_ICON_RENDERER:
            # Determine icon color from map or default to accent
            color_key = self.ICON_COLOR_MAP.get(icon, "icon_accent")
            icon_color = design.get_color(color_key)
            svg_icon = render_feather_icon(icon, size=22, color=icon_color, stroke_width=2.2)
            if svg_icon:
                icon_lbl = tk.Label(title_row, image=svg_icon, bg=bg)
                icon_lbl.pack(side=tk.LEFT, padx=(0, Spacing.SM))
                icon_lbl._icon_ref = svg_icon  # prevent GC
                icon_placed = True
        
        if not icon_placed and icon and icon in EMOJI_ICONS:
            emoji = EMOJI_ICONS[icon]
            tk.Label(
                title_row, text=emoji, bg=bg,
                fg=design.get_color("accent_primary"),
                font=("Segoe UI Emoji", Typography.SIZE_H1)
            ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        tk.Label(
            title_row, text=title, bg=bg,
            fg=design.get_color("fg_primary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold"),
            anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Subtitle
        if subtitle:
            tk.Label(
                left, text=subtitle, bg=bg,
                fg=design.get_color("fg_tertiary"),
                font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
                anchor="w"
            ).pack(fill=tk.X, pady=(Spacing.XXS, 0))
        
        # Right side — action
        if action_widget:
            action_widget.pack(side=tk.RIGHT, padx=(Spacing.MD, 0))
        
        # Bottom accent line — gradient or solid
        if gradient and HAS_ICON_RENDERER:
            # Gradient accent line (blue → purple)
            grad_start = design.get_color("accent_gradient_start")
            grad_end = design.get_color("accent_gradient_end")
            self._accent_canvas = tk.Canvas(
                self, height=2, highlightthickness=0, bg=bg
            )
            self._accent_canvas.pack(fill=tk.X, pady=(Spacing.MD, 0))
            self._accent_canvas.bind("<Configure>", lambda e: self._draw_gradient_line(
                self._accent_canvas, grad_start, grad_end, e.width
            ))
        else:
            accent_line = tk.Frame(
                self, bg=design.get_color("accent_primary"), height=2
            )
            accent_line.pack(fill=tk.X, pady=(Spacing.MD, 0))
    
    def _draw_gradient_line(self, canvas, color1, color2, width):
        """Draw a horizontal gradient line on a canvas"""
        if width < 2:
            return
        canvas.delete("all")
        grad_img = create_gradient_image(width, 2, color1, color2, "horizontal")
        if grad_img:
            canvas.create_image(0, 0, anchor="nw", image=grad_img)
            self._gradient_refs.append(grad_img)  # prevent GC
        else:
            canvas.create_rectangle(0, 0, width, 2, fill=color1, outline="")


# ═══════════════════════════════════════════════════════════════════
#  MODERN BUTTON — Enhanced with icons, variants, hover animation
# ═══════════════════════════════════════════════════════════════════

class ModernButton(ttk.Button):
    """Modern button with icon support, variants, and size options"""
    
    VARIANTS = {
        "primary": "TButton",
        "secondary": "Secondary.TButton",
        "outline": "Outline.TButton",
        "ghost": "Ghost.TButton",
        "danger": "Danger.TButton",
        "danger-filled": "DangerFilled.TButton",
        "success": "SuccessFilled.TButton",
        "purple": "PurpleFilled.TButton",
        "orange": "OrangeFilled.TButton",
        "rose": "RoseFilled.TButton",
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


# ═══════════════════════════════════════════════════════════════════
#  MODERN CARD — Elevated with depth, border glow, hover
# ═══════════════════════════════════════════════════════════════════

class ModernCard(tk.Frame):
    """Elevated card with subtle border, depth, gradient accent, and optional hover glow"""
    
    def __init__(self, parent, title=None, subtitle=None, padding=None, 
                 dark_mode=None, shadow=True, hoverable=False, 
                 accent_top=False, accent_color=None,
                 design: DesignTokens = None, **kwargs):
        # Accept shared DesignTokens or create fallback
        if design is not None:
            self._design = design
        else:
            if dark_mode is None:
                dark_mode = True
            self._design = DesignTokens(dark_mode=dark_mode)
        self._hoverable = hoverable
        self._gradient_refs = []  # prevent GC
        
        bg = self._design.get_color("bg_tertiary")
        border_color = self._design.get_color("border")
        
        super().__init__(
            parent, bg=bg, 
            highlightbackground=border_color,
            highlightthickness=1, 
            **kwargs
        )
        
        # Accent top border — gradient or solid color
        if accent_top:
            if HAS_ICON_RENDERER and not accent_color:
                # Gradient accent bar (blue → purple)
                self._accent_canvas = tk.Canvas(
                    self, height=3, highlightthickness=0, bg=bg
                )
                self._accent_canvas.pack(fill=tk.X)
                grad_start = self._design.get_color("accent_gradient_start")
                grad_end = self._design.get_color("accent_gradient_end")
                self._accent_canvas.bind("<Configure>", lambda e: self._draw_accent_gradient(
                    e.width, grad_start, grad_end
                ))
            else:
                accent_bar = tk.Frame(
                    self, bg=accent_color or self._design.get_color("accent_primary"),
                    height=3
                )
                accent_bar.pack(fill=tk.X)
        
        pad = padding or Spacing.LG
        self._inner = tk.Frame(self, bg=bg)
        self._inner.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)
        
        # Title area
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
        
        # Hover effect — with glow border
        if hoverable:
            self._bg_normal = bg
            self._bg_hover = self._design.get_color("bg_elevated")
            self._border_normal = border_color
            self._border_hover = self._design.get_color("border_glow")
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
    
    def _draw_accent_gradient(self, width, color1, color2):
        """Draw gradient accent bar"""
        if width < 2 or not hasattr(self, '_accent_canvas'):
            return
        self._accent_canvas.delete("all")
        grad_img = create_gradient_image(width, 3, color1, color2, "horizontal")
        if grad_img:
            self._accent_canvas.create_image(0, 0, anchor="nw", image=grad_img)
            self._gradient_refs.append(grad_img)
        else:
            self._accent_canvas.create_rectangle(0, 0, width, 3, fill=color1, outline="")
    
    def _on_enter(self, event=None):
        self.configure(
            bg=self._bg_hover, 
            highlightbackground=self._border_hover
        )
        self._update_children_bg(self._inner, self._bg_hover)
    
    def _on_leave(self, event=None):
        self.configure(
            bg=self._bg_normal,
            highlightbackground=self._border_normal
        )
        self._update_children_bg(self._inner, self._bg_normal)
    
    def _update_children_bg(self, widget, bg):
        """Recursively update background of children (only tk widgets)"""
        try:
            widget.configure(bg=bg)
        except (tk.TclError, AttributeError):
            pass
        for child in widget.winfo_children():
            try:
                if isinstance(child, (tk.Frame, tk.Label)):
                    child.configure(bg=bg)
            except (tk.TclError, AttributeError):
                pass
    
    @property
    def body(self):
        """Access the inner body frame for adding content"""
        return self._inner


# ═══════════════════════════════════════════════════════════════════
#  MODERN ENTRY — Input with placeholder
# ═══════════════════════════════════════════════════════════════════

class ModernEntry(ttk.Entry):
    """Entry widget with placeholder text support"""
    
    def __init__(self, parent, placeholder: str = "", 
                 placeholder_color: str = None, design: DesignTokens = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        
        self._placeholder = placeholder
        self._placeholder_color = placeholder_color or (
            design.get_color("fg_tertiary") if design else "#5E6678"
        )
        self._normal_color = design.get_color("fg_primary") if design else "#F0F2F5"
        self._has_placeholder = False
        
        if placeholder:
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)
            self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder text"""
        if not self.get():
            self._has_placeholder = True
            self.insert(0, self._placeholder)
            self.configure(foreground=self._placeholder_color)
    
    def _on_focus_in(self, event=None):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self._normal_color)
            self._has_placeholder = False
    
    def _on_focus_out(self, event=None):
        if not self.get():
            self._show_placeholder()
    
    def get_value(self) -> str:
        """Get entry value (returns '' if showing placeholder)"""
        if self._has_placeholder:
            return ""
        return self.get()
    
    def set_value(self, text: str):
        """Set entry value, clearing placeholder"""
        self._has_placeholder = False
        self.delete(0, tk.END)
        if text:
            self.insert(0, text)
            self.configure(foreground=self._normal_color)
        else:
            self._show_placeholder()


# ═══════════════════════════════════════════════════════════════════
#  BADGE — Colored tag/pill component
# ═══════════════════════════════════════════════════════════════════

class Badge(tk.Label):
    """Colored badge / pill / tag component
    
    Usage:
        Badge(parent, text="NEW", variant="blue", design=design).pack()
        Badge(parent, text="4K", variant="green", design=design).pack()
    """
    
    VARIANT_KEYS = {
        "blue":    ("tag_blue_bg", "tag_blue_fg"),
        "green":   ("tag_green_bg", "tag_green_fg"),
        "amber":   ("tag_amber_bg", "tag_amber_fg"),
        "red":     ("tag_red_bg", "tag_red_fg"),
        "orange":  ("tag_orange_bg", "tag_orange_fg"),
        "purple":  ("tag_purple_bg", "tag_purple_fg"),
        "rose":    ("tag_rose_bg", "tag_rose_fg"),
        "cyan":    ("tag_cyan_bg", "tag_cyan_fg"),
        "neutral": ("tag_neutral_bg", "tag_neutral_fg"),
    }
    
    def __init__(self, parent, text: str, variant: str = "blue",
                 design: DesignTokens = None, size: str = "md", **kwargs):
        
        bg_key, fg_key = self.VARIANT_KEYS.get(variant, ("tag_blue_bg", "tag_blue_fg"))
        bg = design.get_color(bg_key) if design else "#1E2E4A"
        fg = design.get_color(fg_key) if design else "#60A5FA"
        
        font_size = Typography.SIZE_TINY if size == "sm" else Typography.SIZE_CAPTION
        padx = Spacing.SM if size == "sm" else Spacing.MD
        pady = Spacing.XXS if size == "sm" else Spacing.XS
        
        super().__init__(
            parent, text=text, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, font_size, "bold"),
            padx=padx, pady=pady, **kwargs
        )


# ═══════════════════════════════════════════════════════════════════
#  TOOLTIP — Hover tooltip for any widget
# ═══════════════════════════════════════════════════════════════════

class Tooltip:
    """Hover tooltip that appears after a short delay
    
    Usage:
        btn = ModernButton(parent, text="Save")
        Tooltip(btn, text="Save current settings", design=self.design)
    """
    
    def __init__(self, widget: tk.Widget, text: str, 
                 design: DesignTokens = None, delay: int = 500):
        self.widget = widget
        self.text = text
        self.design = design
        self.delay = delay
        self.tooltip_window = None
        self._after_id = None
        
        widget.bind("<Enter>", self._schedule_show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<Button-1>", self._hide, add="+")
    
    def _schedule_show(self, event=None):
        self._after_id = self.widget.after(self.delay, self._show)
    
    def _show(self):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        
        bg = self.design.get_color("bg_elevated") if self.design else "#252A34"
        fg = self.design.get_color("fg_primary") if self.design else "#F0F2F5"
        border = self.design.get_color("border_glow") if self.design else "#2A3870"
        accent = self.design.get_color("purple_primary") if self.design else "#8B5CF6"
        
        # Outer frame with accent border
        outer = tk.Frame(tw, bg=border)
        outer.pack()
        
        inner = tk.Frame(outer, bg=bg)
        inner.pack(padx=1, pady=1)
        
        # Tiny accent bar at top of tooltip
        tk.Frame(inner, bg=accent, height=2).pack(fill=tk.X)
        
        label = tk.Label(
            inner, text=self.text, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            padx=Spacing.SM, pady=Spacing.XS,
            wraplength=300
        )
        label.pack()
        
        # Center horizontally
        tw.update_idletasks()
        tw_width = tw.winfo_width()
        tw.wm_geometry(f"+{x - tw_width // 2}+{y}")
    
    def _hide(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# ═══════════════════════════════════════════════════════════════════
#  TOGGLE SWITCH — Custom animated on/off switch
# ═══════════════════════════════════════════════════════════════════

class ToggleSwitch(tk.Canvas):
    """Animated toggle switch component
    
    Usage:
        switch = ToggleSwitch(parent, design=self.design, 
                             command=on_toggle_change)
        switch.pack()
        switch.set(True)
    """
    
    WIDTH = 44
    HEIGHT = 24
    KNOB_RADIUS = 9
    PADDING = 3
    
    def __init__(self, parent, design: DesignTokens = None,
                 command: Callable = None, initial: bool = False, **kwargs):
        self._design = design or DesignTokens(dark_mode=True)
        bg = self._design.get_color("bg_primary")
        
        super().__init__(
            parent, width=self.WIDTH, height=self.HEIGHT,
            bg=bg, highlightthickness=0, cursor="hand2",
            **kwargs
        )
        
        self._is_on = initial
        self._command = command
        self._anim_progress = 1.0 if initial else 0.0
        self._animating = False
        
        self.bind("<Button-1>", self._toggle)
        self._draw()
    
    def _draw(self):
        """Draw the switch at current animation progress"""
        self.delete("all")
        
        t = self._anim_progress
        
        # Colors
        off_bg = self._design.get_color("bg_hover")
        on_bg = self._design.get_color("accent_primary")
        knob_color = self._design.get_color("fg_on_accent")
        
        # Interpolate track color
        track_color = Animation.interpolate_color(off_bg, on_bg, t)
        
        # Track (rounded rectangle via ovals + rectangle)
        r = self.HEIGHT // 2
        self.create_oval(0, 0, self.HEIGHT, self.HEIGHT, fill=track_color, outline="")
        self.create_oval(self.WIDTH - self.HEIGHT, 0, self.WIDTH, self.HEIGHT, fill=track_color, outline="")
        self.create_rectangle(r, 0, self.WIDTH - r, self.HEIGHT, fill=track_color, outline="")
        
        # Knob position
        knob_x_off = self.PADDING + self.KNOB_RADIUS
        knob_x_on = self.WIDTH - self.PADDING - self.KNOB_RADIUS
        knob_x = knob_x_off + (knob_x_on - knob_x_off) * t
        knob_y = self.HEIGHT // 2
        
        # Knob shadow
        self.create_oval(
            knob_x - self.KNOB_RADIUS + 1,
            knob_y - self.KNOB_RADIUS + 1,
            knob_x + self.KNOB_RADIUS + 1,
            knob_y + self.KNOB_RADIUS + 1,
            fill=self._design.get_color("shadow_sm"),
            outline=""
        )
        
        # Knob
        self.create_oval(
            knob_x - self.KNOB_RADIUS,
            knob_y - self.KNOB_RADIUS,
            knob_x + self.KNOB_RADIUS,
            knob_y + self.KNOB_RADIUS,
            fill=knob_color,
            outline=""
        )
    
    def _toggle(self, event=None):
        """Toggle the switch with animation"""
        self._is_on = not self._is_on
        self._animate()
        if self._command:
            self._command(self._is_on)
    
    def _animate(self):
        """Animate the toggle transition"""
        if self._animating:
            return
        self._animating = True
        self._anim_start = 0.0 if self._is_on else 1.0
        self._anim_end = 1.0 if self._is_on else 0.0
        self._anim_time = 0
        self._anim_step()
    
    def _anim_step(self):
        """Single animation frame"""
        duration = Animation.NORMAL  # 200ms
        self._anim_time += Animation.FRAME_MS
        t = min(self._anim_time / duration, 1.0)
        eased = Animation.ease_out_cubic(t)
        
        self._anim_progress = self._anim_start + (self._anim_end - self._anim_start) * eased
        self._draw()
        
        if t < 1.0:
            self.after(Animation.FRAME_MS, self._anim_step)
        else:
            self._animating = False
    
    def set(self, value: bool, animate: bool = False):
        """Set switch value"""
        if value != self._is_on:
            self._is_on = value
            if animate:
                self._animate()
            else:
                self._anim_progress = 1.0 if value else 0.0
                self._draw()
    
    def get(self) -> bool:
        """Get current switch value"""
        return self._is_on


# ═══════════════════════════════════════════════════════════════════
#  ANIMATED PANEL — Collapsible with smooth animation
# ═══════════════════════════════════════════════════════════════════

class AnimatedPanel(tk.Frame):
    """Collapsible panel with smooth height animation
    
    Usage:
        panel = AnimatedPanel(parent, design=self.design,
                             title="Advanced Settings")
        panel.pack(fill=tk.X)
        # Add content to panel.content_frame
        tk.Label(panel.content_frame, text="Setting 1").pack()
    """
    
    def __init__(self, parent, design: DesignTokens, title: str,
                 initially_open: bool = False, icon: str = None, **kwargs):
        bg = design.get_color("bg_tertiary")
        super().__init__(parent, bg=bg, **kwargs)
        
        self._design = design
        self._is_open = initially_open
        self._target_height = 0
        self._animating = False
        
        # Header (clickable)
        header_bg = design.get_color("bg_tertiary")
        header_fg = design.get_color("fg_primary")
        self._header = tk.Frame(self, bg=header_bg, cursor="hand2")
        self._header.pack(fill=tk.X)
        
        # Chevron indicator
        self._chevron = tk.Label(
            self._header, text="▸" if not initially_open else "▾",
            bg=header_bg, fg=design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY)
        )
        self._chevron.pack(side=tk.LEFT, padx=(Spacing.MD, Spacing.SM))
        
        # Icon
        if icon and icon in EMOJI_ICONS:
            tk.Label(
                self._header, text=EMOJI_ICONS[icon],
                bg=header_bg, fg=design.get_color("accent_primary"),
                font=("Segoe UI Emoji", Typography.SIZE_BODY)
            ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Title
        tk.Label(
            self._header, text=title, bg=header_bg, fg=header_fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY, "bold"),
            anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=Spacing.SM)
        
        # Hover effect
        hover_bg = design.get_color("bg_hover")
        for w in [self._header, self._chevron]:
            w.bind("<Enter>", lambda e, hbg=hover_bg: self._set_header_bg(hbg))
            w.bind("<Leave>", lambda e, nbg=header_bg: self._set_header_bg(nbg))
            w.bind("<Button-1>", lambda e: self.toggle())
        
        # Content frame
        self.content_frame = tk.Frame(self, bg=bg)
        if initially_open:
            self.content_frame.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.MD))
    
    def _set_header_bg(self, bg):
        self._header.configure(bg=bg)
        for child in self._header.winfo_children():
            try:
                child.configure(bg=bg)
            except (tk.TclError, AttributeError):
                pass
    
    def toggle(self):
        """Toggle panel open/closed"""
        self._is_open = not self._is_open
        
        if self._is_open:
            self._chevron.configure(text="▾")
            self.content_frame.pack(
                fill=tk.X, padx=Spacing.MD, 
                pady=(0, Spacing.MD)
            )
        else:
            self._chevron.configure(text="▸")
            self.content_frame.pack_forget()
    
    @property
    def is_open(self):
        return self._is_open


# ═══════════════════════════════════════════════════════════════════
#  SEPARATOR — Styled horizontal rule
# ═══════════════════════════════════════════════════════════════════

class Separator(tk.Frame):
    """Styled separator / horizontal rule
    
    Usage:
        Separator(parent, design=self.design).pack(fill=tk.X, pady=Spacing.LG)
    """
    
    def __init__(self, parent, design: DesignTokens = None, 
                 color: str = None, height: int = 1, **kwargs):
        bg = color or (design.get_color("border_subtle") if design else "#181B20")
        super().__init__(parent, bg=bg, height=height, **kwargs)


# ═══════════════════════════════════════════════════════════════════
#  INFO BANNER — Alert/notification banner
# ═══════════════════════════════════════════════════════════════════

class InfoBanner(tk.Frame):
    """Alert/info banner with icon, message, and optional dismiss
    
    Usage:
        banner = InfoBanner(parent, text="New version available!", 
                           variant="info", design=self.design, dismissible=True)
        banner.pack(fill=tk.X)
    """
    
    VARIANT_CONFIG = {
        "info":    ("info", "info_bg", "ℹ"),
        "success": ("success", "success_bg", "✓"),
        "warning": ("warning", "warning_bg", "⚠"),
        "error":   ("error", "error_bg", "✖"),
    }
    
    def __init__(self, parent, text: str, variant: str = "info",
                 design: DesignTokens = None, dismissible: bool = False,
                 **kwargs):
        fg_key, bg_key, icon = self.VARIANT_CONFIG.get(variant, ("info", "info_bg", "ℹ"))
        
        bg = design.get_color(bg_key) if design else "#15202E"
        fg = design.get_color(fg_key) if design else "#60A5FA"
        
        super().__init__(parent, bg=bg, **kwargs)
        
        # Colored left accent border
        tk.Frame(self, bg=fg, width=3).pack(side=tk.LEFT, fill=tk.Y)
        
        inner = tk.Frame(self, bg=bg)
        inner.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)
        
        # Icon
        tk.Label(
            inner, text=icon, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Message
        tk.Label(
            inner, text=text, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_SMALL),
            anchor="w", wraplength=600
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dismiss button
        if dismissible:
            dismiss_btn = tk.Label(
                inner, text="✕", bg=bg, fg=fg,
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                cursor="hand2"
            )
            dismiss_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
            dismiss_btn.bind("<Button-1>", lambda e: self.destroy())


# ═══════════════════════════════════════════════════════════════════
#  ICON LABEL — Icon + text composite
# ═══════════════════════════════════════════════════════════════════

class IconLabel(tk.Frame):
    """Icon (SVG or emoji) + text label, commonly used for metadata display
    
    Usage:
        IconLabel(parent, icon="clock", text="2h 30m", design=self.design).pack()
    """
    
    def __init__(self, parent, icon: str, text: str, 
                 design: DesignTokens = None, fg_color: str = None,
                 icon_color_key: str = None, font_size: int = None, **kwargs):
        bg = design.get_color("bg_primary") if design else "#121418"
        fg = fg_color or (design.get_color("fg_secondary") if design else "#9BA3B2")
        
        super().__init__(parent, bg=bg, **kwargs)
        self._icon_ref = None  # prevent GC
        
        size = font_size or Typography.SIZE_BODY
        
        # Try SVG icon first
        icon_placed = False
        if HAS_ICON_RENDERER and icon:
            i_color = design.get_color(icon_color_key) if icon_color_key and design else (
                design.get_color("icon_muted") if design else fg
            )
            svg_icon = render_feather_icon(icon, size=size + 2, color=i_color)
            if svg_icon:
                lbl = tk.Label(self, image=svg_icon, bg=bg)
                lbl.pack(side=tk.LEFT, padx=(0, Spacing.XS))
                lbl._icon_ref = svg_icon
                self._icon_ref = svg_icon
                icon_placed = True
        
        if not icon_placed:
            emoji = EMOJI_ICONS.get(icon, icon)
            tk.Label(
                self, text=emoji, bg=bg, fg=design.get_color("icon_muted") if design else fg,
                font=("Segoe UI Emoji", size)
            ).pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        self.text_label = tk.Label(
            self, text=text, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, size),
            anchor="w"
        )
        self.text_label.pack(side=tk.LEFT)
    
    def set_text(self, text: str):
        """Update the text"""
        self.text_label.configure(text=text)


# ═══════════════════════════════════════════════════════════════════
#  EMPTY STATE — Placeholder for empty content areas
# ═══════════════════════════════════════════════════════════════════

class EmptyState(tk.Frame):
    """Empty state placeholder with icon, title, and description
    
    Usage:
        EmptyState(parent, design=self.design,
                  icon="inbox", title="No downloads yet",
                  description="Paste a URL above to get started")
    """
    
    def __init__(self, parent, design: DesignTokens, 
                 icon: str = None, title: str = "", 
                 description: str = "", action_text: str = None,
                 action_command: Callable = None, **kwargs):
        bg = design.get_color("bg_primary")
        super().__init__(parent, bg=bg, **kwargs)
        
        container = tk.Frame(self, bg=bg)
        container.pack(expand=True, pady=Spacing.XXXL)
        
        # Large icon
        if icon:
            emoji = EMOJI_ICONS.get(icon, icon)
            tk.Label(
                container, text=emoji, bg=bg,
                fg=design.get_color("fg_tertiary"),
                font=("Segoe UI Emoji", 36)
            ).pack(pady=(0, Spacing.LG))
        
        # Title
        if title:
            tk.Label(
                container, text=title, bg=bg,
                fg=design.get_color("fg_secondary"),
                font=(Typography.FONT_FAMILY, Typography.SIZE_H2, "bold"),
                anchor="center"
            ).pack(pady=(0, Spacing.SM))
        
        # Description
        if description:
            tk.Label(
                container, text=description, bg=bg,
                fg=design.get_color("fg_tertiary"),
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                anchor="center", wraplength=350
            ).pack(pady=(0, Spacing.LG))
        
        # Action button
        if action_text and action_command:
            ModernButton(
                container, text=action_text, 
                command=action_command, variant="outline"
            ).pack()


# ═══════════════════════════════════════════════════════════════════
#  HOVER FRAME — Frame with hover background change
# ═══════════════════════════════════════════════════════════════════

class HoverFrame(tk.Frame):
    """Frame that changes background color on hover — for clickable items.
    Also updates all direct children backgrounds on hover.
    
    Usage:
        item = HoverFrame(parent, design=self.design,
                         normal_bg="bg_secondary", hover_bg="bg_hover",
                         cursor="hand2")
    """
    
    def __init__(self, parent, design: DesignTokens,
                 normal_bg: str = "bg_secondary", hover_bg: str = "bg_hover",
                 on_click: Callable = None, **kwargs):
        self._normal_bg = design.get_color(normal_bg)
        self._hover_bg = design.get_color(hover_bg)
        self._design = design
        self._on_click = on_click
        
        super().__init__(parent, bg=self._normal_bg, **kwargs)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        if on_click:
            self.bind("<Button-1>", lambda e: on_click())
    
    def _on_enter(self, event=None):
        self.configure(bg=self._hover_bg)
        for child in self.winfo_children():
            try:
                child.configure(bg=self._hover_bg)
            except (tk.TclError, AttributeError):
                pass
    
    def _on_leave(self, event=None):
        self.configure(bg=self._normal_bg)
        for child in self.winfo_children():
            try:
                child.configure(bg=self._normal_bg)
            except (tk.TclError, AttributeError):
                pass
    
    def set_active(self, active: bool):
        """Set this frame as active (persistent highlight)"""
        if active:
            bg = self._design.get_color("sidebar_item_active")
        else:
            bg = self._normal_bg
        self.configure(bg=bg)
        for child in self.winfo_children():
            try:
                child.configure(bg=bg)
            except (tk.TclError, AttributeError):
                pass


# ═══════════════════════════════════════════════════════════════════
#  PROGRESS RING — Circular progress indicator (Canvas-based)
# ═══════════════════════════════════════════════════════════════════

class ProgressRing(tk.Canvas):
    """Circular progress indicator drawn on Canvas
    
    Usage:
        ring = ProgressRing(parent, design=self.design, size=60)
        ring.pack()
        ring.set_progress(0.75)  # 75%
    """
    
    def __init__(self, parent, design: DesignTokens = None,
                 size: int = 48, thickness: int = 4,
                 show_text: bool = True, accent_color: str = None, **kwargs):
        
        bg = design.get_color("bg_primary") if design else "#121418"
        super().__init__(
            parent, width=size, height=size,
            bg=bg, highlightthickness=0, **kwargs
        )
        
        self._design = design
        self._size = size
        self._thickness = thickness
        self._show_text = show_text
        self._progress = 0.0
        self._accent_color = accent_color  # e.g. "purple_primary", "orange_primary"
        
        self._draw()
    
    def _draw(self):
        """Draw the progress ring"""
        self.delete("all")
        
        s = self._size
        t = self._thickness
        pad = t // 2 + 2
        
        # Track (full circle)
        track_color = self._design.get_color("bg_tertiary") if self._design else "#1E222A"
        self.create_oval(
            pad, pad, s - pad, s - pad,
            outline=track_color, width=t
        )
        
        # Progress arc
        if self._progress > 0:
            if self._accent_color and self._design:
                accent = self._design.get_color(self._accent_color)
            else:
                accent = self._design.get_color("accent_primary") if self._design else "#4C8BF5"
            extent = -360 * self._progress  # Negative = clockwise
            self.create_arc(
                pad, pad, s - pad, s - pad,
                start=90, extent=extent,
                outline=accent, width=t, style="arc"
            )
        
        # Center text
        if self._show_text:
            fg = self._design.get_color("fg_primary") if self._design else "#F0F2F5"
            pct = int(self._progress * 100)
            self.create_text(
                s // 2, s // 2, text=f"{pct}%",
                fill=fg, font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION, "bold")
            )
    
    def set_progress(self, value: float):
        """Set progress value (0.0 to 1.0)"""
        self._progress = max(0.0, min(1.0, value))
        self._draw()


# ═══════════════════════════════════════════════════════════════════
#  ANIMATED COUNTER — Smooth number counting animation
# ═══════════════════════════════════════════════════════════════════

class AnimatedCounter(tk.Label):
    """Label that smoothly animates between number values
    
    Usage:
        counter = AnimatedCounter(parent, design=self.design, prefix="Downloads: ")
        counter.pack()
        counter.set_value(42)  # Animates from 0 to 42
    """
    
    def __init__(self, parent, design: DesignTokens = None,
                 prefix: str = "", suffix: str = "",
                 font_size: int = None, weight: str = "bold", **kwargs):
        
        bg = design.get_color("bg_primary") if design else "#121418"
        fg = kwargs.pop("fg", design.get_color("fg_primary") if design else "#F0F2F5")
        size = font_size or Typography.SIZE_H2
        
        super().__init__(
            parent, text=f"{prefix}0{suffix}", bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, size, weight),
            **kwargs
        )
        
        self._prefix = prefix
        self._suffix = suffix
        self._current = 0
        self._target = 0
        self._animating = False
    
    def set_value(self, value: int, animate: bool = True):
        """Set counter value with optional animation"""
        self._target = value
        if animate and value != self._current:
            self._animate_start = self._current
            self._anim_time = 0
            if not self._animating:
                self._animating = True
                self._anim_step()
        else:
            self._current = value
            self.configure(text=f"{self._prefix}{value}{self._suffix}")
    
    def _anim_step(self):
        duration = Animation.SMOOTH  # 300ms
        self._anim_time += Animation.FRAME_MS
        t = min(self._anim_time / duration, 1.0)
        eased = Animation.ease_out_cubic(t)
        
        self._current = int(self._animate_start + (self._target - self._animate_start) * eased)
        self.configure(text=f"{self._prefix}{self._current}{self._suffix}")
        
        if t < 1.0:
            self.after(Animation.FRAME_MS, self._anim_step)
        else:
            self._current = self._target
            self.configure(text=f"{self._prefix}{self._target}{self._suffix}")
            self._animating = False
