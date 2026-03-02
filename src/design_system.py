"""
EasyCut Design System v2.0
Premium Visual Language — Glass-morphism, Depth, Motion

A comprehensive design token system providing:
- Rich color palettes with semantic gradients
- Glass-morphism and depth effects
- Animation timing and easing
- Sophisticated typography scale
- 4px grid spacing with fluid scale
- Shadow elevation system
- Complete ttk theme with 20+ widget styles

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

from typing import Dict, Tuple
import math

try:
    from font_loader import LOADED_FONT_FAMILY
except ImportError:
    LOADED_FONT_FAMILY = "Segoe UI"


# ═══════════════════════════════════════════════════════════════════
#  COLOR PALETTES
# ═══════════════════════════════════════════════════════════════════

class ColorPalette:
    """Premium color palettes with depth, gradients, and multi-accent tokens"""
    
    # ── DARK THEME — Obsidian Night ─────────────────────────────
    DARK = {
        # Backgrounds — deep layered depth system (warm purple-tinted blacks)
        "bg_base":       "#08090E",
        "bg_primary":    "#0D0F16",
        "bg_secondary":  "#13161F",
        "bg_tertiary":   "#181C28",
        "bg_elevated":   "#1E2333",
        "bg_hover":      "#242A3C",
        "bg_active":     "#2C3450",
        "bg_input":      "#0F111A",
        "bg_glass":      "#121625",
        "bg_overlay":    "#08090E",
        "bg_card_glow":  "#161A2E",
        
        # Foregrounds — crisper contrast
        "fg_primary":    "#ECEEF3",
        "fg_secondary":  "#8A94A8",
        "fg_tertiary":   "#505A6E",
        "fg_disabled":   "#343A48",
        "fg_on_accent":  "#FFFFFF",
        "fg_inverse":    "#0D0F16",
        "fg_link":       "#6EA8FF",
        
        # Accent Primary — Vibrant Azure Blue
        "accent_primary":   "#387FF5",
        "accent_secondary": "#5E9BFF",
        "accent_hover":     "#5E9BFF",
        "accent_pressed":   "#2A6AE0",
        "accent_muted":     "#101828",
        "accent_subtle":    "#142040",
        "accent_glow":      "#1A2C56",
        "accent_gradient_start": "#387FF5",
        "accent_gradient_end":   "#8B5CF6",
        
        # Accent Purple — Secondary accent
        "purple_primary":   "#8B5CF6",
        "purple_hover":     "#A78BFA",
        "purple_muted":     "#1C1233",
        "purple_subtle":    "#241844",
        "purple_glow":      "#2D1F5E",
        "purple_gradient_start": "#8B5CF6",
        "purple_gradient_end":   "#EC4899",
        
        # Accent Orange — Tertiary warm accent
        "orange_primary":   "#F97316",
        "orange_hover":     "#FB923C",
        "orange_muted":     "#261408",
        "orange_subtle":    "#331C0A",
        "orange_glow":      "#3D2410",
        
        # Accent Red — Quaternary vivid accent
        "red_primary":     "#EF4444",
        "red_hover":       "#F87171",
        "red_muted":       "#260E0E",
        "red_subtle":      "#331212",
        "red_glow":        "#3D1818",
        
        # Accent Rose/Pink
        "rose_primary":    "#EC4899",
        "rose_hover":      "#F472B6",
        "rose_muted":      "#26101C",
        "rose_subtle":     "#331424",
        
        # Accent Cyan/Teal
        "cyan_primary":    "#06B6D4",
        "cyan_hover":      "#22D3EE",
        "cyan_muted":      "#06202A",
        "cyan_subtle":     "#082A36",
        
        # Semantic colors — more saturated
        "success":       "#22C992",
        "success_hover": "#1BB580",
        "success_bg":    "#0A2218",
        "success_muted": "#0E281E",
        "warning":       "#F5A623",
        "warning_hover": "#E09318",
        "warning_bg":    "#241C08",
        "warning_muted": "#282014",
        "error":         "#EF4444",
        "error_hover":   "#DC3535",
        "error_bg":      "#260E0E",
        "error_muted":   "#281414",
        "info":          "#5B9AFF",
        "info_bg":       "#0E1828",
        "info_muted":    "#121E38",
        
        # Borders — sharper definition
        "border":        "#1C2030",
        "border_subtle": "#151924",
        "border_focus":  "#387FF5",
        "border_hover":  "#283048",
        "border_strong": "#384058",
        "border_glow":   "#2A3870",
        
        # Shadows
        "shadow_sm":    "#050608",
        "shadow_md":    "#030406",
        "shadow_lg":    "#020204",
        "shadow_glow":  "#162050",
        "shadow":       "#040508",
        
        # Icons — vibrant multi-color
        "icon_primary":  "#C8D0E0",
        "icon_muted":    "#6E7A8E",
        "icon_accent":   "#5E9BFF",
        "icon_purple":   "#A78BFA",
        "icon_orange":   "#FB923C",
        "icon_red":      "#F87171",
        "icon_cyan":     "#22D3EE",
        "icon_success":  "#22C992",
        "icon_warning":  "#F5A623",
        "icon_error":    "#EF4444",
        "icon_rose":     "#F472B6",
        
        # Sidebar — deeper contrast with purple tint
        "sidebar_bg":           "#0B0D14",
        "sidebar_border":       "#161A26",
        "sidebar_item_hover":   "#151B2C",
        "sidebar_item_active":  "#162040",
        "sidebar_indicator":    "#387FF5",
        "sidebar_glow":         "#0E1428",
        
        # Header — premium feel with subtle gradient capability
        "header_bg":           "#0C0F18",
        "header_border":       "#1C2030",
        "header_gradient_start": "#0C0F18",
        "header_gradient_end":   "#121628",
        
        # Scrollbar — minimal
        "scrollbar_track":      "#13161F",
        "scrollbar_thumb":      "#283044",
        "scrollbar_thumb_hover":"#364058",
        
        # Selection
        "selection_bg":   "#1A2C56",
        "selection_fg":   "#ECEEF3",
        
        # Tags (for badges, pills) — vibrant multi-color
        "tag_blue_bg":    "#0E1A38",
        "tag_blue_fg":    "#5B9AFF",
        "tag_green_bg":   "#0A2218",
        "tag_green_fg":   "#22C992",
        "tag_amber_bg":   "#241C08",
        "tag_amber_fg":   "#F5A623",
        "tag_red_bg":     "#260E0E",
        "tag_red_fg":     "#F87171",
        "tag_purple_bg":  "#1C1233",
        "tag_purple_fg":  "#A78BFA",
        "tag_orange_bg":  "#261408",
        "tag_orange_fg":  "#FB923C",
        "tag_rose_bg":    "#26101C",
        "tag_rose_fg":    "#F472B6",
        "tag_cyan_bg":    "#06202A",
        "tag_cyan_fg":    "#22D3EE",
        "tag_neutral_bg": "#1C2030",
        "tag_neutral_fg": "#8A94A8",
        
        # Live / recording — eye-catching
        "live_red":      "#FF3B3B",
        "live_red_bg":   "#3C1010",
        "short_orange":  "#FF7A00",
        "short_orange_bg": "#3C2200",
        
        # Gradient presets (use with icon_renderer.create_gradient_image)
        "gradient_blue_purple":   ("#387FF5", "#8B5CF6"),
        "gradient_purple_pink":   ("#8B5CF6", "#EC4899"),
        "gradient_orange_red":    ("#F97316", "#EF4444"),
        "gradient_cyan_blue":     ("#06B6D4", "#387FF5"),
        "gradient_green_cyan":    ("#22C992", "#06B6D4"),
        "gradient_sunset":        ("#F97316", "#EC4899"),
    }
    
    # ── LIGHT THEME — Pure Canvas ───────────────────────────────
    LIGHT = {
        # Backgrounds — clean paper layers (warmer whites, subtle tint)
        "bg_base":       "#F2F4F8",
        "bg_primary":    "#FFFFFF",
        "bg_secondary":  "#F6F7FB",
        "bg_tertiary":   "#FFFFFF",
        "bg_elevated":   "#FFFFFF",
        "bg_hover":      "#EBEEF5",
        "bg_active":     "#E2E6F0",
        "bg_input":      "#F2F4F8",
        "bg_glass":      "#FFFFFF",
        "bg_overlay":    "#F2F4F8",
        "bg_card_glow":  "#EFF1F9",
        
        # Foregrounds — deeper blacks
        "fg_primary":    "#0F172A",
        "fg_secondary":  "#475569",
        "fg_tertiary":   "#94A3B8",
        "fg_disabled":   "#CBD5E1",
        "fg_on_accent":  "#FFFFFF",
        "fg_inverse":    "#FFFFFF",
        "fg_link":       "#2563EB",
        
        # Accent Primary — Deeper Blue
        "accent_primary":   "#2563EB",
        "accent_secondary": "#1D4ED8",
        "accent_hover":     "#1D4ED8",
        "accent_pressed":   "#1E40AF",
        "accent_muted":     "#EFF4FF",
        "accent_subtle":    "#E4EDFE",
        "accent_glow":      "#DBEAFE",
        "accent_gradient_start": "#2563EB",
        "accent_gradient_end":   "#7C3AED",
        
        # Accent Purple — Secondary accent
        "purple_primary":   "#7C3AED",
        "purple_hover":     "#6D28D9",
        "purple_muted":     "#F3EFFF",
        "purple_subtle":    "#EDE9FE",
        "purple_glow":      "#DDD6FE",
        "purple_gradient_start": "#7C3AED",
        "purple_gradient_end":   "#DB2777",
        
        # Accent Orange — Tertiary warm accent
        "orange_primary":   "#EA580C",
        "orange_hover":     "#C2410C",
        "orange_muted":     "#FFF4ED",
        "orange_subtle":    "#FFEDD5",
        "orange_glow":      "#FED7AA",
        
        # Accent Red — Quaternary vivid accent
        "red_primary":     "#DC2626",
        "red_hover":       "#B91C1C",
        "red_muted":       "#FFF1F2",
        "red_subtle":      "#FEE2E2",
        "red_glow":        "#FECACA",
        
        # Accent Rose/Pink
        "rose_primary":    "#DB2777",
        "rose_hover":      "#BE185D",
        "rose_muted":      "#FFF1F7",
        "rose_subtle":     "#FCE7F3",
        
        # Accent Cyan/Teal
        "cyan_primary":    "#0891B2",
        "cyan_hover":      "#0E7490",
        "cyan_muted":      "#ECFEFF",
        "cyan_subtle":     "#CFFAFE",
        
        # Semantic colors  
        "success":       "#059669",
        "success_hover": "#047857",
        "success_bg":    "#ECFDF5",
        "success_muted": "#F0FDF7",
        "warning":       "#D97706",
        "warning_hover": "#B45309",
        "warning_bg":    "#FFFBEB",
        "warning_muted": "#FEF8EC",
        "error":         "#DC2626",
        "error_hover":   "#B91C1C",
        "error_bg":      "#FEF2F2",
        "error_muted":   "#FFF1F2",
        "info":          "#2563EB",
        "info_bg":       "#EFF6FF",
        "info_muted":    "#F0F5FF",
        
        # Borders — cleaner edges with subtle warmth
        "border":        "#DFE4ED",
        "border_subtle": "#EBEEF5",
        "border_focus":  "#2563EB",
        "border_hover":  "#C7CDD8",
        "border_strong": "#94A3B8",
        "border_glow":   "#BFC8E0",
        
        # Shadows
        "shadow_sm":    "#F1F5F9",
        "shadow_md":    "#E6EBF2",
        "shadow_lg":    "#DCE1EA",
        "shadow_glow":  "#DBEAFE",
        "shadow":       "#E6EBF2",
        
        # Icons — vibrant multi-color
        "icon_primary":  "#334155",
        "icon_muted":    "#64748B",
        "icon_accent":   "#2563EB",
        "icon_purple":   "#7C3AED",
        "icon_orange":   "#EA580C",
        "icon_red":      "#DC2626",
        "icon_cyan":     "#0891B2",
        "icon_success":  "#059669",
        "icon_warning":  "#D97706",
        "icon_error":    "#DC2626",
        "icon_rose":     "#DB2777",
        
        # Sidebar — light with subtle blue tint
        "sidebar_bg":           "#F6F7FB",
        "sidebar_border":       "#DFE4ED",
        "sidebar_item_hover":   "#EBEEF5",
        "sidebar_item_active":  "#DBEAFE",
        "sidebar_indicator":    "#2563EB",
        "sidebar_glow":         "#E8EEFF",
        
        # Header — premium feel with subtle gradient capability
        "header_bg":           "#FFFFFF",
        "header_border":       "#DFE4ED",
        "header_gradient_start": "#FFFFFF",
        "header_gradient_end":   "#F6F7FB",
        
        # Scrollbar
        "scrollbar_track":      "#F2F4F8",
        "scrollbar_thumb":      "#CBD5E1",
        "scrollbar_thumb_hover":"#94A3B8",
        
        # Selection
        "selection_bg":   "#DBEAFE",
        "selection_fg":   "#0F172A",
        
        # Tags — vibrant pops on white with more variety
        "tag_blue_bg":    "#DBEAFE",
        "tag_blue_fg":    "#1D4ED8",
        "tag_green_bg":   "#D1FAE5",
        "tag_green_fg":   "#047857",
        "tag_amber_bg":   "#FEF3C7",
        "tag_amber_fg":   "#B45309",
        "tag_red_bg":     "#FEE2E2",
        "tag_red_fg":     "#B91C1C",
        "tag_purple_bg":  "#EDE9FE",
        "tag_purple_fg":  "#6D28D9",
        "tag_orange_bg":  "#FFEDD5",
        "tag_orange_fg":  "#C2410C",
        "tag_rose_bg":    "#FCE7F3",
        "tag_rose_fg":    "#BE185D",
        "tag_cyan_bg":    "#CFFAFE",
        "tag_cyan_fg":    "#0E7490",
        "tag_neutral_bg": "#F1F5F9",
        "tag_neutral_fg": "#475569",
        
        # Live / recording
        "live_red":      "#EF4444",
        "live_red_bg":   "#FEE2E2",
        "short_orange":  "#F97316",
        "short_orange_bg": "#FFEDD5",
        
        # Gradient presets (use with icon_renderer.create_gradient_image)
        "gradient_blue_purple":   ("#2563EB", "#7C3AED"),
        "gradient_purple_pink":   ("#7C3AED", "#DB2777"),
        "gradient_orange_red":    ("#EA580C", "#DC2626"),
        "gradient_cyan_blue":     ("#0891B2", "#2563EB"),
        "gradient_green_cyan":    ("#059669", "#0891B2"),
        "gradient_sunset":        ("#EA580C", "#DB2777"),
    }


# ═══════════════════════════════════════════════════════════════════
#  TYPOGRAPHY
# ═══════════════════════════════════════════════════════════════════

class Typography:
    """Typography scale — Modern proportional hierarchy"""
    
    FONT_FAMILY = LOADED_FONT_FAMILY
    FONT_MONO = "Consolas"
    
    # Sizes — modular scale (1.25 ratio)
    SIZE_DISPLAY = 36
    SIZE_HERO    = 28
    SIZE_H1      = 22
    SIZE_H2      = 17
    SIZE_H3      = 14
    SIZE_BODY    = 13
    SIZE_SMALL   = 12
    SIZE_CAPTION = 11
    SIZE_TINY    = 9
    
    # Legacy aliases
    SIZE_XXXL = SIZE_DISPLAY
    SIZE_XXL  = SIZE_HERO
    SIZE_XL   = SIZE_H1
    SIZE_LG   = SIZE_H2
    SIZE_MD   = SIZE_BODY
    SIZE_SM   = SIZE_CAPTION
    SIZE_XS   = SIZE_TINY
    
    # Weights
    WEIGHT_BOLD     = "bold"
    WEIGHT_SEMIBOLD = "bold"
    WEIGHT_NORMAL   = "normal"
    WEIGHT_REGULAR  = "normal"
    WEIGHT_MEDIUM   = "bold"
    WEIGHT_EXTRABOLD = "bold"
    WEIGHT_LIGHT    = "normal"
    
    # Line heights (reference)
    LINE_HEIGHT_TIGHT  = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.75


# ═══════════════════════════════════════════════════════════════════
#  SPACING
# ═══════════════════════════════════════════════════════════════════

class Spacing:
    """4px grid spacing system with fluid scale"""
    
    BASE = 4
    
    XXXS = 1
    XXS  = 2
    XS   = 4
    SM   = 8
    MD   = 12
    LG   = 16
    XL   = 24
    XXL  = 32
    XXXL = 48
    HUGE = 64
    
    # Padding presets (x, y)
    PADDING_TIGHT       = (SM, XS)
    PADDING_COMPACT     = (SM, MD)
    PADDING_NORMAL      = (MD, LG)
    PADDING_COMFORTABLE = (LG, XL)
    PADDING_SPACIOUS    = (XL, XXL)
    
    # Input padding
    INPUT_PADDING = (MD, SM)
    BUTTON_PADDING_SM = (SM, XS)
    BUTTON_PADDING_MD = (LG, SM)
    BUTTON_PADDING_LG = (XL, MD)
    
    # Border radius
    RADIUS_XS   = 4
    RADIUS_SM   = 6
    RADIUS_MD   = 8
    RADIUS_LG   = 12
    RADIUS_XL   = 16
    RADIUS_XXL  = 24
    RADIUS_FULL = 9999


# ═══════════════════════════════════════════════════════════════════
#  ICONS
# ═══════════════════════════════════════════════════════════════════

class Icons:
    """Icon sizing system"""
    
    SIZE_XS  = 12
    SIZE_SM  = 16
    SIZE_MD  = 20
    SIZE_LG  = 24
    SIZE_XL  = 32
    SIZE_XXL = 48
    SIZE_HERO = 64


# ═══════════════════════════════════════════════════════════════════
#  SHADOWS & ELEVATION
# ═══════════════════════════════════════════════════════════════════

class Elevation:
    """Shadow elevation levels"""
    NONE = 0
    LOW  = 1
    MID  = 2
    HIGH = 3
    TOP  = 4


# ═══════════════════════════════════════════════════════════════════
#  ANIMATION
# ═══════════════════════════════════════════════════════════════════

class Animation:
    """Animation timing and easing for smooth UI transitions"""
    
    # Durations (milliseconds)
    INSTANT   = 0
    FAST      = 100
    NORMAL    = 200
    SMOOTH    = 300
    SLOW      = 500
    DRAMATIC  = 800
    
    # Frame timing
    FPS_60    = 16
    FPS_30    = 33
    FRAME_MS  = FPS_60
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Smooth deceleration — open/expand"""
        return 1 - (1 - t) ** 3
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Smooth start and end — transitions"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - (-2 * t + 2) ** 3 / 2
    
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quick start, very smooth end — premium feel"""
        return 1 - (1 - t) ** 4
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Gentle acceleration"""
        return t * t
    
    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Exponential ease out — snappy"""
        return 1 if t == 1 else 1 - 2 ** (-10 * t)
    
    @staticmethod
    def spring(t: float, stiffness: float = 0.5) -> float:
        """Spring-like overshoot"""
        return 1 - math.cos(t * math.pi * stiffness) * math.exp(-t * 5)
    
    @staticmethod
    def interpolate_color(color1: str, color2: str, t: float) -> str:
        """Interpolate between two hex colors"""
        def parse(c):
            c = c.lstrip('#')
            return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        
        r1, g1, b1 = parse(color1)
        r2, g2, b2 = parse(color2)
        t = max(0.0, min(1.0, t))
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def interpolate_value(start: float, end: float, t: float) -> float:
        """Interpolate between two numeric values"""
        return start + (end - start) * max(0.0, min(1.0, t))


# ═══════════════════════════════════════════════════════════════════
#  DESIGN TOKENS (single access point)
# ═══════════════════════════════════════════════════════════════════

class DesignTokens:
    """Complete design system — single access point"""
    
    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self.colors = ColorPalette.DARK if dark_mode else ColorPalette.LIGHT
        self.typography = Typography
        self.spacing = Spacing
        self.elevation = Elevation
        self.icons = Icons
        self.animation = Animation
        # Legacy alias
        self.shadows = Elevation
    
    def get_color(self, key: str) -> str:
        """Get color from current theme (returns first color if gradient tuple)"""
        val = self.colors.get(key, "#000000")
        if isinstance(val, tuple):
            return val[0]
        return val
    
    def get_gradient(self, key: str):
        """Get gradient tuple (color1, color2) or None"""
        val = self.colors.get(key)
        if isinstance(val, tuple):
            return val
        return None
    
    def toggle_mode(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.colors = ColorPalette.DARK if self.dark_mode else ColorPalette.LIGHT
    
    @staticmethod
    def get_font_config(size: int = 13, weight: str = "normal", family: str = None) -> Dict:
        return {
            "family": family or Typography.FONT_FAMILY,
            "size": size,
            "weight": weight
        }
    
    def font(self, size: int = None, weight: str = "normal", family: str = None) -> Tuple:
        """Get font tuple for Tkinter"""
        return (
            family or Typography.FONT_FAMILY,
            size or Typography.SIZE_BODY,
            weight
        )


# ═══════════════════════════════════════════════════════════════════
#  MODERN THEME (ttk style engine)
# ═══════════════════════════════════════════════════════════════════

class ModernTheme:
    """Premium theme implementation for ttk widgets"""
    
    def __init__(self, dark_mode: bool = True, font_family: str = None):
        self.tokens = DesignTokens(dark_mode)
        self.dark_mode = dark_mode
        self.font_family = font_family or Typography.FONT_FAMILY
    
    def _font(self, size, weight="normal"):
        return (self.font_family, size, weight)
    
    def get_ttk_style_config(self) -> Dict:
        """Get complete ttk style configuration — premium styled"""
        c = self.tokens.colors
        sp = Spacing
        ty = Typography
        
        return {
            # ═══ FRAMES ═══
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
                    "borderwidth": 0,
                }
            },
            "Glass.TFrame": {
                "configure": {
                    "background": c["bg_secondary"],
                    "borderwidth": 0,
                }
            },
            
            # ═══ LABELS ═══
            "TLabel": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["fg_primary"],
                    "font": self._font(ty.SIZE_BODY),
                }
            },
            "Display.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_DISPLAY, "bold"),
                    "foreground": c["fg_primary"],
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
            "Heading.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_H2, "bold"),
                    "foreground": c["fg_primary"],
                }
            },
            "Caption.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_CAPTION),
                    "foreground": c["fg_tertiary"],
                }
            },
            "Muted.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_BODY),
                    "foreground": c["fg_secondary"],
                }
            },
            "Accent.TLabel": {
                "configure": {
                    "font": self._font(ty.SIZE_BODY, "bold"),
                    "foreground": c["accent_primary"],
                }
            },
            "Success.TLabel": {
                "configure": {
                    "foreground": c["success"],
                    "font": self._font(ty.SIZE_BODY),
                }
            },
            "Warning.TLabel": {
                "configure": {
                    "foreground": c["warning"],
                    "font": self._font(ty.SIZE_BODY),
                }
            },
            "Error.TLabel": {
                "configure": {
                    "foreground": c["error"],
                    "font": self._font(ty.SIZE_BODY),
                }
            },
            
            # ═══ BUTTONS ═══
            "TButton": {
                "configure": {
                    "background": c["accent_primary"],
                    "foreground": c["fg_on_accent"],
                    "bordercolor": c["accent_primary"],
                    "darkcolor": c["accent_primary"],
                    "lightcolor": c["accent_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                    "anchor": "center",
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
                    "bordercolor": c["border_hover"],
                    "borderwidth": 1,
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["bg_hover"]),
                        ("pressed", c["bg_active"]),
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
                    "borderwidth": 1,
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "background": [
                        ("active", c["accent_subtle"]),
                        ("pressed", c["accent_muted"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "Ghost.TButton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["fg_secondary"],
                    "bordercolor": c["bg_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                },
                "map": {
                    "background": [
                        ("active", c["bg_hover"]),
                        ("pressed", c["bg_active"]),
                    ],
                    "foreground": [
                        ("active", c["fg_primary"]),
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "Danger.TButton": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["error"],
                    "bordercolor": c["error"],
                    "borderwidth": 1,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["error_bg"]),
                        ("pressed", c["error_bg"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "DangerFilled.TButton": {
                "configure": {
                    "background": c["error"],
                    "foreground": c["fg_on_accent"],
                    "bordercolor": c["error"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["error_hover"]),
                        ("pressed", c["error_hover"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "SuccessFilled.TButton": {
                "configure": {
                    "background": c["success"],
                    "foreground": c["fg_on_accent"],
                    "bordercolor": c["success"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["success_hover"]),
                        ("pressed", c["success_hover"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "PurpleFilled.TButton": {
                "configure": {
                    "background": c["purple_primary"],
                    "foreground": c["fg_on_accent"],
                    "bordercolor": c["purple_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["purple_hover"]),
                        ("pressed", c["purple_hover"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "OrangeFilled.TButton": {
                "configure": {
                    "background": c["orange_primary"],
                    "foreground": c["fg_on_accent"],
                    "bordercolor": c["orange_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["orange_hover"]),
                        ("pressed", c["orange_hover"]),
                        ("disabled", c["bg_hover"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            "RoseFilled.TButton": {
                "configure": {
                    "background": c["rose_primary"],
                    "foreground": c["fg_on_accent"],
                    "bordercolor": c["rose_primary"],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": "none",
                    "padding": (sp.LG, sp.SM),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["rose_hover"]),
                        ("pressed", c["rose_hover"]),
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
                    "padding": (sp.XL, sp.MD),
                    "font": self._font(ty.SIZE_H3, "bold"),
                }
            },
            
            # ═══ ENTRY ═══
            "TEntry": {
                "configure": {
                    "fieldbackground": c["bg_input"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "darkcolor": c["bg_input"],
                    "lightcolor": c["bg_input"],
                    "insertcolor": c["accent_primary"],
                    "borderwidth": 1,
                    "padding": (sp.MD, sp.SM),
                    "font": self._font(ty.SIZE_BODY),
                    "selectbackground": c["accent_primary"],
                    "selectforeground": c["fg_on_accent"],
                },
                "map": {
                    "bordercolor": [
                        ("focus", c["border_focus"]),
                        ("hover", c["border_hover"]),
                    ],
                    "fieldbackground": [
                        ("disabled", c["bg_hover"]),
                        ("readonly", c["bg_secondary"]),
                    ],
                    "foreground": [
                        ("disabled", c["fg_disabled"]),
                    ],
                }
            },
            
            # ═══ COMBOBOX ═══
            "TCombobox": {
                "configure": {
                    "fieldbackground": c["bg_input"],
                    "background": c["bg_input"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "arrowcolor": c["fg_secondary"],
                    "insertcolor": c["accent_primary"],
                    "selectbackground": c["accent_primary"],
                    "selectforeground": c["fg_on_accent"],
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
            
            # ═══ CHECKBUTTON & RADIOBUTTON ═══
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
                        ("active", c["bg_hover"]),
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
                        ("active", c["bg_hover"]),
                    ],
                }
            },
            
            # ═══ NOTEBOOK ═══
            "TNotebook": {
                "configure": {
                    "background": c["bg_primary"],
                    "borderwidth": 0,
                    "tabmargins": (sp.SM, sp.SM, sp.SM, 0),
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "foreground": c["fg_secondary"],
                    "padding": (sp.LG, sp.MD),
                    "font": self._font(ty.SIZE_BODY, "bold"),
                    "borderwidth": 0,
                    "relief": "flat",
                    "focuscolor": "none",
                },
                "map": {
                    "background": [
                        ("selected", c["accent_primary"]),
                        ("active", c["bg_hover"]),
                        ("!selected", c["bg_tertiary"]),
                    ],
                    "foreground": [
                        ("selected", c["fg_on_accent"]),
                        ("active", c["fg_primary"]),
                        ("!selected", c["fg_tertiary"]),
                    ],
                }
            },
            
            # ═══ LABELFRAME ═══
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
            
            # ═══ SCROLLBAR — thin & minimal ═══
            "TScrollbar": {
                "configure": {
                    "background": c["scrollbar_thumb"],
                    "bordercolor": c["scrollbar_track"],
                    "troughcolor": c["scrollbar_track"],
                    "arrowcolor": c["scrollbar_track"],
                    "borderwidth": 0,
                    "relief": "flat",
                    "width": 8,
                    "arrowsize": 0,
                },
                "map": {
                    "background": [
                        ("active", c["scrollbar_thumb_hover"]),
                        ("pressed", c["accent_primary"]),
                        ("!active", c["scrollbar_thumb"]),
                    ],
                }
            },
            
            # ═══ SEPARATOR ═══
            "TSeparator": {
                "configure": {
                    "background": c["border_subtle"],
                }
            },
            
            # ═══ PROGRESSBAR ═══
            "TProgressbar": {
                "configure": {
                    "background": c["accent_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "bordercolor": c["bg_tertiary"],
                    "lightcolor": c["accent_primary"],
                    "darkcolor": c["accent_primary"],
                    "borderwidth": 0,
                    "thickness": 6,
                }
            },
            "Thick.Horizontal.TProgressbar": {
                "configure": {
                    "background": c["accent_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "bordercolor": c["bg_tertiary"],
                    "lightcolor": c["accent_primary"],
                    "darkcolor": c["accent_primary"],
                    "borderwidth": 0,
                    "thickness": 10,
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
                    "thickness": 6,
                }
            },
            "Purple.Horizontal.TProgressbar": {
                "configure": {
                    "background": c["purple_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "bordercolor": c["bg_tertiary"],
                    "lightcolor": c["purple_primary"],
                    "darkcolor": c["purple_primary"],
                    "borderwidth": 0,
                    "thickness": 6,
                }
            },
            "Orange.Horizontal.TProgressbar": {
                "configure": {
                    "background": c["orange_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "bordercolor": c["bg_tertiary"],
                    "lightcolor": c["orange_primary"],
                    "darkcolor": c["orange_primary"],
                    "borderwidth": 0,
                    "thickness": 6,
                }
            },
            
            # ═══ SPINBOX ═══
            "TSpinbox": {
                "configure": {
                    "fieldbackground": c["bg_input"],
                    "foreground": c["fg_primary"],
                    "bordercolor": c["border"],
                    "arrowcolor": c["fg_secondary"],
                    "insertcolor": c["accent_primary"],
                    "padding": (sp.MD, sp.XS),
                    "font": self._font(ty.SIZE_BODY),
                    "selectbackground": c["accent_primary"],
                    "selectforeground": c["fg_on_accent"],
                },
                "map": {
                    "bordercolor": [
                        ("focus", c["border_focus"]),
                    ],
                    "fieldbackground": [
                        ("disabled", c["bg_hover"]),
                    ],
                }
            },
            
            # ═══ SCALE ═══
            "TScale": {
                "configure": {
                    "background": c["bg_primary"],
                    "troughcolor": c["bg_tertiary"],
                    "borderwidth": 0,
                    "sliderthickness": 16,
                },
                "map": {
                    "background": [
                        ("active", c["accent_primary"]),
                    ],
                }
            },
            
            # ═══ PANEDWINDOW ═══
            "TPanedwindow": {
                "configure": {
                    "background": c["bg_primary"],
                }
            },
            "Sash": {
                "configure": {
                    "sashthickness": 4,
                    "gripcount": 0,
                }
            },
        }
    
    def apply_to_style(self, style_obj):
        """Apply theme to ttk.Style object"""
        config = self.get_ttk_style_config()
        for widget_class, settings in config.items():
            if "configure" in settings:
                try:
                    style_obj.configure(widget_class, **settings["configure"])
                except Exception:
                    pass
            if "map" in settings:
                try:
                    style_obj.map(widget_class, **settings["map"])
                except Exception:
                    pass
    
    def toggle(self):
        """Toggle theme mode"""
        self.dark_mode = not self.dark_mode
        self.tokens.toggle_mode()


# ═══════════════════════════════════════════════════════════════════
#  BACKWARD COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════

class Shadows:
    """Legacy alias for Elevation"""
    NONE = 0
    SM   = 1
    MD   = 2
    LG   = 3
