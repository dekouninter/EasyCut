# -*- coding: utf-8 -*-
"""Tests for donation_system.py — DonationWindow and DonationButton.

Cover data integrity of donation_links, open_link wrapper, and
DonationButton composition.
"""

from unittest.mock import MagicMock, patch

import pytest

from donation_system import DonationWindow, DonationButton


# ---------------------------------------------------------------------------
# DonationWindow
# ---------------------------------------------------------------------------

class TestDonationWindowData:
    """Validate the donation_links data structure."""

    def test_has_coffee_platform(self):
        dw = DonationWindow(parent=MagicMock())
        assert "coffee" in dw.donation_links

    def test_has_livepix_platform(self):
        dw = DonationWindow(parent=MagicMock())
        assert "livepix" in dw.donation_links

    def test_each_link_has_required_keys(self):
        dw = DonationWindow(parent=MagicMock())
        for key, link in dw.donation_links.items():
            assert "name" in link, f"{key} missing 'name'"
            assert "url" in link, f"{key} missing 'url'"
            assert "icon" in link, f"{key} missing 'icon'"

    def test_urls_are_https(self):
        dw = DonationWindow(parent=MagicMock())
        for key, link in dw.donation_links.items():
            assert link["url"].startswith("https://"), f"{key} URL not HTTPS"

    def test_icons_are_nonempty(self):
        dw = DonationWindow(parent=MagicMock())
        for key, link in dw.donation_links.items():
            assert len(link["icon"]) > 0, f"{key} icon is empty"


class TestOpenLink:
    """Tests for open_link() wrapper."""

    def test_opens_browser(self):
        dw = DonationWindow(parent=MagicMock())
        with patch("donation_system.webbrowser.open") as mock_open:
            dw.open_link("https://example.com")
        mock_open.assert_called_once_with("https://example.com")

    def test_exception_does_not_raise(self):
        dw = DonationWindow(parent=MagicMock())
        with patch("donation_system.webbrowser.open", side_effect=Exception("fail")):
            # Should not raise
            dw.open_link("https://example.com")


# ---------------------------------------------------------------------------
# DonationButton composition
# ---------------------------------------------------------------------------

class TestDonationButton:
    def test_creates_donation_window(self):
        db = DonationButton(parent=MagicMock())
        assert isinstance(db.donation_window, DonationWindow)

    def test_donation_window_parent_set(self):
        parent = MagicMock()
        db = DonationButton(parent=parent)
        assert db.donation_window.parent is parent
