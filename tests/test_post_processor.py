# -*- coding: utf-8 -*-
"""Tests for post_processor.py — Post-processing operations."""

import pytest
from pathlib import Path
from unittest.mock import patch
from post_processor import PostProcessor


class TestPostProcessorInit:
    def test_init_creates_instance(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        assert pp is not None

    def test_output_dir_stored(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        assert pp.output_dir == Path(str(tmp_path))


class TestFfmpegAvailable:
    def test_ffmpeg_available_returns_bool(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        assert isinstance(pp.ffmpeg_available, bool)

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_ffmpeg_available_true(self, mock_which, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        assert pp.ffmpeg_available is True

    @patch("shutil.which", return_value=None)
    def test_ffmpeg_not_available(self, mock_which, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        assert pp.ffmpeg_available is False


class TestBuildOutputPath:
    def test_basic_suffix(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        result = pp._build_output_path("video.mp4", "normalized")
        assert "normalized" in str(result)
        assert str(result).endswith(".mp4")

    def test_custom_extension(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        result = pp._build_output_path("video.mp4", "audio", ".mp3")
        assert str(result).endswith(".mp3")

    def test_preserves_directory(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        input_path = str(tmp_path / "subdir" / "video.mkv")
        result = pp._build_output_path(input_path, "compressed")
        assert Path(result).parent == tmp_path / "subdir"


class TestChangeSpeedValidation:
    def test_zero_speed_returns_none(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        result = pp.change_speed("test.mp4", speed=0)
        assert result is None

    def test_negative_speed_returns_none(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        result = pp.change_speed("test.mp4", speed=-1)
        assert result is None

    def test_speed_over_4_returns_none(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        result = pp.change_speed("test.mp4", speed=5)
        assert result is None


class TestCancel:
    def test_cancel_no_process(self, tmp_path):
        pp = PostProcessor(output_dir=str(tmp_path))
        # Should not raise even when no process is active
        pp.cancel()
