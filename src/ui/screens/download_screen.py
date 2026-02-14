# -*- coding: utf-8 -*-
"""
Download Screen

Professional UI for downloading YouTube videos with multiple quality/format options.
Provides real-time logging and status updates during downloads.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from .base_screen import BaseScreen
from ..factories import TabFactory, CanvasScrollFactory
from ...theme import ThemeManager
from ...core.logger import get_logger
from ...core.constants import Constants, TranslationKeys

# Third-party
from icon_manager import get_ui_icon
from design_system import Typography, Spacing, Icons
from modern_components import ModernCard, ModernButton, ModernTabHeader
from ui_enhanced import LogWidget

logger = get_logger(__name__)


class DownloadScreen(BaseScreen):
    """Download tab screen - download videos from YouTube"""
    
    def build(self) -> None:
        """Build the download screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")  # Reference to main app
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create scrollable tab
        self.tab_data = TabFactory.create_scrollable_tab(
            self.notebook,
            "Download",
            self.theme,
            "⬇️"
        )
        
        self.content = self.tab_data["content"]
        canvas = self.tab_data["canvas"]
        
        # Enable mouse wheel scroll
        if self.root_app and hasattr(self.root_app, "enable_mousewheel_scroll"):
            self.root_app.enable_mousewheel_scroll(canvas, self.content)
        
        # === TAB HEADER ===
        ModernTabHeader(
            self.content,
            title=tr("tab_download", "Download"),
            icon_name="download",
            subtitle=tr("download_subtitle", "Download videos and audio from YouTube")
        )
        
        # === URL INPUT CARD ===
        url_card = ModernCard(self.content, title=tr("download_url", "YouTube URL"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_container = ttk.Frame(url_card)
        url_container.pack(fill=tk.X)
        
        # URL input with icon
        input_frame = ttk.Frame(url_container)
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        url_icon = get_ui_icon("video", size=Icons.SIZE_SM)
        if url_icon:
            url_icon_label = ttk.Label(input_frame, image=url_icon)
            url_icon_label.image = url_icon
            url_icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.url_entry = ttk.Entry(input_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Verify button
        ModernButton(
            url_container,
            text=tr("download_verify", "Verify"),
            icon_name="verify",
            command=self.on_verify_click,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT)
        
        # === VIDEO INFO CARD ===
        info_card = ModernCard(self.content, title=tr("download_info", "Video Information"))
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_grid = ttk.Frame(info_card)
        info_grid.pack(fill=tk.X)
        
        # Title row
        ttk.Label(info_grid, text=f"{tr('download_title', 'Title')}:", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.title_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.title_label.grid(row=0, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Duration row
        ttk.Label(info_grid, text=f"{tr('download_duration', 'Duration')}:", style="Subtitle.TLabel").grid(
            row=1, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.duration_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.duration_label.grid(row=1, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # === DOWNLOAD MODE CARD ===
        mode_card = ModernCard(self.content, title=tr("download_mode", "Download Mode"))
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.mode_var = tk.StringVar(value="full")
        
        modes = [
            ("full", tr("download_mode_full", "Complete Video"), "video"),
            ("range", tr("download_mode_range", "Time Range"), "clock"),
            ("until", tr("download_mode_until", "Until Time"), "clock"),
            ("audio", tr("download_mode_audio", "Audio Only"), "music")
        ]
        
        for value, text, icon_name in modes:
            mode_frame = ttk.Frame(mode_card)
            mode_frame.pack(fill=tk.X, pady=Spacing.XS)
            
            icon = get_ui_icon(icon_name, size=Icons.SIZE_SM)
            if icon:
                icon_label = ttk.Label(mode_frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value
            ).pack(side=tk.LEFT)
        
        # === TIME RANGE CARD ===
        time_card = ModernCard(self.content, title=tr("download_time_range", "Time Range"))
        time_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        time_grid = ttk.Frame(time_card)
        time_grid.pack(fill=tk.X)
        
        # Start time
        ttk.Label(time_grid, text=f"{tr('download_start_time', 'Start Time')}:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, Spacing.SM), pady=Spacing.XS
        )
        self.start_time_entry = ttk.Entry(time_grid, width=12)
        self.start_time_entry.insert(0, "00:00:00")
        self.start_time_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, Spacing.XL), pady=Spacing.XS)
        
        # End time
        ttk.Label(time_grid, text=f"{tr('download_end_time', 'End Time')}:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, Spacing.SM), pady=Spacing.XS
        )
        self.end_time_entry = ttk.Entry(time_grid, width=12)
        self.end_time_entry.insert(0, "00:00:00")
        self.end_time_entry.grid(row=0, column=3, sticky=tk.W, pady=Spacing.XS)
        
        # Help text
        ttk.Label(
            time_card,
            text=tr("download_time_help", "Format: HH:MM:SS or MM:SS"),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(Spacing.SM, 0))
        
        # === QUALITY CARD ===
        quality_card = ModernCard(self.content, title=tr("download_quality", "Quality"))
        quality_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.quality_var = tk.StringVar(value="best")
        
        qualities = [
            ("best", tr("download_quality_best", "Best Quality"), "⭐"),
            ("mp4", tr("download_quality_mp4", "MP4 (Best)"), "🎬"),
            ("1080", "1080p Full HD", "📺"),
            ("720", "720p HD", "📱")
        ]
        
        quality_grid = ttk.Frame(quality_card)
        quality_grid.pack(fill=tk.X)
        
        for i, (value, text, emoji) in enumerate(qualities):
            ttk.Radiobutton(
                quality_grid,
                text=f"{emoji} {text}",
                variable=self.quality_var,
                value=value
            ).grid(row=i//2, column=i%2, sticky=tk.W, padx=Spacing.MD, pady=Spacing.XS)
        
        # === AUDIO FORMAT CARD ===
        audio_card = ModernCard(self.content, title=tr("audio_format", "Audio Format"))
        audio_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Format selection
        self.format_var = tk.StringVar(value="mp3")
        
        fmt_frame = ttk.Frame(audio_card)
        fmt_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        formats = [("mp3", "MP3"), ("wav", "WAV"), ("m4a", "M4A"), ("opus", "OPUS")]
        for value, text in formats:
            ttk.Radiobutton(
                fmt_frame,
                text=text,
                variable=self.format_var,
                value=value
            ).pack(side=tk.LEFT, padx=(0, Spacing.LG))
        
        # Bitrate selection
        ttk.Label(audio_card, text=f"🎵 {tr('audio_bitrate', 'Bitrate')}:", style="Subtitle.TLabel").pack(
            anchor=tk.W, pady=(Spacing.SM, Spacing.XS)
        )
        
        self.bitrate_var = tk.StringVar(value="320")
        
        bitrate_frame = ttk.Frame(audio_card)
        bitrate_frame.pack(fill=tk.X)
        
        for br in ["128", "192", "256", "320"]:
            ttk.Radiobutton(
                bitrate_frame,
                text=f"{br} kbps",
                variable=self.bitrate_var,
                value=br
            ).pack(side=tk.LEFT, padx=(0, Spacing.LG))
        
        # === LOG CARD ===
        log_card = ModernCard(self.content, title=tr("download_log", "Activity Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log = LogWidget(log_container, theme=self.design, height=8)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log.yview)
        self.log.config(yscrollcommand=log_scrollbar.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(self.content)
        action_frame.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        self.download_btn = ModernButton(
            action_frame,
            text=tr("download_btn", "Download"),
            icon_name="download",
            command=self.on_download_click,
            variant="primary",
            width=14
        )
        self.download_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.stop_btn = ModernButton(
            action_frame,
            text=tr("download_stop", "Stop"),
            icon_name="stop",
            command=self.on_stop_click,
            variant="secondary",
            width=14
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_clear_log", "Clear Log"),
            icon_name="clear",
            command=self.on_clear_log_click,
            variant="outline",
            width=14
        ).pack(side=tk.LEFT)
        
        self.bind_events()
        self.logger.info("DownloadScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.url_entry.bind("<Return>", self.on_verify_click)
        self.logger.info("DownloadScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        return {
            "url": self.url_entry.get(),
            "mode": self.mode_var.get(),
            "quality": self.quality_var.get(),
            "format": self.format_var.get(),
            "bitrate": self.bitrate_var.get(),
            "start_time": self.start_time_entry.get(),
            "end_time": self.end_time_entry.get()
        }
    
    # Event handlers
    
    def on_verify_click(self, event=None):
        """Handle verify button click"""
        if self.root_app and hasattr(self.root_app, "verify_video"):
            self.root_app.verify_video()
            self.logger.info("Verify video called")
    
    def on_download_click(self):
        """Handle download button click"""
        if self.root_app and hasattr(self.root_app, "start_download"):
            self.root_app.start_download()
            self.logger.info("Download started")
    
    def on_stop_click(self):
        """Handle stop button click"""
        if self.root_app and hasattr(self.root_app, "stop_download"):
            self.root_app.stop_download()
            self.logger.info("Download stopped")
    
    def on_clear_log_click(self):
        """Handle clear log button click"""
        self.log.clear()
        self.logger.info("Download log cleared")
