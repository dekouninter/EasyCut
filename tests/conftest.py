# -*- coding: utf-8 -*-
"""
Shared fixtures for EasyCut test suite.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

import pytest

# Ensure src/ is on the import path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


@pytest.fixture
def tmp_config(tmp_path):
    """Provide a temporary config directory with minimal structure."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def tmp_config_with_creds(tmp_config):
    """Provide a temporary config directory with dummy credentials."""
    creds = {
        "installed": {
            "client_id": "test-client-id.apps.googleusercontent.com",
            "client_secret": "test-secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    (tmp_config / "credentials.json").write_text(json.dumps(creds), encoding="utf-8")
    return tmp_config
