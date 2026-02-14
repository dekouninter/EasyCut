# -*- coding: utf-8 -*-
"""
Live Screen

Professional UI for recording YouTube Live streams with customizable duration,
quality settings, and real-time progress tracking.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from ui.screens.base_screen import BaseScreen
from ui.factories import TabFactory
from theme import ThemeManager
from core.logger import get_logger
from core.constants import Constants, TranslationKeys

# Third-party
from design_system import Typography, Spacing, Icons
from modern_components import ModernCard, ModernButton, ModernTabHeader
from ui_enhanced import LogWidget
from font_loader import LOADED_FONT_FAMILY

logger = get_logger(__name__)


class LiveScreen(BaseScreen):
    """Live tab screen - record live streams from YouTube"""
    
    def build(self) -> None:
        """Build the live screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create simple tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"🔴 {tr('tab_live', 'Live')}")
        
        main = ttk.Frame(tab_frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        self.content = main
        self.frame = tab_frame
        self.tab_data = {"content": main, "frame": tab_frame}
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("live_title", "Live Stream Recorder"),
            icon_name="record",
            subtitle=tr("live_subtitle", "Record live streams with customizable duration and quality")
        )
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("live_url", "Live Stream URL"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_row = ttk.Frame(url_card)
        url_row.pack(fill=tk.X)
        
        url_icon_label = ttk.Label(url_row, text="📡", font=("Segoe UI", 12), style="TLabel")
        url_icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.url_entry = ttk.Entry(url_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        ModernButton(
            url_row,
            text=tr("live_check_stream", "Check"),
            icon_name="verify",
            command=self.on_check_stream_click,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT)
        
        # === STREAM STATUS CARD ===
        status_card = ModernCard(main, title=tr("live_status", "Stream Status"))
        status_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        status_grid = ttk.Frame(status_card)
        status_grid.pack(fill=tk.X)
        
        ttk.Label(status_grid, text=f"{tr('live_status', 'Status')}:", style="Subtitle.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, Spacing.XL))
        self.status_label = ttk.Label(status_grid, text=tr("live_status_unknown", "⚠️ UNKNOWN"), style="Caption.TLabel")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_grid, text=f"{tr('live_duration', 'Duration')}:", style="Subtitle.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, Spacing.XL), pady=(Spacing.SM, 0))
        self.duration_label = ttk.Label(status_grid, text="--:--:--", style="Caption.TLabel")
        self.duration_label.grid(row=1, column=1, sticky=tk.W, pady=(Spacing.SM, 0))
        
        # === RECORDING MODE CARD ===
        mode_card = ModernCard(main, title=tr("live_mode", "Recording Mode"))
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.mode_var = tk.StringVar(value="continuous")
        
        mode_options = [
            ("continuous", tr("live_mode_continuous", "Continuous Recording"), "∞"),
            ("duration", tr("live_mode_duration", "Record Duration"), "⏱️"),
            ("until", tr("live_mode_until", "Record Until Time"), "⏰")
        ]
        
        for value, label, icon in mode_options:
            mode_frame = ttk.Frame(mode_card)
            mode_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(mode_frame, text=icon, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, Spacing.SM))
            ttk.Radiobutton(mode_frame, text=label, variable=self.mode_var, value=value).pack(side=tk.LEFT, anchor=tk.W)
        
        # === DURATION CARD ===
        duration_card = ModernCard(main, title=tr("live_duration_settings", "Duration Settings"))
        duration_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        duration_grid = ttk.Frame(duration_card)
        duration_grid.pack(fill=tk.X)
        
        for i, (key, default) in enumerate([("live_hours", "01"), ("live_minutes", "00"), ("live_seconds", "00")]):
            ttk.Label(duration_grid, text=f"{tr(key, key.split('_')[1].title())}:", style="Caption.TLabel").grid(row=0, column=i*2, sticky=tk.W, padx=(0 if i==0 else Spacing.MD, Spacing.XS))
            entry = ttk.Entry(duration_grid, width=6, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
            entry.insert(0, default)
            entry.grid(row=0, column=i*2+1, sticky=tk.W)
            setattr(self, f"{key}_entry", entry)
        
        # === QUALITY CARD ===
        quality_card = ModernCard(main, title=tr("live_quality", "Recording Quality"))
        quality_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.quality_var = tk.StringVar(value="best")
        
        quality_options = [
            ("best", tr("live_quality_best", "Best Available"), "⭐"),
            ("1080", "1080p Full HD", "🎬"),
            ("720", "720p HD", "📺"),
            ("480", "480p SD", "📱")
        ]
        
        quality_grid = ttk.Frame(quality_card)
        quality_grid.pack(fill=tk.X)
        
        for i, (value, label, icon) in enumerate(quality_options):
            quality_frame = ttk.Frame(quality_grid)
            quality_frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0 if i%2==0 else Spacing.XL, 0), pady=(0, Spacing.XS))
            ttk.Label(quality_frame, text=icon, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, Spacing.SM))
            ttk.Radiobutton(quality_frame, text=label, variable=self.quality_var, value=value).pack(side=tk.LEFT)
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("live_log", "Recording Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.log = LogWidget(log_container, theme=self.design, height=6)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.log.yview)
        self.log.config(yscrollcommand=log_scrollbar.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("live_start_recording", "Start Recording"),
            icon_name="record",
            command=self.on_start_recording_click,
            variant="primary",
            width=18
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("live_stop_recording", "Stop"),
            icon_name="stop",
            command=self.on_stop_recording_click,
            variant="secondary",
            width=12
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
        self.logger.info("LiveScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.url_entry.bind("<Return>", lambda e: self.on_check_stream_click())
        self.logger.info("LiveScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        return {
            "url": self.url_entry.get(),
            "mode": self.mode_var.get(),
            "quality": self.quality_var.get(),
            "hours": self.live_hours_entry.get(),
            "minutes": self.live_minutes_entry.get(),
            "seconds": self.live_seconds_entry.get()
        }
    
    # Event handlers
    
    def on_check_stream_click(self):
        """Handle check stream button click"""
        if self.root_app and hasattr(self.root_app, "verify_live_stream"):
            self.root_app.verify_live_stream()
            self.logger.info("Live stream verification requested")
    
    def on_start_recording_click(self):
        """Handle start recording button click"""
        if self.root_app and hasattr(self.root_app, "start_live_recording"):
            self.root_app.start_live_recording()
            self.logger.info("Live recording started")
    
    def on_stop_recording_click(self):
        """Handle stop recording button click"""
        if self.root_app and hasattr(self.root_app, "stop_live_recording"):
            self.root_app.stop_live_recording()
            self.logger.info("Live recording stopped")
    
    def on_clear_log_click(self):
        """Handle clear log button click"""
        self.log.clear()
        self.logger.info("Live log cleared")
