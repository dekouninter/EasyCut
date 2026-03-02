# -*- coding: utf-8 -*-
"""Tests for the download option builder and related helpers.

Validates format string generation, quality presets, network settings
injection, time-range section building, and rate-limit parsing.
"""

import sys
import types
import tkinter as tk
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ---------------------------------------------------------------------------
# Minimal stubs so we can import easycut helpers without a full Tk app
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_heavy_imports(monkeypatch):
    """Stub out heavyweight imports that easycut.py pulls in at module level."""
    # Provide a fake yt_dlp so the import doesn't fail
    fake_ytdlp = types.ModuleType("yt_dlp")
    fake_ytdlp.YoutubeDL = MagicMock
    monkeypatch.setitem(sys.modules, "yt_dlp", fake_ytdlp)


# ---------------------------------------------------------------------------
# Helpers under test (imported from easycut module via class methods)
# ---------------------------------------------------------------------------

from easycut import EasyCutApp


class TestParseTimecode:
    """EasyCutApp._parse_timecode static method."""

    def test_seconds_only(self):
        assert EasyCutApp._parse_timecode("45") == 45

    def test_mm_ss(self):
        assert EasyCutApp._parse_timecode("01:30") == 90

    def test_hh_mm_ss(self):
        assert EasyCutApp._parse_timecode("1:02:03") == 3723

    def test_zeroes(self):
        assert EasyCutApp._parse_timecode("00:00:00") == 0

    def test_invalid_non_digit(self):
        assert EasyCutApp._parse_timecode("ab:cd:ef") is None

    def test_invalid_too_many_parts(self):
        assert EasyCutApp._parse_timecode("1:2:3:4") is None

    def test_minutes_over_59(self):
        assert EasyCutApp._parse_timecode("00:60:00") is None

    def test_seconds_over_59(self):
        assert EasyCutApp._parse_timecode("00:00:60") is None

    def test_empty_string(self):
        assert EasyCutApp._parse_timecode("") is None


class TestParseRateLimit:
    """EasyCutApp._parse_rate_limit static method."""

    def test_plain_number(self):
        assert EasyCutApp._parse_rate_limit("500") == 500.0

    def test_kilo(self):
        assert EasyCutApp._parse_rate_limit("100K") == 100 * 1024

    def test_kilo_lowercase(self):
        assert EasyCutApp._parse_rate_limit("100k") == 100 * 1024

    def test_mega(self):
        assert EasyCutApp._parse_rate_limit("2M") == 2 * 1024 ** 2

    def test_mega_lowercase(self):
        assert EasyCutApp._parse_rate_limit("1.5m") == 1.5 * 1024 ** 2

    def test_empty(self):
        assert EasyCutApp._parse_rate_limit("") is None

    def test_none(self):
        assert EasyCutApp._parse_rate_limit(None) is None

    def test_invalid(self):
        assert EasyCutApp._parse_rate_limit("abc") is None

    def test_non_string(self):
        assert EasyCutApp._parse_rate_limit(123) is None


class TestFormatTimecode:
    """EasyCutApp._format_timecode static method."""

    def test_zero(self):
        assert EasyCutApp._format_timecode(0) == "00:00:00"

    def test_one_hour(self):
        assert EasyCutApp._format_timecode(3600) == "01:00:00"

    def test_mixed(self):
        assert EasyCutApp._format_timecode(3661) == "01:01:01"

    def test_just_seconds(self):
        assert EasyCutApp._format_timecode(45) == "00:00:45"

    def test_minutes_and_seconds(self):
        assert EasyCutApp._format_timecode(125) == "00:02:05"


# ---------------------------------------------------------------------------
# Build download options (requires a minimal mock app)
# ---------------------------------------------------------------------------

