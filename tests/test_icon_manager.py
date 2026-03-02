# -*- coding: utf-8 -*-
"""Tests for icon_manager.py — Icon loading and theme management."""

import pytest
from pathlib import Path
from icon_manager import IconManager, set_icon_theme, ICON_MAP


class TestIconMap:
    def test_is_dict(self):
        assert isinstance(ICON_MAP, dict)

    def test_not_empty(self):
        assert len(ICON_MAP) > 0

    def test_all_values_are_strings(self):
        for key, value in ICON_MAP.items():
            assert isinstance(value, str), f"ICON_MAP['{key}'] is {type(value)}"

    def test_all_keys_are_strings(self):
        for key in ICON_MAP:
            assert isinstance(key, str)

    def test_essential_icons_exist(self):
        essential = ["download", "play", "stop", "folder", "video", "audio"]
        for icon in essential:
            assert icon in ICON_MAP, f"Icon '{icon}' missing from ICON_MAP"


class TestSetIconTheme:
    def test_set_dark_mode(self):
        set_icon_theme(True)
        from icon_manager import _current_dark_mode
        assert _current_dark_mode is True

    def test_set_light_mode(self):
        set_icon_theme(False)
        from icon_manager import _current_dark_mode
        assert _current_dark_mode is False


class TestIconManagerInit:
    def test_creates_instance(self):
        im = IconManager()
        assert im is not None

    def test_assets_dir_is_path(self):
        im = IconManager()
        assert isinstance(im.assets_dir, Path)

    def test_feather_dir_is_path(self):
        im = IconManager()
        assert isinstance(im.feather_dir, Path)
