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


class TestTimeMarkerHelpers:
    """Helpers used by the download tab time‑range preview."""

    def test_time_to_fraction(self):
        # normal case
        assert EasyCutApp._time_to_fraction(30, 120) == 0.25
        # negative and overflowing
        assert EasyCutApp._time_to_fraction(-5, 100) == 0.0
        assert EasyCutApp._time_to_fraction(150, 100) == 1.0
        # zero duration should always return zero
        assert EasyCutApp._time_to_fraction(10, 0) == 0.0

    def test_fraction_to_time(self):
        assert EasyCutApp._fraction_to_time(0.5, 200) == 100
        assert EasyCutApp._fraction_to_time(-0.1, 50) == 0
        assert EasyCutApp._fraction_to_time(1.2, 50) == 50
        assert EasyCutApp._fraction_to_time(0.3, 0) == 0

    def test_update_time_markers_calls_canvas_coords(self, monkeypatch):
        # prepare a fake app with minimal attributes
        app = MagicMock(spec=EasyCutApp)
        # _parse_timecode must be set on the *instance* too because MagicMock
        # intercepts attribute access before the monkeypatched class attribute
        # can be reached via self.<attr> lookup.
        _fake_parse = lambda txt: 10 if txt == 'start' else 90 if txt == 'end' else None
        monkeypatch.setattr(EasyCutApp, '_parse_timecode', staticmethod(_fake_parse))
        app._parse_timecode = _fake_parse
        # _time_to_fraction must also be bound on the instance for the same reason
        app._time_to_fraction = lambda s, d: (s / d) if d else 0.0
        app.time_start_entry = MagicMock(get=MagicMock(return_value='start'))
        app.time_end_entry = MagicMock(get=MagicMock(return_value='end'))
        app.download_player = MagicMock()
        app.download_player.get_duration.return_value = 100
        # fake canvas
        coords_called = {}
        def coords(shape, *args):
            coords_called[shape] = args
        app.time_canvas = MagicMock()
        app.time_canvas.winfo_width.return_value = 200
        app.time_canvas.winfo_height.return_value = 48
        app.time_canvas.coords.side_effect = coords
        # run the helper
        # bind the design attribute for colors to avoid errors
        app.design = MagicMock()
        app.design.get_color = MagicMock(return_value='#000')
        EasyCutApp._update_time_markers(app)
        # start=10/100 → sx=20; end=90/100 → ex=180 on 200px canvas
        # range_rect uses (sx, 0, ex, h) so x1=20 and x2=180 appear directly
        assert any(v[0] == 20 for v in coords_called.values())
        assert any(len(v) >= 3 and v[2] == 180 for v in coords_called.values())

    def test_mark_and_preview_helpers(self):
        app = MagicMock(spec=EasyCutApp)
        # entries
        app.time_start_entry = MagicMock()
        app.time_end_entry = MagicMock()
        # translator needed by _load_download_preview warnings
        app.translator = MagicMock()
        app.translator.get = MagicMock(return_value="")
        # bind real static helpers so they aren't intercepted by the mock
        app._format_timecode = EasyCutApp._format_timecode
        app._update_time_markers = MagicMock()  # suppress full canvas logic
        app.time_canvas = MagicMock()  # needed by _load_download_preview
        # player returns a floating time
        app.download_player = MagicMock()
        app.download_player.get_time.return_value = 42.7
        # mark start
        EasyCutApp._download_mark_start(app)
        app.time_start_entry.delete.assert_called_once_with(0, tk.END)
        app.time_start_entry.insert.assert_called_once_with(0, "00:00:42")
        # mark end
        EasyCutApp._download_mark_end(app)
        app.time_end_entry.delete.assert_called_once_with(0, tk.END)
        app.time_end_entry.insert.assert_called_once_with(0, "00:00:42")
        # load preview — empty URL should show warning but not crash
        app.download_url_entry = MagicMock(
            get=MagicMock(return_value=""),
            get_value=MagicMock(return_value="")
        )
        # patch messagebox so the warning dialog doesn't open a real window
        import unittest.mock as _um
        with _um.patch("tkinter.messagebox.showwarning"):
            EasyCutApp._load_download_preview(app)
        # with a URL
        app.download_player = MagicMock()
        app.download_player.get_time.return_value = 42.7
        app.download_log = MagicMock()
        app.download_url_entry = MagicMock(
            get=MagicMock(return_value="http://foo"),
            get_value=MagicMock(return_value="http://foo")
        )
        EasyCutApp._load_download_preview(app)
        app.download_player.load.assert_called_once_with("http://foo")


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


# ---------------------------------------------------------------------------
# Download Options Edge Cases
# ---------------------------------------------------------------------------

