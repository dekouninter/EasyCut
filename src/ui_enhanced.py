# -*- coding: utf-8 -*-
"""
Enhanced UI Components Module for EasyCut
Professional User Interface with Theme and Configuration Management

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.4.0
License: GPL-3.0

This module provides:
- Theme Manager: Dark/Light theme with instant hot-reload
- Configuration Manager: Persistent JSON-based settings
- Login Popup: Professional authentication dialog
- Language Selector: Multi-language dropdown/menu
- Log Widget: Auto-scrolling logging display with colored log levels
- Status Bar: Real-time application status with dot indicator
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path


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
            "output_dir": "downloads",
            "log_level": "INFO",
            "browser_cookies": "chrome",     # Browser for cookie extraction or "file"
            "browser_profile": "",           # Browser profile name (e.g., "Profile 1", "Default")
            "use_browser_cookies": True,     # Use browser cookies for auth
            "cookies_file": ""               # Path to cookies.txt file (when browser_cookies="file")
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
    
    Auto-scrolling text widget with automatic timestamp annotation,
    colored log levels, and theme color support.
    """
    
    # Log level colors (dark theme defaults)
    LEVEL_COLORS = {
        "INFO":    "#60A5FA",  # Blue
        "ERROR":   "#F87171",  # Red
        "WARNING": "#FBBF24",  # Amber
        "DEBUG":   "#8B92A8",  # Gray
        "SUCCESS": "#4ADE80",  # Green
    }
    
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
        self._setup_tags()
    
    def _setup_tags(self):
        """Setup text tags for colored log levels"""
        for level, color in self.LEVEL_COLORS.items():
            self.tag_configure(f"level_{level}", foreground=color)
        
        # Timestamp tag — subtle color
        ts_color = "#5C6278"
        if self.theme and hasattr(self.theme, 'get_color'):
            ts_color = self.theme.get_color("fg_tertiary")
        self.tag_configure("timestamp", foreground=ts_color)
    
    def configure_colors(self):
        """Configure widget colors based on current theme"""
        if self.theme:
            if hasattr(self.theme, 'get'):
                bg_color = self.theme.get("bg_entry")
                fg_color = self.theme.get("fg_entry")
            elif hasattr(self.theme, 'get_color'):
                bg_color = self.theme.get_color("bg_input")
                fg_color = self.theme.get_color("fg_primary")
            else:
                bg_color = "#13151C"
                fg_color = "#E8ECF4"
            
            self.config(
                bg=bg_color,
                fg=fg_color,
                insertbackground=fg_color,
                selectbackground="#6C8EEF",
                selectforeground="#FFFFFF",
                relief="flat",
                borderwidth=0,
                padx=8,
                pady=4,
            )
    
    def add_log(self, message, level="INFO"):
        """Add timestamped log message with colored level indicator
        
        Args:
            message (str): Log message content
            level (str): Log level (INFO, ERROR, WARNING, DEBUG, SUCCESS)
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.config(state=tk.NORMAL)
        
        # Insert timestamp with subtle color
        start_idx = self.index(tk.END)
        self.insert(tk.END, f"[{timestamp}] ")
        end_idx = self.index(tk.END)
        self.tag_add("timestamp", start_idx, end_idx)
        
        # Insert level tag with color
        level_upper = level.upper()
        start_idx = self.index(tk.END)
        self.insert(tk.END, f"[{level_upper}] ")
        end_idx = self.index(tk.END)
        tag_name = f"level_{level_upper}"
        if tag_name in [self.tag_names()]:
            pass
        self.tag_add(tag_name, start_idx, end_idx)
        
        # Insert message
        self.insert(tk.END, f"{message}\n")
        
        self.see(tk.END)
        self.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear all log messages from widget"""
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.config(state=tk.DISABLED)


class StatusBar(ttk.Frame):
    """Professional Status Bar Component
    
    Displays application status with colored dot indicator,
    login information, and version details.
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
            "version_label": "v1.4.0 Professional",
        }
        
        # Status dot indicator
        self.status_dot = tk.Canvas(self, width=8, height=8, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(8, 4), pady=0)
        self._draw_dot("#4ADE80")  # Green = ready
        
        # Status label
        self.status_label = ttk.Label(self, text=self.labels.get("status_ready", "Ready"))
        self.status_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Vertical separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Login status label
        self.login_label = ttk.Label(self, text=self.labels.get("login_not_logged", "Not logged in"))
        self.login_label.pack(side=tk.LEFT, padx=8)
        
        # Spacer
        ttk.Frame(self).pack(side=tk.LEFT, expand=True)
        
        # Version label (caption style)
        version_label = ttk.Label(
            self, text=self.labels.get("version_label", "v1.4.0 Professional"),
            style="Caption.TLabel"
        )
        version_label.pack(side=tk.RIGHT, padx=8)
    
    def _draw_dot(self, color):
        """Draw colored status dot"""
        self.status_dot.delete("all")
        self.status_dot.create_oval(1, 1, 7, 7, fill=color, outline="")
    
    def set_status(self, message, dot_color=None):
        """Update status message and optional dot color
        
        Args:
            message (str): New status message
            dot_color (str): Optional dot color (#hex or name)
        """
        self.status_label.config(text=message)
        if dot_color:
            self._draw_dot(dot_color)
    
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
