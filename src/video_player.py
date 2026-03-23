# -*- coding: utf-8 -*-
"""
Embedded Video Player Widget for EasyCut
Uses mpv subprocess + JSON IPC for embedding video in Tkinter
Falls back to VLC (python-vlc) if available

Author: Deko Costa
License: GPL-3.0
"""

import tkinter as tk
from tkinter import ttk
import logging
import threading
import subprocess
import shutil
import time
import os
import sys
import json
import ctypes
from pathlib import Path
from typing import Optional, Callable
import random
import string

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────
# Windows Named Pipe utilities (for mpv IPC)
# ──────────────────────────────────────────

if sys.platform == "win32":
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
else:
    wintypes = None
    kernel32 = None

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

if sys.platform == "win32" and kernel32 and wintypes:
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE

    kernel32.WriteFile.argtypes = [
        wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p
    ]
    kernel32.WriteFile.restype = wintypes.BOOL

    kernel32.ReadFile.argtypes = [
        wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p
    ]
    kernel32.ReadFile.restype = wintypes.BOOL

    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    kernel32.SetNamedPipeHandleState.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD),
        ctypes.c_void_p, ctypes.c_void_p
    ]
    kernel32.SetNamedPipeHandleState.restype = wintypes.BOOL


def _pipe_connect(pipe_name: str, timeout: float = 8.0) -> Optional[int]:
    """Connect to a Windows named pipe, retrying until timeout"""
    start = time.time()
    while time.time() - start < timeout:
        handle = kernel32.CreateFileW(
            pipe_name,
            GENERIC_READ | GENERIC_WRITE,
            0, None, OPEN_EXISTING, 0, None
        )
        if handle != INVALID_HANDLE_VALUE:
            # Set pipe to byte read mode
            mode = wintypes.DWORD(0)
            kernel32.SetNamedPipeHandleState(handle, ctypes.byref(mode), None, None)
            return handle
        time.sleep(0.3)
    return None


def _pipe_send(handle: int, data: dict) -> Optional[dict]:
    """Send JSON command to mpv and read response"""
    if handle is None:
        return None
    try:
        msg = json.dumps(data).encode('utf-8') + b'\n'
        written = wintypes.DWORD()
        kernel32.WriteFile(handle, msg, len(msg), ctypes.byref(written), None)

        buf = ctypes.create_string_buffer(8192)
        read_count = wintypes.DWORD()
        kernel32.ReadFile(handle, buf, 8192, ctypes.byref(read_count), None)

        raw = buf.raw[:read_count.value].decode('utf-8', errors='replace').strip()
        lines = [ln for ln in raw.split('\n') if ln.strip()]
        for line in reversed(lines):
            try:
                resp = json.loads(line)
                if 'error' in resp:
                    return resp
            except json.JSONDecodeError:
                continue
        if lines:
            return json.loads(lines[0])
        return None
    except Exception as e:
        logger.debug(f"Pipe send error: {e}")
        return None


def _pipe_close(handle: int):
    """Close a pipe handle"""
    if handle is not None:
        try:
            kernel32.CloseHandle(handle)
        except Exception:
            pass


# ──────────────────────────────────────────
# Backend detection
# ──────────────────────────────────────────

_MPV_EXE_AVAILABLE = shutil.which("mpv") is not None
_VLC_AVAILABLE = False
_vlc_module = None

try:
    import vlc as _vlc_mod  # type: ignore[import-unresolved]
    _vlc_module = _vlc_mod
    _VLC_AVAILABLE = True
except (ImportError, OSError):
    pass


def get_available_backend() -> Optional[str]:
    """Return the best available player backend"""
    if _MPV_EXE_AVAILABLE:
        return "mpv"
    if _VLC_AVAILABLE:
        return "vlc"
    return None


def is_player_available() -> bool:
    """Check if any player backend is available"""
    return _MPV_EXE_AVAILABLE or _VLC_AVAILABLE


# ──────────────────────────────────────────
# Embedded Player Widget
# ──────────────────────────────────────────

