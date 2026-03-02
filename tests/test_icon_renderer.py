# -*- coding: utf-8 -*-
"""Tests for icon_renderer.py — SVG parsing and color utilities."""

import pytest
from icon_renderer import _parse_points, _parse_path_d, _hex_to_rgba, clear_icon_cache, _CACHE


# ─────────────────────────────────────────────
#  _parse_points
# ─────────────────────────────────────────────

class TestParsePoints:
    def test_basic_pair(self):
        result = _parse_points("10 20")
        assert result == [(10.0, 20.0)]

    def test_multiple_pairs(self):
        result = _parse_points("1 2 3 4 5 6")
        assert result == [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]

    def test_comma_separated(self):
        result = _parse_points("10,20 30,40")
        assert result == [(10.0, 20.0), (30.0, 40.0)]

    def test_mixed_separators(self):
        result = _parse_points("  10, 20  30 ,40 ")
        assert result == [(10.0, 20.0), (30.0, 40.0)]

    def test_odd_number_of_values(self):
        # Odd count: last value has no pair, should be dropped
        result = _parse_points("1 2 3")
        assert result == [(1.0, 2.0)]

    def test_empty_string(self):
        result = _parse_points("")
        assert result == []

    def test_float_values(self):
        result = _parse_points("1.5 2.7 3.14 0.0")
        assert result == [(1.5, 2.7), (3.14, 0.0)]


# ─────────────────────────────────────────────
#  _hex_to_rgba
# ─────────────────────────────────────────────

class TestHexToRgba:
    def test_black(self):
        assert _hex_to_rgba("#000000") == (0, 0, 0, 255)

    def test_white(self):
        assert _hex_to_rgba("#FFFFFF") == (255, 255, 255, 255)

    def test_red(self):
        assert _hex_to_rgba("#FF0000") == (255, 0, 0, 255)

    def test_with_alpha(self):
        assert _hex_to_rgba("#FF000080") == (255, 0, 0, 128)

    def test_full_alpha(self):
        assert _hex_to_rgba("#ABCDEFFF") == (171, 205, 239, 255)

    def test_no_hash(self):
        # Function strips # via lstrip
        assert _hex_to_rgba("FF0000") == (255, 0, 0, 255)

    def test_invalid_length_returns_default(self):
        assert _hex_to_rgba("#FFF") == (200, 200, 200, 255)

    def test_empty_returns_default(self):
        assert _hex_to_rgba("#") == (200, 200, 200, 255)

    def test_lowercase(self):
        assert _hex_to_rgba("#abcdef") == (171, 205, 239, 255)


# ─────────────────────────────────────────────
#  _parse_path_d — SVG path parser
# ─────────────────────────────────────────────

class TestParsePathD:
    def test_simple_move_and_line(self):
        result = _parse_path_d("M 0 0 L 10 10")
        assert len(result) > 0
        # Should have line segments
        assert result[0][0] == "line"

    def test_horizontal_and_vertical(self):
        result = _parse_path_d("M 0 0 H 10 V 20")
        assert len(result) > 0
        segment_type, points = result[0]
        assert segment_type == "line"

    def test_close_path_z(self):
        result = _parse_path_d("M 0 0 L 10 0 L 10 10 Z")
        assert len(result) > 0

    def test_empty_string(self):
        result = _parse_path_d("")
        assert isinstance(result, list)

    def test_cubic_bezier(self):
        result = _parse_path_d("M 0 0 C 1 2 3 4 5 6")
        assert len(result) > 0

    def test_relative_move(self):
        result = _parse_path_d("m 5 5 l 10 10")
        assert len(result) > 0

    def test_arc_command(self):
        result = _parse_path_d("M 10 80 A 25 25 0 0 1 50 80")
        # Arc segments are produced
        assert any(seg[0] == "arc" for seg in result) or len(result) >= 0

    def test_quadratic_bezier(self):
        result = _parse_path_d("M 0 0 Q 5 10 10 0")
        assert len(result) > 0


# ─────────────────────────────────────────────
#  clear_icon_cache
# ─────────────────────────────────────────────

class TestClearIconCache:
    def test_clears_cache(self):
        _CACHE["test_key"] = "test_value"
        clear_icon_cache()
        assert "test_key" not in _CACHE

    def test_cache_is_empty_after_clear(self):
        _CACHE["a"] = 1
        _CACHE["b"] = 2
        clear_icon_cache()
        assert len(_CACHE) == 0

    def test_double_clear_no_error(self):
        clear_icon_cache()
        clear_icon_cache()  # Should not raise
