# -*- coding: utf-8 -*-
"""Additional edge-case tests for design_system.py."""

import pytest
from design_system import (
    Animation, DesignTokens, ModernTheme, Elevation, ColorPalette
)

# Import Shadows from the backward-compat alias
try:
    from design_system import Shadows
except ImportError:
    Shadows = None


# ─────────────────────────────────────────────
#  Animation — clamp behavior
# ─────────────────────────────────────────────

class TestAnimationClamp:
    def test_interpolate_color_negative_t(self):
        """t < 0 should clamp to start color."""
        result = Animation.interpolate_color("#000000", "#FFFFFF", -0.5)
        assert result.lower() == "#000000"

    def test_interpolate_color_over_one(self):
        """t > 1 should clamp to end color."""
        result = Animation.interpolate_color("#000000", "#FFFFFF", 1.5)
        assert result.lower() == "#ffffff"

    def test_interpolate_value_negative_t(self):
        result = Animation.interpolate_value(0, 100, -0.5)
        assert result == pytest.approx(0.0)

    def test_interpolate_value_over_one(self):
        result = Animation.interpolate_value(0, 100, 1.5)
        assert result == pytest.approx(100.0)


# ─────────────────────────────────────────────
#  DesignTokens — unknown key fallback
# ─────────────────────────────────────────────

class TestDesignTokensFallback:
    def test_unknown_key_returns_black(self):
        dt = DesignTokens(dark_mode=True)
        assert dt.get_color("nonexistent_key_xyz") == "#000000"

    def test_unknown_gradient_returns_none(self):
        dt = DesignTokens(dark_mode=True)
        result = dt.get_gradient("nonexistent_key_xyz")
        assert result is None


# ─────────────────────────────────────────────
#  ModernTheme — ttk_style_config has expected keys
# ─────────────────────────────────────────────

class TestModernThemeTtkStyleConfig:
    def test_config_has_standard_widgets(self):
        mt = ModernTheme(dark_mode=True)
        config = mt.get_ttk_style_config()
        # At minimum these standard ttk widget styles should be present
        expected = ["TButton", "TEntry", "TCombobox", "TFrame", "TLabel"]
        for key in expected:
            assert key in config, f"'{key}' missing from ttk style config"

    def test_each_widget_config_has_configure(self):
        mt = ModernTheme(dark_mode=True)
        config = mt.get_ttk_style_config()
        for widget, style_data in config.items():
            if isinstance(style_data, dict):
                assert "configure" in style_data or "map" in style_data, \
                    f"'{widget}' has no 'configure' or 'map'"

    def test_light_mode_different_from_dark(self):
        dark = ModernTheme(dark_mode=True)
        light = ModernTheme(dark_mode=False)
        dark_cfg = dark.get_ttk_style_config()
        light_cfg = light.get_ttk_style_config()
        # At least one color value should differ
        assert dark_cfg != light_cfg


# ─────────────────────────────────────────────
#  Shadows ↔ Elevation backward-compat parity
# ─────────────────────────────────────────────

@pytest.mark.skipif(Shadows is None, reason="Shadows class not available")
class TestShadowsElevationParity:
    def test_none_matches(self):
        assert Shadows.NONE == Elevation.NONE

    def test_sm_matches_low(self):
        assert Shadows.SM == Elevation.LOW

    def test_md_matches_mid(self):
        assert Shadows.MD == Elevation.MID

    def test_lg_matches_high(self):
        assert Shadows.LG == Elevation.HIGH


# ─────────────────────────────────────────────
#  ColorPalette — gradient values have correct format
# ─────────────────────────────────────────────

class TestColorPaletteGradients:
    def test_dark_gradient_values_are_lists_or_strings(self):
        for key, value in ColorPalette.DARK.items():
            assert isinstance(value, (str, list, tuple)), \
                f"DARK['{key}'] is {type(value).__name__}"

    def test_light_gradient_values_are_lists_or_strings(self):
        for key, value in ColorPalette.LIGHT.items():
            assert isinstance(value, (str, list, tuple)), \
                f"LIGHT['{key}'] is {type(value).__name__}"

    def test_gradient_lists_have_two_colors(self):
        import re
        hex_re = re.compile(r'^#[0-9a-fA-F]{6,8}$')
        for palette_name, palette in [("DARK", ColorPalette.DARK), ("LIGHT", ColorPalette.LIGHT)]:
            for key, value in palette.items():
                if isinstance(value, (list, tuple)):
                    assert len(value) == 2, \
                        f"{palette_name}['{key}'] gradient has {len(value)} colors, expected 2"
                    for color in value:
                        assert hex_re.match(color), \
                            f"{palette_name}['{key}'] has invalid color '{color}'"
