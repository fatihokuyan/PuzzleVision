"""
hint_dialog.py
==============
How-to-play / hint dialog extracted from the monolithic file.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout,
    QPushButton, QLabel, QScrollArea,
    QGraphicsDropShadowEffect,
)

from src.config import UISettings
from src.ui import styles

_SECTIONS = [
    {
        "title": "🖥️ Puzzle Nasıl Başlatılır?",
        "items": [
            "1️- Ana menüden 'BAŞLA' butonuna tıklayın",
            "2- İlgilendiğiniz sergiyi seçin",
            "3- Puzzle kartlarından birini seçin",
            "4- 'PUZZLE'I BAŞLAT' butonuna tıklayın",
            "5- Puzzle ekranında eğlenerek öğrenmeye başlayın!",
        ],
    },
    {
        "title": "🎮 Nasıl Oynanır?",
        "items": [
            "👉 Parçaları tutmak için başparmak ve işaret parmağını birleştirin",
            "👋 Bırakmak için parmaklarınızı açın",
            "🔄 Parçaları kenarlardan alıp merkeze doğru yerleştirin",
            "✨ Doğru yere yaklaştığınızda manyetik etki ile yerleşecektir",
        ],
    },
    {
        "title": "🎯 Oyun Kuralları",
        "items": [
            "⏱️ Verilen süre içinde puzzle'ı tamamlamaya çalışın",
            "💚 Yeşil çerçeve doğru yerleştirmeyi gösterir",
            "💔 Kırmızı çerçeve yanlış yerleştirmeyi gösterir",
        ],
    },
    {
        "title": "🎁 Ödül",
        "items": [
            "🎉 Puzzle'ı tamamladığınızda kutlama videosu başlayacak",
            "🌟 Her puzzle size yeni bir deneyim kazandıracak",
            "🔥 Hızlı olun, süreniz kısıtlı!",
            "🎨 Eğlenceli ve öğretici bir deneyime hazır olun",
        ],
    },
]


class HintDialog(QDialog):
    """Scrollable how-to-play guide dialog."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nasıl Oynanır?")
        self.setFixedSize(600, 700)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Touch-scroll state
        self._scrolling      = False
        self._last_y: int    = 0
        self._scroll_area: QScrollArea | None = None
        self._drag_pos       = QPoint()

        self._build_ui()

    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        bg = QWidget()
        bg.setObjectName("bgWidget")
        bg.setStyleSheet(styles.DIALOG_BG_DARK)

        bg_layout = QVBoxLayout(bg)
        bg_layout.setSpacing(20)
        bg_layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("PuzzleVision - Oyun Rehberi")
        title.setFont(QFont(UISettings.FONT_FAMILY, 24, QFont.Bold))
        title.setStyleSheet("""
            color: white;
            padding: 10px;
            background: rgba(52,152,219,0.2);
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)

        # Content
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: rgba(52,152,219,0.2);
                border-radius: 15px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(20, 20, 20, 20)

        for section in _SECTIONS:
            sec_title = QLabel(section["title"])
            sec_title.setFont(QFont(UISettings.FONT_FAMILY, 16, QFont.Bold))
            sec_title.setStyleSheet("""
                color: white;
                padding: 5px;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            """)
            content_layout.addWidget(sec_title)

            for item_text in section["items"]:
                item = QLabel(item_text)
                item.setFont(QFont(UISettings.FONT_FAMILY, 12))
                item.setStyleSheet("""
                    color: white;
                    padding: 8px 15px;
                    background: transparent;
                    border: none;
                    margin: 2px;
                """)
                item.setWordWrap(True)
                content_layout.addWidget(item)

            content_layout.addSpacing(15)

        # Scroll area
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidget(content_widget)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setStyleSheet(styles.SCROLL_AREA)

        # Close button
        close_btn = QPushButton("KAPAT")
        close_btn.setFixedSize(200, 50)
        close_btn.setFont(QFont(UISettings.FONT_FAMILY, 12, QFont.Bold))
        close_btn.setStyleSheet(styles.BTN_HINT_CLOSE)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 100))
        bg.setGraphicsEffect(shadow)

        bg_layout.addWidget(title)
        bg_layout.addWidget(self._scroll_area)
        bg_layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        layout.addWidget(bg)
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Touch-scroll support
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._scroll_area:
            rel_pos = event.pos() - self._scroll_area.pos()
            if self._scroll_area.rect().contains(rel_pos):
                self._scrolling = True
                self._last_y    = event.pos().y()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._scrolling and event.buttons() == Qt.LeftButton and self._scroll_area:
            delta = self._last_y - event.pos().y()
            self._last_y = event.pos().y()
            vbar = self._scroll_area.verticalScrollBar()
            vbar.setValue(vbar.value() + delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._scrolling = False
        super().mouseReleaseEvent(event)
