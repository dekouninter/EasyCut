# -*- coding: utf-8 -*-
"""Tests for channel_monitor.py — Channel monitoring system."""

import json
import pytest
from pathlib import Path
from channel_monitor import ChannelMonitor


class TestChannelMonitorInit:
    def test_init_creates_instance(self, tmp_path):
        cm = ChannelMonitor(
            config_dir=str(tmp_path / "config"),
            output_dir=str(tmp_path / "downloads")
        )
        assert cm is not None

    def test_empty_channels_list(self, tmp_path):
        cm = ChannelMonitor(
            config_dir=str(tmp_path / "config"),
            output_dir=str(tmp_path / "downloads")
        )
        assert cm.get_channels() == []


class TestNormalizeChannelUrl:
    def test_handle_url(self, tmp_path):
        cm = ChannelMonitor(config_dir=str(tmp_path / "config"), output_dir=str(tmp_path / "dl"))
        result = cm._normalize_channel_url("https://www.youtube.com/@mkbhd")
        assert result is not None
        assert "youtube.com" in result

    def test_channel_id_url(self, tmp_path):
        cm = ChannelMonitor(config_dir=str(tmp_path / "config"), output_dir=str(tmp_path / "dl"))
        result = cm._normalize_channel_url("https://youtube.com/channel/UC123abc")
        assert result is not None

    def test_bare_handle(self, tmp_path):
        cm = ChannelMonitor(config_dir=str(tmp_path / "config"), output_dir=str(tmp_path / "dl"))
        result = cm._normalize_channel_url("@mkbhd")
        assert result is not None
        assert "youtube.com" in result

    def test_empty_string(self, tmp_path):
        cm = ChannelMonitor(config_dir=str(tmp_path / "config"), output_dir=str(tmp_path / "dl"))
        result = cm._normalize_channel_url("")
        assert result is None

    def test_non_youtube_url(self, tmp_path):
        cm = ChannelMonitor(config_dir=str(tmp_path / "config"), output_dir=str(tmp_path / "dl"))
        result = cm._normalize_channel_url("https://twitch.tv/something")
        assert result is None


class TestChannelMonitorSettings:
    def _make_monitor(self, tmp_path):
        return ChannelMonitor(
            config_dir=str(tmp_path / "config"),
            output_dir=str(tmp_path / "downloads")
        )

    def test_interval_default(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        interval = cm.get_interval()
        assert 15 <= interval <= 1440

    def test_set_interval_normal(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        cm.set_interval(60)
        assert cm.get_interval() == 60

    def test_set_interval_too_low(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        cm.set_interval(5)
        assert cm.get_interval() >= 15

    def test_set_interval_too_high(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        cm.set_interval(5000)
        assert cm.get_interval() <= 1440

    def test_notifications_toggle(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        cm.set_notifications(False)
        assert cm.get_notifications() is False
        cm.set_notifications(True)
        assert cm.get_notifications() is True

    def test_auto_download_toggle(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        cm.set_auto_download(True)
        assert cm.get_auto_download() is True
        cm.set_auto_download(False)
        assert cm.get_auto_download() is False

    def test_auto_quality(self, tmp_path):
        cm = self._make_monitor(tmp_path)
        cm.set_auto_quality("720")
        assert cm.get_auto_quality() == "720"


class TestChannelMonitorRemoveChannel:
    def test_remove_nonexistent(self, tmp_path):
        cm = ChannelMonitor(
            config_dir=str(tmp_path / "config"),
            output_dir=str(tmp_path / "downloads")
        )
        result = cm.remove_channel("https://youtube.com/@nonexistent")
        assert result is False


class TestChannelMonitorRunning:
    def test_not_running_initially(self, tmp_path):
        cm = ChannelMonitor(
            config_dir=str(tmp_path / "config"),
            output_dir=str(tmp_path / "downloads")
        )
        assert cm.is_running is False

    def test_set_callbacks(self, tmp_path):
        cm = ChannelMonitor(
            config_dir=str(tmp_path / "config"),
            output_dir=str(tmp_path / "downloads")
        )
        # Should not raise
        cm.set_callbacks(
            on_new_video=lambda v: None,
            on_auto_download=lambda v: None,
            on_status_update=lambda s: None
        )


class TestChannelMonitorConfig:
    def test_config_persists(self, tmp_path):
        config_dir = str(tmp_path / "config")
        cm1 = ChannelMonitor(config_dir=config_dir, output_dir=str(tmp_path / "dl"))
        cm1.set_interval(120)
        cm1.set_notifications(False)
        cm1._save_config()

        # Create new instance — should load persisted settings
        cm2 = ChannelMonitor(config_dir=config_dir, output_dir=str(tmp_path / "dl"))
        assert cm2.get_interval() == 120
        assert cm2.get_notifications() is False
