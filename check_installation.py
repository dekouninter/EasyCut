# -*- coding: utf-8 -*-
"""
EasyCut Installation Verification Script

Professional installation checker for EasyCut application.
Verifies all dependencies and project structure.

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
License: MIT

Usage:
    python check_installation.py
"""

import sys
import subprocess
from pathlib import Path

print("\n" + "="*60)
print("  EasyCut - Installation Verification Tool")
print("="*60 + "\n")

# Check Python installation
print("[1] Checking Python installation...")
try:
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"    ✓ Python {python_version}")
    
    if sys.version_info < (3, 8):
        print("    ✗ Minimum required version is Python 3.8")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

# Check yt-dlp installation
print("\n[2] Checking yt-dlp installation...")
try:
    import yt_dlp
    print(f"    ✓ yt-dlp installed")
except ImportError:
    print("    ✗ yt-dlp not installed")
    print("    Execute: pip install -r requirements.txt")

# Check keyring installation
print("\n[3] Checking keyring installation...")
try:
    import keyring
    print(f"    ✓ keyring installed")
except ImportError:
    print("    ✗ keyring not installed")
    print("    Execute: pip install -r requirements.txt")

# Check OAuth dependencies
print("\n[4] Checking OAuth dependencies...")
missing_oauth = []
try:
    import google_auth_oauthlib
    print(f"    ✓ google-auth-oauthlib installed")
except ImportError:
    print("    ✗ google-auth-oauthlib not installed")
    missing_oauth.append("google-auth-oauthlib")

try:
    import google.auth.transport.requests
    print(f"    ✓ google-auth-httplib2 installed")
except ImportError:
    print("    ✗ google-auth-httplib2 not installed")
    missing_oauth.append("google-auth-httplib2")

try:
    import requests
    print(f"    ✓ requests installed")
except ImportError:
    print("    ✗ requests not installed")
    missing_oauth.append("requests")

if missing_oauth:
    print(f"    Install missing: pip install {' '.join(missing_oauth)}")

# Check Tkinter installation
print("\n[5] Checking Tkinter installation...")
try:
    import tkinter
    print(f"    ✓ Tkinter available")
except ImportError:
    print("    ✗ Tkinter not found")
    print("    Execute: pip install tk")

# Check FFmpeg installation
print("\n[6] Checking FFmpeg installation...")
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.decode().split('\n')[0]
        print(f"    ✓ FFmpeg found")
        print(f"      {version_line}")
    else:
        print("    ✗ FFmpeg found but with error")
except FileNotFoundError:
    print("    ✗ FFmpeg not installed")
    print("    Install FFmpeg from: https://ffmpeg.org/download.html")
except subprocess.TimeoutExpired:
    print("    ✗ FFmpeg timeout")
except Exception as e:
    print(f"    ✗ Error: {e}")

# Check folder structure
print("\n[7] Checking folder structure...")
required_dirs = ['src', 'config', 'downloads']
for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"    ✓ {dir_name}/")
    else:
        print(f"    ✗ {dir_name}/ (will be created on first run)")

# Check main files
print("\n[8] Checking main files...")
required_files = [
    'src/easycut.py',
    'src/oauth_manager.py',
    'src/i18n.py',
    'src/ui_enhanced.py',
    'src/donation_system.py',
    'requirements.txt',
    'README.md',
    'BUILD.md'
]

all_exist = True
for file_name in required_files:
    file_path = Path(file_name)
    if file_path.exists():
        print(f"    ✓ {file_name}")
    else:
        print(f"    ✗ {file_name}")
        all_exist = False

print("\n" + "="*60)
if all_exist:
    print("  ✓ Installation verified successfully!")
    print("  Ready to launch: python src/easycut.py")
else:
    print("  ✗ Some files are missing")
    print("  Please verify your installation")
print("="*60 + "\n")
