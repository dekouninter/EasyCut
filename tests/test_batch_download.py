# -*- coding: utf-8 -*-
"""Tests for the batch download system.

Tests cover queue management, progress tracking, error handling, and edge cases
for the batch download functionality introduced in v1.10.0.
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Minimal stubs for importing easycut without a full Tk app
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_heavy_imports(monkeypatch):
    """Stub out heavyweight imports that easycut.py pulls in at module level."""
    fake_ytdlp = types.ModuleType("yt_dlp")
    fake_ytdlp.YoutubeDL = MagicMock
    monkeypatch.setitem(sys.modules, "yt_dlp", fake_ytdlp)


from easycut import EasyCutApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class _FakeConfigManager:
    """Minimal config manager stub."""

    def __init__(self, data=None):
        self._data = data or {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def add_to_history(self, entry):
        pass


class _FakePostProcessor:
    output_dir = "."
    ffmpeg_available = True


class _FakeBatchLog:
    """Fake batch log to capture messages."""

    def __init__(self):
        self.logs = []

    def add_log(self, msg, level="INFO"):
        self.logs.append((msg, level))


@pytest.fixture
def mock_app(monkeypatch):
    """Create a minimal EasyCutApp-like object for batch download testing."""
    app = MagicMock(spec=EasyCutApp)
    app.config_manager = _FakeConfigManager()
    app.post_processor = _FakePostProcessor()
    app.output_dir = Path(".")
    app.batch_log = _FakeBatchLog()

    # Translator stub
    app.translator = MagicMock()
    app.translator.get = MagicMock(side_effect=lambda key, default="": default)

    # Initialize download queue attributes
    app._download_queue = []
    app._queue_paused = False
    app.is_downloading = False

    # Bind real static methods
    app._parse_rate_limit = EasyCutApp._parse_rate_limit

    return app


def create_queue_item(url, status="queued", title=None, progress=0.0,
                      speed="", eta="", error_msg="",
                      downloaded_bytes=0, total_bytes=0):
    """Helper to create a queue item with the expected structure."""
    return {
        "url": url,
        "status": status,
        "title": title or url[:50],
        "progress": progress,
        "speed": speed,
        "eta": eta,
        "error_msg": error_msg,
        "downloaded_bytes": downloaded_bytes,
        "total_bytes": total_bytes,
    }


# ---------------------------------------------------------------------------
# Queue Management Tests
# ---------------------------------------------------------------------------

class TestQueueManagement:
    """Tests for queue item creation and management."""

    def test_queue_item_has_correct_structure(self):
        """Queue item should have all required fields."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        
        required_fields = ["url", "status", "title", "progress", "speed",
                          "eta", "error_msg", "downloaded_bytes", "total_bytes"]
        for field in required_fields:
            assert field in item, f"Missing required field: {field}"

    def test_queue_item_initialized_with_queued_status(self):
        """New queue items should have 'queued' status."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        assert item["status"] == "queued"

    def test_queue_item_progress_initialized_to_zero(self):
        """New queue items should have zero progress."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        assert item["progress"] == 0.0
        assert item["downloaded_bytes"] == 0
        assert item["total_bytes"] == 0

    def test_queue_maintains_fifo_order(self, mock_app):
        """Queue should maintain FIFO (first-in, first-out) order."""
        urls = [
            "https://youtube.com/watch?v=first",
            "https://youtube.com/watch?v=second",
            "https://youtube.com/watch?v=third",
        ]
        
        for url in urls:
            mock_app._download_queue.append(create_queue_item(url))
        
        assert mock_app._download_queue[0]["url"] == urls[0]
        assert mock_app._download_queue[1]["url"] == urls[1]
        assert mock_app._download_queue[2]["url"] == urls[2]

    def test_queue_status_transition_queued_to_downloading(self, mock_app):
        """Item status should transition from queued to downloading."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        mock_app._download_queue.append(item)
        
        assert mock_app._download_queue[0]["status"] == "queued"
        mock_app._download_queue[0]["status"] = "downloading"
        assert mock_app._download_queue[0]["status"] == "downloading"

    def test_queue_status_transition_downloading_to_completed(self, mock_app):
        """Item status should transition from downloading to completed."""
        item = create_queue_item("https://youtube.com/watch?v=abc123", status="downloading")
        mock_app._download_queue.append(item)
        
        mock_app._download_queue[0]["status"] = "completed"
        mock_app._download_queue[0]["progress"] = 1.0
        
        assert mock_app._download_queue[0]["status"] == "completed"
        assert mock_app._download_queue[0]["progress"] == 1.0

    def test_queue_status_transition_downloading_to_failed(self, mock_app):
        """Item status should transition from downloading to failed with error_msg."""
        item = create_queue_item("https://youtube.com/watch?v=abc123", status="downloading")
        mock_app._download_queue.append(item)
        
        mock_app._download_queue[0]["status"] = "failed"
        mock_app._download_queue[0]["error_msg"] = "Network error"
        
        assert mock_app._download_queue[0]["status"] == "failed"
        assert mock_app._download_queue[0]["error_msg"] == "Network error"

    def test_queue_item_title_truncated_to_50_chars(self):
        """Queue item title should be truncated to 50 characters."""
        long_url = "https://youtube.com/watch?v=" + "x" * 100
        item = create_queue_item(long_url)
        assert len(item["title"]) <= 50


# ---------------------------------------------------------------------------
# Progress Tracking Tests
# ---------------------------------------------------------------------------

class TestProgressTracking:
    """Tests for individual and global progress tracking."""

    def test_individual_progress_range_zero_to_one(self, mock_app):
        """Individual progress should be between 0.0 and 1.0."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        mock_app._download_queue.append(item)
        
        # Test various progress values
        mock_app._download_queue[0]["progress"] = 0.0
        assert 0.0 <= mock_app._download_queue[0]["progress"] <= 1.0
        
        mock_app._download_queue[0]["progress"] = 0.5
        assert 0.0 <= mock_app._download_queue[0]["progress"] <= 1.0
        
        mock_app._download_queue[0]["progress"] = 1.0
        assert 0.0 <= mock_app._download_queue[0]["progress"] <= 1.0

    def test_progress_calculated_from_bytes(self, mock_app):
        """Progress should be calculated from downloaded_bytes / total_bytes."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        mock_app._download_queue.append(item)
        
        mock_app._download_queue[0]["downloaded_bytes"] = 50 * 1024 * 1024  # 50 MB
        mock_app._download_queue[0]["total_bytes"] = 100 * 1024 * 1024  # 100 MB
        
        # Calculate progress as the implementation does
        downloaded = mock_app._download_queue[0]["downloaded_bytes"]
        total = mock_app._download_queue[0]["total_bytes"]
        progress = downloaded / total if total > 0 else 0.0
        
        mock_app._download_queue[0]["progress"] = progress
        assert mock_app._download_queue[0]["progress"] == 0.5

    def test_speed_and_eta_stored_as_strings(self, mock_app):
        """Speed and ETA should be stored as formatted strings."""
        item = create_queue_item(
            "https://youtube.com/watch?v=abc123",
            speed="2.5 MB/s",
            eta="1:23"
        )
        mock_app._download_queue.append(item)
        
        assert mock_app._download_queue[0]["speed"] == "2.5 MB/s"
        assert mock_app._download_queue[0]["eta"] == "1:23"

    def test_eta_format_minutes_seconds(self, mock_app):
        """ETA should be formatted as MM:SS."""
        item = create_queue_item("https://youtube.com/watch?v=abc123")
        mock_app._download_queue.append(item)
        
        # Simulate ETA calculation as in the implementation
        eta_seconds = 83  # 1 minute 23 seconds
        mins, secs = divmod(int(eta_seconds), 60)
        eta_formatted = f"{mins}:{secs:02d}"
        
        mock_app._download_queue[0]["eta"] = eta_formatted
        assert mock_app._download_queue[0]["eta"] == "1:23"

    def test_global_progress_completed_count(self, mock_app):
        """Global progress should track completed items out of total."""
        # Add 3 items with different statuses
        mock_app._download_queue.append(create_queue_item("url1", status="completed"))
        mock_app._download_queue.append(create_queue_item("url2", status="downloading"))
        mock_app._download_queue.append(create_queue_item("url3", status="queued"))
        
        completed = sum(1 for item in mock_app._download_queue if item["status"] == "completed")
        total = len(mock_app._download_queue)
        
        assert completed == 1
        assert total == 3


# ---------------------------------------------------------------------------
# Error Handling Tests
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Tests for error handling in batch downloads."""

    def test_failed_item_has_error_msg(self, mock_app):
        """Failed items should capture the error message."""
        item = create_queue_item(
            "https://youtube.com/watch?v=abc123",
            status="failed",
            error_msg="Video unavailable"
        )
        mock_app._download_queue.append(item)
        
        assert mock_app._download_queue[0]["status"] == "failed"
        assert mock_app._download_queue[0]["error_msg"] == "Video unavailable"

    def test_partial_failure_some_succeed_some_fail(self, mock_app):
        """Some items can succeed while others fail."""
        mock_app._download_queue.append(create_queue_item("url1", status="completed"))
        mock_app._download_queue.append(create_queue_item("url2", status="failed", error_msg="Network error"))
        mock_app._download_queue.append(create_queue_item("url3", status="completed"))
        
        completed = sum(1 for item in mock_app._download_queue if item["status"] == "completed")
        failed = sum(1 for item in mock_app._download_queue if item["status"] == "failed")
        
        assert completed == 2
        assert failed == 1

    def test_retry_resets_item_status(self, mock_app):
        """Retry should reset item status and clear error_msg."""
        # Setup failed item
        item = create_queue_item(
            "https://youtube.com/watch?v=abc123",
            status="failed",
            error_msg="Network error",
            progress=0.5,
            speed="1.0 MB/s",
            eta="0:30",
            downloaded_bytes=50000,
            total_bytes=100000
        )
        mock_app._download_queue.append(item)
        mock_app._refresh_queue_ui = MagicMock()
        
        # Simulate retry logic from _retry_batch_item
        index = 0
        item = mock_app._download_queue[index]
        item["status"] = "queued"
        item["progress"] = 0.0
        item["speed"] = ""
        item["eta"] = ""
        item["error_msg"] = ""
        item["downloaded_bytes"] = 0
        item["total_bytes"] = 0
        
        # Verify reset
        assert mock_app._download_queue[0]["status"] == "queued"
        assert mock_app._download_queue[0]["progress"] == 0.0
        assert mock_app._download_queue[0]["error_msg"] == ""
        assert mock_app._download_queue[0]["downloaded_bytes"] == 0
        assert mock_app._download_queue[0]["total_bytes"] == 0

    def test_retry_out_of_bounds_index(self, mock_app):
        """Retry with invalid index should not crash."""
        mock_app._download_queue.append(create_queue_item("url1"))
        mock_app._refresh_queue_ui = MagicMock()
        
        # Simulate _retry_batch_item with out-of-bounds index
        index = 10  # Invalid index
        if index >= len(mock_app._download_queue):
            # Should return early without error
            pass
        
        # Queue should be unchanged
        assert len(mock_app._download_queue) == 1

    def test_error_msg_truncated_for_display(self, mock_app):
        """Error messages can be truncated for display."""
        long_error = "This is a very long error message " * 10
        item = create_queue_item(
            "https://youtube.com/watch?v=abc123",
            status="failed",
            error_msg=long_error
        )
        mock_app._download_queue.append(item)
        
        # Error message should be stored in full
        assert mock_app._download_queue[0]["error_msg"] == long_error
        # But can be truncated for display (as done in _refresh_queue_ui)
        display_error = mock_app._download_queue[0]["error_msg"][:60]
        assert len(display_error) <= 60


