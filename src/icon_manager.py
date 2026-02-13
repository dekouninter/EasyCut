"""
Icon Manager - Carrega ícones Feather e outros assets
Versão simplificada usando apenas emojis/unicode como fallback
"""
import os
from pathlib import Path
from tkinter import PhotoImage
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io

class IconManager:
    """Gerenciador de ícones Feather"""
    
    def __init__(self):
        self.assets_dir = Path(__file__).parent.parent / "assets"
        self.icons_dir = self.assets_dir / "icons"
        self.feather_dir = self.assets_dir / "feather-main" / "icons"
        self.cache = {}
        
    def get_icon(self, name: str, size: int = 16, color: str = None) -> PhotoImage:
        """
        Carrega um ícone
        
        Args:
            name: Nome do ícone (ex: "download", "settings", "github")
            size: Tamanho em pixels (padrão: 16)
            color: Cor em hex (ex: "#5B8CFF") - opcional
            
        Returns:
            PhotoImage para usar em Tkinter ou None
        """
        cache_key = f"{name}_{size}_{color}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Tentar carregar PNG pré-renderizado primeiro
        icon = self._get_png_icon(name, size, color)
        
        if icon:
            self.cache[cache_key] = icon
            return icon
        
        # Fallback para emoji/unicode
        try:
            icon = self._get_emoji_icon(name, size)
            
            if icon:
                self.cache[cache_key] = icon
            
            return icon
        except Exception as e:
            # Se falhar completamente, retornar None
            # (UI deve lidar com isso, talvez mostrando apenas texto)
            return None
    
    def _get_png_icon(self, name: str, size: int, color: str = None) -> PhotoImage:
        """Carrega PNG pré-renderizado"""
        # Tentar buscar com cor específica
        if color:
            theme = "dark" if "E7E9EE" in color or "5B8CFF" in color else "light"
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
        
        # Tentar PNG genérico (sem cor)
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
    
    def _get_emoji_icon(self, name: str, size: int) -> PhotoImage:
        """Cria ícone usando emoji/unicode como fallback"""
        emoji_map = {
            "download": "⬇",
            "upload": "⬆",
            "search": "🔍",
            "settings": "⚙",
            "folder": "📁",
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
            # Criar imagem com emoji
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Usar fonte padrão robusta
            font_size = int(size * 0.8)
            font = None
            
            # Tentar várias fontes
            font_names = [
                "seguiemj.ttf",    # Segoe UI Emoji (Windows)
                "segoeui.ttf",     # Segoe UI
                "arial.ttf",       # Arial
                "C:\\Windows\\Fonts\\seguiemj.ttf",  # Path completo
            ]
            
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except:
                    continue
            
            # Fallback para fonte padrão
            if font is None:
                font = ImageFont.load_default()
            
            # Centralizar texto/emoji
            try:
                bbox = draw.textbbox((0, 0), emoji, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                position = (
                    (size - text_width) // 2 - bbox[0],
                    (size - text_height) // 2 - bbox[1]
                )
            except:
                # Fallback se textbbox não funcionar
                position = (size // 4, size // 4)
            
            # Desenhar com cor padrão
            draw.text(position, emoji, font=font, fill=(150, 150, 150, 255))
            
            photo = ImageTk.PhotoImage(img)
            return photo
            
        except Exception as e:
            print(f"Error creating emoji icon '{name}': {e}")
            # Retornar imagem simples se falhar completamente
            try:
                img = Image.new('RGBA', (size, size), (100, 100, 100, 255))
                photo = ImageTk.PhotoImage(img)
                return photo
            except:
                return None
    
    def get_app_icon(self) -> PhotoImage:
        """Retorna o ícone do app"""
        icon_path = self.assets_dir / "app_icon.png"
        
        if icon_path.exists():
            try:
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                return photo
            except:
                pass
        
        return None
    
    def has_icon(self, name: str) -> bool:
        """Verifica se um ícone existe"""
        return (self.feather_dir / f"{name}.svg").exists()
    
    def list_icons(self) -> list:
        """Lista todos os ícones disponíveis"""
        if not self.feather_dir.exists():
            return []
        
        icons = []
        for icon_file in self.feather_dir.glob("*.svg"):
            icons.append(icon_file.stem)
        
        return sorted(icons)


# Singleton global
icon_manager = IconManager()


# Ícones mapeados para UI do EasyCut
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
    "batch": "layers",
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


def get_ui_icon(icon_key: str, size: int = 16, color: str = None) -> PhotoImage:
    """
    Atalho para pegar ícone mapeado da UI
    
    Args:
        icon_key: Chave do ICON_MAP (ex: "download", "theme_dark")
        size: Tamanho em pixels
        color: Cor opcional
    
    Returns:
        PhotoImage ou None se não encontrado
    """
    feather_name = ICON_MAP.get(icon_key, icon_key)
    return icon_manager.get_icon(feather_name, size, color)
