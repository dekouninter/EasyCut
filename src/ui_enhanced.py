# -*- coding: utf-8 -*-
"""
Enhanced UI Components Module for EasyCut v2.0
Premium User Interface with Theme and Configuration Management

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut

Provides:
- LoginPopup: Professional authentication dialog with modern styling
- LanguageSelector: Multi-language menu/dropdown
- ConfigManager: Persistent JSON-based settings
- LogWidget: Premium auto-scrolling log display with level colors
- StatusBar: Animated status bar with indicators
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
from pathlib import Path

from design_system import DesignTokens, Typography, Spacing, Animation


# ═══════════════════════════════════════════════════════════════════
#  LOGIN POPUP — Premium authentication dialog
# ═══════════════════════════════════════════════════════════════════

class LoginPopup:
    """Professional authentication dialog with modern styling"""
    
    def __init__(self, parent, title="Login", callback=None, labels=None,
                 design: DesignTokens = None):
        self.parent = parent
        self.title = title
        self.callback = callback
        self.design = design or DesignTokens(dark_mode=True)
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
        """Display login dialog"""
        d = self.design
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.title)
        dialog.geometry("480x300")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Style the dialog
        bg = d.get_color("bg_elevated")
        fg = d.get_color("fg_primary")
        fg2 = d.get_color("fg_secondary")
        fg3 = d.get_color("fg_tertiary")
        accent = d.get_color("accent_primary")
        input_bg = d.get_color("bg_input")
        border = d.get_color("border")
        
        dialog.configure(bg=bg)
        
        # Main container
        main = tk.Frame(dialog, bg=bg)
        main.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.XL)
        
        # Title with icon
        title_row = tk.Frame(main, bg=bg)
        title_row.pack(fill=tk.X, pady=(0, Spacing.XL))
        
        tk.Label(
            title_row, text="🔐", bg=bg,
            font=("Segoe UI Emoji", Typography.SIZE_H1)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        tk.Label(
            title_row, text=self.title, bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H2, "bold")
        ).pack(side=tk.LEFT)
        
        # Email field
        tk.Label(
            main, text=self.labels.get("email_label", "Email/Username:"),
            bg=bg, fg=fg2,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION, "bold"),
            anchor="w"
        ).pack(fill=tk.X, pady=(0, Spacing.XS))
        
        email_entry = ttk.Entry(main)
        email_entry.pack(fill=tk.X, pady=(0, Spacing.MD), ipady=4)
        
        # Password field
        tk.Label(
            main, text=self.labels.get("password_label", "Password:"),
            bg=bg, fg=fg2,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION, "bold"),
            anchor="w"
        ).pack(fill=tk.X, pady=(0, Spacing.XS))
        
        password_entry = ttk.Entry(main, show="●")
        password_entry.pack(fill=tk.X, pady=(0, Spacing.MD), ipady=4)
        
        # Notice
        notice = self.labels.get("notice", "Login is only used by yt-dlp.")
        notice_frame = tk.Frame(main, bg=d.get_color("info_bg"))
        notice_frame.pack(fill=tk.X, pady=(0, Spacing.LG))
        
        tk.Label(
            notice_frame, text=f"ℹ  {notice}", bg=d.get_color("info_bg"),
            fg=d.get_color("info"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            justify=tk.LEFT, wraplength=400, anchor="w",
            padx=Spacing.SM, pady=Spacing.SM
        ).pack(fill=tk.X)
        
        # Buttons
        btn_frame = tk.Frame(main, bg=bg)
        btn_frame.pack(fill=tk.X)
        
        def on_ok():
            email = email_entry.get().strip()
            password = password_entry.get()
            if not email or not password:
                messagebox.showwarning(
                    self.labels.get("warning_title", "Warning"),
                    self.labels.get("warning_message", "Please fill all fields.")
                )
                return
            self.result = {"email": email, "password": password, "remember": False}
            if self.callback:
                self.callback(self.result)
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(
            btn_frame, text=self.labels.get("button_ok", "OK"),
            command=on_ok, style="TButton"
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ttk.Button(
            btn_frame, text=self.labels.get("button_cancel", "Cancel"),
            command=on_cancel, style="Ghost.TButton"
        ).pack(side=tk.LEFT)
        
        # Focus
        email_entry.focus()
        dialog.wait_window()
        return self.result


# ═══════════════════════════════════════════════════════════════════
#  LANGUAGE SELECTOR
# ═══════════════════════════════════════════════════════════════════

class LanguageSelector:
    """Multi-Language Selection Component"""
    
    def __init__(self, languages=None, default="en"):
        self.languages = languages or ["en", "pt"]
        self.current = default
    
    def create_menu(self, parent_menu, callback):
        lang_menu = tk.Menu(parent_menu, tearoff=0)
        for lang in self.languages:
            lang_name = "Portuguese (PT)" if lang == "pt" else "English (EN)"
            lang_menu.add_command(
                label=lang_name,
                command=lambda l=lang: callback(l)
            )
        return lang_menu
    
    def create_dropdown(self, parent, callback):
        lang_names = {"pt": "Portuguese (PT)", "en": "English (EN)"}
        available = [lang_names.get(lang, lang) for lang in self.languages]
        combo = ttk.Combobox(parent, values=available, state="readonly", width=20)
        combo.set(lang_names.get(self.current, self.current))
        combo.bind("<<ComboboxSelected>>", lambda e: callback(self.languages[combo.current()]))
        return combo


# ═══════════════════════════════════════════════════════════════════
#  CONFIG MANAGER
# ═══════════════════════════════════════════════════════════════════

class ConfigManager:
    """JSON-Based Configuration Management"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.history_file = self.config_dir / "history_downloads.json"
        self.default_config = {
            "dark_mode": True,
            "language": "en",
            "output_folder": "downloads",
            "log_level": "INFO",
            # user preference: automatically convert downloads to
            # Premiere-compatible MP4/H264 files when requested
            "premiere_compat": False,
            # when True, do not show JS runtime prompt again
            "suppress_js_runtime_prompt": False
        }
    
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading configuration: {e}")
        return self.default_config.copy()
    
    def save(self, config):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key, default=None):
        config = self.load()
        return config.get(key, default)
    
    def set(self, key, value):
        config = self.load()
        config[key] = value
        return self.save(config)
    
    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        return []
    
    def save_history(self, history):
        try:
            history = history[-100:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def add_to_history(self, item):
        history = self.load_history()
        history.append(item)
        self.save_history(history)

    def reset_to_defaults(self):
        """Overwrite config.json with default values (Issue #37)"""
        return self.save(self.default_config.copy())


# ═══════════════════════════════════════════════════════════════════
#  LOG WIDGET — Premium log display with level-colored messages
# ═══════════════════════════════════════════════════════════════════

class LogWidget(tk.Text):
    """Premium auto-scrolling log display with color-coded log levels"""
    
    # Log level config: (color_token, prefix_symbol)
    LEVEL_CONFIG = {
        "INFO":    ("accent_primary", "●"),
        "SUCCESS": ("success", "✓"),
        "WARNING": ("warning", "⚠"),
        "ERROR":   ("error", "✖"),
        "DEBUG":   ("fg_tertiary", "◌"),
    }
    
    def __init__(self, parent, theme=None, design: DesignTokens = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self._design = design
        self.configure_colors()
        self._setup_tags()
    
    def configure_colors(self):
        """Configure widget colors"""
        design = self._design
        if design:
            bg = design.get_color("bg_input")
            fg = design.get_color("fg_primary")
        elif self.theme:
            if hasattr(self.theme, 'get'):
                bg = self.theme.get("bg_entry")
                fg = self.theme.get("fg_entry")
            elif hasattr(self.theme, 'get_color'):
                bg = self.theme.get_color("bg_secondary")
                fg = self.theme.get_color("fg_primary")
            else:
                bg, fg = "#121418", "#F0F2F5"
        else:
            bg, fg = "#121418", "#F0F2F5"
        
        self.config(
            bg=bg, fg=fg, insertbackground=fg,
            relief="flat", borderwidth=0,
            padx=Spacing.SM, pady=Spacing.SM,
            font=(Typography.FONT_MONO, Typography.SIZE_CAPTION),
            wrap=tk.WORD,
            selectbackground="#1C2A4A",
            selectforeground=fg,
        )
    
    def _setup_tags(self):
        """Configure text tags for colored log levels"""
        design = self._design
        if not design:
            return
        
        for level, (color_key, _) in self.LEVEL_CONFIG.items():
            color = design.get_color(color_key)
            self.tag_configure(f"level_{level}", foreground=color)
        
        self.tag_configure("timestamp", foreground=design.get_color("fg_tertiary"))
    
    def add_log(self, message, level="INFO"):
        """Add timestamped, color-coded log message"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        config = self.LEVEL_CONFIG.get(level, ("fg_primary", "●"))
        symbol = config[1]
        
        self.config(state=tk.NORMAL)
        
        # Timestamp
        start = self.index(tk.END)
        self.insert(tk.END, f"  {timestamp} ")
        self.tag_add("timestamp", start, self.index(tk.END))
        
        # Level indicator + message
        msg_start = self.index(tk.END)
        self.insert(tk.END, f"{symbol} {message}\n")
        self.tag_add(f"level_{level}", msg_start, self.index(tk.END))
        
        self.see(tk.END)
        self.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear all log messages"""
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.config(state=tk.DISABLED)


# ═══════════════════════════════════════════════════════════════════
#  STATUS BAR — Premium status bar with indicators
# ═══════════════════════════════════════════════════════════════════

class StatusBar(ttk.Frame):
    """Premium status bar with animated status indicators"""
    
    def __init__(self, parent, theme=None, labels=None, 
                 design: DesignTokens = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self._design = design
        self.labels = labels or {
            "status_ready": "Ready",
            "login_not_logged": "Not logged in",
            "login_logged_prefix": "Logged in as",
            "version_label": "v1.9.0",
        }
        
        # Use a tk.Frame inner for custom colors
        bg = design.get_color("bg_secondary") if design else "#181B22"
        border = design.get_color("border_subtle") if design else "#181B20"
        fg = design.get_color("fg_secondary") if design else "#9BA3B2"
        fg3 = design.get_color("fg_tertiary") if design else "#5E6678"
        accent = design.get_color("accent_primary") if design else "#4C8BF5"
        
        self._inner = tk.Frame(self, bg=bg, height=32)
        self._inner.pack(fill=tk.X)
        self._inner.pack_propagate(False)
        
        # Top border line
        tk.Frame(self._inner, bg=border, height=1).pack(fill=tk.X)
        
        content = tk.Frame(self._inner, bg=bg)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD)
        
        # Status dot + label (left)
        status_row = tk.Frame(content, bg=bg)
        status_row.pack(side=tk.LEFT, fill=tk.Y)
        
        self._status_dot = tk.Label(
            status_row, text="●", bg=bg, fg=accent,
            font=(Typography.FONT_FAMILY, 7)
        )
        self._status_dot.pack(side=tk.LEFT, padx=(0, Spacing.XS), pady=Spacing.SM)
        
        self.status_label = tk.Label(
            status_row, text=self.labels.get("status_ready", "Ready"),
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        )
        self.status_label.pack(side=tk.LEFT, pady=Spacing.SM)
        
        # Separator
        tk.Frame(content, bg=border, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=Spacing.SM, pady=4)
        
        # Version (right) — login status removed: shown only in auth banner
        self._version_label = tk.Label(
            content, text=self.labels.get("version_label", "v1.9.0"),
            bg=bg, fg=fg3,
            font=(Typography.FONT_FAMILY, Typography.SIZE_TINY)
        )
        self._version_label.pack(side=tk.RIGHT, pady=Spacing.SM)
    
    def set_status(self, message, level="info"):
        """Update status with optional level coloring"""
        self.status_label.config(text=message)
        
        if self._design:
            color_map = {
                "info": "accent_primary",
                "success": "success",
                "warning": "warning",
                "error": "error",
            }
            dot_color = self._design.get_color(color_map.get(level, "accent_primary"))
            self._status_dot.config(fg=dot_color)
    
    def set_login_status(self, logged_in, email=""):
        """Update login status in the status bar.
        
        Uses the existing status_label since the dedicated login_label
        was removed (login is now shown in the auth banner).
        """
        if logged_in:
            prefix = self.labels.get("login_logged_prefix", "Logged in as")
            self.status_label.config(text=f"{prefix}: {email}")
            if self._design:
                self._status_dot.config(fg=self._design.get_color("success"))
        else:
            self.status_label.config(text=self.labels.get("login_not_logged", "Not logged in"))
            if self._design:
                self._status_dot.config(fg=self._design.get_color("fg_tertiary"))
