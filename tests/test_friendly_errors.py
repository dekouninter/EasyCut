# -*- coding: utf-8 -*-
"""Tests for _get_friendly_error — yt-dlp error message mapping.

Verifies that every known error pattern is correctly matched and that
the first-match-wins rule holds.  The translator mock returns the i18n
key itself so we can assert on the key string.
"""

import sys
import types
from unittest.mock import MagicMock

import pytest

# Stub yt_dlp before importing easycut
fake_ytdlp = types.ModuleType("yt_dlp")
fake_ytdlp.YoutubeDL = MagicMock
sys.modules.setdefault("yt_dlp", fake_ytdlp)

from easycut import EasyCutApp


@pytest.fixture
def mock_app():
    app = MagicMock(spec=EasyCutApp)
    # translator.get returns the key itself
    app.translator = MagicMock()
    app.translator.get = MagicMock(side_effect=lambda key, default="": key)
    return app


def _call(app, msg):
    return EasyCutApp._get_friendly_error(app, msg)


# ----- Private Video Patterns -----

class TestPrivateVideo:
    def test_private_video_lowercase(self, mock_app):
        assert _call(mock_app, "private video detected") == "err_private"

    def test_video_is_private(self, mock_app):
        assert _call(mock_app, "Video is private") == "err_private"


# ----- Age-Restricted Patterns -----

class TestAgeRestricted:
    def test_sign_in_to_confirm_age(self, mock_app):
        assert _call(mock_app, "Sign in to confirm your age") == "err_age_restricted"

    def test_age_restricted_hyphen(self, mock_app):
        assert _call(mock_app, "This content is age-restricted") == "err_age_restricted"

    def test_age_restricted_no_hyphen(self, mock_app):
        assert _call(mock_app, "age restricted content") == "err_age_restricted"


# ----- Unavailable Patterns -----

class TestUnavailable:
    def test_video_unavailable(self, mock_app):
        assert _call(mock_app, "Video unavailable in your region") == "err_unavailable"

    def test_video_removed(self, mock_app):
        assert _call(mock_app, "This video has been removed") == "err_unavailable"

    def test_no_longer_available(self, mock_app):
        assert _call(mock_app, "This video is no longer available") == "err_unavailable"

    def test_not_available(self, mock_app):
        assert _call(mock_app, "Video is not available") == "err_unavailable"


# ----- Geo-Blocked Patterns -----

class TestGeoBlocked:
    def test_geo_keyword(self, mock_app):
        assert _call(mock_app, "Geo-restricted content") == "err_geo_blocked"

    def test_not_available_in_country(self, mock_app):
        # "not available in your country" also matches "video is not available"
        # from the unavailable pattern above, so first-match-wins → err_unavailable.
        # Use the explicit geo keyword instead.
        assert _call(mock_app, "Content not available in your country due to geo restrictions") == "err_geo_blocked"

    def test_blocked_in_country(self, mock_app):
        assert _call(mock_app, "Content blocked in your country") == "err_geo_blocked"


# ----- Premiere / Scheduled Patterns -----

class TestPremiereScheduled:
    def test_premieres_in(self, mock_app):
        assert _call(mock_app, "Premieres in 3 hours") == "err_live_not_started"

    def test_scheduled_for(self, mock_app):
        assert _call(mock_app, "This stream is scheduled for 2 PM") == "err_live_not_started"

    def test_live_event_will_begin(self, mock_app):
        assert _call(mock_app, "Live event will begin shortly") == "err_live_not_started"


# ----- Rate-Limited Patterns -----

class TestRateLimited:
    def test_http_429(self, mock_app):
        assert _call(mock_app, "HTTP Error 429: Too Many Requests") == "err_rate_limited"

    def test_too_many_requests(self, mock_app):
        assert _call(mock_app, "too many requests from your IP") == "err_rate_limited"

    def test_rate_limit_keyword(self, mock_app):
        assert _call(mock_app, "rate limit exceeded") == "err_rate_limited"


