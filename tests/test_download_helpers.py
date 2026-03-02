# -*- coding: utf-8 -*-
"""Tests for download helpers: _check_duplicate, _apply_channel_default,
download_progress_hook, _queue_clear_completed, _clipper_remove.

These methods live on EasyCutApp and are tested via mock instances
calling the real unbound method.
"""

import sys
import types
from unittest.mock import MagicMock, call

import pytest

# Stub yt_dlp before importing easycut
fake_ytdlp = types.ModuleType("yt_dlp")
fake_ytdlp.YoutubeDL = MagicMock
sys.modules.setdefault("yt_dlp", fake_ytdlp)

from easycut import EasyCutApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class _FakeConfigManager:
    def __init__(self):
        self._data = {}
        self._history = []

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def load_history(self):
        return list(self._history)

    def save_history(self, h):
        self._history = h


@pytest.fixture
def mock_app():
    app = MagicMock(spec=EasyCutApp)
    app.config_manager = _FakeConfigManager()
    app.translator = MagicMock()
    app.translator.get = MagicMock(side_effect=lambda k, d="": d)
    app.download_log = MagicMock()
    app.root = MagicMock()
    app.download_quality_var = MagicMock()
    app.is_downloading = True
    return app


# ---------------------------------------------------------------------------
# _check_duplicate
# ---------------------------------------------------------------------------

class TestCheckDuplicate:
    def _call(self, app, video_id, title="Test"):
        return EasyCutApp._check_duplicate(app, video_id, title)

    def test_empty_video_id_returns_immediately(self, mock_app):
        self._call(mock_app, "")
        mock_app.root.after.assert_not_called()

    def test_no_match_in_empty_history(self, mock_app):
        self._call(mock_app, "abc123")
        mock_app.root.after.assert_not_called()

    def test_match_found_in_history(self, mock_app):
        mock_app.config_manager._history = [
            {"url": "https://youtube.com/watch?v=abc123", "status": "success"}
        ]
        self._call(mock_app, "abc123", "My Video")
        mock_app.root.after.assert_called_once()

    def test_error_status_not_matched(self, mock_app):
        mock_app.config_manager._history = [
            {"url": "https://youtube.com/watch?v=abc123", "status": "error"}
        ]
        self._call(mock_app, "abc123")
        mock_app.root.after.assert_not_called()

    def test_partial_video_id_match(self, mock_app):
        """video_id 'abc' should match URL containing 'abc123'."""
        mock_app.config_manager._history = [
            {"url": "https://youtube.com/watch?v=abc123", "status": "success"}
        ]
        self._call(mock_app, "abc")
        mock_app.root.after.assert_called_once()

    def test_multiple_entries_first_match_returns(self, mock_app):
        mock_app.config_manager._history = [
            {"url": "https://youtube.com/watch?v=aaa", "status": "success"},
            {"url": "https://youtube.com/watch?v=abc", "status": "success"},
        ]
        self._call(mock_app, "abc")
        # Should only schedule one warning (returns after first match)
        assert mock_app.root.after.call_count == 1


# ---------------------------------------------------------------------------
# _apply_channel_default
# ---------------------------------------------------------------------------

class TestApplyChannelDefault:
    def _call(self, app, uploader):
        return EasyCutApp._apply_channel_default(app, uploader)

    def test_empty_uploader_returns(self, mock_app):
        self._call(mock_app, "")
        mock_app.root.after.assert_not_called()

    def test_none_uploader_returns(self, mock_app):
        self._call(mock_app, None)
        mock_app.root.after.assert_not_called()

    def test_exact_match(self, mock_app):
        mock_app.config_manager._data["channel_defaults"] = {"MrBeast": "1080"}
        self._call(mock_app, "MrBeast")
        assert mock_app.root.after.call_count >= 1

    def test_case_insensitive(self, mock_app):
        mock_app.config_manager._data["channel_defaults"] = {"mrbeast": "720"}
        self._call(mock_app, "MRBEAST")
        assert mock_app.root.after.call_count >= 1

    def test_substring_match_forward(self, mock_app):
        mock_app.config_manager._data["channel_defaults"] = {"MrBeast": "best"}
        self._call(mock_app, "MrBeast Gaming")
        assert mock_app.root.after.call_count >= 1

    def test_substring_match_reverse(self, mock_app):
        mock_app.config_manager._data["channel_defaults"] = {"MrBeast Gaming": "audio"}
        self._call(mock_app, "MrBeast")
        assert mock_app.root.after.call_count >= 1

    def test_no_match(self, mock_app):
        mock_app.config_manager._data["channel_defaults"] = {"MrBeast": "1080"}
        self._call(mock_app, "PewDiePie")
        mock_app.root.after.assert_not_called()

    def test_empty_defaults(self, mock_app):
        mock_app.config_manager._data["channel_defaults"] = {}
        self._call(mock_app, "SomeChannel")
        mock_app.root.after.assert_not_called()

    def test_none_defaults(self, mock_app):
        # config returns None for missing key, method should handle it
        self._call(mock_app, "SomeChannel")
        mock_app.root.after.assert_not_called()


# ---------------------------------------------------------------------------
# download_progress_hook
# ---------------------------------------------------------------------------

