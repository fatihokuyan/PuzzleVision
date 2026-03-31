"""
categories_menu.py
==================
"SERGİLERİMİZ" categories grid screen.
"""

from __future__ import annotations

import os
from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QPushButton, QLabel, QSizePolicy,
)

from src.config import CATEGORIES, Paths, UISettings
from src.ui import styles


class CategoriesMenuScreen(QWidget):
    """Scrollable grid of category cards.

    Parameters
    ----------
    on_category : Callable[[str], None]
        Called with the category name when a card is tapped.
    on_back : Callable
        Called when the user taps ANA MENÜ.
    button_registry : list[QPushButton]
        Global button list owned by the main window.
    text_label_registry : list[QLabel]
        List to which category text labels are appended (for glow effect).
    """

    def __init__(
        self,
        on_category: Callable[[str], None],
        on_back:     Callable[[], None],
        button_registry:     list,
        text_label_registry: list,
    ) -> None:
        super().__init__()
        self._build(on_category, on_back, button_registry, text_label_registry)

    # ------------------------------------------------------------------

    def _build(self, on_category, on_back, registry, text_registry) -> None:
        bg = Paths.GAME_BACKGROUND
        if os.path.exists(bg):
            self.setStyleSheet(styles.TRANSPARENT_BG)
        else:
            self.setStyleSheet(styles.GRADIENT_BG)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 5)

        # Title
        title = QLabel(
            "<html><head><style>* { font-family: 'Segoe UI'; }</style></head><body>"
            "<div style='font-size: 28pt; font-weight: bold;'>SERGİLERİMİZ</div>"
            "</body></html>"
        )
        title.setTextFormat(Qt.RichText)
        title.setAlignment(Qt.AlignCenter)
        title.setMinimumHeight(70)
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        title.setStyleSheet(styles.TITLE_LABEL)

        # Category grid
        btn_container = QWidget()
        grid = QGridLayout(btn_container)
        grid.setSpacing(15)

        row, col = 0, 0
        for cat_name, cat_data in CATEGORIES.items():
            btn = self._make_category_button(cat_name, cat_data, on_category, text_registry)
            registry.append(btn)

            if cat_name == "Konya Bilim Merkezi":
                if col != 0:
                    row += 1
                    col = 0
                grid.addWidget(btn, row, 0)
                row += 1
                col = 0
            else:
                grid.addWidget(btn, row, col)
                col += 1
                if col == 4:
                    col = 0
                    row += 1

        scroll = QScrollArea()
        scroll.setWidget(btn_container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(styles.SCROLL_AREA)

        # Back button
        back_btn = QPushButton("ANA MENÜ")
        back_btn.setFixedSize(420, 80)
        back_btn.setFont(QFont(UISettings.FONT_FAMILY, 20, QFont.Bold))
        back_btn.setStyleSheet(styles.BTN_BACK)
        back_btn.clicked.connect(on_back)
        registry.append(back_btn)

        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        layout.setStretchFactor(title,  1)
        layout.setStretchFactor(scroll, 12)
        layout.setStretchFactor(back_btn, 0)

        # Apply static glow to text labels
        for lbl in text_registry:
            lbl.setStyleSheet(styles.CATEGORY_TEXT_LABEL)

    # ------------------------------------------------------------------

    def _make_category_button(self, name, data, on_category, text_registry) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(280, 280)
        btn.setStyleSheet(styles.BTN_CATEGORY_CARD)

        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setContentsMargins(10, 10, 10, 10)
        btn_layout.setSpacing(10)

        # Image container
        img_container = QWidget()
        img_container.setFixedSize(240, 200)
        img_container.setStyleSheet(styles.IMG_CONTAINER)
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(5, 5, 5, 5)

        img_label = QLabel()
        img_label.setFixedSize(230, 190)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("QLabel { background: transparent; border-radius: 12px; padding: 0px; }")

        raw_px = QPixmap(data.get("image", ""))
        if not raw_px.isNull():
            final = QPixmap(230, 190)
            final.fill(Qt.transparent)
            if raw_px.width() / raw_px.height() > 230 / 190:
                scaled = raw_px.scaledToWidth(230, Qt.SmoothTransformation)
                y_pos  = (190 - scaled.height()) // 2
                p = QPainter(final); p.drawPixmap(0, y_pos, scaled); p.end()
            else:
                scaled = raw_px.scaledToHeight(190, Qt.SmoothTransformation)
                x_pos  = (230 - scaled.width()) // 2
                p = QPainter(final); p.drawPixmap(x_pos, 0, scaled); p.end()
            img_label.setPixmap(final)

        img_layout.addWidget(img_label)

        # Text label
        text_label = QLabel(name)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setFont(QFont(UISettings.FONT_FAMILY, 18, QFont.Bold))
        text_label.setStyleSheet(styles.CATEGORY_TEXT_LABEL)
        text_label.setWordWrap(True)
        text_registry.append(text_label)

        btn_layout.addWidget(img_container)
        btn_layout.addWidget(text_label)
        btn.setLayout(btn_layout)

        btn.clicked.connect(lambda _, n=name: on_category(n))
        return btn
