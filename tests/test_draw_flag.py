# -*- coding: utf-8 -*-
"""Tests for _draw_flag static method — PIL flag generation.

Validates every supported language code produces correctly sized RGBA
images, and that unknown codes still produce a valid image.
"""

import sys
import types
from unittest.mock import MagicMock

import pytest

# Stub yt_dlp before importing easycut
fake_ytdlp = types.ModuleType("yt_dlp")
fake_ytdlp.YoutubeDL = MagicMock
sys.modules.setdefault("yt_dlp", fake_ytdlp)

from easycut import EasyCutApp

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

pytestmark = pytest.mark.skipif(not HAS_PIL, reason="Pillow not installed")

KNOWN_CODES = ["en", "pt", "es", "fr", "de", "it", "ja"]


class TestDrawFlag:
    """Tests for the _draw_flag static method."""

    @pytest.mark.parametrize("code", KNOWN_CODES)
    def test_known_code_returns_image(self, code):
        img = EasyCutApp._draw_flag(code)
        assert isinstance(img, Image.Image)

    @pytest.mark.parametrize("code", KNOWN_CODES)
    def test_known_code_default_size(self, code):
        img = EasyCutApp._draw_flag(code)
        w, h = img.size
        assert w == 24
        assert h == int(24 * 0.67)  # 16

    @pytest.mark.parametrize("code", KNOWN_CODES)
    def test_known_code_rgba_mode(self, code):
        img = EasyCutApp._draw_flag(code)
        assert img.mode == "RGBA"

    def test_unknown_code_returns_image(self):
        img = EasyCutApp._draw_flag("xx")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"

    def test_custom_size(self):
        img = EasyCutApp._draw_flag("en", size=48)
        w, h = img.size
        assert w == 48
        assert h == int(48 * 0.67)  # 32

    def test_small_size(self):
        img = EasyCutApp._draw_flag("en", size=8)
        w, h = img.size
        assert w == 8
        assert h == int(8 * 0.67)

    def test_flag_has_border_pixels(self):
        """Every flag has a thin border drawn at the edges."""
        img = EasyCutApp._draw_flag("ja")
        # Top-left corner pixel should not be fully transparent
        # (border is drawn with #555555)
        pixel = img.getpixel((0, 0))
        assert pixel[3] > 0  # alpha > 0

    def test_multiple_calls_distinct_objects(self):
        """Each call should return a unique image object."""
        a = EasyCutApp._draw_flag("en")
        b = EasyCutApp._draw_flag("en")
        assert a is not b
