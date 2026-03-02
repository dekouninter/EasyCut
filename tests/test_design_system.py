# -*- coding: utf-8 -*-
"""Tests for design_system.py — Design tokens, colors, typography, animations."""

import re
import pytest
from design_system import (
    ColorPalette, Typography, Spacing, Icons, Elevation,
    Animation, DesignTokens, ModernTheme, Shadows
)


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class TestColorPalette:
    def test_dark_is_dict(self):
        assert isinstance(ColorPalette.DARK, dict)

    def test_light_is_dict(self):
        assert isinstance(ColorPalette.LIGHT, dict)

    def test_dark_not_empty(self):
        assert len(ColorPalette.DARK) > 50

    def test_light_not_empty(self):
        assert len(ColorPalette.LIGHT) > 50

    def test_dark_and_light_same_keys(self):
        assert set(ColorPalette.DARK.keys()) == set(ColorPalette.LIGHT.keys())

    def test_all_dark_values_are_valid_colors(self):
        for key, value in ColorPalette.DARK.items():
            if isinstance(value, str):
                assert HEX_COLOR_RE.match(value), \
                    f"DARK['{key}'] = {value!r} not valid hex"
            elif isinstance(value, tuple):
                for v in value:
                    assert HEX_COLOR_RE.match(v), \
                        f"DARK['{key}'] tuple has invalid hex: {v!r}"

    def test_all_light_values_are_valid_colors(self):
        for key, value in ColorPalette.LIGHT.items():
            if isinstance(value, str):
                assert HEX_COLOR_RE.match(value), \
                    f"LIGHT['{key}'] = {value!r} not valid hex"
            elif isinstance(value, tuple):
                for v in value:
                    assert HEX_COLOR_RE.match(v), \
                        f"LIGHT['{key}'] tuple has invalid hex: {v!r}"

    def test_essential_color_keys_exist(self):
        essential = [
            "bg_primary", "bg_secondary", "fg_primary", "fg_secondary",
            "border_subtle", "accent_primary", "error", "success", "warning",
        ]
        for key in essential:
            assert key in ColorPalette.DARK, f"'{key}' missing from DARK"
            assert key in ColorPalette.LIGHT, f"'{key}' missing from LIGHT"


class TestTypography:
    def test_font_family_is_string(self):
        assert isinstance(Typography.FONT_FAMILY, str)

    def test_font_mono_is_string(self):
        assert isinstance(Typography.FONT_MONO, str)

    def test_size_hierarchy(self):
        assert Typography.SIZE_DISPLAY > Typography.SIZE_HERO
        assert Typography.SIZE_HERO > Typography.SIZE_H1
        assert Typography.SIZE_H1 >= Typography.SIZE_H2
        assert Typography.SIZE_H2 >= Typography.SIZE_H3
        assert Typography.SIZE_BODY > Typography.SIZE_SM
        assert Typography.SIZE_SM >= Typography.SIZE_TINY

    def test_sizes_are_positive_integers(self):
        for attr in ["SIZE_DISPLAY", "SIZE_HERO", "SIZE_H1", "SIZE_H2",
                      "SIZE_H3", "SIZE_BODY", "SIZE_MD", "SIZE_SM", "SIZE_TINY"]:
            val = getattr(Typography, attr)
            assert isinstance(val, int) and val > 0, f"{attr} = {val}"


class TestSpacing:
    def test_base_positive_integer(self):
        assert isinstance(Spacing.BASE, int) and Spacing.BASE > 0

    def test_spacing_hierarchy(self):
        assert Spacing.XXXS <= Spacing.XXS <= Spacing.XS <= Spacing.SM
        assert Spacing.SM <= Spacing.MD <= Spacing.LG <= Spacing.XL
        assert Spacing.XL <= Spacing.XXL <= Spacing.XXXL

    def test_radius_values(self):
        assert hasattr(Spacing, "RADIUS_SM")
        assert hasattr(Spacing, "RADIUS_MD")
        assert hasattr(Spacing, "RADIUS_LG")
        assert Spacing.RADIUS_SM <= Spacing.RADIUS_MD <= Spacing.RADIUS_LG


class TestIcons:
    def test_size_hierarchy(self):
        assert Icons.SIZE_XS < Icons.SIZE_SM < Icons.SIZE_MD
        assert Icons.SIZE_MD < Icons.SIZE_LG


class TestElevation:
    def test_levels_exist(self):
        for attr in ["NONE", "LOW", "MID", "HIGH", "TOP"]:
            assert hasattr(Elevation, attr)


