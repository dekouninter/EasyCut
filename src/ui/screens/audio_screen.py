# -*- coding: utf-8 -*-
"""
Audio Screen

Professional UI for extracting and converting audio from YouTube videos
to various formats (MP3, WAV, M4A, OPUS) with quality options.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from .base_screen import BaseScreen
from ..factories import TabFactory
from ..theme import ThemeManager
from ...core.logger import get_logger
from ...core.constants import Constants, TranslationKeys

# Third-party
from design_system import Typography, Spacing, Icons
from modern_components import ModernCard, ModernButton, ModernTabHeader
from ui_enhanced import LogWidget
from font_loader import LOADED_FONT_FAMILY

logger = get_logger(__name__)


class AudioScreen(BaseScreen):
    """Audio conversion tab screen - extract and convert audio from YouTube"""
    
    def build(self) -> None:
        """Build the audio screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create simple tab (no scrolling needed for audio tab)
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"🎵 {tr('tab_audio', 'Audio')}")
        
        main = ttk.Frame(tab_frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        self.content = main
        self.frame = tab_frame
        self.tab_data = {"content": main, "frame": tab_frame}
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("audio_title", "Audio Converter"),
            icon_name="music",
            subtitle=tr("audio_subtitle", "Extract and convert audio from YouTube videos")
        )
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("audio_url", "YouTube URL"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_row = ttk.Frame(url_card)
        url_row.pack(fill=tk.X)
        
        url_icon_label = ttk.Label(url_row, text="🎵", font=("Segoe UI", 12), style="TLabel")
        url_icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.url_entry = ttk.Entry(url_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === FORMAT CARD ===
        format_card = ModernCard(main, title=tr("audio_format", "Audio Format"))
        format_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.format_var = tk.StringVar(value="mp3")
        
        format_options = [("MP3", "mp3", "🎵"), ("WAV", "wav", "🎼"), ("M4A", "m4a", "🎶"), ("OPUS", "opus", "🎸")]
        
        format_grid = ttk.Frame(format_card)
        format_grid.pack(fill=tk.X)
        
        for i, (label, value, icon) in enumerate(format_options):
            format_frame = ttk.Frame(format_grid)
            format_frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0 if i%2==0 else Spacing.XL, 0), pady=(0, Spacing.XS))
            ttk.Label(format_frame, text=icon, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, Spacing.SM))
            ttk.Radiobutton(format_frame, text=label, variable=self.format_var, value=value).pack(side=tk.LEFT)
        
        # === BITRATE CARD ===
        bitrate_card = ModernCard(main, title=tr("audio_bitrate", "Audio Quality (Bitrate)"))
        bitrate_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.bitrate_var = tk.StringVar(value="320")
        
        bitrate_options = [("128", "📻 Standard"), ("192", "🎧 Good"), ("256", "⭐ High"), ("320", "💎 Best")]
        
        bitrate_grid = ttk.Frame(bitrate_card)
        bitrate_grid.pack(fill=tk.X)
        
        for i, (value, label) in enumerate(bitrate_options):
            bitrate_frame = ttk.Frame(bitrate_grid)
            bitrate_frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0 if i%2==0 else Spacing.XL, 0), pady=(0, Spacing.XS))
            ttk.Radiobutton(bitrate_frame, text=f"{label} ({value} kbps)", variable=self.bitrate_var, value=value).pack(side=tk.LEFT)
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("audio_log", "Conversion Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log = LogWidget(log_container, theme=self.design, height=8)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log.yview)
        self.log.config(yscrollcommand=log_scrollbar.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("audio_convert", "Convert & Download"),
            icon_name="music",
            command=self.on_convert_click,
            variant="primary",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_clear_log", "Clear Log"),
            icon_name="clear",
            command=self.on_clear_log_click,
            variant="outline",
            width=12
        ).pack(side=tk.LEFT)
        
        self.bind_events()
        self.logger.info("AudioScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.url_entry.bind("<Return>", lambda e: self.on_convert_click())
        self.logger.info("AudioScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        return {
            "url": self.url_entry.get(),
            "format": self.format_var.get(),
            "bitrate": self.bitrate_var.get()
        }
    
    # Event handlers
    
    def on_convert_click(self):
        """Handle convert button click"""
        if self.root_app and hasattr(self.root_app, "start_audio_conversion"):
            self.root_app.start_audio_conversion()
            self.logger.info("Audio conversion started")
    
    def on_clear_log_click(self):
        """Handle clear log button click"""
        self.log.clear()
        self.logger.info("Audio log cleared")
