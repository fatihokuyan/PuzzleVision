"""
puzzle_card.py
==============
Reusable puzzle-card widget used in the category detail page.

Extracted from PuzzleVision.create_puzzle_card().
"""

from __future__ import annotations

import os
from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)

from src.config import UISettings
from src.ui import styles


class PuzzleCard(QWidget):
    """Card widget displaying a puzzle preview image and a start button.

    Parameters
    ----------
    puzzle_data : dict
        Must contain ``"image"`` and ``"video"`` keys (absolute paths).
    category_name : str
        Used by the on_start callback to identify the session.
    on_start : Callable[[str, str, str], None]
        Called with (category_name, image_path, video_path) when the user
        presses "PUZZLE'I BAŞLAT".
    """

    def __init__(
        self,
        puzzle_data: dict,
        category_name: str,
        on_start: Callable[[str, str, str], None],
    ) -> None:
        super().__init__()
        self.setStyleSheet("background: transparent;")

        image_path = puzzle_data.get("image", "")
        video_path = puzzle_data.get("video", "")
        image_exists = self._image_exists(image_path)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Image frame
        img_frame = self._build_image_frame(image_path, image_exists)
        layout.addWidget(img_frame, alignment=Qt.AlignCenter)

        # Start button
        start_btn = self._build_start_button(
            image_exists, category_name, image_path, video_path, on_start
        )
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

    # ------------------------------------------------------------------

    @staticmethod
    def _image_exists(path: str) -> bool:
        return bool(path) and os.path.exists(path)

    def _build_image_frame(self, image_path: str, image_exists: bool) -> QLabel:
        frame = QLabel()
        frame.setFixedSize(770, 480)
        frame.setStyleSheet(styles.PUZZLE_CARD_IMG_FRAME)
        frame.setAlignment(Qt.AlignCenter)

        if image_exists:
            raw_px = QPixmap(image_path)
            if not raw_px.isNull():
                scaled = raw_px.scaled(750, 460, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                final  = QPixmap(770, 480)
                final.fill(Qt.transparent)
                x_off  = (770 - scaled.width())  // 2
                y_off  = (480 - scaled.height()) // 2
                painter = QPainter(final)
                painter.drawPixmap(x_off, y_off, scaled)
                painter.end()
                frame.setPixmap(final)
        else:
            warn_layout = QVBoxLayout(frame)
            warn_layout.setAlignment(Qt.AlignCenter)
            warn = QLabel("Görsel Bulunamadı")
            warn.setFont(QFont(UISettings.FONT_FAMILY, 24))
            warn.setStyleSheet("color: white; background: transparent; font-weight: bold; margin-top: 180px;")
            warn.setAlignment(Qt.AlignCenter)
            warn_layout.addWidget(warn)

        return frame

    def _build_start_button(
        self,
        image_exists: bool,
        category_name: str,
        image_path: str,
        video_path: str,
        on_start: Callable,
    ) -> QPushButton:
        btn = QPushButton("PUZZLE'I BAŞLAT")
        btn.setFixedSize(380, 100)
        btn.setFont(QFont(UISettings.FONT_FAMILY, 18, QFont.Bold))
        btn.setStyleSheet(styles.BTN_PUZZLE_START)
        btn.setProperty("has_image", image_exists)

        if image_exists:
            btn.clicked.connect(
                lambda: on_start(category_name, image_path, video_path)
            )
        else:
            btn.setEnabled(False)

        return btn