class TestAnimation:
    def test_ease_out_cubic_boundaries(self):
        assert Animation.ease_out_cubic(0) == pytest.approx(0.0, abs=0.01)
        assert Animation.ease_out_cubic(1) == pytest.approx(1.0, abs=0.01)

    def test_ease_out_cubic_midpoint(self):
        mid = Animation.ease_out_cubic(0.5)
        assert 0.5 < mid < 1.0  # Should be decelerating

    def test_ease_in_out_cubic_boundaries(self):
        assert Animation.ease_in_out_cubic(0) == pytest.approx(0.0, abs=0.01)
        assert Animation.ease_in_out_cubic(1) == pytest.approx(1.0, abs=0.01)

    def test_ease_in_out_cubic_midpoint(self):
        mid = Animation.ease_in_out_cubic(0.5)
        assert 0.3 < mid < 0.7

    def test_ease_out_quart_boundaries(self):
        assert Animation.ease_out_quart(0) == pytest.approx(0.0, abs=0.01)
        assert Animation.ease_out_quart(1) == pytest.approx(1.0, abs=0.01)

    def test_ease_in_quad_boundaries(self):
        assert Animation.ease_in_quad(0) == pytest.approx(0.0, abs=0.01)
        assert Animation.ease_in_quad(1) == pytest.approx(1.0, abs=0.01)

    def test_ease_out_expo_boundaries(self):
        assert Animation.ease_out_expo(0) == pytest.approx(0.0, abs=0.01)
        assert Animation.ease_out_expo(1) == pytest.approx(1.0, abs=0.01)

    def test_spring_boundaries(self):
        assert Animation.spring(0) == pytest.approx(0.0, abs=0.05)
        assert Animation.spring(1) == pytest.approx(1.0, abs=0.05)

    def test_interpolate_color_black_to_white_midpoint(self):
        result = Animation.interpolate_color("#000000", "#ffffff", 0.5)
        assert HEX_COLOR_RE.match(result)
        # Should be around #7f7f7f or #808080
        r = int(result[1:3], 16)
        assert 120 < r < 135, f"Red channel {r} unexpected for midpoint"

    def test_interpolate_color_at_zero(self):
        result = Animation.interpolate_color("#ff0000", "#0000ff", 0.0)
        assert result.lower() == "#ff0000"

    def test_interpolate_color_at_one(self):
        result = Animation.interpolate_color("#ff0000", "#0000ff", 1.0)
        assert result.lower() == "#0000ff"

    def test_interpolate_color_same_colors(self):
        result = Animation.interpolate_color("#abcdef", "#abcdef", 0.5)
        assert result.lower() == "#abcdef"

    def test_interpolate_value_midpoint(self):
        assert Animation.interpolate_value(0, 100, 0.5) == pytest.approx(50.0)

    def test_interpolate_value_at_zero(self):
        assert Animation.interpolate_value(10, 90, 0.0) == pytest.approx(10.0)

    def test_interpolate_value_at_one(self):
        assert Animation.interpolate_value(10, 90, 1.0) == pytest.approx(90.0)

    def test_timing_constants(self):
        assert Animation.INSTANT < Animation.FAST < Animation.NORMAL
        assert Animation.NORMAL < Animation.SMOOTH < Animation.SLOW

    def test_fps_constants(self):
        # FPS_* values are frame intervals in milliseconds, not literal FPS
        assert Animation.FPS_60 == 16  # ~1000/60
        assert Animation.FPS_30 == 33  # ~1000/30
        assert Animation.FRAME_MS > 0


class TestDesignTokens:
    def test_dark_mode_init(self):
        dt = DesignTokens(dark_mode=True)
        assert dt.dark_mode is True

    def test_light_mode_init(self):
        dt = DesignTokens(dark_mode=False)
        assert dt.dark_mode is False

    def test_get_color_returns_hex(self):
        dt = DesignTokens(dark_mode=True)
        bg = dt.get_color("bg_primary")
        assert isinstance(bg, str)
        assert HEX_COLOR_RE.match(bg), f"'{bg}' is not valid hex"

    def test_get_color_gradient_returns_first(self):
        """For gradient keys, get_color returns the first color."""
        dt = DesignTokens(dark_mode=True)
        # Find a gradient key
        for key, value in ColorPalette.DARK.items():
            if isinstance(value, tuple) and len(value) == 2:
                result = dt.get_color(key)
                assert HEX_COLOR_RE.match(result), \
                    f"Gradient '{key}' get_color returned '{result}'"
                break

    def test_get_gradient_for_gradient_key(self):
        dt = DesignTokens(dark_mode=True)
        for key, value in ColorPalette.DARK.items():
            if isinstance(value, tuple) and len(value) == 2:
                grad = dt.get_gradient(key)
                assert grad is not None
                assert len(grad) == 2
                break

    def test_get_gradient_for_solid_key(self):
        dt = DesignTokens(dark_mode=True)
        result = dt.get_gradient("bg_primary")
        assert result is None

    def test_toggle_mode(self):
        dt = DesignTokens(dark_mode=True)
        assert dt.dark_mode is True
        dt.toggle_mode()
        assert dt.dark_mode is False
        dt.toggle_mode()
        assert dt.dark_mode is True

    def test_get_color_changes_with_mode(self):
        dt = DesignTokens(dark_mode=True)
        dark_bg = dt.get_color("bg_primary")
        dt.toggle_mode()
        light_bg = dt.get_color("bg_primary")
        assert dark_bg != light_bg

    def test_font_method(self):
        dt = DesignTokens(dark_mode=True)
        result = dt.font(12, "bold")
        assert isinstance(result, tuple)
        assert len(result) >= 2

    def test_get_font_config(self):
        result = DesignTokens.get_font_config(14, "normal")
        assert isinstance(result, dict)
        assert "family" in result
        assert "size" in result


class TestModernTheme:
    def test_init_dark(self):
        mt = ModernTheme(dark_mode=True)
        assert mt.dark_mode is True

    def test_init_light(self):
        mt = ModernTheme(dark_mode=False)
        assert mt.dark_mode is False

    def test_toggle(self):
        mt = ModernTheme(dark_mode=True)
        mt.toggle()
        assert mt.dark_mode is False

    def test_get_ttk_style_config(self):
        mt = ModernTheme(dark_mode=True)
        config = mt.get_ttk_style_config()
        assert isinstance(config, dict)
        assert len(config) > 0


class TestShadows:
    def test_legacy_shadow_levels(self):
        assert hasattr(Shadows, "NONE")
        assert hasattr(Shadows, "SM")
        assert hasattr(Shadows, "MD")
        assert hasattr(Shadows, "LG")