# ----- Network Error Patterns -----

class TestNetworkErrors:
    def test_unable_to_download(self, mock_app):
        assert _call(mock_app, "Unable to download webpage") == "err_network"

    def test_connection_error(self, mock_app):
        assert _call(mock_app, "Connection refused") == "err_network"

    def test_timed_out(self, mock_app):
        assert _call(mock_app, "Request timed out") == "err_network"

    def test_urlopen_error(self, mock_app):
        assert _call(mock_app, "urlopen error: network error") == "err_network"

    def test_network_unreachable(self, mock_app):
        assert _call(mock_app, "Network is unreachable") == "err_network"


# ----- No Formats Patterns -----

class TestNoFormats:
    def test_no_video_formats(self, mock_app):
        assert _call(mock_app, "No video formats found") == "err_no_formats"

    def test_requested_format_not_available(self, mock_app):
        assert _call(mock_app, "Requested format not available") == "err_no_formats"

    def test_no_suitable_format(self, mock_app):
        assert _call(mock_app, "No suitable format found") == "err_no_formats"


# ----- FFmpeg / Postprocessing Patterns -----

class TestFFmpegPost:
    def test_ffmpeg_not_found(self, mock_app):
        assert _call(mock_app, "ffmpeg not found") == "err_ffmpeg_post"

    def test_ffprobe_error(self, mock_app):
        assert _call(mock_app, "ffprobe: command not found") == "err_ffmpeg_post"

    def test_postprocessing_failed(self, mock_app):
        assert _call(mock_app, "Postprocessing: error converting") == "err_ffmpeg_post"


# ----- Copyright Patterns -----

class TestCopyright:
    def test_copyright(self, mock_app):
        assert _call(mock_app, "This video contains copyright content") == "err_copyright"

    def test_copyrighted(self, mock_app):
        assert _call(mock_app, "Copyrighted material detected") == "err_copyright"


# ----- Members-Only Patterns -----

class TestMembersOnly:
    def test_join_channel(self, mock_app):
        assert _call(mock_app, "Join this channel to get access") == "err_members_only"

    def test_members_only_hyphen(self, mock_app):
        assert _call(mock_app, "This is members-only content") == "err_members_only"

    def test_members_only_no_hyphen(self, mock_app):
        assert _call(mock_app, "members only video") == "err_members_only"


# ----- Premium Patterns -----

class TestPremium:
    def test_premium(self, mock_app):
        assert _call(mock_app, "Premium content only") == "err_premium_only"

    def test_youtube_red(self, mock_app):
        assert _call(mock_app, "YouTube Red original") == "err_premium_only"


# ----- Cookie / Browser Patterns -----

class TestCookieIssues:
    def test_could_not_copy_cookie(self, mock_app):
        assert _call(mock_app, "Could not copy cookie database") == "browser_test_browser_open"

    def test_cookie_database(self, mock_app):
        assert _call(mock_app, "Failed to read cookie database") == "browser_test_browser_open"


# ----- Fallback / Edge Cases -----

class TestFallback:
    def test_unknown_error_returns_err_unknown(self, mock_app):
        result = _call(mock_app, "Something completely unknown happened")
        assert "err_unknown" in result

    def test_long_message_truncated(self, mock_app):
        long_msg = "x" * 200
        result = _call(mock_app, long_msg)
        # Fallback includes message truncated to 120 chars
        assert len(result.split("\n")[1]) <= 120

    def test_case_insensitive(self, mock_app):
        assert _call(mock_app, "VIDEO IS PRIVATE") == "err_private"

    def test_first_match_wins(self, mock_app):
        # "connection" matches network BEFORE any other pattern
        result = _call(mock_app, "connection error with copyrighted content")
        assert result == "err_network"

    def test_empty_message(self, mock_app):
        result = _call(mock_app, "")
        assert "err_unknown" in result
