"""
EasyCut Design System
Clean Minimal Design Tokens — Steel Blue Accent

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

from typing import Dict, Tuple

try:
    from font_loader import LOADED_FONT_FAMILY
except ImportError:
    LOADED_FONT_FAMILY = "Segoe UI"


class ColorPalette:
    """Clean Minimal color palette — VS Code inspired"""
    
    # === DARK THEME — VS Code Dark ===
    DARK = {
        # Backgrounds
        "bg_primary":    "#1E1E1E",    # Main background
        "bg_secondary":  "#252526",    # Sidebar, secondary panels
        "bg_tertiary":   "#2D2D2D",    # Cards, elevated surfaces
        "bg_elevated":   "#333333",    # Hover states, modals
        "bg_hover":      "#3C3C3C",    # Hover highlight
        
        # Foregrounds
        "fg_primary":    "#E4E4E4",    # Main text
        "fg_secondary":  "#A0A0A0",    # Secondary text, labels
        "fg_tertiary":   "#6A6A6A",    # Placeholders, disabled text
        "fg_disabled":   "#4A4A4A",    # Disabled elements
        
        # Accent — Steel Blue
        "accent_primary": "#4A90D9",   # Buttons, links, focus
        "accent_secondary": "#5BA0E9", # Lighter variant
        "accent_hover":   "#5BA0E9",   # Accent hover state
        "accent_pressed": "#3A80C9",   # Accent pressed state
        "accent_muted":   "#4A90D920", # 12% opacity for backgrounds
        
        # Semantics
        "success":     "#4CAF50",
        "success_bg":  "#1B3A1F",
        "warning":     "#FFA726",
        "warning_bg":  "#3E2E1A",
        "error":       "#EF5350",
        "error_bg":    "#3A1F1F",
        "info":        "#42A5F5",
        "info_bg":     "#1A2E3E",
        
        # Borders
        "border":       "#3C3C3C",
        "border_focus":  "#4A90D9",
        "border_hover":  "#505050",
        
        # Shadow
        "shadow":       "#00000040",
        
        # Icons
        "icon_primary": "#E4E4E4",
        "icon_muted":   "#A0A0A0",
        "icon_accent":  "#4A90D9",
    }
    
    # === LIGHT THEME — Clean White ===
    LIGHT = {
        # Backgrounds
        "bg_primary":    "#FFFFFF",
        "bg_secondary":  "#F5F5F5",
        "bg_tertiary":   "#FAFAFA",
        "bg_elevated":   "#FFFFFF",
        "bg_hover":      "#EEEEEE",
        
        # Foregrounds
        "fg_primary":    "#1A1A1A",
        "fg_secondary":  "#555555",
        "fg_tertiary":   "#888888",
        "fg_disabled":   "#BBBBBB",
        
        # Accent — Steel Blue (same in both themes)
        "accent_primary": "#4A90D9",
        "accent_secondary": "#3A80C9",
        "accent_hover":   "#3A80C9",
        "accent_pressed": "#2A70B9",
        "accent_muted":   "#4A90D915",
        
        # Semantics (darker for contrast on white)
        "success":     "#2E7D32",
        "success_bg":  "#E8F5E9",
        "warning":     "#E65100",
        "warning_bg":  "#FFF3E0",
        "error":       "#C62828",
        "error_bg":    "#FFEBEE",
        "info":        "#1565C0",
        "info_bg":     "#E3F2FD",
        
        # Borders
        "border":       "#E0E0E0",
        "border_focus":  "#4A90D9",
        "border_hover":  "#CCCCCC",
        
        # Shadow
        "shadow":       "#00000015",
        
        # Icons
        "icon_primary": "#1A1A1A",
        "icon_muted":   "#555555",
        "icon_accent":  "#4A90D9",
    }


class Typography:
    """Typography scale — Clean Minimal hierarchy"""
    
    FONT_FAMILY = LOADED_FONT_FAMILY
    FONT_MONO = "Consolas"
    
    # Sizes
    SIZE_HERO    = 32    # App title only
    SIZE_H1      = 24    # Section headers
    SIZE_H2      = 18    # Card titles
    SIZE_H3      = 15    # Subsection titles
    SIZE_BODY    = 13    # Default body text, buttons, inputs
    SIZE_CAPTION = 11    # Captions, timestamps
    SIZE_TINY    = 9     # Badges, version numbers
    
    # Legacy aliases (backward compat with existing code)
    SIZE_XXXL = SIZE_HERO
    SIZE_XXL  = SIZE_H1
    SIZE_XL   = SIZE_H2
    SIZE_LG   = SIZE_H3
    SIZE_MD   = SIZE_BODY
    SIZE_SM   = SIZE_CAPTION
    SIZE_XS   = SIZE_TINY
    
    # Weights
    WEIGHT_BOLD     = "bold"
    WEIGHT_SEMIBOLD = "bold"   # Tkinter only has normal/bold
    WEIGHT_NORMAL   = "normal"
    WEIGHT_REGULAR  = "normal"
    WEIGHT_MEDIUM   = "bold"
    WEIGHT_EXTRABOLD = "bold"
    WEIGHT_LIGHT    = "normal"
    
    # Line heights (reference only — Tkinter doesn't support)
    LINE_HEIGHT_TIGHT  = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.75


class Spacing:
    """4px grid spacing system"""
    
    BASE = 4
    
    XXS  = 2     # Micro gaps
    XS   = 4     # Icon padding, tight
    SM   = 8     # Between inline elements
    MD   = 12    # Card internal padding, rows
    LG   = 16    # Section gaps, sidebar padding
    XL   = 24    # Between major sections
    XXL  = 32    # Page margins
    XXXL = 48    # Large page gaps
    
    # Padding shortcuts
    PADDING_COMPACT     = (SM, MD)       # 8, 12
    PADDING_NORMAL      = (MD, LG)       # 12, 16
    PADDING_COMFORTABLE = (LG, XL)       # 16, 24
    
    # Border radius
    RADIUS_SM   = 4
    RADIUS_MD   = 8
    RADIUS_LG   = 12
    RADIUS_XL   = 16
    RADIUS_FULL = 9999


class Icons:
    """Icon sizing"""
    
    SIZE_XS  = 14
    SIZE_SM  = 18
    SIZE_MD  = 22
    SIZE_LG  = 26
    SIZE_XL  = 36
    SIZE_XXL = 52


class Shadows:
    """Shadow values (simulated via frames in Tkinter)"""
    
    NONE = 0
    SM   = 1     # 1px offset shadow frame
    MD   = 2     # 2px offset shadow frame
    LG   = 3     # 3px offset shadow frame


class DesignTokens:
    """Complete design system — single access point"""
    
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
    def get_font_config(size: int = 13, weight: str = "normal", family: str = None) -> Dict:
        """Get font configuration dictionary"""
        return {
            "family": family or Typography.FONT_FAMILY,
            "size": size,
            "weight": weight
        }


class ModernTheme:
    """Theme implementation for ttk widgets"""
    
    def __init__(self, dark_mode: bool = True, font_family: str = None):
        self.tokens = DesignTokens(dark_mode)
        self.dark_mode = dark_mode
        self.font_family = font_family or Typography.FONT_FAMILY
    
    def _font(self, size, weight="normal"):
        """Helper to create font tuple"""
        return (self.font_family, size, weight)
    
    def get_ttk_style_config(self) -> Dict:
        """Get complete ttk style configuration"""
        colors = self.tokens.colors
        sp = Spacing
        ty = Typography
        
        return {
            # === TFrame ===
            "TFrame": {
                "configure": {
                    "background": colors["bg_primary"],
                    "borderwidth": 0,
                }
            },
            
            "Card.TFrame": {
                "configure": {
                    "background": colors["bg_tertiary"],
                    "borderwidth": 1,
                    "relief": "solid",
                }
            },
            
            # === TLabel ===
            "TLabel": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                }
            },
            
            "Title.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_H1, "bold"),
                    "foreground": colors["fg_primary"],
                }
            },
            
            "Subtitle.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_H3, "bold"),
                    "foreground": colors["fg_secondary"],
                }
            },
            
            "Caption.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_CAPTION),
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
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", colors["accent_hover"]),
                        ("pressed", colors["accent_pressed"]),
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
                        ("active", colors["accent_muted"].replace("20", "30") if "20" in colors["accent_muted"] else colors["bg_secondary"]),
                    ],
                    "foreground": [
                        ("disabled", colors["fg_disabled"]),
                    ],
                }
            },
            
            "Ghost.TButton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["accent_primary"],
                    "bordercolor": colors["bg_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "background": [
                        ("active", colors["bg_hover"]),
                        ("pressed", colors["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", colors["fg_disabled"]),
                    ],
                }
            },
            
            "Danger.TButton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["error"],
                    "bordercolor": colors["error"],
                    "borderwidth": 2,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", colors["error_bg"]),
                        ("pressed", colors["error_bg"]),
                    ],
                    "foreground": [
                        ("disabled", colors["fg_disabled"]),
                    ],
                }
            },
            
            "DangerFilled.TButton": {
                "configure": {
                    "background": colors["error"],
                    "foreground": "#FFFFFF",
                    "bordercolor": colors["error"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", "#D32F2F"),
                        ("pressed", "#B71C1C"),
                        ("disabled", colors["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", colors["fg_disabled"]),
                    ],
                }
            },
            
            # Size variants
            "Small.TButton": {
                "configure": {
                    "padding": (sp.SM, sp.XS),
                    "font": self._font(ty.SIZE_CAPTION, "bold"),
                }
            },
            
            "Large.TButton": {
                "configure": {
                    "padding": (sp.XL, sp.LG),
                    "font": self._font(ty.SIZE_H3, "bold"),
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
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
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
                    "insertcolor": colors["fg_primary"],
                    "selectbackground": colors["accent_primary"],
                    "selectforeground": "#FFFFFF",
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "bordercolor": [
                        ("focus", colors["border_focus"]),
                        ("hover", colors["border_hover"]),
                    ],
                    "fieldbackground": [
                        ("readonly", colors["bg_secondary"]),
                        ("disabled", colors["bg_hover"]),
                    ],
                    "foreground": [
                        ("readonly", colors["fg_primary"]),
                        ("disabled", colors["fg_disabled"]),
                    ],
                }
            },
            
            # === TCheckbutton & TRadiobutton ===
            "TCheckbutton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                    "padding": (sp.SM, sp.XS),
                }
            },
            
            "TRadiobutton": {
                "configure": {
                    "background": colors["bg_primary"],
                    "foreground": colors["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                    "padding": (sp.SM, sp.XS),
                }
            },
            
            # === TNotebook ===
            "TNotebook": {
                "configure": {
                    "background": colors["bg_primary"],
                    "borderwidth": 0,
                    "tabmargins": (sp.SM, sp.SM, sp.SM, 0),
                }
            },
            
            "TNotebook.Tab": {
                "configure": {
                    "background": colors["bg_tertiary"],
                    "foreground": colors["fg_secondary"],
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                    "borderwidth": 1,
                    "relief": "flat",
                },
                "map": {
                    "background": [
                        ("selected", colors["accent_primary"]),
                        ("active", colors["bg_hover"]),
                        ("!selected", colors["bg_tertiary"]),
                    ],
                    "foreground": [
                        ("selected", "#FFFFFF"),
                        ("active", colors["fg_primary"]),
                        ("!selected", colors["fg_tertiary"]),
                    ],
                    "bordercolor": [
                        ("selected", colors["accent_primary"]),
                        ("!selected", colors["border"]),
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
                    "font": self._font(ty.SIZE_BODY, "bold"),
                }
            },
            
            # === TScrollbar (thin, rounded feel) ===
            "TScrollbar": {
                "configure": {
                    "background": colors["bg_hover"],
                    "bordercolor": colors["bg_primary"],
                    "troughcolor": colors["bg_secondary"],
                    "arrowcolor": colors["fg_secondary"],
                    "borderwidth": 0,
                    "relief": "flat",
                    "width": 10,
                },
                "map": {
                    "background": [
                        ("active", colors["accent_primary"]),
                        ("pressed", colors["accent_hover"]),
                        ("!active", colors["bg_hover"]),
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
                    "thickness": 6,
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