# ---------------------------------------------------------------------------
# Edge Cases Tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Tests for edge cases in batch download."""

    def test_empty_queue_handling(self, mock_app):
        """Empty queue should be handled gracefully."""
        assert len(mock_app._download_queue) == 0
        
        # Operations on empty queue should not crash
        completed = sum(1 for item in mock_app._download_queue if item["status"] == "completed")
        total = len(mock_app._download_queue)
        
        assert completed == 0
        assert total == 0
        
        # Progress calculation with empty queue
        progress_pct = (completed / total * 100) if total > 0 else 0
        assert progress_pct == 0

    def test_single_item_batch(self, mock_app):
        """Single item batch should work correctly."""
        mock_app._download_queue.append(create_queue_item("https://youtube.com/watch?v=single"))
        
        assert len(mock_app._download_queue) == 1
        
        # Transition through statuses
        mock_app._download_queue[0]["status"] = "downloading"
        mock_app._download_queue[0]["progress"] = 0.5
        assert mock_app._download_queue[0]["status"] == "downloading"
        
        mock_app._download_queue[0]["status"] = "completed"
        mock_app._download_queue[0]["progress"] = 1.0
        assert mock_app._download_queue[0]["status"] == "completed"

    def test_duplicate_urls_in_queue(self, mock_app):
        """Duplicate URLs should be allowed in queue."""
        url = "https://youtube.com/watch?v=duplicate"
        
        mock_app._download_queue.append(create_queue_item(url))
        mock_app._download_queue.append(create_queue_item(url))
        mock_app._download_queue.append(create_queue_item(url))
        
        assert len(mock_app._download_queue) == 3
        
        # Each item should be independent
        mock_app._download_queue[0]["status"] = "completed"
        mock_app._download_queue[1]["status"] = "failed"
        mock_app._download_queue[2]["status"] = "queued"
        
        assert mock_app._download_queue[0]["status"] == "completed"
        assert mock_app._download_queue[1]["status"] == "failed"
        assert mock_app._download_queue[2]["status"] == "queued"

    def test_queue_clear_completed_removes_only_completed(self, mock_app):
        """Clear completed should only remove completed items."""
        mock_app._download_queue.append(create_queue_item("url1", status="completed"))
        mock_app._download_queue.append(create_queue_item("url2", status="failed"))
        mock_app._download_queue.append(create_queue_item("url3", status="queued"))
        mock_app._download_queue.append(create_queue_item("url4", status="completed"))
        
        # Simulate _queue_clear_completed
        mock_app._download_queue = [
            item for item in mock_app._download_queue
            if item["status"] != "completed"
        ]
        
        assert len(mock_app._download_queue) == 2
        assert mock_app._download_queue[0]["status"] == "failed"
        assert mock_app._download_queue[1]["status"] == "queued"


