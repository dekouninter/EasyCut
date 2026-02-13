"""
Font Loader for EasyCut
Loads custom fonts (Inter) from assets folder

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
"""

import sys
import os
from pathlib import Path
import tkinter.font as tkfont
import logging

logger = logging.getLogger(__name__)


def get_base_path():
    """Get base path for assets (works in dev and frozen/PyInstaller mode)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent.parent


def load_custom_fonts():
    """
    Load custom fonts from assets/fonts directory
    
    Returns:
        bool: True if fonts loaded successfully, False otherwise
    """
    try:
        base_path = get_base_path()
        fonts_dir = base_path / "assets" / "fonts" / "Inter" / "extras" / "ttf"
        
        if not fonts_dir.exists():
            logger.warning(f"Fonts directory not found: {fonts_dir}")
            return False
        
        # On Windows, use GDI to load fonts temporarily
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes
            
            # Load Windows GDI functions
            gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
            FR_PRIVATE = 0x10
            
            fonts_loaded = 0
            fonts_to_load = [
                "InterDisplay-Regular.ttf",
                "InterDisplay-Bold.ttf",
                "InterDisplay-Medium.ttf",
                "InterDisplay-SemiBold.ttf",
                "InterDisplay-Light.ttf",
            ]
            
            for font_file in fonts_to_load:
                font_path = fonts_dir / font_file
                if font_path.exists():
                    result = gdi32.AddFontResourceExW(
                        str(font_path),
                        FR_PRIVATE,
                        0
                    )
                    if result > 0:
                        fonts_loaded += 1
                        logger.info(f"✓ Loaded font: {font_file}")
                    else:
                        logger.warning(f"✗ Failed to load font: {font_file}")
            
            if fonts_loaded > 0:
                logger.info(f"Successfully loaded {fonts_loaded} Inter fonts")
                return True
            else:
                logger.warning("No Inter fonts could be loaded")
                return False
        
        else:
            # On macOS/Linux, fonts need to be installed system-wide or use pygame
            logger.warning("Font loading on non-Windows platforms not implemented yet")
            return False
            
    except Exception as e:
        logger.error(f"Error loading custom fonts: {e}")
        return False


def get_available_font(preferred="Inter", fallback="Segoe UI"):
    """
    Get available font name with fallback
    
    Args:
        preferred: Preferred font family name
        fallback: Fallback font family name
        
    Returns:
        str: Available font name
    """
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        available_fonts = list(tkfont.families(root))
        
        # Check for Inter variations
        inter_fonts = [f for f in available_fonts if 'inter' in f.lower()]
        if inter_fonts:
            font_name = inter_fonts[0]
            logger.info(f"Using Inter font: {font_name}")
            root.destroy()
            return font_name
        
        # Check if preferred font is available
        if preferred in available_fonts:
            logger.info(f"Using preferred font: {preferred}")
            root.destroy()
            return preferred
        
        # Use fallback
        logger.info(f"Using fallback font: {fallback}")
        root.destroy()
        return fallback
        
    except Exception as e:
        logger.error(f"Error checking fonts: {e}")
        return fallback


def setup_fonts():
    """
    Setup custom fonts for the application
    
    Returns:
        str: Font family name to use
    """
    # Try to load custom fonts
    fonts_loaded = load_custom_fonts()
    
    # Get best available font
    if fonts_loaded:
        font_name = get_available_font("Inter Display", "Segoe UI")
    else:
        font_name = get_available_font("Inter", "Segoe UI")
    
    logger.info(f"Using font: {font_name}")
    return font_name
