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
from ui_enhanced import Theme, ConfigManager, LogWidget, StatusBar, LoginPopup
from donation_system import DonationButton
from icon_manager import icon_manager, get_ui_icon

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
        
        # Theme & Language
        self.theme = Theme(dark_mode=self.dark_mode)
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
        """Create professional header with controls"""
        tr = self.translator.get
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        # Logo/Title
        title_lbl = ttk.Label(header, text=tr("about_title", "EasyCut"), font=("Segoe UI", 16, "bold"))
        title_lbl.pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(header, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Theme toggle with icon
        theme_icon_key = "theme_dark" if self.dark_mode else "theme_light"
        theme_icon = get_ui_icon(theme_icon_key, size=16)
        theme_btn = ttk.Button(header, text=" " + tr("header_theme", "Theme"), command=self.toggle_theme, width=10)
        if theme_icon:
            theme_btn.configure(image=theme_icon, compound="left")
            theme_btn.image = theme_icon
        theme_btn.pack(side=tk.LEFT, padx=2)
        
        # Language selector
        lang_options = [
            ("pt", tr("lang_pt", "Portugues")),
            ("en", tr("lang_en", "English"))
        ]
        lang_codes = [code for code, _ in lang_options]
        lang_labels = [label for _, label in lang_options]
        lang_combo = ttk.Combobox(header, values=lang_labels, state="readonly", width=12)
        current_index = lang_codes.index(self.language) if self.language in lang_codes else 0
        lang_combo.set(lang_labels[current_index])
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self.change_language(lang_codes[lang_combo.current()]))
        lang_combo.pack(side=tk.LEFT, padx=2)
        
        # Login button with icon
        login_icon = get_ui_icon("login", size=16)
        login_btn = ttk.Button(header, text=" " + tr("header_login", "YouTube Login"), command=self.open_login_popup, width=16)
        if login_icon:
            login_btn.configure(image=login_icon, compound="left")
            login_btn.image = login_icon
        login_btn.pack(side=tk.LEFT, padx=2)
        
        # Open folder button with icon
        folder_icon = get_ui_icon("folder", size=16)
        folder_btn = ttk.Button(header, text=" " + tr("header_open_folder", "Open Folder"), command=self.open_output_folder, width=14)
        if folder_icon:
            folder_btn.configure(image=folder_icon, compound="left")
            folder_btn.image = folder_icon
        folder_btn.pack(side=tk.LEFT, padx=2)
        
        # Stretch
        ttk.Label(header, text="").pack(side=tk.LEFT, expand=True)
        
        # Version
        ttk.Label(header, text="v1.0.0", font=("Segoe UI", 9), foreground="gray").pack(side=tk.RIGHT, padx=10)
    
    def create_login_banner(self, parent):
        """Create login status banner (when not logged in)"""
        tr = self.translator.get
        banner = ttk.Frame(parent)
        banner.pack(fill=tk.X, padx=5, pady=5)
        
        # Warning icon + message
        msg_frame = ttk.Frame(banner)
        msg_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(msg_frame, text=tr("login_banner_title", "Not connected"), font=("Segoe UI", 10, "bold"), foreground="#FF9800").pack(side=tk.LEFT, padx=5)
        ttk.Label(
            msg_frame,
            text=tr("login_banner_note", "Login is only used by yt-dlp."),
            font=("Segoe UI", 9),
            foreground="#777"
        ).pack(side=tk.LEFT, padx=5)
        
        # Login button
        ttk.Button(banner, text=tr("login_banner_button", "YouTube Login"), command=self.open_login_popup, width=15).pack(side=tk.RIGHT, padx=5)
    
    def create_login_tab(self):
        """Create login tab with popup-only interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔐 Login")
        
        container = ttk.Frame(frame, padding=40)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        ttk.Label(container, text="Authentication", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(container, text=self.get_login_status(), font=("Arial", 11)).pack(pady=20)
        
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
        """Create video download tab with integrated audio options"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tr("tab_download", "Download"))
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # URL Input
        url_frame = ttk.LabelFrame(main, text=tr("download_url", "YouTube URL"), padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.download_url_entry = ttk.Entry(url_frame, width=80)
        self.download_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        verify_icon = get_ui_icon("verify", size=16)
        verify_btn = ttk.Button(url_frame, text=" " + tr("download_verify", "Verify"), command=self.verify_video)
        if verify_icon:
            verify_btn.configure(image=verify_icon, compound="left")
            verify_btn.image = verify_icon
        verify_btn.pack(side=tk.LEFT, padx=5)
        
        # Video Info
        info_frame = ttk.LabelFrame(main, text=tr("download_info", "Video Information"), padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"{tr('download_title', 'Title')}:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.download_title_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.download_title_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text=f"{tr('download_duration', 'Duration')}:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.download_duration_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.download_duration_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Download Mode Section
        mode_frame = ttk.LabelFrame(main, text=tr("download_mode", "Download Mode"), padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.download_mode_var = tk.StringVar(value="full")
        ttk.Radiobutton(mode_frame, text=tr("download_mode_full", "Complete Video"), variable=self.download_mode_var, value="full").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text=tr("download_mode_range", "Time Range"), variable=self.download_mode_var, value="range").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text=tr("download_mode_until", "Until Time"), variable=self.download_mode_var, value="until").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text=tr("download_mode_audio", "Audio Only"), variable=self.download_mode_var, value="audio").pack(anchor=tk.W, pady=3)
        
        # Time Range Inputs (shown when mode changes)
        time_frame = ttk.LabelFrame(main, text=f"{tr('download_start_time', 'Start Time')} / {tr('download_end_time', 'End Time')}", padding=10)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text=f"{tr('download_start_time', 'Start Time')}:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.time_start_entry = ttk.Entry(time_frame, width=15)
        self.time_start_entry.insert(0, "00:00")
        self.time_start_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(time_frame, text=f"{tr('download_end_time', 'End Time')}:", font=("Segoe UI", 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.time_end_entry = ttk.Entry(time_frame, width=15)
        self.time_end_entry.insert(0, "00:00")
        self.time_end_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(time_frame, text=tr("download_time_help", "Use start/end for range."), font=("Segoe UI", 8), foreground="gray").grid(row=1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        # Quality Section
        quality_frame = ttk.LabelFrame(main, text=tr("download_quality", "Quality"), padding=10)
        quality_frame.pack(fill=tk.X, pady=5)
        
        self.download_quality_var = tk.StringVar(value="best")
        ttk.Radiobutton(quality_frame, text=tr("download_quality_best", "Best Quality"), variable=self.download_quality_var, value="best").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text=tr("download_quality_mp4", "MP4 (Best)"), variable=self.download_quality_var, value="mp4").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="1080p", variable=self.download_quality_var, value="1080").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="720p", variable=self.download_quality_var, value="720").pack(anchor=tk.W, pady=2)
        
        # Audio Format Options (shown when Audio mode is selected)
        audio_frame = ttk.LabelFrame(main, text=tr("audio_format", "Audio Format"), padding=10)
        audio_frame.pack(fill=tk.X, pady=5)
        
        self.audio_format_var = tk.StringVar(value="mp3")
        fmt_sub_frame1 = ttk.Frame(audio_frame)
        fmt_sub_frame1.pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(fmt_sub_frame1, text="MP3", variable=self.audio_format_var, value="mp3").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(fmt_sub_frame1, text="WAV", variable=self.audio_format_var, value="wav").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(fmt_sub_frame1, text="M4A", variable=self.audio_format_var, value="m4a").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(fmt_sub_frame1, text="OPUS", variable=self.audio_format_var, value="opus").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(audio_frame, text=f"{tr('audio_bitrate', 'Bitrate')} (kbps):", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=5)
        self.audio_bitrate_var = tk.StringVar(value="320")
        fmt_sub_frame2 = ttk.Frame(audio_frame)
        fmt_sub_frame2.pack(anchor=tk.W, pady=3)
        for br in ["128", "192", "256", "320"]:
            ttk.Radiobutton(fmt_sub_frame2, text=f"{br} kbps", variable=self.audio_bitrate_var, value=br).pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main, text=tr("download_log", "Download Log"), padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.download_log = LogWidget(log_frame, theme=self.theme, height=8)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.download_log.yview)
        self.download_log.config(yscrollcommand=scrollbar.set)
        self.download_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        download_icon = get_ui_icon("download", size=16)
        download_btn = ttk.Button(btn_frame, text=" " + tr("download_btn", "Download"), command=self.start_download, width=14)
        if download_icon:
            download_btn.configure(image=download_icon, compound="left")
            download_btn.image = download_icon
        download_btn.pack(side=tk.LEFT, padx=5)
        
        stop_icon = get_ui_icon("stop", size=16)
        stop_btn = ttk.Button(btn_frame, text=" " + tr("download_stop", "Stop"), command=self.stop_download, width=14)
        if stop_icon:
            stop_btn.configure(image=stop_icon, compound="left")
            stop_btn.image = stop_icon
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        clear_icon = get_ui_icon("clear", size=16)
        clear_btn = ttk.Button(btn_frame, text=" " + tr("download_clear_log", "Clear Log"), command=lambda: self.download_log.clear(), width=14)
        if clear_icon:
            clear_btn.configure(image=clear_icon, compound="left")
            clear_btn.image = clear_icon
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def create_batch_tab(self):
        """Create batch download tab"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tr("tab_batch", "Batch"))
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # URLs Input
        urls_frame = ttk.LabelFrame(main, text=tr("batch_urls", "URLs (one per line)"), padding=10)
        urls_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(urls_frame, orient=tk.VERTICAL)
        self.batch_text = tk.Text(urls_frame, height=10, yscrollcommand=scrollbar.set)
        self.batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batch_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        batch_icon = get_ui_icon("batch", size=16)
        batch_btn = ttk.Button(btn_frame, text=" " + tr("batch_download_all", "Download All"), command=self.start_batch_download)
        if batch_icon:
            batch_btn.configure(image=batch_icon, compound="left")
            batch_btn.image = batch_icon
        batch_btn.pack(side=tk.LEFT, padx=5)
        
        paste_icon = get_ui_icon("paste", size=16)
        paste_btn = ttk.Button(btn_frame, text=" " + tr("batch_paste", "Paste"), command=self.batch_paste)
        if paste_icon:
            paste_btn.configure(image=paste_icon, compound="left")
            paste_btn.image = paste_icon
        paste_btn.pack(side=tk.LEFT, padx=5)
        
        clear_icon = get_ui_icon("clear", size=16)
        clear_btn = ttk.Button(btn_frame, text=" " + tr("batch_clear", "Clear"), command=lambda: self.batch_text.delete(1.0, tk.END))
        if clear_icon:
            clear_btn.configure(image=clear_icon, compound="left")
            clear_btn.image = clear_icon
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main, text=tr("batch_log", "Batch Log"), padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.batch_log = LogWidget(log_frame, theme=self.theme, height=6)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.batch_log.yview)
        self.batch_log.config(yscrollcommand=scrollbar.set)
        self.batch_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_live_tab(self):
        """Create live stream download tab with dynamic features"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tr("tab_live", "Live"))
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main, text=tr("live_title", "Live Stream Recorder"), font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)
        
        # URL Input
        url_frame = ttk.LabelFrame(main, text=tr("live_url", "Live Stream URL"), padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.live_url_entry = ttk.Entry(url_frame, width=80)
        self.live_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        check_icon = get_ui_icon("verify", size=16)
        check_btn = ttk.Button(url_frame, text=" " + tr("live_check_stream", "Check Stream"), command=self.verify_live_stream)
        if check_icon:
            check_btn.configure(image=check_icon, compound="left")
            check_btn.image = check_icon
        check_btn.pack(side=tk.LEFT, padx=5)
        
        # Stream Info
        info_frame = ttk.LabelFrame(main, text=tr("live_status", "Stream Status"), padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"{tr('live_status', 'Status')}:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.live_status_label = ttk.Label(info_frame, text=tr("live_status_unknown", "UNKNOWN"), foreground="#FF0000")
        self.live_status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text=f"{tr('live_duration', 'Duration')} (hh:mm:ss):", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.live_duration_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.live_duration_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Recording Mode
        mode_frame = ttk.LabelFrame(main, text=tr("live_mode", "Recording Mode"), padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.live_mode_var = tk.StringVar(value="continuous")
        ttk.Radiobutton(mode_frame, text=tr("live_mode_continuous", "Continuous Recording"), variable=self.live_mode_var, value="continuous").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text=tr("live_mode_until", "Record Until Time"), variable=self.live_mode_var, value="until").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text=tr("live_mode_duration", "Record Duration"), variable=self.live_mode_var, value="duration").pack(anchor=tk.W, pady=3)
        
        # Duration/Until inputs
        duration_frame = ttk.LabelFrame(main, text=tr("live_mode", "Recording Mode"), padding=10)
        duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duration_frame, text=f"{tr('live_hours', 'Hours')}:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.live_hours_entry = ttk.Entry(duration_frame, width=6)
        self.live_hours_entry.insert(0, "01")
        self.live_hours_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(duration_frame, text=f"{tr('live_minutes', 'Minutes')}:", font=("Segoe UI", 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.live_minutes_entry = ttk.Entry(duration_frame, width=6)
        self.live_minutes_entry.insert(0, "00")
        self.live_minutes_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(duration_frame, text=f"{tr('live_seconds', 'Seconds')}:", font=("Segoe UI", 9)).grid(row=0, column=4, sticky=tk.W, padx=5)
        self.live_seconds_entry = ttk.Entry(duration_frame, width=6)
        self.live_seconds_entry.insert(0, "00")
        self.live_seconds_entry.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # Quality Section
        quality_frame = ttk.LabelFrame(main, text=tr("live_quality", "Quality"), padding=10)
        quality_frame.pack(fill=tk.X, pady=5)
        
        self.live_quality_var = tk.StringVar(value="best")
        ttk.Radiobutton(quality_frame, text=tr("live_quality_best", "Best Available"), variable=self.live_quality_var, value="best").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="1080p", variable=self.live_quality_var, value="1080").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="720p", variable=self.live_quality_var, value="720").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="480p", variable=self.live_quality_var, value="480").pack(anchor=tk.W, pady=2)
        
        # Log
        log_frame = ttk.LabelFrame(main, text=tr("live_log", "Recording Log"), padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.live_log = LogWidget(log_frame, theme=self.theme, height=8)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.live_log.yview)
        self.live_log.config(yscrollcommand=scrollbar.set)
        self.live_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        record_icon = get_ui_icon("record", size=16)
        record_btn = ttk.Button(btn_frame, text=" " + tr("live_start_recording", "Start Recording"), command=self.start_live_recording, width=16)
        if record_icon:
            record_btn.configure(image=record_icon, compound="left")
            record_btn.image = record_icon
        record_btn.pack(side=tk.LEFT, padx=5)
        
        stop_icon = get_ui_icon("stop", size=16)
        stop_btn = ttk.Button(btn_frame, text=" " + tr("live_stop_recording", "Stop Recording"), command=self.stop_live_recording, width=16)
        if stop_icon:
            stop_btn.configure(image=stop_icon, compound="left")
            stop_btn.image = stop_icon
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        clear_icon = get_ui_icon("clear", size=16)
        clear_btn = ttk.Button(btn_frame, text=" " + tr("download_clear_log", "Clear Log"), command=lambda: self.live_log.clear(), width=14)
        if clear_icon:
            clear_btn.configure(image=clear_icon, compound="left")
            clear_btn.image = clear_icon
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def create_audio_tab(self):
        """Create audio conversion tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎵 Audio")
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # URL
        url_frame = ttk.LabelFrame(main, text="YouTube URL", padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.audio_url_entry = ttk.Entry(url_frame, width=80)
        self.audio_url_entry.pack(fill=tk.X)
        
        # Format
        format_frame = ttk.LabelFrame(main, text="Audio Format", padding=10)
        format_frame.pack(fill=tk.X, pady=5)
        
        self.audio_format_var = tk.StringVar(value="mp3")
        for fmt in ["MP3", "WAV", "M4A", "OPUS"]:
            ttk.Radiobutton(format_frame, text=fmt, variable=self.audio_format_var, value=fmt.lower()).pack(anchor=tk.W)
        
        # Bitrate
        bitrate_frame = ttk.LabelFrame(main, text="Bitrate (kbps)", padding=10)
        bitrate_frame.pack(fill=tk.X, pady=5)
        
        self.audio_bitrate_var = tk.StringVar(value="320")
        for br in ["128", "192", "256", "320"]:
            ttk.Radiobutton(bitrate_frame, text=f"{br} kbps", variable=self.audio_bitrate_var, value=br).pack(anchor=tk.W)
        
        # Log
        log_frame = ttk.LabelFrame(main, text="Conversion Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.audio_log = LogWidget(log_frame, theme=self.theme, height=10)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.audio_log.yview)
        self.audio_log.config(yscrollcommand=scrollbar.set)
        self.audio_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button
        ttk.Button(main, text="🎵 Convert", command=self.start_audio_conversion).pack(pady=10)
    
    def create_history_tab(self):
        """Create download history tab"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tr("tab_history", "History"))
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=5)
        
        refresh_icon = get_ui_icon("refresh", size=16)
        refresh_btn = ttk.Button(btn_frame, text=" " + tr("history_update", "Update"), command=self.refresh_history)
        if refresh_icon:
            refresh_btn.configure(image=refresh_icon, compound="left")
            refresh_btn.image = refresh_icon
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clear_icon = get_ui_icon("delete", size=16)
        clear_btn = ttk.Button(btn_frame, text=" " + tr("history_clear", "Clear History"), command=self.clear_history)
        if clear_icon:
            clear_btn.configure(image=clear_icon, compound="left")
            clear_btn.image = clear_icon
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Tree
        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("Date", "Filename", "Status")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, height=20, show="tree headings")
        
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
        """Create professional about tab with credits and information"""
        tr = self.translator.get
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tr("tab_about", "About"))
        
        # Main container with scroll
        canvas = tk.Canvas(frame, bg=self.theme.get("bg"), highlightthickness=0)
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
        main = ttk.Frame(scrollable_frame, padding=30)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title Section
        ttk.Label(main, text=tr("about_title", "EasyCut"), font=("Segoe UI", 22, "bold")).pack(pady=5)
        ttk.Label(main, text=tr("about_subtitle", "Professional YouTube Downloader & Audio Converter"), font=("Segoe UI", 11), foreground="gray").pack(pady=6)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Application Info
        info_frame = ttk.LabelFrame(main, text=tr("about_section_info", "Application Info"), padding=15)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = "\n".join([
            tr("about_version_info", "Version 1.0.0"),
            tr("about_author", "Author: Deko Costa"),
            tr("about_license", "License: MIT"),
        ])
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Segoe UI", 9)).pack(anchor=tk.W)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Social Links
        social_frame = ttk.LabelFrame(main, text=tr("about_section_links", "Connect & Support"), padding=15)
        social_frame.pack(fill=tk.X, pady=10)
        
        def open_link(url):
            import webbrowser
            webbrowser.open(url)
        
        links = [
            (tr("about_link_github", "GitHub Repository"), "https://github.com/dekouninter/EasyCut"),
            (tr("about_link_coffee", "Buy Me a Coffee"), "https://buymeacoffee.com/dekocosta"),
            (tr("about_link_livepix", "Livepix Donate"), "https://livepix.gg/dekocosta"),
        ]
        
        for i, (label, url) in enumerate(links):
            ttk.Button(
                social_frame,
                text=label,
                command=lambda u=url: open_link(u),
                width=35
            ).pack(pady=5)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Features
        features_frame = ttk.LabelFrame(main, text=tr("about_section_features", "Features"), padding=15)
        features_frame.pack(fill=tk.X, pady=10)
        
        features = tr("about_features_list", [])
        if not isinstance(features, list):
            features = []
        
        for feature in features:
            ttk.Label(features_frame, text=feature, font=("Arial", 9)).pack(anchor=tk.W, pady=3)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Technologies & Credits
        tech_frame = ttk.LabelFrame(main, text=tr("about_section_tech", "Technologies & Credits"), padding=15)
        tech_frame.pack(fill=tk.X, pady=10)
        
        tech_text = "\n".join([
            tr("about_credits_libs", "Libraries: yt-dlp, FFmpeg, keyring"),
            tr("about_credits_tools", "Tools: Python, Tkinter"),
            tr("about_tech_text", "Core: Python, Tkinter, yt-dlp, FFmpeg, keyring"),
        ])
        
        ttk.Label(tech_frame, text=tech_text, justify=tk.LEFT, font=("Segoe UI", 9)).pack(anchor=tk.W)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Credits
        credits_frame = ttk.LabelFrame(main, text=tr("about_section_thanks", "Special Thanks"), padding=15)
        credits_frame.pack(fill=tk.X, pady=10)
        
        credits_text = tr("about_thanks_text", "Thanks to the open-source community and creators.")
        ttk.Label(credits_frame, text=credits_text, justify=tk.LEFT, font=("Segoe UI", 9)).pack(anchor=tk.W)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Footer
        footer = ttk.Label(main, text=tr("about_footer", "Made with Python | MIT License | © 2026 Deko Costa"), font=("Segoe UI", 8), foreground="gray")
        footer.pack(pady=20)
    
    def apply_theme(self):
        """Apply theme to window"""
        style = self.theme.get_ttk_style()
        
        # Configure root colors
        self.root.config(bg=self.theme.get("bg"))
    
    def toggle_theme(self):
        """Toggle theme with instant reload"""
        self.dark_mode = self.theme.toggle()
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
