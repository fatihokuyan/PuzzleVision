"""
category_page.py
================
Detail page showing puzzle cards for a single category.
"""

from __future__ import annotations

import os
from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QSizePolicy,
)

from src.config import CATEGORIES, UISettings, Paths
from src.ui import styles
from src.ui.widgets.puzzle_card import PuzzleCard


class CategoryPageScreen(QWidget):
    """Horizontal scroll of PuzzleCard widgets for the selected category.

    Parameters
    ----------
    category_name : str
    on_start_puzzle : Callable[[str,str,str],None]
        Called with (category_name, image_path, video_path).
    on_back : Callable
        Called when the user taps GERİ.
    button_registry : list[QPushButton]
    """

    def __init__(
        self,
        category_name: str,
        on_start_puzzle: Callable[[str, str, str], None],
        on_back: Callable[[], None],
        button_registry: list,
    ) -> None:
        super().__init__()
        self._build(category_name, on_start_puzzle, on_back, button_registry)

    # ------------------------------------------------------------------

    def _build(self, category_name, on_start_puzzle, on_back, registry) -> None:
        bg = Paths.GAME_BACKGROUND
        if os.path.exists(bg):
            bg_url = bg.replace('\\', '/')
            self.setStyleSheet(f"""
                QWidget {{
                    background-image: url('{bg_url}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """)
        else:
            self.setStyleSheet(styles.GRADIENT_BG)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 5, 15, 5)

        # Title
        from src.utils.turkish import to_turkish_upper
        title = QLabel(to_turkish_upper(category_name))
        title.setFont(QFont(UISettings.FONT_FAMILY, 30, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(styles.TITLE_LABEL)

        # Puzzle cards
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        cards_layout = QHBoxLayout(card_container)
        cards_layout.setSpacing(30)
        cards_layout.setAlignment(Qt.AlignCenter)

        cat_data = CATEGORIES.get(category_name, {})
        puzzles  = cat_data.get("puzzles", [])

        for puzzle in puzzles:
            card = PuzzleCard(
                puzzle_data=puzzle,
                category_name=category_name,
                on_start=on_start_puzzle,
            )
            cards_layout.addWidget(card)

        scroll = QScrollArea()
        scroll.setWidget(card_container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(styles.SCROLL_AREA)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Back
        back_btn = QPushButton("GERİ")
        back_btn.setFixedSize(350, 80)
        back_btn.setFont(QFont(UISettings.FONT_FAMILY, 20, QFont.Bold))
        back_btn.setStyleSheet(styles.BTN_BACK)
        back_btn.clicked.connect(on_back)
        registry.append(back_btn)

        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        layout.setStretchFactor(title,  0)
        layout.setStretchFactor(scroll, 1)
