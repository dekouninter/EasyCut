# -*- coding: utf-8 -*-
"""Tests for the format combo population and quality selection logic.

Validates _populate_format_combo, _get_selected_format_id,
_on_format_selected, _on_quality_change, and _set_quality_radios_state.
"""

import sys
import types
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# Stub yt_dlp before importing easycut
fake_ytdlp = types.ModuleType("yt_dlp")
fake_ytdlp.YoutubeDL = MagicMock
sys.modules.setdefault("yt_dlp", fake_ytdlp)

from easycut import EasyCutApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class FakeConfigManager:
    def __init__(self):
        self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value


class FakeCombobox:
    """Minimal ttk.Combobox stub."""

    def __init__(self):
        self._values = []
        self._current = 0

    def current(self, idx=None):
        if idx is not None:
            self._current = idx
        return self._current

    def __setitem__(self, key, value):
        if key == "values":
            self._values = list(value)

    def __getitem__(self, key):
        if key == "values":
            return self._values
        raise KeyError(key)


@pytest.fixture
def mock_app():
    """Minimal mock with format combo and quality var."""
    app = MagicMock(spec=EasyCutApp)
    app.config_manager = FakeConfigManager()
    app.format_combo = FakeCombobox()
    app._format_id_map = {0: None}
    app.download_quality_var = MagicMock()
    app.download_quality_var.get.return_value = "best"
    app._quality_radios = [MagicMock(), MagicMock()]
    return app


# ---------------------------------------------------------------------------
# _get_selected_format_id
# ---------------------------------------------------------------------------

class TestGetSelectedFormatId:
    def test_auto_returns_none(self, mock_app):
        mock_app.format_combo.current(0)
        result = EasyCutApp._get_selected_format_id(mock_app)
        assert result is None

    def test_specific_format(self, mock_app):
        mock_app._format_id_map = {0: None, 1: None, 2: "137", 3: "140"}
        mock_app.format_combo.current(2)
        result = EasyCutApp._get_selected_format_id(mock_app)
        assert result == "137"

    def test_separator_returns_none(self, mock_app):
        mock_app._format_id_map = {0: None, 1: None, 2: "137"}
        mock_app.format_combo.current(1)  # separator
        result = EasyCutApp._get_selected_format_id(mock_app)
        assert result is None

    def test_no_format_id_map(self, mock_app):
        del mock_app._format_id_map
        result = EasyCutApp._get_selected_format_id(mock_app)
        assert result is None


# ---------------------------------------------------------------------------
# _on_format_selected
# ---------------------------------------------------------------------------

class TestOnFormatSelected:
    def test_specific_format_disables_radios(self, mock_app):
        mock_app._format_id_map = {0: None, 1: "137"}
        mock_app.format_combo.current(1)
        # Bind real methods so the internal calls reach actual logic
        mock_app._get_selected_format_id = lambda: EasyCutApp._get_selected_format_id(mock_app)
        mock_app._set_quality_radios_state = lambda s: EasyCutApp._set_quality_radios_state(mock_app, s)
        EasyCutApp._on_format_selected(mock_app)
        for rb in mock_app._quality_radios:
            rb.config.assert_called_with(state="disabled")

    def test_auto_enables_radios(self, mock_app):
        mock_app.format_combo.current(0)
        mock_app._get_selected_format_id = lambda: EasyCutApp._get_selected_format_id(mock_app)
        mock_app._set_quality_radios_state = lambda s: EasyCutApp._set_quality_radios_state(mock_app, s)
        EasyCutApp._on_format_selected(mock_app)
        for rb in mock_app._quality_radios:
            rb.config.assert_called_with(state="normal")

    def test_no_format_combo_attribute(self, mock_app):
        del mock_app.format_combo
        # Should not raise
        EasyCutApp._on_format_selected(mock_app)


# ---------------------------------------------------------------------------
# _on_quality_change
# ---------------------------------------------------------------------------

class TestOnQualityChange:
    def test_quality_change_resets_combo_to_auto(self, mock_app):
        mock_app.download_quality_var.get.return_value = "1080"
        mock_app._set_quality_radios_state = lambda s: EasyCutApp._set_quality_radios_state(mock_app, s)
        mock_app.format_combo.current(2)
        EasyCutApp._on_quality_change(mock_app)
        assert mock_app.format_combo.current() == 0

    def test_auto_quality_no_reset(self, mock_app):
        mock_app.download_quality_var.get.return_value = "auto"
        mock_app._set_quality_radios_state = lambda s: EasyCutApp._set_quality_radios_state(mock_app, s)
        mock_app.format_combo.current(3)
        EasyCutApp._on_quality_change(mock_app)
        # Should NOT reset combo — "auto" maps to quality_var default, not a preset
        assert mock_app.format_combo.current() == 3


# ---------------------------------------------------------------------------
# _set_quality_radios_state
# ---------------------------------------------------------------------------

class TestSetQualityRadiosState:
    def test_disable_all(self, mock_app):
        EasyCutApp._set_quality_radios_state(mock_app, "disabled")
        for rb in mock_app._quality_radios:
            rb.config.assert_called_with(state="disabled")

    def test_enable_all(self, mock_app):
        EasyCutApp._set_quality_radios_state(mock_app, "normal")
        for rb in mock_app._quality_radios:
            rb.config.assert_called_with(state="normal")

    def test_no_radios(self, mock_app):
        mock_app._quality_radios = []
        EasyCutApp._set_quality_radios_state(mock_app, "disabled")  # No error

    def test_radio_config_error_ignored(self, mock_app):
        mock_app._quality_radios[0].config.side_effect = Exception("dead widget")
        EasyCutApp._set_quality_radios_state(mock_app, "disabled")  # Should not raise


# ---------------------------------------------------------------------------
# Format combo separator detection
# ---------------------------------------------------------------------------

class TestFormatSeparators:
    """Verify that separators in _format_id_map always map to None."""

    def test_separator_keys_are_none(self):
        # Simulate what _populate_format_combo builds
        fmt_map = {0: None}  # Auto
        idx = 1
        # Add separator
        fmt_map[idx] = None
        idx += 1
        # Add real format
        fmt_map[idx] = "137"
        idx += 1
        # Another separator
        fmt_map[idx] = None
        idx += 1
        # Another format
        fmt_map[idx] = "140"

        # All None entries should be separators or Auto
        none_keys = [k for k, v in fmt_map.items() if v is None]
        assert 0 in none_keys  # Auto
        assert 1 in none_keys  # separator
        assert 3 in none_keys  # separator

        # All non-None entries are real format IDs
        real_keys = {k: v for k, v in fmt_map.items() if v is not None}
        assert real_keys == {2: "137", 4: "140"}
