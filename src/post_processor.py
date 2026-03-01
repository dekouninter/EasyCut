# -*- coding: utf-8 -*-
"""
Post-Processing Module for EasyCut
FFmpeg-powered video/audio enhancement pipeline

Author: Deko Costa
License: GPL-3.0
"""

import subprocess
import shutil
import logging
import threading
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class PostProcessor:
    """FFmpeg-based post-processing for downloaded media files"""

    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe_path = shutil.which("ffprobe") or "ffprobe"
        self._active_process: Optional[subprocess.Popen] = None

    @property
    def ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available"""
        return shutil.which("ffmpeg") is not None

    def get_media_info(self, filepath: str) -> dict:
        """Get media file info using ffprobe"""
        try:
            cmd = [
                self.ffprobe_path, "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(filepath)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception as e:
            logger.warning(f"ffprobe failed: {e}")
        return {}

    def _build_output_path(self, input_path: str, suffix: str, ext: str = None) -> Path:
        """Build output file path with suffix"""
        p = Path(input_path)
        new_ext = ext or p.suffix
        return p.parent / f"{p.stem}_{suffix}{new_ext}"

    def _run_ffmpeg(self, args: list, callback: Optional[Callable] = None) -> bool:
        """Run FFmpeg command with optional completion callback"""
        try:
            cmd = [self.ffmpeg_path] + args
            logger.info(f"FFmpeg: {' '.join(cmd)}")

            self._active_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            _, stderr = self._active_process.communicate()
            success = self._active_process.returncode == 0

            if not success:
                logger.error(f"FFmpeg error: {stderr.decode('utf-8', errors='replace')[:500]}")

            self._active_process = None
            if callback:
                callback(success)
            return success

        except Exception as e:
            logger.error(f"FFmpeg execution error: {e}")
            self._active_process = None
            if callback:
                callback(False)
            return False

    def cancel(self):
        """Cancel active FFmpeg process"""
        if self._active_process:
            try:
                self._active_process.terminate()
            except Exception:
                pass

    # ── Enhancement Operations ──────────────────────

    def normalize_audio(self, input_path: str, callback: Callable = None) -> Optional[str]:
        """Normalize audio levels using loudnorm filter"""
        output = self._build_output_path(input_path, "normalized")
        args = [
            "-i", str(input_path),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v", "copy",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def denoise_video(self, input_path: str, callback: Callable = None) -> Optional[str]:
        """Apply video denoising using hqdn3d filter"""
        output = self._build_output_path(input_path, "denoised")
        args = [
            "-i", str(input_path),
            "-vf", "hqdn3d=4:3:6:4.5",
            "-c:a", "copy",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def stabilize_video(self, input_path: str, callback: Callable = None) -> Optional[str]:
        """Stabilize shaky video using vidstabdetect/vidstabtransform"""
        # Two-pass stabilization
        transforms_file = self._build_output_path(input_path, "transforms", ".trf")
        output = self._build_output_path(input_path, "stabilized")

        # Pass 1: Detect motion vectors
        args1 = [
            "-i", str(input_path),
            "-vf", f"vidstabdetect=shakiness=5:accuracy=15:result={transforms_file}",
            "-f", "null", "-"
        ]
        if not self._run_ffmpeg(args1):
            return None

        # Pass 2: Apply stabilization
        args2 = [
            "-i", str(input_path),
            "-vf", f"vidstabtransform=input={transforms_file}:smoothing=10,unsharp=5:5:0.8:3:3:0.4",
            "-c:a", "copy",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args2, callback)

        # Cleanup transforms file
        try:
            Path(transforms_file).unlink(missing_ok=True)
        except Exception:
            pass

        return str(output) if success else None

    def upscale(self, input_path: str, target_height: int = 1080, callback: Callable = None) -> Optional[str]:
        """Upscale video to target resolution"""
        output = self._build_output_path(input_path, f"upscaled_{target_height}p")
        args = [
            "-i", str(input_path),
            "-vf", f"scale=-2:{target_height}:flags=lanczos",
            "-c:a", "copy",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def compress(self, input_path: str, crf: int = 28, callback: Callable = None) -> Optional[str]:
        """Compress video with specified CRF value"""
        output = self._build_output_path(input_path, "compressed")
        args = [
            "-i", str(input_path),
            "-c:v", "libx264", "-crf", str(crf),
            "-preset", "medium",
            "-c:a", "aac", "-b:a", "128k",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def scale(self, input_path: str, width: int, height: int, callback: Callable = None) -> Optional[str]:
        """Scale video to specific resolution"""
        output = self._build_output_path(input_path, f"{width}x{height}")
        args = [
            "-i", str(input_path),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def extract_audio(self, input_path: str, format: str = "mp3", callback: Callable = None) -> Optional[str]:
        """Extract audio from video file"""
        ext_map = {"mp3": ".mp3", "wav": ".wav", "m4a": ".m4a", "opus": ".opus"}
        codec_map = {"mp3": "libmp3lame", "wav": "pcm_s16le", "m4a": "aac", "opus": "libopus"}

        ext = ext_map.get(format, ".mp3")
        codec = codec_map.get(format, "libmp3lame")
        output = self._build_output_path(input_path, "audio", ext)

        args = [
            "-i", str(input_path),
            "-vn", "-acodec", codec,
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def trim(self, input_path: str, start_time: str, end_time: str, callback: Callable = None) -> Optional[str]:
        """Trim video between start and end times (HH:MM:SS format)"""
        output = self._build_output_path(input_path, "trimmed")
        args = [
            "-i", str(input_path),
            "-ss", start_time,
            "-to", end_time,
            "-c", "copy",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    # ── Premiere Compatibility Helpers ─────────────────────

    def is_premiere_compatible(self, input_path: str) -> bool:
        """Return True if the file is already in a Premiere-friendly format.

        Checks container and codec names via ffprobe. We consider MP4/MOV with
        H.264 (or ProRes/HEVC) video and AAC (or PCM) audio as compatible.
        """
        info = self.get_media_info(input_path)
        if not info:
            return False
        fmt = info.get('format', {}).get('format_name', '')
        if 'mp4' not in fmt and 'mov' not in fmt:
            return False
        video_codec = None
        audio_codec = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video' and not video_codec:
                video_codec = stream.get('codec_name')
            elif stream.get('codec_type') == 'audio' and not audio_codec:
                audio_codec = stream.get('codec_name')
        if not video_codec or not audio_codec:
            return False
        # allow common Premiere-friendly codecs
        if video_codec.lower() in ('h264', 'prores', 'hevc') and audio_codec.lower() in ('aac', 'mp3', 'pcm_s16le', 'flac'):
            return True
        return False

    def convert_for_premiere(self, input_path: str, callback: Callable = None) -> Optional[str]:
        """Convert any media file to MP4/H264 + AAC for Premiere compatibility."""
        output = self._build_output_path(input_path, "premiere", ".mp4")
        args = [
            "-i", str(input_path),
            # video: h264, reasonable quality
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            # audio: aac at 192kbps
            "-c:a", "aac", "-b:a", "192k",
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def change_speed(self, input_path: str, speed: float = 1.0, callback: Callable = None) -> Optional[str]:
        """Change video playback speed"""
        if speed <= 0 or speed > 4:
            return None
        output = self._build_output_path(input_path, f"speed_{speed}x")
        # Video: setpts, Audio: atempo (atempo only accepts 0.5-2.0, chain for wider range)
        video_filter = f"setpts={1/speed}*PTS"

        # Build atempo chain for audio
        atempo_filters = []
        remaining = speed
        while remaining > 2.0:
            atempo_filters.append("atempo=2.0")
            remaining /= 2.0
        while remaining < 0.5:
            atempo_filters.append("atempo=0.5")
            remaining /= 0.5
        atempo_filters.append(f"atempo={remaining:.4f}")
        audio_filter = ",".join(atempo_filters)

        args = [
            "-i", str(input_path),
            "-vf", video_filter,
            "-af", audio_filter,
            "-y", str(output)
        ]
        success = self._run_ffmpeg(args, callback)
        return str(output) if success else None

    def run_async(self, operation: str, input_path: str, callback: Callable = None,
                  output_callback: Callable = None, **kwargs):
        """Run a post-processing operation in a background thread.

        Args:
            operation: Name of the processing operation.
            input_path: Path to the input file.
            callback: Called with (success: bool) when done.
            output_callback: Called with (output_path: str) on success, allowing
                             callers to load the result (e.g. into a media player).
        """
        ops = {
            "normalize_audio": self.normalize_audio,
            "denoise_video": self.denoise_video,
            "stabilize_video": self.stabilize_video,
            "upscale": self.upscale,
            "compress": self.compress,
            "scale": self.scale,
            "extract_audio": self.extract_audio,
            "trim": self.trim,
            "change_speed": self.change_speed,
            "convert_for_premiere": self.convert_for_premiere,
            "is_premiere_compatible": self.is_premiere_compatible,
        }
        func = ops.get(operation)
        if not func:
            logger.error(f"Unknown operation: {operation}")
            return

        def worker():
            result = func(input_path, callback=callback, **kwargs)
            if output_callback and result:
                output_callback(result)
            return result

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
