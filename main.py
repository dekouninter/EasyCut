#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Professional YouTube Video Downloader
Main Entry Point

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
License: GPL-3.0
"""

import sys
import tkinter as tk
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from easycut import EasyCutApp


def main():
    """Main entry point for EasyCut application"""
    root = tk.Tk()
    
    # Set window icon BEFORE creating the app
    try:
        icon_path = Path(__file__).parent / "assets" / "app_icon.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))
    except Exception as e:
        print(f"Warning: Could not set window icon: {e}")
    
    app = EasyCutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
