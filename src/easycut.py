# -*- coding: utf-8 -*-
"""
EasyCut - YouTube Video Downloader and Audio Converter
Professional Desktop Application using Tkinter

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.0.0
License: MIT

Features:
- Download YouTube videos with multiple quality options
- Batch downloads
- Audio conversion (MP3, WAV, M4A, OPUS)
- Real-time logging
- Secure credential storage
- Dark/Light theme with instant reload
- Multi-language support (EN, PT)
- Professional UI design
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import re
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Import local modules
sys.path.insert(0, os.path.dirname(__file__))
from i18n import translator as t, Translator
from ui_enhanced import ConfigManager, LogWidget, StatusBar, LoginPopup
from donation_system import DonationButton
from icon_manager import icon_manager, get_ui_icon
from design_system import ModernTheme, DesignTokens, Typography, Spacing, Icons
from modern_components import (
    ModernButton, ModernCard, ModernInput, ModernAlert,
    ModernDialog, ModernIconButton, ToastManager
)
from font_loader import setup_fonts, LOADED_FONT_FAMILY

# Import UI Screens (new modular architecture)
from ui.screens import (
    LoginScreen, DownloadScreen, BatchScreen, LiveScreen,
    HistoryScreen, AboutScreen
)

# Import external libraries
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class EasyCutApp:
    """Professional YouTube Downloader Application"""
    
    def __init__(self, root):
        self.root = root
        
        # Configuration
        self.config_manager = ConfigManager()
        self.load_config()
        
        # Load custom fonts FIRST
        self.font_family = setup_fonts()
        
        # Modern Theme & Design System
        self.theme = ModernTheme(dark_mode=self.dark_mode, font_family=self.font_family)
        self.design = DesignTokens(dark_mode=self.dark_mode)
        self.translator = Translator(self.language)
        
        # Icon Manager
        self.icon_manager = icon_manager
        self.icons = {}  # Cache for loaded icons
        
        # UI Components (will be created)
        self.ui_components = {}
        
        # Screen instances (will be created in setup_ui)
        self.screens = {}  # {screen_name: screen_instance}
        
        # State
        self.logged_in = False
        self.current_email = ""
        self.is_downloading = False
        self.active_scroll_canvas = None  # Track active canvas for mouse wheel scroll
        
        # Paths
        self.output_dir = Path(self.config_manager.get("output_folder", "downloads"))
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
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("EasyCut")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
    
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
        
        # --- LOGIN BANNER ---
        if not self.logged_in:
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
        
        # Toast notification manager (top-right of content area)
        self.toast = ToastManager(self.content_area, dark_mode=self.dark_mode)
        
        # Create a notebook (hidden tabs) for content switching
        self.notebook = ttk.Notebook(self.content_area)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        # Hide the notebook tab bar
        style = ttk.Style()
        style.layout("TNotebook", [])  # Remove tab bar layout
        
        # Create sections as notebook pages
        self.create_download_tab()
        self.create_batch_tab()
        self.create_live_tab()
        self.create_history_tab()
        self.create_about_tab()
        
        # Map section names to tab indices
        self._section_map = {
            "download": 0,
            "batch": 1,
            "live": 2,
            "history": 3,
            "about": 4,
        }
        
        # Select initial section
        self._switch_section("download")
        
        # --- LOG PANEL (collapsible) ---
        self._build_log_panel(root_frame)
        
        # --- STATUS BAR ---
        tr = self.translator.get
        status_labels = {
            "status_ready": tr("status_ready", "Ready"),
            "login_not_logged": tr("status_not_logged_in", "Not logged in"),
            "login_logged_prefix": tr("status_logged_in", "Logged in as"),
            "version_label": f"v{tr('version', '1.0.0')}",
        }
        self.status_bar = StatusBar(root_frame, theme=self.theme, labels=status_labels)
        self.status_bar.pack(fill=tk.X)
        self.update_login_status()
        
        # --- DONATION BUTTON ---
        donation_btn = DonationButton(self.root)
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
            
            # Active indicator (left accent bar)
            indicator = tk.Frame(btn_frame, bg=bg, width=3)
            indicator.pack(side=tk.LEFT, fill=tk.Y)
            
            # Icon
            icon_lbl = tk.Label(
                btn_frame, text=icon, bg=bg, fg=fg,
                font=(Typography.FONT_FAMILY, 14),
                padx=Spacing.MD, pady=Spacing.SM
            )
            icon_lbl.pack(side=tk.LEFT)
            
            # Label
            text_lbl = tk.Label(
                btn_frame, text=label, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                anchor="w"
            )
            text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
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
        
        # Version
        tk.Label(
            footer, text="v1.0.0", bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_TINY)
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Folder buttons
        ModernButton(
            footer, text=tr("header_open_folder", "Open Folder"),
            icon_name="folder", command=self.open_output_folder,
            variant="outline", width=18
        ).pack(fill=tk.X, pady=(0, Spacing.XS))
        
        ModernButton(
            footer, text=tr("header_select_folder", "Select Folder"),
            icon_name="folder-plus", command=self.select_output_folder,
            variant="outline", width=18
        ).pack(fill=tk.X)
    
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
        
        # Switch notebook tab
        idx = self._section_map.get(key, 0)
        self.notebook.select(idx)
    
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
                refs["text"].pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            self.sidebar_frame.config(width=50)
            for refs in self.nav_buttons.values():
                refs["text"].pack_forget()
    
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
        
        # Theme toggle
        theme_icon_key = "theme_dark" if self.dark_mode else "theme_light"
        ModernButton(
            right, text=tr("header_theme", "Theme"),
            icon_name=theme_icon_key,
            command=self.toggle_theme,
            variant="outline", width=8
        ).pack(side=tk.LEFT, padx=Spacing.XS)
        
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
        
        # Login status / button
        if not self.logged_in:
            ModernButton(
                right, text=tr("header_login", "Login"),
                icon_name="login",
                command=self.open_login_popup,
                variant="outline", width=8
            ).pack(side=tk.LEFT, padx=Spacing.XS)
        
        # Bottom border
        tk.Frame(parent, bg=self.design.get_color("border"), height=1).pack(fill=tk.X)
    
    def create_login_banner(self, parent):
        """Create slim login status banner (when not logged in)"""
        tr = self.translator.get
        bg = self.design.get_color("bg_secondary")
        fg_sec = self.design.get_color("fg_secondary")
        accent = self.design.get_color("accent_primary")
        
        banner = tk.Frame(parent, bg=bg, height=32)
        banner.pack(fill=tk.X)
        banner.pack_propagate(False)
        
        inner = tk.Frame(banner, bg=bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG)
        
        # Info icon + message
        tk.Label(
            inner, text="ℹ️", bg=bg, font=("Segoe UI Emoji", 10)
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        tk.Label(
            inner,
            text=f"{tr('login_banner_title', 'Not connected')} — {tr('login_banner_note', 'Login is only used by yt-dlp')}",
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Login button (small outline)
        ModernButton(
            inner,
            text=tr("login_banner_button", "Login"),
            icon_name="login",
            command=self.open_login_popup,
            variant="outline",
            size="sm",
            width=8
        ).pack(side=tk.RIGHT, pady=2)
        
        # Bottom border
        tk.Frame(parent, bg=self.design.get_color("border"), height=1).pack(fill=tk.X)
    
    def create_download_tab(self):
        """Create download section"""
        tr = self.translator.get
        
        # Create tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Download")
        
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
        
        # Enable mouse wheel scroll for download tab
        self.enable_mousewheel_scroll(main_canvas, main)
        
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
        
        # === VIDEO INFO CARD ===
        info_card = ModernCard(main, title=tr("download_info", "Video Information"), dark_mode=self.dark_mode)
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_grid = ttk.Frame(info_card.body)
        info_grid.pack(fill=tk.X)
        
        # Title row
        ttk.Label(info_grid, text=f"{tr('download_title', 'Title')}:", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_title_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.download_title_label.grid(row=0, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # Duration row
        ttk.Label(info_grid, text=f"{tr('download_duration', 'Duration')}:", style="Subtitle.TLabel").grid(
            row=1, column=0, sticky=tk.W, padx=(0, Spacing.MD), pady=Spacing.XS
        )
        self.download_duration_label = ttk.Label(info_grid, text="-", style="Caption.TLabel")
        self.download_duration_label.grid(row=1, column=1, sticky=tk.W, pady=Spacing.XS)
        
        # === DOWNLOAD MODE CARD ===
        mode_card = ModernCard(main, title=tr("download_mode", "Download Mode"), dark_mode=self.dark_mode)
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.download_mode_var = tk.StringVar(value="full")
        
        modes = [
            ("full", tr("download_mode_full", "Complete Video")),
            ("range", tr("download_mode_range", "Time Range")),
            ("until", tr("download_mode_until", "Until Time")),
            ("audio", tr("download_mode_audio", "Audio Only"))
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
    
    def create_batch_tab(self):
        """Create batch download section"""
        tr = self.translator.get
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Batch")
        
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
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            text_actions,
            text=tr("batch_clear", "Clear All"),
            icon_name="clear",
            command=lambda: self.batch_text.delete(1.0, tk.END),
            variant="ghost",
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
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("batch_stop", "Stop All"),
            icon_name="stop",
            command=self.stop_download,
            variant="danger",
            width=12
        ).pack(side=tk.LEFT)
    
    def create_live_tab(self):
        """Create live stream recording section"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Live")
        
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
            width=12
        ).pack(side=tk.LEFT)
    
    def create_history_tab(self):
        """Create download history section"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="History")
        
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
    
    def create_about_tab(self):
        """Create about section"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="About")
        
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
        
        # === APP INFO CARD ===
        info_card = ModernCard(main, title=tr("about_section_info", "Application Info"), dark_mode=self.dark_mode)
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_data = [
            ("Version", "1.0.0"),
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
        
        # === FEATURES CARD ===
        features_card = ModernCard(main, title=tr("about_section_features", "Features"), dark_mode=self.dark_mode)
        features_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        features = [
            "Download videos in multiple qualities (4K to 144p)",
            "Extract audio in MP3, WAV, M4A, OPUS formats",
            "Batch download multiple videos simultaneously",
            "Record live streams with customizable duration",
            "Time range selection for video trimming",
            "Dark and Light theme support",
            "Multi-language support (EN, PT, ES)",
            "Professional icon set (Feather Icons)",
            "Download history tracking"
        ]
        
        for feature in features:
            ttk.Label(
                features_card.body,
                text=feature,
                style="Caption.TLabel"
            ).pack(anchor=tk.W, pady=(0, Spacing.XS))
        
        # === TECHNOLOGIES CARD ===
        tech_card = ModernCard(main, title=tr("about_section_tech", "Technologies & Credits"), dark_mode=self.dark_mode)
        tech_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        tech_data = [
            ("Core", "Python 3.13 + Tkinter"),
            ("Downloader", "yt-dlp (Unlicense)"),
            ("Converter", "FFmpeg (GPL-2.0+)"),
            ("Security", "keyring (MIT)"),
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
            "Thanks to the open-source community, yt-dlp developers, FFmpeg team, and all contributors who make projects like this possible. See CREDITS.md for full attributions."
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
    
    def create_screens_new_architecture(self):
        """Create screens using new modular architecture
        
        This method instantiates all screen classes, which represent tabs
        in the Notebook. Each screen handles its own UI layout and delegates
        business logic back to this app instance.
        
        NOTE: LoginScreen is not included here as login is currently handled
        via popup and banner in the header. Can be added to notebook if needed.
        """
        # Prepare kwargs for screen initialization
        screen_kwargs = {
            "translator": self.translator,
            "design": self.design,
            "app": self  # Reference back to main app for business logic calls
        }
        
        # Create all screens with the notebook and theme
        # These replace the monolithic create_*_tab() methods
        self.screens = {
            "download": DownloadScreen(self.notebook, self.design, **screen_kwargs),
            "batch": BatchScreen(self.notebook, self.design, **screen_kwargs),
            "live": LiveScreen(self.notebook, self.design, **screen_kwargs),
            "history": HistoryScreen(self.notebook, self.design, **screen_kwargs),
            "about": AboutScreen(self.notebook, self.design, **screen_kwargs)
        }
        
        # Build each screen (creates UI and binds events)
        for screen_name, screen in self.screens.items():
            screen.build()
            logging.info(f"✓ {screen.__class__.__name__} built")
        
        logging.info(f"✓ All 5 screens created using new modular architecture")
    
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
        self.apply_theme()
        self.setup_ui()
        self.log_app("✓ Theme changed instantly")
    
    def change_language(self, lang):
        """Change language with instant reload"""
        if self.translator.set_language(lang):
            self.config_manager.set("language", lang)
            self.setup_ui()
            self.log_app(f"✓ Language changed to {lang.upper()}")
    
    def open_login_popup(self):
        """Open login popup"""
        tr = self.translator.get
        def handle_login(creds):
            email = creds["email"]
            password = creds["password"]
            remember = creds["remember"]
            
            self.logged_in = True
            self.current_email = email
            
            if remember and KEYRING_AVAILABLE:
                try:
                    keyring.set_password("easycut", "user_email", email)
                    keyring.set_password("easycut", "password", password)
                except Exception as e:
                    self.logger.warning(f"Could not save credentials: {e}")
            
            self.update_login_status()
            self.log_app(f"✓ Logged in as {email}")
        
        labels = {
            "email_label": tr("login_email", "Email/Username") + " (YouTube):",
            "password_label": tr("login_password", "Password") + ":",
            "notice": tr("login_banner_note", "Login is only used by yt-dlp."),
            "button_ok": tr("login_btn", "Login"),
            "button_cancel": tr("msg_cancel", "Cancel"),
            "warning_title": tr("msg_warning", "Warning"),
            "warning_message": tr("login_validation_error", "Please fill all fields."),
        }
        popup = LoginPopup(self.root, title=tr("header_login", "YouTube Login"), callback=handle_login, labels=labels)
        popup.show()
    
    def do_logout(self):
        """Logout user"""
        tr = self.translator.get
        if messagebox.askyesno(tr("msg_confirm", "Confirm"), tr("login_logout", "Logout") + "?"):
            self.logged_in = False
            self.current_email = ""
            
            if KEYRING_AVAILABLE:
                try:
                    keyring.delete_password("easycut", "user_email")
                    keyring.delete_password("easycut", "password")
                except Exception:
                    pass
            
            self.update_login_status()
            self.log_app("✓ Logged out")
    
    def check_saved_credentials(self):
        """Check for saved credentials"""
        if not KEYRING_AVAILABLE:
            return
        
        try:
            email = keyring.get_password("easycut", "user_email")
            password = keyring.get_password("easycut", "password")
            if email and password:
                self.logged_in = True
                self.current_email = email
                self.update_login_status()
        except Exception as e:
            self.logger.warning(f"Could not retrieve credentials: {e}")
    
    def update_login_status(self):
        """Update login status display"""
        if self.status_bar:
            if self.logged_in:
                self.status_bar.set_login_status(True, self.current_email)
            else:
                self.status_bar.set_login_status(False)
    
    def get_login_status(self):
        """Get login status text"""
        tr = self.translator.get
        if self.logged_in:
            return f"{tr('status_logged_in', 'Logged in as')}: {self.current_email}"
        return tr("status_not_logged_in", "Not logged in")
    
    def verify_video(self):
        """Verify video URL"""
        tr = self.translator.get
        url = self.download_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        self.download_log.add_log(tr("log_verifying_url", "Verifying URL..."))
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.download_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                return
            
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    
                    self.download_title_label.config(text=title[:50])
                    mins, secs = divmod(duration, 60)
                    self.download_duration_label.config(text=f"{int(mins)}:{int(secs):02d}")
                    
                    self.download_log.add_log(tr("log_video_info", "Video info retrieved successfully"))
            except Exception as e:
                self.download_log.add_log(f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=verify_thread, daemon=True)
        thread.start()
    
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
        
        self.is_downloading = True
        self.download_log.add_log(f"{tr('log_downloading', 'Downloading video from')} {url}")
        
        quality = self.download_quality_var.get()
        
        def download_thread():
            if not YT_DLP_AVAILABLE:
                self.download_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                self.is_downloading = False
                return
            
            try:
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
                format_str = {
                    'best': 'bestvideo+bestaudio/best',
                    'mp4': 'best[ext=mp4]/best',
                    'audio': 'bestaudio/best'
                }.get(quality, 'best')
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': output_template,
                    'quiet': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": info.get('title', 'unknown'),
                        "status": "success",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                    
                    self.download_log.add_log(tr("download_success", "Download completed successfully!"))
                    self.refresh_history()
            
            except Exception as e:
                self.download_log.add_log(f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR")
            
            finally:
                self.is_downloading = False
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def stop_download(self):
        """Stop current download"""
        tr = self.translator.get
        self.is_downloading = False
        self.download_log.add_log(tr("download_stop", "Stop"))
    
    def start_batch_download(self):
        """Start batch download"""
        tr = self.translator.get
        urls_text = self.batch_text.get(1.0, tk.END).strip()
        
        if not urls_text:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("batch_empty", "Add at least one URL"))
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        self.batch_log.add_log(f"{tr('batch_progress', 'Downloading batch')} ({len(urls)})")
        
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
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_template,
                        'quiet': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        success += 1
                        self.batch_log.add_log(f"[{i}/{len(urls)}] {info.get('title', 'Video')[:30]}")
                
                except Exception as e:
                    self.batch_log.add_log(f"[{i}/{len(urls)}] ✗ Error: {str(e)[:50]}", "ERROR")
            
            self.batch_log.add_log(f"Batch complete: {success}/{len(urls)} successful")
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
        
        if not history:
            empty_label = ttk.Label(
                self.history_records_frame,
                text=tr("history_empty", "No downloads yet"),
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
            from tkinter import filedialog
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
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': str(self.output_dir / '%(title)s-%(id)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.live_progress_hook],
                }
                
                if max_duration:
                    ydl_opts['max_filesize'] = max_duration * 100000  # Approximate
                
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
                self.live_log.add_log(f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR")
            
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
            frame: Optional parent frame to also bind scroll events
        """
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
        
        # Bind scroll events to canvas (Linux uses Button-4 and Button-5)
        canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
        
        # Bind scroll events for Windows and macOS
        canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
        
        # Also bind to parent frame if provided - enables scroll when over widgets in frame
        if frame:
            frame.bind("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
            frame.bind("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
            frame.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))


def main():
    """Main function"""
    root = tk.Tk()
    app = EasyCutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
