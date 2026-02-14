# -*- coding: utf-8 -*-
"""
Unified Theme Management for EasyCut

Consolidates theme management (previously split between ui_enhanced.Theme and ModernTheme)
into a single, professional system supporting:
- Dark and Light themes
- Instant hot-reload
- Complete ttk widget styling
- Custom component colors

Author: Deko Costa
License: MIT
"""

import tkinter.font as tkfont
from tkinter import ttk
from typing import Dict, Tuple
from pathlib import Path

from core.logger import get_logger
from core.constants import Constants

# Try to import icon colors for branding
try:
    from design_system import ColorPalette
    ICON_PRIMARY = ColorPalette.DARK.get("accent_primary", "#f85451")
except:
    ICON_PRIMARY = "#f85451"  # Fallback coral red

logger = get_logger(__name__)


class ThemeManager:
    """
    Unified theme management system
    
    Consolidates all theme-related functionality:
    - Color palettes (dark/light)
    - Typography system
    - Spacing/sizing
    - ttk widget styling
    - Hot-reload support
    """
    
    # =====================================================================
    # COLOR PALETTES
    # =====================================================================
    
    DARK_PALETTE = {
        # Backgrounds
        "bg_primary": "#0A0E27",          # Deep navy blue
        "bg_secondary": "#131829",        # Slightly lighter
        "bg_tertiary": "#1A1F3A",         # Card/panel background
        "bg_elevated": "#20264D",         # Elevated elements
        "bg_hover": "#252B54",            # Hover state
        
        # Foregrounds
        "fg_primary": "#E8EAED",          # Main text
        "fg_secondary": "#A8B1D6",        # Secondary text
        "fg_tertiary": "#6B7AA8",         # Tertiary text
        "fg_disabled": "#4A5578",         # Disabled text
        
        # Accents
        "accent_primary": ICON_PRIMARY,   # From app icon
        "accent_secondary": "#FF9A9A",    # Lighter variant
        "accent_hover": "#E83E3A",        # Darker hover
        
        # Semantics
        "success": "#10B981",
        "success_bg": "#064E3B",
        "warning": "#F59E0B",
        "warning_bg": "#78350F",
        "error": "#EF4444",
        "error_bg": "#7F1D1D",
        "info": "#3B82F6",
        "info_bg": "#1E3A8A",
        
        # UI Elements
        "border": "#2D3555",
        "border_focus": ICON_PRIMARY,
        "border_hover": "#384071",
        "shadow": "rgba(0, 0, 0, 0.5)",
        "overlay": "rgba(10, 14, 39, 0.95)",
        
        # Icons
        "icon_primary": "#E8EAED",
        "icon_muted": "#9CA3AF",
        "icon_accent": ICON_PRIMARY,
    }
    
    LIGHT_PALETTE = {
        # Backgrounds - Pure whites and true grays (NO blue tones)
        "bg_primary": "#FFFFFF",          # Pure white
        "bg_secondary": "#FAFAFA",        # Almost white
        "bg_tertiary": "#F3F3F3",         # Light gray
        "bg_elevated": "#FFFFFF",         # Elevated white
        "bg_hover": "#EFEFEF",            # Hover gray
        
        # Foregrounds - Maximum contrast
        "fg_primary": "#0D0D0D",          # Almost black
        "fg_secondary": "#404040",        # Dark gray
        "fg_tertiary": "#717171",         # Medium gray
        "fg_disabled": "#AAAAAA",         # Disabled gray
        
        # Accents
        "accent_primary": ICON_PRIMARY,   # From app icon
        "accent_secondary": "#FF8680",    # Lighter coral
        "accent_hover": "#E84037",        # Darker coral
        
        # Semantics - Dark colors for better contrast
        "success": "#0F7938",
        "success_bg": "#E8F5E9",
        "warning": "#C67C1B",
        "warning_bg": "#FFF8E1",
        "error": "#C62828",
        "error_bg": "#FFEBEE",
        "info": "#1565C0",
        "info_bg": "#E3F2FD",
        
        # UI Elements
        "border": "#CCCCCC",
        "border_focus": ICON_PRIMARY,
        "border_hover": "#BBBBBB",
        "shadow": "rgba(0, 0, 0, 0.1)",
        "overlay": "rgba(255, 255, 255, 0.95)",
        
        # Icons
        "icon_primary": "#2E2E2E",
        "icon_muted": "#717171",
        "icon_accent": ICON_PRIMARY,
    }
    
    # =====================================================================
    # TYPOGRAPHY SYSTEM
    # =====================================================================
    
    TYPOGRAPHY = {
        "SIZE_XS": 11,
        "SIZE_SM": 13,
        "SIZE_MD": 15,
        "SIZE_LG": 18,
        "SIZE_XL": 22,
        "SIZE_XXL": 28,
        "FONT_FAMILY": "Segoe UI",
    }
    
    # =====================================================================
    # SPACING SYSTEM
    # =====================================================================
    
    SPACING = {
        "XS": 4,      # Extra small
        "SM": 8,      # Small
        "MD": 12,     # Medium
        "LG": 16,     # Large
        "XL": 20,     # Extra large
        "XXL": 24,    # Double extra large
    }
    
    # =====================================================================
    # ICON SIZES
    # =====================================================================
    
    ICON_SIZES = {
        "XS": 12,
        "SM": 16,
        "MD": 20,
        "LG": 24,
        "XL": 32,
        "XXL": 48,
    }
    
    def __init__(self, dark_mode: bool = True, font_family: str = "Segoe UI"):
        """Initialize theme manager"""
        self.dark_mode = dark_mode
        self.font_family = font_family
        self.colors = self.DARK_PALETTE if dark_mode else self.LIGHT_PALETTE
        logger.info(f"ThemeManager initialized: {'DARK' if dark_mode else 'LIGHT'} mode")
    
    # =====================================================================
    # COLOR MANAGEMENT
    # =====================================================================
    
    def get_color(self, key: str, default: str = "#000000") -> str:
        """
        Get color from current theme
        
        Args:
            key: Color key name
            default: Default color if not found
        
        Returns:
            Hex color code
        """
        return self.colors.get(key, default)
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get entire color palette"""
        return self.colors.copy()
    
    # =====================================================================
    # FONT MANAGEMENT
    # =====================================================================
    
    def get_font(self, size: str = "MD", weight: str = "normal") -> Tuple[str, int, str]:
        """
        Get font tuple for tk widgets
        
        Args:
            size: Font size key (XS, SM, MD, LG, XL, XXL)
            weight: Font weight (normal, bold)
        
        Returns:
            Tuple (family, size, weight) for tk.Font()
        """
        size_value = self.TYPOGRAPHY.get(f"SIZE_{size}", 14)
        return (self.font_family, size_value, weight)
    
    def get_font_config(self, size: str = "MD", weight: str = "normal") -> Dict:
        """Get font configuration dictionary"""
        family, size_val, weight_val = self.get_font(size, weight)
        return {
            "family": family,
            "size": size_val,
            "weight": weight_val
        }
    
    # =====================================================================
    # SPACING MANAGEMENT
    # =====================================================================
    
    def get_spacing(self, key: str = "MD") -> int:
        """Get spacing value"""
        return self.SPACING.get(key, 12)
    
    def get_padding(self, size: str = "MD") -> int:
        """Get padding value"""
        return self.get_spacing(size)
    
    # =====================================================================
    # THEME TOGGLING
    # =====================================================================
    
    def toggle(self):
        """Toggle between dark and light themes"""
        self.dark_mode = not self.dark_mode
        self.colors = self.DARK_PALETTE if self.dark_mode else self.LIGHT_PALETTE
        logger.info(f"Theme toggled to: {'DARK' if self.dark_mode else 'LIGHT'}")
        return self.dark_mode
    
    # =====================================================================
    # TTK STYLING
    # =====================================================================
    
    def get_ttk_styles(self) -> Dict:
        """
        Get complete ttk style configuration
        
        Returns:
            Dictionary of all widget style configurations
        """
        c = self.colors
        s = self.SPACING
        t = self.TYPOGRAPHY
        
        return {
            # === BASE STYLES ===
            "TFrame": {
                "configure": {
                    "background": c["bg_primary"],
                    "borderwidth": 0,
                }
            },
            
            "TLabel": {
                "configure": {
                    "background": c["bg_primary"],
                    "foreground": c["fg_primary"],
                    "font": (self.font_family, t["SIZE_MD"], "normal"),
                }
            },
            
            "TButton": {
                "configure": {
                    "background": c["accent_primary"],
                    "foreground": "#FFFFFF",
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "padding": (s["LG"], s["MD"]),
                    "font": (self.font_family, t["SIZE_MD"], "bold"),
                },
                "map": {
                    "background": [
                        ("active", c["accent_hover"]),
                        ("pressed", c["accent_hover"]),
                        ("disabled", c["bg_hover"]),
                    ],
                }
            },
            
            "TEntry": {
                "configure": {
                    "fieldbackground": c["bg_secondary"],
                    "foreground": c["fg_primary"],
                    "borderwidth": 1,
                    "padding": (s["MD"], s["SM"]),
                    "font": (self.font_family, t["SIZE_MD"], "normal"),
                },
                "map": {
                    "bordercolor": [
                        ("focus", c["border_focus"]),
                    ],
                }
            },
            
            "TCombobox": {
                "configure": {
                    "fieldbackground": c["bg_secondary"],
                    "background": c["bg_secondary"],
                    "foreground": c["fg_primary"],
                    "borderwidth": 1,
                    "padding": (s["MD"], s["SM"]),
                    "font": (self.font_family, t["SIZE_MD"], "normal"),
                },
            },
            
            "TNotebook": {
                "configure": {
                    "background": c["bg_primary"],
                    "borderwidth": 0,
                }
            },
            
            "TNotebook.Tab": {
                "configure": {
                    "background": c["bg_tertiary"],
                    "foreground": c["fg_secondary"],
                    "padding": (s["LG"], s["MD"]),
                    "font": (self.font_family, t["SIZE_MD"], "bold"),
                },
                "map": {
                    "background": [
                        ("selected", c["accent_primary"]),
                    ],
                    "foreground": [
                        ("selected", "#FFFFFF"),
                    ],
                }
            },
            
            "TSeparator": {
                "configure": {
                    "background": c["border"],
                }
            },
        }
    
    def apply_to_style(self, style_obj: ttk.Style) -> None:
        """Apply theme to ttk.Style object"""
        try:
            style_obj.theme_use('clam')  # Base theme
            
            styles = self.get_ttk_styles()
            for widget_class, config in styles.items():
                if "configure" in config:
                    style_obj.configure(widget_class, **config["configure"])
                if "map" in config:
                    style_obj.map(widget_class, **config["map"])
            
            logger.info("TTK styles applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply TTK styles: {e}", exc_info=True)
    
    # =====================================================================
    # UTILITY METHODS
    # =====================================================================
    
    def get_mode_name(self) -> str:
        """Get theme mode name"""
        return "DARK" if self.dark_mode else "LIGHT"
    
    def __repr__(self):
        return f"ThemeManager(mode={self.get_mode_name()}, font={self.font_family})"
