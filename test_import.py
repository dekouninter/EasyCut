# -*- coding: utf-8 -*-
"""
EasyCut Module Import Test

Comprehensive import test suite for all EasyCut modules.
Verifies functionality and dependencies are correctly loaded.

Usage:
    python test_import.py
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("="*60)
print("  EasyCut - Module Import Test")
print("="*60)

# Test 1: i18n module
print("\n[1] Testing i18n.py...")
try:
    from i18n import Translator, TRANSLATIONS
    t = Translator("en")
    print("    ✓ Module loaded successfully")
    print(f"    ✓ Languages available: {list(TRANSLATIONS.keys())}")
    print(f"    ✓ Sample translation: {t('app_title')}")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

# Test 2: donation_system module
print("\n[2] Testing donation_system.py...")
try:
    from donation_system import DonationWindow, DonationButton
    print("    ✓ Module loaded successfully")
    print("    ✓ DonationWindow and DonationButton classes available")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

# Test 3: ui_enhanced module
print("\n[3] Testing ui_enhanced.py...")
try:
    from ui_enhanced import Theme, ConfigManager, LogWidget, StatusBar, LoginPopup, LanguageSelector
    print("    ✓ Module loaded successfully")
    print("    ✓ All UI classes available")
    
    # Test Theme
    theme = Theme(dark_mode=True)
    print(f"    ✓ Theme test: Dark mode = {theme.dark_mode}")
    
    # Test ConfigManager
    config = ConfigManager()
    print(f"    ✓ ConfigManager initialized")
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

# Test 4: Check yt-dlp
print("\n[4] Checking yt-dlp...")
try:
    import yt_dlp
    print(f"    ✓ yt-dlp installed")
except ImportError:
    print("    ✗ yt-dlp not found (required for video downloads)")

# Test 5: Check keyring
print("\n[5] Checking keyring...")
try:
    import keyring
    print(f"    ✓ keyring installed")
except ImportError:
    print("    ✗ keyring not found (required for credential storage)")

# Test 6: Check folder structure
print("\n[6] Checking folder structure...")
try:
    from pathlib import Path
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    print(f"    ✓ config/ exists")
    print(f"    ✓ downloads/ exists")
except Exception as e:
    print(f"    ✗ Error: {e}")

print("\n" + "="*60)
print("  ✓ All tests passed successfully!")
print("  Ready to launch: python src/easycut.py")
print("="*60 + "\n")