class EmbeddedPlayer(tk.Frame):
    """
    Embedded video player widget for Tkinter.
    
    mpv backend: subprocess + JSON IPC via Windows named pipe.
      No DLL needed — works with any mpv.exe (MSIX, portable, etc.)
    
    VLC backend: python-vlc + libVLC (requires VLC installed).
    
    Features:
      - Embedded video rendering inside Tkinter
      - Seekbar + time display
      - Play/Pause/Stop + Volume
      - get_time() for precise clip marking
      - YouTube URL support (mpv uses yt-dlp natively)
    """

    def __init__(self, parent, dark_mode: bool = True,
                 on_time_update: Optional[Callable] = None,
                 height: int = 360, **kwargs):
        self._bg = "#0a0a14" if dark_mode else "#f5f5f5"
        super().__init__(parent, bg=self._bg, **kwargs)

        self.dark_mode = dark_mode
        self.on_time_update = on_time_update
        self._backend_name = get_available_backend()

        # mpv subprocess state
        self._mpv_proc: Optional[subprocess.Popen] = None
        self._mpv_pipe_handle = None
        self._mpv_pipe_name = ""

        # VLC state
        self._vlc_instance = None
        self._vlc_player = None

        # Common state
        self._playing = False
        self._paused = False
        self._duration = 0.0
        self._current_time = 0.0
        self._volume = 80
        self._seeking = False
        self._update_running = False
        self._destroyed = False
        self._loaded_url = None
        self._video_height = height
        self._ipc_lock = threading.Lock()

        self._build_ui()

        if self._backend_name:
            logger.info(f"EmbeddedPlayer: [{self._backend_name}] backend ready")

    # ──────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────

    def _build_ui(self):
        fg = "#d0d0d0" if self.dark_mode else "#333333"
        controls_bg = "#12122a" if self.dark_mode else "#e8e8e8"
        video_bg = "#000000"

        # ── Video Display ──
        self.video_frame = tk.Frame(self, bg=video_bg, height=self._video_height)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=(1, 0))
        self.video_frame.pack_propagate(False)

        if not self._backend_name:
            self._show_placeholder()
        else:
            self._ready_label = tk.Label(
                self.video_frame, text="🎬", bg=video_bg, fg="#333333",
                font=("Segoe UI", 48)
            )
            self._ready_label.place(relx=0.5, rely=0.5, anchor="center")

        # ── Controls ──
        self.controls = tk.Frame(self, bg=controls_bg)
        self.controls.pack(fill=tk.X, padx=1, pady=(0, 1))

        # Seekbar row
        seekbar_row = tk.Frame(self.controls, bg=controls_bg)
        seekbar_row.pack(fill=tk.X, padx=10, pady=(6, 2))

        self.time_current_label = tk.Label(
            seekbar_row, text="00:00:00", bg=controls_bg, fg=fg,
            font=("Consolas", 9)
        )
        self.time_current_label.pack(side=tk.LEFT, padx=(0, 6))

        style = ttk.Style()
        style.configure("Player.Horizontal.TScale",
                        background=controls_bg,
                        troughcolor="#1e1e3a" if self.dark_mode else "#cccccc")

        self.seekbar = ttk.Scale(
            seekbar_row, from_=0, to=1000, orient=tk.HORIZONTAL,
            style="Player.Horizontal.TScale",
            command=self._on_seek_changed
        )
        self.seekbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.seekbar.set(0)
        self.seekbar.bind("<ButtonPress-1>", self._on_seek_start)
        self.seekbar.bind("<ButtonRelease-1>", self._on_seek_end)

        self.time_total_label = tk.Label(
            seekbar_row, text="--:--:--", bg=controls_bg, fg=fg,
            font=("Consolas", 9)
        )
        self.time_total_label.pack(side=tk.LEFT, padx=(6, 0))

        # Buttons row
        btn_row = tk.Frame(self.controls, bg=controls_bg)
        btn_row.pack(fill=tk.X, padx=10, pady=(2, 6))

        btn_kw = dict(
            bg="#1e1e3a" if self.dark_mode else "#d0d0d0",
            fg="white" if self.dark_mode else "#333",
            activebackground="#5865F2", activeforeground="white",
            relief="flat", font=("Segoe UI", 12), cursor="hand2",
            width=3, bd=0
        )

        self.play_btn = tk.Button(btn_row, text="▶", command=self.toggle_play, **btn_kw)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 3))

        self.stop_btn = tk.Button(btn_row, text="⏹", command=self.stop, **btn_kw)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Volume
        tk.Label(btn_row, text="🔊", bg=controls_bg, fg=fg,
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 4))

        self.volume_scale = ttk.Scale(
            btn_row, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_volume_changed, length=100,
            style="Player.Horizontal.TScale"
        )
        self.volume_scale.set(self._volume)
        self.volume_scale.pack(side=tk.LEFT, padx=(0, 6))

        self.vol_pct_label = tk.Label(
            btn_row, text=f"{self._volume}%", bg=controls_bg, fg=fg,
            font=("Segoe UI", 9)
        )
        self.vol_pct_label.pack(side=tk.LEFT, padx=(0, 12))

        # LIVE badge
        self._live_badge = tk.Label(
            btn_row, text="● LIVE", bg=controls_bg, fg="#ff4444",
            font=("Segoe UI", 9, "bold")
        )

        # Backend label
        txt = f"[{self._backend_name.upper()}]" if self._backend_name else "[NO PLAYER]"
        self._status_label = tk.Label(
            btn_row, text=txt, bg=controls_bg, fg="#555555",
            font=("Segoe UI", 8)
        )
        self._status_label.pack(side=tk.RIGHT)

    def _show_placeholder(self):
        msg = (
            "🎬  No video player found\n\n"
            "Install mpv (recommended):\n"
            "  winget install mpv\n\n"
            "Or install VLC:\n"
            "  winget install VideoLAN.VLC\n"
            "  pip install python-vlc\n\n"
            "Restart EasyCut after installing."
        )
        tk.Label(
            self.video_frame, text=msg, bg="#000000", fg="#666666",
            font=("Consolas", 10), justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ──────────────────────────────────────
    # Loading Media
    # ──────────────────────────────────────

    def load(self, url: str, is_file: bool = False, live_from_start: bool = False) -> bool:
        """Load media URL into the player
        
        Args:
            url: Media URL or file path
            is_file: True for local file paths
            live_from_start: If True and URL is a live stream, try to load from the beginning
        """
        if not self._backend_name:
            return False
        self.stop()
        self._loaded_url = url
        self._status_label.config(text="Loading...")

        if hasattr(self, '_ready_label'):
            self._ready_label.place_forget()

        if self._backend_name == "mpv":
            return self._load_mpv(url, is_file=is_file, live_from_start=live_from_start)
        elif self._backend_name == "vlc":
            return self._load_vlc(url, is_file)
        return False

    def _load_mpv(self, url: str, is_file: bool = False, live_from_start: bool = False) -> bool:
        """Launch mpv subprocess embedded in Tkinter + IPC pipe"""
        try:
            self.video_frame.update_idletasks()
            wid = str(int(self.video_frame.winfo_id()))

            suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
            self._mpv_pipe_name = rf"\\.\pipe\easycut_mpv_{suffix}"

            cmd = [
                shutil.which("mpv") or "mpv",
                f"--wid={wid}",
                f"--input-ipc-server={self._mpv_pipe_name}",
                "--no-terminal",
                "--no-osc",
                "--keep-open=yes",
                "--idle=no",
                f"--volume={self._volume}",
                "--hwdec=auto",
                "--force-window=no",
            ]

            if is_file:
                # Local files (especially live recordings being written to)
                cmd.extend([
                    "--force-seekable=yes",
                    "--demuxer-max-bytes=500MiB",
                    "--demuxer-readahead-secs=10",
                    "--cache=yes",
                ])
            else:
                # URLs (YouTube, etc.) — use yt-dlp inside mpv
                # Use flexible format chain that works with live MPD manifests
                cmd.extend([
                    "--ytdl=yes",
                    "--ytdl-format=bestvideo[height<=1080][ext!=webm]+bestaudio[ext!=webm]/best[height<=1080][ext!=webm]/bestvideo+bestaudio/best",
                    "--cache=yes",
                    "--demuxer-max-bytes=150MiB",
                ])
                if live_from_start:
                    # Tell yt-dlp to download from the start of the live
                    cmd.append("--ytdl-raw-options=live-from-start=")

            cmd.append(url)

            cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            self._mpv_proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=cflags
            )

            # Connect IPC in background
            def connect():
                handle = _pipe_connect(self._mpv_pipe_name, timeout=12.0)
                if handle and not self._destroyed:
                    self._mpv_pipe_handle = handle
                    self._playing = True
                    self._paused = False
                    self.after(0, lambda: self.play_btn.config(text="⏸"))
                    self.after(0, lambda: self._status_label.config(text="[MPV]"))
                    self.after(0, self._start_update_loop)
                    logger.info("mpv IPC connected")
                elif not self._destroyed:
                    self._playing = True
                    self.after(0, lambda: self._status_label.config(text="[MPV] (no IPC)"))
                    self.after(0, self._start_update_loop)

            threading.Thread(target=connect, daemon=True).start()
            return True

        except Exception as e:
            logger.error(f"mpv launch failed: {e}")
            self._status_label.config(text=f"Error: {e}")
            return False

    def _load_vlc(self, url: str, is_file: bool = False) -> bool:
        """Load with python-vlc"""
        try:
            self.video_frame.update_idletasks()
            if not self._vlc_instance:
                self._vlc_instance = _vlc_module.Instance("--no-xlib", "--quiet",
                                                          "--no-video-title-show")
            if self._vlc_player:
                self._vlc_player.stop()

            self._vlc_player = self._vlc_instance.media_player_new()
            if sys.platform == "win32":
                self._vlc_player.set_hwnd(self.video_frame.winfo_id())

            if not is_file and ("youtube.com" in url or "youtu.be" in url):
                self._status_label.config(text="Extracting stream...")
                threading.Thread(target=self._vlc_youtube_load, args=(url,), daemon=True).start()
                return True

            media = self._vlc_instance.media_new(url)
            self._vlc_player.set_media(media)
            self._vlc_player.audio_set_volume(self._volume)
            self._vlc_player.play()
            self._playing = True
            self._paused = False
            self._start_update_loop()
            self._status_label.config(text="[VLC]")
            return True

        except Exception as e:
            logger.error(f"VLC load failed: {e}")
            self._status_label.config(text=f"Error: {e}")
            return False

    def _vlc_youtube_load(self, youtube_url: str):
        """Extract stream URL for VLC in background"""
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL({'format': 'best[ext=mp4][height<=1080]/best',
                                   'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                stream_url = info.get('url', youtube_url)

            def play():
                if self._destroyed:
                    return
                media = self._vlc_instance.media_new(stream_url)
                self._vlc_player.set_media(media)
                self._vlc_player.audio_set_volume(self._volume)
                self._vlc_player.play()
                self._playing = True
                self._paused = False
                self._start_update_loop()
                self._status_label.config(text="[VLC]")

            self.after(0, play)
        except Exception as e:
            logger.error(f"VLC YouTube extraction: {e}")
            self.after(0, lambda: self._status_label.config(text=f"Error: {e}"))

    # ──────────────────────────────────────
    # mpv IPC
    # ──────────────────────────────────────

    def _mpv_command(self, *args) -> Optional[dict]:
        with self._ipc_lock:
            if not self._mpv_pipe_handle:
                return None
            return _pipe_send(self._mpv_pipe_handle, {"command": list(args)})

    def _mpv_get_property(self, name: str):
        resp = self._mpv_command("get_property", name)
        if resp and resp.get("error") == "success":
            return resp.get("data")
        return None

    def _mpv_set_property(self, name: str, value):
        return self._mpv_command("set_property", name, value)

    # ──────────────────────────────────────
    # Playback Controls
    # ──────────────────────────────────────

    def play(self):
        if self._backend_name == "mpv" and self._mpv_pipe_handle:
            self._mpv_set_property("pause", False)
        elif self._backend_name == "vlc" and self._vlc_player:
            self._vlc_player.play()
        self._playing = True
        self._paused = False
        self.play_btn.config(text="⏸")

    def pause(self):
        if self._backend_name == "mpv" and self._mpv_pipe_handle:
            self._mpv_set_property("pause", True)
        elif self._backend_name == "vlc" and self._vlc_player:
            self._vlc_player.pause()
        self._paused = True
        self.play_btn.config(text="▶")

    def toggle_play(self):
        if self._paused or not self._playing:
            self.play()
        else:
            self.pause()

    def stop(self):
        if self._backend_name == "mpv":
            self._stop_mpv()
        elif self._backend_name == "vlc" and self._vlc_player:
            try:
                self._vlc_player.stop()
            except Exception:
                pass

        self._playing = False
        self._paused = False
        self._current_time = 0.0
        self._duration = 0.0
        self._loaded_url = None
        try:
            self.play_btn.config(text="▶")
            self.seekbar.set(0)
            self.time_current_label.config(text="00:00:00")
            self.time_total_label.config(text="--:--:--")
            self._live_badge.pack_forget()
        except tk.TclError:
            pass

    def _stop_mpv(self):
        with self._ipc_lock:
            if self._mpv_pipe_handle:
                try:
                    _pipe_send(self._mpv_pipe_handle, {"command": ["quit"]})
                except Exception:
                    pass
                _pipe_close(self._mpv_pipe_handle)
                self._mpv_pipe_handle = None

        if self._mpv_proc:
            try:
                self._mpv_proc.terminate()
                self._mpv_proc.wait(timeout=3)
            except Exception:
                try:
                    self._mpv_proc.kill()
                except Exception:
                    pass
            self._mpv_proc = None

    def get_time(self) -> float:
        """Get current playback position in seconds"""
        try:
            if self._backend_name == "mpv":
                t = self._mpv_get_property("time-pos")
                return float(t) if t is not None else self._current_time
            elif self._backend_name == "vlc" and self._vlc_player:
                t = self._vlc_player.get_time()
                return t / 1000.0 if t and t > 0 else 0.0
        except Exception:
            pass
        return self._current_time

    def get_duration(self) -> float:
        """Get total duration (0 for live streams)"""
        try:
            if self._backend_name == "mpv":
                d = self._mpv_get_property("duration")
                return float(d) if d is not None else 0.0
            elif self._backend_name == "vlc" and self._vlc_player:
                d = self._vlc_player.get_length()
                return d / 1000.0 if d and d > 0 else 0.0
        except Exception:
            pass
        return 0.0

    def seek(self, seconds: float):
        """Seek to absolute position in seconds"""
        try:
            if self._backend_name == "mpv":
                self._mpv_command("seek", seconds, "absolute")
            elif self._backend_name == "vlc" and self._vlc_player:
                self._vlc_player.set_time(int(seconds * 1000))
        except Exception as e:
            logger.debug(f"Seek failed: {e}")

    def set_volume(self, volume: int):
        self._volume = max(0, min(100, volume))
        try:
            if self._backend_name == "mpv":
                self._mpv_set_property("volume", self._volume)
            elif self._backend_name == "vlc" and self._vlc_player:
                self._vlc_player.audio_set_volume(self._volume)
        except Exception:
            pass

    @property
    def is_playing(self) -> bool:
        return self._playing and not self._paused

    @property
    def is_loaded(self) -> bool:
        return self._loaded_url is not None and self._playing

    @property
    def backend(self) -> Optional[str]:
        return self._backend_name

    # ──────────────────────────────────────
    # Seekbar / Volume
    # ──────────────────────────────────────

    def _on_seek_start(self, event):
        self._seeking = True

    def _on_seek_end(self, event):
        self._seeking = False
        if self._duration > 0:
            target = (float(self.seekbar.get()) / 1000.0) * self._duration
            self.seek(target)

    def _on_seek_changed(self, value):
        if self._seeking and self._duration > 0 and hasattr(self, 'time_current_label'):
            target = (float(value) / 1000.0) * self._duration
            self.time_current_label.config(text=self._format_time(target))

    def _on_volume_changed(self, value):
        vol = int(float(value))
        self._volume = vol
        if hasattr(self, 'vol_pct_label'):
            self.vol_pct_label.config(text=f"{vol}%")
        self.set_volume(vol)

    # ──────────────────────────────────────
    # Update Loop
    # ──────────────────────────────────────

    def _start_update_loop(self):
        if self._update_running:
            return
        self._update_running = True
        self._do_update()

    def _do_update(self):
        if self._destroyed:
            return
        if not self._playing and not self._paused:
            self._update_running = False
            return

        # Fetch time in background to avoid blocking UI on IPC
        def fetch():
            if self._destroyed:
                return
            cur = self.get_time()
            dur = self.get_duration()
            if not self._destroyed:
                self.after(0, lambda: self._apply_update(cur, dur))

        threading.Thread(target=fetch, daemon=True).start()

        # Check mpv process alive
        if self._backend_name == "mpv" and self._mpv_proc:
            if self._mpv_proc.poll() is not None:
                self._playing = False
                self._update_running = False
                self.after(0, lambda: self._status_label.config(text="[MPV] Ended"))
                return

        if self._playing or self._paused:
            self.after(800, self._do_update)
        else:
            self._update_running = False

    def _apply_update(self, current: float, duration: float):
        if self._destroyed:
            return
        try:
            self._current_time = current
            self._duration = duration
            self.time_current_label.config(text=self._format_time(current))

            if duration > 0:
                self.time_total_label.config(text=self._format_time(duration))
                self._live_badge.pack_forget()
                if not self._seeking:
                    self.seekbar.set((current / duration) * 1000)
            else:
                self.time_total_label.config(text="LIVE")
                if not self._live_badge.winfo_ismapped():
                    self._live_badge.pack(side=tk.RIGHT, padx=(0, 8))

            if self.on_time_update:
                self.on_time_update(current)
        except tk.TclError:
            pass

    # ──────────────────────────────────────
    # Utility
    # ──────────────────────────────────────

    @staticmethod
    def _format_time(seconds: float) -> str:
        if seconds is None or seconds < 0:
            return "00:00:00"
        s = int(seconds)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{sec:02d}"

    def load_file(self, filepath: str):
        return self.load(filepath, is_file=True)

    def load_recording(self, output_dir: str, delay: float = 8.0):
        """Auto-detect and load newest recording file after delay.
        
        Waits for the file to have enough data (>500KB) before loading,
        retrying up to 6 times with 3-second intervals.
        """
        def _delayed():
            time.sleep(delay)
            if self._destroyed:
                return
            out = Path(output_dir)
            exts = {'.mp4', '.mkv', '.ts', '.flv', '.part'}

            # Try multiple times to find a file with enough data
            for attempt in range(6):
                if self._destroyed:
                    return
                files = []
                for ext in exts:
                    files.extend(out.glob(f"*{ext}"))
                if files:
                    newest = max(files, key=lambda f: f.stat().st_mtime)
                    try:
                        size = newest.stat().st_size
                    except OSError:
                        size = 0
                    if size > 500_000:  # At least 500KB
                        logger.info(f"Auto-loading live recording: {newest.name} ({size/1e6:.1f}MB)")
                        self.after(0, lambda f=str(newest): self.load(f, is_file=True))
                        return
                time.sleep(3)

            # Fallback: load whatever we found
            files = []
            for ext in exts:
                files.extend(out.glob(f"*{ext}"))
            if files:
                newest = max(files, key=lambda f: f.stat().st_mtime)
                logger.info(f"Auto-loading (small file): {newest.name}")
                self.after(0, lambda f=str(newest): self.load(f, is_file=True))

        threading.Thread(target=_delayed, daemon=True).start()

    def seek_to_end(self):
        """Seek to the end of the current media (for returning to live edge).
        
        For growing files (live recordings), seeks to near the end.
        For live streams (duration=0), sends mpv the 'seek 100 absolute-percent' cmd.
        """
        if self._backend_name == "mpv" and self._mpv_pipe_handle:
            # Use percent-based seek to jump to end regardless of duration
            self._mpv_command("seek", 100, "absolute-percent")
            return
        
        dur = self.get_duration()
        if dur > 3:
            self.seek(dur - 1)
        elif self._current_time > 0:
            # Duration unknown/stale — seek to a very large value
            # mpv will cap this to the actual end of available data
            self.seek(99999)

    # ──────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────

    def cleanup(self):
        self._destroyed = True
        self._update_running = False
        self._playing = False
        self._stop_mpv()

        if self._vlc_player:
            try:
                self._vlc_player.stop()
                self._vlc_player.release()
            except Exception:
                pass
            self._vlc_player = None

        if self._vlc_instance:
            try:
                self._vlc_instance.release()
            except Exception:
                pass
            self._vlc_instance = None

    def destroy(self):
        self.cleanup()
        super().destroy()
