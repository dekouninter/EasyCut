# -*- coding: utf-8 -*-
"""
Batch Screen

Professional UI for batch downloading multiple YouTube videos simultaneously.
Supports pasting multiple URLs and tracking progress for each download.
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


class BatchScreen(BaseScreen):
    """Batch tab screen - download multiple videos at once"""
    
    def build(self) -> None:
        """Build the batch screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create simple tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"📦 {tr('tab_batch', 'Batch')}")
        
        main = ttk.Frame(tab_frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        self.content = main
        self.frame = tab_frame
        self.tab_data = {"content": main, "frame": tab_frame}
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("tab_batch", "Batch Downloads"),
            icon_name="batch",
            subtitle=tr("batch_subtitle", "Download multiple videos at once")
        )
        
        # === URLS INPUT CARD ===
        urls_card = ModernCard(main, title=tr("batch_urls", "YouTube URLs"))
        urls_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        # Info text
        ttk.Label(
            urls_card,
            text=tr("batch_help", "Paste one URL per line. Up to 50 URLs supported."),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Text area
        text_container = ttk.Frame(urls_card)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        text_scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL)
        self.text_area = tk.Text(
            text_container,
            height=12,
            yscrollcommand=text_scrollbar.set,
            font=(LOADED_FONT_FAMILY, Typography.SIZE_MD),
            wrap=tk.WORD
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.text_area.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons for text area
        text_actions = ttk.Frame(urls_card)
        text_actions.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        ModernButton(
            text_actions,
            text=tr("batch_paste", "Paste from Clipboard"),
            icon_name="paste",
            command=self.on_paste_click,
            variant="secondary",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            text_actions,
            text=tr("batch_clear", "Clear All"),
            icon_name="clear",
            command=self.on_clear_text_click,
            variant="outline",
            width=12
        ).pack(side=tk.LEFT)
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("batch_log", "Batch Progress Log"))
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
            text=tr("batch_download_all", "Start Batch Download"),
            icon_name="download",
            command=self.on_download_all_click,
            variant="primary",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("batch_stop", "Stop All"),
            icon_name="stop",
            command=self.on_stop_all_click,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT)
        
        self.bind_events()
        self.logger.info("BatchScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.logger.info("BatchScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        urls = self.text_area.get(1.0, tk.END).strip().split("\n")
        return {
            "urls": [url.strip() for url in urls if url.strip()]
        }
    
    # Event handlers
    
    def on_paste_click(self):
        """Handle paste from clipboard button click"""
        if self.root_app and hasattr(self.root_app, "batch_paste"):
            self.root_app.batch_paste()
            self.logger.info("Pasted from clipboard")
    
    def on_clear_text_click(self):
        """Handle clear text button click"""
        self.text_area.delete(1.0, tk.END)
        self.logger.info("Batch text cleared")
    
    def on_download_all_click(self):
        """Handle start batch download button click"""
        if self.root_app and hasattr(self.root_app, "start_batch_download"):
            self.root_app.start_batch_download()
            self.logger.info("Batch download started")
    
    def on_stop_all_click(self):
        """Handle stop all button click"""
        if self.root_app and hasattr(self.root_app, "stop_download"):
            self.root_app.stop_download()
            self.logger.info("All downloads stopped")