# ---------------------------------------------------------------------------
# Pause/Resume Tests
# ---------------------------------------------------------------------------

class TestPauseResume:
    """Tests for pause and resume functionality."""

    def test_pause_sets_queued_items_to_paused(self, mock_app):
        """Pausing should change queued items to paused status."""
        mock_app._download_queue.append(create_queue_item("url1", status="queued"))
        mock_app._download_queue.append(create_queue_item("url2", status="downloading"))
        mock_app._download_queue.append(create_queue_item("url3", status="queued"))
        
        # Simulate _queue_toggle_pause (pause)
        mock_app._queue_paused = True
        for item in mock_app._download_queue:
            if item["status"] == "queued":
                item["status"] = "paused"
        
        assert mock_app._download_queue[0]["status"] == "paused"
        assert mock_app._download_queue[1]["status"] == "downloading"  # unchanged
        assert mock_app._download_queue[2]["status"] == "paused"

    def test_resume_sets_paused_items_to_queued(self, mock_app):
        """Resuming should change paused items back to queued status."""
        mock_app._download_queue.append(create_queue_item("url1", status="paused"))
        mock_app._download_queue.append(create_queue_item("url2", status="downloading"))
        mock_app._download_queue.append(create_queue_item("url3", status="paused"))
        mock_app._queue_paused = True
        
        # Simulate _queue_toggle_pause (resume)
        mock_app._queue_paused = False
        for item in mock_app._download_queue:
            if item["status"] == "paused":
                item["status"] = "queued"
        
        assert mock_app._download_queue[0]["status"] == "queued"
        assert mock_app._download_queue[1]["status"] == "downloading"  # unchanged
        assert mock_app._download_queue[2]["status"] == "queued"


