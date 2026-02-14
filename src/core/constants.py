# -*- coding: utf-8 -*-
"""
Global Constants and Translations for EasyCut

Centralizes all hardcoded strings and constants to enable:
- Easy i18n
- Consistent messaging across the app
- Single point of change for any text
- Type safety for all constants

Usage:
    from core.constants import Constants, TranslationKeys
    
    # Use translations
    title = TranslationKeys.TITLE
    
    # Use constants
    quality = Constants.DOWNLOAD_QUALITY_BEST
"""

from typing import Dict


class Constants:
    """Application-wide constants"""
    
    # Application Info
    APP_NAME = "EasyCut"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Professional YouTube Downloader & Audio Converter"
    APP_AUTHOR = "Deko Costa"
    APP_URL = "https://github.com/dekouninter/EasyCut"
    APP_LICENSE = "GPL-3.0"
    
    # Download Options
    class DOWNLOAD:
        # Formats
        FORMAT_MP4 = "mp4"
        FORMAT_MKV = "mkv"
        FORMAT_WEBM = "webm"
        FORMAT_BEST = "best"
        
        # Qualities
        QUALITY_4K = "2160p"
        QUALITY_1080P = "1080p"
        QUALITY_720P = "720p"
        QUALITY_480P = "480p"
        QUALITY_360P = "360p"
        QUALITY_BEST = "best"
        QUALITY_WORST = "worst"
        
        # Defaults
        DEFAULT_QUALITY = QUALITY_BEST
        DEFAULT_FORMAT = FORMAT_MP4
        DEFAULT_AUDIO_FORMAT = "mp3"
        DEFAULT_AUDIO_BITRATE = "192"
    
    # Audio Options
    class AUDIO:
        FORMAT_MP3 = "mp3"
        FORMAT_WAV = "wav"
        FORMAT_M4A = "m4a"
        FORMAT_OPUS = "opus"
        
        BITRATE_128 = "128"
        BITRATE_192 = "192"
        BITRATE_256 = "256"
        BITRATE_320 = "320"
        
        DEFAULT_FORMAT = FORMAT_MP3
        DEFAULT_BITRATE = BITRATE_192
    
    # Window Sizes
    class WINDOW:
        WIDTH_MIN = 800
        HEIGHT_MIN = 600
        WIDTH_DEFAULT = 1000
        HEIGHT_DEFAULT = 700
        WIDTH_MAX = 1920
        HEIGHT_MAX = 1080
    
    # Log Levels
    class LOGGING:
        LEVEL_DEBUG = "DEBUG"
        LEVEL_INFO = "INFO"
        LEVEL_WARNING = "WARNING"
        LEVEL_ERROR = "ERROR"
        LEVEL_CRITICAL = "CRITICAL"
        DEFAULT_LEVEL = LEVEL_INFO
    
    # Download History
    class HISTORY:
        MAX_RECORDS = 100
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        STATUS_SUCCESS = "success"
        STATUS_ERROR = "error"
        STATUS_CANCELLED = "cancelled"
        STATUS_PENDING = "pending"
    
    # Threading
    class THREADING:
        MAX_WORKERS = 4  # Max concurrent downloads
        QUEUE_TIMEOUT = 30  # Seconds
        THREAD_TIMEOUT = 300  # Seconds (5 min)
    
    # Timings
    class TIMINGS:
        UI_REFRESH_MS = 500  # Milliseconds
        SCROLL_STEP = 3  # Units for mousewheel
        ANIMATION_SPEED = 200  # Milliseconds
    
    # Paths
    class PATHS:
        CONFIG_DIR = ".easycut"
        LOG_DIR = "logs"
        HISTORY_FILE = "history.json"
        CREDENTIALS_SERVICE = "easycut"
    
    # Support Links
    class SUPPORT:
        BUY_ME_COFFEE = "https://buymeacoffee.com/dekocosta"
        LIVEPIX = "https://livepix.gg/dekocosta"
        GITHUB = "https://github.com/dekouninter/EasyCut"
        ISSUES = "https://github.com/dekouninter/EasyCut/issues"
    
    # Emoji Icons
    class EMOJI:
        DOWNLOAD = "⬇️"
        UPLOAD = "⬆️"
        SUCCESS = "✅"
        ERROR = "❌"
        WARNING = "⚠️"
        INFO = "ℹ️"
        LOADING = "⏳"
        HISTORY = "📜"
        BATCH = "📦"
        LIVE = "🔴"
        AUDIO = "🎵"
        VIDEO = "🎬"
        SETTINGS = "⚙️"
        THEME_DARK = "🌙"
        THEME_LIGHT = "☀️"
        LANGUAGE = "🌐"
        GITHUB = "🐙"
        HEART = "❤️"


