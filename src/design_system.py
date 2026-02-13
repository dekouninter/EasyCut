"""
EasyCut Design System
Modern, Clean, Professional UI Design Tokens

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

from pathlib import Path
from typing import Dict, Tuple
import tkinter.font as tkfont


class ColorPalette:
    """Modern color palette with accessibility in mind"""
    
    # === DARK THEME - Deep, Rich Colors ===
    DARK = {
        # Backgrounds
        "bg_primary": "#0A0E27",          # Deep navy blue
        "bg_secondary": "#131829",        # Slightly lighter navy
        "bg_tertiary": "#1A1F3A",         # Card/panel background
        "bg_elevated": "#20264D",         # Elevated elements
        "bg_hover": "#252B54",            # Hover state
        
        # Foregrounds
        "fg_primary": "#E8EAED",          # Main text
        "fg_secondary": "#A8B1D6",        # Secondary text
        "fg_tertiary": "#6B7AA8",         # Tertiary text
        "fg_disabled": "#4A5578",         # Disabled text
        
        # Accents & Semantics
        "accent_primary": "#5B8CFF",      # Primary blue
        "accent_secondary": "#7B9FFF",    # Lighter blue
        "accent_hover": "#4A7AEE",        # Hover blue
        
        "success": "#10B981",             # Green
        "success_bg": "#064E3B",          # Success background
        "warning": "#F59E0B",             # Amber
        "warning_bg": "#78350F",          # Warning background
        "error": "#EF4444",               # Red
        "error_bg": "#7F1D1D",            # Error background
        "info": "#3B82F6",                # Blue
        "info_bg": "#1E3A8A",             # Info background
        
        # UI Elements
        "border": "#2D3555",              # Default border
        "border_focus": "#5B8CFF",        # Focused border
        "border_hover": "#384071",        # Hover border
        
        "shadow": "rgba(0, 0, 0, 0.5)",   # Shadow color
        "overlay": "rgba(10, 14, 39, 0.95)",  # Modal overlay
    }
    
    # === LIGHT THEME - Soft, Clean Colors ===
    LIGHT = {
        # Backgrounds
        "bg_primary": "#F8F9FA",          # Soft white
        "bg_secondary": "#FFFFFF",        # Pure white
        "bg_tertiary": "#F1F3F5",         # Light gray
        "bg_elevated": "#FFFFFF",         # Elevated white
        "bg_hover": "#E9ECEF",            # Hover gray
        
        # Foregrounds
        "fg_primary": "#1A1D2E",          # Near black
        "fg_secondary": "#495057",        # Gray
        "fg_tertiary": "#6C757D",         # Light gray
        "fg_disabled": "#ADB5BD",         # Disabled gray
        
        # Accents & Semantics
        "accent_primary": "#2F6BFF",      # Primary blue
        "accent_secondary": "#4B82FF",    # Lighter blue
        "accent_hover": "#1E5AEE",        # Hover blue
        
        "success": "#10B981",             # Green
        "success_bg": "#D1FAE5",          # Success background
        "warning": "#F59E0B",             # Amber
        "warning_bg": "#FEF3C7",          # Warning background
        "error": "#EF4444",               # Red
        "error_bg": "#FEE2E2",            # Error background
        "info": "#3B82F6",                # Blue
        "info_bg": "#DBEAFE",             # Info background
        
        # UI Elements
        "border": "#DEE2E6",              # Default border
        "border_focus": "#2F6BFF",        # Focused border
        "border_hover": "#ADB5BD",        # Hover border
        
        "shadow": "rgba(0, 0, 0, 0.1)",   # Shadow color
        "overlay": "rgba(255, 255, 255, 0.95)",  # Modal overlay
    }


class Typography:
    """Modern typography system with proper hierarchy"""
    
    # Font families with fallbacks
    FONT_SANS = "Inter, Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif"
    FONT_MONO = "JetBrains Mono, Consolas, Monaco, Courier New, monospace"
    
    # Font sizes (in pixels)
    SIZE_XXXL = 32   # Hero titles
    SIZE_XXL = 24    # Page titles
    SIZE_XL = 20     # Section titles
    SIZE_LG = 16     # Large text
    SIZE_MD = 14     # Body text (default)
    SIZE_SM = 12     # Small text
    SIZE_XS = 10     # Extra small text
    
    # Font weights
    WEIGHT_LIGHT = "300"
    WEIGHT_REGULAR = "400"
    WEIGHT_MEDIUM = "500"
    WEIGHT_SEMIBOLD = "600"
    WEIGHT_BOLD = "700"
    
    # Line heights
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.75
    
    # Letter spacing
    LETTER_SPACING_TIGHT = "-0.02em"
    LETTER_SPACING_NORMAL = "0"
    LETTER_SPACING_WIDE = "0.05em"


class Spacing:
    """Consistent spacing system based on 4px grid"""
    
    # Base unit (4px)
    BASE = 4
    
    # Spacing scale
    XS = BASE * 1      # 4px
    SM = BASE * 2      # 8px
    MD = BASE * 3      # 12px
    LG = BASE * 4      # 16px
    XL = BASE * 6      # 24px
    XXL = BASE * 8     # 32px
    XXXL = BASE * 12   # 48px
    
    # Padding shortcuts
    PADDING_COMPACT = (SM, MD)      # (8, 12)
    PADDING_NORMAL = (MD, LG)       # (12, 16)
    PADDING_COMFORTABLE = (LG, XL)  # (16, 24)
    
    # Border radius
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 9999


class Shadows:
    """Modern shadow system for depth"""
    
    NONE = "0 0 0 rgba(0, 0, 0, 0)"
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    XXL = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
    
    # Inner shadows
    INNER = "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"


class Icons:
    """Icon sizing system"""
    
    SIZE_XS = 12
    SIZE_SM = 16
    SIZE_MD = 20
    SIZE_LG = 24
    SIZE_XL = 32
    SIZE_XXL = 48


class DesignTokens:
    """Complete design system tokens"""
    
    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self.colors = ColorPalette.DARK if dark_mode else ColorPalette.LIGHT
        self.typography = Typography
        self.spacing = Spacing
        self.shadows = Shadows
        self.icons = Icons
    
    def get_color(self, key: str) -> str:
        """Get color from current theme"""
        return self.colors.get(key, "#000000")
    
    def toggle_mode(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.colors = ColorPalette.DARK if self.dark_mode else ColorPalette.LIGHT
    
    @staticmethod
    def get_font_config(size: int = 14, weight: str = "400", family: str = None) -> Dict:
        """Get font configuration dictionary"""
        return {
            "family": family or Typography.FONT_SANS,
            "size": size,
            "weight": weight
        }


class ModernTheme:
    """Modern theme implementation for ttk widgets"""
    
    def __init__(self, dark_mode: bool = True):
        self.tokens = DesignTokens(dark_mode)
        self.dark_mode = dark_mode
    
    def get_ttk_style_config(self) -> Dict:
        """Get complete ttk style configuration"""
        colors = self.tokens.colors
        spacing = self.tokens.spacing
        
        return {
            # === TFrame ===
            "TFrame": {
                "configure": {
                    "background": colors["bg_primary"],
                    "borderwidth": 0,
                }
            },
            
            # === TLabel ===
            "TLabel": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["fg_primary"],
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_REGULAR),
                    "padding": (spacing.SM, spacing.SM),
                }
            },
            
            "Title.TLabel": {
                "configure": {
                    "font": ("Inter", Typography.SIZE_XXL, Typography.WEIGHT_BOLD),
                    "foreground": colors["fg_primary"],
                }
            },
            
            "Subtitle.TLabel": {
                "configure": {
                    "font": ("Inter", Typography.SIZE_LG, Typography.WEIGHT_SEMIBOLD),
                    "foreground": colors["fg_secondary"],
                }
            },
            
            "Caption.TLabel": {
                "configure": {
                    "font": ("Inter", Typography.SIZE_SM, Typography.WEIGHT_REGULAR),
                    "foreground": colors["fg_tertiary"],
                }
            },
            
            # === TButton ===
            "TButton": {
                "configure": {
                    "background": colors["accent_primary"],
                    "foreground": "#FFFFFF",
                    "bordercolor": colors["accent_primary"],
                    "darkcolor": colors["accent_primary"],
                    "lightcolor": colors["accent_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (spacing.LG, spacing.MD),
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                },
                "map": {
                    "background": [
                        ("active", colors["accent_hover"]),
                        ("pressed", colors["accent_hover"]),
                        ("disabled", colors["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", colors["fg_disabled"]),
                    ],
                }
            },
            
            "Secondary.TButton": {
                "configure": {
                    "background": colors["bg_tertiary"],
                    "foreground": colors["fg_primary"],
                    "bordercolor": colors["border"],
                },
                "map": {
                    "background": [
                        ("active", colors["bg_hover"]),
                        ("pressed", colors["bg_hover"]),
                    ],
                }
            },
            
            "Outline.TButton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["accent_primary"],
                    "bordercolor": colors["accent_primary"],
                    "borderwidth": 2,
                },
                "map": {
                    "background": [
                        ("active", colors["bg_secondary"]),
                    ],
                }
            },
            
            # === TEntry ===
            "TEntry": {
                "configure": {
                    "fieldbackground": colors["bg_secondary"],
                    "foreground": colors["fg_primary"],
                    "bordercolor": colors["border"],
                    "darkcolor": colors["bg_secondary"],
                    "lightcolor": colors["bg_secondary"],
                    "insertcolor": colors["fg_primary"],
                    "borderwidth": 1,
                    "padding": (spacing.MD, spacing.SM),
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_REGULAR),
                },
                "map": {
                    "bordercolor": [
                        ("focus", colors["border_focus"]),
                        ("hover", colors["border_hover"]),
                    ],
                    "fieldbackground": [
                        ("disabled", colors["bg_hover"]),
                    ],
                }
            },
            
            # === TCombobox ===
            "TCombobox": {
                "configure": {
                    "fieldbackground": colors["bg_secondary"],
                    "background": colors["bg_secondary"],
                    "foreground": colors["fg_primary"],
                    "bordercolor": colors["border"],
                    "arrowcolor": colors["fg_secondary"],
                    "padding": (spacing.MD, spacing.SM),
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_REGULAR),
                },
                "map": {
                    "bordercolor": [
                        ("focus", colors["border_focus"]),
                        ("hover", colors["border_hover"]),
                    ],
                }
            },
            
            # === TCheckbutton & TRadiobutton ===
            "TCheckbutton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["fg_primary"],
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_REGULAR),
                    "padding": (spacing.SM, spacing.XS),
                }
            },
            
            "TRadiobutton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["fg_primary"],
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_REGULAR),
                    "padding": (spacing.SM, spacing.XS),
                }
            },
            
            # === TNotebook ===
            "TNotebook": {
                "configure": {
                    "background": colors["bg_primary"],
                    "borderwidth": 0,
                    "tabmargins": (spacing.SM, spacing.SM, spacing.SM, 0),
                }
            },
            
            "TNotebook.Tab": {
                "configure": {
                    "background": colors["bg_tertiary"],
                    "foreground": colors["fg_secondary"],
                    "padding": (spacing.LG, spacing.MD),
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                    "borderwidth": 0,
                },
                "map": {
                    "background": [
                        ("selected", colors["bg_elevated"]),
                        ("active", colors["bg_hover"]),
                    ],
                    "foreground": [
                        ("selected", colors["fg_primary"]),
                        ("active", colors["fg_primary"]),
                    ],
                }
            },
            
            # === TLabelframe ===
            "TLabelframe": {
                "configure": {
                    "background": colors["bg_tertiary"],
                    "bordercolor": colors["border"],
                    "borderwidth": 1,
                    "relief": "flat",
                }
            },
            
            "TLabelframe.Label": {
                "configure": {
                    "background": colors["bg_tertiary"],
                    "foreground": colors["fg_primary"],
                    "font": ("Inter", Typography.SIZE_MD, Typography.WEIGHT_SEMIBOLD),
                }
            },
            
            # === TScrollbar ===
            "TScrollbar": {
                "configure": {
                    "background": colors["bg_hover"],
                    "bordercolor": colors["bg_primary"],
                    "troughcolor": colors["bg_secondary"],
                    "arrowcolor": colors["fg_secondary"],
                    "borderwidth": 0,
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("active", colors["accent_primary"]),
                    ],
                }
            },
            
            # === TSeparator ===
            "TSeparator": {
                "configure": {
                    "background": colors["border"],
                }
            },
            
            # === TProgressbar ===
            "TProgressbar": {
                "configure": {
                    "background": colors["accent_primary"],
                    "troughcolor": colors["bg_tertiary"],
                    "bordercolor": colors["bg_tertiary"],
                    "lightcolor": colors["accent_primary"],
                    "darkcolor": colors["accent_primary"],
                    "borderwidth": 0,
                    "thickness": 8,
                }
            },
        }
    
    def apply_to_style(self, style_obj):
        """Apply theme to ttk.Style object"""
        config = self.get_ttk_style_config()
        
        for widget_class, settings in config.items():
            if "configure" in settings:
                style_obj.configure(widget_class, **settings["configure"])
            if "map" in settings:
                style_obj.map(widget_class, **settings["map"])
    
    def toggle(self):
        """Toggle theme mode"""
        self.dark_mode = not self.dark_mode
        self.tokens.toggle_mode()