class TestDownloadProgressHook:
    def _call(self, app, d):
        return EasyCutApp.download_progress_hook(app, d)

    def test_cancellation_raises(self, mock_app):
        mock_app.is_downloading = False
        with pytest.raises(Exception, match="cancelled"):
            self._call(mock_app, {"status": "downloading"})

    def test_downloading_updates_label(self, mock_app):
        mock_app.download_progress_label = MagicMock()
        self._call(mock_app, {
            "status": "downloading",
            "_percent_str": " 50% ",
            "_speed_str": "1MiB/s",
            "_eta_str": "00:30",
        })
        mock_app.root.after.assert_called_once()

    def test_downloading_excludes_unknown_speed(self, mock_app):
        """When speed is 'Unknown B/s' it should be omitted from display."""
        mock_app.download_progress_label = MagicMock()
        self._call(mock_app, {
            "status": "downloading",
            "_percent_str": "75%",
            "_speed_str": "Unknown B/s",
            "_eta_str": "Unknown",
        })
        # Still updates with percent only
        mock_app.root.after.assert_called_once()

    def test_finished_status(self, mock_app):
        mock_app.download_progress_label = MagicMock()
        self._call(mock_app, {"status": "finished"})
        mock_app.root.after.assert_called_once()

    def test_error_status(self, mock_app):
        mock_app.download_progress_label = MagicMock()
        self._call(mock_app, {"status": "error"})
        mock_app.root.after.assert_called_once()

    def test_no_progress_label_returns_safely(self, mock_app):
        """When download_progress_label attribute is missing, no crash."""
        del mock_app.download_progress_label
        # Should not raise for non-cancellation status
        self._call(mock_app, {"status": "downloading"})

    def test_unknown_status_no_crash(self, mock_app):
        mock_app.download_progress_label = MagicMock()
        self._call(mock_app, {"status": "unknown_xyz"})
        # No after call for unknown status
        mock_app.root.after.assert_not_called()


# ---------------------------------------------------------------------------
# _queue_clear_completed
# ---------------------------------------------------------------------------

class TestQueueClearCompleted:
    def test_removes_completed_items(self, mock_app):
        mock_app._download_queue = [
            {"url": "a", "status": "completed"},
            {"url": "b", "status": "queued"},
            {"url": "c", "status": "completed"},
        ]
        EasyCutApp._queue_clear_completed(mock_app)
        assert len(mock_app._download_queue) == 1
        assert mock_app._download_queue[0]["url"] == "b"

    def test_no_completed_items(self, mock_app):
        mock_app._download_queue = [
            {"url": "a", "status": "queued"},
            {"url": "b", "status": "error"},
        ]
        EasyCutApp._queue_clear_completed(mock_app)
        assert len(mock_app._download_queue) == 2

    def test_all_completed(self, mock_app):
        mock_app._download_queue = [
            {"url": "a", "status": "completed"},
            {"url": "b", "status": "completed"},
        ]
        EasyCutApp._queue_clear_completed(mock_app)
        assert mock_app._download_queue == []

    def test_empty_queue(self, mock_app):
        mock_app._download_queue = []
        EasyCutApp._queue_clear_completed(mock_app)
        assert mock_app._download_queue == []

    def test_preserves_paused_items(self, mock_app):
        mock_app._download_queue = [
            {"url": "a", "status": "paused"},
            {"url": "b", "status": "completed"},
        ]
        EasyCutApp._queue_clear_completed(mock_app)
        assert len(mock_app._download_queue) == 1
        assert mock_app._download_queue[0]["status"] == "paused"


# ---------------------------------------------------------------------------
# _clipper_remove
# ---------------------------------------------------------------------------

class TestClipperRemove:
    def test_remove_middle_clip(self, mock_app):
        mock_app._clip_markers = [
            {"index": 1, "start": "0:00", "end": "1:00"},
            {"index": 2, "start": "1:00", "end": "2:00"},
            {"index": 3, "start": "2:00", "end": "3:00"},
        ]
        EasyCutApp._clipper_remove(mock_app, 2)
        assert len(mock_app._clip_markers) == 2
        # Re-indexed: 1, 2
        assert mock_app._clip_markers[0]["index"] == 1
        assert mock_app._clip_markers[1]["index"] == 2

    def test_remove_only_clip(self, mock_app):
        mock_app._clip_markers = [{"index": 1, "start": "0:00", "end": "1:00"}]
        EasyCutApp._clipper_remove(mock_app, 1)
        assert mock_app._clip_markers == []

    def test_remove_nonexistent_index(self, mock_app):
        mock_app._clip_markers = [{"index": 1, "start": "0:00", "end": "1:00"}]
        EasyCutApp._clipper_remove(mock_app, 99)
        # List unchanged (still has original item, re-indexed to 1)
        assert len(mock_app._clip_markers) == 1
        assert mock_app._clip_markers[0]["index"] == 1

    def test_remove_first_reindexes(self, mock_app):
        mock_app._clip_markers = [
            {"index": 1, "start": "a"},
            {"index": 2, "start": "b"},
            {"index": 3, "start": "c"},
            {"index": 4, "start": "d"},
        ]
        EasyCutApp._clipper_remove(mock_app, 1)
        # Should re-index remaining 3 clips as 1, 2, 3
        assert [c["index"] for c in mock_app._clip_markers] == [1, 2, 3]
        assert mock_app._clip_markers[0]["start"] == "b"

    def test_remove_last(self, mock_app):
        mock_app._clip_markers = [
            {"index": 1, "start": "a"},
            {"index": 2, "start": "b"},
        ]
        EasyCutApp._clipper_remove(mock_app, 2)
        assert len(mock_app._clip_markers) == 1
        assert mock_app._clip_markers[0]["index"] == 1
        assert mock_app._clip_markers[0]["start"] == "a"
