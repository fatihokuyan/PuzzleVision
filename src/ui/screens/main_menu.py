"""
main_menu.py
============
Main menu screen (BAŞLA / İPUCU / ÇIKIŞ buttons).
"""

from __future__ import annotations

import os
from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton,
)

from src.config import Paths, UISettings
from src.ui import styles


class MainMenuScreen(QWidget):
    """First page the user sees.

    Parameters
    ----------
    on_start : Callable
        Called when the user taps BAŞLA.
    on_hint : Callable
        Called when the user taps İPUCU.
    on_exit : Callable
        Called when the user taps ÇIKIŞ.
    button_registry : list[QPushButton]
        Mutable list owned by the main window – each new button is appended.
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        on_hint:  Callable[[], None],
        on_exit:  Callable[[], None],
        button_registry: list,
    ) -> None:
        super().__init__()
        self._build(on_start, on_hint, on_exit, button_registry)

    # ------------------------------------------------------------------

    def _build(self, on_start, on_hint, on_exit, registry) -> None:
        # Background via stylesheet (transparent when bg_label is set)
        bg = Paths.MAIN_BACKGROUND
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

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        # Buttons container
        btn_container = QWidget()
        btn_container.setMinimumHeight(220)
        btn_container.setMaximumHeight(220)
        btn_container.setContentsMargins(0, 0, 0, 0)
        btn_container.setAttribute(Qt.WA_TranslucentBackground)

        grid = QGridLayout(btn_container)
        grid.setHorizontalSpacing(80)
        grid.setVerticalSpacing(40)
        grid.setContentsMargins(0, 0, 0, 0)

        # BAŞLA
        start_btn = QPushButton("BAŞLA")
        start_btn.setFixedSize(600, 170)
        start_btn.setFont(QFont(UISettings.FONT_FAMILY, 50, QFont.Bold))
        start_btn.setStyleSheet(styles.BTN_START)
        start_btn.clicked.connect(on_start)
        registry.append(start_btn)

        # İPUCU
        hint_btn = QPushButton("İPUCU")
        hint_btn.setFixedSize(250, 150)
        hint_btn.setFont(QFont(UISettings.FONT_FAMILY, 25, QFont.Bold))
        hint_btn.setStyleSheet(styles.BTN_HINT)
        hint_btn.clicked.connect(on_hint)
        registry.append(hint_btn)

        # ÇIKIŞ
        exit_btn = QPushButton("ÇIKIŞ")
        exit_btn.setFixedSize(250, 150)
        exit_btn.setFont(QFont(UISettings.FONT_FAMILY, 25, QFont.Bold))
        exit_btn.setStyleSheet(styles.BTN_EXIT)
        exit_btn.clicked.connect(on_exit)
        registry.append(exit_btn)

        grid.addWidget(hint_btn,  0, 0, Qt.AlignRight)
        grid.addWidget(start_btn, 0, 1, Qt.AlignCenter)
        grid.addWidget(exit_btn,  0, 2, Qt.AlignLeft)

        layout.addStretch(1)
        layout.addStretch(12)
        layout.addWidget(btn_container, alignment=Qt.AlignHCenter | Qt.AlignBottom)
