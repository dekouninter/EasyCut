# -*- coding: utf-8 -*-
"""Tests for easycut.py — _YTLogger, _is_js_runtime_outdated, and more utility tests."""

import pytest
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from easycut import _YTLogger, EasyCutApp


# ─────────────────────────────────────────────
#  _YTLogger
# ─────────────────────────────────────────────

class TestYTLogger:
    def test_suppress_fragments_is_tuple(self):
        assert isinstance(_YTLogger._SUPPRESS_FRAGMENTS, tuple)

    def test_suppress_fragments_not_empty(self):
        assert len(_YTLogger._SUPPRESS_FRAGMENTS) > 0

    def test_debug_is_noop(self):
        """debug() should not raise nor log."""
        logger = _YTLogger()
        logger.debug("some debug message")  # Should not raise

    def test_info_is_noop(self):
        """info() should not raise nor log."""
        logger = _YTLogger()
        logger.info("some info message")  # Should not raise

    def test_error_logs(self, caplog):
        logger = _YTLogger()
        with caplog.at_level(logging.ERROR):
            logger.error("something broke")
        assert any("[yt-dlp] something broke" in r.message for r in caplog.records)

    def test_warning_suppressed_deno(self, caplog):
        logger = _YTLogger()
        with caplog.at_level(logging.WARNING):
            logger.warning("Deno not found in PATH")
        # Suppressed warnings should not appear in log
        assert not any("Deno" in r.message for r in caplog.records)

    def test_warning_suppressed_jsinterp(self, caplog):
        logger = _YTLogger()
        with caplog.at_level(logging.WARNING):
            logger.warning("jsinterp extraction failed")
        assert not any("jsinterp" in r.message for r in caplog.records)

    def test_warning_not_suppressed_passes_through(self, caplog):
        logger = _YTLogger()
        with caplog.at_level(logging.WARNING):
            logger.warning("Video unavailable for region lock")
        assert any("Video unavailable" in r.message for r in caplog.records)

    def test_suppress_deno_not_found(self):
        assert "Deno not found" in _YTLogger._SUPPRESS_FRAGMENTS

    def test_suppress_browser_javascript(self):
        assert "Browser JavaScript" in _YTLogger._SUPPRESS_FRAGMENTS

    def test_suppress_ejs(self):
        assert "EJS" in _YTLogger._SUPPRESS_FRAGMENTS


# ─────────────────────────────────────────────
#  _is_js_runtime_outdated (instance method, uses no self state)
# ─────────────────────────────────────────────

class TestIsJsRuntimeOutdated:
    """Test via unbound call on a minimal object."""

    @staticmethod
    def _call(version: str) -> bool:
        # Call unbound - method only uses the version param
        return EasyCutApp._is_js_runtime_outdated(None, version)

    def test_old_version(self):
        assert self._call("16.0.0") is True

    def test_minimum_ok_version(self):
        assert self._call("18.0.0") is False

    def test_recent_version(self):
        assert self._call("22.11.0") is False

    def test_edge_version_17(self):
        assert self._call("17.9.0") is True

    def test_invalid_version_string(self):
        assert self._call("abc") is False

    def test_empty_string(self):
        assert self._call("") is False

    def test_just_major(self):
        assert self._call("20") is False

    def test_just_major_old(self):
        assert self._call("10") is True
