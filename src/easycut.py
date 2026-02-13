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
        self.root.title("EasyCut - YouTube Downloader & Audio Converter")
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
        self.status_bar = StatusBar(main_frame, theme=self.theme)
        self.status_bar.pack(fill=tk.X)
        self.update_login_status()
        
        # Donation button
        donation_btn = DonationButton(self.root)
        donation_btn.create_floating_button(main_frame)
    
    def create_header(self, parent):
        """Create professional header with controls"""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        # Logo/Title
        title_lbl = ttk.Label(header, text="🎬 EasyCut", font=("Arial", 14, "bold"))
        title_lbl.pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(header, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Theme toggle
        ttk.Button(header, text="🌓 Theme", command=self.toggle_theme, width=10).pack(side=tk.LEFT, padx=2)
        
        # Language selector
        lang_var = tk.StringVar(value="English" if self.language == "en" else "Portuguese")
        lang_combo = ttk.Combobox(header, values=["English", "Portuguese"], state="readonly", width=12)
        lang_combo.set(lang_var.get())
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self.change_language("en" if lang_combo.get() == "English" else "pt"))
        lang_combo.pack(side=tk.LEFT, padx=2)
        
        # Login button
        ttk.Button(header, text="🔐 Login", command=self.open_login_popup, width=10).pack(side=tk.LEFT, padx=2)
        
        # Logout button
        ttk.Button(header, text="📂 Folder", command=self.open_output_folder, width=10).pack(side=tk.LEFT, padx=2)
        
        # Stretch
        ttk.Label(header, text="").pack(side=tk.LEFT, expand=True)
        
        # Version
        ttk.Label(header, text="v1.0.0", font=("Arial", 9), foreground="gray").pack(side=tk.RIGHT, padx=10)
    
    def create_login_banner(self, parent):
        """Create login status banner (when not logged in)"""
        banner = ttk.Frame(parent)
        banner.pack(fill=tk.X, padx=5, pady=5)
        
        # Warning icon + message
        msg_frame = ttk.Frame(banner)
        msg_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(msg_frame, text="⚠️ Not logged in", font=("Arial", 10, "bold"), foreground="#FF9800").pack(side=tk.LEFT, padx=5)
        ttk.Label(msg_frame, text="Some features require authentication", font=("Arial", 9), foreground="#777").pack(side=tk.LEFT, padx=5)
        
        # Login button
        ttk.Button(banner, text="🔓 Login Now", command=self.open_login_popup, width=15).pack(side=tk.RIGHT, padx=5)
    
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
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⬇ Download")
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # URL Input
        url_frame = ttk.LabelFrame(main, text="📌 YouTube URL", padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.download_url_entry = ttk.Entry(url_frame, width=80)
        self.download_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(url_frame, text="✓ Check", command=self.verify_video).pack(side=tk.LEFT, padx=5)
        
        # Video Info
        info_frame = ttk.LabelFrame(main, text="📊 Video Information", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Title:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.download_title_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.download_title_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="Duration:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.download_duration_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.download_duration_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Download Mode Section
        mode_frame = ttk.LabelFrame(main, text="🎬 Download Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.download_mode_var = tk.StringVar(value="full")
        ttk.Radiobutton(mode_frame, text="Full Video", variable=self.download_mode_var, value="full").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text="Time Range", variable=self.download_mode_var, value="range").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text="Until Time", variable=self.download_mode_var, value="until").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text="Audio Only 🎵", variable=self.download_mode_var, value="audio").pack(anchor=tk.W, pady=3)
        
        # Time Range Inputs (shown when mode changes)
        time_frame = ttk.LabelFrame(main, text="⏱️ Time Range (MM:SS format)", padding=10)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="Start:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.time_start_entry = ttk.Entry(time_frame, width=15)
        self.time_start_entry.insert(0, "00:00")
        self.time_start_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(time_frame, text="End/Until:", font=("Arial", 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.time_end_entry = ttk.Entry(time_frame, width=15)
        self.time_end_entry.insert(0, "00:00")
        self.time_end_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(time_frame, text="Help: 'Start' for range mode, both for range | 'End' for until mode", font=("Arial", 8), foreground="gray").grid(row=1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        # Quality Section
        quality_frame = ttk.LabelFrame(main, text="🎯 Quality", padding=10)
        quality_frame.pack(fill=tk.X, pady=5)
        
        self.download_quality_var = tk.StringVar(value="best")
        ttk.Radiobutton(quality_frame, text="Best Available", variable=self.download_quality_var, value="best").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="MP4 (Compatible)", variable=self.download_quality_var, value="mp4").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="1080p HD", variable=self.download_quality_var, value="1080").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="720p HD", variable=self.download_quality_var, value="720").pack(anchor=tk.W, pady=2)
        
        # Audio Format Options (shown when Audio mode is selected)
        audio_frame = ttk.LabelFrame(main, text="🔊 Audio Format", padding=10)
        audio_frame.pack(fill=tk.X, pady=5)
        
        self.audio_format_var = tk.StringVar(value="mp3")
        fmt_sub_frame1 = ttk.Frame(audio_frame)
        fmt_sub_frame1.pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(fmt_sub_frame1, text="MP3", variable=self.audio_format_var, value="mp3").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(fmt_sub_frame1, text="WAV", variable=self.audio_format_var, value="wav").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(fmt_sub_frame1, text="M4A", variable=self.audio_format_var, value="m4a").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(fmt_sub_frame1, text="OPUS", variable=self.audio_format_var, value="opus").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(audio_frame, text="Bitrate (kbps):", font=("Arial", 9)).pack(anchor=tk.W, pady=5)
        self.audio_bitrate_var = tk.StringVar(value="320")
        fmt_sub_frame2 = ttk.Frame(audio_frame)
        fmt_sub_frame2.pack(anchor=tk.W, pady=3)
        for br in ["128", "192", "256", "320"]:
            ttk.Radiobutton(fmt_sub_frame2, text=f"{br} kbps", variable=self.audio_bitrate_var, value=br).pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main, text="📝 Download Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.download_log = LogWidget(log_frame, theme=self.theme, height=8)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.download_log.yview)
        self.download_log.config(yscrollcommand=scrollbar.set)
        self.download_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="⬇ Download", command=self.start_download, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⏹ Stop", command=self.stop_download, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Clear Log", command=lambda: self.download_log.clear(), width=15).pack(side=tk.LEFT, padx=5)
    
    def create_batch_tab(self):
        """Create batch download tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📦 Batch")
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # URLs Input
        urls_frame = ttk.LabelFrame(main, text="URLs (one per line)", padding=10)
        urls_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(urls_frame, orient=tk.VERTICAL)
        self.batch_text = tk.Text(urls_frame, height=10, yscrollcommand=scrollbar.set)
        self.batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batch_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="⬇ Download All", command=self.start_batch_download).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Paste", command=self.batch_paste).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Clear", command=lambda: self.batch_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main, text="Batch Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.batch_log = LogWidget(log_frame, theme=self.theme, height=6)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.batch_log.yview)
        self.batch_log.config(yscrollcommand=scrollbar.set)
        self.batch_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_live_tab(self):
        """Create live stream download tab with dynamic features"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔴 Live")
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main, text="🔴 Live Stream Recorder", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # URL Input
        url_frame = ttk.LabelFrame(main, text="📌 Live Stream URL", padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.live_url_entry = ttk.Entry(url_frame, width=80)
        self.live_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(url_frame, text="✓ Check Stream", command=self.verify_live_stream).pack(side=tk.LEFT, padx=5)
        
        # Stream Info
        info_frame = ttk.LabelFrame(main, text="📊 Stream Information", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Status:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.live_status_label = ttk.Label(info_frame, text="🔴 UNKNOWN", foreground="#FF0000")
        self.live_status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="Duration (hh:mm:ss):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.live_duration_label = ttk.Label(info_frame, text="-", foreground="gray")
        self.live_duration_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Recording Mode
        mode_frame = ttk.LabelFrame(main, text="🎬 Recording Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.live_mode_var = tk.StringVar(value="continuous")
        ttk.Radiobutton(mode_frame, text="Continuous Recording", variable=self.live_mode_var, value="continuous").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text="Record Until Time", variable=self.live_mode_var, value="until").pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text="Record Duration", variable=self.live_mode_var, value="duration").pack(anchor=tk.W, pady=3)
        
        # Duration/Until inputs
        duration_frame = ttk.LabelFrame(main, text="⏱️ Record Settings", padding=10)
        duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duration_frame, text="Hours:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.live_hours_entry = ttk.Entry(duration_frame, width=6)
        self.live_hours_entry.insert(0, "01")
        self.live_hours_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(duration_frame, text="Minutes:", font=("Arial", 9)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.live_minutes_entry = ttk.Entry(duration_frame, width=6)
        self.live_minutes_entry.insert(0, "00")
        self.live_minutes_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(duration_frame, text="Seconds:", font=("Arial", 9)).grid(row=0, column=4, sticky=tk.W, padx=5)
        self.live_seconds_entry = ttk.Entry(duration_frame, width=6)
        self.live_seconds_entry.insert(0, "00")
        self.live_seconds_entry.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # Quality Section
        quality_frame = ttk.LabelFrame(main, text="🎯 Quality", padding=10)
        quality_frame.pack(fill=tk.X, pady=5)
        
        self.live_quality_var = tk.StringVar(value="best")
        ttk.Radiobutton(quality_frame, text="Best Available", variable=self.live_quality_var, value="best").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="1080p", variable=self.live_quality_var, value="1080").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="720p", variable=self.live_quality_var, value="720").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(quality_frame, text="480p", variable=self.live_quality_var, value="480").pack(anchor=tk.W, pady=2)
        
        # Log
        log_frame = ttk.LabelFrame(main, text="📝 Recording Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.live_log = LogWidget(log_frame, theme=self.theme, height=8)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.live_log.yview)
        self.live_log.config(yscrollcommand=scrollbar.set)
        self.live_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🔴 Start Recording", command=self.start_live_recording, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⏹ Stop Recording", command=self.stop_live_recording, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Clear Log", command=lambda: self.live_log.clear(), width=15).pack(side=tk.LEFT, padx=5)
    
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
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📜 History")
        
        main = ttk.Frame(frame, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Clear", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        # Tree
        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("Date", "Filename", "Status")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, height=20, show="tree headings")
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.config(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_history()
    
    def create_about_tab(self):
        """Create professional about tab with credits and information"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="ℹ About")
        
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
        ttk.Label(main, text="🎬 EasyCut", font=("Arial", 24, "bold")).pack(pady=5)
        ttk.Label(main, text="Professional YouTube Downloader & Audio Converter", font=("Arial", 12, "italic"), foreground="gray").pack(pady=10)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Application Info
        info_frame = ttk.LabelFrame(main, text="📋 Application Info", padding=15)
        info_frame.pack(fill=tk.X, pady=10)
        
        app_info = [
            ("Version", "1.0.0"),
            ("License", "MIT"),
            ("Author", "Deko Costa"),
            ("Release Date", "February 2026"),
        ]
        
        for label, value in app_info:
            lbl = ttk.Label(info_frame, text=f"{label}:", font=("Arial", 10, "bold"))
            lbl.grid(row=app_info.index((label, value)), column=0, sticky=tk.W, padx=10, pady=5)
            val = ttk.Label(info_frame, text=value, foreground="gray")
            val.grid(row=app_info.index((label, value)), column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Social Links
        social_frame = ttk.LabelFrame(main, text="🔗 Connect & Support", padding=15)
        social_frame.pack(fill=tk.X, pady=10)
        
        def open_link(url):
            import webbrowser
            webbrowser.open(url)
        
        links = [
            ("🐙 GitHub Repository", "https://github.com/dekouninter/EasyCut"),
            ("☕ Buy Me a Coffee", "https://buymeacoffee.com/dekocosta"),
            ("💰 Livepix Donate", "https://livepix.gg/dekocosta"),
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
        features_frame = ttk.LabelFrame(main, text="✨ Features", padding=15)
        features_frame.pack(fill=tk.X, pady=10)
        
        features = [
            "✓ Single & Batch Video Downloads",
            "✓ Integrated Audio Conversion (MP3, WAV, M4A, OPUS)",
            "✓ Live Stream Recording with Dynamic Controls",
            "✓ Time Range & Custom Cutting",
            "✓ Multiple Quality Selections",
            "✓ Real-time Logging & Progress Tracking",
            "✓ Dark/Light Theme with Instant Reload",
            "✓ Multi-language Support (EN, PT)",
            "✓ Secure Credential Storage (Windows Keyring)",
            "✓ Download History",
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=feature, font=("Arial", 9)).pack(anchor=tk.W, pady=3)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Technologies & Credits
        tech_frame = ttk.LabelFrame(main, text="🛠️ Technologies & Credits", padding=15)
        tech_frame.pack(fill=tk.X, pady=10)
        
        tech_text = """
Core Technologies:
• Python 3.8+ - Programming Language
• Tkinter - GUI Framework
• yt-dlp - YouTube Video Downloading (GPL-3.0)
• FFmpeg - Audio/Video Processing (GPL-2.0)
• keyring - Secure Credential Storage (MIT)

Additional Libraries:
• threading - Concurrent Operations
• logging - Application Logging
• json - Configuration Management
• pathlib - File System Operations

Design & Inspiration:
• Microsoft Fluent Design System
• Modern UI/UX Principles
• Professional Python Development Standards
        """
        
        ttk.Label(tech_frame, text=tech_text, justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Credits
        credits_frame = ttk.LabelFrame(main, text="🙏 Special Thanks", padding=15)
        credits_frame.pack(fill=tk.X, pady=10)
        
        credits_text = """
Special thanks to:

• yt-dlp Community - For maintaining the best YouTube downloader
• FFmpeg Project - For powerful multimedia processing
• Python Community - For excellent open-source tools
• Tkinter Community - For GUI framework support

This application is built with ❤️ for video enthusiasts and content creators.
"""
        
        ttk.Label(credits_frame, text=credits_text, justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W)
        
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Footer
        footer = ttk.Label(main, text="Made with Python 🐍 | MIT License | © 2026 Deko Costa", font=("Arial", 8), foreground="gray")
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
        
        popup = LoginPopup(self.root, callback=handle_login)
        popup.show()
    
    def do_logout(self):
        """Logout user"""
        if messagebox.askyesno("Confirm", "Do you want to disconnect?"):
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
        if self.logged_in:
            return f"Logged in as: {self.current_email}"
        return "Not logged in"
    
    def verify_video(self):
        """Verify video URL"""
        url = self.download_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        self.download_log.add_log("Verifying URL...")
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.download_log.add_log("yt-dlp not installed", "ERROR")
                return
            
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    
                    self.download_title_label.config(text=title[:50])
                    mins, secs = divmod(duration, 60)
                    self.download_duration_label.config(text=f"{int(mins)}:{int(secs):02d}")
                    
                    self.download_log.add_log("✓ Video info retrieved")
            except Exception as e:
                self.download_log.add_log(f"Error: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=verify_thread, daemon=True)
        thread.start()
    
    def start_download(self):
        """Start downloading video"""
        url = self.download_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return
        
        self.is_downloading = True
        self.download_log.add_log(f"Downloading: {url}")
        
        quality = self.download_quality_var.get()
        
        def download_thread():
            if not YT_DLP_AVAILABLE:
                self.download_log.add_log("yt-dlp not installed", "ERROR")
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
                    
                    self.download_log.add_log("✓ Download completed")
                    self.refresh_history()
            
            except Exception as e:
                self.download_log.add_log(f"✗ Error: {str(e)}", "ERROR")
            
            finally:
                self.is_downloading = False
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def stop_download(self):
        """Stop current download"""
        self.is_downloading = False
        self.download_log.add_log("Download stopped")
    
    def start_batch_download(self):
        """Start batch download"""
        urls_text = self.batch_text.get(1.0, tk.END).strip()
        
        if not urls_text:
            messagebox.showwarning("Warning", "Add at least one URL")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        self.batch_log.add_log(f"Downloading {len(urls)} videos...")
        
        def batch_thread():
            success = 0
            for i, url in enumerate(urls, 1):
                if not self.is_valid_youtube_url(url):
                    self.batch_log.add_log(f"[{i}/{len(urls)}] Invalid URL", "WARNING")
                    continue
                
                if not YT_DLP_AVAILABLE:
                    self.batch_log.add_log("yt-dlp not installed", "ERROR")
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
                        self.batch_log.add_log(f"[{i}/{len(urls)}] ✓ Downloaded: {info.get('title', 'Video')[:30]}")
                
                except Exception as e:
                    self.batch_log.add_log(f"[{i}/{len(urls)}] ✗ Error: {str(e)[:50]}", "ERROR")
            
            self.batch_log.add_log(f"Batch complete: {success}/{len(urls)} successful")
            self.refresh_history()
        
        thread = threading.Thread(target=batch_thread, daemon=True)
        thread.start()
    
    def batch_paste(self):
        """Paste from clipboard"""
        try:
            data = self.root.clipboard_get()
            self.batch_text.insert(tk.END, data)
        except Exception as e:
            messagebox.showerror("Error", f"Could not paste: {e}")
    
    def start_audio_conversion(self):
        """Start audio conversion"""
        url = self.audio_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        fmt = self.audio_format_var.get()
        bitrate = self.audio_bitrate_var.get()
        
        self.audio_log.add_log(f"Converting to {fmt.upper()} ({bitrate}kbps)...")
        
        def audio_thread():
            if not YT_DLP_AVAILABLE:
                self.audio_log.add_log("yt-dlp not installed", "ERROR")
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
                    
                    self.audio_log.add_log("✓ Conversion completed")
                    self.refresh_history()
            
            except Exception as e:
                self.audio_log.add_log(f"✗ Error: {str(e)}", "ERROR")
        
        thread = threading.Thread(target=audio_thread, daemon=True)
        thread.start()
    
    def refresh_history(self):
        """Refresh download history"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.config_manager.load_history()
        
        if not history:
            self.history_tree.insert("", tk.END, values=("No downloads yet", "-", "-"))
            return
        
        for item in reversed(history):
            date_obj = datetime.fromisoformat(item.get("date", ""))
            date_str = date_obj.strftime("%Y-%m-%d %H:%M")
            filename = item.get("filename", "unknown")
            status = item.get("status", "unknown")
            
            self.history_tree.insert("", tk.END, values=(date_str, filename[:40], status))
    
    def clear_history(self):
        """Clear download history"""
        if messagebox.askyesno("Confirm", "Clear all history?"):
            self.config_manager.save_history([])
            self.refresh_history()
    
    def open_output_folder(self):
        """Open output folder"""
        try:
            import subprocess
            subprocess.Popen(f'explorer "{self.output_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")
    
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
        url = self.live_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            self.live_status_label.config(text="❌ INVALID", foreground="#FF0000")
            return
        
        self.live_log.add_log("Checking stream status...")
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.live_log.add_log("yt-dlp not installed", "ERROR")
                self.live_status_label.config(text="❌ ERROR", foreground="#FF0000")
                return
            
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    is_live = info.get('is_live', False)
                    
                    if is_live:
                        self.live_status_label.config(text="🔴 LIVE NOW", foreground="#FF0000")
                        self.live_log.add_log("✓ Stream is LIVE and ready to record")
                    else:
                        self.live_status_label.config(text="⏱️ OFFLINE", foreground="#FF9800")
                        self.live_log.add_log("Stream is currently offline")
                    
                    duration = info.get('duration')
                    if duration:
                        hours, remainder = divmod(duration, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        self.live_duration_label.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
                    
            except Exception as e:
                self.live_log.add_log(f"Error: {str(e)}", "ERROR")
                self.live_status_label.config(text="❌ ERROR", foreground="#FF0000")
        
        thread = threading.Thread(target=verify_thread, daemon=True)
        thread.start()
    
    def start_live_recording(self):
        """Start recording live stream"""
        url = self.live_url_entry.get().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        if not YT_DLP_AVAILABLE:
            messagebox.showerror("Error", "yt-dlp is not installed")
            return
        
        self.is_downloading = True
        self.live_log.add_log("Starting live stream recording...")
        
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
                    self.live_log.add_log("📥 Downloading live stream...")
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": Path(filename).name,
                        "status": "success",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                    
                    self.live_log.add_log("✓ Recording completed successfully")
                    self.refresh_history()
            
            except Exception as e:
                self.live_log.add_log(f"✗ Error: {str(e)}", "ERROR")
            
            finally:
                self.is_downloading = False
        
        thread = threading.Thread(target=record_thread, daemon=True)
        thread.start()
    
    def stop_live_recording(self):
        """Stop live stream recording"""
        if self.is_downloading:
            self.is_downloading = False
            self.live_log.add_log("Recording stopped by user")
        else:
            messagebox.showinfo("Info", "No recording in progress")
    
    def live_progress_hook(self, d):
        """Progress hook for live recording"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '0 B/s')
            eta = d.get('_eta_str', 'Unknown')
            self.live_log.add_log(f"⬇️ {percent} | Speed: {speed} | ETA: {eta}")


def main():
    """Main function"""
    root = tk.Tk()
    app = EasyCutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
