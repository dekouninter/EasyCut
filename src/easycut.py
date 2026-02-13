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
    ModernDialog, ModernIconButton, ModernTabHeader
)
from font_loader import setup_fonts, LOADED_FONT_FAMILY

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
        
        # State
        self.logged_in = False
        self.current_email = ""
        self.is_downloading = False
        
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
        self.root.title(self.translator.get("app_title", "EasyCut"))
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # Set window icon
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "app_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            self.logger.warning(f"Could not set window icon: {e}")
        
        # Apply style
        self.apply_theme()
    
    def setup_ui(self):
        """Setup complete user interface"""
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with controls
        self.create_header(main_frame)
        
        # Login status banner (if not logged in)
        if not self.logged_in:
            self.create_login_banner(main_frame)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs (without Login tab)
        self.create_download_tab()
        self.create_batch_tab()
        self.create_live_tab()
        self.create_history_tab()
        self.create_about_tab()
        
        # Status bar
        tr = self.translator.get
        status_labels = {
            "status_ready": tr("status_ready", "Ready"),
            "login_not_logged": tr("status_not_logged_in", "Not logged in"),
            "login_logged_prefix": tr("status_logged_in", "Logged in as"),
            "version_label": f"v{tr('version', '1.0.0')}",
        }
        self.status_bar = StatusBar(main_frame, theme=self.theme, labels=status_labels)
        self.status_bar.pack(fill=tk.X)
        self.update_login_status()
        
        # Donation button
        donation_btn = DonationButton(self.root)
        donation_btn.create_floating_button(main_frame)
    
    def create_header(self, parent):
        """Create modern professional header with controls"""
        tr = self.translator.get
        
        # Main header container with elevated background
        header_container = ttk.Frame(parent)
        header_container.pack(fill=tk.X, padx=0, pady=0)
        
        header = ttk.Frame(header_container, padding=(Spacing.LG, Spacing.MD))
        header.pack(fill=tk.X)
        
        # Left side: Logo + App name
        left_frame = ttk.Frame(header)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # App icon and title
        app_title_frame = ttk.Frame(left_frame)
        app_title_frame.pack(side=tk.LEFT, padx=(0, Spacing.XL))
        
        # Try to load app icon
        app_icon = get_ui_icon("video", size=Icons.SIZE_LG)
        if app_icon:
            icon_label = ttk.Label(app_title_frame, image=app_icon)
            icon_label.image = app_icon
            icon_label.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Title with gradient effect (simulated with label)
        title_frame = ttk.Frame(app_title_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_lbl = ttk.Label(
            title_frame,
            text=tr("about_title", "EasyCut"),
            style="Title.TLabel"
        )
        title_lbl.pack(anchor="w")
        
        subtitle_lbl = ttk.Label(
            title_frame,
            text="YouTube Downloader Pro",
            style="Caption.TLabel"
        )
        subtitle_lbl.pack(anchor="w")
        
        # Separator
        ttk.Separator(left_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=Spacing.MD)
        
        # Theme toggle with modern button
        theme_icon_key = "theme_dark" if self.dark_mode else "theme_light"
        theme_btn = ModernButton(
            left_frame,
            text=tr("header_theme", "Theme"),
            icon_name=theme_icon_key,
            command=self.toggle_theme,
            variant="secondary",
            width=10
        )
        theme_btn.pack(side=tk.LEFT, padx=Spacing.XS)
        
        # Language selector with flag icon
        lang_frame = ttk.Frame(left_frame)
        lang_frame.pack(side=tk.LEFT, padx=Spacing.XS)
        
        lang_icon = get_ui_icon("language", size=Icons.SIZE_SM)
        if lang_icon:
            lang_icon_label = ttk.Label(lang_frame, image=lang_icon)
            lang_icon_label.image = lang_icon
            lang_icon_label.pack(side=tk.LEFT, padx=(Spacing.SM, Spacing.XS))
        
        lang_options = [
            ("pt", tr("lang_pt", "Português")),
            ("en", tr("lang_en", "English"))
        ]
        lang_codes = [code for code, _ in lang_options]
        lang_labels = [label for _, label in lang_options]
        
        lang_combo = ttk.Combobox(
            lang_frame,
            values=lang_labels,
            state="readonly",
            width=12
        )
        current_index = lang_codes.index(self.language) if self.language in lang_codes else 0
        lang_combo.set(lang_labels[current_index])
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self.change_language(lang_codes[lang_combo.current()]))
        lang_combo.pack(side=tk.LEFT)
        
        # Right side: Actions
        right_frame = ttk.Frame(header)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Open folder button
        folder_btn = ModernButton(
            right_frame,
            text=tr("header_open_folder", "Open Folder"),
            icon_name="folder",
            command=self.open_output_folder,
            variant="secondary",
            width=14
        )
        folder_btn.pack(side=tk.RIGHT, padx=Spacing.XS)
        
        # Login button (primary action)
        login_btn = ModernButton(
            right_frame,
            text=tr("header_login", "YouTube Login"),
            icon_name="login",
            command=self.open_login_popup,
            variant="primary",
            width=16
        )
        login_btn.pack(side=tk.RIGHT, padx=Spacing.XS)
        
        # Version badge
        version_label = ttk.Label(
            right_frame,
            text="v1.0.0",
            style="Caption.TLabel"
        )
        version_label.pack(side=tk.RIGHT, padx=Spacing.MD)
        
        # Bottom border for header
        ttk.Separator(header_container, orient=tk.HORIZONTAL).pack(fill=tk.X)
    
    def create_login_banner(self, parent):
        """Create modern login status banner (when not logged in)"""
        tr = self.translator.get
        
        # Create alert banner
        banner_frame = ttk.Frame(parent, padding=(Spacing.LG, Spacing.MD))
        banner_frame.pack(fill=tk.X)
        
        # Use ModernAlert for the banner
        alert = ModernAlert(
            banner_frame,
            message=f"{tr('login_banner_title', 'Not connected')} - {tr('login_banner_note', 'Login is only used by yt-dlp. Credentials are not stored.')}",
            variant="warning",
            dismissible=False
        )
        alert.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Login button on the right
        login_btn = ModernButton(
            banner_frame,
            text=tr("login_banner_button", "YouTube Login"),
            icon_name="login",
            command=self.open_login_popup,
            variant="primary",
            width=16
        )
        login_btn.pack(side=tk.RIGHT, padx=(Spacing.MD, 0))
    
    def create_login_tab(self):
        """Create login tab with popup-only interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔐 Login")
        
        container = ttk.Frame(frame, padding=40)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        ttk.Label(container, text="Authentication", font=("Arial", 16, "bold"), style="TLabel").pack(pady=10)
        ttk.Label(container, text=self.get_login_status(), font=("Arial", 11), style="TLabel").pack(pady=20)
        
        # Buttons
        ttk.Button(container, text="🔓 Login (Popup)", command=self.open_login_popup, width=20).pack(pady=5)
        ttk.Button(container, text="🚪 Logout", command=self.do_logout, width=20).pack(pady=5)
        
        # Info
        ttk.Label(
            container,
            text="Use popup login for secure authentication\nCredentials are stored securely using Windows Keyring",
            justify=tk.CENTER,
            wraplength=400
        ).pack(pady=20)
    
    def create_download_tab(self):
        """Create modern professional download tab"""
        tr = self.translator.get
        
        # Create tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"⬇️ {tr('tab_download', 'Download')}")
        
        # Main scrollable container
        main_canvas = tk.Canvas(frame, bg=self.design.get_color("bg_primary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=main_canvas.yview)
        main = ttk.Frame(main_canvas, padding=Spacing.LG)
        
        main.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=main, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("tab_download", "Download"),
            icon_name="download",
            subtitle=tr("download_subtitle", "Download videos and audio from YouTube")
        )
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("download_url", "YouTube URL"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_container = ttk.Frame(url_card)
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
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT)
        
        # === VIDEO INFO CARD ===
        info_card = ModernCard(main, title=tr("download_info", "Video Information"))
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_grid = ttk.Frame(info_card)
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
        mode_card = ModernCard(main, title=tr("download_mode", "Download Mode"))
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.download_mode_var = tk.StringVar(value="full")
        
        modes = [
            ("full", tr("download_mode_full", "Complete Video"), "video"),
            ("range", tr("download_mode_range", "Time Range"), "clock"),
            ("until", tr("download_mode_until", "Until Time"), "clock"),
            ("audio", tr("download_mode_audio", "Audio Only"), "music")
        ]
        
        for value, text, icon_name in modes:
            mode_frame = ttk.Frame(mode_card)
            mode_frame.pack(fill=tk.X, pady=Spacing.XS)
            
            icon = get_ui_icon(icon_name, size=Icons.SIZE_SM)
            if icon:
                icon_label = ttk.Label(mode_frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.download_mode_var,
                value=value
            ).pack(side=tk.LEFT)
        
        # === TIME RANGE CARD ===
        time_card = ModernCard(main, title=tr("download_time_range", "Time Range"))
        time_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        time_grid = ttk.Frame(time_card)
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
            time_card,
            text=tr("download_time_help", "Format: HH:MM:SS or MM:SS"),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(Spacing.SM, 0))
        
        # === QUALITY CARD ===
        quality_card = ModernCard(main, title=tr("download_quality", "Quality"))
        quality_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.download_quality_var = tk.StringVar(value="best")
        
        qualities = [
            ("best", tr("download_quality_best", "Best Quality"), "⭐"),
            ("mp4", tr("download_quality_mp4", "MP4 (Best)"), "🎬"),
            ("1080", "1080p Full HD", "📺"),
            ("720", "720p HD", "📱")
        ]
        
        quality_grid = ttk.Frame(quality_card)
        quality_grid.pack(fill=tk.X)
        
        for i, (value, text, emoji) in enumerate(qualities):
            ttk.Radiobutton(
                quality_grid,
                text=f"{emoji} {text}",
                variable=self.download_quality_var,
                value=value
            ).grid(row=i//2, column=i%2, sticky=tk.W, padx=Spacing.MD, pady=Spacing.XS)
        
        # === AUDIO FORMAT CARD ===
        audio_card = ModernCard(main, title=tr("audio_format", "Audio Format"))
        audio_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Format selection
        self.audio_format_var = tk.StringVar(value="mp3")
        
        fmt_frame = ttk.Frame(audio_card)
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
        ttk.Label(audio_card, text=f"🎵 {tr('audio_bitrate', 'Bitrate')}:", style="Subtitle.TLabel").pack(
            anchor=tk.W, pady=(Spacing.SM, Spacing.XS)
        )
        
        self.audio_bitrate_var = tk.StringVar(value="320")
        
        bitrate_frame = ttk.Frame(audio_card)
        bitrate_frame.pack(fill=tk.X)
        
        for br in ["128", "192", "256", "320"]:
            ttk.Radiobutton(
                bitrate_frame,
                text=f"{br} kbps",
                variable=self.audio_bitrate_var,
                value=br
            ).pack(side=tk.LEFT, padx=(0, Spacing.LG))
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("download_log", "Activity Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.download_log = LogWidget(log_container, theme=self.design, height=8)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.download_log.yview)
        self.download_log.config(yscrollcommand=log_scrollbar.set)
        self.download_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        ModernButton(
            action_frame,
            text=tr("download_btn", "Download"),
            icon_name="download",
            command=self.start_download,
            variant="primary",
            width=14
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_stop", "Stop"),
            icon_name="stop",
            command=self.stop_download,
            variant="secondary",
            width=14
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_clear_log", "Clear Log"),
            icon_name="clear",
            command=lambda: self.download_log.clear(),
            variant="outline",
            width=14
        ).pack(side=tk.LEFT)
    
    def create_batch_tab(self):
        """Create modern batch download tab"""
        tr = self.translator.get
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"☰ {tr('tab_batch', 'Batch')}")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
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
            text=tr("batch_help", "📝 Paste one URL per line. Up to 50 URLs supported."),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Text area
        text_container = ttk.Frame(urls_card)
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
        text_actions = ttk.Frame(urls_card)
        text_actions.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        ModernButton(
            text_actions,
            text=tr("batch_paste", "Paste from Clipboard"),
            icon_name="paste",
            command=self.batch_paste,
            variant="secondary",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            text_actions,
            text=tr("batch_clear", "Clear All"),
            icon_name="clear",
            command=lambda: self.batch_text.delete(1.0, tk.END),
            variant="outline",
            width=12
        ).pack(side=tk.LEFT)
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("batch_log", "Batch Progress Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.batch_log = LogWidget(log_container, theme=self.design, height=6)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.batch_log.yview)
        self.batch_log.config(yscrollcommand=log_scrollbar.set)
        self.batch_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("batch_download_all", "Start Batch Download"),
            icon_name="download",
            command=self.start_batch_download,
            variant="primary",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("batch_stop", "Stop All"),
            icon_name="stop",
            command=self.stop_download,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT)
    
    def create_live_tab(self):
        """Create modern live stream recording tab"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"● {tr('tab_live', 'Live')}")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("live_title", "Live Stream Recorder"),
            icon_name="record",
            subtitle=tr("live_subtitle", "🔴 Record live streams with customizable duration and quality")
        )
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("live_url", "Live Stream URL"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_row = ttk.Frame(url_card)
        url_row.pack(fill=tk.X)
        
        url_icon_label = ttk.Label(url_row, text="📡", font=("Segoe UI", 12), style="TLabel")
        url_icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.live_url_entry = ttk.Entry(url_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self.live_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        ModernButton(
            url_row,
            text=tr("live_check_stream", "Check"),
            icon_name="verify",
            command=self.verify_live_stream,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT)
        
        # === STREAM STATUS CARD ===
        status_card = ModernCard(main, title=tr("live_status", "Stream Status"))
        status_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        status_grid = ttk.Frame(status_card)
        status_grid.pack(fill=tk.X)
        
        ttk.Label(status_grid, text=f"{tr('live_status', 'Status')}:", style="Subtitle.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, Spacing.XL))
        self.live_status_label = ttk.Label(status_grid, text=tr("live_status_unknown", "⚠️ UNKNOWN"), style="Caption.TLabel")
        self.live_status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_grid, text=f"{tr('live_duration', 'Duration')}:", style="Subtitle.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, Spacing.XL), pady=(Spacing.SM, 0))
        self.live_duration_label = ttk.Label(status_grid, text="--:--:--", style="Caption.TLabel")
        self.live_duration_label.grid(row=1, column=1, sticky=tk.W, pady=(Spacing.SM, 0))
        
        # === RECORDING MODE CARD ===
        mode_card = ModernCard(main, title=tr("live_mode", "Recording Mode"))
        mode_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.live_mode_var = tk.StringVar(value="continuous")
        
        mode_options = [
            ("continuous", tr("live_mode_continuous", "Continuous Recording"), "∞"),
            ("duration", tr("live_mode_duration", "Record Duration"), "⏱️"),
            ("until", tr("live_mode_until", "Record Until Time"), "⏰")
        ]
        
        for value, label, icon in mode_options:
            mode_frame = ttk.Frame(mode_card)
            mode_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(mode_frame, text=icon, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, Spacing.SM))
            ttk.Radiobutton(mode_frame, text=label, variable=self.live_mode_var, value=value).pack(side=tk.LEFT, anchor=tk.W)
        
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
        
        self.live_quality_var = tk.StringVar(value="best")
        
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
            ttk.Radiobutton(quality_frame, text=label, variable=self.live_quality_var, value=value).pack(side=tk.LEFT)
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("live_log", "Recording Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.live_log = LogWidget(log_container, theme=self.design, height=6)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.live_log.yview)
        self.live_log.config(yscrollcommand=log_scrollbar.set)
        self.live_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("live_start_recording", "Start Recording"),
            icon_name="record",
            command=self.start_live_recording,
            variant="primary",
            width=18
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("live_stop_recording", "Stop"),
            icon_name="stop",
            command=self.stop_live_recording,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_clear_log", "Clear Log"),
            icon_name="clear",
            command=lambda: self.live_log.clear(),
            variant="outline",
            width=12
        ).pack(side=tk.LEFT)
    
    def create_audio_tab(self):
        """Create modern audio conversion tab"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"🎵 {tr('tab_audio', 'Audio')}")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("audio_title", "Audio Converter"),
            icon_name="music",
            subtitle=tr("audio_subtitle", "🎧 Extract and convert audio from YouTube videos")
        )
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("audio_url", "YouTube URL"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        url_row = ttk.Frame(url_card)
        url_row.pack(fill=tk.X)
        
        url_icon_label = ttk.Label(url_row, text="🎵", font=("Segoe UI", 12), style="TLabel")
        url_icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.audio_url_entry = ttk.Entry(url_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self.audio_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === FORMAT CARD ===
        format_card = ModernCard(main, title=tr("audio_format", "Audio Format"))
        format_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.audio_format_var = tk.StringVar(value="mp3")
        
        format_options = [("MP3", "mp3", "🎵"), ("WAV", "wav", "🎼"), ("M4A", "m4a", "🎶"), ("OPUS", "opus", "🎸")]
        
        format_grid = ttk.Frame(format_card)
        format_grid.pack(fill=tk.X)
        
        for i, (label, value, icon) in enumerate(format_options):
            format_frame = ttk.Frame(format_grid)
            format_frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0 if i%2==0 else Spacing.XL, 0), pady=(0, Spacing.XS))
            ttk.Label(format_frame, text=icon, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, Spacing.SM))
            ttk.Radiobutton(format_frame, text=label, variable=self.audio_format_var, value=value).pack(side=tk.LEFT)
        
        # === BITRATE CARD ===
        bitrate_card = ModernCard(main, title=tr("audio_bitrate", "Audio Quality (Bitrate)"))
        bitrate_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.audio_bitrate_var = tk.StringVar(value="320")
        
        bitrate_options = [("128", "📻 Standard"), ("192", "🎧 Good"), ("256", "⭐ High"), ("320", "💎 Best")]
        
        bitrate_grid = ttk.Frame(bitrate_card)
        bitrate_grid.pack(fill=tk.X)
        
        for i, (value, label) in enumerate(bitrate_options):
            bitrate_frame = ttk.Frame(bitrate_grid)
            bitrate_frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=(0 if i%2==0 else Spacing.XL, 0), pady=(0, Spacing.XS))
            ttk.Radiobutton(bitrate_frame, text=f"{label} ({value} kbps)", variable=self.audio_bitrate_var, value=value).pack(side=tk.LEFT)
        
        # === LOG CARD ===
        log_card = ModernCard(main, title=tr("audio_log", "Conversion Log"))
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        log_container = ttk.Frame(log_card)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.audio_log = LogWidget(log_container, theme=self.design, height=8)
        log_scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=self.audio_log.yview)
        self.audio_log.config(yscrollcommand=log_scrollbar.set)
        self.audio_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X)
        
        ModernButton(
            action_frame,
            text=tr("audio_convert", "Convert & Download"),
            icon_name="music",
            command=self.start_audio_conversion,
            variant="primary",
            width=20
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("download_clear_log", "Clear Log"),
            icon_name="clear",
            command=lambda: self.audio_log.clear(),
            variant="outline",
            width=12
        ).pack(side=tk.LEFT)
    
    def create_history_tab(self):
        """Create modern download history tab"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"📅 {tr('tab_history', 'History')}")
        
        main = ttk.Frame(frame, padding=Spacing.LG)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === TAB HEADER ===
        ModernTabHeader(
            main,
            title=tr("history_title", "Download History"),
            icon_name="history",
            subtitle=tr("history_subtitle", "📋 Track all your downloads in one place")
        )
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk. X, pady=(0, Spacing.MD))
        
        ModernButton(
            action_frame,
            text=tr("history_update", "Refresh"),
            icon_name="refresh",
            command=self.refresh_history,
            variant="secondary",
            width=12
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ModernButton(
            action_frame,
            text=tr("history_clear", "Clear History"),
            icon_name="delete",
            command=self.clear_history,
            variant="outline",
            width=14
        ).pack(side=tk.LEFT)
        
        # === HISTORY TABLE CARD ===
        table_card = ModernCard(main, title=tr("history_records", "Download Records"))
        table_card.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = ttk.Frame(table_card)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Date", "Filename", "Status")
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            height=20,
            show="tree headings"
        )
        
        col_labels = {
            "Date": tr("history_date", "Date"),
            "Filename": tr("history_filename", "Filename"),
            "Status": tr("history_status", "Status"),
        }
        
        for col in columns:
            self.history_tree.heading(col, text=col_labels.get(col, col))
            self.history_tree.column(col, width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.config(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_history()
    
    def create_about_tab(self):
        """Create modern professional about tab"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"ℹ️ {tr('tab_about', 'About')}")
        
        # Scrollable container
        canvas = tk.Canvas(frame, bg=self.design.get_color("bg_primary"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Content
        main = ttk.Frame(scrollable_frame, padding=Spacing.XXL)
        main.pack(fill=tk.BOTH, expand=True)
        
        # === APP TITLE ===
        ttk.Label(
            main,
            text=tr("about_title", "EasyCut"),
            font=(LOADED_FONT_FAMILY, Typography.SIZE_XXL, "bold")
        ).pack(pady=(0, Spacing.XS))
        
        ttk.Label(
            main,
            text=tr("about_subtitle", "🎬 Professional YouTube Downloader & Audio Converter"),
            style="Caption.TLabel"
        ).pack(pady=(0, Spacing.LG))
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=Spacing.MD)
        
        # === APP INFO CARD ===
        info_card = ModernCard(main, title=tr("about_section_info", "📦 Application Info"))
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_data = [
            ("Version", "1.0.0"),
            ("Author", "Deko Costa"),
            ("License", "GPL-3.0"),
            ("Release", "2026")
        ]
        
        for label, value in info_data:
            row = ttk.Frame(info_card)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === SOCIAL LINKS CARD ===
        social_card = ModernCard(main, title=tr("about_section_links", "💚 Connect & Support"))
        social_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        def open_link(url):
            import webbrowser
            webbrowser.open(url)
        
        links = [
            ("� " + tr("about_link_github", "GitHub Repository"), "https://github.com/dekouninter/EasyCut"),
            ("☕ " + tr("about_link_coffee", "Buy Me a Coffee"), "https://buymeacoffee.com/dekocosta"),
            ("💖 " + tr("about_link_kofi", "Support on Ko-fi"), "https://ko-fi.com/dekocosta"),
            ("💸 " + tr("about_link_livepix", "Livepix (Brazil)"), "https://livepix.gg/dekocosta"),
        ]
        
        for label, url in links:
            ModernButton(
                social_card,
                text=label,
                command=lambda u=url: open_link(u),
                variant="outline",
                width=30
            ).pack(pady=(0, Spacing.SM), fill=tk.X)
        
        # === FEATURES CARD ===
        features_card = ModernCard(main, title=tr("about_section_features", "✨ Features"))
        features_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        features = [
            "✅ Download videos in multiple qualities (4K to 144p)",
            "✅ Extract audio in MP3, WAV, M4A, OPUS formats",
            "✅ Batch download multiple videos simultaneously",
            "✅ Record live streams with customizable duration",
            "✅ Time range selection for video trimming",
            "✅ Dark and Light theme support",
            "✅ Multi-language support (EN, PT, ES)",
            "✅ Professional icon set (Feather Icons)",
            "✅ Download history tracking"
        ]
        
        for feature in features:
            ttk.Label(
                features_card,
                text=feature,
                style="Caption.TLabel"
            ).pack(anchor=tk.W, pady=(0, Spacing.XS))
        
        # === TECHNOLOGIES CARD ===
        tech_card = ModernCard(main, title=tr("about_section_tech", "🛠️ Technologies & Credits"))
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
            row = ttk.Frame(tech_card)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === THANKS CARD ===
        thanks_card = ModernCard(main, title=tr("about_section_thanks", "🙏 Special Thanks"))
        thanks_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        thanks_text = tr(
            "about_thanks_text",
            "Thanks to the open-source community, yt-dlp developers, FFmpeg team, and all contributors who make projects like this possible. See CREDITS.md for full attributions."
        )
        ttk.Label(
            thanks_card,
            text=thanks_text,
            style="Caption.TLabel",
            wraplength=600,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # === FOOTER ===
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=Spacing.LG)
        
        ttk.Label(
            main,
            text=tr("about_footer", "💜 Made with Python | GPL-3.0 License | © 2026 Deko Costa"),
            style="Caption.TLabel"
        ).pack(pady=Spacing.MD)
    
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
    
    def start_audio_conversion(self):
        """Start audio conversion"""
        tr = self.translator.get
        url = self.audio_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        fmt = self.audio_format_var.get()
        bitrate = self.audio_bitrate_var.get()
        
        self.audio_log.add_log(f"{tr('audio_convert', 'Convert')}: {fmt.upper()} ({bitrate}kbps)")
        
        def audio_thread():
            if not YT_DLP_AVAILABLE:
                self.audio_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                return
            
            try:
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': fmt,
                        'preferredquality': bitrate,
                    }],
                    'quiet': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": f"{info.get('title', 'unknown')}.{fmt}",
                        "status": "success",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                    
                    self.audio_log.add_log(tr("audio_success", "Audio conversion completed!"))
                    self.refresh_history()
            
            except Exception as e:
                self.audio_log.add_log(f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=audio_thread, daemon=True)
        thread.start()
    
    def refresh_history(self):
        """Refresh download history"""
        tr = self.translator.get
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.config_manager.load_history()
        
        if not history:
            self.history_tree.insert("", tk.END, values=(tr("history_empty", "No downloads yet"), "-", "-"))
            return
        
        for item in reversed(history):
            date_obj = datetime.fromisoformat(item.get("date", ""))
            date_str = date_obj.strftime("%Y-%m-%d %H:%M")
            filename = item.get("filename", "unknown")
            status = item.get("status", "unknown")
            
            self.history_tree.insert("", tk.END, values=(date_str, filename[:40], status))
    
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
            self.live_status_label.config(text=tr("live_status_error", "ERROR"), foreground="#FF0000")
            return
        
        self.live_log.add_log(tr("live_check_stream", "Check Stream"))
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.live_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                self.live_status_label.config(text=tr("live_status_error", "ERROR"), foreground="#FF0000")
                return
            
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    is_live = info.get('is_live', False)
                    
                    if is_live:
                        self.live_status_label.config(text=tr("live_status_live", "LIVE"), foreground="#FF0000")
                        self.live_log.add_log(tr("live_recording_started", "Live stream recording started..."))
                    else:
                        self.live_status_label.config(text=tr("live_status_offline", "OFFLINE"), foreground="#FF9800")
                        self.live_log.add_log(tr("live_status_offline", "OFFLINE"))
                    
                    duration = info.get('duration')
                    if duration:
                        hours, remainder = divmod(duration, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        self.live_duration_label.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
                    
            except Exception as e:
                self.live_log.add_log(f"{tr('msg_error', 'Error')}: {str(e)}", "ERROR")
                self.live_status_label.config(text=tr("live_status_error", "ERROR"), foreground="#FF0000")
        
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


def main():
    """Main function"""
    root = tk.Tk()
    app = EasyCutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
