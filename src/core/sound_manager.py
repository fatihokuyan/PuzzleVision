"""
sound_manager.py
================
Manages all in-game sound effects via pygame.mixer.

Responsibilities
----------------
* Load .wav files once at construction time.
* Play sounds with a per-sound cooldown to avoid audio spam.
* Clean up pygame mixer on close().

Usage
-----
    sm = SoundManager()
    sm.play("pick")
    ...
    sm.close()
"""

from __future__ import annotations

import time
from pathlib import Path

import pygame

from src.config import Paths, GameSettings


class SoundManager:
    """Loads and plays puzzle sound effects with cooldown protection."""

    SOUND_NAMES = Paths.SOUND_NAMES  # ["pick", "drop", "correct", "complete", "start"]

    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound | None] = {
            name: None for name in self.SOUND_NAMES
        }
        self._cooldowns: dict[str, float] = {name: 0.0 for name in self.SOUND_NAMES}
        self._cooldown_secs = GameSettings.SOUND_COOLDOWN

        self._init_mixer()
        self._load_sounds()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_mixer(self) -> None:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(32)
        except Exception as exc:
            print(f"SoundManager: mixer init failed – {exc}")

    def _load_sounds(self) -> None:
        sound_dir = Path(Paths.PUZZLE_SOUNDS_DIR) if hasattr(Paths, "PUZZLE_SOUNDS_DIR") else None

        # Paths.PUZZLE_SOUNDS_DIR is not defined as a class attribute —
        # we reference the module-level variable instead.
        from src.config import PUZZLE_SOUNDS_DIR
        sound_dir = Path(PUZZLE_SOUNDS_DIR)

        if not sound_dir.exists():
            print(f"SoundManager: sound directory not found – {sound_dir}")
            return

        for name in self.SOUND_NAMES:
            path = sound_dir / f"{name}.wav"
            if path.exists():
                try:
                    self._sounds[name] = pygame.mixer.Sound(str(path))
                except Exception as exc:
                    print(f"SoundManager: could not load '{name}' – {exc}")
            else:
                print(f"SoundManager: file missing – {path}")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def play(self, name: str) -> None:
        """Play *name* sound if it is loaded and the cooldown has expired."""
        sound = self._sounds.get(name)
        if sound is None:
            return

        now = time.time()
        if now <= self._cooldowns[name]:
            return  # Still in cooldown

        try:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
                self._cooldowns[name] = now + self._cooldown_secs
        except Exception as exc:
            print(f"SoundManager: play('{name}') failed – {exc}")

    def close(self) -> None:
        """Shut down pygame mixer and pygame itself."""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            if pygame.get_init():
                pygame.quit()
        except Exception as exc:
            print(f"SoundManager: close() error – {exc}")
