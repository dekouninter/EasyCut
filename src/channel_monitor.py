# -*- coding: utf-8 -*-
"""
Channel Monitor Module for EasyCut
Background channel monitoring with auto-download support

Author: Deko Costa
License: GPL-3.0
"""

import json
import logging
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List, Dict

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


class ChannelMonitor:
    """Monitors YouTube channels for new uploads and triggers auto-downloads"""

    def __init__(self, config_dir: str = "config", output_dir: str = "downloads"):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.config_file = self.config_dir / "following.json"
        self.config_dir.mkdir(exist_ok=True)

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._on_new_video: Optional[Callable] = None
        self._on_auto_download: Optional[Callable] = None
        self._on_status_update: Optional[Callable] = None

        # Load persisted config
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load channel monitoring config from disk"""
        default = {
            "channels": [],
            "check_interval_minutes": 60,
            "auto_download": False,
            "auto_quality": "best",
            "notifications": True,
            "last_check": None,
            "known_videos": {}  # channel_url -> list of video_ids
        }
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Merge with defaults for any missing keys
                for key, val in default.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception as e:
            logger.warning(f"Failed to load following config: {e}")
        return default

    def _save_config(self):
        """Persist config to disk"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save following config: {e}")

    # ── Channel Management ──────────────────────

    def get_channels(self) -> List[Dict]:
        """Get list of followed channels"""
        return self._config.get("channels", [])

    def add_channel(self, url: str) -> Optional[Dict]:
        """Add a channel to the monitoring list. Returns channel info or None."""
        url = url.strip()
        if not url:
            return None

        # Normalize URL
        url = self._normalize_channel_url(url)
        if not url:
            return None

        # Check for duplicates
        for ch in self._config["channels"]:
            if ch["url"] == url:
                return None  # Already following

        # Fetch channel info
        info = self._fetch_channel_info(url)
        if not info:
            # Still add with minimal info
            info = {
                "url": url,
                "name": url.split("/")[-1],
                "thumbnail": "",
                "subscriber_count": 0,
                "added_date": datetime.now().isoformat()
            }

        self._config["channels"].append(info)
        self._save_config()
        logger.info(f"Added channel: {info.get('name', url)}")
        return info

    def remove_channel(self, url: str) -> bool:
        """Remove a channel from monitoring list"""
        url = self._normalize_channel_url(url) or url
        original_len = len(self._config["channels"])
        self._config["channels"] = [
            ch for ch in self._config["channels"] if ch["url"] != url
        ]
        if len(self._config["channels"]) < original_len:
            # Clean up known videos
            self._config["known_videos"].pop(url, None)
            self._save_config()
            return True
        return False

    def set_channel_notify(self, url: str, value: bool):
        """Set per-channel notification toggle (Issue #62/#66)"""
        url = self._normalize_channel_url(url) or url
        for ch in self._config["channels"]:
            if ch["url"] == url:
                ch["notify"] = value
                self._save_config()
                return

    def set_channel_auto_download(self, url: str, value: bool):
        """Set per-channel auto-download toggle (Issue #62/#66)"""
        url = self._normalize_channel_url(url) or url
        for ch in self._config["channels"]:
            if ch["url"] == url:
                ch["auto_download"] = value
                self._save_config()
                return

    def _normalize_channel_url(self, url: str) -> Optional[str]:
        """Normalize a YouTube channel URL (Issue #59 — also accepts bare username with/without @)"""
        import re
        url = url.strip()
        # Patterns: @handle, /channel/ID, /c/name, /user/name
        patterns = [
            r'(https?://(?:www\.)?youtube\.com/@[\w\-\.]+)',
            r'(https?://(?:www\.)?youtube\.com/channel/[\w\-]+)',
            r'(https?://(?:www\.)?youtube\.com/c/[\w\-]+)',
            r'(https?://(?:www\.)?youtube\.com/user/[\w\-]+)',
        ]
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                return m.group(1)

        # If it's just a handle like @username
        if url.startswith("@"):
            return f"https://www.youtube.com/{url}"

        # If it's a bare username without @ (e.g. "mkbhd" or "LinusTechTips")
        # Only treat as handle if it looks like a plain word (no slashes, dots after first char)
        if re.fullmatch(r'[\w][\w\-\.]*', url) and not url.startswith("http"):
            return f"https://www.youtube.com/@{url}"

        return None

    def _fetch_channel_info(self, url: str) -> Optional[Dict]:
        """Fetch channel metadata using yt-dlp"""
        if not YT_DLP_AVAILABLE:
            return None
        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlist_items': '1',
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"{url}/videos", download=False)
                return {
                    "url": url,
                    "name": info.get('channel', info.get('uploader', url.split('/')[-1])),
                    "thumbnail": info.get('thumbnails', [{}])[-1].get('url', '') if info.get('thumbnails') else '',
                    "subscriber_count": info.get('channel_follower_count', 0),
                    "added_date": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"Failed to fetch channel info for {url}: {e}")
            return None

    # ── Video Checking ──────────────────────

    def check_for_new_videos(self, channel_url: str = None) -> List[Dict]:
        """Check one or all channels for new videos. Returns list of new videos."""
        if not YT_DLP_AVAILABLE:
            return []

        channels = self._config["channels"]
        if channel_url:
            channels = [ch for ch in channels if ch["url"] == channel_url]

        all_new = []
        for ch in channels:
            try:
                new_videos = self._check_channel(ch["url"])
                for vid in new_videos:
                    vid["channel_name"] = ch.get("name", "Unknown")
                all_new.extend(new_videos)
            except Exception as e:
                logger.warning(f"Error checking channel {ch.get('name', ch['url'])}: {e}")

        self._config["last_check"] = datetime.now().isoformat()
        self._save_config()
        return all_new

    def _check_channel(self, channel_url: str) -> List[Dict]:
        """Check a single channel for new videos"""
        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlist_items': '1-10',  # Check last 10 videos
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"{channel_url}/videos", download=False)

            entries = info.get('entries', [])
            if not entries:
                return []

            known = set(self._config["known_videos"].get(channel_url, []))
            new_videos = []

            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                video_id = entry.get('id', '')
                if video_id and video_id not in known:
                    new_videos.append({
                        "video_id": video_id,
                        "title": entry.get('title', 'Unknown'),
                        "url": entry.get('url', f"https://www.youtube.com/watch?v={video_id}"),
                        "duration": entry.get('duration', 0),
                        "channel_url": channel_url,
                    })

            # Update known videos
            current_ids = [e.get('id', '') for e in entries if isinstance(e, dict) and e.get('id')]
            self._config["known_videos"][channel_url] = current_ids
            self._save_config()

            return new_videos

        except Exception as e:
            logger.warning(f"Failed to check channel {channel_url}: {e}")
            return []

    # ── Background Monitor ──────────────────────

    def set_callbacks(self, on_new_video: Callable = None,
                      on_auto_download: Callable = None,
                      on_status_update: Callable = None):
        """Set callback functions for events"""
        self._on_new_video = on_new_video
        self._on_auto_download = on_auto_download
        self._on_status_update = on_status_update

    def start_monitoring(self):
        """Start background monitoring thread"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Channel monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self._running = False
        if self._thread:
            self._thread = None
        logger.info("Channel monitoring stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    def _monitor_loop(self):
        """Background loop that periodically checks for new videos"""
        while self._running:
            try:
                interval = self._config.get("check_interval_minutes", 60) * 60
                if self._on_status_update:
                    self._on_status_update("checking")

                new_videos = self.check_for_new_videos()

                if new_videos:
                    if self._on_new_video:
                        self._on_new_video(new_videos)

                    if self._config.get("auto_download", False) and self._on_auto_download:
                        for vid in new_videos:
                            self._on_auto_download(vid)

                if self._on_status_update:
                    self._on_status_update("idle")

                # Sleep in small increments to allow quick stop
                for _ in range(int(interval)):
                    if not self._running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(60)  # Wait a minute on error

    # ── Settings ──────────────────────

    def get_interval(self) -> int:
        """Get check interval in minutes"""
        return self._config.get("check_interval_minutes", 60)

    def set_interval(self, minutes: int):
        """Set check interval in minutes"""
        self._config["check_interval_minutes"] = max(15, min(1440, minutes))
        self._save_config()

    def get_auto_download(self) -> bool:
        return self._config.get("auto_download", False)

    def set_auto_download(self, enabled: bool):
        self._config["auto_download"] = enabled
        self._save_config()

    def get_auto_quality(self) -> str:
        return self._config.get("auto_quality", "best")

    def set_auto_quality(self, quality: str):
        self._config["auto_quality"] = quality
        self._save_config()

    def get_notifications(self) -> bool:
        return self._config.get("notifications", True)

    def set_notifications(self, enabled: bool):
        self._config["notifications"] = enabled
        self._save_config()

    def get_last_check(self) -> Optional[str]:
        return self._config.get("last_check")
