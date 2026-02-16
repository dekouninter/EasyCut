"""
EasyCut Design System v2.0
Modern Glassmorphic Design Tokens — Refined Dark/Light Themes

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.4.0
"""

from typing import Dict

try:
    from font_loader import LOADED_FONT_FAMILY
except ImportError:
    LOADED_FONT_FAMILY = "Segoe UI"


class ColorPalette:
    """Refined color palettes — Glassmorphic Dark & Clean Light"""
    
    # === DARK THEME — Deep Blue-tinted ===
    DARK = {
        # Backgrounds — Blue-tinted dark with depth layers
        "bg_primary":    "#13151C",    # Deep background
        "bg_secondary":  "#191C26",    # Sidebar, panels
        "bg_tertiary":   "#1F2230",    # Cards, surfaces
        "bg_elevated":   "#262A38",    # Modals, dropdowns, hover surfaces
        "bg_hover":      "#2C3042",    # Hover highlight
        "bg_input":      "#171A24",    # Input field background
        "bg_overlay":    "#0D0F14CC",  # Overlay backdrop (80% opacity hex)
        
        # Foregrounds — Cool white hierarchy
        "fg_primary":    "#E8ECF4",    # Main text — high contrast
        "fg_secondary":  "#8B92A8",    # Secondary text, labels
        "fg_tertiary":   "#5C6278",    # Placeholders, disabled
        "fg_disabled":   "#3D4258",    # Disabled elements
        "fg_inverse":    "#13151C",    # Text on accent buttons
        
        # Accent — Vibrant Blue-Violet
        "accent_primary":   "#6C8EEF",   # Primary action color
        "accent_secondary": "#7E9DF2",   # Lighter variant
        "accent_hover":     "#7E9DF2",   # Hover state
        "accent_pressed":   "#5A7ADB",   # Pressed state
        "accent_muted":     "#6C8EEF18", # 9% opacity for subtle backgrounds
        "accent_glow":      "#6C8EEF30", # 19% opacity for glow/focus rings
        
        # Semantics — Vibrant flat colors
        "success":       "#4ADE80",
        "success_bg":    "#132B1F",
        "success_muted": "#4ADE8025",
        "warning":       "#FBBF24",
        "warning_bg":    "#2B2211",
        "warning_muted": "#FBBF2425",
        "error":         "#F87171",
        "error_bg":      "#2B1515",
        "error_hover":   "#EF4444",
        "error_pressed": "#DC2626",
        "error_muted":   "#F8717125",
        "info":          "#60A5FA",
        "info_bg":       "#15202B",
        "info_muted":    "#60A5FA25",
        
        # Borders — Subtle
        "border":        "#262A38",
        "border_focus":  "#6C8EEF",
        "border_hover":  "#353A4E",
        "border_subtle": "#1F2230",
        
        # Shadow
        "shadow":        "#00000060",
        
        # Icons
        "icon_primary":  "#E8ECF4",
        "icon_muted":    "#8B92A8",
        "icon_accent":   "#6C8EEF",
        
        # Sidebar specific
        "sidebar_bg":       "#14161E",
        "sidebar_active":   "#1E2234",
        "sidebar_indicator": "#6C8EEF",
        "sidebar_hover":    "#1A1E2C",
        
        # Header
        "header_bg":       "#14161E",
        "header_border":   "#1F2230",
    }
    
    # === LIGHT THEME — Clean White with Blue accents ===
    LIGHT = {
        # Backgrounds
        "bg_primary":    "#F8F9FC",
        "bg_secondary":  "#F0F1F7",
        "bg_tertiary":   "#FFFFFF",
        "bg_elevated":   "#FFFFFF",
        "bg_hover":      "#E8EAF2",
        "bg_input":      "#FFFFFF",
        "bg_overlay":    "#F8F9FCCC",
        
        # Foregrounds
        "fg_primary":    "#1A1D2E",
        "fg_secondary":  "#4A5068",
        "fg_tertiary":   "#8890A5",
        "fg_disabled":   "#B8BDD0",
        "fg_inverse":    "#FFFFFF",
        
        # Accent — Slightly deeper blue for contrast
        "accent_primary":   "#5B78E0",
        "accent_secondary": "#4A68D0",
        "accent_hover":     "#4A68D0",
        "accent_pressed":   "#3A58C0",
        "accent_muted":     "#5B78E012",
        "accent_glow":      "#5B78E028",
        
        # Semantics — Richer for light backgrounds
        "success":       "#22C55E",
        "success_bg":    "#ECFDF5",
        "success_muted": "#22C55E18",
        "warning":       "#F59E0B",
        "warning_bg":    "#FFFBEB",
        "warning_muted": "#F59E0B18",
        "error":         "#EF4444",
        "error_bg":      "#FEF2F2",
        "error_hover":   "#DC2626",
        "error_pressed": "#B91C1C",
        "error_muted":   "#EF444418",
        "info":          "#3B82F6",
        "info_bg":       "#EFF6FF",
        "info_muted":    "#3B82F618",
        
        # Borders
        "border":        "#E2E4EF",
        "border_focus":  "#5B78E0",
        "border_hover":  "#C8CCDC",
        "border_subtle": "#ECEDF5",
        
        # Shadow
        "shadow":        "#1A1D2E0A",
        
        # Icons
        "icon_primary":  "#1A1D2E",
        "icon_muted":    "#4A5068",
        "icon_accent":   "#5B78E0",
        
        # Sidebar
        "sidebar_bg":       "#F0F1F7",
        "sidebar_active":   "#FFFFFF",
        "sidebar_indicator": "#5B78E0",
        "sidebar_hover":    "#E8EAF2",
        
        # Header
        "header_bg":       "#FFFFFF",
        "header_border":   "#E2E4EF",
    }


