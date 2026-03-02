# -*- coding: utf-8 -*-
"""Tests for ui_enhanced.py — ConfigManager file operations."""

import json
import pytest
from ui_enhanced import ConfigManager


class TestConfigManagerDefaults:
    def test_default_config_is_dict(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        assert isinstance(cm.default_config, dict)

    def test_default_dark_mode_true(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        assert cm.default_config["dark_mode"] is True

    def test_default_language_en(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        assert cm.default_config["language"] == "en"

    def test_default_log_level(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        assert "log_level" in cm.default_config


class TestConfigManagerLoad:
    def test_load_no_file_returns_defaults(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        config = cm.load()
        assert isinstance(config, dict)
        assert config["dark_mode"] is True

    def test_load_existing_file(self, tmp_config):
        # Write a config file first
        config_file = tmp_config / "config.json"
        config_file.write_text(json.dumps({"dark_mode": False, "language": "pt"}))
        cm = ConfigManager(config_dir=str(tmp_config))
        config = cm.load()
        assert config["dark_mode"] is False
        assert config["language"] == "pt"

    def test_load_corrupt_json_returns_defaults(self, tmp_config):
        config_file = tmp_config / "config.json"
        config_file.write_text("not valid json {{{")
        cm = ConfigManager(config_dir=str(tmp_config))
        config = cm.load()
        # Should fall back to defaults
        assert isinstance(config, dict)
        assert "dark_mode" in config


class TestConfigManagerSave:
    def test_save_creates_file(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        result = cm.save({"dark_mode": False, "language": "pt"})
        assert result is True
        assert (tmp_config / "config.json").exists()

    def test_save_then_load_roundtrip(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        original = {"dark_mode": False, "language": "es", "custom_key": "value"}
        cm.save(original)
        loaded = cm.load()
        assert loaded["dark_mode"] is False
        assert loaded["language"] == "es"
        assert loaded["custom_key"] == "value"


class TestConfigManagerGetSet:
    def test_get_existing_key(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        cm.load()
        assert cm.get("dark_mode") is True

    def test_get_missing_key_returns_none(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        cm.load()
        assert cm.get("nonexistent_key_xyz") is None

    def test_get_missing_key_with_default(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        cm.load()
        assert cm.get("nonexistent_key_xyz", "fallback") == "fallback"

    def test_set_persists(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        cm.load()
        cm.set("dark_mode", False)
        # Re-load from disk
        cm2 = ConfigManager(config_dir=str(tmp_config))
        config = cm2.load()
        assert config["dark_mode"] is False


class TestConfigManagerHistory:
    def test_load_history_no_file(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        history = cm.load_history()
        assert isinstance(history, list)
        assert len(history) == 0

    def test_save_and_load_history(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        items = [{"url": "https://youtube.com/1", "title": "Test"}]
        cm.save_history(items)
        loaded = cm.load_history()
        assert len(loaded) == 1
        assert loaded[0]["url"] == "https://youtube.com/1"

    def test_add_to_history(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        cm.add_to_history({"url": "https://youtube.com/1"})
        cm.add_to_history({"url": "https://youtube.com/2"})
        history = cm.load_history()
        assert len(history) == 2

    def test_history_cap_100(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        items = [{"url": f"https://youtube.com/{i}"} for i in range(150)]
        cm.save_history(items)
        loaded = cm.load_history()
        assert len(loaded) <= 100

    def test_reset_to_defaults(self, tmp_config):
        cm = ConfigManager(config_dir=str(tmp_config))
        cm.load()
        cm.set("dark_mode", False)
        cm.set("language", "ja")
        cm.reset_to_defaults()
        config = cm.load()
        assert config["dark_mode"] is True
        assert config["language"] == "en"
