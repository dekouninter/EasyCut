# -*- coding: utf-8 -*-
"""
EasyCut - YouTube Video Downloader and Audio Converter
Professional Desktop Application using Tkinter

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
Version: 1.9.0
License: GPL-3.0

Features:
- Download YouTube videos with multiple quality options
- Batch downloads with queue management
- Audio conversion (MP3, WAV, M4A, OPUS)
- YouTube OAuth authentication (integrated)
- Real-time logging
- Live stream recording support
- Dark/Light theme with instant reload
- Multi-language support (EN, PT, ES, FR, DE, IT, JA)
- Professional UI design with modern components
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import logging
import re
import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import time

# Import local modules
sys.path.insert(0, os.path.dirname(__file__))
from i18n import translator as t, Translator
from ui_enhanced import ConfigManager, LogWidget, StatusBar
from oauth_manager import OAuthManager, OAuthError
from donation_system import DonationButton
from icon_manager import icon_manager, get_ui_icon, set_icon_theme
from design_system import ModernTheme, DesignTokens, Typography, Spacing, Icons
from modern_components import (
    ModernButton, ModernCard, ScrollableFrame, SectionHeader,
    Badge, Tooltip, InfoBanner, EmptyState, Separator, IconLabel,
    ToggleSwitch, AnimatedPanel, ModernEntry, HoverFrame, ProgressRing,
    AnimatedCounter, EMOJI_ICONS, HAS_ICON_RENDERER
)
from font_loader import setup_fonts, LOADED_FONT_FAMILY
from post_processor import PostProcessor
from channel_monitor import ChannelMonitor
from video_player import EmbeddedPlayer, is_player_available
from __version__ import __version__ as APP_VERSION

# SVG icon renderer for high-quality icons
try:
    from icon_renderer import render_feather_icon, create_gradient_image, clear_icon_cache
    _HAS_SVG = True
except ImportError:
    _HAS_SVG = False
    def render_feather_icon(*a, **kw): return None
    def create_gradient_image(*a, **kw): return None
    def clear_icon_cache(): pass

# pywinstyles for Windows Mica/Acrylic backdrop
try:
    import pywinstyles
    _HAS_PYWINSTYLES = True
except ImportError:
    _HAS_PYWINSTYLES = False

# darkdetect for OS theme detection
try:
    import darkdetect
    _HAS_DARKDETECT = True
except ImportError:
    _HAS_DARKDETECT = False

# Import external libraries
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

class _YTLogger:
    """Custom yt-dlp logger that suppresses Deno and other noisy non-critical warnings (Issue #23)."""

    _SUPPRESS_FRAGMENTS = (
        "Deno not found",
        "Browser JavaScript",
        "jsinterp",
        "challenge solving failed",  # suppress EJS warning
        "js:github",              # suggestion line from EJS
        "remote-components",      # part of the recommendation text
        "EJS",                    # generic reference
    )

    def debug(self, _msg: str) -> None:
        pass  # silence yt-dlp debug chatter; progress tracked via progress_hooks

    def info(self, _msg: str) -> None:
        pass  # suppress info; use progress_hooks for display

    _runtime_warned = False

    def warning(self, msg: str) -> None:
        # if the message matches any of the suppressed fragments we normally
        # drop it, but if it's the challenge-failed/EJS warning we also pop up a
        # friendly reminder once so the user knows to install a JS runtime.
        if any(fragment in msg for fragment in self._SUPPRESS_FRAGMENTS):
            if ("challenge" in msg or "EJS" in msg) and not self._runtime_warned:
                try:
                    import tkinter as _tk
                    from tkinter import messagebox
                    self._runtime_warned = True
                    messagebox.showwarning(
                        "JavaScript Runtime",
                        "yt-dlp encountered a JavaScript challenge.\n"
                        "Install Node.js or the EJS solver (see yt-dlp wiki) "
                        "for full format support."
                    )
                except Exception:
                    pass
            return  # drop non-critical JS-engine warnings
        logging.getLogger(__name__).warning("[yt-dlp] %s", msg)

    def error(self, msg: str) -> None:
        logging.getLogger(__name__).error("[yt-dlp] %s", msg)


class EasyCutApp:
    """Professional YouTube Downloader Application"""
    
    def __init__(self, root):
        self.root = root
        
        # Configuration
        self.config_manager = ConfigManager()
        self.load_config()
        # translator must exist before any messages are shown
        self.translator = Translator(self.language)
        # warn about missing JavaScript runtime which yt-dlp may require for
        # EJS challenge solving; this is informational rather than fatal
        if not self.config_manager.get("suppress_js_runtime_prompt", False):
            tr = self.translator.get
            if not shutil.which("node") and not shutil.which("d8"):
                # no runtime, prompt user with direct install link
                self._show_js_runtime_dialog(missing=True)
            else:
                # check whether runtime is too old (arbitrary threshold)
                ver = self._get_js_runtime_version()
                if ver and self._is_js_runtime_outdated(ver):
                    self._show_js_runtime_dialog(missing=False, version=ver)
        
        # OAuth Manager
        self.oauth_manager = OAuthManager(config_dir="config")

        # JavaScript runtime helpers
        # The dialog is shown above during initialization if needed
        
        # Load custom fonts FIRST
        self.font_family = setup_fonts()
        
        # Modern Theme & Design System
        self.theme = ModernTheme(dark_mode=self.dark_mode, font_family=self.font_family)
        self.design = DesignTokens(dark_mode=self.dark_mode)
        
        # Icon Manager
        self.icon_manager = icon_manager
        set_icon_theme(self.dark_mode)  # Sync icon colors with theme
        
        # State
        self.is_downloading = False
        self.is_recording = False   # Separate flag for live recording (Issues #46/#53)
        self.download_semaphore = threading.BoundedSemaphore(value=3)
        self._video_formats = []  # Fetched format list from yt-dlp
        self._video_info_cache = {}  # Cached metadata from last verify
        self._format_id_map = {}  # Maps combo index to format_id
        self._channel_limit_var = None  # Channel video limit spinbox variable
        self._thumbnail_cache = {}  # video_id -> PhotoImage for history
        self._download_queue = []  # List of {url, status, title} for batch queue
        self.download_quality_var = tk.StringVar(value="best")  # Quality preset for downloads

        # Complete remaining initialization (paths, post-processor, UI setup etc.)
        self._finish_init()

    # ---- JS runtime helpers --------------------------------------------------
    def _get_js_runtime_version(self) -> str | None:
        """Return the version string of a JS runtime on PATH (node or d8) or None."""
        for cmd in ("node", "d8"):
            path = shutil.which(cmd)
            if path:
                try:
                    completed = subprocess.run([path, "--version"],
                                               capture_output=True, text=True, timeout=3)
                    out = completed.stdout.strip() or completed.stderr.strip()
                    # node outputs like 'v18.12.1'
                    return out.lstrip('v')
                except Exception:
                    return None
        return None

    def _is_js_runtime_outdated(self, version: str) -> bool:
        """Simple check: runtime is outdated if major version < 18."""
        try:
            major = int(version.split(".")[0])
            return major < 18
        except Exception:
            return False

    def _install_js_runtime_dialog(self, parent_win) -> None:
        """Attempt to run `npm install -g ejs` and notify the user of result."""
        tr = self.translator.get
        try:
            from tkinter import messagebox
        except ImportError:
            return
        # run in background thread to avoid freezing UI
        def worker():
            # create progress window on the main thread
            prog = None
            bar = None
            def _create_progress():
                nonlocal prog, bar
                try:
                    prog = tk.Toplevel(parent_win) if parent_win else tk.Toplevel(self.root)
                    prog.title(tr("js_runtime_installing","Installing runtime"))
                    bar = ttk.Progressbar(prog, mode="indeterminate")
                    bar.pack(fill="x", padx=20, pady=20)
                    bar.start(10)
                except Exception:
                    pass
            self.root.after(0, _create_progress)
            import time; time.sleep(0.3)  # allow main thread to create widgets
            try:
                subprocess.run(["npm", "install", "-g", "ejs"], check=True)
                def _on_success():
                    if prog:
                        try: bar.stop(); prog.destroy()
                        except Exception: pass
                    messagebox.showinfo(tr("js_runtime_installing","Installing runtime"),
                                        tr("js_runtime_installed","Installation complete"))
                    self.config_manager.set("suppress_js_runtime_prompt", True)
                self.root.after(0, _on_success)
            except Exception as exc:
                def _on_fail():
                    if prog:
                        try: bar.stop(); prog.destroy()
                        except Exception: pass
                    messagebox.showerror(tr("js_runtime_installing","Installing runtime"),
                                         tr("js_runtime_install_failed","Installation failed"))
                self.root.after(0, _on_fail)
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _show_js_runtime_dialog(self, missing: bool, version: str | None = None) -> None:
        """Pop up a window guiding the user to install or update a JS runtime.
        If `missing` True, presents install instructions; otherwise suggests update.
        """
        try:
            from tkinter import Toplevel, Label, Button
            import webbrowser
        except ImportError:
            return

        tr = self.translator.get
        title = tr("js_runtime_missing", "JS runtime missing")
        msg = tr("js_runtime_info", "No JavaScript runtime (e.g. Node.js) was found in PATH. "
                 "Certain YouTube videos require it for full format support. "
                 "See yt-dlp wiki for EJS installation.")
        if not missing and version:
            msg = tr("js_runtime_update_info", "Your JavaScript runtime (v{}) may be outdated.")
            msg = msg.format(version) + "\n" + tr("js_runtime_info", "No JavaScript runtime (e.g. Node.js) was found in PATH. "
                 "Certain YouTube videos require it for full format support. "
                 "See yt-dlp wiki for EJS installation.")

        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("420x200")
        Label(dlg, text=msg, wraplength=400, justify="left").pack(padx=10, pady=10)
        dont_var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(dlg, text=tr("js_runtime_dont_show","Don't show again"), variable=dont_var)
        cb.pack(pady=(0,10))
        def install_action():
            # try to install via npm first
            if shutil.which("npm"):
                self._install_js_runtime_dialog(dlg)
            else:
                webbrowser.open("https://github.com/yt-dlp/yt-dlp#ejs--javascript-runtime")
        btn_text = tr("js_runtime_install_button", "Install runtime")
        Button(dlg, text=btn_text, command=install_action).pack(pady=5)
        def close_action():
            if dont_var.get():
                self.config_manager.set("suppress_js_runtime_prompt", True)
            dlg.destroy()
        Button(dlg, text=tr("msg_close","Close"), command=close_action).pack(pady=5)

    # ---- End of JS runtime helpers -------------------------------------------

    def _finish_init(self):
        """Complete initialization — called from __init__ after early setup."""
        self._queue_paused = False  # Whether the queue is paused
        self._chapters_info = []  # Detected video chapters from yt-dlp
        
        # Paths (must be set before PostProcessor/ChannelMonitor)
        self.output_dir = Path(self.config_manager.get("output_dir", "downloads"))
        self.output_dir.mkdir(exist_ok=True)
        
        # Post-processor and Channel Monitor
        self.post_processor = PostProcessor(output_dir=str(self.output_dir))
        self.channel_monitor = ChannelMonitor(config_dir="config", output_dir=str(self.output_dir))
        self.embedded_player = None  # Embedded video player in Live tab
        self.pp_player = None        # Embedded video player in Post-Processing card
        self._clip_markers = []  # List of {start, end} for live clipper
        self._clip_start_time = None  # Current clip start timestamp
        self._live_recording_start = None  # When live recording started
        self._live_elapsed_seconds = 0  # Elapsed seconds in live recording
        
        # Setup
        self.setup_logging()
        self.setup_window()
        self.apply_theme()  # CRITICAL: Apply theme BEFORE creating UI
        self.setup_ui()
        self.log_app("✓ EasyCut started successfully")
        # Issue #63: verify followed channels shortly after startup
        self.root.after(5000, self._following_startup_check)
    
    def load_config(self):
        """Load configuration from file"""
        config = self.config_manager.load()
        self.dark_mode = config.get("dark_mode", True)  # Default: Dark
        self.language = config.get("language", "en")    # Default: English
    
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
        self.logger.info(f"Version: {APP_VERSION}")
    
    def setup_window(self):
        """Setup main window with optional Windows Mica backdrop"""
        self.root.title("EasyCut")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 700)
        
        # Apply pywinstyles Mica backdrop (Windows 11 only, graceful fallback)
        if _HAS_PYWINSTYLES:
            try:
                if self.dark_mode:
                    pywinstyles.apply_style(self.root, "dark")
                else:
                    pywinstyles.apply_style(self.root, "normal")
            except Exception:
                pass
        
        # Setup graceful shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup complete user interface — premium sidebar layout"""
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # State
        self.sidebar_expanded = True
        self.active_section = "download"
        self.section_frames = {}
        self.nav_buttons = {}
        
        # Root layout
        root_frame = tk.Frame(self.root, bg=self.design.get_color("bg_base"))
        root_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- HEADER (52px) ---
        self.create_header(root_frame)
        
        # --- OAuth AUTHENTICATION BANNER ---
        self.create_login_banner(root_frame)
        
        # --- BODY (sidebar + content) ---
        body = tk.Frame(root_frame, bg=self.design.get_color("bg_primary"))
        body.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar_bg = self.design.get_color("sidebar_bg")
        self.sidebar_frame = tk.Frame(body, bg=sidebar_bg, width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)
        
        # Sidebar border (right edge)
        tk.Frame(
            self.sidebar_frame, bg=self.design.get_color("sidebar_border"), width=1
        ).pack(side=tk.RIGHT, fill=tk.Y)
        
        self._build_sidebar()
        
        # Content area
        self.content_area = tk.Frame(body, bg=self.design.get_color("bg_primary"))
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
        self.section_frames["following"] = self.create_following_tab()
        self.section_frames["history"] = self.create_history_tab()
        self.section_frames["settings"] = self.create_settings_tab()
        self.section_frames["about"] = self.create_about_tab()
        
        # Select initial section
        self._switch_section("download")
        
        # --- LOG PANEL (collapsible — inside content_area so it doesn't overlap sidebar) ---
        self._build_log_panel(self.content_area)
        
        # --- STATUS BAR ---
        tr = self.translator.get
        version_label = tr("version", APP_VERSION)
        status_labels = {
            "status_ready": tr("status_ready", "Ready"),
            "login_not_logged": f"YouTube — {tr('status_not_logged_in', 'not signed in')}",
            "login_logged_prefix": tr("status_logged_in", "Logged in as"),
            "version_label": f"v{version_label}",
        }
        self.status_bar = StatusBar(root_frame, theme=self.theme, labels=status_labels, design=self.design)
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
        """Build the premium sidebar navigation with refined visual hierarchy"""
        tr = self.translator.get
        bg = self.design.get_color("sidebar_bg")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        fg_ter = self.design.get_color("fg_tertiary")
        accent = self.design.get_color("accent_primary")
        hover_bg = self.design.get_color("sidebar_item_hover")
        active_bg = self.design.get_color("sidebar_item_active")
        border_color = self.design.get_color("sidebar_border")
        
        # Toggle button area — clean hamburger
        toggle_frame = tk.Frame(self.sidebar_frame, bg=bg)
        toggle_frame.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.MD, Spacing.XS))
        
        self.sidebar_toggle_btn = tk.Label(
            toggle_frame, text="☰", bg=bg, fg=fg_ter,
            font=(Typography.FONT_FAMILY, 16), cursor="hand2"
        )
        self.sidebar_toggle_btn.pack(anchor="w", padx=Spacing.XS)
        self.sidebar_toggle_btn.bind("<Button-1>", lambda e: self._toggle_sidebar())
        self.sidebar_toggle_btn.bind("<Enter>", lambda e: self.sidebar_toggle_btn.config(fg=accent))
        self.sidebar_toggle_btn.bind("<Leave>", lambda e: self.sidebar_toggle_btn.config(fg=fg_ter))
        
        # Section label — uppercase tracking
        self._nav_section_label = tk.Label(
            self.sidebar_frame, text=tr("sidebar_navigation", "NAVIGATION").upper(),
            bg=bg, fg=fg_ter,
            font=(Typography.FONT_FAMILY, Typography.SIZE_TINY, "bold"),
            anchor="w"
        )
        self._nav_section_label.pack(fill=tk.X, padx=(Spacing.XL, Spacing.MD), pady=(Spacing.MD, Spacing.XS))
        
        # Separator under label (stored so we can hide on collapse)
        self._nav_section_separator = tk.Frame(self.sidebar_frame, bg=border_color, height=1)
        self._nav_section_separator.pack(fill=tk.X, padx=Spacing.LG, pady=(0, Spacing.SM))
        
        # Navigation items with SVG icons and color accents
        nav_items = [
            ("download", "download",    "icon_accent",  tr("tab_download", "Download")),
            ("batch",    "layers",      "icon_purple",  tr("tab_batch", "Batch")),
            ("live",     "radio",       "icon_red",     tr("tab_live", "Live")),
            ("following","eye",         "icon_cyan",    tr("tab_following", "Following")),
            ("history",  "clipboard",   "icon_orange",  tr("tab_history", "History")),
            ("settings", "settings",    "icon_muted",   tr("tab_settings", "Settings")),
            ("about",    "info",        "icon_accent",  tr("tab_about", "About")),
        ]
        
        # Emoji fallbacks in case SVG fails
        _emoji_fallback = {
            "download": "⬇️", "layers": "📦", "radio": "🔴",
            "eye": "👁️", "clipboard": "📜", "settings": "⚙️", "info": "ℹ️",
        }
        
        self._nav_container = tk.Frame(self.sidebar_frame, bg=bg)
        nav_container = self._nav_container
        nav_container.pack(fill=tk.X)
        
        self._sidebar_icon_refs = []  # Prevent GC of icon images
        
        # Icon column is fixed-width so icons stay in the same position
        # whether the sidebar is expanded (220px) or collapsed (56px).
        # collapsed = padx(SM=8) on each side + icon(28) + internal = ~48px centered in 56
        _ICON_COL_WIDTH = 40  # fixed icon column width
        
        for key, icon_name, icon_color_key, label in nav_items:
            # Outer wrapper for nav item
            btn_frame = tk.Frame(nav_container, bg=bg, cursor="hand2")
            btn_frame.pack(fill=tk.X, pady=Spacing.XXS)
            btn_frame.pack_propagate(False)
            btn_frame.config(height=40)
            # Column 0 = indicator (3px fixed), Column 1 = icon (fixed), Column 2 = text (stretches)
            btn_frame.grid_columnconfigure(0, minsize=3)
            btn_frame.grid_columnconfigure(1, minsize=_ICON_COL_WIDTH)
            btn_frame.grid_columnconfigure(2, weight=1)
            
            # Active indicator (left accent bar — 3px)
            indicator = tk.Frame(btn_frame, bg=bg, width=3)
            indicator.grid(row=0, column=0, sticky="ns")
            
            # Try SVG icon first, fallback to emoji
            icon_color = self.design.get_color(icon_color_key)
            svg_icon = render_feather_icon(icon_name, size=18, color=icon_color) if _HAS_SVG else None
            
            if svg_icon:
                icon_lbl = tk.Label(
                    btn_frame, image=svg_icon, bg=bg,
                    anchor="center"
                )
                icon_lbl._icon_ref = svg_icon
                self._sidebar_icon_refs.append(svg_icon)
            else:
                emoji = _emoji_fallback.get(icon_name, "●")
                icon_lbl = tk.Label(
                    btn_frame, text=emoji, bg=bg, fg=fg,
                    font=("Segoe UI Emoji", 14),
                    anchor="center"
                )
            icon_lbl.grid(row=0, column=1, sticky="nsew", pady=Spacing.XS)
            
            # Label with medium weight
            text_lbl = tk.Label(
                btn_frame, text=label, bg=bg, fg=fg_sec,
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                anchor="w"
            )
            text_lbl.grid(row=0, column=2, sticky="w", padx=(Spacing.XS, 0), pady=Spacing.XS)
            
            # Store refs
            self.nav_buttons[key] = {
                "frame": btn_frame,
                "indicator": indicator,
                "icon": icon_lbl,
                "text": text_lbl,
            }
            
            # Click + hover bindings
            for widget in (btn_frame, icon_lbl, text_lbl):
                widget.bind("<Button-1>", lambda e, k=key: self._switch_section(k))
                widget.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
                widget.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))
        
        # Footer — packed right after nav items (no side=BOTTOM gap)
        footer = tk.Frame(self.sidebar_frame, bg=bg)
        footer.pack(fill=tk.X, padx=Spacing.SM, pady=(Spacing.SM, Spacing.SM))

        # Separator above footer
        tk.Frame(footer, bg=border_color, height=1).pack(fill=tk.X, pady=(0, Spacing.SM))

        # Folder buttons
        open_label = tr("header_open_folder", "Open Folder")
        select_label = tr("header_select_folder", "Select Folder")

        # Open Folder
        open_btn_frame = tk.Frame(footer, bg=bg)
        open_btn_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
        
        open_btn = ModernButton(
            open_btn_frame, text=open_label,
            icon_name="folder", command=self.open_output_folder,
            variant="outline", width=18
        )
        open_btn.pack(fill=tk.X)
        Tooltip(open_btn, text=tr("tooltip_open_folder", "Open download folder in file explorer"), design=self.design)
        
        # Icon-only version for collapsed state
        open_icon = get_ui_icon("folder", size=20)
        open_icon_lbl = tk.Label(
            open_btn_frame, image=open_icon, bg=bg, 
            cursor="hand2", borderwidth=0, relief="flat",
            highlightthickness=1, highlightbackground=border_color,
            padx=Spacing.SM, pady=Spacing.SM
        )
        open_icon_lbl.image = open_icon
        open_icon_lbl.bind("<Button-1>", lambda e: self.open_output_folder())
        open_icon_lbl.bind("<Enter>", lambda e: open_icon_lbl.config(bg=hover_bg))
        open_icon_lbl.bind("<Leave>", lambda e: open_icon_lbl.config(bg=bg))
        
        # Select Folder
        select_btn_frame = tk.Frame(footer, bg=bg)
        select_btn_frame.pack(fill=tk.X)
        
        select_btn = ModernButton(
            select_btn_frame, text=select_label,
            icon_name="folder-plus", command=self.select_output_folder,
            variant="outline", width=18
        )
        select_btn.pack(fill=tk.X)
        Tooltip(select_btn, text=tr("tooltip_select_folder", "Choose a different download folder"), design=self.design)
        
        # Icon-only version for collapsed
        select_icon = get_ui_icon("folder-plus", size=20)
        select_icon_lbl = tk.Label(
            select_btn_frame, image=select_icon, bg=bg,
            cursor="hand2", borderwidth=0, relief="flat",
            highlightthickness=1, highlightbackground=border_color,
            padx=Spacing.SM, pady=Spacing.SM
        )
        select_icon_lbl.image = select_icon
        select_icon_lbl.bind("<Button-1>", lambda e: self.select_output_folder())
        select_icon_lbl.bind("<Enter>", lambda e: select_icon_lbl.config(bg=hover_bg))
        select_icon_lbl.bind("<Leave>", lambda e: select_icon_lbl.config(bg=bg))

        # Version label  
        version_lbl = tk.Label(
            footer, text=f"v{tr('version', APP_VERSION)}", bg=bg,
            fg=fg_ter,
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
        """Switch active content section with visual feedback"""
        self.active_section = key
        bg = self.design.get_color("sidebar_bg")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        accent = self.design.get_color("accent_primary")
        active_bg = self.design.get_color("sidebar_item_active")
        
        # Update sidebar visuals
        for k, refs in self.nav_buttons.items():
            if k == key:
                refs["indicator"].config(bg=accent)
                refs["frame"].config(bg=active_bg)
                refs["icon"].config(bg=active_bg)
                refs["text"].config(bg=active_bg, fg=fg)
            else:
                refs["indicator"].config(bg=bg)
                refs["frame"].config(bg=bg)
                refs["icon"].config(bg=bg)
                refs["text"].config(bg=bg, fg=fg_sec)
        
        # Switch visible section frame
        frame = self.section_frames.get(key)
        if frame:
            frame.tkraise()
        # Reset notification bell when user navigates to Following tab (Issue #64)
        if key == "following":
            self._bell_count = 0
            if hasattr(self, '_bell_label'):
                self._bell_label.config(text="🔔")
    
    def _nav_hover(self, key, entering):
        """Handle sidebar nav hover effects"""
        if key == self.active_section:
            return
        refs = self.nav_buttons[key]
        bg = self.design.get_color("sidebar_bg")
        hover_bg = self.design.get_color("sidebar_item_hover")
        color = hover_bg if entering else bg
        refs["frame"].config(bg=color)
        refs["icon"].config(bg=color)
        refs["text"].config(bg=color)
    
    def _toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed with animation.
        
        Icons stay at the exact same screen position in both modes.
        Expanding only reveals text beside the icons.
        Grid column config never changes — col0=3px, col1=40px, col2=stretch.
        """
        self.sidebar_expanded = not self.sidebar_expanded
        bg = self.design.get_color("sidebar_bg")
        if self.sidebar_expanded:
            self.sidebar_frame.config(width=220)
            for refs in self.nav_buttons.values():
                # Show indicator and text — grid columns unchanged
                refs["indicator"].grid(row=0, column=0, sticky="ns")
                refs["text"].grid(row=0, column=2, sticky="w", padx=(Spacing.XS, 0), pady=Spacing.XS)
            
            # Restore hamburger to left-aligned
            self.sidebar_toggle_btn.pack_configure(anchor="w", padx=Spacing.XS)
            
            # Restore section label and separator visibility (keep space, just show content)
            if hasattr(self, '_nav_section_label'):
                self._nav_section_label.config(fg=self.design.get_color("fg_tertiary"))
            if hasattr(self, '_nav_section_separator'):
                self._nav_section_separator.config(bg=self.design.get_color("sidebar_border"))

            # Show buttons, hide icon labels
            for data in ("open", "select"):
                self.footer_buttons[data]["button"].pack(fill=tk.X)
                self.footer_buttons[data]["icon_label"].pack_forget()

            self.footer_buttons["version"].pack_configure(anchor="w")
        else:
            self.sidebar_frame.config(width=56)
            for refs in self.nav_buttons.values():
                # Hide text and indicator — grid columns stay the same
                # so icons remain at the exact same x position
                refs["text"].grid_remove()
                refs["indicator"].grid_remove()
            
            # Make section label and separator invisible but keep their space
            # so nav items stay at the same vertical position
            if hasattr(self, '_nav_section_label'):
                self._nav_section_label.config(fg=bg)
            if hasattr(self, '_nav_section_separator'):
                self._nav_section_separator.config(bg=bg)

            # Center the hamburger toggle
            self.sidebar_toggle_btn.pack_configure(anchor="center", padx=0)

            # Hide buttons, show centered icon labels
            for data in ("open", "select"):
                self.footer_buttons[data]["button"].pack_forget()
                self.footer_buttons[data]["icon_label"].pack(pady=Spacing.XS, anchor="center")

            self.footer_buttons["version"].pack_configure(anchor="center")
    
    # ──────────────────────────────────────────
    # LOG PANEL (collapsible)
    # ──────────────────────────────────────────
    
    def _build_log_panel(self, parent):
        """Build premium collapsible log panel at bottom"""
        self.log_panel_visible = False
        tr = self.translator.get
        
        # Toggle bar with subtle styling
        bar_bg = self.design.get_color("bg_secondary")
        bar_fg = self.design.get_color("fg_tertiary")
        border = self.design.get_color("border_subtle")
        
        # Top border
        tk.Frame(parent, bg=border, height=1).pack(fill=tk.X)
        
        self.log_toggle_bar = tk.Frame(parent, bg=bar_bg, height=28, cursor="hand2")
        self.log_toggle_bar.pack(fill=tk.X)
        self.log_toggle_bar.pack_propagate(False)
        
        toggle_content = tk.Frame(self.log_toggle_bar, bg=bar_bg)
        toggle_content.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD)
        
        # Left: chevron + label
        self._log_chevron = tk.Label(
            toggle_content, text="▴", bg=bar_bg, fg=bar_fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION)
        )
        self._log_chevron.pack(side=tk.LEFT)
        
        toggle_label = tk.Label(
            toggle_content, text=f" {tr('log_panel_title', 'Activity Log')}", bg=bar_bg,
            fg=bar_fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION),
            cursor="hand2"
        )
        toggle_label.pack(side=tk.LEFT)

        # Right: shortcut hint (fixed to match actual binding Ctrl+Shift+L — Issue #38)
        tk.Label(
            toggle_content, text="Ctrl+Shift+L", bg=bar_bg,
            fg=self.design.get_color("fg_disabled") if self.dark_mode else self.design.get_color("fg_tertiary"),
            font=(Typography.FONT_MONO, Typography.SIZE_TINY)
        ).pack(side=tk.RIGHT)
        # Tooltip clarifying what the log shows (Issue #12)
        Tooltip(self.log_toggle_bar,
                text=tr("tooltip_log_panel",
                        "Activity Log — shows download progress, errors and status messages"),
                design=self.design)
        
        for w in (self.log_toggle_bar, toggle_label, self._log_chevron, toggle_content):
            w.bind("<Button-1>", lambda e: self._toggle_log_panel())
        
        # Log content frame
        self.log_panel = tk.Frame(parent, bg=bar_bg)
        
        self.global_log = LogWidget(self.log_panel, theme=self.design, design=self.design, height=8)
        self.global_log.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Alias per-section logs to the global log (Issues #49, #65, #67)
        self.download_log = self.global_log
        self.batch_log = self.global_log
        self.live_log = self.global_log
        self.following_log = self.global_log
    
    def _toggle_log_panel(self):
        """Toggle log panel visibility"""
        self.log_panel_visible = not self.log_panel_visible
        if self.log_panel_visible:
            self.log_panel.pack(fill=tk.X, before=self.log_toggle_bar)
            self._log_chevron.config(text="▾")
        else:
            self.log_panel.pack_forget()
            self._log_chevron.config(text="▴")
    
    # ──────────────────────────────────────────
    # KEYBOARD SHORTCUTS
    # ──────────────────────────────────────────
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # Theme / UI toggles
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.root.bind("<Control-Shift-L>", lambda e: self._toggle_log_panel())
        self.root.bind("<Control-o>", lambda e: self.open_output_folder())
        # Tab navigation — letters (primary) and numbers (secondary)
        self.root.bind("<Control-d>", lambda e: self._switch_section("download"))
        self.root.bind("<Control-b>", lambda e: self._switch_section("batch"))
        self.root.bind("<Control-l>", lambda e: self._switch_section("live"))
        self.root.bind("<Control-h>", lambda e: self._switch_section("history"))
        self.root.bind("<Control-Key-1>", lambda e: self._switch_section("download"))
        self.root.bind("<Control-Key-2>", lambda e: self._switch_section("batch"))
        self.root.bind("<Control-Key-3>", lambda e: self._switch_section("live"))
        self.root.bind("<Control-Key-4>", lambda e: self._switch_section("history"))
        self.root.bind("<Control-Key-5>", lambda e: self._switch_section("about"))
        self.root.bind("<Escape>", lambda e: self._on_escape())
    
    def _on_escape(self):
        """Handle Escape key: stop active download/recording, or hide log panel"""
        if self.is_recording:  # Issue #46/#53: recording is now independent from downloading
            self.stop_live_recording()
        elif self.is_downloading:
            self.stop_download()
        elif self.log_panel_visible:
            self._toggle_log_panel()
    
    def create_header(self, parent):
        """Create premium 52px header — Logo + Title + Controls with gradient accent"""
        tr = self.translator.get
        bg = self.design.get_color("header_bg")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        accent = self.design.get_color("accent_primary")
        
        header = tk.Frame(parent, bg=bg, height=52)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        self._header_gradient_refs = []  # Prevent GC
        
        inner = tk.Frame(header, bg=bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=0)
        
        # Left: Icon + Title + Version badge
        left = tk.Frame(inner, bg=bg)
        left.pack(side=tk.LEFT, fill=tk.Y)
        
        # App icon — try SVG scissors first, then PIL .ico, then emoji
        app_icon_placed = False
        if _HAS_SVG:
            svg_icon = render_feather_icon("scissors", size=24, color=accent)
            if svg_icon:
                icon_label = tk.Label(left, image=svg_icon, bg=bg)
                icon_label.image = svg_icon
                icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
                app_icon_placed = True
        
        if not app_icon_placed:
            try:
                from PIL import Image, ImageTk
                icon_path = Path(__file__).parent.parent / "assets" / "headerapp_icon.ico"
                if icon_path.exists():
                    img = Image.open(icon_path)
                    img = img.resize((28, 28), Image.Resampling.LANCZOS)
                    app_icon = ImageTk.PhotoImage(img)
                    icon_label = tk.Label(left, image=app_icon, bg=bg)
                    icon_label.image = app_icon
                    icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
                    app_icon_placed = True
            except Exception:
                pass
        
        if not app_icon_placed:
            tk.Label(left, text="✂️", bg=bg, font=("Segoe UI Emoji", 16)).pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        tk.Label(
            left, text="EasyCut", bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H2, "bold")
        ).pack(side=tk.LEFT)
        
        # Version badge — purple variant for visual variety
        Badge(
            left, text="v1.9", variant="purple", design=self.design, size="sm"
        ).pack(side=tk.LEFT, padx=(Spacing.SM, 0), pady=(Spacing.XS, 0))
        
        # Right: Controls
        right = tk.Frame(inner, bg=bg)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Language selector — custom dropdown with PIL-drawn flag images
        # (Windows Tk/GDI cannot render regional indicator flag emoji natively,
        #  and PIL also fails to compose the 2-codepoint ligatures into color flags.
        #  Solution: draw simplified geometric flags using PIL primitives.)
        lang_options = [
            ("en", "English"),
            ("pt", "Português"),
            ("es", "Español"),
            ("fr", "Français"),
            ("de", "Deutsch"),
            ("it", "Italiano"),
            ("ja", "日本語"),
        ]
        current_index = next((i for i, (c, _) in enumerate(lang_options) if c == self.language), 0)
        
        # Draw flag images with PIL geometric shapes
        self._lang_flag_images = {}  # prevent GC
        try:
            from PIL import Image, ImageDraw, ImageTk
            for code, _ in lang_options:
                self._lang_flag_images[code] = ImageTk.PhotoImage(self._draw_flag(code))
        except Exception:
            self._lang_flag_images = {}
        
        # Button that shows current language + flag
        cur_code, cur_name = lang_options[current_index]
        lang_btn_bg = self.design.get_color("bg_tertiary")
        lang_btn_hover = self.design.get_color("bg_hover")
        lang_btn_fg = self.design.get_color("fg_secondary")
        lang_btn_border = self.design.get_color("border_subtle")
        
        self._lang_btn = tk.Frame(right, bg=lang_btn_bg, cursor="hand2",
                                   highlightthickness=1, highlightbackground=lang_btn_border)
        self._lang_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        
        if cur_code in self._lang_flag_images:
            self._lang_flag_label = tk.Label(self._lang_btn, image=self._lang_flag_images[cur_code],
                                              bg=lang_btn_bg)
            self._lang_flag_label.pack(side=tk.LEFT, padx=(Spacing.XS, 2))
        else:
            self._lang_flag_label = None
        
        self._lang_text_label = tk.Label(
            self._lang_btn, text=cur_name, bg=lang_btn_bg, fg=lang_btn_fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_SM)
        )
        self._lang_text_label.pack(side=tk.LEFT, padx=(0, 2))
        
        # Dropdown arrow
        tk.Label(self._lang_btn, text="▾", bg=lang_btn_bg, fg=lang_btn_fg,
                 font=(Typography.FONT_FAMILY, 8)).pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        # Store options for dropdown
        self._lang_options = lang_options
        self._lang_btn_bg = lang_btn_bg
        self._lang_btn_hover = lang_btn_hover
        
        # Bind click to open dropdown
        for widget in (self._lang_btn, self._lang_text_label):
            widget.bind("<Button-1>", lambda e: self._open_lang_dropdown())
        if self._lang_flag_label:
            self._lang_flag_label.bind("<Button-1>", lambda e: self._open_lang_dropdown())
        
        # Hover effect
        def _lang_enter(e):
            for w in (self._lang_btn, self._lang_text_label):
                w.configure(bg=lang_btn_hover)
            if self._lang_flag_label:
                self._lang_flag_label.configure(bg=lang_btn_hover)
        def _lang_leave(e):
            for w in (self._lang_btn, self._lang_text_label):
                w.configure(bg=lang_btn_bg)
            if self._lang_flag_label:
                self._lang_flag_label.configure(bg=lang_btn_bg)
        for widget in (self._lang_btn, self._lang_text_label):
            widget.bind("<Enter>", _lang_enter)
            widget.bind("<Leave>", _lang_leave)
        if self._lang_flag_label:
            self._lang_flag_label.bind("<Enter>", _lang_enter)
            self._lang_flag_label.bind("<Leave>", _lang_leave)
        
        Tooltip(self._lang_btn, text=tr("tooltip_language", "Change application language"), design=self.design)
        
        # Theme toggle — moon (dark mode) / sun (light mode) with strong accent border
        theme_icon_name = "moon" if self.dark_mode else "sun"
        theme_icon_color = self.design.get_color("purple_primary") if self.dark_mode else self.design.get_color("orange_primary")
        # bg_secondary is too close to header in dark mode; use bg_tertiary for clear contrast
        btn_pill_bg = self.design.get_color("bg_tertiary")
        btn_pill_hover = self.design.get_color("bg_hover")
        # Use the accent color as border so the button is unmistakably visible
        btn_pill_border = self.design.get_color("purple_primary") if self.dark_mode else self.design.get_color("orange_primary")
        
        # Use emoji 🌙/☀️ so the icon is always clearly visible
        # (SVG stroke-only icon is too thin/invisible on dark backgrounds)
        theme_emoji = "🌙" if self.dark_mode else "☀️"
        theme_btn = tk.Label(
            right, text=theme_emoji, bg=btn_pill_bg,
            fg=theme_icon_color, font=("Segoe UI Emoji", 13), cursor="hand2",
            padx=Spacing.SM, pady=Spacing.XXS,
            highlightthickness=1, highlightbackground=btn_pill_border
        )
        theme_btn.pack(side=tk.RIGHT, padx=Spacing.XS)
        theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())
        Tooltip(theme_btn, text=tr("tooltip_theme", "Toggle dark/light theme (Ctrl+T)"), design=self.design)
        
        # Hover effects for theme button
        theme_btn.bind("<Enter>", lambda e: theme_btn.config(bg=btn_pill_hover))
        theme_btn.bind("<Leave>", lambda e: theme_btn.config(bg=btn_pill_bg))
        
        # Notification bell — shows new video count from followed channels (Issue #64)
        bell_count = getattr(self, '_bell_count', 0)
        bell_text = f"🔔 {bell_count}" if bell_count > 0 else "🔔"
        self._bell_label = tk.Label(
            right, text=bell_text, bg=btn_pill_bg,
            fg=fg_sec, font=("Segoe UI Emoji", 13), cursor="hand2",
            padx=Spacing.SM, pady=Spacing.XXS
        )
        self._bell_label.pack(side=tk.RIGHT, padx=Spacing.XS)
        self._bell_label.bind("<Button-1>", lambda e: self._switch_section("following"))
        self._bell_label.bind("<Enter>", lambda e: self._bell_label.config(bg=btn_pill_hover))
        self._bell_label.bind("<Leave>", lambda e: self._bell_label.config(bg=btn_pill_bg))
        Tooltip(self._bell_label, text=tr("tooltip_bell", "New videos from followed channels — click to open Following tab"), design=self.design)
        
        # Bottom border — gradient line (blue → purple)
        if _HAS_SVG:
            grad_canvas = tk.Canvas(parent, height=2, highlightthickness=0, bg=bg)
            grad_canvas.pack(fill=tk.X)
            grad_start = self.design.get_color("accent_gradient_start")
            grad_end = self.design.get_color("accent_gradient_end")
            def _draw_header_gradient(e, c=grad_canvas, s=grad_start, en=grad_end):
                c.delete("all")
                g = create_gradient_image(e.width, 2, s, en, "horizontal")
                if g:
                    c.create_image(0, 0, anchor="nw", image=g)
                    self._header_gradient_refs.append(g)
            grad_canvas.bind("<Configure>", _draw_header_gradient)
        else:
            tk.Frame(parent, bg=self.design.get_color("header_border"), height=1).pack(fill=tk.X)
    
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
            text=tr("yt_auth_title", "YouTube Authentication"),
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_H3, "bold")
        ).pack(anchor="w", pady=(0, Spacing.XS))
        
        # Info text
        info_text = tr(
            "yt_auth_info",
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
                    tr("msg_info", "Info"),
                    tr("yt_already_auth", "Already authenticated! Re-authenticate?")
                )
                if not result:
                    return
            
            # Show loading state
            sync_btn.config(state="disabled")
            self.account_status_label.config(
                text=tr("yt_opening_browser", "Opening browser..."),
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
                                text=tr("yt_auth_success", "✓ Authenticated! Ready to download"),
                                fg=self.design.get_color("success")
                            )
                            if hasattr(self, 'download_log') and self.download_log:
                                self.download_log.add_log(tr("yt_auth_log_success", "✓ YouTube authentication successful!"))
                            # Update status bar + logout button visibility
                            self.root.after(0, self.update_login_status)
                        else:
                            self.account_status_label.config(
                                text=tr("yt_auth_cookie_fail", "✗ Failed to get cookies"),
                                fg=self.design.get_color("error")
                            )
                    else:
                        self.account_status_label.config(
                            text=tr("yt_auth_failed", "✗ Authentication failed"),
                            fg=self.design.get_color("error")
                        )
                
                except OAuthError as e:
                    # User-friendly OAuth error messages
                    error_msg = str(e)
                    self.account_status_label.config(
                        text=tr("yt_auth_oauth_error", "✗ OAuth Error (see popup)"),
                        fg=self.design.get_color("error")
                    )
                    # Show detailed error in popup
                    self.root.after(0, lambda: messagebox.showerror(tr("yt_auth_oauth_title", "OAuth Error"), error_msg))
                    if hasattr(self, 'download_log') and self.download_log:
                        self.download_log.add_log(tr("yt_auth_log_error", "OAuth error - check popup for details"), "ERROR")
                
                
                finally:
                    sync_btn.config(state="normal")
            
            thread = threading.Thread(target=auth_thread, daemon=True)
            thread.start()
        
        sync_btn = ModernButton(
            control_frame,
            text=tr("yt_sync_btn", "Sync with YouTube"),
            icon_name="log-in",
            command=handle_sync,
            variant="primary",
            size="sm",
            width=18
        )
        sync_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Logout button — only shown when authenticated
        def handle_logout():
            """Handle logout"""
            result = messagebox.askyesno(
                tr("msg_confirm", "Confirm"),
                tr("yt_logout_confirm", "Remove YouTube authentication?")
            )
            if result:
                self.oauth_manager.logout()
                # Also delete any yt_cookies.txt so yt-dlp stops using stale auth
                try:
                    cookies_path = Path("config") / "yt_cookies.txt"
                    if cookies_path.exists():
                        cookies_path.unlink()
                except Exception:
                    pass
                self.account_status_label.config(
                    text=tr("yt_not_authenticated", "Not authenticated"),
                    fg=self.design.get_color("fg_secondary")
                )
                if hasattr(self, 'download_log') and self.download_log:
                    self.download_log.add_log(tr("yt_logged_out", "Logged out from YouTube"))
                # Update UI state (hide logout, update status)
                self.update_login_status()
        
        self._logout_btn_widget = ModernButton(
            control_frame,
            text=tr("yt_logout_btn", "Logout"),
            icon_name="log-out",
            command=handle_logout,
            variant="ghost",
            size="sm",
            width=10
        )
        # Only show logout button if already authenticated
        if self.oauth_manager.is_authenticated():
            self._logout_btn_widget.pack(side=tk.LEFT)
        
        # Account Status
        status_frame = tk.Frame(banner, bg=bg)
        status_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        tk.Label(
            status_frame,
            text=tr("yt_status_label", "Status:"),
            bg=bg, fg=fg_sec,
            font=(Typography.FONT_FAMILY, Typography.SIZE_CAPTION, "bold")
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Status label
        if self.oauth_manager.is_authenticated():
            status_text = tr("yt_auth_ready", "✓ Authenticated and ready")
            status_color = self.design.get_color("success")
        else:
            status_text = tr("yt_not_authenticated", "Not authenticated yet")
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
        """Create download section — professional visual polish"""
        tr = self.translator.get
        
        # Create tab
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable container
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        main = scroll.interior
        main.configure(padding=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("tab_download", "Download"),
            subtitle=tr("download_subtitle", "Download videos and audio from YouTube"),
            icon="download"
        ).pack(fill=tk.X, pady=(0, Spacing.LG))
        
        # === URL INPUT CARD ===
        url_card = ModernCard(main, title=tr("download_url", "YouTube URL"), design=self.design, accent_top=True)
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
        
        self.download_url_entry = ModernEntry(
            input_frame, placeholder=tr("download_url_placeholder", "Paste YouTube URL here..."),
            design=self.design
        )
        self.download_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Enter key triggers Verify (Issue #18)
        self.download_url_entry.bind("<Return>", lambda e: self.verify_video())
        # Right-click context menu (Issue #17)
        def _show_url_context_menu(event):
            _cm = tk.Menu(self.root, tearoff=0)
            _cm.configure(
                bg=self.design.get_color("bg_secondary"),
                fg=self.design.get_color("fg_primary"),
                activebackground=self.design.get_color("accent_primary"),
                activeforeground=self.design.get_color("fg_on_accent"),
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                bd=0, relief="flat"
            )
            _cm.add_command(label=tr("ctx_copy", "Copy"),
                           command=lambda: self.download_url_entry.event_generate("<<Copy>>"))
            _cm.add_command(label=tr("ctx_paste", "Paste"),
                           command=lambda: self.download_url_entry.event_generate("<<Paste>>"))
            _cm.add_command(label=tr("ctx_select_all", "Select All"),
                           command=lambda: self.download_url_entry.select_range(0, tk.END))
            _cm.add_separator()
            _cm.add_command(label=tr("ctx_clear", "Clear"),
                           command=lambda: self.download_url_entry.delete(0, tk.END))
            try:
                _cm.tk_popup(event.x_root, event.y_root)
            finally:
                _cm.grab_release()
        self.download_url_entry.bind("<Button-3>", _show_url_context_menu)

        # Verify button
        verify_btn = ModernButton(
            url_container,
            text=tr("download_verify", "Verify"),
            icon_name="verify",
            command=self.verify_video,
            variant="outline",
            size="sm",
            width=10
        )
        verify_btn.pack(side=tk.LEFT)
        Tooltip(verify_btn, text=tr("tooltip_verify", "Verify URL and fetch video metadata"), design=self.design)
        
        # === VIDEO INFO CARD (Metadata + Thumbnail) ===
        info_card = ModernCard(main, title=tr("download_info", "Video Information"), design=self.design, hoverable=True)
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
        # Follow Channel button — hidden until verify populates uploader (Issue #19)
        self._follow_channel_btn = ModernButton(
            info_grid,
            text=f"\u2795 {tr('follow_channel_btn', 'Follow')}",
            command=self._follow_channel_from_download,
            variant="ghost",
            size="sm",
            width=8
        )
        Tooltip(self._follow_channel_btn,
                text=tr("tooltip_follow_channel", "Add this channel to Following list"),
                design=self.design)
        # Initially hidden; shown by verify_thread when uploader_url is available

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
        
        # === UNIFIED FORMAT & QUALITY CARD (merged from two cards — Fix #20) ===
        format_card = ModernCard(main, title=tr("format_quality_title", "Format & Quality"), design=self.design, hoverable=True)
        format_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        # keep reference for later hiding/showing quality block
        self.format_card = format_card

        # --- Quality presets row ---
        quality_frame = ttk.Frame(format_card.body)
        quality_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        ttk.Label(quality_frame, text=f"{tr('quality_label', 'Quality')}:", style="Caption.TLabel").pack(
            side=tk.LEFT, padx=(0, Spacing.SM)
        )
        self._quality_radios = []
        for qval, qlabel in [
            ("best", tr("quality_best", "Best")),
            ("1080", "1080p"),
            ("720", "720p"),
            ("mp4", "MP4"),
            ("audio", tr("quality_audio", "Audio")),
        ]:
            rb = ttk.Radiobutton(quality_frame, text=qlabel, variable=self.download_quality_var, value=qval)
            rb.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            self._quality_radios.append(rb)

        # --- Specific format (populated after Verify — advanced override) ---
        Separator(format_card.body, design=self.design).pack(fill=tk.X, pady=(Spacing.SM, Spacing.SM))

        format_container = ttk.Frame(format_card.body)
        format_container.pack(fill=tk.X)

        ttk.Label(format_container, text=f"{tr('format_select', 'Specific Format')}:", style="Caption.TLabel").pack(
            side=tk.LEFT, padx=(0, Spacing.SM)
        )

        self.format_var = tk.StringVar(value="auto")
        self.format_combo = ttk.Combobox(
            format_container,
            textvariable=self.format_var,
            state="readonly",
            width=55
        )
        self.format_combo['values'] = [tr("format_auto", "Auto (Best)")]
        self.format_combo.current(0)
        self.format_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        # wire up interactions so choosing a specific format disables the
        # quality presets and vice-versa
        self.format_combo.bind('<<ComboboxSelected>>', self._on_format_selected)
        # still trace quality changes for config persistence
        self.download_quality_var.trace_add('write', lambda *args: self._on_quality_change())

        self.format_status_label = ttk.Label(format_card.body,
            text=tr("format_status_hint", "Verify a URL above to see available formats"),
            style="Caption.TLabel")
        self.format_status_label.pack(anchor=tk.W, pady=(Spacing.XS, 0))
        
        # === DOWNLOAD MODE CARD ===
        mode_card = ModernCard(main, title=tr("download_mode", "Download Mode"), design=self.design, hoverable=True)
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
        
        # Channel limit control (shown below mode grid)
        channel_limit_frame = ttk.Frame(mode_card.body)
        channel_limit_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        ttk.Label(
            channel_limit_frame,
            text=f"{tr('channel_limit', 'Latest videos')}:",
            style="Caption.TLabel"
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self._channel_limit_var = tk.IntVar(value=10)
        channel_spinbox = ttk.Spinbox(
            channel_limit_frame,
            from_=1, to=500,
            textvariable=self._channel_limit_var,
            width=6
        )
        channel_spinbox.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        ttk.Label(
            channel_limit_frame,
            text=tr('channel_limit_help', 'Number of latest videos to download (1-500)'),
            style="Caption.TLabel"
        ).pack(side=tk.LEFT)
        
        # === TIME RANGE CARD ===
        time_card = ModernCard(main, title=tr("download_time_range", "Time Range"), design=self.design)
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
        
        # === AUDIO FORMAT CARD (applies when mode = Audio Only) ===
        audio_card = ModernCard(main, title=f"{tr('audio_format', 'Audio Format')} — {tr('download_mode_audio', 'Audio Only')}", design=self.design)
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
        
        # === SUBTITLE CARD ===
        sub_card = ModernCard(main, title=tr("sub_title", "Subtitles"), design=self.design)
        sub_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Enable subtitles checkbox
        self.sub_enable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sub_card.body,
            text=tr("sub_enable", "Download Subtitles"),
            variable=self.sub_enable_var
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Transcript download button (TXT with timestamps)
        tr_btn = ModernButton(
            sub_card.body,
            text=tr("download_transcript_btn", "Download Transcript"),
            command=self.download_transcript,
            variant="outline",
            size="sm"
        )
        tr_btn.pack(anchor=tk.W, pady=(Spacing.SM, 0))
        Tooltip(tr_btn, text=tr("tooltip_download_transcript", "Download subtitle transcript with timestamps (TXT)"), design=self.design)
        
        # Subtitle type
        sub_type_frame = ttk.Frame(sub_card.body)
        sub_type_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        self.sub_type_var = tk.StringVar(value="auto")
        for value, text in [("auto", tr("sub_auto", "Auto-generated")), ("manual", tr("sub_manual", "Manual")), ("both", tr("sub_both", "Both"))]:
            ttk.Radiobutton(sub_type_frame, text=text, variable=self.sub_type_var, value=value).pack(side=tk.LEFT, padx=(0, Spacing.LG))
        
        # Language selection — common presets as checkbuttons + custom free text
        lang_frame = ttk.Frame(sub_card.body)
        lang_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
        ttk.Label(lang_frame, text=f"{tr('sub_language', 'Language')}:", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, Spacing.XS))

        # Quick preset row
        sub_lang_presets = [
            ("en", "English"), ("pt", "Português"), ("es", "Español"),
            ("fr", "Français"), ("de", "Deutsch"), ("ja", "日本語"),
        ]
        self._sub_lang_vars = {code: tk.BooleanVar(value=(code == "en")) for code, _ in sub_lang_presets}

        def _update_sub_lang_entry():
            selected = [code for code, var in self._sub_lang_vars.items() if var.get()]
            custom = self.sub_lang_entry.get().strip()
            # Remove preset codes from custom field, then merge
            custom_codes = [c.strip() for c in custom.split(",") if c.strip() and c.strip() not in self._sub_lang_vars]
            all_codes = selected + custom_codes
            self.sub_lang_entry.delete(0, tk.END)
            self.sub_lang_entry.insert(0, ", ".join(all_codes))

        preset_row = ttk.Frame(lang_frame)
        preset_row.pack(fill=tk.X, pady=(0, Spacing.XS))
        for code, name in sub_lang_presets:
            ttk.Checkbutton(
                preset_row, text=f"{name} ({code})",
                variable=self._sub_lang_vars[code],
                command=_update_sub_lang_entry
            ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        # Manual override entry (advanced)
        custom_row = ttk.Frame(lang_frame)
        custom_row.pack(fill=tk.X, pady=(0, Spacing.XS))
        ttk.Label(custom_row, text=tr("sub_custom_lang", "Custom:"), style="Caption.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.sub_lang_entry = ttk.Entry(custom_row, width=24)
        self.sub_lang_entry.insert(0, "en")
        self.sub_lang_entry.pack(side=tk.LEFT)
        ttk.Label(custom_row, text=tr("sub_help", "e.g., en, pt, es"), style="Caption.TLabel").pack(side=tk.LEFT, padx=(Spacing.SM, 0))
        
        # Subtitle format
        fmt_sub_frame = ttk.Frame(sub_card.body)
        fmt_sub_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        ttk.Label(fmt_sub_frame, text=f"{tr('sub_format', 'Format')}:", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.sub_format_var = tk.StringVar(value="srt")
        sub_format_combo = ttk.Combobox(fmt_sub_frame, textvariable=self.sub_format_var, values=["srt", "vtt", "ass", "json3"], width=8, state="readonly")
        sub_format_combo.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Embed in video
        self.sub_embed_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sub_card.body,
            text=tr("sub_embed", "Embed in video"),
            variable=self.sub_embed_var
        ).pack(anchor=tk.W)
        
        # === CHAPTERS CARD (shown/hidden dynamically after verify) ===
        self._chapters_card_frame = ttk.Frame(main)
        # Not packed by default — shown only when chapters detected
        
        chapters_card = ModernCard(self._chapters_card_frame, title=tr("chapters_title", "Chapters"), design=self.design)
        chapters_card.pack(fill=tk.X)
        
        self._chapters_list_frame = ttk.Frame(chapters_card.body)
        self._chapters_list_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Split by chapters checkbox
        self._chapters_split_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            chapters_card.body,
            text=tr("chapters_split", "Split by Chapters"),
            variable=self._chapters_split_var
        ).pack(anchor=tk.W, pady=(0, Spacing.XS))
        
        ttk.Label(
            chapters_card.body,
            text=tr("chapters_split_help", "Download each chapter as a separate file"),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        ModernButton(
            chapters_card.body,
            text=tr("chapters_download_all", "Download All Chapters"),
            command=self._download_chapters,
            variant="outline",
            size="sm",
            width=22
        ).pack(anchor=tk.W)
        
        # === ACTION BUTTONS ===
        Separator(main, design=self.design).pack(fill=tk.X, pady=Spacing.MD)
        
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        dl_btn = ModernButton(
            action_frame,
            text=tr("download_btn", "Download"),
            icon_name="download",
            command=self.start_download,
            variant="primary",
            size="lg",
            width=14
        )
        dl_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(dl_btn, text=tr("tooltip_download", "Start downloading the verified video"), design=self.design)
        
        stop_btn = ModernButton(
            action_frame,
            text=tr("download_stop", "Stop"),
            icon_name="stop",
            command=self.stop_download,
            variant="danger",
            size="lg",
            width=14
        )
        stop_btn.pack(side=tk.LEFT)
        Tooltip(stop_btn, text=tr("tooltip_stop", "Cancel current download"), design=self.design)

        # progress label next to the buttons; use helper for consistency
        self._make_progress_label(action_frame, attr="download_progress_label")

        # make sure radios/format combo are consistent on first show
        self._on_format_selected()

        return frame
    
    def create_batch_tab(self):
        """Create batch download section with download queue management"""
        tr = self.translator.get
        
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable container
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        main = scroll.interior
        main.configure(padding=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("tab_batch", "Batch Downloads"),
            subtitle=tr("batch_subtitle", "Download multiple videos at once"),
            icon="batch"
        ).pack(fill=tk.X, pady=(0, Spacing.LG))
        
        # === INFO BANNER ===
        InfoBanner(
            main, text=tr("batch_info_tip", "Paste one URL per line. Supports playlists, channels, and individual videos."),
            variant="info", design=self.design, dismissible=True
        ).pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # === URLS INPUT CARD ===
        urls_card = ModernCard(main, title=tr("batch_urls", "YouTube URLs"), design=self.design, accent_top=True)
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
            height=8,
            yscrollcommand=text_scrollbar.set,
            font=(LOADED_FONT_FAMILY, Typography.SIZE_MD),
            wrap=tk.WORD
        )
        self.batch_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.batch_text.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Right-click context menu on batch text area (Issue #45)
        def _batch_ctx_menu(event):
            _cm = tk.Menu(self.root, tearoff=0)
            _cm.configure(
                bg=self.design.get_color("bg_secondary"),
                fg=self.design.get_color("fg_primary"),
                activebackground=self.design.get_color("accent_primary"),
                activeforeground=self.design.get_color("fg_on_accent"),
                font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
                bd=0, relief="flat"
            )
            _cm.add_command(label=tr("ctx_copy", "Copy"),
                           command=lambda: self.batch_text.event_generate("<<Copy>>"))
            _cm.add_command(label=tr("ctx_paste", "Paste"),
                           command=lambda: self.batch_text.event_generate("<<Paste>>"))
            _cm.add_command(label=tr("ctx_select_all", "Select All"),
                           command=lambda: self.batch_text.tag_add(tk.SEL, "1.0", tk.END))
            _cm.add_separator()
            _cm.add_command(label=tr("ctx_clear", "Clear"),
                           command=lambda: self.batch_text.delete("1.0", tk.END))
            try:
                _cm.tk_popup(event.x_root, event.y_root)
            finally:
                _cm.grab_release()
        self.batch_text.bind("<Button-3>", _batch_ctx_menu)
        text_actions = ttk.Frame(urls_card.body)
        text_actions.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        paste_btn = ModernButton(
            text_actions,
            text=tr("batch_paste", "Paste from Clipboard"),
            icon_name="paste",
            command=self.batch_paste,
            variant="outline",
            size="sm",
            width=20
        )
        paste_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(paste_btn, text=tr("tooltip_paste_clipboard", "Paste URLs from clipboard"), design=self.design)
        
        ModernButton(
            text_actions,
            text=tr("batch_clear", "Clear All"),
            icon_name="clear",
            command=lambda: self.batch_text.delete(1.0, tk.END),
            variant="ghost",
            size="sm",
            width=12
        ).pack(side=tk.LEFT)
        
        # URL count label
        self._batch_url_count = ttk.Label(text_actions, text="0 URLs", style="Caption.TLabel")
        self._batch_url_count.pack(side=tk.RIGHT)

        # Keep URL count label in sync with the text area
        def _update_batch_url_count(*_args):
            text = self.batch_text.get("1.0", tk.END).strip()
            count = len([u for u in text.split("\n") if u.strip()]) if text else 0
            self._batch_url_count.config(text=f"{count} URLs")
        self.batch_text.bind("<KeyRelease>", _update_batch_url_count)
        self.batch_text.bind("<<Paste>>", lambda e: self.root.after(50, _update_batch_url_count))

        # === ACTION BUTTONS (above queue for quicker access — Issue #44) ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(Spacing.MD, Spacing.SM))

        batch_dl_btn = ModernButton(
            action_frame,
            text=tr("batch_download_all", "Start Batch Download"),
            icon_name="download",
            command=self.start_batch_download,
            variant="primary",
            size="lg",
            width=22
        )
        batch_dl_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(batch_dl_btn, text=tr("tooltip_batch_download", "Start downloading all URLs in the list"), design=self.design)

        # Verify All button (Issue #42) — fetches info for each URL in the list
        verify_all_btn = ModernButton(
            action_frame,
            text=tr("batch_verify_all", "Verify All"),
            icon_name="check-circle",
            command=self._batch_verify_all,
            variant="outline",
            size="lg",
            width=14
        )
        verify_all_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(verify_all_btn, text=tr("tooltip_batch_verify_all", "Fetch title and duration for each URL in the list"), design=self.design)

        stop_all_btn = ModernButton(
            action_frame,
            text=tr("batch_stop", "Stop All"),
            icon_name="stop",
            command=self.stop_download,
            variant="danger",
            size="lg",
            width=12
        )
        stop_all_btn.pack(side=tk.LEFT)

        # Batch progress label (item counter + per-item %)
        # reuse same helper for consistency
        self.batch_progress_label = self._make_progress_label(action_frame, attr="batch_progress_label")

        # === DOWNLOAD QUEUE CARD ===
        queue_card = ModernCard(main, title=tr("queue_title", "Download Queue"), design=self.design)
        queue_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        # Queue status bar
        queue_status_frame = ttk.Frame(queue_card.body)
        queue_status_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        self.queue_progress_label = ttk.Label(
            queue_status_frame,
            text=tr("queue_progress", "{} of {} completed").format(0, 0),
            style="Caption.TLabel"
        )
        self.queue_progress_label.pack(side=tk.LEFT)
        
        ModernButton(
            queue_status_frame,
            text=tr("queue_clear_done", "Clear Completed"),
            command=self._queue_clear_completed,
            variant="ghost",
            size="sm",
            width=16
        ).pack(side=tk.RIGHT)
        
        pause_btn = ModernButton(
            queue_status_frame,
            text=tr("queue_pause", "Pause Queue"),
            command=self._queue_toggle_pause,
            variant="outline",
            size="sm",
            width=14
        )
        pause_btn.pack(side=tk.RIGHT, padx=(0, Spacing.SM))
        Tooltip(pause_btn, text=tr("tooltip_pause_queue", "Pause/resume the download queue"), design=self.design)
        
        # Scrollable queue list (replaced Canvas boilerplate with ScrollableFrame)
        queue_scroll = ScrollableFrame(queue_card.body, design=self.design, show_scrollbar=True)
        queue_scroll.pack(fill=tk.BOTH, expand=True)
        queue_scroll.config(height=120)
        self.queue_list_frame = queue_scroll.interior

        return frame

    def create_live_tab(self):
        """Create live stream recording + clipper section.
        
        Layout (top → bottom):
        ┌─────────────────────────────────────────────┐
        │  Section Header                             │
        ├─────────────────────────────────────────────┤
        │  [URL entry                                ]│
        │  [✓ Verificar]  [▶ Preview]  [● REC]  [■ Stop]│
        ├─────────────────────────────────────────────┤
        │  ● LIVE  |  Channel  |  thumb  |  00:12:34 ▲│
        ├─────────────────────────────────────────────┤
        │                                             │
        │            Embedded Video Player            │
        │            (16:9 optimal aspect)            │
        │                                             │
        │  ── seekbar (full rewind to live start) ──  │
        │  ▶ ⏸ 🔊▬▬ vol                              │
        ├─────────────────────────────────────────────┤
        │ [Start][End] 00:00→00:30 [⬇ Save] | 30 60 120 | ● AO VIVO│
        └─────────────────────────────────────────────┘
        """
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable content
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        main = scroll.interior
        main.configure(padding=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("clipper_title", "Live Stream Clipper"),
            subtitle=tr("clipper_subtitle", "Record, watch, and clip live streams in real-time"),
            icon="live"
        ).pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # === URL + ACTIONS CARD ===
        url_card = ModernCard(main, title=tr("live_url", "Live Stream URL"), design=self.design,
                             accent_top=True, accent_color=self.design.get_color("red_primary"))
        url_card.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Row 1: URL entry (full width)
        self.live_url_entry = ModernEntry(
            url_card.body, placeholder=tr("live_url_placeholder", "Paste live stream URL here..."),
            design=self.design, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD)
        )
        self.live_url_entry.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Row 2: Action buttons (auto-sized, no fixed width)
        btn_row = ttk.Frame(url_card.body)
        btn_row.pack(fill=tk.X)
        
        # -- Color constants for custom buttons --
        accent = self.design.get_color("accent_primary")
        bg_ctrl = self.design.get_color("bg_secondary")
        fg_main = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        
        # Verify Stream
        self._live_check_btn = ModernButton(
            btn_row,
            text=tr("live_check_stream", "Verify Stream"),
            icon_name="verify",
            command=self.verify_live_stream,
            variant="primary",
            size="md"
        )
        self._live_check_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(self._live_check_btn, text=tr("tooltip_check_live", "Check if the stream is live and available"), design=self.design)
        
        # Preview
        self._live_preview_btn = ModernButton(
            btn_row,
            text=f"▶  {tr('player_load_preview', 'Preview')}",
            command=self._load_live_preview,
            variant="outline",
            size="md"
        )
        self._live_preview_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(self._live_preview_btn, text=tr("tooltip_load_preview", "Load video preview in embedded player"), design=self.design)
        
        # REC — red filled button
        self._live_rec_btn = ModernButton(
            btn_row,
            text=f"●  {tr('live_start_recording', 'REC')}",
            command=self.start_live_recording,
            variant="danger-filled",
            size="md"
        )
        self._live_rec_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(self._live_rec_btn, text=tr("tooltip_start_recording", "Start recording the full live stream from the beginning"), design=self.design)
        
        # Stop — danger outline
        self._live_stop_btn = ModernButton(
            btn_row,
            text=f"■  {tr('live_stop_recording', 'Stop')}",
            command=self.stop_live_recording,
            variant="danger",
            size="md"
        )
        self._live_stop_btn.pack(side=tk.LEFT)
        Tooltip(self._live_stop_btn, text=tr("tooltip_stop_recording", "Stop recording and save the video file"), design=self.design)
        
        # === STREAM STATUS STRIP (compact, below URL) ===
        status_bg = self.design.get_color("bg_tertiary")
        status_fg = self.design.get_color("fg_primary")
        status_fg_sec = self.design.get_color("fg_secondary")
        status_fg_ter = self.design.get_color("fg_tertiary")
        status_border = self.design.get_color("border_subtle")
        
        self._live_status_strip = tk.Frame(main, bg=status_bg, 
                                            highlightbackground=status_border, highlightthickness=1)
        self._live_status_strip.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        status_inner = tk.Frame(self._live_status_strip, bg=status_bg)
        status_inner.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.XS)
        
        # Live indicator dot
        self._live_dot_label = tk.Label(status_inner, text="●", bg=status_bg, fg=status_fg_ter,
                                         font=(Typography.FONT_FAMILY, 10))
        self._live_dot_label.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        # Status text
        self.live_status_label = tk.Label(status_inner, text=tr("live_status_unknown", "Waiting..."),
                                          bg=status_bg, fg=status_fg_sec,
                                          font=(Typography.FONT_FAMILY, Typography.SIZE_SM))
        self.live_status_label.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Separator
        tk.Frame(status_inner, bg=status_border, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=Spacing.SM, pady=2)
        
        # Channel name
        self._live_channel_label = tk.Label(status_inner, text="—", bg=status_bg, fg=status_fg,
                                             font=(Typography.FONT_FAMILY, Typography.SIZE_SM, "bold"))
        self._live_channel_label.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Thumbnail (small, 48x27 — 16:9)
        self._live_thumb_label = tk.Label(status_inner, bg=status_bg, width=6, height=1)
        self._live_thumb_label.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        self._live_thumb_ref = None  # prevent GC
        
        # Separator
        tk.Frame(status_inner, bg=status_border, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=Spacing.SM, pady=2)
        
        # Elapsed time (counting up ▲)
        self.live_elapsed_label = tk.Label(status_inner, text="00:00:00", bg=status_bg,
                                            fg=self.design.get_color("accent_primary"),
                                            font=(Typography.FONT_MONO, Typography.SIZE_SM, "bold"))
        self.live_elapsed_label.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        tk.Label(status_inner, text="▲", bg=status_bg, fg=self.design.get_color("accent_primary"),
                 font=(Typography.FONT_FAMILY, 8)).pack(side=tk.LEFT)
        
        # Duration (right-aligned)
        self.live_duration_label = tk.Label(status_inner, text="", bg=status_bg,
                                             fg=status_fg_ter,
                                             font=(Typography.FONT_MONO, Typography.SIZE_TINY))
        self.live_duration_label.pack(side=tk.RIGHT)
        
        # === EMBEDDED VIDEO PLAYER (16:9 optimal) ===
        player_border = self.design.get_color("border")
        
        player_container = tk.Frame(main, bg=player_border)
        player_container.pack(fill=tk.X, pady=(0, 0))
        
        if is_player_available():
            self.embedded_player = EmbeddedPlayer(
                player_container,
                dark_mode=self.dark_mode,
                height=420
            )
            self.embedded_player.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        else:
            # Placeholder with install instructions
            ph_bg = "#0a0a14" if self.dark_mode else "#f5f5f5"
            ph_fg = self.design.get_color("fg_tertiary")
            placeholder_frame = tk.Frame(player_container, bg=ph_bg, height=280)
            placeholder_frame.pack(fill=tk.X, padx=1, pady=1)
            placeholder_frame.pack_propagate(False)
            tk.Label(
                placeholder_frame,
                text=(
                    f"🎬  {tr('player_no_backend', 'No video player found')}\n\n"
                    f"{tr('player_install_mpv', 'Install mpv (recommended)')}:\n"
                    "  winget install mpv\n\n"
                    f"{tr('player_install_vlc', 'Or install VLC')}:\n"
                    "  winget install VideoLAN.VLC\n"
                    "  pip install python-vlc"
                ),
                bg=ph_bg, fg=ph_fg,
                font=("Consolas", 10),
                justify="center"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        # === CLIP CONTROLS BAR (below player, integrated) ===
        clip_bar_bg = self.design.get_color("bg_secondary")
        clip_accent = self.design.get_color("accent_primary")
        
        clip_bar = tk.Frame(main, bg=clip_bar_bg, highlightbackground=player_border, highlightthickness=1)
        clip_bar.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        clip_bar_inner = tk.Frame(clip_bar, bg=clip_bar_bg)
        clip_bar_inner.pack(fill=tk.X, padx=Spacing.SM, pady=Spacing.XS)
        
        # Left group: Mark Start / Mark End / Time label / Download
        mark_frame = tk.Frame(clip_bar_inner, bg=clip_bar_bg)
        mark_frame.pack(side=tk.LEFT)
        
        self._live_mark_start_btn = ModernButton(
            mark_frame,
            text=f"▶  {tr('clipper_mark_start', 'Start')}",
            command=self._clipper_mark_start,
            variant="success",
            size="sm"
        )
        self._live_mark_start_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        Tooltip(self._live_mark_start_btn, text=tr("tooltip_mark_start", "Mark the start time for a clip at current preview position"), design=self.design)
        
        self._live_mark_end_btn = ModernButton(
            mark_frame,
            text=f"■  {tr('clipper_mark_end', 'End')}",
            command=self._clipper_mark_end,
            variant="danger",
            size="sm"
        )
        self._live_mark_end_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(self._live_mark_end_btn, text=tr("tooltip_mark_end", "Mark the end time for a clip at current preview position"), design=self.design)
        
        # Marked time display (appears when start is marked)
        self._clip_time_label = tk.Label(mark_frame, text="", bg=clip_bar_bg, fg=clip_accent,
                                          font=(Typography.FONT_MONO, Typography.SIZE_SM))
        self._clip_time_label.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        # Download clip button (appears when start+end are marked)
        self._download_clip_btn = ModernButton(
            mark_frame,
            text=f"⬇  {tr('clipper_download_clip', 'Save Clip')}",
            command=self._clipper_download_marked,
            variant="primary",
            size="sm"
        )
        # Not packed yet — shown when both start and end are marked
        Tooltip(self._download_clip_btn, text=tr("tooltip_download_clip", "Download the marked clip segment immediately"), design=self.design)
        
        # Separator
        tk.Frame(clip_bar_inner, bg=self.design.get_color("border_subtle"), width=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=Spacing.SM, pady=2)
        
        # Quick cut buttons (instant download from current preview position)
        quick_frame = tk.Frame(clip_bar_inner, bg=clip_bar_bg)
        quick_frame.pack(side=tk.LEFT)
        
        tk.Label(quick_frame, text=f"✂ {tr('clipper_quick_cut', 'Quick Cut')}:", bg=clip_bar_bg,
                 fg=self.design.get_color("fg_tertiary"),
                 font=(Typography.FONT_FAMILY, Typography.SIZE_TINY)).pack(side=tk.LEFT, padx=(0, Spacing.XS))
        
        for secs, label in [(30, "30s"), (60, "60s"), (120, "2min")]:
            btn = ModernButton(
                quick_frame,
                text=label,
                command=lambda s=secs: self._clipper_quick_cut(s),
                variant="ghost",
                size="sm"
            )
            btn.pack(side=tk.LEFT, padx=(0, Spacing.XXS))
            Tooltip(btn, text=tr("tooltip_quick_cut", f"Instantly download the last {secs} seconds from current preview position"), design=self.design)
        
        # Separator
        tk.Frame(clip_bar_inner, bg=self.design.get_color("border_subtle"), width=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=Spacing.SM, pady=2)
        
        # LIVE button (right side) — seeks to live edge
        self._return_live_btn = ModernButton(
            clip_bar_inner,
            text=f"● {tr('live_return_to_live', 'LIVE')}",
            command=self._return_to_live,
            variant="danger-filled",
            size="sm"
        )
        self._return_live_btn.pack(side=tk.RIGHT)
        Tooltip(self._return_live_btn, text=tr("tooltip_return_to_live", "Jump to the latest position in the live stream"), design=self.design)
        
        # Hidden: recording mode (always continuous) + quality from config
        self.live_mode_var = tk.StringVar(value="continuous")
        self.live_quality_var = tk.StringVar(value=self.config_manager.get("live_quality", "best"))
        
        # Hidden duration entries kept for backend compatibility
        _hidden_dur = ttk.Frame(main)
        for key, default in [("live_hours", "01"), ("live_minutes", "00"), ("live_seconds", "00")]:
            entry = ttk.Entry(_hidden_dur, width=6, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
            entry.insert(0, default)
            setattr(self, f"{key}_entry", entry)

        return frame
    
    def create_following_tab(self):
        """Create channel following/monitoring section"""
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable content
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        main = scroll.interior
        main.configure(padding=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("following_title", "Following Channels"),
            subtitle=tr("following_subtitle", "Monitor channels for new uploads and auto-download"),
            icon="following"
        ).pack(fill=tk.X, pady=(0, Spacing.LG))
        
        # === ADD CHANNEL CARD — cyan accent ===
        add_card = ModernCard(main, title=f"➕ {tr('following_add', 'Add Channel')}", design=self.design, 
                             accent_top=True, accent_color=self.design.get_color("cyan_primary"))
        add_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Info banner
        InfoBanner(
            add_card.body, text=tr("following_info_tip", "Add YouTube channel URLs to monitor for new uploads. Enable auto-download to save new videos automatically."),
            variant="info", design=self.design, dismissible=True
        ).pack(fill=tk.X, pady=(0, Spacing.SM))
        
        add_row = ttk.Frame(add_card.body)
        add_row.pack(fill=tk.X)
        
        self.following_url_entry = ModernEntry(
            add_row, placeholder=tr("following_add_placeholder", "https://youtube.com/@channel"),
            design=self.design, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD)
        )
        self.following_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        add_btn = ModernButton(
            add_row,
            text=tr("following_add", "Add Channel"),
            command=self._following_add_channel,
            variant="primary",
            size="sm",
            width=14
        )
        add_btn.pack(side=tk.LEFT)
        Tooltip(add_btn, text=tr("tooltip_add_channel", "Add this channel to your following list"), design=self.design)
        
        # === MONITORING SETTINGS CARD ===
        settings_card = ModernCard(main, title=f"⚙️ {tr('tab_settings', 'Settings')}", design=self.design)
        settings_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        settings_grid = ttk.Frame(settings_card.body)
        settings_grid.pack(fill=tk.X)
        
        # Auto-download toggle
        self.following_auto_var = tk.BooleanVar(value=self.channel_monitor.get_auto_download())
        ttk.Checkbutton(
            settings_grid,
            text=f"⬇️ {tr('following_auto_download', 'Auto-Download')} — {tr('following_auto_download_help', 'Automatically download new uploads')}",
            variable=self.following_auto_var,
            command=self._following_save_settings
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=Spacing.XS)
        
        # Notifications toggle
        self.following_notify_var = tk.BooleanVar(value=self.channel_monitor.get_notifications())
        ttk.Checkbutton(
            settings_grid,
            text=f"🔔 {tr('following_notifications', 'Notifications')} — {tr('following_notifications_help', 'Show notification when new video is detected')}",
            variable=self.following_notify_var,
            command=self._following_save_settings
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=Spacing.XS)
        
        # Check interval
        ttk.Label(settings_grid, text=f"🕐 {tr('following_interval', 'Check Interval')}:", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=(Spacing.SM, Spacing.XS)
        )
        
        self.following_interval_var = tk.StringVar(value=str(self.channel_monitor.get_interval()))
        interval_combo = ttk.Combobox(
            settings_grid,
            textvariable=self.following_interval_var,
            values=["15", "30", "60", "360", "1440"],
            state="readonly",
            width=8
        )
        interval_combo.grid(row=2, column=1, sticky=tk.W, pady=(Spacing.SM, Spacing.XS), padx=(Spacing.SM, 0))
        interval_combo.bind("<<ComboboxSelected>>", lambda e: self._following_save_settings())
        
        ttk.Label(settings_grid, text=f"({tr('following_interval_help', 'minutes')})", style="Caption.TLabel").grid(
            row=2, column=2, sticky=tk.W, padx=(Spacing.XS, 0), pady=(Spacing.SM, Spacing.XS)
        )
        
        # Issue #61: Following quality moved to Settings tab — initialize from channel_monitor
        self.following_quality_var = tk.StringVar(value=self.channel_monitor.get_auto_quality())
        
        # Action buttons
        action_frame = ttk.Frame(settings_card.body)
        action_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        check_now_btn = ModernButton(
            action_frame,
            text=f"🔍 {tr('following_check_now', 'Check Now')}",
            command=self._following_check_now,
            variant="primary",
            size="sm",
            width=14
        )
        check_now_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(check_now_btn, text=tr("tooltip_check_now", "Check all channels for new uploads now"), design=self.design)
        
        self.following_monitor_btn_text = tk.StringVar(value=f"▶️ {tr('following_enabled', 'Start Monitoring')}")
        monitor_btn = ModernButton(
            action_frame,
            text=f"▶️ {tr('following_enabled', 'Start Monitoring')}",
            command=self._following_toggle_monitor,
            variant="outline",
            size="sm",
            width=18
        )
        monitor_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(monitor_btn, text=tr("tooltip_toggle_monitor", "Start/stop automatic channel monitoring"), design=self.design)
        
        # Last check timestamp
        last_check = self.channel_monitor.get_last_check()
        last_check_text = tr("following_never_checked", "Never checked")
        if last_check:
            try:
                dt = datetime.fromisoformat(last_check)
                last_check_text = tr("following_last_check", "Last check: {}").format(dt.strftime("%d/%m/%Y %H:%M"))
            except Exception:
                pass
        
        self.following_last_check_label = ttk.Label(action_frame, text=last_check_text, style="Caption.TLabel")
        self.following_last_check_label.pack(side=tk.LEFT, padx=(Spacing.MD, 0))
        
        # === FOLLOWED CHANNELS LIST CARD ===
        channels_card = ModernCard(main, title=f"📺 {tr('following_channels', 'Followed Channels')}", design=self.design)
        channels_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
        
        # Scrollable channel list — replaced Canvas boilerplate with ScrollableFrame
        ch_scroll = ScrollableFrame(channels_card.body, design=self.design, show_scrollbar=True)
        ch_scroll.pack(fill=tk.BOTH, expand=True)
        ch_scroll.config(height=200)
        self.following_channels_frame = ch_scroll.interior
        
        # Following log — redirected to global Activity Log (Issue #65/#67)
        # self.following_log alias set in _build_log_panel after global_log exists

        # Populate channels list
        self._refresh_following_channels()
        
        # Setup channel monitor callbacks
        self.channel_monitor.set_callbacks(
            on_new_video=self._following_on_new_videos,
            on_auto_download=self._following_auto_download,
            on_status_update=self._following_status_update
        )
        
        return frame
    
    # ──────────────────────────────────────────
    # FOLLOWING TAB METHODS
    # ──────────────────────────────────────────

    def _follow_channel_from_download(self):
        """Follow the channel from the currently verified video (Issue #19)"""
        tr = self.translator.get
        url = getattr(self, '_cached_uploader_url', '')
        if not url:
            messagebox.showwarning(tr("msg_warning", "Warning"),
                                   tr("following_invalid_url", "Invalid channel URL"))
            return
        self.download_log.add_log(f"➕ {tr('following_checking', 'Checking...')}")

        def add_thread():
            result = self.channel_monitor.add_channel(url)
            if result:
                def _on_added():
                    self.download_log.add_log(
                        f"✅ {tr('following_added', 'Channel added: {}').format(result.get('name', url))}"
                    )
                    self._refresh_following_channels()
                self.root.after(0, _on_added)
            else:
                self.root.after(0, lambda: self.download_log.add_log(
                    f"⚠️ {tr('following_already_added', 'Channel already being followed')}", "WARNING"
                ))

        threading.Thread(target=add_thread, daemon=True).start()

    def _following_add_channel(self):
        """Add a new channel to follow"""
        tr = self.translator.get
        url = self.following_url_entry.get().strip()
        
        if not url or url == "https://youtube.com/@channel":
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("following_invalid_url", "Invalid channel URL"))
            return
        
        self.following_log.add_log(f"🔍 {tr('following_checking', 'Checking...')}")
        
        def add_thread():
            result = self.channel_monitor.add_channel(url)
            if result:
                self.root.after(0, lambda: self.following_log.add_log(
                    f"✅ {tr('following_added', 'Channel added: {}').format(result.get('name', url))}"
                ))
                self.root.after(0, self._refresh_following_channels)
                self.root.after(0, lambda: self.following_url_entry.delete(0, tk.END))
            elif result is None:
                # Check if it's already followed
                channels = self.channel_monitor.get_channels()
                normalized = self.channel_monitor._normalize_channel_url(url)
                already = any(ch["url"] == normalized for ch in channels) if normalized else False
                if already:
                    self.root.after(0, lambda: self.following_log.add_log(
                        f"⚠️ {tr('following_already_added', 'Channel already being followed')}", "WARNING"
                    ))
                else:
                    self.root.after(0, lambda: self.following_log.add_log(
                        f"❌ {tr('following_invalid_url', 'Invalid channel URL')}", "ERROR"
                    ))
        
        threading.Thread(target=add_thread, daemon=True).start()

    def _refresh_following_channels(self):
        """Refresh the followed channels list UI (Issue #60 — improved card layout)"""
        tr = self.translator.get
        
        if not hasattr(self, 'following_channels_frame'):
            return
        
        for widget in self.following_channels_frame.winfo_children():
            widget.destroy()
        
        channels = self.channel_monitor.get_channels()
        
        if not channels:
            ttk.Label(
                self.following_channels_frame,
                text=tr("following_no_channels", "No channels followed yet"),
                style="Caption.TLabel"
            ).pack(pady=Spacing.LG)
            return
        
        card_bg = self.design.get_color("bg_tertiary")
        border_col = self.design.get_color("border_primary")
        fg_primary = self.design.get_color("fg_primary")
        fg_secondary = self.design.get_color("fg_secondary")
        fg_tertiary = self.design.get_color("fg_tertiary")
        error_col = self.design.get_color("error")

        for i, ch in enumerate(channels):
            # Outer frame with subtle bottom border between items
            outer = tk.Frame(self.following_channels_frame, bg=border_col)
            outer.pack(fill=tk.X, pady=(0, 1))
            
            row = tk.Frame(outer, bg=card_bg, pady=Spacing.SM, padx=Spacing.SM)
            row.pack(fill=tk.X)
            
            # Left info column
            info_col = tk.Frame(row, bg=card_bg)
            info_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Channel icon + name on first line
            name_row = tk.Frame(info_col, bg=card_bg)
            name_row.pack(fill=tk.X, anchor="w")
            
            tk.Label(
                name_row, text="📺",
                font=("Segoe UI Emoji", 12),
                bg=card_bg,
            ).pack(side=tk.LEFT, padx=(0, Spacing.XS))
            
            tk.Label(
                name_row,
                text=ch.get("name", tr("following_unknown_channel", "Unknown Channel")),
                font=(LOADED_FONT_FAMILY, Typography.SIZE_BODY, "bold"),
                fg=fg_primary,
                bg=card_bg,
                anchor="w",
            ).pack(side=tk.LEFT)
            
            # URL on second line (truncated)
            url_raw = ch.get("url", "")
            url_short = url_raw[len("https://www.youtube.com/"):] if url_raw.startswith("https://www.youtube.com/") else url_raw
            if len(url_short) > 38:
                url_short = url_short[:35] + "…"
            tk.Label(
                info_col,
                text=url_short,
                font=(LOADED_FONT_FAMILY, Typography.SIZE_TINY),
                fg=fg_tertiary,
                bg=card_bg,
                anchor="w",
            ).pack(fill=tk.X, padx=(Spacing.LG, 0))
            
            # Added date on third line
            added = ch.get("added_date", "")
            if added:
                try:
                    dt = datetime.fromisoformat(added)
                    date_text = tr("following_added_date", "Added {}").format(dt.strftime("%d/%m/%Y"))
                    tk.Label(
                        info_col,
                        text=date_text,
                        font=(LOADED_FONT_FAMILY, Typography.SIZE_TINY),
                        fg=fg_tertiary,
                        bg=card_bg,
                        anchor="w",
                    ).pack(fill=tk.X, padx=(Spacing.LG, 0))
                except Exception:
                    pass
            
            # Per-channel toggles: Notify + Auto-Download (Issues #62, #66)
            ch_notify = ch.get("notify", True)
            ch_auto_dl = ch.get("auto_download", False)
            toggles_row = tk.Frame(info_col, bg=card_bg)
            toggles_row.pack(fill=tk.X, padx=(Spacing.LG, 0), pady=(Spacing.XS, 0))

            notify_var = tk.BooleanVar(value=ch_notify)
            notify_lbl = tk.Label(
                toggles_row,
                text=f"🔔 {tr('following_toggle_notify', 'Notify')}" if ch_notify else f"🔕 {tr('following_toggle_notify', 'Notify')}",
                font=(LOADED_FONT_FAMILY, Typography.SIZE_TINY),
                fg=self.design.get_color("accent_primary") if ch_notify else fg_tertiary,
                bg=card_bg, cursor="hand2"
            )
            notify_lbl.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            def _toggle_notify(_url=ch["url"], _lbl=notify_lbl, _var=notify_var):
                nv = not _var.get()
                _var.set(nv)
                self.channel_monitor.set_channel_notify(_url, nv)
                _lbl.config(
                    text=f"🔔 {tr('following_toggle_notify', 'Notify')}" if nv else f"🔕 {tr('following_toggle_notify', 'Notify')}",
                    fg=self.design.get_color("accent_primary") if nv else fg_tertiary
                )
            notify_lbl.bind("<Button-1>", lambda e, fn=_toggle_notify: fn())
            Tooltip(notify_lbl, text=tr("following_toggle_notify_tip", "Toggle notifications for this channel"), design=self.design)

            auto_dl_var = tk.BooleanVar(value=ch_auto_dl)
            auto_lbl = tk.Label(
                toggles_row,
                text=f"⬇️ {tr('following_toggle_auto_dl', 'Auto-DL')}" if ch_auto_dl else f"⬜ {tr('following_toggle_auto_dl', 'Auto-DL')}",
                font=(LOADED_FONT_FAMILY, Typography.SIZE_TINY),
                fg=self.design.get_color("accent_primary") if ch_auto_dl else fg_tertiary,
                bg=card_bg, cursor="hand2"
            )
            auto_lbl.pack(side=tk.LEFT)
            def _toggle_auto_dl(_url=ch["url"], _lbl=auto_lbl, _var=auto_dl_var):
                nv = not _var.get()
                _var.set(nv)
                self.channel_monitor.set_channel_auto_download(_url, nv)
                _lbl.config(
                    text=f"⬇️ {tr('following_toggle_auto_dl', 'Auto-DL')}" if nv else f"⬜ {tr('following_toggle_auto_dl', 'Auto-DL')}",
                    fg=self.design.get_color("accent_primary") if nv else fg_tertiary
                )
            auto_lbl.bind("<Button-1>", lambda e, fn=_toggle_auto_dl: fn())
            Tooltip(auto_lbl, text=tr("following_toggle_auto_dl_tip", "Auto-download new videos from this channel"), design=self.design)

            # Right: remove button
            remove_lbl = tk.Label(
                row, text="✕", cursor="hand2",
                font=(LOADED_FONT_FAMILY, Typography.SIZE_BODY, "bold"),
                bg=card_bg,
                fg=error_col,
            )
            remove_lbl.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
            remove_lbl.bind("<Button-1>", lambda e, url=ch["url"]: self._following_remove_channel(url))
            Tooltip(remove_lbl, text=tr("following_remove_tooltip", "Remove channel"), design=self.design)

    def _following_remove_channel(self, url: str):
        """Remove a followed channel"""
        tr = self.translator.get
        if self.channel_monitor.remove_channel(url):
            self.following_log.add_log(f"🗑️ {tr('following_removed', 'Channel removed')}")
            self._refresh_following_channels()

    def _following_save_settings(self):
        """Save following tab settings"""
        self.channel_monitor.set_auto_download(self.following_auto_var.get())
        self.channel_monitor.set_notifications(self.following_notify_var.get())
        try:
            self.channel_monitor.set_interval(int(self.following_interval_var.get()))
        except ValueError:
            pass
        self.channel_monitor.set_auto_quality(self.following_quality_var.get())

    def _following_startup_check(self):
        """Check for new videos on startup (Issue #63) — silent, no log if nothing found"""
        if not self.channel_monitor.get_channels():
            return
        import threading
        def _run():
            new_videos = self.channel_monitor.check_for_new_videos()
            if new_videos:
                count = len(new_videos)
                self.root.after(0, lambda: self._update_bell_count(count))
                tr = self.translator.get
                msg = tr("following_new_found", "{} new video(s) found!").format(count)
                self.root.after(0, lambda: self.following_log.add_log(f"🔔 {msg}"))
                for vid in new_videos:
                    self.root.after(0, lambda v=vid: self.following_log.add_log(
                        f"  📹 {v.get('title', 'Unknown')[:50]} ({v.get('channel_name', '')})"
                    ))
        threading.Thread(target=_run, daemon=True).start()

    def _update_bell_count(self, count: int):
        """Update the notification bell badge in the header (Issue #64)"""
        self._bell_count = getattr(self, '_bell_count', 0) + count
        if hasattr(self, '_bell_label'):
            if self._bell_count > 0:
                self._bell_label.config(text=f"🔔 {self._bell_count}")
            else:
                self._bell_label.config(text="🔔")

    def _following_check_now(self):
        """Manually check all followed channels for new videos"""
        tr = self.translator.get
        self.following_log.add_log(f"🔍 {tr('following_checking', 'Checking for new videos...')}")
        
        def check_thread():
            new_videos = self.channel_monitor.check_for_new_videos()
            if new_videos:
                msg = tr("following_new_found", "{} new video(s) found!").format(len(new_videos))
                self.root.after(0, lambda: self._update_bell_count(len(new_videos)))
                self.root.after(0, lambda: self.following_log.add_log(f"🎉 {msg}"))
                for vid in new_videos:
                    self.root.after(0, lambda v=vid: self.following_log.add_log(
                        f"  📹 {v.get('title', 'Unknown')[:50]} ({v.get('channel_name', '')})"
                    ))
            else:
                self.root.after(0, lambda: self.following_log.add_log(
                    f"ℹ️ {tr('following_no_new', 'No new videos found')}"
                ))
            
            # Update last check label
            last = self.channel_monitor.get_last_check()
            if last:
                try:
                    dt = datetime.fromisoformat(last)
                    txt = tr("following_last_check", "Last check: {}").format(dt.strftime("%d/%m/%Y %H:%M"))
                    self.root.after(0, lambda: self.following_last_check_label.config(text=txt))
                except Exception:
                    pass
        
        threading.Thread(target=check_thread, daemon=True).start()

    def _following_toggle_monitor(self):
        """Toggle background monitoring on/off"""
        tr = self.translator.get
        if self.channel_monitor.is_running:
            self.channel_monitor.stop_monitoring()
            self.following_log.add_log(f"⏹️ {tr('following_disabled', 'Monitoring disabled')}")
        else:
            self.channel_monitor.start_monitoring()
            self.following_log.add_log(f"▶️ {tr('following_enabled', 'Monitoring enabled')}")

    def _following_on_new_videos(self, videos: list):
        """Callback when new videos are detected by the monitor"""
        tr = self.translator.get
        if not videos:
            return
        
        for vid in videos:
            channel = vid.get("channel_name", "Unknown")
            title = vid.get("title", "Unknown")
            msg = tr("following_new_video", "New video from {}!").format(channel)
            self.root.after(0, lambda m=msg, t=title: self.following_log.add_log(f"🔔 {m}: {t[:40]}"))
        
        # Show notification
        if self.channel_monitor.get_notifications():
            count = len(videos)
            msg = tr("following_new_found", "{} new video(s) found!").format(count)
            self.root.after(0, lambda: messagebox.showinfo("EasyCut", msg))

    def _following_auto_download(self, video: dict):
        """Auto-download a new video detected by the monitor"""
        tr = self.translator.get
        url = video.get("url", "")
        title = video.get("title", "Unknown")
        if not url:
            return
        
        self.root.after(0, lambda: self.following_log.add_log(
            f"⬇️ {tr('following_auto_started', 'Auto-downloading: {}').format(title[:40])}"
        ))
        
        def download_thread():
            try:
                quality = self.channel_monitor.get_auto_quality()
                output_template = str(self.output_dir / "%(title)s.%(ext)s")
                base_opts = self._build_download_options(output_template, quality, "full")
                ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                
                info = self._run_ydl_download(url, ydl_opts)
                
                entry = {
                    "date": datetime.now().isoformat(),
                    "filename": info.get('title', title),
                    "status": "success",
                    "url": url,
                    "thumbnail": info.get('thumbnail', ''),
                    "video_id": info.get('id', ''),
                }
                self.config_manager.add_to_history(entry)
                
                self.root.after(0, lambda: self.following_log.add_log(f"✅ {title[:40]}"))
                self.root.after(0, self.refresh_history)
            except Exception as e:
                self.root.after(0, lambda: self.following_log.add_log(
                    f"❌ {title[:30]}: {str(e)[:50]}", "ERROR"
                ))
        
        threading.Thread(target=download_thread, daemon=True).start()

    def _following_status_update(self, status: str):
        """Callback for monitor status changes"""
        tr = self.translator.get
        if status == "checking":
            self.root.after(0, lambda: self.following_log.add_log(
                f"🔍 {tr('following_checking', 'Checking for new videos...')}"
            ))
        elif status == "idle":
            last = self.channel_monitor.get_last_check()
            if last:
                try:
                    dt = datetime.fromisoformat(last)
                    txt = tr("following_last_check", "Last check: {}").format(dt.strftime("%d/%m/%Y %H:%M"))
                    self.root.after(0, lambda: self.following_last_check_label.config(text=txt))
                except Exception:
                    pass

    def create_history_tab(self):
        """Create download history + post-processing hub section"""
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable content
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        main = scroll.interior
        main.configure(padding=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("history_title", "Download History") + " & " + tr("live_postprocess", "Post-Processing"),
            subtitle=tr("history_subtitle", "Track all your downloads in one place") + " • " + tr("pp_enhance", "Enhance..."),
            icon="history"
        ).pack(fill=tk.X, pady=(0, Spacing.LG))
        
        # === ACTION BUTTONS ===
        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        refresh_btn = ModernButton(
            action_frame,
            text=tr("history_update", "Refresh"),
            icon_name="refresh",
            command=self.refresh_history,
            variant="outline",
            width=12
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(refresh_btn, text=tr("tooltip_refresh_history", "Reload download history from disk"), design=self.design)
        
        clear_btn = ModernButton(
            action_frame,
            text=tr("history_clear", "Clear History"),
            icon_name="delete",
            command=self.clear_history,
            variant="danger",
            width=14
        )
        clear_btn.pack(side=tk.LEFT)
        Tooltip(clear_btn, text=tr("tooltip_clear_history", "Delete all download records"), design=self.design)

        ttk.Label(
            action_frame,
            text=f"{tr('history_search', 'Search')}:",
            style="Caption.TLabel"
        ).pack(side=tk.LEFT, padx=(Spacing.LG, Spacing.SM))

        self.history_search_entry = ModernEntry(
            action_frame, placeholder=tr("history_search_placeholder", "Filter by title..."),
            design=self.design, width=28
        )
        self.history_search_entry.pack(side=tk.LEFT)
        self.history_search_entry.bind("<KeyRelease>", lambda _e: self.refresh_history())

        # === POST-PROCESSING TOOLS CARD ===
        pp_card = ModernCard(main, title=f"🛠️ {tr('live_postprocess', 'Post-Processing')}", design=self.design, accent_top=True, hoverable=True)
        pp_card.pack(fill=tk.X, pady=(0, Spacing.MD))

        pp_info = ttk.Label(
            pp_card.body,
            text=tr("pp_select_file", "Select a file to process"),
            style="Caption.TLabel"
        )
        pp_info.pack(anchor="w", pady=(0, Spacing.SM))

        # File selector
        pp_file_frame = ttk.Frame(pp_card.body)
        pp_file_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        self.pp_file_var = tk.StringVar(value="")
        pp_file_entry = ttk.Entry(pp_file_frame, textvariable=self.pp_file_var, state="readonly", font=(LOADED_FONT_FAMILY, Typography.SIZE_SM))
        pp_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))

        _pp_file_select_btn = ModernButton(
            pp_file_frame,
            text="📂 " + tr("browser_cookies_file_button", "Select File"),
            command=self._pp_select_file,
            variant="outline",
            size="sm",
            width=14
        )
        _pp_file_select_btn.pack(side=tk.LEFT)
        Tooltip(_pp_file_select_btn, text=tr("tooltip_pp_select_file", "Select a video or audio file to process"), design=self.design)

        # Issues #29/#30: Embedded media player for PP preview with full controls
        if is_player_available():
            self.pp_player = EmbeddedPlayer(
                pp_card.body,
                dark_mode=self.dark_mode,
                height=300
            )
            self.pp_player.pack(fill=tk.BOTH, expand=True, pady=(Spacing.SM, 0))

        # Enhancement buttons row 1
        pp_buttons1 = ttk.Frame(pp_card.body)
        pp_buttons1.pack(fill=tk.X, pady=(Spacing.SM, Spacing.XS))

        _pp_op_tooltip_keys = {
            "normalize_audio": ("tooltip_pp_normalize", "Normalize audio levels for consistent volume"),
            "denoise_video": ("tooltip_pp_denoise", "Remove video noise and improve image quality"),
            "stabilize_video": ("tooltip_pp_stabilize", "Apply stabilization to reduce camera shake"),
            "compress": ("tooltip_pp_compress", "Reduce file size using video compression"),
        }
        for op, label_key, icon in [
            ("normalize_audio", "pp_normalize_audio", "🔊"),
            ("denoise_video", "pp_denoise_video", "🎞️"),
            ("stabilize_video", "pp_stabilize_video", "📐"),
            ("compress", "pp_compress", "📦"),
        ]:
            _pp_btn = ModernButton(
                pp_buttons1,
                text=f"{icon} {tr(label_key, label_key)}",
                command=lambda o=op: self._run_post_process(o),
                variant="outline",
                size="sm",
            )
            _pp_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))
            _tip_key, _tip_default = _pp_op_tooltip_keys[op]
            Tooltip(_pp_btn, text=tr(_tip_key, _tip_default), design=self.design)

        # Enhancement buttons row 2
        pp_buttons2 = ttk.Frame(pp_card.body)
        pp_buttons2.pack(fill=tk.X, pady=(Spacing.XS, Spacing.SM))

        _pp_extract_btn = ModernButton(
            pp_buttons2,
            text=f"🔈 {tr('pp_extract_audio', 'Extract Audio (MP3)')}",
            command=lambda: self._run_post_process("extract_audio"),
            variant="outline",
            size="sm",
        )
        _pp_extract_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        Tooltip(_pp_extract_btn, text=tr("tooltip_pp_extract_audio", "Extract audio track and save as MP3"), design=self.design)

        _pp_upscale_btn = ModernButton(
            pp_buttons2,
            text=f"⬆️ {tr('pp_upscale', 'Upscale to 1080p')}",
            command=lambda: self._run_post_process("upscale", target_height=1080),
            variant="outline",
            size="sm",
        )
        _pp_upscale_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        Tooltip(_pp_upscale_btn, text=tr("tooltip_pp_upscale_1080", "Upscale video resolution to 1080p"), design=self.design)

        _pp_speed_btn = ModernButton(
            pp_buttons2,
            text=f"⏩ {tr('pp_speed', 'Change Speed')}",
            command=self._pp_change_speed_dialog,
            variant="outline",
            size="sm",
        )
        _pp_speed_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))
        Tooltip(_pp_speed_btn, text=tr("tooltip_pp_speed_change", "Change playback speed of the selected file"), design=self.design)

        # Scale/Resize row
        pp_scale_frame = ttk.Frame(pp_card.body)
        pp_scale_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        ttk.Label(pp_scale_frame, text=f"📏 {tr('pp_scale', 'Scale / Resize')}:", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.SM))

        for res, h in [("1080p", 1080), ("720p", 720), ("480p", 480)]:
            ModernButton(
                pp_scale_frame,
                text=res,
                command=lambda height=h: self._run_post_process("upscale", target_height=height),
                variant="ghost",
                size="sm",
                width=8
            ).pack(side=tk.LEFT, padx=(0, Spacing.XS))

        # Trim row
        pp_trim_frame = ttk.Frame(pp_card.body)
        pp_trim_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        ttk.Label(pp_trim_frame, text=f"✂️ {tr('pp_trim', 'Trim Video')}:", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        ttk.Label(pp_trim_frame, text=tr("pp_trim_start", "Start"), style="Caption.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.XS))

        self.pp_trim_start_var = tk.StringVar(value="00:00:00")
        ttk.Entry(pp_trim_frame, textvariable=self.pp_trim_start_var, width=10, font=(LOADED_FONT_FAMILY, Typography.SIZE_SM)).pack(side=tk.LEFT, padx=(0, Spacing.XS))

        # Issue #31: Capture start time from the current player position
        def _pp_set_trim_start():
            if self.pp_player:
                t = self.pp_player.get_time() or 0.0
                h, r = divmod(int(t), 3600)
                m, s = divmod(r, 60)
                self.pp_trim_start_var.set(f"{h:02d}:{m:02d}:{s:02d}")
        _pp_set_start_btn = ModernButton(
            pp_trim_frame,
            text=tr("pp_set_start", "⏱ Set"),
            command=_pp_set_trim_start,
            variant="ghost",
            size="sm",
            width=6
        )
        _pp_set_start_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(_pp_set_start_btn, text=tr("tooltip_pp_set_start", "Set start time from current player position"), design=self.design)

        ttk.Label(pp_trim_frame, text=tr("pp_trim_end", "End"), style="Caption.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.XS))

        self.pp_trim_end_var = tk.StringVar(value="00:01:00")
        ttk.Entry(pp_trim_frame, textvariable=self.pp_trim_end_var, width=10, font=(LOADED_FONT_FAMILY, Typography.SIZE_SM)).pack(side=tk.LEFT, padx=(0, Spacing.XS))

        # Issue #31: Capture end time from the current player position
        def _pp_set_trim_end():
            if self.pp_player:
                t = self.pp_player.get_time() or 0.0
                h, r = divmod(int(t), 3600)
                m, s = divmod(r, 60)
                self.pp_trim_end_var.set(f"{h:02d}:{m:02d}:{s:02d}")
        _pp_set_end_btn = ModernButton(
            pp_trim_frame,
            text=tr("pp_set_end", "⏱ Set"),
            command=_pp_set_trim_end,
            variant="ghost",
            size="sm",
            width=6
        )
        _pp_set_end_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(_pp_set_end_btn, text=tr("tooltip_pp_set_end", "Set end time from current player position"), design=self.design)

        _pp_trim_btn = ModernButton(
            pp_trim_frame,
            text=tr("pp_trim", "Trim"),
            command=lambda: self._run_post_process("trim", start_time=self.pp_trim_start_var.get(), end_time=self.pp_trim_end_var.get()),
            variant="primary",
            size="sm",
            width=10
        )
        _pp_trim_btn.pack(side=tk.LEFT)
        Tooltip(_pp_trim_btn, text=tr("tooltip_pp_trim", "Trim to time range (HH:MM:SS format)"), design=self.design)

        # PP Status
        self.pp_status_label = tk.Label(
            pp_card.body, text="",
            bg=self.design.get_color("bg_tertiary"),
            fg=self.design.get_color("fg_secondary"),
            font=(LOADED_FONT_FAMILY, Typography.SIZE_SM)
        )
        self.pp_status_label.pack(anchor="w", pady=(Spacing.XS, 0))

        # === HISTORY TABLE CARD ===
        table_card = ModernCard(main, title=tr("history_records", "Download Records"), design=self.design)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(Spacing.MD, 0))
        
        # Records displayed in a plain frame — outer ScrollableFrame handles scrolling
        history_records_container = ttk.Frame(table_card.body)
        history_records_container.pack(fill=tk.BOTH, expand=True)
        self.history_records_frame = history_records_container
        
        self.refresh_history()

        return frame
    
    def create_settings_tab(self):
        """Create settings configuration section"""
        tr = self.translator.get
        from tkinter import filedialog
        
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable content
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        main = scroll.interior
        main.configure(padding=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("tab_settings", "Settings"),
            subtitle=tr("settings_subtitle", "Configure application preferences"),
            icon="settings"
        ).pack(fill=tk.X, pady=(0, Spacing.LG))
        
        # === GENERAL CARD (Issue #36: Download folder setting) ===
        general_card = ModernCard(main, title=tr("settings_general", "General"), design=self.design, hoverable=True)
        general_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        folder_frame = ttk.Frame(general_card.body)
        folder_frame.pack(fill=tk.X)
        ttk.Label(folder_frame, text=f"📁 {tr('settings_output_folder', 'Download Folder')}:", style="Subtitle.TLabel").pack(anchor=tk.W)
        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill=tk.X, pady=(Spacing.XS, 0))
        self._settings_folder_entry = ttk.Entry(folder_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self._settings_folder_entry.insert(0, str(self.output_dir))
        self._settings_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        
        def _browse_folder():
            from tkinter import filedialog as fld
            chosen = fld.askdirectory(title=tr("header_select_folder", "Select Folder"), initialdir=str(self.output_dir))
            if chosen:
                self._settings_folder_entry.delete(0, tk.END)
                self._settings_folder_entry.insert(0, chosen)
        
        _folder_browse_btn = ModernButton(
            folder_row,
            text=tr("settings_cookies_browse", "Browse..."),
            command=_browse_folder,
            variant="outline", size="sm", width=10
        )
        _folder_browse_btn.pack(side=tk.LEFT)
        Tooltip(_folder_browse_btn, text=tr("tooltip_browse_folder", "Choose download destination folder"), design=self.design)
        ttk.Label(folder_frame, text=tr("settings_output_folder_help", "Where downloaded files are saved"), style="Caption.TLabel").pack(anchor=tk.W)
        # Premiere compatibility setting
        self._settings_premiere_var = tk.BooleanVar(value=self.config_manager.get("premiere_compat", False))
        ttk.Checkbutton(
            general_card.body,
            text=tr("settings_premiere_convert", "Auto-convert for Premiere compatibility"),
            variable=self._settings_premiere_var
        ).pack(anchor=tk.W, pady=(Spacing.SM, 0))
        ttk.Label(
            general_card.body,
            text=tr("settings_premiere_convert_help", "Automatically convert downloaded videos to MP4/H264 suitable for Adobe Premiere"),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # === NETWORK CARD ===
        net_card = ModernCard(main, title=tr("settings_network", "Network"), design=self.design, hoverable=True)
        net_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Proxy
        proxy_frame = ttk.Frame(net_card.body)
        proxy_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        ttk.Label(proxy_frame, text=f"{tr('settings_proxy', 'Proxy URL')}:", style="Subtitle.TLabel").pack(anchor=tk.W)
        self._settings_proxy_entry = ttk.Entry(proxy_frame, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self._settings_proxy_entry.insert(0, self.config_manager.get("proxy", ""))
        self._settings_proxy_entry.pack(fill=tk.X, pady=(Spacing.XS, 0))
        ttk.Label(proxy_frame, text=tr("settings_proxy_help", "HTTP/SOCKS proxy"), style="Caption.TLabel").pack(anchor=tk.W)
        
        # Rate limit
        rate_frame = ttk.Frame(net_card.body)
        rate_frame.pack(fill=tk.X, pady=(Spacing.SM, Spacing.SM))
        ttk.Label(rate_frame, text=f"{tr('settings_rate_limit', 'Speed Limit')}:", style="Subtitle.TLabel").pack(anchor=tk.W)
        self._settings_rate_entry = ttk.Entry(rate_frame, width=15)
        self._settings_rate_entry.insert(0, self.config_manager.get("rate_limit", ""))
        self._settings_rate_entry.pack(anchor=tk.W, pady=(Spacing.XS, 0))
        ttk.Label(rate_frame, text=tr("settings_rate_limit_help", "e.g., 5M, 500K"), style="Caption.TLabel").pack(anchor=tk.W)
        
        # Max retries
        retries_frame = ttk.Frame(net_card.body)
        retries_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        ttk.Label(retries_frame, text=f"{tr('settings_retries', 'Max Retries')}:", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self._settings_retries_var = tk.IntVar(value=self.config_manager.get("max_retries", 3))
        ttk.Spinbox(retries_frame, from_=1, to=10, textvariable=self._settings_retries_var, width=5).pack(side=tk.LEFT)
        
        # Cookie file
        cookie_frame = ttk.Frame(net_card.body)
        cookie_frame.pack(fill=tk.X, pady=(0, 0))
        ttk.Label(cookie_frame, text=f"{tr('settings_cookies', 'Cookie File')}:", style="Subtitle.TLabel").pack(anchor=tk.W)
        cookie_row = ttk.Frame(cookie_frame)
        cookie_row.pack(fill=tk.X, pady=(Spacing.XS, 0))
        self._settings_cookie_entry = ttk.Entry(cookie_row, font=(LOADED_FONT_FAMILY, Typography.SIZE_MD))
        self._settings_cookie_entry.insert(0, self.config_manager.get("cookies_file", ""))
        self._settings_cookie_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))
        _cookie_browse_btn = ModernButton(
            cookie_row,
            text=tr("settings_cookies_browse", "Browse..."),
            command=lambda: self._browse_cookie_file(),
            variant="outline", size="sm", width=10
        )
        _cookie_browse_btn.pack(side=tk.LEFT)
        Tooltip(_cookie_browse_btn, text=tr("tooltip_browse_cookie", "Select a Netscape-format cookie file"), design=self.design)
        
        # === GLOBAL QUALITY CARD (Issues #51, #61) ===
        quality_settings_card = ModernCard(main, title=tr("settings_quality_title", "Global Quality Settings"), design=self.design, hoverable=True)
        quality_settings_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        quality_settings_grid = ttk.Frame(quality_settings_card.body)
        quality_settings_grid.pack(fill=tk.X)
        quality_settings_grid.columnconfigure(1, weight=1)
        
        quality_opts = ["best", "1080", "720", "480", "audio"]
        
        # Live recording quality (Issue #51)
        ttk.Label(quality_settings_grid, text=f"\U0001f534 {tr('settings_live_quality', 'Live Recording Quality')}:", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, Spacing.XS), padx=(0, Spacing.SM)
        )
        self.live_quality_var = tk.StringVar(value=self.config_manager.get("live_quality", "best"))
        live_q_combo = ttk.Combobox(
            quality_settings_grid,
            textvariable=self.live_quality_var,
            values=quality_opts,
            state="readonly",
            width=10
        )
        live_q_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, Spacing.XS))
        ttk.Label(quality_settings_grid, text=tr("settings_live_quality_help", "Default quality for live stream recording"), style="Caption.TLabel").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, Spacing.SM)
        )
        
        # Following auto-download quality (Issue #61)
        ttk.Label(quality_settings_grid, text=f"\U0001f4fa {tr('settings_following_quality', 'Following Auto-Download Quality')}:", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=(0, Spacing.XS), padx=(0, Spacing.SM)
        )
        self.following_quality_var = tk.StringVar(value=self.channel_monitor.get_auto_quality())
        following_q_combo = ttk.Combobox(
            quality_settings_grid,
            textvariable=self.following_quality_var,
            values=quality_opts,
            state="readonly",
            width=10
        )
        following_q_combo.grid(row=2, column=1, sticky=tk.W, pady=(0, Spacing.XS))
        ttk.Label(quality_settings_grid, text=tr("settings_following_quality_help", "Default quality for auto-downloaded channel videos"), style="Caption.TLabel").grid(
            row=3, column=0, columnspan=2, sticky=tk.W
        )
        
        # === ARCHIVE CARD ===
        archive_card = ModernCard(main, title=tr("settings_archive", "Archive & Tracking"), design=self.design, hoverable=True)
        archive_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Enable archive
        self._settings_archive_var = tk.BooleanVar(value=self.config_manager.get("archive_enabled", False))
        ttk.Checkbutton(
            archive_card.body,
            text=tr("archive_enable", "Enable Archive Mode"),
            variable=self._settings_archive_var
        ).pack(anchor=tk.W, pady=(0, Spacing.XS))
        ttk.Label(archive_card.body, text=tr("archive_help", "Track downloaded videos and skip duplicates automatically"), style="Caption.TLabel").pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Archive stats
        archive_path = Path(self.config_manager.config_dir) / "download_archive.txt"
        archive_count = 0
        if archive_path.exists():
            archive_count = sum(1 for _ in open(archive_path, encoding='utf-8', errors='ignore'))
        
        self._archive_count_label = ttk.Label(
            archive_card.body,
            text=tr("archive_count", "{} videos archived").format(archive_count),
            style="Caption.TLabel"
        )
        self._archive_count_label.pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Archive buttons
        archive_btn_frame = ttk.Frame(archive_card.body)
        archive_btn_frame.pack(fill=tk.X)
        
        _archive_export_btn = ModernButton(archive_btn_frame, text=tr("archive_export", "Export"), command=self._export_archive, variant="outline", size="sm", width=10)
        _archive_export_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(_archive_export_btn, text=tr("tooltip_archive_export", "Export download archive to a file"), design=self.design)
        _archive_import_btn = ModernButton(archive_btn_frame, text=tr("archive_import", "Import"), command=self._import_archive, variant="outline", size="sm", width=10)
        _archive_import_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(_archive_import_btn, text=tr("tooltip_archive_import", "Import a previously exported archive file"), design=self.design)
        _archive_clear_btn = ModernButton(archive_btn_frame, text=tr("archive_clear", "Clear"), command=self._clear_archive, variant="danger", size="sm", width=10)
        _archive_clear_btn.pack(side=tk.LEFT)
        Tooltip(_archive_clear_btn, text=tr("tooltip_archive_clear", "Clear all archived video IDs"), design=self.design)
        
        # === QUALITY PROFILES CARD ===
        profile_card = ModernCard(main, title=tr("profile_title", "Quality Profiles"), design=self.design)
        profile_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Profile selector
        profile_row = ttk.Frame(profile_card.body)
        profile_row.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        self._profile_var = tk.StringVar()
        profiles = self.config_manager.get("quality_profiles", {})
        profile_names = list(profiles.keys()) if profiles else []
        
        self._profile_combo = ttk.Combobox(profile_row, textvariable=self._profile_var, values=profile_names, width=25, state="readonly")
        self._profile_combo.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        if profile_names:
            self._profile_combo.current(0)
        
        _profile_load_btn = ModernButton(profile_row, text=tr("profile_load", "Load"), command=self._load_profile, variant="outline", size="sm", width=8)
        _profile_load_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        Tooltip(_profile_load_btn, text=tr("tooltip_profile_load", "Apply selected quality profile to download settings"), design=self.design)
        _profile_delete_btn = ModernButton(profile_row, text=tr("profile_delete", "Delete"), command=self._delete_profile, variant="danger", size="sm", width=8)
        _profile_delete_btn.pack(side=tk.LEFT)
        Tooltip(_profile_delete_btn, text=tr("tooltip_profile_delete", "Delete the selected quality profile"), design=self.design)
        
        # Save new profile
        save_profile_row = ttk.Frame(profile_card.body)
        save_profile_row.pack(fill=tk.X, pady=(0, 0))
        
        self._profile_name_entry = ttk.Entry(save_profile_row, width=25)
        self._profile_name_entry.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self._profile_name_entry.insert(0, tr("profile_name", "Profile Name"))
        self._profile_name_entry.bind("<FocusIn>", lambda e: self._profile_name_entry.delete(0, tk.END) if self._profile_name_entry.get() == tr("profile_name", "Profile Name") else None)
        
        _profile_save_btn = ModernButton(save_profile_row, text=tr("profile_save", "Save Current"), command=self._save_profile, variant="primary", size="sm", width=14)
        _profile_save_btn.pack(side=tk.LEFT)
        Tooltip(_profile_save_btn, text=tr("tooltip_profile_save", "Save current format/quality settings as a named profile"), design=self.design)
        
        # === PER-CHANNEL DEFAULTS CARD ===
        channel_card = ModernCard(main, title=tr("channel_defaults_title", "Per-Channel Defaults"), design=self.design)
        channel_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        ttk.Label(
            channel_card.body,
            text=tr("channel_defaults_help", "Set default quality for specific channels"),
            style="Caption.TLabel"
        ).pack(anchor=tk.W, pady=(0, Spacing.SM))
        
        # Channel defaults list container
        self._channel_defaults_frame = ttk.Frame(channel_card.body)
        self._channel_defaults_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        self._refresh_channel_defaults_ui()
        
        # Add new channel default row
        add_row = ttk.Frame(channel_card.body)
        add_row.pack(fill=tk.X)
        
        self._channel_default_name_entry = ttk.Entry(add_row, width=25)
        self._channel_default_name_entry.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self._channel_default_name_entry.insert(0, tr("channel_defaults_channel", "Channel"))
        self._channel_default_name_entry.bind("<FocusIn>", lambda e: self._channel_default_name_entry.delete(0, tk.END) if self._channel_default_name_entry.get() == tr("channel_defaults_channel", "Channel") else None)
        
        self._channel_default_quality_var = tk.StringVar(value="best")
        ttk.Combobox(
            add_row,
            textvariable=self._channel_default_quality_var,
            values=["best", "1080", "720", "480", "audio"],
            width=10,
            state="readonly"
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        _channel_add_btn = ModernButton(
            add_row,
            text=tr("channel_defaults_add", "Add"),
            command=self._add_channel_default,
            variant="outline", size="sm", width=8
        )
        _channel_add_btn.pack(side=tk.LEFT)
        Tooltip(_channel_add_btn, text=tr("tooltip_channel_add", "Add per-channel quality default"), design=self.design)
        
        # === SAVE BUTTON ===
        save_frame = ttk.Frame(main)
        save_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))
        
        save_btn = ModernButton(
            save_frame,
            text=tr("settings_save", "Save Settings"),
            icon_name="save",
            command=self._save_settings,
            variant="primary",
            size="lg",
            width=18
        )
        save_btn.pack(side=tk.LEFT)
        Tooltip(save_btn, text=tr("tooltip_save_settings", "Save all configuration changes"), design=self.design)

        # Reset to defaults button (Issue #37) — shows detail about what will be reset
        def _confirm_reset():
            detail = (
                f"• {tr('settings_reset_item_theme', 'Theme')} → Dark\n"
                f"• {tr('settings_reset_item_lang', 'Language')} → English\n"
                f"• {tr('settings_reset_item_folder', 'Download folder')} → downloads/\n"
                f"• {tr('settings_reset_item_format', 'Format & quality')} → Best\n"
                f"• {tr('settings_reset_item_cookies', 'Cookies & proxy')} → cleared\n"
                f"• {tr('settings_reset_item_subs', 'Subtitles')} → disabled\n"
                f"• {tr('settings_reset_item_retries', 'Retries & rate limit')} → default\n"
                f"• Premiere compatibility setting will be preserved"
            )
            if messagebox.askyesno(
                tr("settings_reset_title", "Reset to Defaults"),
                f"{tr('settings_reset_msg', 'The following settings will be reset:')}\n\n{detail}\n\n{tr('settings_reset_confirm', 'Continue?')}"
            ):
                self.config_manager.reset_to_defaults()
                self.setup_ui()

        reset_btn = ModernButton(
            save_frame,
            text=tr("settings_reset_btn", "Reset Defaults"),
            icon_name="rotate-ccw",
            command=_confirm_reset,
            variant="ghost",
            size="lg",
        )
        reset_btn.pack(side=tk.LEFT, padx=(Spacing.SM, 0))
        Tooltip(reset_btn, text=tr("tooltip_reset_settings", "Reset all settings to factory defaults"), design=self.design)
        
        return frame
    
    def _save_settings(self):
        tr = self.translator.get
        # Issue #36: save download folder from general card
        new_folder = self._settings_folder_entry.get().strip()
        if new_folder and new_folder != str(self.output_dir):
            self.output_dir = Path(new_folder)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.config_manager.set("output_dir", str(self.output_dir))
        self.config_manager.set("proxy", self._settings_proxy_entry.get().strip())
        self.config_manager.set("rate_limit", self._settings_rate_entry.get().strip())
        self.config_manager.set("max_retries", self._settings_retries_var.get())
        self.config_manager.set("cookies_file", self._settings_cookie_entry.get().strip())
        self.config_manager.set("archive_enabled", self._settings_archive_var.get())
        # when the folder changes we must update dependent components
        self.post_processor.output_dir = self.output_dir
        self.channel_monitor.output_dir = str(self.output_dir)
        # Issues #51/#61: save global quality settings
        self.config_manager.set("live_quality", self.live_quality_var.get())
        self.channel_monitor.set_auto_quality(self.following_quality_var.get())
        # Premiere compatibility toggle
        self.config_manager.set("premiere_compat", self._settings_premiere_var.get())
        self.download_log.add_log(tr("settings_saved", "Settings saved successfully!"))
    
    def _browse_cookie_file(self):
        """Browse for cookie file"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select cookies.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self._settings_cookie_entry.delete(0, tk.END)
            self._settings_cookie_entry.insert(0, path)
    
    def _export_archive(self):
        """Export archive file"""
        from tkinter import filedialog
        tr = self.translator.get
        archive_path = Path(self.config_manager.config_dir) / "download_archive.txt"
        if not archive_path.exists():
            messagebox.showinfo(tr("msg_info", "Info"), tr("archive_count", "{} videos archived").format(0))
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="easycut_archive.txt"
        )
        if dest:
            import shutil
            shutil.copy2(archive_path, dest)
            messagebox.showinfo(tr("msg_info", "Info"), tr("settings_saved", "Exported!"))
    
    def _import_archive(self):
        """Import archive file"""
        from tkinter import filedialog
        tr = self.translator.get
        src = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if src:
            archive_path = Path(self.config_manager.config_dir) / "download_archive.txt"
            # Merge: append imported entries (deduplicate)
            existing = set()
            if archive_path.exists():
                with open(archive_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing = set(line.strip() for line in f if line.strip())
            with open(src, 'r', encoding='utf-8', errors='ignore') as f:
                new_entries = set(line.strip() for line in f if line.strip())
            merged = existing | new_entries
            with open(archive_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(merged)) + '\n')
            count = len(merged)
            self._archive_count_label.config(text=tr("archive_count", "{} videos archived").format(count))
            messagebox.showinfo(tr("msg_info", "Info"), tr("archive_count", "{} videos archived").format(count))
    
    def _clear_archive(self):
        """Clear archive file"""
        tr = self.translator.get
        archive_path = Path(self.config_manager.config_dir) / "download_archive.txt"
        if not archive_path.exists():
            return
        count = sum(1 for _ in open(archive_path, encoding='utf-8', errors='ignore'))
        if messagebox.askyesno(tr("msg_confirm", "Confirm"), tr("archive_cleared", "Clear archive ({} entries)?").format(count)):
            archive_path.unlink()
            self._archive_count_label.config(text=tr("archive_count", "{} videos archived").format(0))
    
    def _save_profile(self):
        """Save current quality/mode settings as a named profile"""
        tr = self.translator.get
        name = self._profile_name_entry.get().strip()
        if not name or name == tr("profile_name", "Profile Name"):
            return
        
        profile = {
            "quality": self.download_quality_var.get(),
            "mode": self.download_mode_var.get(),
            "audio_format": self.audio_format_var.get(),
            "audio_bitrate": self.audio_bitrate_var.get(),
            "subtitles": self.sub_enable_var.get(),
            "sub_type": self.sub_type_var.get(),
            "sub_lang": self.sub_lang_entry.get(),
            "sub_format": self.sub_format_var.get(),
        }
        
        profiles = self.config_manager.get("quality_profiles", {}) or {}
        profiles[name] = profile
        self.config_manager.set("quality_profiles", profiles)
        
        # Refresh combo
        self._profile_combo['values'] = list(profiles.keys())
        self._profile_var.set(name)
        self.download_log.add_log(tr("profile_saved", "Profile '{}' saved").format(name))
    
    def _load_profile(self):
        """Load a saved quality profile"""
        tr = self.translator.get
        name = self._profile_var.get()
        if not name:
            return
        
        profiles = self.config_manager.get("quality_profiles", {}) or {}
        profile = profiles.get(name)
        if not profile:
            return
        
        # Apply settings
        self.download_quality_var.set(profile.get("quality", "best"))
        self.download_mode_var.set(profile.get("mode", "full"))
        self.audio_format_var.set(profile.get("audio_format", "mp3"))
        self.audio_bitrate_var.set(profile.get("audio_bitrate", "320"))
        self.sub_enable_var.set(profile.get("subtitles", False))
        self.sub_type_var.set(profile.get("sub_type", "auto"))
        self.sub_lang_entry.delete(0, tk.END)
        self.sub_lang_entry.insert(0, profile.get("sub_lang", "en"))
        self.sub_format_var.set(profile.get("sub_format", "srt"))
        
        self.download_log.add_log(tr("profile_loaded", "Profile '{}' loaded").format(name))
    
    def _delete_profile(self):
        """Delete a saved quality profile"""
        tr = self.translator.get
        name = self._profile_var.get()
        if not name:
            return
        
        profiles = self.config_manager.get("quality_profiles", {}) or {}
        if name in profiles:
            del profiles[name]
            self.config_manager.set("quality_profiles", profiles)
            self._profile_combo['values'] = list(profiles.keys())
            self._profile_var.set("")
            self.download_log.add_log(tr("profile_deleted", "Profile '{}' deleted").format(name))
    
    def _refresh_channel_defaults_ui(self):
        """Refresh the per-channel defaults display in settings"""
        tr = self.translator.get
        
        for widget in self._channel_defaults_frame.winfo_children():
            widget.destroy()
        
        defaults = self.config_manager.get("channel_defaults", {}) or {}
        
        if not defaults:
            ttk.Label(
                self._channel_defaults_frame,
                text=tr("channel_defaults_none", "No channel defaults configured"),
                style="Caption.TLabel"
            ).pack(anchor=tk.W)
            return
        
        quality_labels = {"best": "Best", "1080": "1080p", "720": "720p", "480": "480p", "audio": "Audio"}
        
        for channel_name, quality in defaults.items():
            row = ttk.Frame(self._channel_defaults_frame)
            row.pack(fill=tk.X, pady=1)
            
            ttk.Label(
                row,
                text=f"📺 {channel_name}",
                style="Subtitle.TLabel"
            ).pack(side=tk.LEFT, padx=(0, Spacing.MD))
            
            ttk.Label(
                row,
                text=f"→ {quality_labels.get(quality, quality)}",
                style="Caption.TLabel"
            ).pack(side=tk.LEFT, padx=(0, Spacing.MD))
            
            ModernButton(
                row,
                text=tr("channel_defaults_remove", "Remove"),
                command=lambda ch=channel_name: self._remove_channel_default(ch),
                variant="ghost", size="sm", width=8
            ).pack(side=tk.RIGHT)
    
    def _add_channel_default(self):
        """Add a per-channel quality default"""
        tr = self.translator.get
        channel_name = self._channel_default_name_entry.get().strip()
        if not channel_name or channel_name == tr("channel_defaults_channel", "Channel"):
            return
        
        quality = self._channel_default_quality_var.get()
        defaults = self.config_manager.get("channel_defaults", {}) or {}
        defaults[channel_name] = quality
        self.config_manager.set("channel_defaults", defaults)
        
        self._channel_default_name_entry.delete(0, tk.END)
        self._refresh_channel_defaults_ui()
    
    def _remove_channel_default(self, channel_name: str):
        """Remove a per-channel quality default"""
        defaults = self.config_manager.get("channel_defaults", {}) or {}
        if channel_name in defaults:
            del defaults[channel_name]
            self.config_manager.set("channel_defaults", defaults)
        self._refresh_channel_defaults_ui()
    
    def _apply_channel_default(self, uploader: str):
        """Check if a channel has a default quality and apply it"""
        if not uploader:
            return
        tr = self.translator.get
        defaults = self.config_manager.get("channel_defaults", {}) or {}
        
        # Case-insensitive match
        for channel_name, quality in defaults.items():
            if channel_name.lower() in uploader.lower() or uploader.lower() in channel_name.lower():
                self.root.after(0, lambda q=quality: self.download_quality_var.set(q))
                self.root.after(0, lambda: self.download_log.add_log(
                    f"⚙️ {tr('channel_defaults_applied', 'Applied channel default: {}').format(quality)}"
                ))
                return
    
    def _show_chapters_ui(self):
        """Show chapters card in download tab after verify detects chapters"""
        tr = self.translator.get
        
        if not self._chapters_info:
            return
        
        # Clear previous chapter list
        for widget in self._chapters_list_frame.winfo_children():
            widget.destroy()
        
        # Show the chapters card
        self._chapters_card_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        ch_count_label = ttk.Label(
            self._chapters_list_frame,
            text=tr("chapters_found", "{} chapters found").format(len(self._chapters_info)),
            style="Subtitle.TLabel"
        )
        ch_count_label.pack(anchor=tk.W, pady=(0, Spacing.XS))
        
        # Show each chapter with time
        for idx, ch in enumerate(self._chapters_info[:20], 1):
            ch_title = ch.get('title', f'Chapter {idx}')
            ch_start = int(ch.get('start_time', 0))
            ch_end = int(ch.get('end_time', 0))
            start_str = self._format_timecode(ch_start)
            end_str = self._format_timecode(ch_end)
            
            ch_row = ttk.Frame(self._chapters_list_frame)
            ch_row.pack(fill=tk.X, pady=1)
            
            ttk.Label(
                ch_row,
                text=f"  {idx}. {ch_title}",
                style="Caption.TLabel"
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                ch_row,
                text=f"  [{start_str} → {end_str}]",
                style="Caption.TLabel"
            ).pack(side=tk.LEFT)
    
    def _download_chapters(self):
        """Download video split by chapters"""
        tr = self.translator.get
        url = self.download_url_entry.get_value().strip()
        
        if not url or not self._chapters_info:
            return
        
        if self.is_downloading:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("download_progress", "Downloading..."))
            return
        
        self.is_downloading = True
        quality = self.download_quality_var.get()
        mode = self.download_mode_var.get()
        chapters = self._chapters_info
        
        if self._chapters_split_var.get():
            # Split mode: download each chapter as separate file
            self.download_log.add_log(f"📖 {tr('chapters_download_all', 'Download All Chapters')} ({len(chapters)})")
            
            def chapters_thread():
                success = 0
                for i, ch in enumerate(chapters, 1):
                    ch_title = ch.get('title', f'Chapter {i}')
                    start_time = ch.get('start_time', 0)
                    end_time = ch.get('end_time', 0)
                    
                    self.root.after(0, lambda t=ch_title, n=i: self.download_log.add_log(
                        tr("chapters_progress", "Downloading chapter {}/{}: {}").format(n, len(chapters), t)
                    ))
                    
                    # Build section dict for chapter time range
                    section_dict = {'start': start_time, 'end': end_time}
                    output_template = str(self.output_dir / f"%(title)s - {ch_title}.%(ext)s")
                    
                    try:
                        base_opts = self._build_download_options(output_template, quality, mode, section=section_dict, quiet=True)
                        ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                        info = self._run_ydl_download(url, ydl_opts)
                        success += 1
                        
                        entry = {
                            "date": datetime.now().isoformat(),
                            "filename": f"{info.get('title', 'unknown')} - {ch_title}",
                            "status": "success",
                            "url": url,
                            "thumbnail": info.get('thumbnail', ''),
                            "video_id": info.get('id', '')
                        }
                        self.config_manager.add_to_history(entry)
                    except Exception as e:
                        self.root.after(0, lambda err=str(e): self.download_log.add_log(
                            f"✗ {self._get_friendly_error(err)[:80]}", "ERROR"
                        ))
                
                self.is_downloading = False
                self.root.after(0, lambda: self.download_log.add_log(
                    f"✓ {tr('chapters_completed', 'All chapters downloaded successfully')} ({success}/{len(chapters)})"
                ))
                self.refresh_history()
            
            thread = threading.Thread(target=chapters_thread, daemon=True)
            thread.start()
        else:
            # Normal download with chapter metadata preserved
            self.is_downloading = False
            self.start_download()
    
    def create_about_tab(self):
        """Create about section"""
        tr = self.translator.get
        frame = ttk.Frame(self.section_container)
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Scrollable container
        scroll = ScrollableFrame(frame, design=self.design)
        scroll.pack(fill=tk.BOTH, expand=True)
        
        # Content frame
        main = ttk.Frame(scroll.interior, padding=Spacing.XXL)
        main.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)
        
        # === SECTION HEADER ===
        SectionHeader(
            main, design=self.design,
            title=tr("about_title", "EasyCut"),
            subtitle=tr("about_subtitle", "Professional YouTube Downloader & Audio Converter"),
            icon="about"
        ).pack(fill=tk.X, pady=(0, Spacing.LG))
        
        # === LEGAL DISCLAIMER — replaced with InfoBanner ===
        InfoBanner(
            main,
            text=tr(
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
            ),
            variant="warning", design=self.design, dismissible=False
        ).pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # === APP INFO CARD — with accent top ===
        info_card = ModernCard(main, title=tr("about_section_info", "Application Info"), design=self.design, accent_top=True)
        info_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        info_data = [
            ("Version", APP_VERSION),
            ("Author", "Deko Costa"),
            ("License", "GPL-3.0"),
            ("Release", str(__import__('datetime').datetime.now().year))
        ]
        
        for label, value in info_data:
            row = ttk.Frame(info_card.body)
            row.pack(fill=tk.X, pady=(0, Spacing.XS))
            ttk.Label(row, text=f"{label}:", style="Subtitle.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style="Caption.TLabel").pack(side=tk.LEFT)
        
        # === SOCIAL LINKS CARD — purple accent ===
        social_card = ModernCard(main, title=tr("about_section_links", "Connect & Support"), design=self.design, hoverable=True,
                                accent_top=True, accent_color=self.design.get_color("purple_primary"))
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
        
        # === TECHNOLOGIES CARD — orange accent ===
        tech_card = ModernCard(main, title=tr("about_section_tech", "Technologies & Credits"), design=self.design, hoverable=True,
                              accent_top=True, accent_color=self.design.get_color("orange_primary"))
        tech_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        tech_data = [
            ("Core", f"Python {sys.version_info.major}.{sys.version_info.minor} + Tkinter"),
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
        
        # === THANKS CARD — rose accent ===
        thanks_card = ModernCard(main, title=tr("about_section_thanks", "Special Thanks"), design=self.design,
                                accent_top=True, accent_color=self.design.get_color("rose_primary"))
        thanks_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        thanks_text = tr(
            "about_thanks_text",
            "Thanks to the open-source community, yt-dlp developers, FFmpeg team, and all contributors who make projects like this possible."
        )
        thanks_label = ttk.Label(
            thanks_card.body,
            text=thanks_text,
            style="Caption.TLabel",
            wraplength=500,
            justify=tk.LEFT
        )
        thanks_label.pack(anchor=tk.W, fill=tk.X)
        # Responsive wraplength — keeps text from overflowing at any window width >= 1100 (Issue #34)
        frame.bind("<Configure>",
                   lambda e, lbl=thanks_label: lbl.config(wraplength=max(250, e.width - 100)),
                   add="+")

        # === FOOTER ===
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=Spacing.LG)
        
        ttk.Label(
            main,
            text=tr("about_footer", f"Made with Python | GPL-3.0 License | {__import__('datetime').datetime.now().year} Deko Costa"),
            style="Caption.TLabel"
        ).pack(pady=Spacing.MD)

        return frame
    
    def apply_theme(self):
        """Apply premium theme to window"""
        style = ttk.Style()
        
        try:
            style.theme_use("clam")
        except Exception:
            pass
        
        self.theme.apply_to_style(style)
        
        bg_color = self.design.get_color("bg_primary")
        fg_color = self.design.get_color("fg_primary")
        bg_input = self.design.get_color("bg_input")
        bg_sec = self.design.get_color("bg_secondary")
        accent = self.design.get_color("accent_primary")
        border = self.design.get_color("border")
        
        self.root.config(bg=bg_color)
        
        # Global option database
        self.root.option_add("*TFrame.background", bg_color)
        self.root.option_add("*TLabel.background", bg_color)
        self.root.option_add("*TLabel.foreground", fg_color)
        self.root.option_add("*Label.background", bg_color)
        self.root.option_add("*Label.foreground", fg_color)
        self.root.option_add("*background", bg_color)
        self.root.option_add("*foreground", fg_color)
        
        # Text + Input colors
        self.root.option_add("*Text.background", bg_input)
        self.root.option_add("*Text.foreground", fg_color)
        self.root.option_add("*Text.insertBackground", fg_color)
        self.root.option_add("*Text.selectBackground", accent)
        self.root.option_add("*Text.selectForeground", self.design.get_color("fg_on_accent"))
        self.root.option_add("*Entry.background", bg_input)
        self.root.option_add("*Entry.foreground", fg_color)
        
        # Combobox dropdown
        self.root.option_add("*TCombobox*Listbox.background", bg_sec)
        self.root.option_add("*TCombobox*Listbox.foreground", fg_color)
        self.root.option_add("*TCombobox*Listbox.selectBackground", accent)
        self.root.option_add("*TCombobox*Listbox.selectForeground", self.design.get_color("fg_on_accent"))
    
    def toggle_theme(self):
        """Toggle theme with instant reload"""
        self.theme.toggle()
        self.design.toggle_mode()
        self.dark_mode = not self.dark_mode
        self.config_manager.set("dark_mode", self.dark_mode)
        set_icon_theme(self.dark_mode)  # Update icon colors
        clear_icon_cache()  # Clear SVG icon cache for new theme colors
        
        # Update pywinstyles backdrop
        if _HAS_PYWINSTYLES:
            try:
                pywinstyles.apply_style(self.root, "dark" if self.dark_mode else "normal")
            except Exception:
                pass
        
        self.apply_theme()
        self.setup_ui()
        self.log_app("✓ Theme changed instantly")
    
    @staticmethod
    def _draw_flag(code, size=24):
        """Draw a simplified geometric flag image using PIL primitives."""
        from PIL import Image, ImageDraw
        h = int(size * 0.67)  # ~2:3 aspect ratio
        img = Image.new('RGBA', (size, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        w = size
        
        if code == 'en':  # UK Union Jack
            d.rectangle([0, 0, w, h], fill='#012169')
            d.line([(0, 0), (w, h)], fill='white', width=3)
            d.line([(w, 0), (0, h)], fill='white', width=3)
            d.line([(0, 0), (w, h)], fill='#C8102E', width=1)
            d.line([(w, 0), (0, h)], fill='#C8102E', width=1)
            d.rectangle([w//2 - 3, 0, w//2 + 2, h], fill='white')
            d.rectangle([0, h//2 - 2, w, h//2 + 2], fill='white')
            d.rectangle([w//2 - 1, 0, w//2 + 1, h], fill='#C8102E')
            d.rectangle([0, h//2 - 1, w, h//2 + 1], fill='#C8102E')
        elif code == 'pt':  # Brazil
            d.rectangle([0, 0, w, h], fill='#009C3B')
            cx, cy = w // 2, h // 2
            d.polygon([(cx, 1), (w - 2, cy), (cx, h - 1), (2, cy)], fill='#FFDF00')
            d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill='#002776')
        elif code == 'es':  # Spain
            s = h // 4
            d.rectangle([0, 0, w, s], fill='#AA151B')
            d.rectangle([0, s, w, h - s], fill='#F1BF00')
            d.rectangle([0, h - s, w, h], fill='#AA151B')
        elif code == 'fr':  # France
            tw = w // 3
            d.rectangle([0, 0, tw, h], fill='#002395')
            d.rectangle([tw, 0, tw * 2, h], fill='#FFFFFF')
            d.rectangle([tw * 2, 0, w, h], fill='#ED2939')
        elif code == 'de':  # Germany
            th = h // 3
            d.rectangle([0, 0, w, th], fill='#000000')
            d.rectangle([0, th, w, th * 2], fill='#DD0000')
            d.rectangle([0, th * 2, w, h], fill='#FFCC00')
        elif code == 'it':  # Italy
            tw = w // 3
            d.rectangle([0, 0, tw, h], fill='#008C45')
            d.rectangle([tw, 0, tw * 2, h], fill='#F4F5F0')
            d.rectangle([tw * 2, 0, w, h], fill='#CD212A')
        elif code == 'ja':  # Japan
            d.rectangle([0, 0, w, h], fill='#FFFFFF')
            cx, cy = w // 2, h // 2
            r = min(w, h) // 3
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill='#BC002D')
        
        # Thin border for definition against dark backgrounds
        d.rectangle([0, 0, w - 1, h - 1], outline='#555555')
        return img

    def _open_lang_dropdown(self):
        """Open a custom dropdown with PIL-drawn flag images for language selection."""
        if hasattr(self, '_lang_popup') and self._lang_popup and self._lang_popup.winfo_exists():
            self._lang_popup.destroy()
            return
        
        bg = self.design.get_color("bg_elevated")
        bg_hover = self.design.get_color("bg_hover")
        fg = self.design.get_color("fg_primary")
        fg_sec = self.design.get_color("fg_secondary")
        border = self.design.get_color("border_subtle")
        accent = self.design.get_color("accent_primary")
        
        # Position below the button
        btn = self._lang_btn
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height() + 2
        
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.configure(bg=border)
        popup.attributes("-topmost", True)
        self._lang_popup = popup
        
        inner = tk.Frame(popup, bg=bg, padx=1, pady=1)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        def _select(code):
            popup.destroy()
            self._lang_popup = None
            self.change_language(code)
        
        for i, (code, name) in enumerate(self._lang_options):
            is_current = (code == self.language)
            row_bg = accent if is_current else bg
            row_fg = "#ffffff" if is_current else fg
            
            row = tk.Frame(inner, bg=row_bg, cursor="hand2")
            row.pack(fill=tk.X)
            
            # Flag image
            if code in self._lang_flag_images:
                flag_lbl = tk.Label(row, image=self._lang_flag_images[code], bg=row_bg)
                flag_lbl.pack(side=tk.LEFT, padx=(8, 4), pady=3)
            
            # Language name
            name_lbl = tk.Label(row, text=name, bg=row_bg, fg=row_fg,
                                font=(Typography.FONT_FAMILY, Typography.SIZE_SM),
                                anchor="w", width=12)
            name_lbl.pack(side=tk.LEFT, padx=(0, 12), pady=3)
            
            # Bind click on all widgets in row
            for w in (row, name_lbl) + ((flag_lbl,) if code in self._lang_flag_images else ()):
                w.bind("<Button-1>", lambda e, c=code: _select(c))
            
            # Hover effect (skip current)
            if not is_current:
                def _enter(e, r=row, nlbl=name_lbl, flbl=None):
                    r.configure(bg=bg_hover)
                    nlbl.configure(bg=bg_hover)
                    if flbl:
                        flbl.configure(bg=bg_hover)
                def _leave(e, r=row, nlbl=name_lbl, rbg=bg, flbl=None):
                    r.configure(bg=rbg)
                    nlbl.configure(bg=rbg)
                    if flbl:
                        flbl.configure(bg=rbg)
                
                flag_widget = flag_lbl if code in self._lang_flag_images else None
                for w in (row, name_lbl) + ((flag_lbl,) if flag_widget else ()):
                    w.bind("<Enter>", lambda e, r=row, n=name_lbl, f=flag_widget: _enter(e, r, n, f))
                    w.bind("<Leave>", lambda e, r=row, n=name_lbl, b=bg, f=flag_widget: _leave(e, r, n, b, f))
        
        # Position and show
        popup.geometry(f"+{x}+{y}")
        popup.update_idletasks()
        
        # Close on click anywhere outside the popup
        def _dismiss_popup(e=None):
            if popup.winfo_exists():
                popup.destroy()
                self._lang_popup = None
                # Unbind the global click handler
                try:
                    self.root.unbind("<Button-1>", self._lang_dismiss_bind_id)
                except Exception:
                    pass
        
        def _on_root_click(e):
            """Close popup when clicking outside it."""
            try:
                # Check if click is inside the popup window
                px, py = popup.winfo_rootx(), popup.winfo_rooty()
                pw, ph = popup.winfo_width(), popup.winfo_height()
                if not (px <= e.x_root <= px + pw and py <= e.y_root <= py + ph):
                    _dismiss_popup()
            except Exception:
                _dismiss_popup()
        
        # Small delay to avoid catching the click that opened the dropdown
        self.root.after(50, lambda: setattr(
            self, '_lang_dismiss_bind_id',
            self.root.bind("<Button-1>", _on_root_click, "+")
        ))
        popup.focus_set()
    
    def change_language(self, lang):
        """Change language with instant reload"""
        if self.translator.set_language(lang):
            self.language = lang
            self.config_manager.set("language", lang)
            self.setup_ui()
            self.log_app(f"✓ Language changed to {lang.upper()}")
    
    def update_login_status(self):
        """Update banner auth label and logout button visibility.
        
        The status bar no longer shows login info (removed to avoid duplication
        with the persistent auth banner). This method only updates the banner
        account_status_label and the logout button.
        """
        try:
            tr = self.translator.get
            if self.oauth_manager.is_authenticated():
                email = self.oauth_manager.get_user_email()
                if email:
                    text = f"✓ {email}"
                else:
                    text = tr("yt_auth_ready", "✓ Authenticated and ready")
                if hasattr(self, 'account_status_label'):
                    self.account_status_label.config(
                        text=text,
                        fg=self.design.get_color("success")
                    )
                # Show logout button in banner
                if hasattr(self, '_logout_btn_widget') and self._logout_btn_widget:
                    self._logout_btn_widget.pack(side=tk.LEFT)
            else:
                text = tr("yt_not_authenticated", "Not authenticated yet")
                if hasattr(self, 'account_status_label'):
                    self.account_status_label.config(
                        text=text,
                        fg=self.design.get_color("fg_secondary")
                    )
                # Hide logout button
                if hasattr(self, '_logout_btn_widget') and self._logout_btn_widget:
                    self._logout_btn_widget.pack_forget()
        except Exception:
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
                    prefs_file = Path(profile_path) / "Preferences"
                    if prefs_file.exists():
                        with open(prefs_file, 'r', encoding='utf-8') as f:
                            prefs = json.load(f)
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
        """Get yt-dlp options with all network settings applied.

        Reads cookie file, proxy, rate-limit and retry settings from the
        user configuration and merges them into *base_opts*.

        Args:
            base_opts (dict): Base options to extend.

        Returns:
            dict: yt-dlp options with network settings configured.
        """
        opts = base_opts.copy() if base_opts else {}

        # --- Cookie file ---
        # Prefer the user-configured path; fall back to the default location.
        custom_cookie = self.config_manager.get("cookies_file", "")
        if custom_cookie and Path(custom_cookie).exists():
            opts['cookiefile'] = str(Path(custom_cookie))
        else:
            default_cookie = Path("config") / "yt_cookies.txt"
            if default_cookie.exists():
                opts['cookiefile'] = str(default_cookie)

        # --- Proxy ---
        proxy = self.config_manager.get("proxy", "")
        if proxy:
            opts['proxy'] = proxy

        # --- Rate limit ---
        rate_limit = self.config_manager.get("rate_limit", "")
        if rate_limit:
            rate_bytes = self._parse_rate_limit(rate_limit)
            if rate_bytes:
                opts['ratelimit'] = rate_bytes

        # --- Retries ---
        retries = self.config_manager.get("max_retries", 3)
        if retries and retries > 0:
            opts['retries'] = retries

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
        url = self.download_url_entry.get_value().strip()
        
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
                verify_opts = self.get_ydl_opts_with_cookies({
                    'quiet': True,
                    'no_warnings': True,
                })
                with yt_dlp.YoutubeDL(verify_opts) as ydl:
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

                # Follow Channel button — show after verify if uploader URL is available (Issue #19)
                uploader_url = info.get('uploader_url', info.get('channel_url', ''))
                self._cached_uploader_url = uploader_url
                if uploader_url:
                    self.root.after(0, lambda: self._follow_channel_btn.grid(
                        row=2, column=2, padx=(Spacing.SM, 0), pady=Spacing.XS
                    ))
                else:
                    self.root.after(0, lambda: self._follow_channel_btn.grid_remove())

                # --- Playlist / Channel info ---
                entries = info.get('entries', None)
                if entries:
                    # This is a playlist/channel — show aggregate info
                    entry_list = list(entries) if not isinstance(entries, list) else entries
                    n_videos = len(entry_list)
                    total_dur = sum(e.get('duration', 0) or 0 for e in entry_list if isinstance(e, dict))
                    if total_dur:
                        t_h, t_rem = divmod(int(total_dur), 3600)
                        t_m, t_s = divmod(t_rem, 60)
                        total_dur_str = f"{t_h}h {t_m:02d}m" if t_h else f"{t_m}m {t_s:02d}s"
                    else:
                        total_dur_str = "-"
                    
                    playlist_msg = tr("playlist_info", "Playlist: {} videos").format(n_videos)
                    dur_msg = tr("playlist_duration", "Total duration: {}").format(total_dur_str)
                    self.root.after(0, lambda: self.download_log.add_log(
                        f"📋 {playlist_msg} | {dur_msg}"
                    ))
                    # Update duration label with total playlist duration
                    self.root.after(0, lambda: self.download_duration_label.config(
                        text=f"{n_videos} videos • {total_dur_str}"
                    ))
                    
                    # --- SMART ROUTE: Auto-populate Batch tab with playlist URLs ---
                    video_urls = []
                    for entry in entry_list:
                        if isinstance(entry, dict):
                            vid_id = entry.get('id', '')
                            vid_url = entry.get('url', '')
                            if not vid_url and vid_id:
                                vid_url = f"https://www.youtube.com/watch?v={vid_id}"
                            if vid_url:
                                video_urls.append(vid_url)
                    
                    if video_urls:
                        def route_to_batch(urls=video_urls, count=n_videos):
                            is_channel = '/channel/' in url or '/@' in url or '/c/' in url or '/user/' in url
                            route_key = "smart_route_channel" if is_channel else "smart_route_playlist"
                            route_msg = tr(route_key, "Playlist detected — sending {} URLs to Batch tab").format(count)
                            self.download_log.add_log(f"🔀 {route_msg}")
                            answer = messagebox.askyesno(
                                tr("tab_batch", "Batch"),
                                route_msg + f"\n\n{tr('live_switch', 'Switch to Batch tab?')}"
                            )
                            if answer:
                                self.batch_text.delete(1.0, tk.END)
                                self.batch_text.insert(tk.END, "\n".join(urls))
                                self._switch_section("batch")
                        self.root.after(0, route_to_batch)
                
                # --- Thumbnail ---
                thumbnail_url = info.get('thumbnail', '')
                if thumbnail_url:
                    self._load_thumbnail(thumbnail_url)
                
                # --- Available Formats ---
                formats = info.get('formats', [])
                self._video_formats = formats
                self._populate_format_combo(formats)
                
                # --- Available Subtitles ---
                subtitles = info.get('subtitles', {})
                auto_subs = info.get('automatic_captions', {})
                all_sub_langs = sorted(set(list(subtitles.keys()) + list(auto_subs.keys())))
                if all_sub_langs:
                    sub_msg = tr("sub_found", "Subtitles found: {}").format(", ".join(all_sub_langs[:20]))
                    self.root.after(0, lambda: self.download_log.add_log(f"📝 {sub_msg}"))
                
                # --- Per-Channel Quality Default ---
                self._apply_channel_default(uploader)
                
                # --- Live Stream Detection ---
                is_live = info.get('is_live', False)
                if is_live:
                    def auto_route_live():
                        route_msg = tr("smart_route_live", "Live stream detected — switching to Live tab")
                        self.download_log.add_log(f"🔴 {route_msg}")
                        self.live_url_entry.delete(0, tk.END)
                        self.live_url_entry.insert(0, url)
                        self._switch_section("live")
                        # Auto-verify the live stream
                        self.verify_live_stream()
                    self.root.after(0, auto_route_live)
                
                # --- YouTube Shorts Detection ---
                is_short = '/shorts/' in url or (duration and duration < 62 and info.get('height', 0) > info.get('width', 0))
                if is_short:
                    self.root.after(0, lambda: self.download_log.add_log(
                        f"📱 {tr('shorts_detected', 'YouTube Short detected')} ({dur_str})"
                    ))
                
                # --- YouTube Chapters ---
                chapters = info.get('chapters', []) or []
                self._chapters_info = chapters
                if chapters:
                    ch_msg = tr("chapters_found", "{} chapters found").format(len(chapters))
                    self.root.after(0, lambda: self.download_log.add_log(f"📖 {ch_msg}"))
                    # Show chapter list in log
                    for idx, ch in enumerate(chapters[:15], 1):
                        ch_title = ch.get('title', f'Chapter {idx}')
                        ch_start = int(ch.get('start_time', 0))
                        ch_end = int(ch.get('end_time', 0))
                        ch_dur = self._format_timecode(ch_end - ch_start)
                        self.root.after(0, lambda t=ch_title, d=ch_dur, n=idx: 
                            self.download_log.add_log(f"  {n}. {t} ({d})")
                        )
                    self.root.after(0, self._show_chapters_ui)
                else:
                    self._chapters_info = []
                    # Hide chapters UI if present
                    if hasattr(self, '_chapters_card_frame'):
                        self.root.after(0, lambda: self._chapters_card_frame.pack_forget())
                
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
        self._format_id_map = {0: None}  # Maps display index to format_id
        
        # Categorize and sort formats
        video_audio = []
        video_only = []
        audio_only = []
        
        for f in formats:
            fmt_id = f.get('format_id', '?')
            ext = f.get('ext', '?')
            # if premiere compatibility is enabled don't even show webm options
            if self.config_manager.get("premiere_compat", False) and ext.lower() == 'webm':
                continue
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
        
        # remember user's selection if possible
        previous = None
        try:
            previous = self._get_selected_format_id()
        except Exception:
            previous = None

        def update_ui():
            self.format_combo['values'] = format_options
            # restore previous selection when still available
            if previous:
                for idx, fid in self._format_id_map.items():
                    if fid == previous:
                        self.format_combo.current(idx)
                        break
                else:
                    self.format_combo.current(0)
            else:
                self.format_combo.current(0)
            self.format_status_label.config(text=status)
            # When a specific format is chosen, dim quality radios to hint
            # they won't take effect; when Auto is chosen, re-enable them.
            self._on_format_selected()
        
        self.root.after(0, update_ui)
    
    def _get_selected_format_id(self):
        """Get the yt-dlp format ID from the combobox selection, or None for auto.

        Returns ``None`` when the current selection is Auto or a category
        separator, meaning the quality preset should be used instead.
        """
        if not hasattr(self, '_format_id_map'):
            return None
        idx = self.format_combo.current()
        fmt_id = self._format_id_map.get(idx)
        return fmt_id

    # --- helpers for UI interactions ------------------------------------------------
    def _on_format_selected(self, event=None):
        """Callback when user picks an item from the format combobox.

        When a specific format is selected (not Auto and not a separator),
        dim the quality preset radios to signal they won't take effect.
        When Auto is re-selected, restore the quality radios.
        """
        if not hasattr(self, 'format_combo'):
            return
        fmt_id = self._get_selected_format_id()
        if fmt_id is not None:
            # A real format was selected — disable quality presets
            self._set_quality_radios_state('disabled')
        else:
            # Auto or separator — quality presets are in charge
            self._set_quality_radios_state('normal')

    def _on_quality_change(self):
        """Called when the quality radio variable changes.

        If the user switches quality manually, revert the format combo
        back to Auto (index 0) so the quality preset takes effect.
        """
        if hasattr(self, 'format_combo') and self.download_quality_var.get() != 'auto':
            self.format_combo.current(0)
            self._set_quality_radios_state('normal')

    def _set_quality_radios_state(self, state: str):
        """Enable/disable quality radio widgets."""
        for rb in getattr(self, '_quality_radios', []):
            try:
                rb.config(state=state)
            except Exception:
                pass

    def _make_progress_label(self, parent, attr: str = 'download_progress_label'):
        """Utility to create a styled progress label attached to a parent frame.
        Stores the reference on ``self`` under the given attribute name and
        returns the label widget.  Used by download and batch tabs.
        """
        lbl = tk.Label(
            parent,
            text="",
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_secondary"),
            font=(LOADED_FONT_FAMILY, Typography.SIZE_SM)
        )
        setattr(self, attr, lbl)
        lbl.pack(side=tk.LEFT, padx=(Spacing.MD, 0))
        return lbl
    
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
    def _parse_rate_limit(rate_text: str):
        """Parse rate-limit strings like '100', '1.5K', '2M' into numeric bytes/sec.
        Uses binary multiples (1K = 1024).
        Returns float or None on failure.
        """
        if not rate_text or not isinstance(rate_text, str):
            return None
        try:
            unit = rate_text[-1].upper()
            if unit == 'K':
                return float(rate_text[:-1]) * 1024
            if unit == 'M':
                return float(rate_text[:-1]) * (1024 ** 2)
            return float(rate_text)
        except Exception:
            return None

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

        return {'start': start_seconds, 'end': end_seconds}

    def _build_download_options(self, output_template: str, quality: str, mode: str, section: dict = None, quiet: bool = False, format_id: str = None):
        """Create yt-dlp options for a download."""
        # If a specific format_id was selected from the format combo, use it directly
        if format_id:
            format_str = format_id
        else:
            # build format string based on quality presets; if premiere compatibility
            # is enabled we also avoid webm in the fallback branch.  note that the
            # mp4 preset previously fell back to an unrestricted 'best' which could
            # return webm, so replace that with a non-webm fallback.
            tr = self.translator.get
            exclude_webm = "[ext!=webm]" if self.config_manager.get("premiere_compat", False) else ""
            format_map = {
                # exclude webm in every part unless explicit mp4
                'best': f'bestvideo{exclude_webm}+bestaudio{exclude_webm}/best{exclude_webm}',
                # mp4 preset is strict: only mp4 video+audio, no fallback to webm at
                # higher bitrate/resolution
                'mp4': f'bestvideo[ext=mp4]{exclude_webm}+bestaudio[ext=mp4]{exclude_webm}/best[ext=mp4]{exclude_webm}',
                '1080': f'bestvideo[height<=1080]{exclude_webm}+bestaudio{exclude_webm}/best[height<=1080]{exclude_webm}',
                '720': f'bestvideo[height<=720]{exclude_webm}+bestaudio{exclude_webm}/best[height<=720]{exclude_webm}',
                'audio': f'bestaudio{exclude_webm}/best{exclude_webm}'
            }
            format_str = format_map.get(quality, f'bestvideo{exclude_webm}+bestaudio{exclude_webm}/best{exclude_webm}')


        base_opts = {
            'format': format_str,
            'outtmpl': output_template,
            'quiet': quiet,
            'no_warnings': True,          # suppress Deno + JS-engine noise (Issue #23)
            'logger': _YTLogger(),        # custom logger filters non-critical warnings (Issue #23)
            'progress_hooks': [self.download_progress_hook],
        }

        # Audio mode: add FFmpeg postprocessor so the user's format/bitrate
        # selection (mp3, wav, m4a, opus) is actually honoured.
        if mode == 'audio':
            audio_fmt = self.audio_format_var.get()   # mp3 / wav / m4a / opus
            audio_br = self.audio_bitrate_var.get()   # 128 / 192 / 256 / 320
            base_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_fmt,
                'preferredquality': audio_br,
            }]

        # Playlist / channel handling
        if mode in ('playlist', 'channel'):
            base_opts['noplaylist'] = False
            # For channel mode, limit to the N latest videos the user chose
            if mode == 'channel' and hasattr(self, '_channel_limit_var') and self._channel_limit_var is not None:
                try:
                    limit = int(self._channel_limit_var.get())
                    if 1 <= limit <= 500:
                        base_opts['playlistend'] = limit
                except (ValueError, TypeError):
                    pass
        else:
            base_opts['noplaylist'] = True

        # Subtitle options — honour the UI checkboxes
        if self.sub_enable_var.get():
            sub_type = self.sub_type_var.get()       # auto / manual / both
            sub_fmt  = self.sub_format_var.get()     # srt / vtt / ass / json3
            sub_lang = self.sub_lang_entry.get().strip() or 'en'
            sub_langs = [s.strip() for s in sub_lang.split(',') if s.strip()]

            if sub_type in ('manual', 'both'):
                base_opts['writesubtitles'] = True
            if sub_type in ('auto', 'both'):
                base_opts['writeautomaticsub'] = True
            base_opts['subtitlesformat'] = sub_fmt
            base_opts['subtitleslangs'] = sub_langs

            # Embed subtitles into the video file if requested
            if self.sub_embed_var.get():
                base_opts.setdefault('postprocessors', []).append({
                    'key': 'FFmpegEmbedSubtitle',
                    'already_have_subtitle': False,
                })

        # Time range / section download
        if section:
            s_start = section.get('start', 0)
            s_end = section.get('end', None)
            base_opts['download_ranges'] = lambda info, ydl, _s=s_start, _e=s_end: [
                {'start_time': _s, 'end_time': _e}
            ]
            base_opts['force_keyframes_at_cuts'] = True

        return base_opts

    def download_transcript(self):
        """Download text transcript with timestamps (TXT) for the current URL.

        Uses yt-dlp to fetch automatically generated or manual subtitles and
        saves as a .txt file in the output directory.  WebM formats are
        excluded by default through format rules.
        """
        tr = self.translator.get
        url = self.download_url_entry.get_value().strip()
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return

        if not YT_DLP_AVAILABLE:
            messagebox.showerror(tr("msg_error", "Error"), "yt-dlp not available")
            return

        self.download_log.add_log(f"📝 {tr('download_transcript_btn', 'Downloading transcript...')}")  # reuse status label


        def _thread():
            try:
                opts = {
                    'outtmpl': str(self.output_dir / '%(title)s-%(id)s.%(ext)s'),
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'skip_download': True,
                    'subtitlesformat': 'vtt',
                    'subtitleslangs': [self.sub_lang_entry.get().strip() or 'en'],
                }
                ydl_opts = self.get_ydl_opts_with_cookies(opts)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                # find .vtt file and convert to .txt
                recent = sorted(self.output_dir.glob('*'), key=lambda f: f.stat().st_mtime, reverse=True)
                for f in recent:
                    if f.suffix.lower() == '.vtt':
                        txt = f.with_suffix('.txt')
                        try:
                            with open(f, 'r', encoding='utf-8') as vf, open(txt, 'w', encoding='utf-8') as tf:
                                for line in vf:
                                    tf.write(line)
                            self.root.after(0, lambda name=txt.name: self.download_log.add_log(f"✅ {tr('download_transcript_btn', 'Transcript saved')}: {name}"))
                        except Exception as vtt_err:
                            self.root.after(0, lambda msg=str(vtt_err): self.download_log.add_log(f"⚠️ VTT conversion failed: {msg}", "WARNING"))
                        break
            except Exception as e:
                self.root.after(0, lambda msg=str(e): self.download_log.add_log(f"❌ {tr('msg_error', 'Error')}: {msg}", "ERROR"))

        threading.Thread(target=_thread, daemon=True).start()

    def _run_ydl_download(self, url: str, ydl_opts: dict):
        """Run yt-dlp download with a concurrency limit.

        After the download completes we optionally convert the file to a
        Premiere-compatible MP4/H264 format if the user has enabled the
        "premiere_compat" toggle in settings.  This keeps the conversion
        logic centralized for both single and batch downloads.
        """
        with self.download_semaphore:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Resolve the downloaded file path while ydl is still in scope
                path = info.get('_filename') or None
                if not path:
                    # Fall back to requested_downloads list (reliable in modern yt-dlp)
                    rd = info.get('requested_downloads')
                    if rd and isinstance(rd, list) and rd[0].get('filepath'):
                        path = rd[0]['filepath']
                    else:
                        try:
                            path = ydl.prepare_filename(info)
                        except Exception:
                            path = None
                info['_filename'] = path  # cache for callers
        if self.config_manager.get("premiere_compat", False):
            if path and Path(path).exists():
                if not self.post_processor.is_premiere_compatible(path):
                    tr = self.translator.get
                    self.download_log.add_log(tr('log_premiere_converting', 'Converting to Premiere-compatible format...'))
                    newpath = self.post_processor.convert_for_premiere(path)
                    if newpath:
                        info['_filename'] = newpath
                        self.download_log.add_log(tr('log_premiere_converted', 'Conversion complete'))
        else:
            # if user didn't ask for conversion but result is incompatible, warn
            if path and Path(path).exists() and not self.post_processor.is_premiere_compatible(path):
                tr = self.translator.get
                self.download_log.add_log(
                    tr('log_premiere_warn',
                       'Downloaded file is not Premiere-compatible; enable conversion in settings.'),
                    "WARNING"
                )
        return info
    
    def download_progress_hook(self, d):
        """Progress hook for yt-dlp — updates download progress label in the UI.
        
        Also checks the is_downloading flag to support cancellation via stop_download().
        When is_downloading is False, raises an exception to abort yt-dlp.
        """
        # Cancellation check — yt-dlp calls the hook frequently so this
        # provides a responsive stop mechanism
        if not self.is_downloading:
            raise Exception("Download cancelled by user")
        
        if not hasattr(self, 'download_progress_label'):
            return
        status = d.get('status')
        if status == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            if percent:
                parts = [percent]
                if speed and speed != 'Unknown B/s':
                    parts.append(speed)
                if eta and eta != 'Unknown':
                    parts.append(f"ETA {eta}")
                display = '  '.join(parts)
                # update whichever labels are present so user sees progress
                def _upd(p=display):
                    if hasattr(self, 'download_progress_label'):
                        self.download_progress_label.config(text=p)
                    if hasattr(self, 'batch_progress_label'):
                        self.batch_progress_label.config(text=p)
                self.root.after(0, _upd)
        elif status == 'finished':
            def _done():
                txt = self.translator.get('download_done', '✓ Done')
                if hasattr(self, 'download_progress_label'):
                    self.download_progress_label.config(text=txt)
                if hasattr(self, 'batch_progress_label'):
                    self.batch_progress_label.config(text=txt)
            self.root.after(0, _done)
        elif status == 'error':
            def _err():
                txt = self.translator.get('download_failed', '✗ Error')
                if hasattr(self, 'download_progress_label'):
                    self.download_progress_label.config(text=txt)
                if hasattr(self, 'batch_progress_label'):
                    self.batch_progress_label.config(text=txt)
            self.root.after(0, _err)

    def start_download(self):
        """Start downloading video"""
        tr = self.translator.get
        url = self.download_url_entry.get_value().strip()
        
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
        
        # reload output directory in case user changed it without saving
        self.output_dir = Path(self.config_manager.get("output_dir", str(self.output_dir)))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # keep post_processor and monitor in sync
        self.post_processor.output_dir = self.output_dir
        self.channel_monitor.output_dir = str(self.output_dir)

        self.is_downloading = True
        # Clear progress label(s) for the new download
        if hasattr(self, 'download_progress_label'):
            self.download_progress_label.config(text="")
        if hasattr(self, 'batch_progress_label'):
            self.batch_progress_label.config(text="")
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
                
                # log chosen format in case users report it being ignored
                self.logger.info(f"  Selected format_id: {selected_format_id}")
                info = self._run_ydl_download(url, ydl_opts)
                # sanity check: if user chose mp4 quality but resulting ext isn't mp4,
                # log a warning so we can debug further.
                if quality == 'mp4' and info.get('ext') and info.get('ext').lower() != 'mp4':
                    self.logger.warning("quality=mp4 but downloaded ext=%s", info.get('ext'))
                    self.download_log.add_log(
                        tr('log_quality_mismatch', 'Requested MP4 quality but downloaded {}.').format(info.get('ext','')), 
                        "WARNING"
                    )

                entry = {
                    "date": datetime.now().isoformat(),
                    "filename": info.get('title', 'unknown'),
                    "status": "success",
                    "url": url,
                    "thumbnail": info.get('thumbnail', ''),
                    "video_id": info.get('id', ''),
                    "is_live": info.get('is_live', False) or False,
                }
                self.config_manager.add_to_history(entry)
                
                # Structured logging
                self.logger.info(f"Download completed: {info.get('title', 'unknown')}")
                self.logger.info(f"  File: {info.get('_filename', 'unknown')}")

                self.download_log.add_log(tr("download_success", "Download completed successfully!"))
                self.refresh_history()
            
            except Exception as e:
                error_msg = str(e)
                # Detect user-initiated cancellation — don't treat as error
                if not self.is_downloading or 'cancelled by user' in error_msg.lower():
                    self.logger.info(f"Download cancelled: {url}")
                    self.download_log.add_log(tr("download_stop", "Download cancelled"))
                else:
                    # Structured logging
                    self.logger.error(f"Download failed: {url}")
                    self.logger.error(f"  Error: {error_msg}")
                    
                    # User-friendly error message
                    friendly = self._get_friendly_error(error_msg)
                    self.download_log.add_log(f"{tr('msg_error', 'Error')}: {friendly}", "ERROR")
                    
                    # Add failed entry to history only for real errors
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": url[:50],
                        "status": "error",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
            
            finally:
                self.is_downloading = False
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def stop_download(self):
        """Stop current download by setting cancellation flag.
        
        The progress hook checks is_downloading and raises an exception
        to abort the yt-dlp download when the flag is cleared.
        """
        tr = self.translator.get
        self.is_downloading = False
        self.download_log.add_log(tr("download_stop", "Download cancelled"))
        self.logger.info("Download cancelled by user")
    
    def _get_friendly_error(self, error_msg: str) -> str:
        """Map common yt-dlp errors to user-friendly translated messages"""
        tr = self.translator.get
        error_lower = error_msg.lower()
        
        # Pattern → i18n key mapping (order matters — first match wins)
        patterns = [
            (["private video", "video is private"], "err_private"),
            (["sign in to confirm your age", "age-restricted", "age restricted"], "err_age_restricted"),
            (["video unavailable", "this video has been removed", "this video is no longer available", "video is not available"], "err_unavailable"),
            (["geo", "not available in your country", "blocked in your country", "available in your country"], "err_geo_blocked"),
            (["premieres in", "scheduled for", "live event will begin"], "err_live_not_started"),
            (["http error 429", "too many requests", "rate limit"], "err_rate_limited"),
            (["unable to download", "connection", "timed out", "urlopen error", "network is unreachable"], "err_network"),
            (["no video formats", "requested format not available", "no suitable format"], "err_no_formats"),
            (["postprocessing", "ffmpeg", "ffprobe"], "err_ffmpeg_post"),
            (["copyright", "copyrighted"], "err_copyright"),
            (["join this channel", "members-only", "members only"], "err_members_only"),
            (["premium", "youtube red"], "err_premium_only"),
            (["could not copy", "cookie database"], "browser_test_browser_open"),
        ]
        
        for keywords, key in patterns:
            if any(kw in error_lower for kw in keywords):
                return tr(key, error_msg[:100])
        
        # Fallback: truncated original message
        return f"{tr('err_unknown', 'An unexpected error occurred.')}\n{error_msg[:120]}"
    
    def on_closing(self):
        """Handle application closing gracefully"""
        tr = self.translator.get
        
        # Check if downloads or live recording are active
        active = self.is_downloading or getattr(self, 'is_recording', False)
        if active:
            response = messagebox.askyesnocancel(
                tr("msg_confirm", "Confirm"),
                tr("msg_download_active", "Downloads are in progress. Close anyway?")
            )
            if not response:  # User clicked No or Cancel
                return
        
        # Stop active live recording via the existing cancellation flag
        if getattr(self, 'is_recording', False):
            try:
                self._live_user_cancelled = True
                self.is_recording = False
            except Exception:
                pass
        
        # Log shutdown
        self.logger.info("Application shutdown initiated")
        
        # Save current config
        try:
            self.config_manager.set("output_dir", str(self.output_dir))
            self.config_manager.set("language", self.language)
            # Save Premiere toggle state even if user didn't hit 'Save'
            try:
                self.config_manager.set("premiere_compat", self._settings_premiere_var.get())
            except Exception:
                pass
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
        
        # Final log
        self.logger.info("EasyCut Application Closed")
        self.logger.info("="*60)
        
        # Stop channel monitor
        try:
            self.channel_monitor.stop_monitoring()
        except Exception:
            pass
        
        # Cancel any active post-processing
        try:
            self.post_processor.cancel()
        except Exception:
            pass
        
        # Cleanup embedded video player
        try:
            if self.embedded_player:
                self.embedded_player.cleanup()
        except Exception:
            pass
        
        # Cleanup post-processing video player
        try:
            if self.pp_player:
                self.pp_player.cleanup()
        except Exception:
            pass
        
        # Destroy window
        self.root.destroy()
    
    def _batch_verify_all(self):
        """Fetch title/duration/format info for all URLs in the batch list (Issue #42)"""
        tr = self.translator.get
        urls_text = self.batch_text.get(1.0, tk.END).strip()
        if not urls_text:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("batch_empty", "Add at least one URL"))
            return
        urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
        if not urls:
            return
        self.batch_log.add_log(f"🔍 {tr('batch_verifying_all', 'Verifying {} URL(s)...').format(len(urls))}")
        import threading, yt_dlp as _ydl_mod
        def _run():
            for i, url in enumerate(urls, 1):
                prefix = f"[{i}/{len(urls)}]"
                try:
                    base_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True,
                            'logger': _YTLogger()}
                    opts = self.get_ydl_opts_with_cookies(base_opts)
                    with _ydl_mod.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                    title = info.get('title', url)[:50]
                    duration = info.get('duration')
                    dur_str = f" [{int(duration//60)}:{int(duration%60):02d}]" if duration else ""
                    self.root.after(0, lambda p=prefix, t=title, d=dur_str:
                        self.batch_log.add_log(f"  ✅ {p} {t}{d}"))
                except Exception as e:
                    self.root.after(0, lambda p=prefix, u=url, err=str(e):
                        self.batch_log.add_log(f"  ❌ {p} {u[:40]} — {err[:60]}"))
            self.root.after(0, lambda: self.batch_log.add_log(
                f"✔ {tr('batch_verify_done', 'Verification complete')}"))
        threading.Thread(target=_run, daemon=True).start()

    def start_batch_download(self):
        """Start batch download with queue management"""
        tr = self.translator.get
        urls_text = self.batch_text.get(1.0, tk.END).strip()
        
        if not urls_text:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("batch_empty", "Add at least one URL"))
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # reload output directory just in case (similar to single download)
        self.output_dir = Path(self.config_manager.get("output_dir", str(self.output_dir)))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.post_processor.output_dir = self.output_dir
        self.channel_monitor.output_dir = str(self.output_dir)

        # Get current download mode and quality from UI
        quality = self.download_quality_var.get()
        mode = self.download_mode_var.get()
        self.logger.info(f"Batch selected quality={quality} mode={mode}")
        
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
        
        # Initialize download queue
        self._download_queue = []
        self._queue_paused = False
        for url in urls:
            self._download_queue.append({
                "url": url,
                "status": "queued",
                "title": url[:50],
            })
        self._refresh_queue_ui()
        
        self.is_downloading = True
        # clear any previous progress indications
        if hasattr(self, 'download_progress_label'):
            self.download_progress_label.config(text="")
        if hasattr(self, 'batch_progress_label'):
            self.batch_progress_label.config(text="")
        self.batch_log.add_log(f"{tr('batch_progress', 'Downloading batch')} ({len(urls)})")  # removed duplicate below
        self.logger.info(f"Batch download started: {len(urls)} URLs")
        self.logger.info(f"  Quality: {quality}, Mode: {mode}")
        
        def batch_thread():
            success = 0
            _total = len(self._download_queue)

            def _batch_item_hook(d, idx=0):
                if d.get("status") == "downloading":
                    pct = d.get("_percent_str", "").strip()
                    spd = d.get("_speed_str", "").strip()
                    eta = d.get("eta", "")
                    msg = f"[{idx+1}/{_total}] {pct}"
                    if spd:
                        msg += f" | {spd}"
                    if eta:
                        msg += f" | ETA {eta}s"
                    def _upd(m=msg):
                        if hasattr(self, "batch_progress_label"):
                            try:
                                self.batch_progress_label.config(text=m)
                            except tk.TclError:
                                pass
                    self.root.after(0, _upd)

            for i, item in enumerate(self._download_queue):
                # Check if stopped
                if not self.is_downloading and i > 0:
                    break
                
                # Pause support — wait while paused
                while self._queue_paused:
                    import time
                    time.sleep(0.5)
                    if not self.is_downloading:
                        break
                
                url = item["url"]
                
                if not self.is_valid_youtube_url(url):
                    item["status"] = "failed"
                    item["title"] = f"Invalid URL: {url[:40]}"
                    self.root.after(0, self._refresh_queue_ui)
                    self.batch_log.add_log(f"[{i+1}/{len(self._download_queue)}] {tr('download_invalid_url', 'Invalid URL')}", "WARNING")
                    continue
                
                if not YT_DLP_AVAILABLE:
                    self.batch_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR")
                    break
                
                item["status"] = "downloading"
                self.root.after(0, self._refresh_queue_ui)
                
                try:
                    output_template = str(self.output_dir / "%(title)s.%(ext)s")
                    # respect specific format id if chosen
                    selected_format_id = self._get_selected_format_id()
                    self.logger.info(f"  Selected format_id (batch): {selected_format_id}")
                    base_opts = self._build_download_options(output_template, quality, mode, section=section, quiet=True, format_id=selected_format_id)
                    # Attach per-item progress hook (preserves existing hooks)
                    base_opts.setdefault("progress_hooks", [])
                    base_opts["progress_hooks"].append(lambda d, idx=i: _batch_item_hook(d, idx))
                    ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                    
                    info = self._run_ydl_download(url, ydl_opts)
                    # same sanity check for batch
                    if quality == 'mp4' and info.get('ext') and info.get('ext').lower() != 'mp4':
                        self.logger.warning("batch quality=mp4 but downloaded ext=%s", info.get('ext'))
                        self.batch_log.add_log(
                            tr('log_quality_mismatch', 'Requested MP4 quality but downloaded {}.').format(info.get('ext','')), 
                            "WARNING"
                        )
                    success += 1
                    item["status"] = "completed"
                    item["title"] = info.get('title', 'Video')[:50]
                    self.root.after(0, self._refresh_queue_ui)
                    self.batch_log.add_log(f"[{i+1}/{len(self._download_queue)}] ✓ {item['title'][:30]}")
                    
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": info.get('title', 'unknown'),
                        "status": "success",
                        "url": url,
                        "thumbnail": info.get('thumbnail', ''),
                        "video_id": info.get('id', '')
                    }
                    self.config_manager.add_to_history(entry)
                
                except Exception as e:
                    error_msg = str(e)
                    friendly = self._get_friendly_error(error_msg)
                    item["status"] = "failed"
                    self.root.after(0, self._refresh_queue_ui)
                    self.batch_log.add_log(f"[{i+1}/{len(self._download_queue)}] ✗ {friendly[:80]}", "ERROR")
                    
                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": url[:50],
                        "status": "error",
                        "url": url
                    }
                    self.config_manager.add_to_history(entry)
                    
                    if "could not copy" in error_msg.lower() and "cookie" in error_msg.lower():
                        break
            
            self.batch_log.add_log(f"Batch complete: {success}/{len(self._download_queue)} successful")
            self.logger.info(f"Batch download completed: {success}/{len(self._download_queue)} successful")
            self.is_downloading = False
            def _clear_batch_progress():
                if hasattr(self, "batch_progress_label"):
                    try:
                        self.batch_progress_label.config(text="")
                    except tk.TclError:
                        pass
            self.root.after(0, _clear_batch_progress)
            self.root.after(0, self._refresh_queue_ui)
            self.refresh_history()
        
        thread = threading.Thread(target=batch_thread, daemon=True)
        thread.start()
    
    def _refresh_queue_ui(self):
        """Refresh the visual queue list"""
        tr = self.translator.get
        
        if not hasattr(self, 'queue_list_frame'):
            return
        
        for widget in self.queue_list_frame.winfo_children():
            widget.destroy()
        
        status_emoji = {
            "queued": "⏳",
            "downloading": "⬇️",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
        }
        status_color = {
            "queued": self.design.get_color("fg_secondary"),
            "downloading": self.design.get_color("accent_primary"),
            "completed": self.design.get_color("success"),
            "failed": self.design.get_color("error"),
            "paused": self.design.get_color("warning"),
        }
        
        completed = sum(1 for item in self._download_queue if item["status"] == "completed")
        total = len(self._download_queue)
        self.queue_progress_label.config(
            text=tr("queue_progress", "{} of {} completed").format(completed, total)
        )
        
        for i, item in enumerate(self._download_queue):
            row_frame = tk.Frame(
                self.queue_list_frame,
                bg=self.design.get_color("bg_tertiary"),
            )
            row_frame.pack(fill=tk.X, pady=1, padx=Spacing.XS)
            
            # Status emoji
            tk.Label(
                row_frame,
                text=status_emoji.get(item["status"], "❓"),
                font=("Segoe UI Emoji", 11),
                bg=self.design.get_color("bg_tertiary"),
                fg=status_color.get(item["status"], self.design.get_color("fg_primary")),
            ).pack(side=tk.LEFT, padx=(Spacing.SM, Spacing.XS))
            
            # Title / URL
            tk.Label(
                row_frame,
                text=f"{i+1}. {item['title'][:55]}",
                font=(LOADED_FONT_FAMILY, Typography.SIZE_SM),
                bg=self.design.get_color("bg_tertiary"),
                fg=self.design.get_color("fg_primary"),
                anchor="w",
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Status text
            status_text = tr(f"queue_{item['status']}", item["status"].title())
            tk.Label(
                row_frame,
                text=status_text,
                font=(LOADED_FONT_FAMILY, Typography.SIZE_TINY),
                bg=self.design.get_color("bg_tertiary"),
                fg=status_color.get(item["status"], self.design.get_color("fg_secondary")),
            ).pack(side=tk.RIGHT, padx=Spacing.SM)
    
    def _queue_toggle_pause(self):
        """Toggle pause/resume for the download queue"""
        self._queue_paused = not self._queue_paused
        tr = self.translator.get
        if self._queue_paused:
            self.batch_log.add_log(tr("queue_paused", "Paused"))
            # Mark currently queued items as paused visually
            for item in self._download_queue:
                if item["status"] == "queued":
                    item["status"] = "paused"
        else:
            self.batch_log.add_log(tr("queue_resume", "Resume Queue"))
            for item in self._download_queue:
                if item["status"] == "paused":
                    item["status"] = "queued"
        self._refresh_queue_ui()
    
    def _queue_clear_completed(self):
        """Remove completed items from the download queue"""
        self._download_queue = [item for item in self._download_queue if item["status"] != "completed"]
        self._refresh_queue_ui()
    
    def batch_paste(self):
        """Paste from clipboard"""
        tr = self.translator.get
        try:
            data = self.root.clipboard_get()
            self.batch_text.insert(tk.END, data)
        except Exception as e:
            messagebox.showerror(tr("msg_error", "Error"), f"{tr('msg_error', 'Error')}: {e}")
    
    # ──────────────────────────────────────────
    # POST-PROCESSING METHODS
    # ──────────────────────────────────────────

    def _pp_select_file(self):
        """Open file dialog to select a file for post-processing"""
        tr = self.translator.get
        filepath = filedialog.askopenfilename(
            title=tr("pp_select_file", "Select a file to process"),
            initialdir=str(self.output_dir),
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.flv"),
                ("Audio files", "*.mp3 *.wav *.m4a *.opus *.ogg *.flac"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.pp_file_var.set(filepath)
            # Issue #29: Load the selected file in the embedded PP player
            if self.pp_player:
                self.pp_player.load(filepath, is_file=True)

    def _run_post_process(self, operation: str, **kwargs):
        """Run a post-processing operation on the selected file"""
        tr = self.translator.get
        filepath = self.pp_file_var.get()
        
        if not filepath or not Path(filepath).exists():
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("pp_no_file", "File not found"))
            return
        
        if not self.post_processor.ffmpeg_available:
            messagebox.showerror(tr("msg_error", "Error"), tr("log_ffmpeg_not_found", "FFmpeg not found"))
            return
        
        self.pp_status_label.config(
            text=f"⏳ {tr('pp_processing', 'Processing...')}",
            fg=self.design.get_color("accent_primary")
        )
        
        def on_done(success):
            if success:
                self.root.after(0, lambda: self.pp_status_label.config(
                    text=f"✅ {tr('pp_done', 'Processing complete!')}",
                    fg=self.design.get_color("success")
                ))
            else:
                self.root.after(0, lambda: self.pp_status_label.config(
                    text=f"❌ {tr('pp_enhance_error', 'Enhancement failed')}",
                    fg=self.design.get_color("error")
                ))

        # Issue #32: Load the processed output file into the PP player for before/after preview
        def on_output(output_path: str):
            if self.pp_player and output_path:
                self.root.after(0, lambda: self.pp_player.load(output_path, is_file=True))

        self.post_processor.run_async(operation, filepath, callback=on_done, output_callback=on_output, **kwargs)

    def _pp_change_speed_dialog(self):
        """Show dialog to choose speed value"""
        tr = self.translator.get
        filepath = self.pp_file_var.get()
        if not filepath or not Path(filepath).exists():
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("pp_no_file", "File not found"))
            return
        
        # Simple speed selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(tr("pp_speed", "Change Speed"))
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.lift()
        dialog.focus_set()
        dialog.configure(bg=self.design.get_color("bg_primary"))
        
        tk.Label(
            dialog,
            text=tr("pp_speed_help", "Adjust playback speed (0.25x - 4x)"),
            bg=self.design.get_color("bg_primary"),
            fg=self.design.get_color("fg_primary"),
            font=(LOADED_FONT_FAMILY, Typography.SIZE_BODY)
        ).pack(pady=Spacing.MD)
        
        speed_var = tk.DoubleVar(value=1.0)
        speed_frame = ttk.Frame(dialog)
        speed_frame.pack(pady=Spacing.SM)
        
        for spd in [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 4.0]:
            ttk.Radiobutton(speed_frame, text=f"{spd}x", variable=speed_var, value=spd).pack(
                side=tk.LEFT, padx=Spacing.XS
            )
        
        def apply_speed():
            dialog.destroy()
            self._run_post_process("change_speed", speed=speed_var.get())
        
        ModernButton(dialog, text="OK", command=apply_speed, variant="primary", width=10).pack(pady=Spacing.MD)
    
    def _pp_process_from_history(self, filepath: str, operation: str, **kwargs):
        """Run post-processing on a file directly from history card"""
        if filepath:
            self.pp_file_var.set(filepath)
            self._switch_section("history")
            self._run_post_process(operation, **kwargs)

    def _redownload_from_history(self, url: str):
        """Send a URL from history back to the Download tab and trigger verify"""
        if not url:
            return
        self._switch_section("download")
        if hasattr(self, "download_url_entry"):
            self.download_url_entry.delete(0, tk.END)
            self.download_url_entry.insert(0, url)
        # Small delay so the section switch completes before verify runs
        self.root.after(100, self.verify_video)

    def refresh_history(self):
        """Refresh download history with improved card layout"""
        tr = self.translator.get
        
        # Clear existing records
        for widget in self.history_records_frame.winfo_children():
            widget.destroy()
        
        history = self.config_manager.load_history()

        query = ""
        if hasattr(self, "history_search_entry"):
            query = self.history_search_entry.get_value().strip().lower()

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
                record_card = ModernCard(self.history_records_frame, design=self.design)
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
                
                # Main layout: thumbnail | info
                main_frame = ttk.Frame(record_card.body)
                main_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
                
                # Thumbnail (if available)
                thumbnail_url = item.get("thumbnail", "")
                video_id = item.get("video_id", "")
                if thumbnail_url and video_id:
                    thumb_label = tk.Label(
                        main_frame,
                        text="🎬",
                        width=10, height=3,
                        bg=self.design.get_color("bg_secondary"),
                        relief="flat"
                    )
                    thumb_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
                    
                    # Async thumbnail load (use cache)
                    if video_id in self._thumbnail_cache:
                        photo = self._thumbnail_cache[video_id]
                        thumb_label.config(image=photo, text="", width=80, height=45)
                        thumb_label.image = photo
                    else:
                        self._load_history_thumbnail(thumb_label, thumbnail_url, video_id)
                
                # Info section
                info_frame = ttk.Frame(main_frame)
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Header with status
                header_frame = ttk.Frame(info_frame)
                header_frame.pack(fill=tk.X)
                
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
                
                # Badge: Live / Shorts / type indicators
                item_url = item.get("url", "")
                is_live_entry = item.get("is_live", False)
                is_short_entry = '/shorts/' in item_url
                
                if is_live_entry:
                    Badge(
                        header_frame, text=f"🔴 {tr('live_badge', 'LIVE')}",
                        variant="red", design=self.design, size="sm"
                    ).pack(side=tk.RIGHT, padx=(Spacing.XS, 0))
                
                if is_short_entry:
                    Badge(
                        header_frame, text=f"📱 {tr('shorts_badge', 'SHORT')}",
                        variant="orange", design=self.design, size="sm"
                    ).pack(side=tk.RIGHT, padx=(Spacing.XS, 0))
                
                # === Per-card Actions: always show URL actions, PP only on success ===
                item_url_copy = item.get("url", "")
                actions_frame = ttk.Frame(record_card.body)
                actions_frame.pack(fill=tk.X, pady=(Spacing.XS, 0))

                if item_url_copy:
                    # Copy URL
                    copy_lbl = tk.Label(
                        actions_frame, text="📋", cursor="hand2",
                        font=("Segoe UI Emoji", 10),
                        bg=self.design.get_color("bg_tertiary"),
                        fg=self.design.get_color("fg_secondary")
                    )
                    copy_lbl.pack(side=tk.LEFT, padx=(0, Spacing.XS))
                    copy_lbl.bind("<Button-1>",
                        lambda e, u=item_url_copy: (self.root.clipboard_clear(), self.root.clipboard_append(u)))
                    Tooltip(copy_lbl, text=tr("tooltip_copy_url", "Copy URL to clipboard"), design=self.design)

                    # Re-download button
                    redl_btn = ModernButton(
                        actions_frame,
                        text=f"🔁 {tr('redownload_btn', 'Re-download')}",
                        command=lambda u=item_url_copy: self._redownload_from_history(u),
                        variant="outline", size="sm", width=14
                    )
                    redl_btn.pack(side=tk.LEFT, padx=(Spacing.XS, Spacing.SM))
                    Tooltip(redl_btn, text=tr("tooltip_redownload", "Send this URL back to the download tab"), design=self.design)

                if status == "success":
                    # Build file path for this item
                    item_filepath = self.output_dir / filename if filename else None
                    actual_file = None
                    if item_filepath:
                        for ext in ['', '.mp4', '.mkv', '.mp3', '.m4a', '.opus', '.wav']:
                            candidate = Path(str(item_filepath) + ext) if ext else item_filepath
                            if candidate.exists():
                                actual_file = str(candidate)
                                break
                        if not actual_file:
                            stem = item_filepath.stem
                            for f in self.output_dir.glob(f"{stem}.*"):
                                actual_file = str(f)
                                break

                    if actual_file:
                        for op_name, op_icon, op_key in [
                            ("normalize_audio", "🔊", "pp_normalize_audio"),
                            ("compress", "📦", "pp_compress"),
                            ("extract_audio", "🔈", "pp_extract_audio"),
                        ]:
                            lbl = tk.Label(
                                actions_frame, text=f"{op_icon}", cursor="hand2",
                                font=("Segoe UI Emoji", 10),
                                bg=self.design.get_color("bg_tertiary"),
                                fg=self.design.get_color("fg_secondary")
                            )
                            lbl.pack(side=tk.LEFT, padx=(Spacing.XS, 0))
                            lbl.bind(
                                "<Button-1>",
                                lambda e, fp=actual_file, op=op_name: self._pp_process_from_history(fp, op)
                            )
                            Tooltip(lbl, text=tr(op_key, op_name.replace("_", " ").title()), design=self.design)
                
            except Exception as e:
                self.logger.warning(f"Error displaying history record: {e}")
    
    def _load_history_thumbnail(self, label, url: str, video_id: str):
        """Load a thumbnail for a history card asynchronously"""
        def fetch():
            try:
                import urllib.request
                import io
                from PIL import Image, ImageTk
                
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
                
                img = Image.open(io.BytesIO(data))
                img = img.resize((80, 45), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache it
                self._thumbnail_cache[video_id] = photo
                
                def update():
                    try:
                        label.config(image=photo, text="", width=80, height=45)
                        label.image = photo
                    except tk.TclError:
                        pass  # Widget may have been destroyed
                
                self.root.after(0, update)
            except Exception:
                pass  # Silently fail — placeholder stays
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def clear_history(self):
        """Clear download history"""
        tr = self.translator.get
        if messagebox.askyesno(tr("msg_confirm", "Confirm"), tr("history_clear", "Clear History") + "?"):
            self.config_manager.save_history([])
            self.refresh_history()
    
    def open_output_folder(self):
        """Open output folder in system file explorer"""
        tr = self.translator.get
        try:
            if sys.platform == 'win32':
                os.startfile(str(self.output_dir))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(self.output_dir)])
            else:
                subprocess.Popen(['xdg-open', str(self.output_dir)])
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
        """Verify live stream availability and show metadata in status strip"""
        tr = self.translator.get
        url = self.live_url_entry.get_value().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            self.root.after(0, lambda: self.live_status_label.config(
                text=tr("live_status_error", "ERROR"), fg=self.design.get_color("error")))
            self.root.after(0, lambda: self._live_dot_label.config(fg=self.design.get_color("error")))
            return
        
        self.live_log.add_log(tr("live_check_stream", "Checking stream..."))
        self.root.after(0, lambda: self.live_status_label.config(
            text=tr("live_checking", "Checking..."), fg=self.design.get_color("fg_secondary")))
        
        def verify_thread():
            if not YT_DLP_AVAILABLE:
                self.root.after(0, lambda: self.live_log.add_log(tr("msg_error", "Error") + ": yt-dlp", "ERROR"))
                self.root.after(0, lambda: self.live_status_label.config(
                    text=tr("live_status_error", "ERROR"), fg=self.design.get_color("error")))
                return
            
            try:
                # Use cookies for authentication (avoids bot detection)
                base_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'skip_download': True,
                }
                ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    is_live = info.get('is_live', False)
                    channel = info.get('channel', info.get('uploader', '—'))
                    title = info.get('title', '—')
                    thumb_url = info.get('thumbnail', '')
                    
                    # Calculate how long the live has been streaming
                    live_elapsed_secs = 0
                    release_ts = info.get('release_timestamp')
                    if release_ts:
                        live_elapsed_secs = int(time.time() - release_ts)
                    elif info.get('duration'):
                        live_elapsed_secs = int(info['duration'])
                    
                    # Store the live start timestamp for the elapsed timer
                    if is_live and release_ts:
                        self._live_stream_start_ts = release_ts
                    
                    if is_live:
                        status_text = "🔴 LIVE"
                        status_color = self.design.get_color("error")
                        dot_color = "#ff4444"
                    else:
                        status_text = tr("live_status_offline", "OFFLINE")
                        status_color = self.design.get_color("warning")
                        dot_color = self.design.get_color("warning")
                    
                    def update_ui():
                        self.live_status_label.config(text=status_text, fg=status_color)
                        self._live_dot_label.config(fg=dot_color)
                        self._live_channel_label.config(text=channel)
                        self.live_log.add_log(f"{status_text} — {channel}: {title}")
                        
                        # Show elapsed time since live started (or duration for VODs)
                        if live_elapsed_secs > 0:
                            h, rem = divmod(live_elapsed_secs, 3600)
                            m, s = divmod(rem, 60)
                            self.live_elapsed_label.config(text=f"{int(h):02d}:{int(m):02d}:{int(s):02d}")
                            self.live_duration_label.config(text="LIVE" if is_live else f"{int(h):02d}:{int(m):02d}:{int(s):02d}")
                        else:
                            self.live_duration_label.config(text="LIVE" if is_live else "—")
                        
                        # Start a live elapsed counter from the stream start
                        if is_live and release_ts:
                            self._start_live_verify_timer()
                    
                    self.root.after(0, update_ui)
                    
                    # Load thumbnail in background
                    if thumb_url:
                        self._load_live_thumbnail(thumb_url)
                    
            except Exception as e:
                error_str = str(e)
                self.root.after(0, lambda: self.live_log.add_log(f"{tr('msg_error', 'Error')}: {error_str}", "ERROR"))
                self.root.after(0, lambda: self.live_status_label.config(
                    text=tr("live_status_error", "ERROR"), fg=self.design.get_color("error")))
                self.root.after(0, lambda: self._live_dot_label.config(fg=self.design.get_color("error")))
                
                # Show hint if it's a cookie/bot issue
                if "Sign in" in error_str or "bot" in error_str.lower():
                    self.root.after(0, lambda: self.live_log.add_log(
                        "💡 Tip: Configure cookies in Settings → Account tab", "WARNING"))
        
        thread = threading.Thread(target=verify_thread, daemon=True)
        thread.start()
    
    def _start_live_verify_timer(self):
        """Keep elapsed label counting up from the live stream's actual start time.
        Runs every second. Stops when recording starts (recording has its own timer)."""
        if self.is_recording:
            return  # Recording timer takes over
        ts = getattr(self, '_live_stream_start_ts', None)
        if not ts:
            return
        elapsed = int(time.time() - ts)
        if elapsed < 0:
            elapsed = 0
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        try:
            self.live_elapsed_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        except Exception:
            return
        self.root.after(1000, self._start_live_verify_timer)
    
    def _load_live_thumbnail(self, thumb_url):
        """Download and display live stream thumbnail in status strip"""
        def _fetch():
            try:
                import urllib.request
                from PIL import Image, ImageTk
                import io
                
                req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
                
                img = Image.open(io.BytesIO(data))
                # Resize to 48x27 (16:9 aspect)
                img = img.resize((48, 27), Image.LANCZOS)
                
                def apply():
                    if not self.root.winfo_exists():
                        return
                    photo = ImageTk.PhotoImage(img)
                    self._live_thumb_ref = photo
                    self._live_thumb_label.config(image=photo, width=48, height=27)
                
                self.root.after(0, apply)
            except Exception:
                pass
        
        threading.Thread(target=_fetch, daemon=True).start()
    
    def start_live_recording(self):
        """Start recording live stream — downloads the entire live from start to end"""
        tr = self.translator.get
        url = self.live_url_entry.get_value().strip()
        
        if not url or not self.is_valid_youtube_url(url):
            messagebox.showerror(tr("msg_error", "Error"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        if not YT_DLP_AVAILABLE:
            messagebox.showerror(tr("msg_error", "Error"), "yt-dlp not available")
            return

        if self.is_recording:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("live_already_recording", "Recording already in progress"))
            return
        
        self.is_recording = True
        self._live_user_cancelled = False
        self._live_recording_start = time.time()
        self._live_elapsed_seconds = 0
        self._clip_start_time = None
        self.live_log.add_log(f"● {tr('live_recording_started', 'Recording started...')}")
        
        # Update status strip to show recording state
        self.root.after(0, lambda: self._live_dot_label.config(fg="#ff4444"))
        self.root.after(0, lambda: self.live_status_label.config(
            text=f"● {tr('live_recording', 'RECORDING')}", fg="#ff4444"))
        
        # Start elapsed timer
        self._start_live_elapsed_timer()
        
        # Auto-load recording file in embedded player after a short delay
        # This switches from the live stream URL to the local file, enabling:
        # - Full seekbar from the beginning of the live
        # - Rewind / fast-forward within the recorded portion
        if self.embedded_player and is_player_available():
            self.embedded_player.load_recording(str(self.output_dir), delay=8.0)
            self.live_log.add_log(f"🎬 {tr('player_auto_loading', 'Loading recording file for full timeline access...')}")
        
        def record_thread():
            try:
                quality = self.live_quality_var.get()
                
                # Use flexible format chains —
                # "best[height<=X]/best" falls back if the filter matches nothing
                # (live MPD manifests often lack height metadata)
                format_str = {
                    "best": "bestvideo+bestaudio/best",
                    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/bestvideo+bestaudio/best",
                    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]/bestvideo+bestaudio/best",
                    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]/bestvideo+bestaudio/best",
                }.get(quality, "bestvideo+bestaudio/best")
                
                base_opts = {
                    'format': format_str,
                    # do not download WebM even if format_str allows it
                    'reject': 'webm',
                    'outtmpl': str(self.output_dir / '%(title)s-%(id)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.live_progress_hook],
                    # Record from the live start (yt-dlp downloads from beginning by default for lives)
                    'live_from_start': True,
                }
                
                ydl_opts = self.get_ydl_opts_with_cookies(base_opts)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.root.after(0, lambda: self.live_log.add_log(tr("download_progress", "Downloading...")))
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                    # convert live recording if user requested Premiere compatibility
                    if self.config_manager.get("premiere_compat", False):
                        if not self.post_processor.is_premiere_compatible(filename):
                            tr = self.translator.get
                            self.live_log.add_log(tr('log_premiere_converting', 'Converting to Premiere-compatible format...'))
                            newfn = self.post_processor.convert_for_premiere(filename)
                            if newfn:
                                filename = newfn
                                self.live_log.add_log(tr('log_premiere_converted', 'Conversion complete'))

                    entry = {
                        "date": datetime.now().isoformat(),
                        "filename": Path(filename).name,
                        "status": "success",
                        "url": url,
                        "is_live": True,
                        "thumbnail": info.get('thumbnail', ''),
                        "video_id": info.get('id', '')
                    }
                    self.config_manager.add_to_history(entry)
                    
                    self.root.after(0, lambda: self.live_log.add_log(
                        f"✅ {tr('live_recording_completed', 'Recording completed successfully!')}"))
                    self.root.after(0, self.refresh_history)
            
            except Exception as e:
                error_msg = str(e)
                if "__user_cancelled__" in error_msg:
                    pass  # Already logged in stop_live_recording
                elif "Could not copy" in error_msg and "cookie database" in error_msg:
                    self.root.after(0, lambda: self.live_log.add_log(
                        tr("browser_test_browser_open", "⚠️ Browser is open! Close it first."), "WARNING"))
                else:
                    self.root.after(0, lambda msg=error_msg: self.live_log.add_log(
                        f"{tr('msg_error', 'Error')}: {msg}", "ERROR"))
                    # Try to save partial recording to history
                    try:
                        partial_files = sorted(self.output_dir.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
                        if not partial_files:
                            partial_files = sorted(self.output_dir.glob("*.mkv"), key=lambda f: f.stat().st_mtime, reverse=True)
                        if not partial_files:
                            partial_files = sorted(self.output_dir.glob("*.ts"), key=lambda f: f.stat().st_mtime, reverse=True)
                        if partial_files:
                            partial = partial_files[0]
                            entry = {
                                "date": datetime.now().isoformat(),
                                "filename": partial.name,
                                "status": "partial",
                                "url": url,
                                "is_live": True,
                                "thumbnail": "",
                                "video_id": ""
                            }
                            self.config_manager.add_to_history(entry)
                            self.root.after(0, lambda n=partial.name: self.live_log.add_log(
                                f"⚠️ {tr('live_stream_ended', 'Stream ended — partial recording saved')}: {n}", "WARNING"))
                            self.root.after(0, self.refresh_history)
                    except Exception:
                        pass
            
            finally:
                self.is_recording = False
                self._live_user_cancelled = False
                # Update status strip
                self.root.after(0, lambda: self.live_status_label.config(
                    text=tr("live_recording_stopped", "Stopped"), fg=self.design.get_color("fg_secondary")))
                self.root.after(0, lambda: self._live_dot_label.config(fg=self.design.get_color("fg_tertiary")))
        
        thread = threading.Thread(target=record_thread, daemon=True)
        thread.start()
    
    def stop_live_recording(self):
        """Stop live stream recording — sets cancel flag which is checked by the progress hook"""
        tr = self.translator.get
        if self.is_recording:
            self.is_recording = False
            self._live_recording_start = None
            self._live_user_cancelled = True
            self.live_log.add_log(f"■ {tr('live_recording_stopped', 'Recording stopped by user')}")
            # Update status strip
            self.live_status_label.config(text=tr("live_recording_stopped", "Stopped"),
                                           fg=self.design.get_color("fg_secondary"))
            self._live_dot_label.config(fg=self.design.get_color("fg_tertiary"))
        else:
            messagebox.showinfo(tr("msg_info", "Information"), tr("live_not_recording", "No recording in progress"))
    
    def live_progress_hook(self, d):
        """Progress hook for live recording — also handles user cancellation"""
        if getattr(self, '_live_user_cancelled', False):
            raise Exception("__user_cancelled__")
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '0 B/s')
            eta = d.get('_eta_str', 'Unknown')
            # Use root.after for thread-safe UI update
            msg = f"{percent} | Speed: {speed} | ETA: {eta}"
            self.root.after(0, lambda m=msg: self.live_log.add_log(m))
            # Update elapsed timer
            if self._live_recording_start:
                elapsed = int(time.time() - self._live_recording_start)
                self._live_elapsed_seconds = elapsed
                h, rem = divmod(elapsed, 3600)
                m, s = divmod(rem, 60)
                self.root.after(0, lambda: self.live_elapsed_label.config(text=f"{h:02d}:{m:02d}:{s:02d}"))

    # ──────────────────────────────────────────
    # LIVE CLIPPER METHODS
    # ──────────────────────────────────────────

    def _start_live_elapsed_timer(self):
        """Issue #55: Independent 1-second polling timer to keep elapsed label in sync"""
        if not self._live_recording_start or not self.is_recording:
            return
        elapsed = int(time.time() - self._live_recording_start)
        self._live_elapsed_seconds = elapsed
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        try:
            self.live_elapsed_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        except Exception:
            return
        # Reschedule every second while recording
        self.root.after(1000, self._start_live_elapsed_timer)

    def _load_live_preview(self):
        """Load the live stream URL into the embedded video player.
        
        Passes live_from_start=True so mpv/yt-dlp will load from
        the beginning of the live broadcast, not the current live edge.
        """
        tr = self.translator.get
        url = self.live_url_entry.get_value().strip()
        if not url:
            messagebox.showwarning(tr("msg_warning", "Warning"), tr("download_invalid_url", "Invalid YouTube URL"))
            return
        
        # Try embedded player first
        if self.embedded_player and is_player_available():
            self.live_log.add_log(f"▶ {tr('player_loading', 'Loading preview...')}")
            # pass live_from_start flag for mpv
            success = self.embedded_player.load(url, live_from_start=True)
            if success:
                self.live_log.add_log(f"▶ {tr('player_loaded', 'Preview loaded')} [{self.embedded_player.backend.upper()}]")
            else:
                self.live_log.add_log(f"❌ {tr('player_load_failed', 'Failed to load preview')}", "ERROR")
            return
        
        # Fallback: open in external player or browser
        self._open_in_external_player(url)
    
    def _return_to_live(self):
        """Jump to the latest position in the live stream (seeks to live edge)"""
        if not self.embedded_player:
            return
        # Works even if is_loaded reports False (live streams may have duration=0)
        if self.embedded_player._playing or self.embedded_player._loaded_url:
            self.embedded_player.seek_to_end()
            self.live_log.add_log(f"● {self.translator.get('live_return_to_live', 'LIVE')} — seeking to live edge")
    
    def _open_in_external_player(self, url: str):
        """Fallback: open URL in external player (VLC, mpv, or browser)"""
        try:
            import subprocess as sp
            vlc_path = shutil.which("vlc")
            mpv_path = shutil.which("mpv")
            if vlc_path:
                sp.Popen([vlc_path, url], creationflags=sp.CREATE_NO_WINDOW if hasattr(sp, 'CREATE_NO_WINDOW') else 0)
                self.live_log.add_log(f"▶️ Opened in VLC")
            elif mpv_path:
                sp.Popen([mpv_path, url], creationflags=sp.CREATE_NO_WINDOW if hasattr(sp, 'CREATE_NO_WINDOW') else 0)
                self.live_log.add_log(f"▶️ Opened in mpv")
            else:
                if sys.platform == 'win32':
                    os.startfile(url)
                else:
                    import webbrowser
                    webbrowser.open(url)
                self.live_log.add_log(f"▶️ Opened in default browser")
        except Exception as e:
            self.live_log.add_log(f"Error opening player: {e}", "ERROR")

    def _clipper_mark_start(self):
        """Mark the start time of a clip segment at current preview position"""
        tr = self.translator.get
        if not self.is_recording:
            messagebox.showinfo(tr("msg_info", "Information"), tr("clipper_not_recording", "Start recording first, then mark clips."))
            return
        # Use embedded player time if loaded, otherwise fall back to elapsed
        if self.embedded_player and self.embedded_player.is_playing:
            self._clip_start_time = int(self.embedded_player.get_time())
        else:
            self._clip_start_time = self._live_elapsed_seconds
        h, rem = divmod(self._clip_start_time, 3600)
        m, s = divmod(rem, 60)
        self.live_log.add_log(f"🟢 {tr('clipper_mark_start', 'Mark Start')}: {h:02d}:{m:02d}:{s:02d}")
        # Update clip time label
        if hasattr(self, '_clip_time_label'):
            self._clip_time_label.config(text=f"▶ {h:02d}:{m:02d}:{s:02d} → ...")
        # Hide download button until end is marked
        if hasattr(self, '_download_clip_btn'):
            self._download_clip_btn.pack_forget()

    def _clipper_mark_end(self):
        """Mark the end time of a clip segment at current preview position"""
        tr = self.translator.get
        if self._clip_start_time is None:
            messagebox.showinfo(tr("msg_info", "Information"), tr("clipper_mark_start_first", "Click Mark Start first, then Mark End."))
            return
        
        # Use embedded player time if loaded, otherwise fall back to elapsed
        if self.embedded_player and self.embedded_player.is_playing:
            end_time = int(self.embedded_player.get_time())
        else:
            end_time = self._live_elapsed_seconds
        start_time = self._clip_start_time
        
        if end_time <= start_time:
            return
        
        clip = {
            "start": start_time,
            "end": end_time,
            "index": len(self._clip_markers) + 1
        }
        self._clip_markers.append(clip)
        self._clip_start_time = None
        
        # Format times
        sh, srem = divmod(start_time, 3600)
        sm, ss = divmod(srem, 60)
        eh, erem = divmod(end_time, 3600)
        em, es = divmod(erem, 60)
        dur = end_time - start_time
        
        self.live_log.add_log(
            f"🔴 Clip #{clip['index']}: {sh:02d}:{sm:02d}:{ss:02d} → {eh:02d}:{em:02d}:{es:02d} ({dur}s)"
        )
        
        # Update clip time label with full range
        if hasattr(self, '_clip_time_label'):
            self._clip_time_label.config(text=f"{sh:02d}:{sm:02d}:{ss:02d} → {eh:02d}:{em:02d}:{es:02d} ({dur}s)")
        
        # Show download clip button
        if hasattr(self, '_download_clip_btn'):
            self._download_clip_btn.pack(side=tk.LEFT, padx=(Spacing.XS, 0))
        
        self._refresh_clip_list()
    
    def _clipper_download_marked(self):
        """Download the most recently marked clip segment immediately"""
        if not self._clip_markers:
            return
        clip = self._clip_markers[-1]
        self._clipper_download_single(clip)
        # Reset time label
        if hasattr(self, '_clip_time_label'):
            self._clip_time_label.config(text="")
        if hasattr(self, '_download_clip_btn'):
            self._download_clip_btn.pack_forget()

    def _clipper_quick_cut(self, seconds: int):
        """Quick-cut: instantly download last N seconds from current preview position.
        
        Uses the current preview position as the end point. If the live hasn't
        run long enough, clips from 0 to current position. Downloads immediately
        without confirmation — concurrent with the main recording.
        """
        tr = self.translator.get
        if not self.is_recording:
            messagebox.showinfo(tr("msg_info", "Information"), tr("clipper_not_recording", "Start recording first, then mark clips."))
            return
        
        # Get current position (player or elapsed)
        if self.embedded_player and self.embedded_player.is_playing:
            end_time = int(self.embedded_player.get_time())
        else:
            end_time = self._live_elapsed_seconds
        
        # Clamp start to 0 if not enough time has passed
        start_time = max(0, end_time - seconds)
        if end_time <= 0:
            return
        
        clip = {
            "start": start_time,
            "end": end_time,
            "index": len(self._clip_markers) + 1
        }
        self._clip_markers.append(clip)
        
        sh, srem = divmod(start_time, 3600)
        sm, ss = divmod(srem, 60)
        eh, erem = divmod(end_time, 3600)
        em, es = divmod(erem, 60)
        actual_dur = end_time - start_time
        
        self.live_log.add_log(
            f"⏪ {tr('clipper_quick_cut', 'Quick Cut')} {actual_dur}s — Clip #{clip['index']}: "
            f"{sh:02d}:{sm:02d}:{ss:02d} → {eh:02d}:{em:02d}:{es:02d}"
        )
        self._refresh_clip_list()
        
        # Instant download — no confirmation needed
        self._clipper_download_single(clip)
    
    def _clipper_download_single(self, clip):
        """Download a single clip segment in the background (concurrent with main recording)"""
        tr = self.translator.get
        if not self.post_processor.ffmpeg_available:
            self.live_log.add_log(f"❌ {tr('log_ffmpeg_not_found', 'FFmpeg not found')}", "ERROR")
            return
        
        # Find the most recent recording file
        recent_files = sorted(self.output_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
        video_files = [f for f in recent_files if f.suffix.lower() in ('.mp4', '.mkv', '.webm', '.ts', '.flv')]
        
        if not video_files:
            self.live_log.add_log(f"⚠️ {tr('pp_no_file', 'No recorded file found')}", "WARNING")
            return
        
        source_file = str(video_files[0])
        idx = clip['index']
        
        def _cut_thread():
            sh, srem = divmod(clip["start"], 3600)
            sm, ss = divmod(srem, 60)
            eh, erem = divmod(clip["end"], 3600)
            em, es = divmod(erem, 60)
            start_str = f"{sh:02d}:{sm:02d}:{ss:02d}"
            end_str = f"{eh:02d}:{em:02d}:{es:02d}"
            
            result = self.post_processor.trim(source_file, start_str, end_str)
            if result:
                # convert clip if needed
                if self.config_manager.get("premiere_compat", False) and not self.post_processor.is_premiere_compatible(result):
                    tr2 = self.translator.get
                    self.live_log.add_log(tr2('log_premiere_converting', 'Converting to Premiere-compatible format...'))
                    newclip = self.post_processor.convert_for_premiere(result)
                    if newclip:
                        result = newclip
                        self.live_log.add_log(tr2('log_premiere_converted', 'Conversion complete'))
                self.root.after(0, lambda: self.live_log.add_log(
                    f"✅ {tr('clipper_saved', 'Clip saved')}: Clip #{idx}"))
            else:
                self.root.after(0, lambda: self.live_log.add_log(
                    f"❌ Clip #{idx} failed", "ERROR"))
        
        self.live_log.add_log(f"⬇ Downloading Clip #{idx}...")
        threading.Thread(target=_cut_thread, daemon=True).start()

    def _refresh_clip_list(self):
        """Refresh the clip list UI"""
        tr = self.translator.get
        if not hasattr(self, 'clip_list_frame'):
            return
        
        for widget in self.clip_list_frame.winfo_children():
            widget.destroy()
        
        if not self._clip_markers:
            tk.Label(
                self.clip_list_frame,
                text=tr("clipper_no_clips", "No clips marked"),
                bg=self.design.get_color("bg_tertiary"),
                fg=self.design.get_color("fg_tertiary"),
                font=(Typography.FONT_FAMILY, Typography.SIZE_TINY)
            ).pack(pady=Spacing.XS)
            return
        
        for clip in self._clip_markers:
            row = tk.Frame(self.clip_list_frame, bg=self.design.get_color("bg_secondary"))
            row.pack(fill=tk.X, pady=1, padx=Spacing.XS)
            
            sh, srem = divmod(clip["start"], 3600)
            sm, ss = divmod(srem, 60)
            eh, erem = divmod(clip["end"], 3600)
            em, es = divmod(erem, 60)
            dur = clip["end"] - clip["start"]
            
            tk.Label(
                row,
                text=f"✂ #{clip['index']}",
                font=(Typography.FONT_FAMILY, Typography.SIZE_TINY),
                bg=self.design.get_color("bg_secondary"),
                fg=self.design.get_color("accent_primary"),
            ).pack(side=tk.LEFT, padx=(Spacing.SM, Spacing.XS))
            
            tk.Label(
                row,
                text=f"{sh:02d}:{sm:02d}:{ss:02d} → {eh:02d}:{em:02d}:{es:02d} ({dur}s)",
                font=(Typography.FONT_MONO, Typography.SIZE_TINY),
                bg=self.design.get_color("bg_secondary"),
                fg=self.design.get_color("fg_primary"),
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Download this clip
            dl_lbl = tk.Label(
                row, text="⬇", cursor="hand2",
                font=(Typography.FONT_FAMILY, 10),
                bg=self.design.get_color("bg_secondary"),
                fg=self.design.get_color("accent_primary"),
            )
            dl_lbl.pack(side=tk.RIGHT, padx=(0, Spacing.XS))
            dl_lbl.bind("<Button-1>", lambda e, c=clip: self._clipper_download_single(c))
            
            # Remove button
            remove_lbl = tk.Label(
                row, text="✕", cursor="hand2",
                font=(Typography.FONT_FAMILY, 10),
                bg=self.design.get_color("bg_secondary"),
                fg=self.design.get_color("error"),
            )
            remove_lbl.pack(side=tk.RIGHT, padx=Spacing.XS)
            remove_lbl.bind("<Button-1>", lambda e, idx=clip["index"]: self._clipper_remove(idx))

    def _clipper_remove(self, index):
        """Remove a clip by index"""
        self._clip_markers = [c for c in self._clip_markers if c["index"] != index]
        # Re-index
        for i, c in enumerate(self._clip_markers, 1):
            c["index"] = i
        self._refresh_clip_list()