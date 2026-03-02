# -*- coding: utf-8 -*-
"""Tests for modern_components.py — Non-GUI constants and maps."""

import pytest
from modern_components import EMOJI_ICONS, HAS_ICON_RENDERER


class TestEmojiIcons:
    def test_is_dict(self):
        assert isinstance(EMOJI_ICONS, dict)

    def test_not_empty(self):
        assert len(EMOJI_ICONS) > 0

    def test_all_keys_are_strings(self):
        for key in EMOJI_ICONS:
            assert isinstance(key, str)

    def test_all_values_are_strings(self):
        for key, value in EMOJI_ICONS.items():
            assert isinstance(value, str), f"EMOJI_ICONS['{key}'] is {type(value).__name__}"

    def test_all_values_non_empty(self):
        for key, value in EMOJI_ICONS.items():
            assert len(value) > 0, f"EMOJI_ICONS['{key}'] is empty"

    def test_essential_icons_present(self):
        essential = [
            "download", "play", "stop", "pause", "settings",
            "folder", "search", "check", "delete", "edit",
            "theme_dark", "theme_light", "language", "video", "music",
        ]
        for icon in essential:
            assert icon in EMOJI_ICONS, f"'{icon}' missing from EMOJI_ICONS"

    def test_nav_icons_present(self):
        """Icons used for navigation tabs."""
        nav = ["live", "following", "history", "about", "batch"]
        for icon in nav:
            assert icon in EMOJI_ICONS, f"Nav icon '{icon}' missing"

    def test_no_duplicate_keys(self):
        # Dicts naturally prevent duplicates, but verify count
        keys = list(EMOJI_ICONS.keys())
        assert len(keys) == len(set(keys))


class TestHasIconRenderer:
    def test_is_bool(self):
        assert isinstance(HAS_ICON_RENDERER, bool)

    def test_true_when_pillow_installed(self):
        """In our venv, Pillow is installed so this should be True."""
        try:
            from PIL import Image
            assert HAS_ICON_RENDERER is True
        except ImportError:
            # If Pillow is not available, it should be False
            assert HAS_ICON_RENDERER is False
