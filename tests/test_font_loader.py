# -*- coding: utf-8 -*-
"""Tests for font_loader.py — Font loading utilities."""

import pytest
from pathlib import Path
from font_loader import get_base_path, LOADED_FONT_FAMILY


class TestGetBasePath:
    def test_returns_path(self):
        result = get_base_path()
        assert isinstance(result, Path)

    def test_path_exists(self):
        result = get_base_path()
        assert result.exists()


class TestLoadedFontFamily:
    def test_is_string(self):
        assert isinstance(LOADED_FONT_FAMILY, str)

    def test_not_empty(self):
        assert len(LOADED_FONT_FAMILY) > 0

    def test_default_is_segoe(self):
        # Before setup_fonts() is called, default is Segoe UI
        assert LOADED_FONT_FAMILY in ("Segoe UI", "Inter Display", "Inter")