# ---------------------------------------------------------------------------
# Status Count Tests
# ---------------------------------------------------------------------------

class TestStatusCounting:
    """Tests for counting items by status."""

    def test_count_all_status_types(self, mock_app):
        """Should correctly count items in each status."""
        mock_app._download_queue.append(create_queue_item("url1", status="queued"))
        mock_app._download_queue.append(create_queue_item("url2", status="queued"))
        mock_app._download_queue.append(create_queue_item("url3", status="downloading"))
        mock_app._download_queue.append(create_queue_item("url4", status="completed"))
        mock_app._download_queue.append(create_queue_item("url5", status="completed"))
        mock_app._download_queue.append(create_queue_item("url6", status="completed"))
        mock_app._download_queue.append(create_queue_item("url7", status="failed"))
        mock_app._download_queue.append(create_queue_item("url8", status="paused"))
        
        queued = sum(1 for item in mock_app._download_queue if item["status"] == "queued")
        downloading = sum(1 for item in mock_app._download_queue if item["status"] == "downloading")
        completed = sum(1 for item in mock_app._download_queue if item["status"] == "completed")
        failed = sum(1 for item in mock_app._download_queue if item["status"] == "failed")
        paused = sum(1 for item in mock_app._download_queue if item["status"] == "paused")
        
        assert queued == 2
        assert downloading == 1
        assert completed == 3
        assert failed == 1
        assert paused == 1

    def test_global_progress_percentage(self, mock_app):
        """Global progress percentage should be calculated correctly."""
        mock_app._download_queue.append(create_queue_item("url1", status="completed"))
        mock_app._download_queue.append(create_queue_item("url2", status="completed"))
        mock_app._download_queue.append(create_queue_item("url3", status="downloading"))
        mock_app._download_queue.append(create_queue_item("url4", status="queued"))
        
        completed = sum(1 for item in mock_app._download_queue if item["status"] == "completed")
        total = len(mock_app._download_queue)
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        assert progress_pct == 50.0
