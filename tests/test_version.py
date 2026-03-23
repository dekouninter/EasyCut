# -*- coding: utf-8 -*-
"""Tests for __version__.py — single source of truth for version."""

import re
from __version__ import __version__


class TestVersion:
    def test_version_is_string(self):
        assert isinstance(__version__, str)

    def test_version_not_empty(self):
        assert len(__version__) > 0

    def test_version_semver_format(self):
        assert re.match(r"^\d+\.\d+\.\d+$", __version__), \
            f"Version '{__version__}' does not match X.Y.Z format"

    def test_version_current(self):
        assert __version__ == "1.10.0"
