"""
app.py
======
Application bootstrap.

Handles:
  - High-DPI policy
  - Qt style attributes
  - Main window instantiation and fullscreen positioning
  - Application event loop
"""

from __future__ import annotations

import sys
import os

# PyQt5 must be imported before any other application code to ensure
# proper initialisation order.
# IMPORTANT: Mediapipe MUST be imported before cv2 or PyQt5 on Windows to prevent DLL load failures.
import mediapipe as mp

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.ui.main_window import PuzzleVision


def main() -> int:
    """Bootstrap the PuzzleVision application.  Returns the exit code."""

    # ---- High-DPI scaling ----
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # ---- Main window ----
    window = PuzzleVision()
    window.show()
    window.showFullScreen()

    return app.exec_()
