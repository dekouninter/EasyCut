# -*- coding: utf-8 -*-
"""
Enhanced UI Components Module for EasyCut
Professional User Interface with Theme and Configuration Management

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.0.0
License: MIT

This module provides:
- Theme Manager: Dark/Light theme with instant hot-reload
- Configuration Manager: Persistent JSON-based settings
- Login Popup: Professional authentication dialog
- Language Selector: Multi-language dropdown/menu
- Log Widget: Auto-scrolling logging display
- Status Bar: Real-time application status
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os
from pathlib import Path


class Theme:
    """Professional Theme Manager for Dark/Light Mode Support
    
    Manages color schemes and theme switching with instant hot-reload.
    Supports both native Tkinter and ttk widget styling.
    """
    
    BASE_FONT = ("Segoe UI", 10)
    TITLE_FONT = ("Segoe UI", 14, "bold")
    SMALL_FONT = ("Segoe UI", 9)

    LIGHT_THEME = {
        "bg": "#FFFFFF",
        "fg": "#0D0D0D",
        "muted": "#404040",
        "accent": "#f85451",
        "accent_hover": "#E84037",
        "bg_button": "#EFEFEF",
        "fg_button": "#0D0D0D",
        "bg_entry": "#FFFFFF",
        "fg_entry": "#0D0D0D",
        "bg_frame": "#F3F3F3",
        "card_bg": "#FFFFFF",
        "border": "#CCCCCC",
    }
    
    DARK_THEME = {
        "bg": "#0F1115",
        "fg": "#E7E9EE",
        "muted": "#9AA4B2",
        "accent": "#f85451",
        "accent_hover": "#E83E3A",
        "bg_button": "#1A1E26",
        "fg_button": "#E7E9EE",
        "bg_entry": "#141820",
        "fg_entry": "#E7E9EE",
        "bg_frame": "#12161D",
        "card_bg": "#151A22",
        "border": "#2A2F3A",
    }
    
    def __init__(self, dark_mode=False):
        """Initialize theme manager with default mode"""
        self.dark_mode = dark_mode
        self.current_theme = self.DARK_THEME if dark_mode else self.LIGHT_THEME
    
    def get(self, key):
        """Get color value from current theme
        
        Args:
            key (str): Color key name
            
        Returns:
            str: Hex color code
        """
        return self.current_theme.get(key, "#000000")
    
    def toggle(self):
        """Toggle between dark and light themes with instant reload
        
        Returns:
            bool: New dark_mode state
        """
        self.dark_mode = not self.dark_mode
        self.current_theme = self.DARK_THEME if self.dark_mode else self.LIGHT_THEME
        return self.dark_mode
    
    def get_style(self):
        """Get complete current theme dictionary
        
        Returns:
            dict: Current theme color mapping
        """
        return self.current_theme.copy()
    
    def get_ttk_style(self):
        """Create ttk style object based on current theme
        
        Configures all ttk widgets with theme colors
        
        Returns:
            ttk.Style: Configured style object
        """
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('.', font=self.BASE_FONT)
        style.configure('TFrame', background=self.get("bg"))
        style.configure('TLabel', background=self.get("bg"), foreground=self.get("fg"))
        style.configure('TButton', background=self.get("bg_button"), foreground=self.get("fg_button"), padding=(10, 6))
        style.map('TButton', background=[('active', self.get("accent"))])
        style.configure('TEntry', fieldbackground=self.get("bg_entry"), foreground=self.get("fg_entry"), padding=(6, 4))
        style.configure('TCombobox', fieldbackground=self.get("bg_entry"), foreground=self.get("fg_entry"))
        style.configure('TNotebook', background=self.get("bg"), tabmargins=(6, 4, 6, 0))
        style.configure('TNotebook.Tab', background=self.get("bg_button"), foreground=self.get("fg_button"), padding=(12, 6))
        style.map('TNotebook.Tab', background=[('selected', self.get("bg_frame"))])
        style.configure('TLabelframe', background=self.get("bg"), bordercolor=self.get("border"))
        style.configure('TLabelframe.Label', background=self.get("bg"), foreground=self.get("fg"), font=self.SMALL_FONT)

        return style


class LoginPopup:
    """Professional User Authentication Dialog
    
    Provides secure popup authentication interface with credential
    storage option. Supports callback on successful authentication.
    """
    
    def __init__(self, parent, title="Login", callback=None, labels=None):
        """Initialize login popup
        
        Args:
            parent: Parent window
            title (str): Dialog title
            callback: Function to call with login data
        """
        self.parent = parent
        self.title = title
        self.callback = callback
        self.labels = labels or {
            "email_label": "Email/Usuario do YouTube:",
            "password_label": "Senha:",
            "notice": "Login usado apenas pelo yt-dlp. Credenciais nao sao armazenadas.",
            "button_ok": "Entrar",
            "button_cancel": "Cancelar",
            "warning_title": "Aviso",
            "warning_message": "Preencha todos os campos.",
        }
        self.result = None
    
    def show(self):
        """Display login dialog and handle authentication
        
        Returns:
            dict: Login result with email, password, remember_flag
        """
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.title)
        dialog.geometry("420x260")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Email/Username field
        ttk.Label(main_frame, text=self.labels.get("email_label", "Email/Username:")).grid(row=0, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(main_frame, width=30)
        email_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=10)
        
        # Password field
        ttk.Label(main_frame, text=self.labels.get("password_label", "Password:")).grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=10)

        # YouTube login notice
        notice = self.labels.get("notice", "Login is only used by yt-dlp. Credentials are not stored.")
        ttk.Label(main_frame, text=notice, justify=tk.LEFT, wraplength=360).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=10
        )
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=15)
        
        def on_ok():
            email = email_entry.get().strip()
            password = password_entry.get()
            remember = False
            
            if not email or not password:
                messagebox.showwarning(
                    self.labels.get("warning_title", "Warning"),
                    self.labels.get("warning_message", "Please fill all fields.")
                )
                return
            
            self.result = {
                "email": email,
                "password": password,
                "remember": remember
            }
            
            if self.callback:
                self.callback(self.result)
            
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text=self.labels.get("button_ok", "OK"), command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.labels.get("button_cancel", "Cancel"), command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Focus on first field
        email_entry.focus()
        
        # Wait for dialog to close
        dialog.wait_window()
        return self.result


class LanguageSelector:
    """Multi-Language Selection Component
    
    Provides language selection via menu or dropdown with support for
    callback on language change. Enables dynamic language switching.
    """
    
    def __init__(self, languages=None, default="en"):
        """Initialize language selector
        
        Args:
            languages (list): Available language codes
            default (str): Default language code
        """
        self.languages = languages or ["en", "pt"]
        self.current = default
    
    def create_menu(self, parent_menu, callback):
        """Create language submenu for menu bar
        
        Args:
            parent_menu: Parent menu widget
            callback: Function to call on language selection
            
        Returns:
            tk.Menu: Language submenu
        """
        lang_menu = tk.Menu(parent_menu, tearoff=0)
        
        for lang in self.languages:
            lang_name = "Portuguese (PT)" if lang == "pt" else "English (EN)"
            lang_menu.add_command(
                label=lang_name,
                command=lambda l=lang: callback(l)
            )
        
        return lang_menu
    
    def create_dropdown(self, parent, callback):
        """Create language dropdown combobox
        
        Args:
            parent: Parent widget
            callback: Function to call on selection change
            
        Returns:
            ttk.Combobox: Language selector combo box
        """
        lang_names = {
            "pt": "Portuguese (PT)",
            "en": "English (EN)"
        }
        available = [lang_names.get(lang, lang) for lang in self.languages]
        
        combo = ttk.Combobox(
            parent,
            values=available,
            state="readonly",
            width=20
        )
        combo.set(lang_names.get(self.current, self.current))
        combo.bind("<<ComboboxSelected>>", lambda e: callback(self.languages[combo.current()]))
        
        return combo


class ConfigManager:
    """JSON-Based Configuration Management System
    
    Handles persistent storage of application settings and download history.
    Supports automatic default configuration creation and error recovery.
    """
    
    def __init__(self, config_dir="config"):
        """Initialize configuration manager
        
        Args:
            config_dir (str): Configuration directory path
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.history_file = self.config_dir / "history_downloads.json"
        self.default_config = {
            "dark_mode": True,
            "language": "pt",
            "output_folder": "downloads",
            "log_level": "INFO"
        }
    
    def load(self):
        """Load configuration from JSON file
        
        Returns:
            dict: Configuration dictionary or default if file not found
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading configuration: {e}")
        return self.default_config.copy()
    
    def save(self, config):
        """Save configuration to JSON file
        
        Args:
            config (dict): Configuration dictionary to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value by key
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = self.load()
        return config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save
        
        Args:
            key (str): Configuration key
            value: Value to set
            
        Returns:
            bool: True if saved successfully
        """
        config = self.load()
        config[key] = value
        return self.save(config)
    
    def load_history(self):
        """Load download history from JSON file
        
        Returns:
            list: List of download history entries
        """
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        return []
    
    def save_history(self, history):
        """Save download history to JSON file
        
        Args:
            history (list): Download history entries
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Keep only last 100 items
            history = history[-100:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def add_to_history(self, item):
        """Add new item to download history
        
        Args:
            item (dict): History entry to add
        """
        history = self.load_history()
        history.append(item)
        self.save_history(history)


class LogWidget(tk.Text):
    """Custom Log Display Widget
    
    Auto-scrolling text widget with automatic timestamp annotation
    and theme color support for professional log presentation.
    """
    
    def __init__(self, parent, theme=None, **kwargs):
        """Initialize log widget
        
        Args:
            parent: Parent widget
            theme: Theme manager for color scheme
            **kwargs: Additional Tk.Text arguments
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.configure_colors()
    
    def configure_colors(self):
        """Configure widget colors based on current theme"""
        if self.theme:
            # Support both old Theme and new DesignTokens
            if hasattr(self.theme, 'get'):
                # Old Theme interface
                bg_color = self.theme.get("bg_entry")
                fg_color = self.theme.get("fg_entry")
            elif hasattr(self.theme, 'get_color'):
                # New DesignTokens interface
                bg_color = self.theme.get_color("bg_secondary")
                fg_color = self.theme.get_color("fg_primary")
            else:
                # Fallback
                bg_color = "#1A1D2E"
                fg_color = "#E8EAED"
            
            self.config(
                bg=bg_color,
                fg=fg_color,
                insertbackground=fg_color
            )
    
    def add_log(self, message, level="INFO"):
        """Add timestamped log message to display
        
        Args:
            message (str): Log message content
            level (str): Log level (INFO, ERROR, WARNING, DEBUG)
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        self.config(state=tk.NORMAL)
        self.insert(tk.END, log_line)
        self.see(tk.END)
        self.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear all log messages from widget"""
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.config(state=tk.DISABLED)


class StatusBar(ttk.Frame):
    """Professional Status Bar Component
    
    Displays application status, login information, and version details.
    Auto-updates with theme changes.
    """
    
    def __init__(self, parent, theme=None, labels=None, **kwargs):
        """Initialize status bar
        
        Args:
            parent: Parent widget
            theme: Theme manager for color scheme
            **kwargs: Additional Frame arguments
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.labels = labels or {
            "status_ready": "Ready",
            "login_not_logged": "Not logged in",
            "login_logged_prefix": "Logged in as",
            "version_label": "v1.0.0 Professional",
        }
        
        # Status label
        self.status_label = ttk.Label(self, text=self.labels.get("status_ready", "Ready"))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Vertical separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Login status label
        self.login_label = ttk.Label(self, text=self.labels.get("login_not_logged", "Not logged in"))
        self.login_label.pack(side=tk.LEFT, padx=5)
        
        # Spacer
        ttk.Frame(self).pack(side=tk.LEFT, expand=True)
        
        # Version label
        version_label = ttk.Label(self, text=self.labels.get("version_label", "v1.0.0 Professional"))
        version_label.pack(side=tk.RIGHT, padx=5)
    
    def set_status(self, message):
        """Update status message
        
        Args:
            message (str): New status message
        """
        self.status_label.config(text=message)
    
    def set_login_status(self, logged_in, email=""):
        """Update login status display
        
        Args:
            logged_in (bool): Whether user is logged in
            email (str): User email if logged in
        """
        if logged_in:
            prefix = self.labels.get("login_logged_prefix", "Logged in as")
            self.login_label.config(text=f"{prefix}: {email}")
        else:
            self.login_label.config(text=self.labels.get("login_not_logged", "Not logged in"))
