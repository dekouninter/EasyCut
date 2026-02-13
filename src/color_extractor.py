# -*- coding: utf-8 -*-
"""
Color Extraction System for EasyCut
Extracts dominant colors from app_icon.png for themed color palette

Author: Deko Costa
License: GPL-3.0
"""

from pathlib import Path
from PIL import Image
import colorsys
from collections import Counter


def get_icon_path() -> Path:
    """Get path to app icon"""
    return Path(__file__).parent.parent / "assets" / "app_icon.png"


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_brightness(rgb: tuple) -> float:
    """Get brightness of RGB color (0-1)"""
    r, g, b = [x / 255.0 for x in rgb]
    return (0.299 * r + 0.587 * g + 0.114 * b)


def get_saturation(rgb: tuple) -> float:
    """Get saturation of RGB color (0-1)"""
    r, g, b = [x / 255.0 for x in rgb]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    
    if max_c == min_c:
        return 0.0
    
    if max_c <= 0.5:
        return (max_c - min_c) / (max_c + min_c)
    else:
        return (max_c - min_c) / (2.0 - max_c - min_c)


def extract_dominant_colors(image_path: Path, num_colors: int = 6) -> list:
    """
    Extract dominant colors from image
    
    Args:
        image_path: Path to image file
        num_colors: Number of colors to extract
    
    Returns:
        List of hex colors sorted by prominence
    """
    try:
        # Open and resize image
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((100, 100))
        
        # Get all pixels
        pixels = list(img.getdata())
        
        # Count color frequency
        color_counts = Counter(pixels)
        
        # Sort by frequency
        dominant_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return hex colors
        hex_colors = [rgb_to_hex(color[0]) for color in dominant_colors[:num_colors]]
        return hex_colors
    
    except Exception as e:
        print(f"Error extracting colors: {e}")
        return []


def extract_vibrant_colors(image_path: Path) -> dict:
    """
    Extract vibrant colors from image suitable for theming
    
    Returns prominent, saturated colors for:
    - Primary (most prominent)
    - Accent (second most prominent)
    - Secondary (third most prominent)
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((150, 150))
        
        pixels = list(img.getdata())
        
        # Filter by saturation (more saturated = more vibrant)
        vibrant_pixels = []
        for pixel in pixels:
            saturation = get_saturation(pixel)
            brightness = get_brightness(pixel)
            
            # Keep pixels that are:
            # - Not too dark (brightness > 0.1)
            # - Not too light (brightness < 0.95)
            # - Reasonably saturated (saturation > 0.1)
            if 0.1 < brightness < 0.95 and saturation > 0.1:
                vibrant_pixels.append(pixel)
        
        if not vibrant_pixels:
            vibrant_pixels = pixels
        
        # Count vibrant color frequency
        color_counts = Counter(vibrant_pixels)
        dominant = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return as structured dict
        colors = {
            "primary": rgb_to_hex(dominant[0][0]) if len(dominant) > 0 else "#FF3B30",
            "accent": rgb_to_hex(dominant[1][0]) if len(dominant) > 1 else "#D32F2F",
            "secondary": rgb_to_hex(dominant[2][0]) if len(dominant) > 2 else "#1976D2",
        }
        
        return colors
    
    except Exception as e:
        print(f"Error extracting vibrant colors: {e}")
        return {
            "primary": "#FF3B30",
            "accent": "#D32F2F",
            "secondary": "#1976D2",
        }


def get_theme_palette_from_icon() -> dict:
    """
    Get complete theme palette derived from app icon
    
    Returns dict with colors for DARK and LIGHT themes
    """
    icon_path = get_icon_path()
    
    if not icon_path.exists():
        print(f"Icon not found: {icon_path}")
        return _get_default_palette()
    
    # Extract vibrant colors
    icon_colors = extract_vibrant_colors(icon_path)
    
    # Build theme-aware palette
    primary = icon_colors["primary"]
    accent = icon_colors["accent"]
    secondary = icon_colors["secondary"]
    
    palette = {
        "DARK": {
            "primary_color": primary,
            "accent_primary": primary,
            "accent_secondary": accent,
            "accent_tertiary": secondary,
        },
        "LIGHT": {
            "primary_color": primary,
            "accent_primary": primary,
            "accent_secondary": accent,
            "accent_tertiary": secondary,
        }
    }
    
    return palette


def _get_default_palette() -> dict:
    """Get default palette if icon extraction fails"""
    return {
        "DARK": {
            "primary_color": "#FF3B30",
            "accent_primary": "#FF3B30",
            "accent_secondary": "#D32F2F",
            "accent_tertiary": "#1976D2",
        },
        "LIGHT": {
            "primary_color": "#FF3B30",
            "accent_primary": "#FF3B30",
            "accent_secondary": "#D32F2F",
            "accent_tertiary": "#1976D2",
        }
    }


if __name__ == "__main__":
    """Test color extraction"""
    icon_path = get_icon_path()
    
    print(f"Icon path: {icon_path}")
    print(f"Icon exists: {icon_path.exists()}")
    
    if icon_path.exists():
        print("\n=== Dominant Colors ===")
        dominant = extract_dominant_colors(icon_path)
        for i, color in enumerate(dominant, 1):
            print(f"{i}. {color}")
        
        print("\n=== Vibrant Colors ===")
        vibrant = extract_vibrant_colors(icon_path)
        for name, color in vibrant.items():
            print(f"{name.upper()}: {color}")
        
        print("\n=== Theme Palette ===")
        palette = get_theme_palette_from_icon()
        for theme, colors in palette.items():
            print(f"\n{theme}:")
            for name, color in colors.items():
                print(f"  {name}: {color}")