class _FakeConfigManager:
    """Minimal config manager stub."""

    def __init__(self, data=None):
        self._data = data or {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value


class _FakePostProcessor:
    output_dir = "."
    ffmpeg_available = True


@pytest.fixture
def mock_app(monkeypatch):
    """Create a minimal EasyCutApp-like object with just the attributes
    needed for _build_download_options, get_ydl_opts_with_cookies, etc."""
    app = MagicMock(spec=EasyCutApp)
    app.config_manager = _FakeConfigManager()
    app.post_processor = _FakePostProcessor()
    app.output_dir = Path(".")

    # Translator stub — _build_download_options reads self.translator.get
    app.translator = MagicMock()
    app.translator.get = MagicMock(side_effect=lambda key, default="": default)

    # Tk variables as plain mock objects that return values via .get()
    app.sub_enable_var = MagicMock(get=MagicMock(return_value=False))
    app.sub_type_var = MagicMock(get=MagicMock(return_value="auto"))
    app.sub_format_var = MagicMock(get=MagicMock(return_value="srt"))
    app.sub_embed_var = MagicMock(get=MagicMock(return_value=False))
    app.sub_lang_entry = MagicMock(get=MagicMock(return_value="en"))
    app.audio_format_var = MagicMock(get=MagicMock(return_value="mp3"))
    app.audio_bitrate_var = MagicMock(get=MagicMock(return_value="192"))
    app.download_progress_hook = MagicMock()
    app._channel_limit_var = MagicMock(get=MagicMock(return_value="10"))

    # Bind the real static methods
    app._parse_rate_limit = EasyCutApp._parse_rate_limit

    return app


class TestBuildDownloadOptions:
    """Tests for _build_download_options via the real method."""

    def _call(self, app, **kwargs):
        # Bind the unbound method to our mock
        return EasyCutApp._build_download_options(
            app,
            output_template="%(title)s.%(ext)s",
            quality=kwargs.get("quality", "best"),
            mode=kwargs.get("mode", "full"),
            section=kwargs.get("section"),
            quiet=kwargs.get("quiet", False),
            format_id=kwargs.get("format_id"),
        )

    def test_default_best_format(self, mock_app):
        opts = self._call(mock_app)
        assert "bestvideo" in opts["format"]
        assert "bestaudio" in opts["format"]

    def test_specific_format_id_overrides_quality(self, mock_app):
        opts = self._call(mock_app, format_id="137")
        assert opts["format"] == "137"

    def test_audio_mode_adds_postprocessor(self, mock_app):
        opts = self._call(mock_app, mode="audio")
        pp = opts.get("postprocessors", [])
        assert len(pp) == 1
        assert pp[0]["key"] == "FFmpegExtractAudio"
        assert pp[0]["preferredcodec"] == "mp3"
        assert pp[0]["preferredquality"] == "192"

    def test_playlist_mode_noplaylist_false(self, mock_app):
        opts = self._call(mock_app, mode="playlist")
        assert opts["noplaylist"] is False

    def test_channel_mode_has_playlistend(self, mock_app):
        opts = self._call(mock_app, mode="channel")
        assert opts["noplaylist"] is False
        assert opts["playlistend"] == 10

    def test_full_mode_noplaylist_true(self, mock_app):
        opts = self._call(mock_app, mode="full")
        assert opts["noplaylist"] is True

    def test_section_adds_download_ranges(self, mock_app):
        section = {"start": 10, "end": 60}
        opts = self._call(mock_app, section=section)
        assert "download_ranges" in opts
        assert opts["force_keyframes_at_cuts"] is True

    def test_subtitles_enabled(self, mock_app):
        mock_app.sub_enable_var.get.return_value = True
        opts = self._call(mock_app)
        assert opts.get("writeautomaticsub") is True
        assert opts["subtitlesformat"] == "srt"

    def test_subtitles_embed(self, mock_app):
        mock_app.sub_enable_var.get.return_value = True
        mock_app.sub_embed_var.get.return_value = True
        opts = self._call(mock_app)
        pp_keys = [pp["key"] for pp in opts.get("postprocessors", [])]
        assert "FFmpegEmbedSubtitle" in pp_keys

    def test_premiere_compat_excludes_webm(self, mock_app):
        mock_app.config_manager.set("premiere_compat", True)
        opts = self._call(mock_app, quality="best")
        assert "[ext!=webm]" in opts["format"]

    def test_no_premiere_compat_no_webm_filter(self, mock_app):
        mock_app.config_manager.set("premiere_compat", False)
        opts = self._call(mock_app, quality="best")
        assert "[ext!=webm]" not in opts["format"]

    def test_1080p_quality(self, mock_app):
        opts = self._call(mock_app, quality="1080")
        assert "height<=1080" in opts["format"]

    def test_720p_quality(self, mock_app):
        opts = self._call(mock_app, quality="720")
        assert "height<=720" in opts["format"]

    def test_mp4_quality(self, mock_app):
        opts = self._call(mock_app, quality="mp4")
        assert "[ext=mp4]" in opts["format"]

    def test_audio_quality(self, mock_app):
        opts = self._call(mock_app, quality="audio")
        assert "bestaudio" in opts["format"]


class TestGetYdlOptsWithCookies:
    """Tests for get_ydl_opts_with_cookies: cookie, proxy, rate, retries."""

    def _call(self, app, base=None):
        return EasyCutApp.get_ydl_opts_with_cookies(app, base)

    def test_custom_cookie_file(self, mock_app, tmp_path):
        cookie = tmp_path / "my_cookies.txt"
        cookie.write_text("# Netscape cookie")
        mock_app.config_manager.set("cookies_file", str(cookie))
        opts = self._call(mock_app)
        assert opts["cookiefile"] == str(cookie)

    def test_default_cookie_file(self, mock_app, tmp_path, monkeypatch):
        # No custom cookie, but default exists
        default = tmp_path / "config" / "yt_cookies.txt"
        default.parent.mkdir()
        default.write_text("# Netscape cookie")
        monkeypatch.chdir(tmp_path)
        opts = self._call(mock_app)
        # The method uses relative Path("config") / "yt_cookies.txt"
        assert opts["cookiefile"] == str(Path("config") / "yt_cookies.txt")

    def test_no_cookie_file(self, mock_app, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        opts = self._call(mock_app)
        assert "cookiefile" not in opts

    def test_proxy_set(self, mock_app):
        mock_app.config_manager.set("proxy", "socks5://127.0.0.1:9050")
        opts = self._call(mock_app)
        assert opts["proxy"] == "socks5://127.0.0.1:9050"

    def test_proxy_empty(self, mock_app):
        opts = self._call(mock_app)
        assert "proxy" not in opts

    def test_rate_limit(self, mock_app):
        mock_app.config_manager.set("rate_limit", "5M")
        opts = self._call(mock_app)
        assert opts["ratelimit"] == 5 * 1024 ** 2

    def test_rate_limit_empty(self, mock_app):
        opts = self._call(mock_app)
        assert "ratelimit" not in opts

    def test_retries(self, mock_app):
        mock_app.config_manager.set("max_retries", 5)
        opts = self._call(mock_app)
        assert opts["retries"] == 5

    def test_retries_default(self, mock_app):
        # Default is 3 from _FakeConfigManager.get fallback
        opts = self._call(mock_app)
        assert opts["retries"] == 3

    def test_base_opts_preserved(self, mock_app):
        base = {"format": "bestvideo+bestaudio", "quiet": True}
        opts = self._call(mock_app, base)
        assert opts["format"] == "bestvideo+bestaudio"
        assert opts["quiet"] is True

    def test_base_opts_not_mutated(self, mock_app):
        base = {"format": "best"}
        mock_app.config_manager.set("proxy", "http://proxy")
        self._call(mock_app, base)
        # Original dict should not have been modified
        assert "proxy" not in base
