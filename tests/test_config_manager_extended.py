# -*- coding: utf-8 -*-
"""Tests for configuration manager (ui_enhanced.py ConfigManager).

Covers get/set/save/load/reset, history management, channel defaults,
and archive tracking.
"""

import json
from pathlib import Path

import pytest

from ui_enhanced import ConfigManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cm(tmp_path):
    """ConfigManager backed by a temporary directory."""
    config_dir = str(tmp_path / "config")
    mgr = ConfigManager(config_dir=config_dir)
    return mgr


@pytest.fixture
def cm_with_history(cm):
    """ConfigManager with some pre-seeded history."""
    entries = [
        {"date": "2025-01-01", "filename": "Video A", "status": "success", "url": "https://youtube.com/watch?v=aaa"},
        {"date": "2025-01-02", "filename": "Video B", "status": "error", "url": "https://youtube.com/watch?v=bbb"},
        {"date": "2025-01-03", "filename": "Video C", "status": "success", "url": "https://youtube.com/watch?v=ccc"},
    ]
    cm.save_history(entries)
    return cm


# ---------------------------------------------------------------------------
# Basic get/set/save/load
# ---------------------------------------------------------------------------

class TestConfigManagerBasics:
    def test_get_default(self, cm):
        assert cm.get("nonexistent", "fallback") == "fallback"

    def test_set_and_get(self, cm):
        cm.set("my_key", "my_value")
        assert cm.get("my_key") == "my_value"

    def test_set_overwrites(self, cm):
        cm.set("key", "first")
        cm.set("key", "second")
        assert cm.get("key") == "second"

    def test_save_and_load(self, cm):
        cm.set("output_dir", "/tmp/downloads")
        cm.set("dark_mode", True)
        # save() requires a config dict; set() already calls save() internally
        # So we just verify persistence via a new instance
        cm2 = ConfigManager(config_dir=str(cm.config_dir))
        loaded = cm2.load()
        assert loaded.get("output_dir") == "/tmp/downloads"
        assert loaded.get("dark_mode") is True


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

class TestHistoryManagement:
    def test_load_empty_history(self, cm):
        history = cm.load_history()
        assert history == []

    def test_add_to_history(self, cm):
        entry = {"date": "2025-06-01", "filename": "test.mp4", "status": "success", "url": "https://youtube.com/watch?v=xxx"}
        cm.add_to_history(entry)
        history = cm.load_history()
        assert len(history) == 1
        assert history[0]["filename"] == "test.mp4"

    def test_history_limit(self, cm):
        # Add more than 100 entries
        for i in range(110):
            cm.add_to_history({"date": f"2025-01-{i:03d}", "filename": f"vid_{i}", "status": "success", "url": f"https://youtube.com/watch?v={i}"})
        history = cm.load_history()
        assert len(history) <= 100

    def test_save_and_load_history(self, cm_with_history):
        history = cm_with_history.load_history()
        assert len(history) == 3
        assert history[0]["filename"] == "Video A"

    def test_clear_history(self, cm_with_history):
        cm_with_history.save_history([])
        assert cm_with_history.load_history() == []


# ---------------------------------------------------------------------------
# Reset to defaults
# ---------------------------------------------------------------------------

class TestResetDefaults:
    def test_reset_clears_custom_values(self, cm):
        cm.set("proxy", "http://myproxy:8080")
        cm.set("rate_limit", "5M")
        cm.reset_to_defaults()
        # After reset, custom values should be gone
        # reset_to_defaults calls save() which updates the cache
        assert cm.get("proxy") is None
        assert cm.get("rate_limit") is None


# ---------------------------------------------------------------------------
# Config persistence edge cases
# ---------------------------------------------------------------------------

class TestConfigEdgeCases:
    def test_corrupt_config_file(self, cm):
        """Loading a corrupt JSON config file should not crash."""
        config_path = Path(cm.config_dir) / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("NOT VALID JSON {{{", encoding="utf-8")
        cm._cache = None  # Force re-read from disk
        loaded = cm.load()
        assert isinstance(loaded, dict)

    def test_missing_config_dir_created(self, tmp_path):
        """ConfigManager should create the config directory if missing."""
        new_dir = str(tmp_path / "new_config")
        cm = ConfigManager(config_dir=new_dir)
        assert Path(new_dir).exists()

    def test_bool_values(self, cm):
        cm.set("premiere_compat", True)
        assert cm.get("premiere_compat") is True
        cm.set("premiere_compat", False)
        assert cm.get("premiere_compat") is False

    def test_int_values(self, cm):
        cm.set("max_retries", 5)
        assert cm.get("max_retries") == 5

    def test_nested_dict_value(self, cm):
        cm.set("channel_defaults", {"TechChannel": "1080"})
        result = cm.get("channel_defaults")
        assert result == {"TechChannel": "1080"}
