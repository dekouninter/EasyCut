# -*- coding: utf-8 -*-
"""
History Screen

Shows a card-based layout of all download records with status indicators,
dates, and file information.
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
from design_system import Spacing, Icons
from modern_components import ModernCard, ModernButton, ModernTabHeader

logger = get_logger(__name__)


class HistoryScreen(BaseScreen):
    """History tab screen - display download history records"""
    
    def build(self) -> None:
        """Build the history screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create simple tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"📋 {tr('tab_history', 'History')}")
        
        main = ttk.Frame(tab_frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        self.content = main
        self.frame = tab_frame
        self.tab_data = {"content": main, "frame": tab_frame}
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("history_title", "Download History"),
            icon_name="history",
            subtitle=tr("history_subtitle", "Track all your downloads in one place")
        )
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        ModernButton(
            action_frame,
            text=tr("history_update", "Refresh"),
            icon_name="refresh",
            command=self.on_refresh_click,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("history_clear", "Clear History"),
            icon_name="delete",
            command=self.on_clear_click,
            variant="outline",
            width=14
        ).pack(side=tk.LEFT)
        
        # === HISTORY RECORDS CARD ===
        records_card = ModernCard(main, title=tr("history_records", "Download Records"))
        records_card.pack(fill=tk.BOTH, expand=True, pady=(Spacing.MD, 0))
        
        # Create scrollable area for records
        canvas = tk.Canvas(records_card, bg=self.design.get_color("bg_tertiary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(records_card, orient=tk.VERTICAL, command=canvas.yview)
        
        self.records_frame = ttk.Frame(canvas)
        self.records_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.records_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scroll
        if self.root_app and hasattr(self.root_app, "enable_mousewheel_scroll"):
            self.root_app.enable_mousewheel_scroll(canvas, self.records_frame)
        
        self.canvas = canvas
        
        self.bind_events()
        self.load_history()
        self.logger.info("HistoryScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.logger.info("HistoryScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        return {}
    
    # Screen-specific methods
    
    def load_history(self):
        """Load and display download history"""
        if self.root_app and hasattr(self.root_app, "refresh_history"):
            self.root_app.refresh_history()
            self.logger.info("History loaded")
    
    def add_record(self, filename: str, status: str, date: str):
        """Add a history record to the display"""
        # Status emoji
        status_emoji = {
            "success": "✅",
            "error": "❌",
            "pending": "⏳"
        }.get(status, "⏳")
        
        # Create record frame
        record_frame = ttk.Frame(self.records_frame)
        record_frame.pack(fill=tk.X, pady=(0, Spacing.SM), padx=Spacing.SM)
        
        # Record content
        content = ttk.Frame(record_frame)
        content.pack(fill=tk.X)
        
        # Status indicator with emoji
        ttk.Label(content, text=status_emoji, font=("Arial", 14)).pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # File info
        info_frame = ttk.Frame(content)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(info_frame, text=filename, style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Label(info_frame, text=date, style="Caption.TLabel").pack(anchor=tk.W)
        
        self.logger.debug(f"Added record: {filename} ({status})")
    
    # Event handlers
    
    def on_refresh_click(self):
        """Handle refresh button click"""
        self.load_history()
        self.logger.info("History refreshed")
    
    def on_clear_click(self):
        """Handle clear history button click"""
        if self.root_app and hasattr(self.root_app, "clear_history"):
            self.root_app.clear_history()
            self.logger.info("History cleared")