class TranslationKeys:
    """
    Translation key dictionary
    
    Centralized translation keys for all UI strings
    This enables easy i18n integration
    """
    
    # Application
    APP_TITLE = "app_title"
    APP_SUBTITLE = "app_subtitle"
    APP_DESCRIPTION = "app_description"
    WINDOW_TITLE = "window_title"
    
    # Tabs
    class TAB:
        DOWNLOAD = "tab_download"
        BATCH = "tab_batch"
        LIVE = "tab_live"
        AUDIO = "tab_audio"
        HISTORY = "tab_history"
        ABOUT = "tab_about"
        LOGIN = "tab_login"
    
    # Download Tab
    class DOWNLOAD:
        TITLE = "download_title"
        SUBTITLE = "download_subtitle"
        URL = "download_url"
        URL_PLACEHOLDER = "download_url_placeholder"
        QUALITY = "download_quality"
        FORMAT = "download_format"
        BUTTON_START = "download_btn"
        BUTTON_STOP = "download_stop"
        BUTTON_CLEAR = "download_clear_log"
        LOG = "download_log"
        STATUS_READY = "status_ready"
        STATUS_DOWNLOADING = "status_downloading"
        STATUS_COMPLETED = "status_completed"
    
    # Batch Tab
    class BATCH:
        TITLE = "batch_title"
        URLS = "batch_urls"
        URLS_HELP = "batch_urls_help"
        BUTTON_ADD = "batch_btn_add"
        BUTTON_REMOVE = "batch_btn_remove"
        BUTTON_START = "batch_download_all"
        BUTTON_CLEAR = "batch_clear_log"
        LOG = "batch_log"
    
    # Live Tab
    class LIVE:
        TITLE = "live_title"
        URL = "live_url"
        DURATION = "live_duration"
        BUTTON_START = "live_start"
        BUTTON_STOP = "live_stop"
    
    # Audio Tab
    class AUDIO:
        TITLE = "audio_title"
        FORMAT = "audio_format"
        BITRATE = "audio_bitrate"
        BUTTON_CONVERT = "audio_convert"
    
    # History Tab
    class HISTORY:
        TITLE = "history_title"
        RECORDS = "history_records"
        BUTTON_CLEAR = "history_clear"
        EMPTY = "history_empty"
        DATE = "history_date"
        STATUS = "history_status"
    
    # Header
    class HEADER:
        THEME = "header_theme"
        SELECT_FOLDER = "header_select_folder"
        OPEN_FOLDER = "header_open_folder"
        LOGIN = "header_login"
        LOGOUT = "header_logout"
    
    # Login
    class LOGIN:
        TITLE = "login_title"
        EMAIL = "login_email"
        PASSWORD = "login_password"
        BUTTON_LOGIN = "login_button"
        BUTTON_CANCEL = "login_cancel"
        SUCCESS = "login_success"
        ERROR = "login_error"
    
    # Common
    class COMMON:
        OK = "button_ok"
        CANCEL = "button_cancel"
        SAVE = "button_save"
        DELETE = "button_delete"
        CLOSE = "button_close"
        YES = "button_yes"
        NO = "button_no"
        ERROR = "error_message"
        SUCCESS = "success_message"
        WARNING = "warning_message"
        INFO = "info_message"
    
    # Status Messages
    class STATUS:
        READY = "status_ready"
        DOWNLOADING = "status_downloading"
        COMPLETED = "status_completed"
        ERROR = "status_error"
        CANCELLED = "status_cancelled"
        NOT_CONNECTED = "not_connected_youtube"
    
    @staticmethod
    def get_all() -> Dict[str, str]:
        """Get all translation keys as flat dictionary"""
        keys = {}
        for attr_name in dir(TranslationKeys):
            if not attr_name.startswith('_'):
                attr = getattr(TranslationKeys, attr_name)
                if isinstance(attr, str):
                    keys[attr] = attr
                elif hasattr(attr, '__dict__'):
                    for inner_name in dir(attr):
                        if not inner_name.startswith('_'):
                            inner_attr = getattr(attr, inner_name)
                            if isinstance(inner_attr, str):
                                keys[inner_attr] = inner_attr
        return keys
