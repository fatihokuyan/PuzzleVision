"""
config.py
=========
Central configuration module for PuzzleVision.

All hardcoded paths, game constants, and UI settings are defined here.
Changing a value in this file propagates throughout the entire application.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base Directories
# ---------------------------------------------------------------------------

# Project root is the parent of the `src` directory
BASE_DIR = Path(__file__).resolve().parent.parent

ICON_IMAGES_DIR   = BASE_DIR / "icon_images"
PUZZLE_IMAGES_DIR = BASE_DIR / "puzzle_images"
PUZZLE_SOUNDS_DIR = BASE_DIR / "puzzle_sounds"
PUZZLE_VIDEOS_DIR = BASE_DIR / "puzzle_videos"
SERGI_IMAGES_DIR  = BASE_DIR / "sergi_images"

# ---------------------------------------------------------------------------
# Resource Paths
# ---------------------------------------------------------------------------

class Paths:
    """Static container for all file paths used by the application."""

    # Backgrounds
    MAIN_BACKGROUND   = str(ICON_IMAGES_DIR / "mainandtwoscreen.png")
    GAME_BACKGROUND   = str(ICON_IMAGES_DIR / "background.png")
    SECOND_SCREEN_BG  = str(ICON_IMAGES_DIR / "two_screen.png")

    # Icons & assets
    LOCK_ICON         = str(ICON_IMAGES_DIR / "lock_icon.png")
    PUZZLE_ICON       = str(ICON_IMAGES_DIR / "puzzle_pieces.png")
    LOADING_GIF       = str(ICON_IMAGES_DIR / "loading.gif")

    # Executables
    FFPLAY_EXE        = str(BASE_DIR / "ffplay.exe")

    # Sound files (without extension – SoundManager appends ".wav")
    SOUND_NAMES = ["pick", "drop", "correct", "complete", "start"]


# ---------------------------------------------------------------------------
# Game Settings
# ---------------------------------------------------------------------------

class GameSettings:
    """Puzzle game engine constants."""

    PUZZLE_SIZE             = 4          # Grid dimension (4×4)
    SCALE_PERCENT           = 30         # Image resize percent
    TIME_LIMIT_SECONDS      = 200        # Per-puzzle time limit

    PINCH_THRESHOLD         = 40         # Pixels – finger distance to detect pinch
    PINCH_RELEASE_THRESHOLD = 70         # Pixels – finger distance to release
    SNAP_THRESHOLD          = 70         # Pixels – magnetic snap distance
    SMOOTHING_FACTOR        = 0.5        # Piece drag smoothing (0-1)

    PICK_RANGE              = 60         # Pixels – grab radius around piece centre
    SOUND_COOLDOWN          = 0.2        # Seconds between same-sound plays
    FRAME_RATE              = 60         # Target game loop FPS

    # MediaPipe hand tracking
    MAX_HANDS               = 2
    DETECTION_CONFIDENCE    = 0.6
    TRACKING_CONFIDENCE     = 0.4
    MODEL_COMPLEXITY        = 0

    # Frame resolution fed to the game window
    FRAME_WIDTH             = 1280
    FRAME_HEIGHT            = 720

    # Thumbnail resolution fed to MediaPipe (reduces CPU load)
    MEDIAPIPE_WIDTH         = 240
    MEDIAPIPE_HEIGHT        = 180

    # Completion transition durations (seconds)
    TRANSITION_SHOW_ORIGINAL  = 1.0
    TRANSITION_FADE_FULLSCREEN = 1.0
    TRANSITION_SHOW_FULLSCREEN = 1.0

    # Video fade-in duration (seconds)
    VIDEO_FADE_IN_DURATION    = 6.0


# ---------------------------------------------------------------------------
# Camera Settings
# ---------------------------------------------------------------------------

class CameraSettings:
    """OpenCV camera initialisation parameters."""

    INDEX       = 0
    WIDTH       = 1280
    HEIGHT      = 720
    FPS         = 60
    FOURCC      = "MJPG"
    BUFFER_SIZE = 1


# ---------------------------------------------------------------------------
# UI Settings
# ---------------------------------------------------------------------------

class UISettings:
    """PyQt5 interface constants."""

    WINDOW_WIDTH  = 1920
    WINDOW_HEIGHT = 1080

    # Inactivity timeout before returning to main menu (ms)
    INACTIVITY_TIMEOUT_MS = 20_000

    # Page transition fade duration (ms)
    FADE_DURATION_MS = 350

    # Loading screen timers (ms)
    LOADING_TOTAL_MS      = 3_000
    LOADING_EARLY_PREP_MS = 1_500

    # Admin password
    ADMIN_PASSWORD   = "2001"
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_SECONDS  = 30

    # Fonts
    FONT_FAMILY = "Segoe UI"


# ---------------------------------------------------------------------------
# Category Definitions
# ---------------------------------------------------------------------------

def _cat(folder: str, sergi_img: str, puzzles: list[dict]) -> dict:
    """Helper to build a category entry with absolute paths."""
    return {
        "image": str(SERGI_IMAGES_DIR / sergi_img),
        "puzzles": [
            {
                "image": str(PUZZLE_IMAGES_DIR / folder / p["image"]),
                "video": str(PUZZLE_VIDEOS_DIR / folder / p["video"]),
            }
            for p in puzzles
        ],
    }


CATEGORIES: dict[str, dict] = {
    "Vücudumuz": _cat(
        "vucudumuz", "vucudumuz.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Evrenimiz": _cat(
        "evrenimiz", "evrenimiz.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Temel Adımlar": _cat(
        "temel_adimlar", "temel_adimlar.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "İslam Bilim Tarihi": _cat(
        "islam_bilim", "islam_bilim.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Dünyamız": _cat(
        "dunyamiz", "dunyamiz.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Yeni Ufuklar": _cat(
        "yeni_ufuklar", "yeni_ufuklar.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Keşif Yolu": _cat(
        "kesif_yolu", "kesif_yolu.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Sözcüklerin Serüveni": _cat(
        "sozcukler", "sozcukler.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
            {"image": "puzzle2.jpg", "video": "video2.mp4"},
        ],
    ),
    "Konya Bilim Merkezi": _cat(
        "konya_bilim", "konya_bilim.png",
        [
            {"image": "puzzle1.jpg", "video": "video1.mp4"},
        ],
    ),
}
