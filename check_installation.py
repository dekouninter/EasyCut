# -*- coding: utf-8 -*-
"""
Utility used by Quickstart/Documentation to verify that required
Python packages and external tools are present.

Run this before launching `main.py` when working from source.  It will
print missing items and a short advice to install them.

This file was accidentally removed; restoring as part of general
workspace health improvements (Feb 2026).
"""
import importlib
import shutil

REQUIRED_PKGS = [
    'yt_dlp',
    'keyring',
    'PIL',
    'google_auth_oauthlib',
    'google_auth_httplib2',
    'requests',
    'pywinstyles',
    'darkdetect',
]


def check_packages():
    missing = []
    for pkg in REQUIRED_PKGS:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    return missing


def check_executable(name):
    return shutil.which(name) is not None


def main():
    print("\nEasyCut dependency checker")
    print("==========================")
    pkgs = check_packages()
    if pkgs:
        print("\nMissing Python packages:")
        for p in pkgs:
            print(f"  - {p}")
        print("\nInstall them with:\n  pip install -r requirements.txt\n")
    else:
        print("All Python packages appear to be installed.")

    tools = ['ffmpeg', 'node']
    miss_tools = [t for t in tools if not check_executable(t)]
    if miss_tools:
        print("\nRecommended external software not found:")
        for t in miss_tools:
            print(f"  - {t}  (ffmpeg required for post-processing)")
        print("\nYou can download them from their respective websites.")
    else:
        print("All required external tools are available.")

    print("\nDone. You may now run `python main.py`.\n")


if __name__ == '__main__':
    main()
