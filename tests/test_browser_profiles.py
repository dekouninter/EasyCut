# -*- coding: utf-8 -*-
"""Tests for browser profile/account detection helpers.

Covers get_browser_profile_paths and detect_youtube_accounts.
"""

import sys
import json
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Stub yt_dlp before importing easycut
fake_ytdlp = types.ModuleType("yt_dlp")
fake_ytdlp.YoutubeDL = MagicMock
sys.modules.setdefault("yt_dlp", fake_ytdlp)

from easycut import EasyCutApp


class _FakeConfigManager:
    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value


@pytest.fixture
def mock_app():
    app = MagicMock(spec=EasyCutApp)
    app.config_manager = _FakeConfigManager()
    app.translator = MagicMock()
    app.translator.get = MagicMock(side_effect=lambda k, d="": d)
    app.design = MagicMock()
    app.design.get_color = MagicMock(return_value="#aaa")
    return app


# ---------------------------------------------------------------------------
# get_browser_profile_paths
# ---------------------------------------------------------------------------

class TestGetBrowserProfilePaths:
    """Tests for get_browser_profile_paths."""

    def test_unknown_browser_returns_empty(self, mock_app):
        result = EasyCutApp.get_browser_profile_paths(mock_app, "safari")
        assert result == []

    def test_chrome_base_not_exists(self, mock_app, tmp_path):
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "chrome")
        assert result == []

    def test_chrome_default_profile(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        (base / "Default").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "chrome")
        assert len(result) == 1
        assert result[0][0] == "Default"

    def test_chrome_multiple_profiles(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        (base / "Default").mkdir(parents=True)
        (base / "Profile 1").mkdir(parents=True)
        (base / "Profile 2").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "chrome")
        assert len(result) == 3
        names = [r[0] for r in result]
        assert "Default" in names
        assert "Profile 1" in names
        assert "Profile 2" in names

    def test_edge_profile(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data"
        (base / "Default").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "edge")
        assert len(result) == 1

    def test_brave_profile(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data"
        (base / "Default").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "brave")
        assert len(result) == 1

    def test_firefox_profiles(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        (base / "abc123.default").mkdir(parents=True)
        (base / "xyz456.dev-edition").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "firefox")
        assert len(result) == 2

    def test_firefox_ignores_hidden_dirs(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        (base / "normal_profile").mkdir(parents=True)
        (base / ".hidden").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = EasyCutApp.get_browser_profile_paths(mock_app, "firefox")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# detect_youtube_accounts
# ---------------------------------------------------------------------------

class TestDetectYoutubeAccounts:
    """Tests for detect_youtube_accounts."""

    def test_browser_none_returns_empty(self, mock_app):
        mock_app.config_manager._data["browser_cookies"] = "none"
        result = EasyCutApp.detect_youtube_accounts(mock_app)
        assert result == []

    def test_chrome_with_account_info(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        default = base / "Default"
        default.mkdir(parents=True)
        prefs = {"account_info": [{"full_name": "John Doe", "email": "john@example.com"}]}
        (default / "Preferences").write_text(json.dumps(prefs), encoding="utf-8")

        mock_app.config_manager._data["browser_cookies"] = "chrome"

        with patch("pathlib.Path.home", return_value=tmp_path):
            mock_app.get_browser_profile_paths = lambda b: EasyCutApp.get_browser_profile_paths(mock_app, b)
            result = EasyCutApp.detect_youtube_accounts(mock_app)

        assert len(result) == 1
        assert "John Doe" in result[0][0]
        assert result[0][1] == "chrome"

    def test_chrome_without_account_info(self, mock_app, tmp_path):
        base = tmp_path / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        default = base / "Default"
        default.mkdir(parents=True)
        prefs = {"some_other_key": "value"}
        (default / "Preferences").write_text(json.dumps(prefs), encoding="utf-8")

        mock_app.config_manager._data["browser_cookies"] = "chrome"

        with patch("pathlib.Path.home", return_value=tmp_path):
            mock_app.get_browser_profile_paths = lambda b: EasyCutApp.get_browser_profile_paths(mock_app, b)
            result = EasyCutApp.detect_youtube_accounts(mock_app)

        assert len(result) == 1
        # fallback display name: "Chrome - Default"
        assert "Chrome" in result[0][0]

    def test_default_browser_is_chrome(self, mock_app, tmp_path):
        """When browser_cookies is not set, should default to chrome."""
        # No browser_cookies set → config_manager.get returns None → default is "chrome"
        # Actually the method does: browser = self.config_manager.get("browser_cookies", "chrome")
        # So unset returns "chrome", not "none"
        base = tmp_path / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        (base / "Default").mkdir(parents=True)

        with patch("pathlib.Path.home", return_value=tmp_path):
            mock_app.get_browser_profile_paths = lambda b: EasyCutApp.get_browser_profile_paths(mock_app, b)
            result = EasyCutApp.detect_youtube_accounts(mock_app)

        assert len(result) == 1
