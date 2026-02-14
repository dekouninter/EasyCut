# -*- coding: utf-8 -*-
"""
Login Screen

Authentication tab for managing YouTube login credentials securely
using Windows Keyring.
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
from design_system import Typography, Spacing
from modern_components import ModernButton
from font_loader import LOADED_FONT_FAMILY

logger = get_logger(__name__)


class LoginScreen(BaseScreen):
    """Login tab screen - authentication and credential management"""
    
    def build(self) -> None:
        """Build the login screen UI"""
        # Access translator from kwargs
        self.translator = self.kwargs.get("translator")
        self.design = self.kwargs.get("design")
        self.root_app = self.kwargs.get("app")
        
        tr = self.translator.get if self.translator else lambda k, d: d
        
        # Create simple tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"🔐 {tr('tab_login', 'Login')}")
        
        container = ttk.Frame(tab_frame, padding=40)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.content = container
        self.frame = tab_frame
        self.tab_data = {"content": container, "frame": tab_frame}
        
        # === TITLE ===
        ttk.Label(
            container,
            text=tr("login_tab_title", "Authentication"),
            font=(LOADED_FONT_FAMILY, 16, "bold"),
            style="TLabel"
        ).pack(pady=10)
        
        # === LOGIN STATUS ===
        self.status_label = ttk.Label(
            container,
            text=self.get_login_status(),
            font=(LOADED_FONT_FAMILY, 11),
            style="TLabel"
        )
        self.status_label.pack(pady=20)
        
        # === BUTTONS ===
        ModernButton(
            container,
            text=tr("login_popup_btn", "Login (Popup)"),
            command=self.on_login_click,
            width=20
        ).pack(pady=5)
        
        ModernButton(
            container,
            text=tr("login_logout_btn", "Logout"),
            command=self.on_logout_click,
            width=20
        ).pack(pady=5)
        
        # === INFO ===
        ttk.Label(
            container,
            text=tr("login_tab_info", "Use popup login for secure authentication\nCredentials are stored securely using Windows Keyring"),
            justify=tk.CENTER,
            wraplength=400
        ).pack(pady=20)
        
        self.bind_events()
        self.logger.info("LoginScreen built successfully")
    
    def bind_events(self) -> None:
        """Bind UI events"""
        self.logger.info("LoginScreen events bound")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current screen data"""
        return {
            "login_status": self.get_login_status()
        }
    
    # Screen-specific methods
    
    def get_login_status(self) -> str:
        """Get current login status message"""
        if self.root_app and hasattr(self.root_app, "get_login_status"):
            return self.root_app.get_login_status()
        return "⚠️ Not logged in"
    
    def update_status(self):
        """Update login status label"""
        self.status_label.config(text=self.get_login_status())
        self.logger.info("Login status updated")
    
    # Event handlers
    
    def on_login_click(self):
        """Handle login button click"""
        if self.root_app and hasattr(self.root_app, "open_login_popup"):
            self.root_app.open_login_popup()
            self.update_status()
            self.logger.info("Login popup opened")
    
    def on_logout_click(self):
        """Handle logout button click"""
        if self.root_app and hasattr(self.root_app, "do_logout"):
            self.root_app.do_logout()
            self.update_status()
            self.logger.info("User logged out")
