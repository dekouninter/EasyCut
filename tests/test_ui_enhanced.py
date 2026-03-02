# -*- coding: utf-8 -*-
"""Tests for ui_enhanced.py — LogWidget constants."""

import pytest
from ui_enhanced import LogWidget


class TestLogWidgetLevelConfig:
    def test_is_dict(self):
        assert isinstance(LogWidget.LEVEL_CONFIG, dict)

    def test_expected_levels(self):
        expected = ["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG"]
        for level in expected:
            assert level in LogWidget.LEVEL_CONFIG, \
                f"Level '{level}' missing from LEVEL_CONFIG"

    def test_each_level_has_tuple(self):
        for level, config in LogWidget.LEVEL_CONFIG.items():
            assert isinstance(config, tuple), \
                f"LEVEL_CONFIG['{level}'] is {type(config).__name__}"

    def test_each_level_has_color_and_symbol(self):
        for level, config in LogWidget.LEVEL_CONFIG.items():
            assert len(config) == 2, \
                f"LEVEL_CONFIG['{level}'] should have 2 elements"
            color_token, symbol = config
            assert isinstance(color_token, str)
            assert isinstance(symbol, str)
            assert len(symbol) > 0, f"'{level}' symbol is empty"

    def test_no_extra_levels(self):
        """Only expected levels should be present."""
        expected = {"INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG"}
        actual = set(LogWidget.LEVEL_CONFIG.keys())
        extra = actual - expected
        assert not extra, f"Unexpected levels: {extra}"
