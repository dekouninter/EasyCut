# -*- coding: utf-8 -*-
"""
EasyCut - YouTube Video Downloader and Audio Converter
Professional Desktop Application using Tkinter

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.2.1
License: GPL-3.0

Features:
- Download YouTube videos with multiple quality options
- Batch downloads with queue management
- Audio conversion (MP3, WAV, M4A, OPUS)
- YouTube OAuth authentication (integrated)
- Real-time logging
- Live stream recording support
- Dark/Light theme with instant reload
- Multi-language support (EN, PT)
- Professional UI design with modern components
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import re
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Import local modules
sys.path.insert(0, os.path.dirname(__file__))
from i18n import translator as t, Translator
from ui_enhanced import ConfigManager, LogWidget, StatusBar, LoginPopup
from oauth_manager import OAuthManager, OAuthError
from donation_system import DonationButton
from icon_manager import icon_manager, get_ui_icon, set_icon_theme
from design_system import ModernTheme, DesignTokens, Typography, Spacing, Icons
from modern_components import (
    ModernButton, ModernCard
)
from font_loader import setup_fonts, LOADED_FONT_FAMILY

# Import external libraries
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

class EasyCutApp:
    """Professional YouTube Downloader Application"""
    
    def __init__(self, root):
        self.root = root
        
        # Configuration
        self.config_manager = ConfigManager()
        self.load_config()
        
        # OAuth Manager
        self.oauth_manager = OAuthManager(config_dir="config")
        
        # Load custom fonts FIRST
        self.font_family = setup_fonts()
        
        # Modern Theme & Design System
        self.theme = ModernTheme(dark_mode=self.dark_mode, font_family=self.font_family)
        self.design = DesignTokens(dark_mode=self.dark_mode)
        self.translator = Translator(self.language)
        
        # Icon Manager
        self.icon_manager = icon_manager
        set_icon_theme(self.dark_mode)  # Sync icon colors with theme
        
        # State
        self.is_downloading = False
        self.active_scroll_canvas = None  # Track active canvas for mouse wheel scroll
        self.browser_var = None  # Browser selection variable
        self.download_semaphore = threading.BoundedSemaphore(value=3)
        self._video_formats = []  # Fetched format list from yt-dlp
        self._video_info_cache = {}  # Cached metadata from last verify
        self._format_id_map = {}  # Maps combo index to format_id
        
        # Paths
        self.output_dir = Path(self.config_manager.get("output_dir", "downloads"))
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup
        self.setup_logging()
        self.setup_window()
        self.apply_theme()  # CRITICAL: Apply theme BEFORE creating UI
        self.setup_ui()
        self.check_saved_credentials()
        self.log_app("✓ EasyCut started successfully")
    
    def load_config(self):
        """Load configuration from file"""
        config = self.config_manager.load()
        self.dark_mode = config.get("dark_mode", True)  # Default: Dark
        self.language = config.get("language", "pt")    # Default: Portuguese
    
    def setup_logging(self):
        """Setup application logging"""
        log_file = Path("config") / "app.log"
        log_file.parent.mkdir(exist_ok=True)
        
        # Configure logging with rotation
        from logging.handlers import RotatingFileHandler
        
        # File handler with rotation (5MB max, keep 3 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
        # Console handler for debugging (only warnings and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)-8s | %(message)s'
        ))
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*60)
        self.logger.info("EasyCut Application Started")
        self.logger.info(f"Version: 1.2.1")
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("EasyCut")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # Setup graceful shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup complete user interface — sidebar layout"""
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # State
        self.sidebar_expanded = True
        self.active_section = "download"
        self.section_frames = {}
        self.nav_buttons = {}
        
        # Root layout
        root_frame = ttk.Frame(self.root)
        root_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- HEADER (45px) ---
        self.create_header(root_frame)
        
        # --- OAuth AUTHENTICATION BANNER ---
        self.create_login_banner(root_frame)
        
        # --- BODY (sidebar + content) ---
        body = ttk.Frame(root_frame)
        body.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar_frame = tk.Frame(body, bg=self.design.get_color("bg_secondary"), width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)
        self._build_sidebar()
        
        # Content area
        self.content_area = ttk.Frame(body)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Section container (stacked frames)
        self.section_container = ttk.Frame(self.content_area)
        self.section_container.pack(fill=tk.BOTH, expand=True)
        self.section_container.grid_rowconfigure(0, weight=1)
        self.section_container.grid_columnconfigure(0, weight=1)

        # Create sections as stacked frames
        self.section_frames["download"] = self.create_download_tab()
        self.section_frames["batch"] = self.create_batch_tab()
        self.section_frames["live"] = self.create_live_tab()
        self.section_frames["history"] = self.create_history_tab()
        self.section_frames["about"] = self.create_about_tab()
        
        # Select initial section
        self._switch_section("download")
        
        # --- LOG PANEL (collapsible) ---
        self._build_log_panel(root_frame)
        
        # --- STATUS BAR ---
        tr = self.translator.get
        version_label = tr("version", "1.2.1")
        status_labels = {
            "status_ready": tr("status_ready", "Ready"),
            "login_not_logged": tr("status_not_logged_in", "Not logged in"),
            "login_logged_prefix": tr("status_logged_in", "Logged in as"),
            "version_label": f"v{version_label}",
        }
        self.status_bar = StatusBar(root_frame, theme=self.theme, labels=status_labels)
        self.status_bar.pack(fill=tk.X)
        self.update_login_status()
        
        # --- DONATION BUTTON ---
        donation_btn = DonationButton(self.root, translator=self.translator)
        donation_btn.create_floating_button(root_frame)
        
        # --- KEYBOARD SHORTCUTS ---
        self._bind_shortcuts()
    
    # ──────────────────────────────────────────
    # SIDEBAR
    # ──────────────────────────────────────────
    
    def _build_sidebar(self):
        """Build the sidebar navigation"""
        tr = self.translator.get
        bg = self.design.get_color("bg_secondary")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        accent = self.design.get_color("accent_primary")
        hover_bg = self.design.get_color("bg_hover")
        
        # Toggle button
        toggle_frame = tk.Frame(self.sidebar_frame, bg=bg)
        toggle_frame.pack(fill=tk.X, padx=Spacing.SM, pady=(Spacing.SM, Spacing.MD))
        
        self.sidebar_toggle_btn = tk.Label(
            toggle_frame, text="☰", bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, 16), cursor="hand2"
        )
        self.sidebar_toggle_btn.pack(anchor="w", padx=Spacing.SM)
        self.sidebar_toggle_btn.bind("<Button-1>", lambda e: self._toggle_sidebar())
        
        # Navigation items
        nav_items = [
            ("download", "⬇️", tr("tab_download", "Download")),
            ("batch",    "📦", tr("tab_batch", "Batch")),
            ("live",     "🔴", tr("tab_live", "Live")),
            ("history",  "📜", tr("tab_history", "History")),
            ("about",    "ℹ️",  tr("tab_about", "About")),
        ]
        
        nav_container = tk.Frame(self.sidebar_frame, bg=bg)
        nav_container.pack(fill=tk.BOTH, expand=True)
        
        for key, icon, label in nav_items:
            btn_frame = tk.Frame(nav_container, bg=bg, cursor="hand2")
            btn_frame.pack(fill=tk.X, pady=1)
            btn_frame.pack_propagate(False)
            btn_frame.config(height=40)
            btn_frame.grid_columnconfigure(2, weight=1)
            
            # Active indicator (left accent bar)
            indicator = tk.Frame(btn_frame, bg=bg, width=3)
            indicator.grid(row=0, column=0, sticky="ns")
            
            # Icon
            icon_lbl = tk.Label(
                btn_frame, text=icon, bg=bg, fg=fg,
                font=("Segoe UI Emoji", 14),
                width=2, anchor="center"
            )
            icon_lbl.grid(row=0, column=1, padx=(Spacing.MD, Spacing.SM), pady=Spacing.SM)
            
            # Label
            text_lbl = tk.Label(
                btn_frame, text=label, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                anchor="w"
            )
            text_lbl.grid(row=0, column=2, sticky="w", pady=Spacing.SM)
            
            # Store refs
            self.nav_buttons[key] = {
                "frame": btn_frame,
                "indicator": indicator,
                "icon": icon_lbl,
                "text": text_lbl,
            }
            
            # Click binding
            for widget in (btn_frame, icon_lbl, text_lbl):
                widget.bind("<Button-1>", lambda e, k=key: self._switch_section(k))
                widget.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
                widget.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))
        
        # Footer
        footer = tk.Frame(self.sidebar_frame, bg=bg)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=Spacing.SM, pady=Spacing.SM)

        # Folder buttons
        open_label = tr("header_open_folder", "Open Folder")
        select_label = tr("header_select_folder", "Select Folder")

        # Open Folder button/frame
        open_btn_frame = tk.Frame(footer, bg=bg)
        open_btn_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
        
        open_btn = ModernButton(
            open_btn_frame, text=open_label,
            icon_name="folder", command=self.open_output_folder,
            variant="outline", width=18
        )
        open_btn.pack(fill=tk.X)
        
        # Icon-only version for collapsed state
        border_color = self.design.get_color("border_primary")
        open_icon = get_ui_icon("folder", size=20)
        open_icon_lbl = tk.Label(
            open_btn_frame, image=open_icon, bg=bg, 
            cursor="hand2", borderwidth=1, relief="solid",
            highlightthickness=1, highlightbackground=border_color,
            padx=Spacing.SM, pady=Spacing.SM
        )
        open_icon_lbl.image = open_icon
        open_icon_lbl.bind("<Button-1>", lambda e: self.open_output_folder())
        open_icon_lbl.bind("<Enter>", lambda e: open_icon_lbl.config(bg=self.design.get_color("bg_hover")))
        open_icon_lbl.bind("<Leave>", lambda e: open_icon_lbl.config(bg=bg))
        
        # Select Folder button/frame
        select_btn_frame = tk.Frame(footer, bg=bg)
        select_btn_frame.pack(fill=tk.X)
        
        select_btn = ModernButton(
            select_btn_frame, text=select_label,
            icon_name="folder-plus", command=self.select_output_folder,
            variant="outline", width=18
        )
        select_btn.pack(fill=tk.X)
        
        # Icon-only version for collapsed state
        select_icon = get_ui_icon("folder-plus", size=20)
        select_icon_lbl = tk.Label(
            select_btn_frame, image=select_icon, bg=bg,
            cursor="hand2", borderwidth=1, relief="solid",
            highlightthickness=1, highlightbackground=border_color,
            padx=Spacing.SM, pady=Spacing.SM
        )
        select_icon_lbl.image = select_icon
        select_icon_lbl.bind("<Button-1>", lambda e: self.select_output_folder())
        select_icon_lbl.bind("<Enter>", lambda e: select_icon_lbl.config(bg=self.design.get_color("bg_hover")))
        select_icon_lbl.bind("<Leave>", lambda e: select_icon_lbl.config(bg=bg))

        # Version (moved below buttons)
        version_lbl = tk.Label(
            footer, text=f"v{tr('version', '1.2.1')}", bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_TINY)
        )
        version_lbl.pack(anchor="w", pady=(Spacing.SM, 0))

        self.footer_buttons = {
            "open": {
                "button": open_btn,
                "icon_label": open_icon_lbl,
                "text": open_label
            },
            "select": {
                "button": select_btn,
                "icon_label": select_icon_lbl,
                "text": select_label
            },
            "version": version_lbl,
        }
    
    def _switch_section(self, key):
        """Switch active content section"""
        self.active_section = key
        bg = self.design.get_color("bg_secondary")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        accent = self.design.get_color("accent_primary")
        
        # Update sidebar visuals
        for k, refs in self.nav_buttons.items():
            if k == key:
                refs["indicator"].config(bg=accent)
                refs["frame"].config(bg=self.design.get_color("bg_tertiary"))
                refs["icon"].config(bg=self.design.get_color("bg_tertiary"))
                refs["text"].config(bg=self.design.get_color("bg_tertiary"), fg=fg)
            else:
                refs["indicator"].config(bg=bg)
                refs["frame"].config(bg=bg)
                refs["icon"].config(bg=bg)
                refs["text"].config(bg=bg, fg=fg_sec)
        
        # Switch visible section frame
        frame = self.section_frames.get(key)
        if frame:
            frame.tkraise()
    
    def _nav_hover(self, key, entering):
        """Handle sidebar nav hover effects"""
        if key == self.active_section:
            return
        refs = self.nav_buttons[key]
        bg = self.design.get_color("bg_secondary")
        hover_bg = self.design.get_color("bg_hover")
        color = hover_bg if entering else bg
        refs["frame"].config(bg=color)
        refs["icon"].config(bg=color)
        refs["text"].config(bg=color)
    
    def _toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed"""
        self.sidebar_expanded = not self.sidebar_expanded
        if self.sidebar_expanded:
            self.sidebar_frame.config(width=200)
            for refs in self.nav_buttons.values():
                refs["icon"].grid_remove()
                refs["icon"].grid(row=0, column=1, padx=(Spacing.MD, Spacing.SM), pady=Spacing.SM)
                refs["text"].grid(row=0, column=2, sticky="w", pady=Spacing.SM)

            # Show buttons, hide icon labels
            for data in ("open", "select"):
                self.footer_buttons[data]["button"].pack(fill=tk.X)
                self.footer_buttons[data]["icon_label"].pack_forget()

            self.footer_buttons["version"].pack_configure(anchor="w")
        else:
            self.sidebar_frame.config(width=50)
            for refs in self.nav_buttons.values():
                refs["text"].grid_remove()
                refs["icon"].grid_remove()
                refs["icon"].config(anchor="center")
                refs["icon"].grid(row=0, column=1, columnspan=2, sticky="nsew", pady=Spacing.SM)

            # Hide buttons, show centered icon labels
            for data in ("open", "select"):
                self.footer_buttons[data]["button"].pack_forget()
                self.footer_buttons[data]["icon_label"].pack(pady=Spacing.XS, expand=True)

            self.footer_buttons["version"].pack_configure(anchor="center")
    
    # ──────────────────────────────────────────
    # LOG PANEL (collapsible)
    # ──────────────────────────────────────────
    
    def _build_log_panel(self, parent):
        """Build collapsible log panel at bottom"""
        self.log_panel_visible = False
        
        # Toggle bar
        self.log_toggle_bar = tk.Frame(parent, bg=self.design.get_color("bg_secondary"), height=28, cursor="hand2")
        self.log_toggle_bar.pack(fill=tk.X)
        self.log_toggle_bar.pack_propagate(False)
        
        toggle_label = tk.Label(
            self.log_toggle_bar,
            text="▲ Log",
            bg=self.design.get_color("bg_secondary"),
            fg=self.design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            cursor="hand2"
        )
        toggle_label.pack(side=tk.LEFT, padx=Spacing.MD)
        
        for w in (self.log_toggle_bar, toggle_label):
            w.bind("<Button-1>", lambda e: self._toggle_log_panel())
        
        # Log content frame
        self.log_panel = tk.Frame(parent, bg=self.design.get_color("bg_secondary"))
        # Start hidden
        
        self.global_log = LogWidget(self.log_panel, theme=self.design, height=8)
        self.global_log.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Alias per-section logs to the global log
        self.download_log = self.global_log
        self.batch_log = self.global_log
        self.live_log = self.global_log
    
    def _toggle_log_panel(self):
        """Toggle log panel visibility"""
        self.log_panel_visible = not self.log_panel_visible
        if self.log_panel_visible:
            self.log_panel.pack(fill=tk.X, before=self.log_toggle_bar)
            # Update toggle text
            for child in self.log_toggle_bar.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text="▼ Log")
        else:
            self.log_panel.pack_forget()
            for child in self.log_toggle_bar.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text="▲ Log")
    
    # ──────────────────────────────────────────
    # KEYBOARD SHORTCUTS
    # ──────────────────────────────────────────
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.root.bind("<Control-l>", lambda e: self._toggle_log_panel())
        self.root.bind("<Control-o>", lambda e: self.open_output_folder())
        self.root.bind("<Control-Key-1>", lambda e: self._switch_section("download"))
        self.root.bind("<Control-Key-2>", lambda e: self._switch_section("batch"))
        self.root.bind("<Control-Key-3>", lambda e: self._switch_section("live"))
        self.root.bind("<Control-Key-4>", lambda e: self._switch_section("history"))
        self.root.bind("<Control-Key-5>", lambda e: self._switch_section("about"))
        self.root.bind("<Escape>", lambda e: self._on_escape())
    
    def _on_escape(self):
        """Handle Escape key"""
        if self.log_panel_visible:
            self._toggle_log_panel()
    
    def create_header(self, parent):
        """Create slim 45px header — Logo + Title + Controls"""
        tr = self.translator.get
        bg = self.design.get_color("bg_secondary")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        
        header = tk.Frame(parent, bg=bg, height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        inner = tk.Frame(header, bg=bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.XS)
        
        # Left: Icon + Title
        left = tk.Frame(inner, bg=bg)
        left.pack(side=tk.LEFT, fill=tk.Y)
        
        try:
            from PIL import Image, ImageTk
            icon_path = Path(__file__).parent.parent / "assets" / "headerapp_icon.ico"
            if icon_path.exists():
                img = Image.open(icon_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                app_icon = ImageTk.PhotoImage(img)
                icon_label = tk.Label(left, image=app_icon, bg=bg)
                icon_label.image = app_icon
                icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        except Exception:
            pass
        
        tk.Label(
            left, text="EasyCut", bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H2, "bold")
        ).pack(side=tk.LEFT)
        
        # Right: Controls
        right = tk.Frame(inner, bg=bg)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Theme toggle (icon only — compact)
        theme_icon = "🌙" if self.dark_mode else "☀️"
        theme_btn = tk.Label(
            right, text=theme_icon, bg=bg, fg=fg_sec,
            font=("Segoe UI Emoji", 14), cursor="hand2",
            padx=Spacing.SM
        )
        theme_btn.pack(side=tk.LEFT, padx=Spacing.XS)
        theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())
        
        # Language selector
        lang_options = [
            ("pt", tr("lang_pt", "Português")),
            ("en", tr("lang_en", "English"))
        ]
        lang_codes = [code for code, _ in lang_options]
        lang_labels = [label for _, label in lang_options]
        
        lang_combo = ttk.Combobox(
            right, values=lang_labels, state="readonly", width=10
        )
        current_index = lang_codes.index(self.language) if self.language in lang_codes else 0
        lang_combo.set(lang_labels[current_index])
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self.change_language(lang_codes[lang_combo.current()]))
        lang_combo.pack(side=tk.LEFT, padx=Spacing.XS)
        

        
        # Bottom border
        tk.Frame(parent, bg=self.design.get_color("border"), height=1).pack(fill=tk.X)
    
    def create_browser_auth_banner(self, parent):
        """Create browser authentication banner (reserved for future use)"""
        tr = self.translator.get
        bg = self.design.get_color("bg_secondary")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        
        banner = tk.Frame(parent, bg=bg)
        banner.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.SM)
        
        # Title
        tk.Label(
            banner, 
            text=tr("browser_cookies_title", "Browser Authentication"),
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H3, "bold")
        ).pack(anchor="w", pady=(0, Spacing.XS))
        
        # Info text
        tk.Label(
            banner,
            text=tr("browser_cookies_info", "EasyCut uses cookies from your browser"),
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            justify=tk.LEFT
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Browser selector
        selector_frame = tk.Frame(banner, bg=bg)
        selector_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        tk.Label(
            selector_frame,
            text=tr("browser_select_label", "Select Browser:"),
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Browser dropdown
        browsers = [
            ("chrome", tr("browser_chrome", "Chrome")),
            ("firefox", tr("browser_firefox", "Firefox")),
            ("edge", tr("browser_edge", "Edge")),
            ("opera", tr("browser_opera", "Opera")),
            ("brave", tr("browser_brave", "Brave")),
            ("safari", tr("browser_safari", "Safari")),
            ("file", tr("browser_cookies_file", "Cookies File")),
            ("none", tr("browser_none", "None"))
        ]
        
        current_browser = self.config_manager.get("browser_cookies", "chrome")
        self.browser_var = tk.StringVar(value=current_browser)
        
        browser_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.browser_var,
            values=[b[1] for b in browsers],
            state="readonly",
            width=25,
            font=(LOADED_FONT_FAMILY, Typography.SIZE_BODY)
        )
        browser_combo.pack(side=tk.LEFT)
        
        # Set current value
        for i, (code, name) in enumerate(browsers):
            if code == current_browser:
                browser_combo.current(i)
                break
        
        # Save on change
        def on_browser_change(event):
            selected_index = browser_combo.current()
            browser_code = browsers[selected_index][0]
            self.config_manager.set("browser_cookies", browser_code)
            if hasattr(self, 'download_log') and self.download_log:
                self.download_log.add_log(f"Browser changed to: {browsers[selected_index][1]}")
            
            # Show/hide profile selector or file selector
            if browser_code == "file":
                profile_frame.pack_forget()
                cookies_file_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
                cookies_help_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
            elif browser_code == "none":
                profile_frame.pack_forget()
                cookies_file_frame.pack_forget()
                cookies_help_frame.pack_forget()
            else:
                cookies_file_frame.pack_forget()
                cookies_help_frame.pack_forget()
                profile_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
                # Refresh profiles when browser changes
                self.refresh_browser_profiles()
        
        browser_combo.bind("<<ComboboxSelected>>", on_browser_change)
        
        # Cookies file selector (hidden by default)
        cookies_file_frame = tk.Frame(banner, bg=bg)
        
        tk.Label(
            cookies_file_frame,
            text=tr("browser_cookies_file_label", "Cookies File:"),
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.cookies_file_var = tk.StringVar(value=self.config_manager.get("cookies_file", ""))
        
        cookies_file_label = tk.Label(
            cookies_file_frame,
            textvariable=self.cookies_file_var,
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            width=30,
            anchor="w"
        )
        cookies_file_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        def select_cookies_file():
            from tkinter import filedialog
            filepath = filedialog.askopenfilename(
                title=tr("browser_cookies_file_button", "Select Cookies File"),
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filepath:
                self.cookies_file_var.set(filepath)
                self.config_manager.set("cookies_file", filepath)
                if hasattr(self, 'download_log') and self.download_log:
                    self.download_log.add_log(f"Cookies file: {Path(filepath).name}")
        
        ModernButton(
            cookies_file_frame,
            text=tr("browser_cookies_file_button", "Select File"),
            icon_name="file",
            command=select_cookies_file,
            variant="outline",
            size="sm",
            width=12
        ).pack(side=tk.LEFT)
        
        # Help text for exporting cookies (shown when file mode is selected)
        cookies_help_frame = tk.Frame(banner, bg=bg)
        help_text = f"{tr('browser_cookies_export_help', 'How to export cookies:')}\n" \
                   f"{tr('browser_cookies_export_step1', '1. Install browser extension Get cookies.txt LOCALLY')}\n" \
                   f"{tr('browser_cookies_export_step2', '2. Go to youtube.com and click the extension')}\n" \
                   f"{tr('browser_cookies_export_step3', '3. Click Export and save the cookies.txt file')}\n" \
                   f"{tr('browser_cookies_export_step4', '4. Select the saved file here')}"
        
        tk.Label(
            cookies_help_frame,
            text=help_text,
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            justify=tk.LEFT
        ).pack(anchor="w", padx=(0, 0))
        
        # Profile/Account selector with auto-detection
        profile_frame = tk.Frame(banner, bg=bg)
        profile_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        tk.Label(
            profile_frame,
            text=tr("browser_profile_auto_label", "YouTube Account:"),
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Profile dropdown (will be populated by detect function)
        self.detected_accounts = []
        self.profile_var = tk.StringVar()
        
        self.profile_combo = ttk.Combobox(
            profile_frame,
            textvariable=self.profile_var,
            values=[tr("browser_profile_select", "Select account...")],
            state="readonly",
            width=25,
            font=(LOADED_FONT_FAMILY, Typography.SIZE_BODY)
        )
        self.profile_combo.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.profile_combo.current(0)
        
        # Save on change
        def on_profile_change(event):
            selected_index = self.profile_combo.current()
            if selected_index >= 0 and selected_index < len(self.detected_accounts):
                display_name, browser_name, profile_name = self.detected_accounts[selected_index]
                self.config_manager.set("browser_profile", profile_name)
                if hasattr(self, 'download_log') and self.download_log:
                    self.download_log.add_log(f"Account set to: {display_name}")
        
        self.profile_combo.bind("<<ComboboxSelected>>", on_profile_change)
        
        # Refresh button
        ModernButton(
            profile_frame,
            text=tr("browser_profile_refresh", "Refresh"),
            icon_name="refresh-cw",
            command=self.refresh_browser_profiles,
            variant="ghost",
            size="sm",
            width=10
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Test Connection Button
        ModernButton(
            profile_frame,
            text=tr("browser_test_button", "Test Connection"),
            icon_name="check-circle",
            command=self.test_browser_connection,
            variant="outline",
            size="sm",
            width=15
        ).pack(side=tk.LEFT)
        
        # Show appropriate frame based on browser selection
        if current_browser == "file":
            cookies_file_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
            cookies_help_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        elif current_browser != "none":
            profile_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Account Status
        status_frame = tk.Frame(banner, bg=bg)
        status_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        tk.Label(
            status_frame,
            text=tr("browser_account_status", "Account Status:"),
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION, "bold")
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.account_status_label = tk.Label(
            status_frame,
            text=tr("browser_account_none", "No account detected"),
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        )
        self.account_status_label.pack(side=tk.LEFT)
        
        # Bottom border
        tk.Frame(parent, bg=self.design.get_color("border"), height=1).pack(fill=tk.X)
    
    def create_login_banner(self, parent):
        """Create OAuth authentication banner"""
        tr = self.translator.get
        bg = self.design.get_color("bg_secondary")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        
        banner = tk.Frame(parent, bg=bg)
        banner.pack(fill=tk.X, padx=Spacing.LG, pady=Spacing.SM)
        
        # Title
        tk.Label(
            banner, 
            text="YouTube Authentication",
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H3, "bold")
        ).pack(anchor="w", pady=(0, Spacing.XS))
        
        # Info text
        info_text = (
            "Authenticate with Google to download videos and live streams.\n"
            "Your browser stays free to browse YouTube while downloads happen."
        )
        tk.Label(
            banner,
            text=info_text,
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            justify=tk.LEFT
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Control frame
        control_frame = tk.Frame(banner, bg=bg)
        control_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Sync button
        def handle_sync():
            """Handle clicking the sync button"""
            if self.oauth_manager.is_authenticated():
                # Already authenticated
                result = messagebox.askyesno(
                    "Info",
                    "Already authenticated! Re-authenticate?"
                )
                if not result:
                    return
            
            # Show loading state
            sync_btn.config(state="disabled")
            self.account_status_label.config(
                text="Opening browser...",
                fg=self.design.get_color("warning")
            )
            self.root.update()
            
            # Perform authentication in background thread
            def auth_thread():
                try:
                    success = self.oauth_manager.authenticate()
                    
                    if success:
                        # Get cookies for yt-dlp
                        cookies_path = self.oauth_manager.get_youtube_cookies()
                        if cookies_path:
                            self.account_status_label.config(
                                text="✓ Authenticated! Ready to download",
                                fg=self.design.get_color("success")
                            )
                            if hasattr(self, 'download_log') and self.download_log:
                                self.download_log.add_log("✓ YouTube authentication successful!")
                        else:
                            self.account_status_label.config(
                                text="✗ Failed to get cookies",
                                fg=self.design.get_color("error")
                            )
                    else:
                        self.account_status_label.config(
                            text="✗ Authentication failed",
                            fg=self.design.get_color("error")
                        )
                
                except OAuthError as e:
                    # User-friendly OAuth error messages
                    error_msg = str(e)
                    self.account_status_label.config(
                        text="✗ OAuth Error (see popup)",
                        fg=self.design.get_color("error")
                    )
                    # Show detailed error in popup
                    self.root.after(0, lambda: messagebox.showerror("OAuth Error", error_msg))
                    if hasattr(self, 'download_log') and self.download_log:
                        self.download_log.add_log("OAuth error - check popup for details", "ERROR")
                
                
                finally:
                    sync_btn.config(state="normal")
            
            thread = threading.Thread(target=auth_thread, daemon=True)
            thread.start()
        
        sync_btn = ModernButton(
            control_frame,
            text="Sync with YouTube",
            icon_name="log-in",
            command=handle_sync,
            variant="primary",
            size="sm",
            width=18
        )
        sync_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Logout button
        def handle_logout():
            """Handle logout"""
            result = messagebox.askyesno(
                "Confirm",
                "Remove YouTube authentication?"
            )
            if result:
                self.oauth_manager.logout()
                self.account_status_label.config(
                    text="Not authenticated",
                    fg=self.design.get_color("fg_secondary")
                )
                if hasattr(self, 'download_log') and self.download_log:
                    self.download_log.add_log("Logged out from YouTube")
        
        ModernButton(
            control_frame,
            text="Logout",
            icon_name="log-out",
            command=handle_logout,
            variant="ghost",
            size="sm",
            width=10
        ).pack(side=tk.LEFT)
        
        # Account Status
        status_frame = tk.Frame(banner, bg=bg)
        status_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        tk.Label(
            status_frame,
            text="Status:",
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION, "bold")
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Status label
        if self.oauth_manager.is_authenticated():
            status_text = "✓ Authenticated and ready"
            status_color = self.design.get_color("success")
        else:
            status_text = "Not authenticated yet"
            status_color = self.design.get_color("fg_secondary")
        
        self.account_status_label = tk.Label(
            status_frame,
            text=status_text,
            bg=bg, fg=status_color,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        )
        self.account_status_label.pack(side=tk.LEFT)
        
        # Bottom border
        tk.Frame(parent, bg=self.design.get_color("border"), height=1).pack(fill=tk.X)
    
    
    def create_download_tab(self):
        """Create download section"""
        tr = self.translator.get
        
        # Create tab
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Main scrollable container
        main_canvas = tk.Canvas(frame, bg=self.design.get_color("bg_primary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=main_canvas.yview)
        main = ttk.Frame(main_canvas, padding=Spacing.LG)
        
        main.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=main, anchor="nw", tags="content")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Update inner frame width on canvas resize
        main_canvas.bind("<Configure>", lambda e: main_canvas.itemconfig("content", width=e.width))
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === SECTION HEADER ===
        hdr = tk.Frame(main, bg=self.design.get_color("bg_primary"))
        hdr.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(
            hdr, text=tr("tab_download", "Download"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_primary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold")
        ).pack(anchor="w")
        tk.Label(
            hdr, text=tr("download_subtitle", "Download videos and audio from YouTube"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        ).pack(anchor="w")
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("download_url", "YouTube URL"), dark_mode=self.dark_mode)
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_container = ttk.Frame(url_card.body)
        url_container.pack(fill=tk.X)
        
        # URL input with icon
        input_frame = ttk.Frame(url_container)
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        url_icon = get_ui_icon("video", size=Icons.SIZE_SM)
        if url_icon:
            url_icon_label = ttk.Label(input_frame, image=url_icon)
            url_icon_label.image = url_icon
            url_icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.download_url_entry = ttk.Entry(input_frame)
        self.download_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Verify button
        ModernButton(
            url_container,
            text=tr("download_verify", "Verify"),
            icon_name="verify",
            command=self.verify_video,
            variant="outline",
            size="sm",
            width=10
        ).pack(side=tk.LEFT)
        
        # === VIDEO INFO CARD (Metadata + Thumbnail) ===
        info_card = ModernCard(main, title=tr("download_info", "Video Information"), dark_mode=self.dark_mode)
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_row = ttk.Frame(info_card.body)
        info_row.pack(fill=tk.X)
        
        # Left: metadata grid
        info_grid = ttk.Frame(info_row)
        info_grid.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Title row
        ttk.Label(info_grid, text=f"{tr('download_title', 'Title')}:", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_title_label = ttk.Label(info_grid, text="-", style="Caption.TLabel", wraplength=350)
        self.download_title_label.grid(row=0, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Duration row
        ttk.Label(info_grid, text=f"{tr('download_duration', 'Duration')}:", style="Subtitle.TLabel").grid(
            row=1, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_duration_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.download_duration_label.grid(row=1, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Uploader row
        ttk.Label(info_grid, text=f"{tr('meta_uploader', 'Uploader')}:", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_uploader_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.download_uploader_label.grid(row=2, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Views row
        ttk.Label(info_grid, text=f"{tr('meta_views', 'Views')}:", style="Subtitle.TLabel").grid(
            row=3, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_views_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.download_views_label.grid(row=3, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Upload date row
        ttk.Label(info_grid, text=f"{tr('meta_upload_date', 'Upload Date')}:", style="Subtitle.TLabel").grid(
            row=4, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_date_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.download_date_label.grid(row=4, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Right: thumbnail placeholder
        self.thumbnail_frame = ttk.Frame(info_row)
        self.thumbnail_frame.pack(side=tk.RIGHT, padx=(Spacing.MD, 0))
        
        self.thumbnail_label = tk.Label(
            self.thumbnail_frame,
            text="🖼",
            width=20, height=6,
            bg=self.design.get_color("bg_tertiary"),
            fg=self.design.get_color("fg_tertiary"),
            font=("Segoe UI Emoji", 24),
            relief=tk.FLAT
        )
        self.thumbnail_label.pack()
        
        # === FORMAT SELECTION CARD ===
        format_card = ModernCard(main, title=tr("format_title", "Available Formats"), dark_mode=self.dark_mode)
        format_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        format_container = ttk.Frame(format_card.body)
        format_container.pack(fill=tk.X)
        
        ttk.Label(format_container, text=f"{tr('format_select', 'Select Format')}:", style="Subtitle.TLabel").pack(
            side=tk.LEFT, padx=(0, Spacing.SM)
        )
        
        self.format_var = tk.StringVar(value="auto")
        self.format_combo = ttk.Combobox(
            format_container,
            textvariable=self.format_var,
            state="readonly",
            width=60
        )
        self.format_combo['values'] = [tr("format_auto", "Auto (Best)")]
        self.format_combo.current(0)
        self.format_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        self.format_status_label = ttk.Label(format_card.body, text="", style="Caption.TLabel")
        self.format_status_label.pack(anchor=tk.W, pady=(Spacing.XS, 0))
        
        # === DOWNLOAD MODE CARD ===
        mode_card = ModernCard(main, title=tr("download_mode", "Download Mode"), dark_mode=self.dark_mode)
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.download_mode_var = tk.StringVar(value="full")
        
        modes = [
            ("full", tr("download_mode_full", "Complete Video")),
            ("range", tr("download_mode_range", "Time Range")),
            ("until", tr("download_mode_until", "Until Time")),
            ("audio", tr("download_mode_audio", "Audio Only")),
            ("playlist", tr("download_mode_playlist", "Full Playlist")),
            ("channel", tr("download_mode_channel", "Channel Videos"))
        ]
        
        mode_grid = ttk.Frame(mode_card.body)
        mode_grid.pack(fill=tk.X)
        
        for i, (value, text) in enumerate(modes):
            ttk.Radiobutton(
                mode_grid,
                text=text,
                variable=self.download_mode_var,
                value=value
            ).grid(row=i // 2, column=i % 2, sticky=tk.W, padx=Spacing.SM, pady=Spacing.XS)
        
        # === TIME RANGE CARD ===
        time_card = ModernCard(main, title=tr("download_time_range", "Time Range"), dark_mode=self.dark_mode)
        time_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        time_grid = ttk.Frame(time_card.body)
        time_grid.pack(fill=tk.X)
        
        # Start time
        ttk.Label(time_grid, text=f"{tr('download_start_time', 'Start Time')}:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, Spacing.SM), pady=Spacing.XS
        )
        self.time_start_entry = ttk.Entry(time_grid, width=12)
        self.time_start_entry.insert(0, "00:00:00")
        self.time_start_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, Spacing.XL), pady=Spacing.XS)
        
        # End time
        ttk.Label(time_grid, text=f"{tr('download_end_time', 'End Time')}:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, Spacing.SM), pady=Spacing.XS
        )
        self.time_end_entry = ttk.Entry(time_grid, width=12)
        self.time_end_entry.insert(0, "00:00:00")
        self.time_end_entry.grid(row=0, column=3, sticky=tk.W, pady=Spacing.XS)
        
        # Help text
        ttk.Label(
            time_card.body,
            text=tr("download_time_help", "Format: HH:MM:SS or MM:SS"),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(Spacing.SM, 0))
        
        # === QUALITY CARD ===
        quality_card = ModernCard(main, title=tr("download_quality", "Quality"), dark_mode=self.dark_mode)
        quality_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.download_quality_var = tk.StringVar(value="best")
        
        qualities = [
            ("best", tr("download_quality_best", "Best Quality")),
            ("mp4", tr("download_quality_mp4", "MP4 (Best)")),
            ("1080", "1080p Full HD"),
            ("720", "720p HD")
        ]
        
        quality_grid = ttk.Frame(quality_card.body)
        quality_grid.pack(fill=tk.X)
        
        for i, (value, text) in enumerate(qualities):
            ttk.Radiobutton(
                quality_grid,
                text=text,
                variable=self.download_quality_var,
                value=value
            ).grid(row=i // 2, column=i % 2, sticky=tk.W, padx=Spacing.SM, pady=Spacing.XS)
        
        # === AUDIO FORMAT CARD ===
        audio_card = ModernCard(main, title=tr("audio_format", "Audio Format"), dark_mode=self.dark_mode)
        audio_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Format selection
        self.audio_format_var = tk.StringVar(value="mp3")
        
        fmt_frame = ttk.Frame(audio_card.body)
        fmt_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        formats = [("mp3", "MP3"), ("wav", "WAV"), ("m4a", "M4A"), ("opus", "OPUS")]
        for value, text in formats:
            ttk.Radiobutton(
                fmt_frame,
                text=text,
                variable=self.audio_format_var,
                value=value
            ).pack(side=tk.LEFT, padx=(0, Spacing.LG))
        
        # Bitrate selection
        ttk.Label(audio_card.body, text=f"{tr('audio_bitrate', 'Bitrate')}:", style="Subtitle.TLabel").pack(
            anchor=tk.W, pady=(Spacing.SM, Spacing.XS)
        )
        
        self.audio_bitrate_var = tk.StringVar(value="320")
        
        bitrate_frame = ttk.Frame(audio_card.body)
        bitrate_frame.pack(fill=tk.X)
        
        for br in ["128", "192", "256", "320"]:
            ttk.Radiobutton(
                bitrate_frame,
                text=f"{br} kbps",
                variable=self.audio_bitrate_var,
                value=br
            ).pack(side=tk.LEFT, padx=(0, Spacing.LG))
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        ModernButton(
            action_frame,
            text=tr("download_btn", "Download"),
            icon_name="download",
            command=self.start_download,
            variant="primary",
            size="lg",
            width=14
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_stop", "Stop"),
            icon_name="stop",
            command=self.stop_download,
            variant="danger",
            size="lg",
            width=14
        ).pack(side=tk.LEFT)

        # Enable mouse wheel scroll AFTER all widgets are created
        self.enable_mousewheel_scroll(main_canvas, main)

        return frame
    
    def create_batch_tab(self):
        """Create batch download section"""
        tr = self.translator.get
        
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === SECTION HEADER ===
        hdr = tk.Frame(main, bg=self.design.get_color("bg_primary"))
        hdr.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(
            hdr, text=tr("tab_batch", "Batch Downloads"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_primary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold")
        ).pack(anchor="w")
        tk.Label(
            hdr, text=tr("batch_subtitle", "Download multiple videos at once"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        ).pack(anchor="w")
        
        # === URLS INPUT CARD ===
        urls_card = ModernCard(main, title=tr("batch_urls", "YouTube URLs"), dark_mode=self.dark_mode)
        urls_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        # Info text
        ttk.Label(
            urls_card.body,
            text=tr("batch_help", "Paste one URL per line. Up to 50 URLs supported."),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Text area
        text_container = ttk.Frame(urls_card.body)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        text_scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL)
        self.batch_text = tk.Text(
            text_container,
            height=12,
            yscrollcommand=text_scrollbar.set,
            font=(LOADED_FONT_FAMILY, Typography.SIZE_MD),
            wrap=tk.WORD
        )
        self.batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.batch_text.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons for text area
        text_actions = ttk.Frame(urls_card.body)
        text_actions.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        ModernButton(
            text_actions,
            text=tr("batch_paste", "Paste from Clipboard"),
            icon_name="paste",
            command=self.batch_paste,
            variant="outline",
            size="sm",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            text_actions,
            text=tr("batch_clear", "Clear All"),
            icon_name="clear",
            command=lambda: self.batch_text.delete(1.0, tk.END),
            variant="ghost",
            size="sm",
            width=12
        ).pack(side=tk.LEFT)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("batch_download_all", "Start Batch Download"),
            icon_name="download",
            command=self.start_batch_download,
            variant="primary",
            size="lg",
            width=22
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("batch_stop", "Stop All"),
            icon_name="stop",
            command=self.stop_download,
            variant="danger",
            size="lg",
            width=12
        ).pack(side=tk.LEFT)

        return frame
    
    def create_live_tab(self):
        """Create live stream recording section"""
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === SECTION HEADER ===
        hdr = tk.Frame(main, bg=self.design.get_color("bg_primary"))
        hdr.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(
            hdr, text=tr("live_title", "Live Stream Recorder"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_primary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold")
        ).pack(anchor="w")
        tk.Label(
            hdr, text=tr("live_subtitle", "Record live streams with customizable duration and quality"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        ).pack(anchor="w")
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("live_url", "Live Stream URL"), dark_mode=self.dark_mode)
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_row = ttk.Frame(url_card.body)
        url_row.pack(fill=tk.X)
        
        self.live_url_entry = ttk.Entry(url_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self.live_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        ModernButton(
            url_row,
            text=tr("live_check_stream", "Check"),
            icon_name="verify",
            command=self.verify_live_stream,
            variant="outline",
            size="sm",
            width=10
        ).pack(side=tk.LEFT)
        
        # === STREAM STATUS CARD ===
        status_card = ModernCard(main, title=tr("live_status", "Stream Status"), dark_mode=self.dark_mode)
        status_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        status_grid = ttk.Frame(status_card.body)
        status_grid.pack(fill=tk.X)
        
        ttk.Label(status_grid, text=f"{tr('live_status', 'Status')}:", style="Subtitle.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, Spacing.XL))
        self.live_status_label = ttk.Label(status_grid, text=tr("live_status_unknown", "Unknown"), style="Caption.TLabel")
        self.live_status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_grid, text=f"{tr('live_duration', 'Duration')}:", style="Subtitle.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, Spacing.XL), pady=(Spacing.SM, 0))
        self.live_duration_label = ttk.Label(status_grid, text="--:--:--", style="Caption.TLabel")
        self.live_duration_label.grid(row=1, column=1, sticky=tk.W, pady=(Spacing.SM, 0))
        
        # === RECORDING MODE CARD ===
        mode_card = ModernCard(main, title=tr("live_mode", "Recording Mode"), dark_mode=self.dark_mode)
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.live_mode_var = tk.StringVar(value="continuous")
        
        mode_options = [
            ("continuous", tr("live_mode_continuous", "Continuous Recording")),
            ("duration", tr("live_mode_duration", "Record Duration")),
            ("until", tr("live_mode_until", "Record Until Time"))
        ]
        
        for value, label in mode_options:
            ttk.Radiobutton(mode_card.body, text=label, variable=self.live_mode_var, value=value).pack(fill=tk.X, anchor=tk.W, pady=Spacing.XS)
        
        # === DURATION CARD ===
        duration_card = ModernCard(main, title=tr("live_duration_settings", "Duration Settings"), dark_mode=self.dark_mode)
        duration_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        duration_grid = ttk.Frame(duration_card.body)
        duration_grid.pack(fill=tk.X)
        
        for i, (key, default) in enumerate([("live_hours", "01"), ("live_minutes", "00"), ("live_seconds", "00")]):
            ttk.Label(duration_grid, text=f"{tr(key, key.split('_')[1].title())}:", style="Caption.TLabel").grid(row=0, column=i*2, sticky=tk.W, padx=(0 if i==0 else Spacing.MD, Spacing.XS))
            entry = ttk.Entry(duration_grid, width=6, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
            entry.insert(0, default)
            entry.grid(row=0, column=i*2+1, sticky=tk.W)
            setattr(self, f"{key}_entry", entry)
        
        # === QUALITY CARD ===
        quality_card = ModernCard(main, title=tr("live_quality", "Recording Quality"), dark_mode=self.dark_mode)
        quality_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.live_quality_var = tk.StringVar(value="best")
        
        quality_options = [
            ("best", tr("live_quality_best", "Best Available")),
            ("1080", "1080p Full HD"),
            ("720", "720p HD"),
            ("480", "480p SD")
        ]
        
        quality_grid = ttk.Frame(quality_card.body)
        quality_grid.pack(fill=tk.X)
        
        for i, (value, label) in enumerate(quality_options):
            ttk.Radiobutton(quality_grid, text=label, variable=self.live_quality_var, value=value).grid(
                row=i // 2, column=i % 2, sticky=tk.W, padx=Spacing.SM, pady=Spacing.XS
            )
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("live_start_recording", "Start Recording"),
            icon_name="record",
            command=self.start_live_recording,
            variant="primary",
            size="lg",
            width=18
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("live_stop_recording", "Stop"),
            icon_name="stop",
            command=self.stop_live_recording,
            variant="danger",
            size="lg",
            width=12
        ).pack(side=tk.LEFT)

        return frame
    
    def create_history_tab(self):
        """Create download history section"""
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === SECTION HEADER ===
        hdr = tk.Frame(main, bg=self.design.get_color("bg_primary"))
        hdr.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(
            hdr, text=tr("history_title", "Download History"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_primary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold")
        ).pack(anchor="w")
        tk.Label(
            hdr, text=tr("history_subtitle", "Track all your downloads in one place"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        ).pack(anchor="w")
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        ModernButton(
            action_frame,
            text=tr("history_update", "Refresh"),
            icon_name="refresh",
            command=self.refresh_history,
            variant="outline",
            width=12
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("history_clear", "Clear History"),
            icon_name="delete",
            command=self.clear_history,
            variant="danger",
            width=14
        ).pack(side=tk.LEFT)

        ttk.Label(
            action_frame,
            text=f"{tr('history_search', 'Search')}:",
            style="Caption.TLabel"
        ).pack(side=tk.LEFT, padx=(Spacing.LG, Spacing.SM))

        self.history_search_var = tk.StringVar()
        history_search_entry = ttk.Entry(action_frame, textvariable=self.history_search_var, width=28)
        history_search_entry.pack(side=tk.LEFT)
        history_search_entry.bind("<KeyRelease>", lambda _e: self.refresh_history())

        # === HISTORY TABLE CARD ===
        table_card = ModernCard(main, title=tr("history_records", "Download Records"), dark_mode=self.dark_mode)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(Spacing.MD, 0))
        
        # Scrollable records list
        canvas = tk.Canvas(table_card.body, bg=self.design.get_color("bg_tertiary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_card.body, orient=tk.VERTICAL, command=canvas.yview)
        self.history_records_frame = ttk.Frame(canvas)
        
        self.history_records_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.history_records_frame, anchor="nw", tags="content")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Update inner frame width on canvas resize
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("content", width=e.width))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scroll for history tab
        self.enable_mousewheel_scroll(canvas, self.history_records_frame)
        
        self.refresh_history()

        return frame
    
    def create_about_tab(self):
        """Create about section"""
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable container
        canvas = tk.Canvas(frame, bg=self.design.get_color("bg_primary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="content")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Update inner frame width on canvas resize
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("content", width=e.width))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scroll for about tab
        self.enable_mousewheel_scroll(canvas, scrollable_frame)
        
        # Content frame (no centering - just pack normally for visibility)
        main = ttk.Frame(scrollable_frame, padding=Spacing.XXL)
        main.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)
        
        # === SECTION HEADER ===
        hdr_bg = self.design.get_color("bg_primary")
        hdr = tk.Frame(main, bg=hdr_bg)
        hdr.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(
            hdr, text=tr("about_title", "EasyCut"),
            bg=hdr_bg, fg=self.design.get_color("fg_primary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_H1, "bold")
        ).pack(anchor="w")
        tk.Label(
            hdr, text=tr("about_subtitle", "Professional YouTube Downloader & Audio Converter"),
            bg=hdr_bg, fg=self.design.get_color("fg_secondary"),
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        ).pack(anchor="w")
        
        # === LEGAL DISCLAIMER CARD ===
        disclaimer_card = ModernCard(main, title="⚠️ " + tr("about_section_legal", "Legal Notice - Personal Use Only"), dark_mode=self.dark_mode)
        disclaimer_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        disclaimer_bg = self.design.get_color("warning") if not self.dark_mode else "#3d2f00"
        disclaimer_fg = self.design.get_color("fg_primary")
        
        disclaimer_frame = tk.Frame(disclaimer_card.body, bg=disclaimer_bg, padx=Spacing.MD, pady=Spacing.MD)
        disclaimer_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        disclaimer_text = tr(
            "about_legal_disclaimer",
            "FOR PERSONAL USE ONLY\n\n"
            "EasyCut is intended for downloading:\n"
            "• Your own videos uploaded to YouTube\n"
            "• Content with explicit creator permission\n"
            "• Content allowed under fair use in your jurisdiction\n\n"
            "YOU ARE RESPONSIBLE FOR:\n"
            "• Complying with YouTube's Terms of Service\n"
            "• Respecting copyright laws\n"
            "• Obtaining necessary permissions\n\n"
            "Developers are NOT responsible for copyright violations or misuse."
        )
        
        tk.Label(
            disclaimer_frame,
            text=disclaimer_text,
            bg=disclaimer_bg,
            fg=disclaimer_fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            justify=tk.LEFT,
            wraplength=600
        ).pack(anchor="w")
        
        # === APP INFO CARD ===
        info_card = ModernCard(main, title=tr("about_section_info", "Application Info"), dark_mode=self.dark_mode)
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_data = [
            ("Version", "1.2.1"),
            ("Author", "Deko Costa"),
            ("License", "GPL-3.0"),
            ("Release", "2026")
        ]
        
        for label, value in info_data:
            row = ttk.Frame(info_card.body)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === SOCIAL LINKS CARD ===
        social_card = ModernCard(main, title=tr("about_section_links", "Connect & Support"), dark_mode=self.dark_mode)
        social_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        def open_link(url):
            import webbrowser
            webbrowser.open(url)
        
        links = [
            (tr("about_link_github", "GitHub Repository"), "https://github.com/dekouninter/EasyCut"),
            (tr("about_link_coffee", "Buy Me a Coffee"), "https://buymeacoffee.com/dekocosta"),
            (tr("about_link_kofi", "Support on Ko-fi"), "https://ko-fi.com/dekocosta"),
            (tr("about_link_livepix", "Livepix (Brazil)"), "https://livepix.gg/dekocosta"),
        ]
        
        for label, url in links:
            ModernButton(
                social_card.body,
                text=label,
                command=lambda u=url: open_link(u),
                variant="outline",
                width=30
            ).pack(pady=(0, Spacing.SM), fill=tk.X)
        
        # === TECHNOLOGIES CARD ===
        tech_card = ModernCard(main, title=tr("about_section_tech", "Technologies & Credits"), dark_mode=self.dark_mode)
        tech_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        tech_data = [
            ("Core", "Python 3.13 + Tkinter"),
            ("Downloader", "yt-dlp (Unlicense)"),
            ("Converter", "FFmpeg (GPL-2.0+)"),
            ("Security", "OAuth 2.0"),
            ("Icons", "Feather Icons (MIT)"),
            ("Font", "Inter (OFL 1.1)"),
            ("Image", "Pillow (HPND)")
        ]
        
        for label, value in tech_data:
            row = ttk.Frame(tech_card.body)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === THANKS CARD ===
        thanks_card = ModernCard(main, title=tr("about_section_thanks", "Special Thanks"), dark_mode=self.dark_mode)
        thanks_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        thanks_text = tr(
            "about_thanks_text",
            "Thanks to the open-source community, yt-dlp developers, FFmpeg team, and all contributors who make projects like this possible."
        )
        ttk.Label(
            thanks_card.body,
            text=thanks_text,
            style="Caption.TLabel",
            wraplength=600,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # === FOOTER ===
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=Spacing.LG)
        
        ttk.Label(
            main,
            text=tr("about_footer", "Made with Python | GPL-3.0 License | 2026 Deko Costa"),
            style="Caption.TLabel"
        ).pack(pady=Spacing.MD)

        return frame
    
    def apply_theme(self):
        """Apply modern theme to window"""
        style = ttk.Style()
        
        # Try to use a custom theme base (avoid Windows theme conflicts)
        try:
            style.theme_use("clam")  # Use base theme compatible with customization
        except:
            pass  # If clam not available, continue anyway
        
        self.theme.apply_to_style(style)
        
        # Force configure root colors and option database
        bg_color = self.design.get_color("bg_primary")
        fg_color = self.design.get_color("fg_primary")
        
        self.root.config(bg=bg_color)
        
        # Force colors through X11 option database (affects ALL widgets globally)
        self.root.option_add("*TFrame.background", bg_color)
        self.root.option_add("*TLabel.background", bg_color)
        self.root.option_add("*TLabel.foreground", fg_color)
        self.root.option_add("*Label.background", bg_color)
        self.root.option_add("*Label.foreground", fg_color)
        self.root.option_add("*background", bg_color)
        self.root.option_add("*foreground", fg_color)
        
        # Combobox dropdown list colors
        self.root.option_add("*TCombobox*Listbox.background", self.design.get_color("bg_secondary"))
        self.root.option_add("*TCombobox*Listbox.foreground", fg_color)
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.design.get_color("accent_primary"))
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
    
    def toggle_theme(self):
        """Toggle theme with instant reload"""
        self.theme.toggle()
        self.design.toggle_mode()
        self.dark_mode = not self.dark_mode
        self.config_manager.set("dark_mode", self.dark_mode)
        set_icon_theme(self.dark_mode)  # Update icon colors
        self.apply_theme()
        self.setup_ui()
        self.log_app("✓ Theme changed instantly")
    
    def change_language(self, lang):
        """Change language with instant reload"""
        if self.translator.set_language(lang):
            self.language = lang
            self.config_manager.set("language", lang)
            self.setup_ui()
            self.log_app(f"✓ Language changed to {lang.upper()}")
    
    def open_login_popup(self):
        """Deprecated: Login popup replaced by browser authentication"""
        tr = self.translator.get
        messagebox.showinfo(
            tr("browser_cookies_title", "Browser Authentication"),
            tr("browser_cookies_info", "EasyCut now uses cookies from your browser.\nSelect your browser in the settings above.")
        )
    
    def check_saved_credentials(self):
        """Deprecated: Credential saving replaced by browser cookies"""
        pass
    
    def update_login_status(self):
        """Deprecated: Login status replaced by browser selection"""
        pass
    
    def get_browser_profile_paths(self, browser):
        """Get list of profile directories for a browser
        
        Args:
            browser (str): Browser name (chrome, firefox, edge, etc.)
            
        Returns:
            list: List of (profile_name, profile_path) tuples
        """
        profiles = []
        
        try:
            if browser == "chrome":
                base = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
            elif browser == "edge":
                base = Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data"
            elif browser == "brave":
                base = Path.home() / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data"
            elif browser == "opera":
                base = Path.home() / "AppData" / "Roaming" / "Opera Software" / "Opera Stable"
            elif browser == "firefox":
                base = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
            else:
                return profiles
            
            if not base.exists():
                return profiles
            
            # For Chromium-based browsers
            if browser in ["chrome", "edge", "brave", "opera"]:
                # Check Default profile
                if (base / "Default").exists():
                    profiles.append(("Default", str(base / "Default")))
                
                # Check Profile 1, Profile 2, etc.
                for i in range(1, 20):  # Check up to Profile 19
                    profile_dir = base / f"Profile {i}"
                    if profile_dir.exists():
                        profiles.append((f"Profile {i}", str(profile_dir)))
            
            # For Firefox
            elif browser == "firefox":
                for profile_dir in base.iterdir():
                    if profile_dir.is_dir() and not profile_dir.name.startswith('.'):
                        profiles.append((profile_dir.name, str(profile_dir)))
        
        except Exception as e:
            print(f"Error getting browser profiles: {e}")
        
        return profiles
    
    def detect_youtube_accounts(self):
        """Detect YouTube accounts from browser profiles
        
        Returns:
            list: List of (display_name, browser, profile_name) tuples
        """
        tr = self.translator.get
        accounts = []
        
        browser = self.config_manager.get("browser_cookies", "chrome")
        if browser == "none":
            return accounts
        
        # Update status
        if hasattr(self, 'account_status_label'):
            self.account_status_label.config(
                text=tr("browser_profile_detecting", "Detecting accounts..."),
                fg=self.design.get_color("fg_secondary")
            )
            self.root.update()
        
        profiles = self.get_browser_profile_paths(browser)
        
        # Try to get account names from browser preferences
        for profile_name, profile_path in profiles:
            account_name = None
            
            # Try to read account info from Chrome/Edge Preferences file
            if browser in ["chrome", "edge", "brave"]:
                try:
                    import json as json_module
                    prefs_file = Path(profile_path) / "Preferences"
                    if prefs_file.exists():
                        with open(prefs_file, 'r', encoding='utf-8') as f:
                            prefs = json_module.load(f)
                            # Try to get Google account info
                            account_info = prefs.get('account_info', [])
                            if account_info and len(account_info) > 0:
                                account_name = account_info[0].get('full_name') or account_info[0].get('email', '').split('@')[0]
                except Exception:
                    pass
            
            # Build display name
            if account_name:
                display_name = f"{account_name} ({browser.capitalize()} - {profile_name})"
            else:
                display_name = f"{browser.capitalize()} - {profile_name}"
            
            accounts.append((display_name, browser, profile_name))
        
        return accounts
    
    def refresh_browser_profiles(self):
        """Refresh the browser profile dropdown with detected accounts"""
        tr = self.translator.get
        
        if not hasattr(self, 'profile_combo'):
            return
        
        # Run detection in background thread
        def detect_thread():
            accounts = self.detect_youtube_accounts()
            
            # Update UI in main thread
            def update_ui():
                if not accounts:
                    self.profile_combo['values'] = [tr("browser_profile_none_found", "No accounts found")]
                    self.profile_combo.current(0)
                    if hasattr(self, 'account_status_label'):
                        self.account_status_label.config(
                            text=tr("browser_profile_none_found", "No accounts found"),
                            fg=self.design.get_color("warning")
                        )
                else:
                    # Store account mapping
                    self.detected_accounts = accounts
                    display_names = [acc[0] for acc in accounts]
                    self.profile_combo['values'] = display_names
                    self.profile_combo.current(0)
                    
                    # Update account status
                    if hasattr(self, 'account_status_label'):
                        self.account_status_label.config(
                            text=f"✓ {len(accounts)} account(s) found",
                            fg=self.design.get_color("success")
                        )
                    
                    # Auto-select based on saved config
                    saved_profile = self.config_manager.get("browser_profile", "")
                    if saved_profile:
                        for i, (_, _, profile_name) in enumerate(accounts):
                            if profile_name == saved_profile:
                                self.profile_combo.current(i)
                                break
            
            self.root.after(0, update_ui)
        
        thread = threading.Thread(target=detect_thread, daemon=True)
        thread.start()
    
    def get_ydl_opts_with_cookies(self, base_opts=None):
        """Get yt-dlp options with OAuth cookies configured
        
        Args:
            base_opts (dict): Base options to extend
            
        Returns:
            dict: yt-dlp options with OAuth cookies file configured
        """
        opts = base_opts.copy() if base_opts else {}
        
        # Get OAuth cookies file
        cookies_file = Path("config") / "yt_cookies.txt"
        
        if cookies_file.exists():
            opts['cookiefile'] = str(cookies_file)
        
        return opts
    
    def test_browser_connection(self):
        """Test if browser authentication is working"""
        tr = self.translator.get
        
        if not YT_DLP_AVAILABLE:
            messagebox.showerror(tr("msg_error", "Error"), "yt-dlp not available")
            return
        
        # Update status to "checking"
        self.account_status_label.config(
            text=tr("browser_test_checking", "Testing connection..."),
            fg=self.design.get_color("fg_secondary")
        )
        self.root.update()
        
        def test_thread():
            try:
                # Try to extract info from a YouTube URL that requires authentication
                # Using youtube.com/feed/subscriptions or a simple public video
                test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video
                
                ydl_opts = self.get_ydl_opts_with_cookies({
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'skip_download': True
                })
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(test_url, download=False)
                    
                    # Check if we got auth info
                    uploader = info.get('uploader', '')
                    channel = info.get('channel', '')
                    
                    # Try to get user info if authenticated
                    # Note: yt-dlp doesn't easily expose the logged-in username,
                    # but we can check if we have access to private features
                    
                    if uploader or channel:
                        self.account_status_label.config(
                            text=f"{tr('browser_test_success', '✓ Connected to YouTube')}",
                            fg=self.design.get_color("success")
                        )
                        if hasattr(self, 'download_log') and self.download_log:
                            self.download_log.add_log(tr("browser_test_success", "✓ Connection successful"))
                    else:
                        self.account_status_label.config(
                            text=tr("browser_test_no_auth", "⚠ Not authenticated"),
                            fg=self.design.get_color("warning")
                        )
                
            except Exception as e:
                error_msg = str(e)
                # Check if error is due to browser being open
                if "Could not copy" in error_msg and "cookie database" in error_msg:
                    self.account_status_label.config(
                        text=tr("browser_test_browser_open", "⚠️ Browser is open! Close it first."),
                        fg=self.design.get_color("warning")
                    )
                    if hasattr(self, 'download_log') and self.download_log:
                        self.download_log.add_log(tr("browser_test_browser_open", "⚠️ Browser is open! Close it first."), "WARNING")
                else:
                    self.account_status_label.config(
                        text=f"{tr('browser_test_failed', '✗ Connection failed')}: {error_msg[:50]}",
                        fg=self.design.get_color("error")
                    )
                    if hasattr(self, 'download_log') and self.download_log:
                        self.download_log.add_log(f"Connection test failed: {error_msg}", "ERROR")
        
        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()
    
    def verify_video(self):
        """Verify video URL and fetch full metadata, formats, and thumbnail"""
        tr = self.translator.get
        url = self.download_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        self.download_log.add_log(tr("meta_fetching", "Fetching video info..."))
        self.format_status_label.config(text=tr("format_fetching", "Fetching available formats..."))
        
        # Reset metadata UI
        self.download_title_label.config(text="...")
        self.download_duration_label.config(text="...")
        self.download_uploader_label.config(text="...")
        self.download_views_label.config(text="...")
        self.download_date_label.config(text="...")
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.download_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                return
            
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                
                # Cache the full info
                self._video_info_cache = info
                
                # --- Metadata ---
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', info.get('channel', '-'))
                view_count = info.get('view_count', 0)
                upload_date = info.get('upload_date', '')  # YYYYMMDD
                video_id = info.get('id', '')
                
                # Format duration
                if duration:
                    hours, remainder = divmod(int(duration), 3600)
                    mins, secs = divmod(remainder, 60)
                    dur_str = f"{hours}:{mins:02d}:{secs:02d}" if hours else f"{mins}:{secs:02d}"
                else:
                    dur_str = "-"
                
                # Format views
                if view_count:
                    if view_count >= 1_000_000:
                        views_str = f"{view_count / 1_000_000:.1f}M"
                    elif view_count >= 1_000:
                        views_str = f"{view_count / 1_000:.1f}K"
                    else:
                        views_str = str(view_count)
                else:
                    views_str = "-"
                
                # Format upload date
                if upload_date and len(upload_date) == 8:
                    date_str = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[:4]}"
                else:
                    date_str = "-"
                
                # Update metadata labels (thread-safe via root.after)
                self.root.after(0, lambda: self.download_title_label.config(text=title[:80]))
                self.root.after(0, lambda: self.download_duration_label.config(text=dur_str))
                self.root.after(0, lambda: self.download_uploader_label.config(text=uploader[:50]))
                self.root.after(0, lambda: self.download_views_label.config(text=views_str))
                self.root.after(0, lambda: self.download_date_label.config(text=date_str))
                
                # --- Thumbnail ---
                thumbnail_url = info.get('thumbnail', '')
                if thumbnail_url:
                    self._load_thumbnail(thumbnail_url)
                
                # --- Available Formats ---
                formats = info.get('formats', [])
                self._video_formats = formats
                self._populate_format_combo(formats)
                
                # --- Duplicate Detection ---
                self._check_duplicate(video_id, title)
                
                self.root.after(0, lambda: self.download_log.add_log(
                    tr("log_video_info", "Video info retrieved successfully")
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.download_log.add_log(
                    f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR"
                ))
                self.root.after(0, lambda: self.format_status_label.config(text=""))
        
        thread = threading.Thread(target=verify_thread, daemon=True)
        thread.start()
    
    def _load_thumbnail(self, url: str):
        """Load thumbnail from URL and display in UI"""
        try:
            import urllib.request
            import io
            from PIL import Image, ImageTk
            
            # Download thumbnail
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
            
            # Resize to fit UI (160x90 = 16:9)
            img = Image.open(io.BytesIO(data))
            img = img.resize((160, 90), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            def update_ui():
                self.thumbnail_label.config(image=photo, text="", width=160, height=90)
                self.thumbnail_label.image = photo  # Keep reference
            
            self.root.after(0, update_ui)
        except Exception as e:
            self.logger.debug(f"Thumbnail load failed: {e}")
    
    def _populate_format_combo(self, formats: list):
        """Populate the format selection combobox with available formats"""
        tr = self.translator.get
        
        format_options = [tr("format_auto", "Auto (Best)")]
        self._format_id_map = {"auto": None}  # Maps display index to format_id
        
        # Categorize and sort formats
        video_audio = []
        video_only = []
        audio_only = []
        
        for f in formats:
            fmt_id = f.get('format_id', '?')
            ext = f.get('ext', '?')
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')
            height = f.get('height')
            fps = f.get('fps')
            filesize = f.get('filesize') or f.get('filesize_approx')
            tbr = f.get('tbr')
            note = f.get('format_note', '')
            
            has_video = vcodec and vcodec != 'none'
            has_audio = acodec and acodec != 'none'
            
            # Build display string
            parts = []
            if height:
                parts.append(f"{height}p")
            if fps:
                parts.append(f"{fps}fps")
            if ext:
                parts.append(ext)
            if tbr:
                parts.append(f"{int(tbr)}kbps")
            if filesize:
                size_mb = filesize / (1024 * 1024)
                parts.append(f"{size_mb:.1f}MB" if size_mb < 1024 else f"{size_mb/1024:.1f}GB")
            if note:
                parts.append(note)
            
            display = f"[{fmt_id}] {' | '.join(parts)}"
            
            if has_video and has_audio:
                video_audio.append((display, fmt_id, height or 0))
            elif has_video:
                video_only.append((display + " [V]", fmt_id, height or 0))
            elif has_audio:
                audio_only.append((display + " [A]", fmt_id, 0))
        
        # Sort by resolution (highest first)
        video_audio.sort(key=lambda x: x[2], reverse=True)
        video_only.sort(key=lambda x: x[2], reverse=True)
        
        idx = 1
        if video_audio:
            format_options.append(f"── {tr('format_video_audio', 'Video + Audio')} ──")
            self._format_id_map[idx] = None  # separator
            idx += 1
            for display, fmt_id, _ in video_audio[:15]:  # Limit to top 15
                format_options.append(display)
                self._format_id_map[idx] = fmt_id
                idx += 1
        
        if video_only:
            format_options.append(f"── {tr('format_video_only', 'Video Only')} ──")
            self._format_id_map[idx] = None
            idx += 1
            for display, fmt_id, _ in video_only[:10]:
                format_options.append(display)
                self._format_id_map[idx] = fmt_id
                idx += 1
        
        if audio_only:
            format_options.append(f"── {tr('format_audio_only', 'Audio Only')} ──")
            self._format_id_map[idx] = None
            idx += 1
            for display, fmt_id, _ in audio_only[:10]:
                format_options.append(display)
                self._format_id_map[idx] = fmt_id
                idx += 1
        
        total = len(video_audio) + len(video_only) + len(audio_only)
        status = tr("format_count", "{} formats available").format(total)
        
        def update_ui():
            self.format_combo['values'] = format_options
            self.format_combo.current(0)
            self.format_status_label.config(text=status)
        
        self.root.after(0, update_ui)
    
    def _get_selected_format_id(self):
        """Get the yt-dlp format ID from the combobox selection, or None for auto"""
        if not hasattr(self, '_format_id_map'):
            return None
        idx = self.format_combo.current()
        fmt_id = self._format_id_map.get(idx)
        return fmt_id
    
    def _check_duplicate(self, video_id: str, title: str):
        """Check if video was already downloaded and warn user"""
        tr = self.translator.get
        if not video_id:
            return
        
        history = self.config_manager.load_history()
        for entry in history:
            entry_url = entry.get("url", "")
            if video_id in entry_url and entry.get("status") == "success":
                self.root.after(0, lambda t=title: self.download_log.add_log(
                    f"⚠ {tr('dup_found', 'This video was already downloaded:')} {t[:40]}",
                    "WARNING"
                ))
                return

    @staticmethod
    def _parse_timecode(time_text: str):
        """Parse HH:MM:SS or MM:SS into total seconds."""
        parts = time_text.split(":")
        if not parts or len(parts) > 3:
            return None
        if any(not p.isdigit() for p in parts):
            return None
        nums = [int(p) for p in parts]
        if len(nums) == 1:
            hours, minutes, seconds = 0, 0, nums[0]
        elif len(nums) == 2:
            hours, minutes, seconds = 0, nums[0], nums[1]
        else:
            hours, minutes, seconds = nums
        if minutes >= 60 or seconds >= 60:
            return None
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def _format_timecode(total_seconds: int) -> str:
        """Format seconds as HH:MM:SS."""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _build_download_section(self, mode: str):
        """Build yt-dlp download section for range/until modes."""
        if mode not in ("range", "until"):
            return None

        tr = self.translator.get
        start_text = self.time_start_entry.get().strip()
        end_text = self.time_end_entry.get().strip()

        start_seconds = self._parse_timecode(start_text) if mode == "range" else 0
        end_seconds = self._parse_timecode(end_text)

        if end_seconds is None or (mode == "range" and start_seconds is None):
            raise ValueError(tr("download_time_invalid", "Invalid time format. Use HH:MM:SS or MM:SS."))

        if mode == "range" and end_seconds <= start_seconds:
            raise ValueError(tr("download_time_order", "End time must be greater than start time."))

        start_tc = self._format_timecode(start_seconds)
        end_tc = self._format_timecode(end_seconds)
        return f"*{start_tc}-{end_tc}"

    def _build_download_options(self, output_template: str, quality: str, mode: str, section: str = None, quiet: bool = False, format_id: str = None):
        """Create yt-dlp options for a download."""
        # If a specific format_id was selected from the format combo, use it directly
        if format_id:
            format_str = format_id
        else:
            format_map = {
                'best': 'bestvideo+bestaudio/best',
                'mp4': 'best[ext=mp4]/best',
                '1080': 'bestvideo[height<=1080]+bestaudio/best',
                '720': 'bestvideo[height<=720]+bestaudio/best',
                'audio': 'bestaudio/best'
            }
            format_str = format_map.get(quality, 'best')

        base_opts = {
            'format': format_str,
            'outtmpl': output_template,
            'quiet': quiet,
        }
        
        # Playlist handling
        if mode == "playlist":
            base_opts['noplaylist'] = False  # Download entire playlist
        elif mode == "channel":
            base_opts['noplaylist'] = False  # Enable playlist for channels
            base_opts['playlistend'] = 10  # Download last 10 videos by default
        else:
            base_opts['noplaylist'] = True  # Download single video only

        if section:
            base_opts['download_sections'] = [section]

        if mode == "audio":
            audio_codec = self.audio_format_var.get()
            audio_quality = self.audio_bitrate_var.get()
            base_opts['format'] = 'bestaudio/best'
            base_opts['postprocessors'] = [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_codec,
                    'preferredquality': audio_quality,
                }
            ]

        return base_opts

    def _run_ydl_download(self, url: str, ydl_opts: dict):
        """Run yt-dlp download with a concurrency limit."""
        with self.download_semaphore:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)
    
    def start_download(self):
        """Start downloading video"""
        tr = self.translator.get
        url = self.download_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        if self.is_downloading:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("download_progress", "Downloading..."))
            return
        
        # --- Duplicate detection ---
        if self._video_info_cache:
            video_id = self._video_info_cache.get('id', '')
            cached_title = self._video_info_cache.get('title', '')
            if video_id:
                history = self.config_manager.load_history()
                for entry in history:
                    if video_id in entry.get('url', '') and entry.get('status') == 'success':
                        answer = messagebox.askyesno(
                            tr('dup_title', 'Duplicate Detected'),
                            f"{tr('dup_found', 'This video was already downloaded:')}\n{cached_title[:60]}\n\n{tr('dup_overwrite', 'Download again?')}"
                        )
                        if not answer:
                            self.download_log.add_log(tr('dup_skipped', 'Download skipped (duplicate)'))
                            return
                        break
        
        self.is_downloading = True
        self.download_log.add_log(f"{tr('log_downloading', 'Downloading video from')} {url}")
        
        quality = self.download_quality_var.get()
        mode = self.download_mode_var.get()
        
        # Structured logging
        self.logger.info(f"Download started: {url}")
        self.logger.info(f"  Quality: {quality}, Mode: {mode}")

        if mode == "audio" and not shutil.which("ffmpeg"):
            messagebox.showerror(
                tr("msg_error", "Error"),
                tr("log_ffmpeg_not_found", "FFmpeg not found. Audio conversion may not work.")
            )
            self.is_downloading = False
            return

        # Build time range section (not applicable for playlist mode)
        section = None
        if mode in ("range", "until"):
            try:
                section = self._build_download_section(mode)
            except ValueError as exc:
                messagebox.showerror(tr("msg_error", "Error"), str(exc))
                self.is_downloading = False
                return
        
        def download_thread():
            if not YT_DLP_AVAILABLE:
                self.download_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                self.is_downloading = False
                return
            
            try:
                # Use specific format from combobox if selected
                selected_format_id = self._get_selected_format_id()
                
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
                base_opts = self._build_download_options(
                    output_template, quality, mode,
                    section=section, quiet=False,
                    format_id=selected_format_id
                )
                ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                
                info = self._run_ydl_download(url, ydl_opts)

                entry = {
                    "date": datetime.now().isoformat(),
                    "filename": info.get('title', 'unknown'),
                    "status": "success",
                    "url": url
                }
                self.config_manager.add_to_history(entry)
                
                # Structured logging
                self.logger.info(f"Download completed: {info.get('title', 'unknown')}")
                self.logger.info(f"  File: {info.get('_filename', 'unknown')}")

                self.download_log.add_log(tr("download_success", "Download completed successfully!"))
                self.refresh_history()
            
            except Exception as e:
                error_msg = str(e)
                # Structured logging
                self.logger.error(f"Download failed: {url}")
                self.logger.error(f"  Error: {error_msg}")
                
                # Check if error is due to browser being open
                if "Could not copy" in error_msg and "cookie database" in error_msg:
                    self.download_log.add_log(tr("browser_test_browser_open", "⚠️ Browser is open! Close it first."), "WARNING")
                else:
                    self.download_log.add_log(f"{tr('msg_error', 'Error')}: {error_msg}", "ERROR")
            
            finally:
                self.is_downloading = False
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def stop_download(self):
        """Stop current download"""
        tr = self.translator.get
        self.is_downloading = False
        self.download_log.add_log(tr("download_stop", "Stop"))
    
    def on_closing(self):
        """Handle application closing gracefully"""
        tr = self.translator.get
        
        # Check if downloads are active
        if self.is_downloading:
            response = messagebox.askyesnocancel(
                tr("msg_confirm", "Confirm"),
                tr("msg_download_active", "Downloads are in progress. Close anyway?")
            )
            if not response:  # User clicked No or Cancel
                return
        
        # Log shutdown
        self.logger.info("Application shutdown initiated")
        
        # Save current config
        try:
            self.config_manager.set("output_dir", str(self.output_dir))
            self.config_manager.set("language", self.language)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
        
        # Final log
        self.logger.info("EasyCut Application Closed")
        self.logger.info("="*60)
        
        # Destroy window
        self.root.destroy()
    
    def start_batch_download(self):
        """Start batch download"""
        tr = self.translator.get
        urls_text = self.batch_text.get(1.0, tk.END).strip()
        
        if not urls_text:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("batch_empty", "Add at least one URL"))
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Get current download mode and quality from UI
        quality = self.download_quality_var.get()
        mode = self.download_mode_var.get()
        
        # Check FFmpeg for audio mode before starting batch
        if mode == "audio" and not shutil.which("ffmpeg"):
            messagebox.showerror(
                tr("msg_error", "Error"),
                tr("log_ffmpeg_not_found", "FFmpeg not found. Audio conversion may not work.")
            )
            return
        
        # Build time range section if needed
        section = None
        if mode in ("range", "until"):
            try:
                section = self._build_download_section(mode)
            except ValueError as exc:
                messagebox.showerror(tr("msg_error", "Error"), str(exc))
                return
        
        self.batch_log.add_log(f"{tr('batch_progress', 'Downloading batch')} ({len(urls)})")
        
        # Structured logging
        self.logger.info(f"Batch download started: {len(urls)} URLs")
        self.logger.info(f"  Quality: {quality}, Mode: {mode}")
        
        def batch_thread():
            success = 0
            for i, url in enumerate(urls, 1):
                if not self.is_valid_youtube_url(url):
                    self.batch_log.add_log(f"[{i}/{len(urls)}] {tr('download_invalid_url', 'Invalid URL')}", "WARNING")
                    continue
                
                if not YT_DLP_AVAILABLE:
                    self.batch_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                    break
                
                try:
                    output_template = str(self.output_dir / "%(title)s.%(ext)s")
                    base_opts = self._build_download_options(output_template, quality, mode, section=section, quiet=True)
                    ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                    
                    info = self._run_ydl_download(url, ydl_opts)
                    success += 1
                    self.batch_log.add_log(f"[{i}/{len(urls)}] {info.get('title', 'Video')[:30]}")
                    
                    # Add per-video history entry
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": info.get('title', 'unknown'),
                        "status": "success",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                
                except Exception as e:
                    error_msg = str(e)
                    # Check if error is due to browser being open
                    if "Could not copy" in error_msg and "cookie database" in error_msg:
                        self.batch_log.add_log(f"[{i}/{len(urls)}] {tr('browser_test_browser_open', '⚠️ Browser is open! Close it first.')}", "WARNING")
                        break  # Stop batch if browser is open
                    else:
                        self.batch_log.add_log(f"[{i}/{len(urls)}] ✗ Error: {error_msg[:50]}", "ERROR")
            
            self.batch_log.add_log(f"Batch complete: {success}/{len(urls)} successful")
            self.logger.info(f"Batch download completed: {success}/{len(urls)} successful")
            self.refresh_history()
        
        thread = threading.Thread(target=batch_thread, daemon=True)
        thread.start()
    
    def batch_paste(self):
        """Paste from clipboard"""
        tr = self.translator.get
        try:
            data = self.root.clipboard_get()
            self.batch_text.insert(tk.END, data)
        except Exception as e:
            messagebox.showerror(tr("msg_error", "Error"), f"{tr('msg_error', 'Error')}: {e}")
    

    
    def refresh_history(self):
        """Refresh download history with improved card layout"""
        tr = self.translator.get
        
        # Clear existing records
        for widget in self.history_records_frame.winfo_children():
            widget.destroy()
        
        history = self.config_manager.load_history()

        query = ""
        if hasattr(self, "history_search_var"):
            query = self.history_search_var.get().strip().lower()

        if query:
            filtered = []
            for item in history:
                filename = str(item.get("filename", "")).lower()
                url = str(item.get("url", "")).lower()
                status = str(item.get("status", "")).lower()
                date = str(item.get("date", "")).lower()
                if query in filename or query in url or query in status or query in date:
                    filtered.append(item)
            history = filtered

        if not history:
            empty_label = ttk.Label(
                self.history_records_frame,
                text=tr("history_no_results", "No downloads match your search") if query else tr("history_empty", "No downloads yet"),
                style="Caption.TLabel"
            )
            empty_label.pack(pady=Spacing.XXL)
            return
        
        # Display records as cards
        for item in reversed(history):
            try:
                date_obj = datetime.fromisoformat(item.get("date", ""))
                date_str = date_obj.strftime("%d/%m/%Y %H:%M")
                filename = item.get("filename", "unknown")
                status = item.get("status", "unknown")
                
                # Create record card
                record_card = ModernCard(self.history_records_frame, dark_mode=self.dark_mode)
                record_card.pack(fill=tk.X, pady=Spacing.XS, padx=0)
                
                # Status color
                status_color_map = {
                    "success": self.design.get_color("success"),
                    "error": self.design.get_color("error"),
                    "pending": self.design.get_color("warning")
                }
                status_color = status_color_map.get(status, self.design.get_color("info"))
                status_emoji_map = {
                    "success": "✅",
                    "error": "❌",
                    "pending": "⏳"
                }
                status_emoji = status_emoji_map.get(status, "ℹ️")
                
                # Header with status
                header_frame = ttk.Frame(record_card.body)
                header_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
                
                status_label = tk.Label(
                    header_frame,
                    text=status_emoji,
                    font=("Segoe UI Emoji", 14),
                    fg=status_color,
                    bg=self.design.get_color("bg_tertiary")
                )
                status_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
                
                filename_label = tk.Label(
                    header_frame,
                    text=filename[:50],
                    font=(LOADED_FONT_FAMILY, 11, "bold"),
                    fg=self.design.get_color("fg_primary"),
                    bg=self.design.get_color("bg_tertiary"),
                    wraplength=400,
                    justify=tk.LEFT
                )
                filename_label.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)
                
                date_label = tk.Label(
                    header_frame,
                    text=date_str,
                    font=(LOADED_FONT_FAMILY, 9),
                    fg=self.design.get_color("fg_tertiary"),
                    bg=self.design.get_color("bg_tertiary")
                )
                date_label.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
                
            except Exception as e:
                self.logger.warning(f"Error displaying history record: {e}")
    
    def clear_history(self):
        """Clear download history"""
        tr = self.translator.get
        if messagebox.askyesno(tr("msg_confirm", "Confirm"), tr("history_clear", "Clear History") + "?"):
            self.config_manager.save_history([])
            self.refresh_history()
    
    def open_output_folder(self):
        """Open output folder"""
        tr = self.translator.get
        try:
            import subprocess
            subprocess.Popen(f'explorer "{self.output_dir}"')
        except Exception as e:
            messagebox.showerror(tr("msg_error", "Error"), f"{tr('msg_error', 'Error')}: {e}")
    
    def select_output_folder(self):
        """Let user select output folder"""
        tr = self.translator.get
        try:
            selected_dir = filedialog.askdirectory(
                title=tr("header_select_folder", "Select Folder"),
                initialdir=str(self.output_dir)
            )
            if selected_dir:
                self.output_dir = Path(selected_dir)
                self.config_manager.set("output_dir", str(self.output_dir))
                messagebox.showinfo(
                    tr("msg_info", "Information"),
                    tr("folder_selected", f"Output folder changed to:\n{self.output_dir}")
                )
        except Exception as e:
            messagebox.showerror(tr("msg_error", "Error"), f"{tr('msg_error', 'Error')}: {e}")
    
    def log_app(self, message):
        """Log application message"""
        self.logger.info(message)
    
    @staticmethod
    def is_valid_youtube_url(url):
        """Validate YouTube URL"""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return re.match(youtube_regex, url) is not None
    
    def verify_live_stream(self):
        """Verify live stream availability and status"""
        tr = self.translator.get
        url = self.live_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            self.live_status_label.config(text=tr("live_status_error", "ERROR"), foreground=self.design.get_color("error"))
            return
        
        self.live_log.add_log(tr("live_check_stream", "Check Stream"))
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.live_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                self.live_status_label.config(text=tr("live_status_error", "ERROR"), foreground=self.design.get_color("error"))
                return
            
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    is_live = info.get('is_live', False)
                    
                    if is_live:
                        self.live_status_label.config(text=tr("live_status_live", "LIVE"), foreground=self.design.get_color("error"))
                        self.live_log.add_log(tr("live_recording_started", "Live stream recording started..."))
                    else:
                        self.live_status_label.config(text=tr("live_status_offline", "OFFLINE"), foreground=self.design.get_color("warning"))
                        self.live_log.add_log(tr("live_status_offline", "OFFLINE"))
                    
                    duration = info.get('duration')
                    if duration:
                        hours, remainder = divmod(duration, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        self.live_duration_label.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
                    
            except Exception as e:
                self.live_log.add_log(f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR")
                self.live_status_label.config(text=tr("live_status_error", "ERROR"), foreground=self.design.get_color("error"))
        
        thread = threading.Thread(target=verify_thread, daemon=True)
        thread.start()
    
    def start_live_recording(self):
        """Start recording live stream"""
        tr = self.translator.get
        url = self.live_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        if not YT_DLP_AVAILABLE:
            messagebox.showerror(tr("msg_error", "Error"), "yt-dlp")
            return
        
        self.is_downloading = True
        self.live_log.add_log(tr("live_recording_started", "Live stream recording started..."))
        
        def record_thread():
            try:
                mode = self.live_mode_var.get()
                quality = self.live_quality_var.get()
                
                # Map quality to format
                format_str = {
                    "best": "best",
                    "1080": "best[height<=1080]",
                    "720": "best[height<=720]",
                    "480": "best[height<=480]",
                }[quality]
                
                # Calculate duration based on mode
                if mode == "duration":
                    hours = int(self.live_hours_entry.get() or "0")
                    minutes = int(self.live_minutes_entry.get() or "0")
                    seconds = int(self.live_seconds_entry.get() or "0")
                    max_duration = hours * 3600 + minutes * 60 + seconds
                    if max_duration == 0:
                        max_duration = 3600  # Default 1 hour
                else:
                    max_duration = None
                
                base_opts = {
                    'format': format_str,
                    'outtmpl': str(self.output_dir / '%(title)s-%(id)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.live_progress_hook],
                }
                
                if max_duration:
                    base_opts['max_filesize'] = max_duration * 100000  # Approximate
                
                ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.live_log.add_log(tr("download_progress", "Downloading..."))
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": Path(filename).name,
                        "status": "success",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                    
                    self.live_log.add_log(tr("live_recording_completed", "Recording completed successfully!"))
                    self.refresh_history()
            
            except Exception as e:
                error_msg = str(e)
                # Check if error is due to browser being open
                if "Could not copy" in error_msg and "cookie database" in error_msg:
                    self.live_log.add_log(tr("browser_test_browser_open", "⚠️ Browser is open! Close it first."), "WARNING")
                else:
                    self.live_log.add_log(f"{tr('msg_error', 'Error')}: {error_msg}", "ERROR")
            
            finally:
                self.is_downloading = False
        
        thread = threading.Thread(target=record_thread, daemon=True)
        thread.start()
    
    def stop_live_recording(self):
        """Stop live stream recording"""
        tr = self.translator.get
        if self.is_downloading:
            self.is_downloading = False
            self.live_log.add_log(tr("live_recording_stopped", "Recording stopped by user"))
        else:
            messagebox.showinfo(tr("msg_info", "Information"), tr("status_ready", "Ready"))
    
    def live_progress_hook(self, d):
        """Progress hook for live recording"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '0 B/s')
            eta = d.get('_eta_str', 'Unknown')
            self.live_log.add_log(f"{percent} | Velocidade: {speed} | ETA: {eta}")
    
    def _on_mousewheel(self, event, canvas):
        """Handle mouse wheel scroll for canvas"""
        # Check if canvas exists and has scrollable content
        if not canvas or not hasattr(canvas, 'yview'):
            return
        
        # Determine scroll direction
        if event.num == 5 or event.delta < 0:  # Scroll down
            canvas.yview_scroll(3, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up
            canvas.yview_scroll(-3, "units")
    
    def enable_mousewheel_scroll(self, canvas, frame=None):
        """Enable mouse wheel scrolling for a canvas anywhere within its area
        
        Args:
            canvas: Canvas widget to enable scrolling for
            frame: Optional parent frame to also bind scroll events (recursively to all children)
        """
        # Store canvas reference for later use
        if not hasattr(self, '_scroll_canvases'):
            self._scroll_canvases = []
        self._scroll_canvases.append(canvas)
        
        # Track mouse entering/leaving canvas area for global scroll handling
        def on_canvas_enter(e):
            self.active_scroll_canvas = canvas
        
        def on_canvas_leave(e):
            # Only unset if this is still the active canvas
            if self.active_scroll_canvas is canvas:
                self.active_scroll_canvas = None
        
        # Bind to canvas
        canvas.bind("<Enter>", on_canvas_enter)
        canvas.bind("<Leave>", on_canvas_leave)
        
        # Use bind_all with a check to only scroll the active canvas
        # This captures events even when over child widgets
        def scroll_handler(event):
            # Only scroll if mouse is over this canvas
            if self.active_scroll_canvas is canvas:
                self._on_mousewheel(event, canvas)
                return "break"  # Prevent event propagation
        
        # Bind at application level but check if over our canvas
        canvas.bind_all("<MouseWheel>", scroll_handler, "+")
        canvas.bind_all("<Button-4>", scroll_handler, "+")
        canvas.bind_all("<Button-5>", scroll_handler, "+")

