# -*- coding: utf-8 -*-
"""Tests for the post-processor module (post_processor.py).

Covers FFmpeg availability detection, output path building, Premiere
compatibility checking, and async operation dispatch.
"""

import sys
import json
import subprocess
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from post_processor import PostProcessor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pp(tmp_path):
    """PostProcessor with FFmpeg stubbed out."""
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        processor = PostProcessor(output_dir=str(tmp_path))
    return processor


@pytest.fixture
def pp_no_ffmpeg(tmp_path):
    """PostProcessor when FFmpeg is not available."""
    with patch("shutil.which", return_value=None):
        processor = PostProcessor(output_dir=str(tmp_path))
    return processor


# ---------------------------------------------------------------------------
# Init & FFmpeg detection
# ---------------------------------------------------------------------------

class TestPostProcessorInit:
    def test_ffmpeg_available(self, pp):
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            assert pp.ffmpeg_available is True
        assert pp.ffmpeg_path == "/usr/bin/ffmpeg"

    def test_ffmpeg_unavailable(self, pp_no_ffmpeg):
        with patch("shutil.which", return_value=None):
            assert pp_no_ffmpeg.ffmpeg_available is False
        # ffmpeg_path falls back to "ffmpeg" string (not None)
        assert pp_no_ffmpeg.ffmpeg_path == "ffmpeg"


# ---------------------------------------------------------------------------
# Output path building
# ---------------------------------------------------------------------------

class TestBuildOutputPath:
    def test_suffix_added(self, pp):
        result = pp._build_output_path("/tmp/video.mp4", "normalized")
        assert result == Path("/tmp/video_normalized.mp4")

    def test_custom_extension(self, pp):
        result = pp._build_output_path("/tmp/video.mkv", "audio", ".mp3")
        assert result == Path("/tmp/video_audio.mp3")

    def test_preserves_original_ext(self, pp):
        result = pp._build_output_path("/tmp/clip.webm", "stabilized")
        assert result.suffix == ".webm"


# ---------------------------------------------------------------------------
# Premiere compatibility checks
# ---------------------------------------------------------------------------

class TestPremiereCompatibility:
    """Tests for is_premiere_compatible and convert_for_premiere."""

    def test_compatible_mp4_h264_aac(self, pp):
        info = {
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {"codec_type": "audio", "codec_name": "aac"},
            ],
        }
        with patch.object(pp, "get_media_info", return_value=info):
            assert pp.is_premiere_compatible("/tmp/video.mp4") is True

    def test_incompatible_webm_vp9(self, pp):
        info = {
            "format": {"format_name": "matroska,webm"},
            "streams": [
                {"codec_type": "video", "codec_name": "vp9"},
                {"codec_type": "audio", "codec_name": "opus"},
            ],
        }
        with patch.object(pp, "get_media_info", return_value=info):
            assert pp.is_premiere_compatible("/tmp/video.webm") is False

    def test_compatible_prores(self, pp):
        info = {
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
            "streams": [
                {"codec_type": "video", "codec_name": "prores"},
                {"codec_type": "audio", "codec_name": "pcm_s16le"},
            ],
        }
        with patch.object(pp, "get_media_info", return_value=info):
            assert pp.is_premiere_compatible("/tmp/video.mov") is True

    def test_no_info_returns_false(self, pp):
        with patch.object(pp, "get_media_info", return_value={}):
            assert pp.is_premiere_compatible("/tmp/video.mp4") is False

    def test_no_audio_stream_returns_false(self, pp):
        info = {
            "format": {"format_name": "mov,mp4"},
            "streams": [{"codec_type": "video", "codec_name": "h264"}],
        }
        with patch.object(pp, "get_media_info", return_value=info):
            assert pp.is_premiere_compatible("/tmp/video.mp4") is False

    def test_convert_for_premiere_calls_ffmpeg(self, pp):
        with patch.object(pp, "_run_ffmpeg", return_value=True) as mock_ff:
            result = pp.convert_for_premiere("/tmp/video.webm")
        assert result is not None
        assert "_premiere" in result
        assert ".mp4" in result
        mock_ff.assert_called_once()
        args = mock_ff.call_args[0][0]
        assert "-c:v" in args
        assert "libx264" in args

    def test_convert_for_premiere_failure(self, pp):
        with patch.object(pp, "_run_ffmpeg", return_value=False):
            result = pp.convert_for_premiere("/tmp/video.webm")
        assert result is None


# ---------------------------------------------------------------------------
# Operation dispatch (run_async)
# ---------------------------------------------------------------------------

class TestRunAsync:
    def test_unknown_operation(self, pp):
        result = pp.run_async("unknown_op", "/tmp/video.mp4")
        assert result is None

    def test_dispatches_normalize_audio(self, pp):
        with patch.object(pp, "normalize_audio", return_value="/tmp/out.mp4") as mock_op:
            thread = pp.run_async("normalize_audio", "/tmp/video.mp4")
            thread.join(timeout=5)
        mock_op.assert_called_once()

    def test_output_callback_called(self, pp):
        callback = MagicMock()
        output_cb = MagicMock()
        with patch.object(pp, "compress", return_value="/tmp/compressed.mp4"):
            thread = pp.run_async("compress", "/tmp/video.mp4",
                                  callback=callback, output_callback=output_cb)
            thread.join(timeout=5)
        output_cb.assert_called_once_with("/tmp/compressed.mp4")

    def test_output_callback_not_called_on_failure(self, pp):
        output_cb = MagicMock()
        with patch.object(pp, "denoise_video", return_value=None):
            thread = pp.run_async("denoise_video", "/tmp/video.mp4",
                                  output_callback=output_cb)
            thread.join(timeout=5)
        output_cb.assert_not_called()

    def test_kwargs_passed_through(self, pp):
        with patch.object(pp, "upscale", return_value="/tmp/up.mp4") as mock_op:
            thread = pp.run_async("upscale", "/tmp/video.mp4",
                                  target_height=1080)
            thread.join(timeout=5)
        mock_op.assert_called_once_with("/tmp/video.mp4", callback=None,
                                        target_height=1080)


# ---------------------------------------------------------------------------
# Individual operations (parameter validation)
# ---------------------------------------------------------------------------

class TestChangeSpeed:
    def test_invalid_speed_zero(self, pp):
        result = pp.change_speed("/tmp/video.mp4", speed=0)
        assert result is None

    def test_invalid_speed_negative(self, pp):
        result = pp.change_speed("/tmp/video.mp4", speed=-1)
        assert result is None

    def test_invalid_speed_too_fast(self, pp):
        result = pp.change_speed("/tmp/video.mp4", speed=5)
        assert result is None

    def test_valid_speed_calls_ffmpeg(self, pp):
        with patch.object(pp, "_run_ffmpeg", return_value=True) as mock_ff:
            result = pp.change_speed("/tmp/video.mp4", speed=2.0)
        assert result is not None
        mock_ff.assert_called_once()


class TestCancel:
    def test_cancel_terminates_process(self, pp):
        mock_proc = MagicMock()
        pp._active_process = mock_proc
        pp.cancel()
        mock_proc.terminate.assert_called_once()

    def test_cancel_no_active_process(self, pp):
        pp._active_process = None
        pp.cancel()  # Should not raise