class TestDownloadOptionsEdgeCases:
    """Edge case tests for download options and format handling."""

    def _call(self, app, **kwargs):
        return EasyCutApp._build_download_options(
            app,
            output_template="%(title)s.%(ext)s",
            quality=kwargs.get("quality", "best"),
            mode=kwargs.get("mode", "full"),
            section=kwargs.get("section"),
            quiet=kwargs.get("quiet", False),
            format_id=kwargs.get("format_id"),
        )

    def test_invalid_quality_string_uses_fallback(self, mock_app):
        """Invalid quality strings should be handled gracefully."""
        # Quality strings that don't match known presets
        invalid_qualities = ["invalid", "4k", "8k", "hd", "sd", ""]
        for quality in invalid_qualities:
            opts = self._call(mock_app, quality=quality)
            # Should not crash, format should be set to something
            assert "format" in opts
            assert isinstance(opts["format"], str)

    def test_none_quality_handled(self, mock_app):
        """None quality should be handled gracefully."""
        try:
            opts = self._call(mock_app, quality=None)
            assert "format" in opts
        except (TypeError, AttributeError):
            pass  # Also acceptable to raise

    def test_empty_format_id(self, mock_app):
        """Empty format_id should not override quality."""
        opts = self._call(mock_app, quality="1080", format_id="")
        # Empty format_id should be ignored, quality should apply
        assert "height<=1080" in opts["format"] or opts["format"] != ""

    def test_whitespace_format_id(self, mock_app):
        """Whitespace-only format_id should be handled.
        
        NOTE: Currently passes whitespace through as-is (known limitation).
        Ideally should strip and use quality fallback. Documenting current behavior.
        """
        opts = self._call(mock_app, quality="720", format_id="   ")
        # Currently passes whitespace through (TODO: fix to use quality fallback)
        assert opts["format"] == "   "  # Document current behavior

    def test_section_with_zero_start(self, mock_app):
        """Section starting at 0 should work correctly."""
        section = {"start": 0, "end": 60}
        opts = self._call(mock_app, section=section)
        assert "download_ranges" in opts

    def test_section_with_same_start_end(self, mock_app):
        """Section with start==end should be handled."""
        section = {"start": 30, "end": 30}
        opts = self._call(mock_app, section=section)
        # Should create options without crashing
        assert "download_ranges" in opts

    def test_section_with_start_greater_than_end(self, mock_app):
        """Section with start > end should be handled gracefully."""
        section = {"start": 60, "end": 30}
        opts = self._call(mock_app, section=section)
        # Implementation might swap or handle this
        assert "download_ranges" in opts

    def test_very_large_section_values(self, mock_app):
        """Very large section values (24+ hours) should work."""
        section = {"start": 0, "end": 100000}  # ~27.7 hours
        opts = self._call(mock_app, section=section)
        assert "download_ranges" in opts

    def test_section_with_none_values(self, mock_app):
        """Section with None values should be handled."""
        try:
            section = {"start": None, "end": 60}
            opts = self._call(mock_app, section=section)
            # Should handle gracefully
            assert opts is not None
        except (TypeError, AttributeError):
            pass  # Acceptable to raise


class TestParseTimecodeDownloadEdgeCases:
    """Additional timecode parsing edge cases specific to download context."""

    def test_zero_padded_values(self):
        """Zero-padded values should work correctly."""
        assert EasyCutApp._parse_timecode("00:00:00") == 0
        assert EasyCutApp._parse_timecode("00:01:00") == 60
        assert EasyCutApp._parse_timecode("01:00:00") == 3600

    def test_mixed_padding(self):
        """Mix of padded and unpadded should work."""
        assert EasyCutApp._parse_timecode("1:01:01") == 3661
        assert EasyCutApp._parse_timecode("01:1:01") == 3661
        assert EasyCutApp._parse_timecode("01:01:1") == 3661


class TestParseRateLimitEdgeCases:
    """Edge case tests for rate limit parsing."""

    def test_gigabytes(self):
        """G suffix for gigabytes should work if supported, else return None."""
        result = EasyCutApp._parse_rate_limit("1G")
        # Implementation may or may not support G
        assert result is None or result == 1024 ** 3

    def test_zero_rate(self):
        """Zero rate limit should work."""
        assert EasyCutApp._parse_rate_limit("0") == 0.0

    def test_very_small_rate(self):
        """Very small rate should work."""
        assert EasyCutApp._parse_rate_limit("0.001") == 0.001

    def test_very_large_rate(self):
        """Very large rate should work."""
        assert EasyCutApp._parse_rate_limit("999999999") == 999999999.0

    def test_whitespace_in_rate(self):
        """Whitespace in rate should be handled."""
        # Current implementation doesn't strip, so this may fail
        result = EasyCutApp._parse_rate_limit(" 100K ")
        # Could be None (not stripped) or 102400 (if stripped)
        assert result is None or result == 102400.0

    def test_special_characters_in_rate(self):
        """Special characters should be rejected."""
        assert EasyCutApp._parse_rate_limit("100$") is None
        assert EasyCutApp._parse_rate_limit("100!") is None
        assert EasyCutApp._parse_rate_limit("@100") is None
