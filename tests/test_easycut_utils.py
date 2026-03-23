# -*- coding: utf-8 -*-
"""Tests for easycut.py — Static utility methods from EasyCutApp."""

import pytest

# Import the class directly — static methods don't need Tk
from easycut import EasyCutApp


class TestParseTimecode:
    """Tests for EasyCutApp._parse_timecode(time_text) -> int|None."""

    def test_mm_ss_basic(self):
        assert EasyCutApp._parse_timecode("1:30") == 90

    def test_mm_ss_padded(self):
        assert EasyCutApp._parse_timecode("01:30") == 90

    def test_hh_mm_ss_basic(self):
        assert EasyCutApp._parse_timecode("1:00:00") == 3600

    def test_hh_mm_ss_complex(self):
        assert EasyCutApp._parse_timecode("1:23:45") == 5025

    def test_zero(self):
        assert EasyCutApp._parse_timecode("0:00") == 0

    def test_single_number_seconds(self):
        assert EasyCutApp._parse_timecode("59") == 59

    def test_large_single_number(self):
        # Bare number is treated as total seconds with no upper limit
        assert EasyCutApp._parse_timecode("120") == 120

    def test_bare_total_seconds_large(self):
        # Common shorthand: type "90" to mean 1 min 30 s
        assert EasyCutApp._parse_timecode("90") == 90
        assert EasyCutApp._parse_timecode("3600") == 3600
        assert EasyCutApp._parse_timecode("7200") == 7200

    def test_empty_string(self):
        assert EasyCutApp._parse_timecode("") is None

    def test_letters(self):
        assert EasyCutApp._parse_timecode("abc") is None

    def test_too_many_parts(self):
        assert EasyCutApp._parse_timecode("1:2:3:4") is None

    def test_negative(self):
        assert EasyCutApp._parse_timecode("-1:00") is None

    def test_none_input(self):
        # Method might not handle None, but should not raise unhandled
        try:
            result = EasyCutApp._parse_timecode(None)
        except (TypeError, AttributeError):
            pass  # acceptable


class TestFormatTimecode:
    """Tests for EasyCutApp._format_timecode(total_seconds) -> str."""

    def test_zero(self):
        assert EasyCutApp._format_timecode(0) == "00:00:00"

    def test_one_minute_thirty(self):
        assert EasyCutApp._format_timecode(90) == "00:01:30"

    def test_one_hour(self):
        assert EasyCutApp._format_timecode(3600) == "01:00:00"

    def test_complex(self):
        assert EasyCutApp._format_timecode(3661) == "01:01:01"

    def test_max_day(self):
        assert EasyCutApp._format_timecode(86399) == "23:59:59"


class TestParseRateLimit:
    """Tests for EasyCutApp._parse_rate_limit(rate_text) -> float|None."""

    def test_plain_number(self):
        assert EasyCutApp._parse_rate_limit("100") == 100.0

    def test_kilobytes(self):
        assert EasyCutApp._parse_rate_limit("1K") == 1024.0

    def test_kilobytes_lowercase(self):
        assert EasyCutApp._parse_rate_limit("1k") == 1024.0

    def test_megabytes(self):
        assert EasyCutApp._parse_rate_limit("2M") == 2 * 1024 * 1024

    def test_fractional_kilobytes(self):
        assert EasyCutApp._parse_rate_limit("1.5K") == 1.5 * 1024

    def test_empty_string(self):
        assert EasyCutApp._parse_rate_limit("") is None

    def test_none_input(self):
        assert EasyCutApp._parse_rate_limit(None) is None

    def test_invalid_text(self):
        assert EasyCutApp._parse_rate_limit("abc") is None

    def test_integer_input(self):
        # Should handle non-string gracefully
        assert EasyCutApp._parse_rate_limit(123) is None


class TestIsValidYoutubeUrl:
    """Tests for EasyCutApp.is_valid_youtube_url(url) -> bool."""

    def test_standard_watch(self):
        assert EasyCutApp.is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_short_url(self):
        assert EasyCutApp.is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True

    def test_no_www(self):
        assert EasyCutApp.is_valid_youtube_url("https://youtube.com/watch?v=abc123") is True

    def test_http_no_s(self):
        assert EasyCutApp.is_valid_youtube_url("http://youtube.com/watch?v=abc123") is True

    def test_embed_url(self):
        assert EasyCutApp.is_valid_youtube_url("https://www.youtube.com/embed/abc123") is True

    def test_shorts_url(self):
        assert EasyCutApp.is_valid_youtube_url("https://youtube.com/shorts/abc123") is True

    def test_playlist_url(self):
        assert EasyCutApp.is_valid_youtube_url("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf") is True

    def test_live_url(self):
        assert EasyCutApp.is_valid_youtube_url("https://www.youtube.com/live/abc123") is True

    def test_channel_url(self):
        # Channel URLs are YouTube URLs
        assert EasyCutApp.is_valid_youtube_url("https://www.youtube.com/@mkbhd") is True

    def test_vimeo_rejected(self):
        assert EasyCutApp.is_valid_youtube_url("https://vimeo.com/123456") is False

    def test_empty_string(self):
        assert EasyCutApp.is_valid_youtube_url("") is False

    def test_random_text(self):
        assert EasyCutApp.is_valid_youtube_url("not a url at all") is False

    def test_none_input(self):
        try:
            result = EasyCutApp.is_valid_youtube_url(None)
            assert result is False
        except (TypeError, AttributeError):
            pass  # also acceptable
