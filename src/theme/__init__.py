# -*- coding: utf-8 -*-
"""
EasyCut Theme System
Unified theme management using design_system.py
"""

# Theme is now managed entirely by design_system.py
# This package is kept for backwards-compatible imports

try:
    from design_system import DesignTokens, ModernTheme, ColorPalette, Typography, Spacing, Icons, Shadows
    # Backward-compatible alias — ThemeManager was removed in favor of DesignTokens
    ThemeManager = DesignTokens
    __all__ = ["DesignTokens", "ModernTheme", "ColorPalette", "Typography", "Spacing", "Icons", "Shadows", "ThemeManager"]
except ImportError:
    __all__ = []