class Typography:
    """Typography system — Modern hierarchy with comfortable sizes"""
    
    FONT_FAMILY = LOADED_FONT_FAMILY
    FONT_MONO = "Consolas"
    FONT_EMOJI = "Segoe UI Emoji"
    
    # Sizes — Slightly increased for better readability
    SIZE_DISPLAY = 36    # Hero banners only
    SIZE_H1      = 26    # Page titles
    SIZE_H2      = 20    # Section headers
    SIZE_H3      = 16    # Card titles, subsections
    SIZE_BODY    = 13    # Default body text
    SIZE_BODY_SM = 12    # Compact body text
    SIZE_CAPTION = 11    # Captions, timestamps
    SIZE_TINY    = 9     # Badges, version numbers
    
    # Legacy aliases
    SIZE_MD   = SIZE_BODY
    SIZE_HERO = SIZE_DISPLAY
    
    # Weights
    WEIGHT_BOLD   = "bold"
    WEIGHT_NORMAL = "normal"
    
    # Line heights (approximate — Tkinter doesn't support directly)
    LINE_HEIGHT_TIGHT  = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_LOOSE  = 1.8


class Spacing:
    """Refined 4px grid spacing system with more granularity"""
    
    BASE = 4
    
    XXS  = 2     # Micro gaps (icon internal)
    XS   = 4     # Icon padding, tight
    SM   = 8     # Between inline elements
    MD   = 12    # Card internal padding, rows
    LG   = 16    # Section gaps, sidebar padding
    XL   = 24    # Between major sections
    XXL  = 32    # Page margins
    XXXL = 48    # Large page gaps
    
    # Component-specific spacing
    CARD_PADDING   = 16   # Internal card padding
    CARD_GAP       = 12   # Gap between stacked cards
    SIDEBAR_ITEM_H = 44   # Sidebar navigation item height
    HEADER_HEIGHT  = 52   # Header height
    
    # Padding shortcut (legacy)
    PADDING_NORMAL = (MD, LG)


class Elevation:
    """Elevation/depth levels for visual hierarchy"""
    
    LEVEL_0 = 0   # Flat — background surfaces
    LEVEL_1 = 1   # Subtle — cards, panels
    LEVEL_2 = 2   # Raised — dropdowns, tooltips
    LEVEL_3 = 3   # Floating — modals, popovers


class BorderRadius:
    """Border radius tokens (for Canvas-drawn elements)"""
    
    NONE = 0
    SM   = 4
    MD   = 8
    LG   = 12
    XL   = 16
    PILL = 999


class Icons:
    """Icon sizing system"""
    
    SIZE_XS  = 14
    SIZE_SM  = 18
    SIZE_MD  = 22
    SIZE_LG  = 28
    SIZE_XL  = 36
    SIZE_XXL = 52


