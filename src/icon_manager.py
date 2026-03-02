"""
Icon Manager - Loads Feather icons and other assets
Simplified version using emoji/unicode as fallback
"""
import os
from pathlib import Path
from tkinter import PhotoImage

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    Image = ImageTk = ImageDraw = ImageFont = None

class IconManager:
    """Feather icon manager"""
    
    def __init__(self):
        self.assets_dir = Path(__file__).parent.parent / "assets"
        self.icons_dir = self.assets_dir / "icons"
        self.feather_dir = self.assets_dir / "feather-main" / "icons"
        self.cache = {}
        
    def get_icon(self, name: str, size: int = 16, color: str = None) -> PhotoImage:
        """
        Load an icon
        
        Args:
            name: Icon name (e.g. "download", "settings", "github")
            size: Size in pixels (default: 16)
            color: Hex color (e.g. "#5B8CFF") - optional
            
        Returns:
            PhotoImage for use in Tkinter or None
        """
        cache_key = f"{name}_{size}_{color}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try loading pre-rendered PNG first
        icon = self._get_png_icon(name, size, color)
        
        if icon:
            self.cache[cache_key] = icon
            return icon
        
        # Fallback to emoji/unicode
        try:
            icon = self._get_emoji_icon(name, size, color)
            
            if icon:
                self.cache[cache_key] = icon
            
            return icon
        except Exception as e:
            # If everything fails, return None
            # (UI should handle this, perhaps showing text only)
            return None
    
    def _get_png_icon(self, name: str, size: int, color: str = None) -> PhotoImage:
        """Load pre-rendered PNG icon"""
        if not _HAS_PIL:
            return None
        # Try to find color-specific variant
        if color:
            theme = "dark" if "E7E9EE" in color or "f85451" in color or "5B8CFF" in color else "light"
            png_path = self.icons_dir / f"{name}_{size}_{theme}.png"
            
            if png_path.exists():
                try:
                    img = Image.open(png_path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    photo = ImageTk.PhotoImage(img)
                    return photo
                except Exception as e:
                    pass
        
        # Try generic PNG (no color)
        png_path = self.icons_dir / f"{name}_{size}.png"
        
        if png_path.exists():
            try:
                img = Image.open(png_path)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                photo = ImageTk.PhotoImage(img)
                return photo
            except Exception as e:
                pass
        
        return None
    
    def _get_emoji_icon(self, name: str, size: int, color: str = None) -> PhotoImage:
        """Create icon using emoji/unicode as fallback"""
        if not _HAS_PIL:
            return None
        emoji_map = {
            "download": "⬇",
            "upload": "⬆",
            "search": "🔍",
            "settings": "⚙",
            "folder": "📁",
            "folder-plus": "📂",
            "file": "📄",
            "music": "🎵",
            "video": "🎬",
            "globe": "🌐",
            "moon": "🌙",
            "sun": "☀",
            "heart": "❤",
            "star": "⭐",
            "check-circle": "✓",
            "x-circle": "✗",
            "alert-triangle": "⚠",
            "info": "ℹ",
            "log-in": "→",
            "log-out": "←",
            "refresh-cw": "↻",
            "trash-2": "🗑",
            "clock": "🕐",
            "calendar": "📅",
            "github": "🐙",
            "coffee": "☕",
            "play-circle": "▶",
            "stop-circle": "⏹",
            "circle": "⏺",
            "radio": "📻",
            "layers": "☰",
            "clipboard": "📋",
            "external-link": "↗",
            "sliders": "🎛",
            "loader": "⟳",
        }
        
        emoji = emoji_map.get(name, "•")
        
        try:
            # Create image with emoji fallback
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Use robust default font
            font_size = int(size * 0.8)
            font = None
            
            # Try several fonts
            font_names = [
                "seguiemj.ttf",    # Segoe UI Emoji (Windows)
                "segoeui.ttf",     # Segoe UI
                "arial.ttf",       # Arial
                str(Path(os.environ.get('WINDIR', 'C:\\Windows')) / "Fonts" / "seguiemj.ttf"),
            ]
            
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except Exception:
                    continue
            
            # Fallback to default font
            if font is None:
                font = ImageFont.load_default()
            
            # Center text/emoji
            try:
                bbox = draw.textbbox((0, 0), emoji, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                position = (
                    (size - text_width) // 2 - bbox[0],
                    (size - text_height) // 2 - bbox[1]
                )
            except Exception:
                # Fallback if textbbox fails
                position = (size // 4, size // 4)
            
            # Draw with theme color (or default)
            if color:
                # Convert hex to RGBA tuple
                try:
                    c = color.lstrip('#')
                    fill_color = tuple(int(c[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                except Exception:
                    fill_color = (150, 150, 150, 255)
            else:
                fill_color = (150, 150, 150, 255)
            draw.text(position, emoji, font=font, fill=fill_color)
            
            photo = ImageTk.PhotoImage(img)
            return photo
            
        except Exception as e:
            print(f"Error creating emoji icon '{name}': {e}")
            # Return simple fallback image if complete failure
            try:
                img = Image.new('RGBA', (size, size), (100, 100, 100, 255))
                photo = ImageTk.PhotoImage(img)
                return photo
            except Exception:
                return None
    

# Singleton global
icon_manager = IconManager()


# Icons mapped for EasyCut UI
ICON_MAP = {
    # Header
    "theme_dark": "moon",
    "theme_light": "sun",
    "login": "log-in",
    "logout": "log-out",
    "folder": "folder",
    "language": "globe",
    
    # Download Tab
    "verify": "search",
    "download": "download",
    "clipboard": "clipboard",
    "audio": "music",
    "video": "video",
    "quality": "sliders",
    
    # Live Tab
    "live": "radio",
    "record": "circle",
    "stop": "stop-circle",
    "play": "play-circle",
    
    # Batch Tab
    "batch": "copy",
    "paste": "clipboard",
    "clear": "x-circle",
    
    # History Tab
    "history": "clock",
    "refresh": "refresh-cw",
    "delete": "trash-2",
    "open": "external-link",
    
    # About Tab
    "info": "info",
    "github": "github",
    "coffee": "coffee",
    "heart": "heart",
    
    # Status
    "success": "check-circle",
    "error": "x-circle",
    "warning": "alert-triangle",
    "loading": "loader",
}


# Global theme state for icons
_current_dark_mode = True

def set_icon_theme(dark_mode: bool):
    """Update global theme used for icon colors"""
    global _current_dark_mode
    _current_dark_mode = dark_mode
    # Clear cache to reload icons with new colors
    icon_manager.cache.clear()


def get_ui_icon(icon_key: str, size: int = 16, color: str = None, theme: str = None) -> PhotoImage:
    """
    Shortcut to get mapped UI icon with smart theme colors
    
    Args:
        icon_key: Key from ICON_MAP (e.g. "download", "theme_dark")
        size: Size in pixels
        color: Optional color (if None, uses default theme color)
        theme: Theme ("dark" or "light") - if None, uses global state
    
    Returns:
        PhotoImage or None if not found
    """
    feather_name = ICON_MAP.get(icon_key, icon_key)
    
    # If no color specified, use current theme default
    if not color:
        try:
            from design_system import DesignTokens
            is_dark = _current_dark_mode if theme is None else (theme == "dark")
            tokens = DesignTokens(dark_mode=is_dark)
            color = tokens.get_color("icon_primary")
        except Exception:
            pass
    
    return icon_manager.get_icon(feather_name, size, color)
