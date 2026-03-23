# -*- coding: utf-8 -*-
"""
Professional Donation System for EasyCut
Manages donation links and support interface with professional UI

Author: Deko Costa
Repository: https://github.com/dekouninter/EasyCut
License: MIT

Features:
- Multiple donation platforms (Ko-fi, Buy Me a Coffee, Livepix)
- Branded buttons with platform colours
- Professional modal presentation
- Floating action button
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from i18n import translator as t

try:
    from font_loader import LOADED_FONT_FAMILY
except ImportError:
    LOADED_FONT_FAMILY = "Segoe UI"

try:
    from design_system import DesignTokens
except ImportError:
    DesignTokens = None


class DonationWindow:
    """Professional Donation Support Window

    Displays available donation platforms with professional UI
    and links to support the EasyCut project development.
    """

    # Platform brand colours
    _PLATFORMS = [
        {
            "key": "kofi",
            "name": "Ko-fi",
            "icon": "☕",
            "url": "https://ko-fi.com/dekocosta",
            "bg": "#FF5E5B",
            "fg": "#ffffff",
            "hover": "#e04e4b",
        },
        {
            "key": "coffee",
            "name": "Buy Me a Coffee",
            "icon": "☕",
            "url": "https://buymeacoffee.com/dekocosta",
            "bg": "#FFDD00",
            "fg": "#000000",
            "hover": "#e5c700",
        },
        {
            "key": "livepix",
            "name": "Livepix",
            "icon": "🎁",
            "url": "https://livepix.gg/dekocosta",
            "bg": "#9B59B6",
            "fg": "#ffffff",
            "hover": "#8344a0",
        },
    ]

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        # Keep legacy dict for any external code that might read it
        self.donation_links = {
            p["key"]: {"name": p["name"], "url": p["url"], "icon": p["icon"]}
            for p in self._PLATFORMS
        }

    def open_donation_window(self):
        """Display donation window with branded support options."""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title(t("donation_title"))
        self.window.geometry("480x400")
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()

        # Detect dark/light from parent background
        try:
            tokens = DesignTokens()
            win_bg    = tokens.get_color("bg_primary")
            fg_main   = tokens.get_color("fg_primary")
            fg_sub    = tokens.get_color("fg_secondary")
            header_bg = tokens.get_color("accent_primary")
        except Exception:
            win_bg    = "#1e1e2e"
            fg_main   = "#cdd6f4"
            fg_sub    = "#a6adc8"
            header_bg = "#4A90D9"

        self.window.configure(bg=win_bg)

        # ── Header canvas (solid accent bar with icon + title) ──────────────
        header = tk.Canvas(
            self.window, height=90,
            bg=header_bg, highlightthickness=0,
        )
        header.pack(fill=tk.X)
        header.create_text(
            240, 32, text="❤️  Support EasyCut",
            fill="#ffffff",
            font=(LOADED_FONT_FAMILY, 16, "bold"),
            anchor="center",
        )
        header.create_text(
            240, 62, text=t("donation_description"),
            fill="#ffffffcc",
            font=(LOADED_FONT_FAMILY, 9),
            anchor="center",
            width=440,
        )

        # ── Platform buttons ─────────────────────────────────────────────────
        buttons_frame = tk.Frame(self.window, bg=win_bg)
        buttons_frame.pack(fill=tk.X, padx=32, pady=(20, 8))

        for platform in self._PLATFORMS:
            bg_col    = platform["bg"]
            fg_col    = platform["fg"]
            hover_col = platform["hover"]

            btn = tk.Button(
                buttons_frame,
                text=f"  {platform['icon']}   {platform['name']}",
                command=lambda url=platform["url"]: self.open_link(url),
                bg=bg_col,
                fg=fg_col,
                activebackground=hover_col,
                activeforeground=fg_col,
                font=(LOADED_FONT_FAMILY, 11, "bold"),
                cursor="hand2",
                padx=20,
                pady=10,
                relief=tk.FLAT,
                bd=0,
                anchor="w",
            )
            btn.pack(fill=tk.X, pady=6)
            btn.bind("<Enter>", lambda e, b=btn, h=hover_col: b.config(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_col:    b.config(bg=c))

        # ── Footer ───────────────────────────────────────────────────────────
        tk.Label(
            self.window,
            text="Thank you for supporting EasyCut! 🙏",
            bg=win_bg, fg=fg_sub,
            font=(LOADED_FONT_FAMILY, 9, "italic"),
        ).pack(pady=(8, 16))

    def open_link(self, url: str):
        """Open donation link in the default browser."""
        try:
            webbrowser.open(url)
        except Exception as exc:
            print(f"Error opening link: {exc}")


class DonationButton:
    """Sidebar / Floating Action Button for Donations."""

    def __init__(self, parent):
        self.parent = parent
        self.button = None
        self.donation_window = DonationWindow(parent)

    def create_sidebar_button(self, parent_frame, bg: str, fg: str, accent: str, hover_bg: str):
        """Create a sidebar-style support button row.

        Returns a dict with 'button' and 'icon_label' for collapse handling.
        """
        try:
            from design_system import Spacing, Typography
        except ImportError:
            class Spacing:
                XS = 4; SM = 8
            class Typography:
                FONT_FAMILY = LOADED_FONT_FAMILY; SIZE_BODY = 10

        btn_frame = tk.Frame(parent_frame, bg=bg, cursor="hand2")
        btn_frame.pack(fill=tk.X, pady=(0, 2))
        btn_frame.pack_propagate(False)
        btn_frame.config(height=36)

        btn_frame.grid_columnconfigure(0, minsize=3)
        btn_frame.grid_columnconfigure(1, minsize=40)
        btn_frame.grid_columnconfigure(2, weight=1)

        # Indicator
        indicator = tk.Frame(btn_frame, bg=bg, width=3)
        indicator.grid(row=0, column=0, sticky="ns")

        # Icon label (always visible — shown in collapsed state)
        icon_lbl = tk.Label(
            btn_frame, text="❤", bg=bg, fg=accent,
            font=(Typography.FONT_FAMILY, 14),
            anchor="center",
        )
        icon_lbl.grid(row=0, column=1, sticky="nsew", pady=Spacing.XS)

        # Text label (hidden in collapsed state)
        text_lbl = tk.Label(
            btn_frame, text="Support Development",
            bg=bg, fg=fg,
            font=(Typography.FONT_FAMILY, Typography.SIZE_BODY),
            anchor="w",
        )
        text_lbl.grid(row=0, column=2, sticky="w", padx=(Spacing.XS, 0), pady=Spacing.XS)

        for w in (btn_frame, icon_lbl, text_lbl):
            w.bind("<Button-1>", lambda e: self.open_donation())
            w.bind("<Enter>",    lambda e: btn_frame.config(bg=hover_bg) or icon_lbl.config(bg=hover_bg) or text_lbl.config(bg=hover_bg))
            w.bind("<Leave>",    lambda e: btn_frame.config(bg=bg) or icon_lbl.config(bg=bg) or text_lbl.config(bg=bg))

        return {"button": btn_frame, "icon_label": icon_lbl, "text_label": text_lbl}

    def create_floating_button(self, root_window):
        """Legacy floating button — kept for backwards compatibility."""
        try:
            tokens = DesignTokens()
            accent = tokens.get_color("accent_primary")
            accent_hover = tokens.get_color("accent_hover")
        except Exception:
            accent = "#4A90D9"
            accent_hover = "#3A7BC8"

        floating_frame = ttk.Frame(root_window)
        floating_frame.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        self.button = tk.Button(
            floating_frame,
            text="❤️ Support Development",
            command=self.open_donation,
            bg=accent,
            fg="white",
            font=(LOADED_FONT_FAMILY, 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=6,
            relief=tk.RAISED,
            bd=2,
        )
        self.button.pack()
        self.button.bind("<Enter>", lambda e: self.button.config(bg=accent_hover))
        self.button.bind("<Leave>", lambda e: self.button.config(bg=accent))

    def open_donation(self):
        """Open donation window when button clicked."""
        self.donation_window.open_donation_window()