class DesignTokens:
    """Complete design system — single access point"""
    
    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self.colors = ColorPalette.DARK if dark_mode else ColorPalette.LIGHT
        self.typography = Typography
        self.spacing = Spacing
        self.elevation = Elevation
        self.radius = BorderRadius
        self.icons = Icons
    
    def get_color(self, key: str) -> str:
        """Get color from current theme"""
        return self.colors.get(key, "#FF00FF")  # Magenta = missing token
    
    def toggle_mode(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.colors = ColorPalette.DARK if self.dark_mode else ColorPalette.LIGHT


class ModernTheme:
    """Theme implementation for ttk widgets — v2.0"""
    
    def __init__(self, dark_mode: bool = True, font_family: str = None):
        self.tokens = DesignTokens(dark_mode)
        self.dark_mode = dark_mode
        self.font_family = font_family or Typography.FONT_FAMILY
    
    def _font(self, size, weight="normal"):
        """Helper to create font tuple"""
        return (self.font_family, size, weight)
    
    def get_ttk_style_config(self) -> Dict:
        """Get complete ttk style configuration"""
        c = self.tokens.colors
        sp = Spacing
        ty = Typography
        
        return {
            # ══════════════════════════════════════
            # FRAMES
            # ══════════════════════════════════════
            "TFrame": {
                "configure": {
                    "background": c["bg_primary"],
                    "borderwidth": 0,
                }
            },
            
            "Card.TFrame": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "borderwidth": 1,
                    "relief": "solid",
                }
            },
            
            "Elevated.TFrame": {
                "configure": {
                    "background": c["bg_elevated"],
                    "borderwidth": 1,
                    "relief": "solid",
                }
            },
            
            # ══════════════════════════════════════
            # LABELS
            # ══════════════════════════════════════
            "TLabel": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                }
            },
            
            "Title.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_H1, "bold"),
                    "foreground": c["fg_primary"],
                }
            },
            
            "Subtitle.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_H3, "bold"),
                    "foreground": c["fg_secondary"],
                }
            },
            
            "Caption.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_CAPTION),
                    "foreground": c["fg_tertiary"],
                }
            },
            
            "Accent.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_BODY, "bold"),
                    "foreground": c["accent_primary"],
                }
            },
            
            "Badge.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_TINY, "bold"),
                    "foreground": c["accent_primary"],
                    "padding": (6, 2),
                }
            },
            
            # ══════════════════════════════════════
            # BUTTONS — Refined with better padding
            # ══════════════════════════════════════
            "TButton": {
                "configure": {
                    "background": c["accent_primary"],
                    "foreground": c.get("fg_inverse", "#FFFFFF"),
                    "bordercolor": c["accent_primary"],
                    "darkcolor": c["accent_primary"],
                    "lightcolor": c["accent_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["accent_hover"]),
                        ("pressed", c["accent_pressed"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "Secondary.TButton": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "darkcolor": c["bg_tertiary"],
                    "lightcolor": c["bg_tertiary"],
                    "borderwidth": 1,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "background": [
                        ("active", c["bg_hover"]),
                        ("pressed", c["bg_hover"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "Outline.TButton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["accent_primary"],
                    "bordercolor": c["accent_primary"],
                    "darkcolor": c["bg_primary"],
                    "lightcolor": c["bg_primary"],
                    "borderwidth": 2,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "background": [
                        ("active", c["accent_muted"]),
                        ("pressed", c["accent_muted"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "IconOnly.Outline.TButton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["accent_primary"],
                    "bordercolor": c["accent_primary"],
                    "darkcolor": c["bg_primary"],
                    "lightcolor": c["bg_primary"],
                    "borderwidth": 2,
                    "padding": (sp.XS, sp.XS),
                    "anchor": "center",
                    "focusthickness": 0,
                    "focuscolor": "none",
                },
                "map": {
                    "background": [
                        ("active", c["accent_muted"]),
                        ("pressed", c["accent_muted"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "Ghost.TButton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["accent_primary"],
                    "bordercolor": c["bg_primary"],
                    "darkcolor": c["bg_primary"],
                    "lightcolor": c["bg_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "background": [
                        ("active", c["bg_hover"]),
                        ("pressed", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "Danger.TButton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["error"],
                    "bordercolor": c["error"],
                    "darkcolor": c["bg_primary"],
                    "lightcolor": c["bg_primary"],
                    "borderwidth": 2,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["error_muted"]),
                        ("pressed", c["error_muted"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "DangerFilled.TButton": {
                "configure": {
                    "background": c["error"],
                    "foreground": "#FFFFFF",
                    "bordercolor": c["error"],
                    "darkcolor": c["error"],
                    "lightcolor": c["error"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c.get("error_hover", "#DC2626")),
                        ("pressed", c.get("error_pressed", "#B91C1C")),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            "Success.TButton": {
                "configure": {
                    "background": c["success"],
                    "foreground": c.get("fg_inverse", "#FFFFFF"),
                    "bordercolor": c["success"],
                    "darkcolor": c["success"],
                    "lightcolor": c["success"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["success"]),
                        ("pressed", c["success"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
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
            
            # ══════════════════════════════════════
            # ENTRY — Refined inputs
            # ══════════════════════════════════════
            "TEntry": {
                "configure": {
                    "fieldbackground": c["bg_input"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "darkcolor": c["bg_input"],
                    "lightcolor": c["bg_input"],
                    "insertcolor": c["accent_primary"],
                    "selectbackground": c["accent_primary"],
                    "selectforeground": "#FFFFFF",
                    "borderwidth": 1,
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "bordercolor": [
                        ("focus", c["border_focus"]),
                        ("hover", c["border_hover"]),
                    ],
                    "fieldbackground": [
                        ("disabled", c["bg_hover"]),
                    ],
                }
            },
            
            # ══════════════════════════════════════
            # COMBOBOX
            # ══════════════════════════════════════
            "TCombobox": {
                "configure": {
                    "fieldbackground": c["bg_input"],
                    "background": c["bg_input"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "arrowcolor": c["fg_secondary"],
                    "insertcolor": c["accent_primary"],
                    "selectbackground": c["accent_primary"],
                    "selectforeground": "#FFFFFF",
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "bordercolor": [
                        ("focus", c["border_focus"]),
                        ("hover", c["border_hover"]),
                    ],
                    "fieldbackground": [
                        ("readonly", c["bg_input"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("readonly", c["fg_primary"]),
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            # ══════════════════════════════════════
            # CHECKBUTTON & RADIOBUTTON
            # ══════════════════════════════════════
            "TCheckbutton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                    "padding": (sp.SM, sp.XS),
                    "focuscolor": "none",
                },
                "map": {
                    "background": [
                        ("active", c["bg_primary"]),
                    ],
                }
            },
            
            "TRadiobutton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                    "padding": (sp.SM, sp.XS),
                    "focuscolor": "none",
                },
                "map": {
                    "background": [
                        ("active", c["bg_primary"]),
                    ],
                }
            },
            
            # ══════════════════════════════════════
            # NOTEBOOK (tabs hidden — sidebar handles navigation)
            # ══════════════════════════════════════
            "TNotebook": {
                "configure": {
                    "background": c["bg_primary"],
                    "borderwidth": 0,
                    "tabmargins": (0, 0, 0, 0),
                }
            },
            
            # ══════════════════════════════════════
            # LABELFRAME — Refined borders
            # ══════════════════════════════════════
            "TLabelframe": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "bordercolor": c["border"],
                    "borderwidth": 1,
                    "relief": "flat",
                }
            },
            
            "TLabelframe.Label": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "foreground": c["fg_primary"],
                    "font": self._font(ty.SIZE_BODY, "bold"),
                }
            },
            
            "Accent.TLabelframe": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "bordercolor": c["accent_primary"],
                    "borderwidth": 2,
                    "relief": "flat",
                }
            },
            
            # ══════════════════════════════════════
            # SCROLLBAR — Thin & modern
            # ══════════════════════════════════════
            "TScrollbar": {
                "configure": {
                    "background": c["bg_hover"],
                    "bordercolor": c["bg_primary"],
                    "troughcolor": c["bg_secondary"],
                    "arrowcolor": c["fg_tertiary"],
                    "borderwidth": 0,
                    "relief": "flat",
                    "width": 8,
                },
                "map": {
                    "background": [
                        ("active", c["accent_primary"]),
                        ("pressed", c["accent_hover"]),
                        ("!active", c["bg_hover"]),
                    ],
                }
            },
            
            # ══════════════════════════════════════
            # SEPARATOR
            # ══════════════════════════════════════
            "TSeparator": {
                "configure": {
                    "background": c["border"],
                }
            },
            
            # ══════════════════════════════════════
            # PROGRESSBAR — Modern accent bar
            # ══════════════════════════════════════
            "TProgressbar": {
                "configure": {
                    "background": c["accent_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "bordercolor": c["bg_tertiary"],
                    "lightcolor": c["accent_primary"],
                    "darkcolor": c["accent_primary"],
                    "borderwidth": 0,
                    "thickness": 8,
                }
            },
            
            "Success.Horizontal.TProgressbar": {
                "configure": {
                    "background": c["success"],
                    "troughcolor": c["bg_tertiary"],
                    "bordercolor": c["bg_tertiary"],
                    "lightcolor": c["success"],
                    "darkcolor": c["success"],
                    "borderwidth": 0,
                    "thickness": 8,
                }
            },
            
            # ══════════════════════════════════════
            # SPINBOX
            # ══════════════════════════════════════
            "TSpinbox": {
                "configure": {
                    "fieldbackground": c["bg_input"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "darkcolor": c["bg_input"],
                    "lightcolor": c["bg_input"],
                    "arrowcolor": c["fg_secondary"],
                    "insertcolor": c["accent_primary"],
                    "borderwidth": 1,
                    "padding": (sp.SM, sp.XS),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "bordercolor": [
                        ("focus", c["border_focus"]),
                        ("hover", c["border_hover"]),
                    ],
                    "fieldbackground": [
                        ("disabled", c["bg_hover"]),
                    ],
                }
            },
            
            # ══════════════════════════════════════
            # SCALE
            # ══════════════════════════════════════
            "TScale": {
                "configure": {
                    "background": c["bg_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "borderwidth": 0,
                    "sliderthickness": 16,
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
