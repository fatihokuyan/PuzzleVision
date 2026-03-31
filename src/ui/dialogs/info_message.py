"""
info_message.py
===============
Non-modal informational overlay shown when a puzzle starts.

Previously inlined as show_info_message() inside PuzzleVision.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QLabel,
)

from src.config import UISettings
from src.ui import styles


class InfoMessageDialog(QDialog):
    """Semi-transparent floating tip shown on the kiosk screen at game start."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(False)
        self.setFixedSize(600, 240)
        self._build_ui()

    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setObjectName("infoMessageWidget")
        widget.setStyleSheet(styles.INFO_MESSAGE_WIDGET)

        inner = QVBoxLayout(widget)
        inner.setContentsMargins(24, 18, 24, 18)
        inner.setSpacing(15)

        title = QLabel("OYUN BAŞLIYOR!")
        title.setFont(QFont(UISettings.FONT_FAMILY, 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        content_html = (
            "Lütfen ikinci ekrana bakın. Puzzle parçalarını el hareketlerinizle "
            "sürükleyerek doğru yerlere yerleştirin."
            "<br><br>"
            "<font color='#ffe082'><i>İpucu: Bir parçayı tutmak için başparmak "
            "ve işaret parmağınızı birleştirin, bırakmak için açın.</i></font>"
        )
        content = QLabel(content_html)
        content.setFont(QFont(UISettings.FONT_FAMILY, 14))
        content.setAlignment(Qt.AlignCenter)
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)

        inner.addWidget(title)
        inner.addWidget(content)

        outer.addWidget(widget)
        self.setLayout(outer)

    def position_on_screen(self, screen_geometry) -> None:
        """Centre horizontally and place near the bottom of *screen_geometry*."""
        x = (screen_geometry.width()  - self.width())  // 2
        y = int(screen_geometry.height() * 0.80) - self.height() // 2
        self.move(x, y)
