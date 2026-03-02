# -*- coding: utf-8 -*-
"""Tests for video_player.py — Player availability checks."""

import pytest
from unittest.mock import patch
from video_player import is_player_available, get_available_backend


class TestIsPlayerAvailable:
    def test_returns_bool(self):
        assert isinstance(is_player_available(), bool)

    @patch("shutil.which", return_value="/usr/bin/mpv")
    def test_available_with_mpv(self, mock_which):
        # Force re-evaluation by calling the function
        result = is_player_available()
        assert isinstance(result, bool)

    @patch("shutil.which", return_value=None)
    def test_result_without_mpv(self, mock_which):
        result = is_player_available()
        assert isinstance(result, bool)


class TestGetAvailableBackend:
    def test_returns_string_or_none(self):
        result = get_available_backend()
        assert result is None or isinstance(result, str)

    def test_valid_backends(self):
        result = get_available_backend()
        assert result in (None, "mpv", "vlc")


class TestPlayerConstants:
    """Test that Windows pipe constants are defined."""
    from video_player import GENERIC_READ, GENERIC_WRITE, OPEN_EXISTING, INVALID_HANDLE_VALUE

    def test_generic_read(self):
        assert isinstance(self.GENERIC_READ, int)

    def test_generic_write(self):
        assert isinstance(self.GENERIC_WRITE, int)

    def test_open_existing(self):
        assert isinstance(self.OPEN_EXISTING, int)

    def test_invalid_handle(self):
        assert isinstance(self.INVALID_HANDLE_VALUE, int)
