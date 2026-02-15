# -*- coding: utf-8 -*-
"""
Professional Donation System for EasyCut
Manages donation links and support interface with professional UI

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
License: GPL-3.0

Features:
- Multiple donation platforms (Buy Me a Coffee, Livepix)
- Professional modal presentation
- Hover effects and animations
- Floating action button
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from i18n import translator as t

try:
    from font_loader import LOADED_FONT_FAMILY
except ImportError:
    LOADED_FONT_FAMILY = "Segoe UI"

try:
    from design_system import DesignTokens
except ImportError:
    DesignTokens = None


class DonationWindow:
    """Professional Donation Support Window
    
    Displays available donation platforms with professional UI
    and links to support the EasyCut project development.
    """
    
    def __init__(self, parent):
        """Initialize donation window
        
        Args:
            parent: Parent window reference
        """
        self.parent = parent
        self.window = None
        self.donation_links = {
            "coffee": {
                "name": "Buy Me a Coffee",
                "url": "https://buymeacoffee.com/dekocosta",
                "icon": "☕"
            },
            "livepix": {
                "name": "Livepix",
                "url": "https://livepix.gg/dekocosta",
                "icon": "🎁"
            }
        }
    
    def open_donation_window(self):
        """Display donation window with support options"""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title(t("donation_title"))
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Center window on parent
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=t("donation_title"),
            font=(LOADED_FONT_FAMILY, 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text=t("donation_description"),
            wraplength=360,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10)
        
        # Get accent color from theme
        accent = "#4A90D9"
        accent_hover = "#3A7BC8"
        try:
            tokens = DesignTokens()
            accent = tokens.get_color("accent_primary")
            accent_hover = tokens.get_color("accent_hover")
        except Exception:
            pass  # Use defaults
        
        # Donation platform buttons
        for key, donation in self.donation_links.items():
            btn = tk.Button(
                buttons_frame,
                text=f"{donation['icon']} {donation['name']}",
                command=lambda url=donation['url']: self.open_link(url),
                bg=accent,
                fg="white",
                font=(LOADED_FONT_FAMILY, 11, "bold"),
                cursor="hand2",
                padx=15,
                pady=10,
                relief=tk.RAISED,
                bd=2
            )
            btn.pack(pady=8, fill=tk.X)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn, h=accent_hover: b.config(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, a=accent: b.config(bg=a))
        
        # Thank you message
        thanks_label = ttk.Label(
            main_frame,
            text="Thank you for supporting EasyCut Development!",
            wraplength=360,
            justify=tk.CENTER,
            font=(LOADED_FONT_FAMILY, 9, "italic")
        )
        thanks_label.pack(pady=(20, 0))
    
    def open_link(self, url):
        """Open donation link in default web browser
        
        Args:
            url (str): Link URL to open
        """
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening link: {e}")


class DonationButton:
    """Floating Action Button for Donations
    
    Provides quick access to donation options with floating
    action button placement and hover animations.
    """
    
    def __init__(self, parent):
        """Initialize donation button
        
        Args:
            parent: Parent window reference
        """
        self.parent = parent
        self.button = None
        self.donation_window = DonationWindow(parent)
    
    def create_floating_button(self, root_window):
        """Create floating donation action button
        
        Args:
            root_window: Root window for button placement
        """
        # Get accent color from theme
        accent = "#4A90D9"
        accent_hover = "#3A7BC8"
        try:
            tokens = DesignTokens()
            accent = tokens.get_color("accent_primary")
            accent_hover = tokens.get_color("accent_hover")
        except Exception:
            pass  # Use defaults
        
        # Floating button frame
        floating_frame = ttk.Frame(root_window)
        floating_frame.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
        
        # Donation button
        self.button = tk.Button(
            floating_frame,
            text="❤️ Support Development",
            command=self.open_donation,
            bg=accent,
            fg="white",
            font=(LOADED_FONT_FAMILY, 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=6,
            relief=tk.RAISED,
            bd=2
        )
        self.button.pack()
        
        # Hover effects
        self.button.bind("<Enter>", lambda e: self.button.config(bg=accent_hover))
        self.button.bind("<Leave>", lambda e: self.button.config(bg=accent))
    
    def open_donation(self):
        """Open donation window when button clicked"""
        self.donation_window.open_donation_window()
