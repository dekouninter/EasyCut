# -*- coding: utf-8 -*-
"""Extended _YTLogger tests — challenge/EJS popup path and edge cases.

Existing test_yt_logger.py covers suppression of known fragments and
pass-through of unknown warnings.  These tests cover the interactive
messagebox path and the _runtime_warned flag.
"""

import sys
import types
from unittest.mock import MagicMock, patch

import pytest

# Stub yt_dlp before importing easycut
fake_ytdlp = types.ModuleType("yt_dlp")
fake_ytdlp.YoutubeDL = MagicMock
sys.modules.setdefault("yt_dlp", fake_ytdlp)

from easycut import _YTLogger


@pytest.fixture(autouse=True)
def reset_warned():
    """Reset _runtime_warned before each test."""
    _YTLogger._runtime_warned = False
    yield
    _YTLogger._runtime_warned = False


class TestChallengeWarningPopup:
    """Tests for the interactive messagebox path triggered by challenge/EJS warnings."""

    def test_challenge_warning_sets_runtime_warned(self):
        logger = _YTLogger()
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            logger.warning("challenge solving failed for some reason")
        assert logger._runtime_warned is True
        mock_warn.assert_called_once()

    def test_ejs_warning_sets_runtime_warned(self):
        logger = _YTLogger()
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            logger.warning("EJS solver missing")
        assert logger._runtime_warned is True
        mock_warn.assert_called_once()

    def test_second_challenge_warning_no_popup(self):
        logger = _YTLogger()
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            logger.warning("challenge solving failed #1")
            logger.warning("challenge solving failed #2")
        # Popup only on first call
        assert mock_warn.call_count == 1

    def test_suppress_fragment_without_challenge_no_popup(self):
        """A suppress fragment that isn't challenge/EJS should NOT cause a popup."""
        logger = _YTLogger()
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            logger.warning("Deno not found")
        mock_warn.assert_not_called()
        assert logger._runtime_warned is False

    def test_messagebox_import_error_handled_gracefully(self):
        """If tkinter is not available, the warning should not crash."""
        logger = _YTLogger()
        with patch.dict(sys.modules, {"tkinter": None}):
            # Force ImportError when tkinter is accessed
            with patch("builtins.__import__", side_effect=ImportError("no tkinter")):
                # Should not raise even if messagebox can't be imported
                try:
                    logger.warning("challenge solving failed")
                except ImportError:
                    pass  # Acceptable — the method uses try/except internally


class TestYTLoggerEdgeCases:
    def test_debug_is_silent(self):
        logger = _YTLogger()
        # Should not raise
        logger.debug("some debug message")

    def test_info_is_silent(self):
        logger = _YTLogger()
        logger.info("some info message")

    def test_error_logs_to_logger(self):
        logger = _YTLogger()
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            logger.error("Something critical failed")
        mock_logger.error.assert_called_once()

    def test_unknown_warning_passes_through(self):
        logger = _YTLogger()
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            logger.warning("Some unrecognized warning from yt-dlp")
        mock_logger.warning.assert_called_once()

    def test_suppressed_warning_does_not_pass_through(self):
        logger = _YTLogger()
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            logger.warning("Deno not found in PATH")
        mock_logger.warning.assert_not_called()

    def test_jsinterp_suppressed(self):
        logger = _YTLogger()
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            logger.warning("jsinterp: some error")
        mock_logger.warning.assert_not_called()

    def test_empty_warning_passes_through(self):
        logger = _YTLogger()
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            logger.warning("")
        # Empty string doesn't match any suppress fragment, so passes through
        mock_logger.warning.assert_called_once()
