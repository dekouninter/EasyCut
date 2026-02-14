# -*- coding: utf-8 -*-
"""
About Screen

Professional information display showing app details, features, technologies,
social links, and credits.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from .base_screen import BaseScreen
from ..factories import TabFactory
from ...theme import ThemeManager
from ...core.logger import get_logger
from ...core.constants import Constants, TranslationKeys

# Third-party
from design_system import Typography, Spacing, Icons
from modern_components import ModernCard, ModernButton, ModernTabHeader
from font_loader import LOADED_FONT_FAMILY

logger = get_logger(__name__)


class AboutScreen(BaseScreen):
    """About tab screen - app information and credits"""
    
    def build(self) -> None:
        """Build the about screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create scrollable tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"ℹ️ {tr('tab_about', 'About')}")
        
        # Scrollable container
        canvas = tk.Canvas(tab_frame, bg=self.design.get_color("bg_primary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scroll
        if self.root_app and hasattr(self.root_app, "enable_mousewheel_scroll"):
            self.root_app.enable_mousewheel_scroll(canvas, scrollable_frame)
        
        # Content frame
        main = ttk.Frame(scrollable_frame, padding=Spacing.XXL)
        main.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)
        
        self.content = main
        self.frame = tab_frame
        self.canvas = canvas
        self.tab_data = {"content": main, "frame": tab_frame, "canvas": canvas}
        
        # === APP TITLE ===
        title_frame = ttk.Frame(main)
        title_frame.pack(pady=(0, Spacing.MD))
        
        ttk.Label(
            title_frame,
            text=tr("about_title", "EasyCut"),
            font=(LOADED_FONT_FAMILY, Typography.SIZE_XXL, "bold"),
            justify=tk.CENTER
        ).pack()
        
        ttk.Label(
            title_frame,
            text=tr("about_subtitle", "🎬 Professional YouTube Downloader & Audio Converter"),
            style="Caption.TLabel",
            justify=tk.CENTER
        ).pack()
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=Spacing.LG)
        
        # === APP INFO CARD ===
        info_card = ModernCard(main, title=tr("about_section_info", "📦 Application Info"))
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_data = [
            ("Version", "1.0.0"),
            ("Author", "Deko Costa"),
            ("License", "GPL-3.0"),
            ("Release", "2026")
        ]
        
        for label, value in info_data:
            row = ttk.Frame(info_card)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === SOCIAL LINKS CARD ===
        social_card = ModernCard(main, title=tr("about_section_links", "💚 Connect & Support"))
        social_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        links = [
            ("🐙 " + tr("about_link_github", "GitHub Repository"), "https://github.com/dekouninter/EasyCut"),
            ("☕ " + tr("about_link_coffee", "Buy Me a Coffee"), "https://buymeacoffee.com/dekocosta"),
            ("💖 " + tr("about_link_kofi", "Support on Ko-fi"), "https://ko-fi.com/dekocosta"),
            ("💸 " + tr("about_link_livepix", "Livepix (Brazil)"), "https://livepix.gg/dekocosta"),
        ]
        
        for label, url in links:
            ModernButton(
                social_card,
                text=label,
                command=lambda u=url: self.open_link(u),
                variant="outline",
                width=30
            ).pack(pady=(0, Spacing.SM), fill=tk.X)
        
        # === FEATURES CARD ===
        features_card = ModernCard(main, title=tr("about_section_features", "✨ Features"))
        features_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        features = [
            "✅ Download videos in multiple qualities (4K to 144p)",
            "✅ Extract audio in MP3, WAV, M4A, OPUS formats",
            "✅ Batch download multiple videos simultaneously",
            "✅ Record live streams with customizable duration",
            "✅ Time range selection for video trimming",
            "✅ Dark and Light theme support",
            "✅ Multi-language support (EN, PT, ES)",
            "✅ Professional icon set (Feather Icons)",
            "✅ Download history tracking"
        ]
        
        for feature in features:
            ttk.Label(
                features_card,
                text=feature,
                style="Caption.TLabel"
            ).pack(anchor=tk.W, pady=(0, Spacing.XS))
        
        # === TECHNOLOGIES CARD ===
        tech_card = ModernCard(main, title=tr("about_section_tech", "🛠️ Technologies & Credits"))
        tech_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        tech_data = [
            ("Core", "Python 3.13 + Tkinter"),
            ("Downloader", "yt-dlp (Unlicense)"),
            ("Converter", "FFmpeg (GPL-2.0+)"),
            ("Security", "keyring (MIT)"),
            ("Icons", "Feather Icons (MIT)"),
            ("Font", "Inter (OFL 1.1)"),
            ("Image", "Pillow (HPND)")
        ]
        
        for label, value in tech_data:
            row = ttk.Frame(tech_card)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === THANKS CARD ===
        thanks_card = ModernCard(main, title=tr("about_section_thanks", "🙏 Special Thanks"))
        thanks_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        thanks_text = tr(
            "about_thanks_text",
            "Thanks to the open-source community, yt-dlp developers, FFmpeg team, and all contributors who make projects like this possible."
        )
        ttk.Label(
            thanks_card,
            text=thanks_text,
            style="Caption.TLabel",
            wraplength=600,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # === FOOTER ===
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=Spacing.LG)
        
        ttk.Label(
            main,
            text=tr("about_footer", "💜 Made with Python | GPL-3.0 License | © 2026 Deko Costa"),
            style="Caption.TLabel"
        ).pack(pady=Spacing.MD)
        
        self.bind_events()
        self.logger.info("AboutScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.logger.info("AboutScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        return {}
    
    # Screen-specific methods
    
    def open_link(self, url: str):
        """Open a URL in the default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            self.logger.info(f"Opened link: {url}")
        except Exception as e:
            self.logger.error(f"Failed to open link {url}: {e}")
