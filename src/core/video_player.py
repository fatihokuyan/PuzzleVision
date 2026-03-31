"""
video_player.py
===============
Manages ffplay subprocess-based video playback.

Responsibilities
----------------
* Launch ffplay with the correct screen geometry and fade-in filter.
* Poll for completion while keeping the Qt event loop alive.
* Forcefully terminate the subprocess when requested.
* Notify the caller (via callback) when playback ends.

Design note
-----------
Video playback is inherently blocking because ffplay is a separate process.
The ``play()`` method loops until the process exits, calling
``QApplication.processEvents()`` every iteration so the Qt UI stays
responsive.
"""

from __future__ import annotations

import os
import subprocess
import time
from typing import Callable

import keyboard
from PyQt5.QtWidgets import QApplication

from src.config import Paths, GameSettings


class VideoPlayer:
    """Plays a video file using the bundled ffplay.exe.

    Parameters
    ----------
    on_finished:
        Callable invoked (with ``success: bool``) when playback ends
        or is forcefully stopped.
    """

    def __init__(self, on_finished: Callable[[bool], None] | None = None) -> None:
        self._process: subprocess.Popen | None = None
        self._on_finished = on_finished
        self._active = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def play(
        self,
        video_path: str,
        x: int = 0,
        y: int = 0,
        width: int = 1920,
        height: int = 1080,
    ) -> bool:
        """Start ffplay and block until it exits or is cancelled.

        Returns ``True`` if the video finished normally, ``False`` otherwise.
        """
        if not self._validate_assets(video_path):
            self._notify(False)
            return False

        self._active = True
        fade_filter = f"fade=in:0:{int(GameSettings.VIDEO_FADE_IN_DURATION * 25)}"

        cmd = [
            Paths.FFPLAY_EXE,
            "-fs",
            "-autoexit",
            "-noborder",
            "-alwaysontop",
            "-window_title", "Video Player",
            "-loglevel", "quiet",
            "-vf", fade_filter,
            "-x", str(width),
            "-y", str(height),
            "-left", str(x),
            "-top", str(y),
            video_path,
        ]

        print(f"VideoPlayer: starting – {video_path}")
        try:
            self._process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except Exception as exc:
            print(f"VideoPlayer: could not launch ffplay – {exc}")
            self._active = False
            self._notify(False)
            return False

        success = self._wait_for_completion()
        self._process = None
        self._active = False
        self._notify(success)
        return success

    def stop(self) -> None:
        """Forcefully terminate the running process."""
        if self._process is None:
            return
        print(f"VideoPlayer: terminating PID {self._process.pid}")
        try:
            self._process.terminate()
            try:
                self._process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        except Exception as exc:
            print(f"VideoPlayer: stop() error – {exc}")
        self._process = None
        self._active = False

    @property
    def is_playing(self) -> bool:
        return self._process is not None and self._process.poll() is None

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _validate_assets(self, video_path: str) -> bool:
        if not os.path.exists(Paths.FFPLAY_EXE):
            print("VideoPlayer: ffplay.exe not found.")
            return False
        if not os.path.exists(video_path):
            print(f"VideoPlayer: video not found – {video_path}")
            return False
        return True

    def _wait_for_completion(self) -> bool:
        """Poll the subprocess while pumping Qt events. Returns True on clean exit."""
        check_interval = 0.1
        while True:
            QApplication.processEvents()

            if self._process and self._process.poll() is not None:
                return True  # ffplay exited on its own
            if not self._process:
                return False  # was stopped externally
            if not self._active:
                self.stop()
                return False

            if keyboard.is_pressed("esc"):
                print("VideoPlayer: ESC pressed – stopping.")
                self.stop()
                return False

            time.sleep(check_interval)

    def _notify(self, success: bool) -> None:
        if self._on_finished:
            try:
                self._on_finished(success)
            except Exception as exc:
                print(f"VideoPlayer: on_finished callback error – {exc}")
