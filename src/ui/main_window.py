"""
main_window.py
==============
PuzzleVision – Ana pencere (QMainWindow).

Sorumlulukları:
  - Ekranları QStackedWidget ile yönetmek
  - Eylemsizlik zamanlayıcısı (inactivity timer)
  - Oyun başlatma / bitirme döngüsü
  - Event filtresi (kiosk dokunma kilidini kaldırma)
  - Arka plan görüntüsü
"""

from __future__ import annotations

import os
import sys
import threading

from PyQt5.QtCore import (
    Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSlot,
)
from PyQt5.QtGui import QColor, QFont, QPixmap, QKeyEvent
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QLabel, QApplication, QGraphicsOpacityEffect,
)

from src.config import Paths, UISettings, CATEGORIES
from src.ui.screen_manager import ScreenManager
from src.ui import styles
from src.ui.screens.main_menu import MainMenuScreen
from src.ui.screens.categories_menu import CategoriesMenuScreen
from src.ui.screens.category_page import CategoryPageScreen
from src.ui.dialogs.admin_password import AdminPasswordDialog
from src.ui.dialogs.hint_dialog import HintDialog
from src.ui.dialogs.info_message import InfoMessageDialog
from src.ui.widgets.loading_screen import LoadingScreen
from src.core.puzzle_game import PuzzleGame


# Page index constants
PAGE_MAIN       = 0
PAGE_CATEGORIES = 1
PAGE_CATEGORY   = 2


class PuzzleVision(QMainWindow):
    """Main application window (kiosk screen)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PuzzleVision")
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        # Sub-system references
        self._screen_manager   = ScreenManager()
        self._game_thread: threading.Thread | None = None
        self._current_game     = None
        self._loading_screen: LoadingScreen | None = None
        self._info_dialog: InfoMessageDialog | None = None

        # Button registries (for global enable/disable during game)
        self._buttons: list = []
        self._text_labels: list = []

        # Internal page state
        self._current_category: str = ""

        # Inactivity timer
        self._inactivity_timer = QTimer(self)
        self._inactivity_timer.timeout.connect(self._on_inactivity)
        self._inactivity_timer.start(UISettings.INACTIVITY_TIMEOUT_MS)

        # Second-screen idle label
        self._second_screen_label: QLabel | None = None

        self._build_ui()
        self._install_event_filter()
        self._setup_second_screen_idle()

    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_ui(self) -> None:
        kiosk_geo = self._screen_manager.kiosk_screen.geometry()
        self.setGeometry(kiosk_geo)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        # Central widget
        central = QWidget()
        central.setStyleSheet(styles.TRANSPARENT_BG)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Background label
        self._bg_label = QLabel(central)
        self._bg_label.setScaledContents(True)
        self._bg_label.setGeometry(0, 0, kiosk_geo.width(), kiosk_geo.height())

        bg_path = Paths.MAIN_BACKGROUND
        if os.path.exists(bg_path):
            self._bg_label.setPixmap(QPixmap(bg_path))
            self.setStyleSheet(styles.APP_STYLE)
        else:
            self.setStyleSheet(styles.APP_STYLE_FALLBACK)

        # Stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(styles.TRANSPARENT_BG)
        root_layout.addWidget(self._stack)

        self._add_screens()

    def _add_screens(self) -> None:
        # PAGE_MAIN
        main_menu = MainMenuScreen(
            on_start=self._go_categories,
            on_hint=self._show_hint,
            on_exit=self._confirm_exit,
            button_registry=self._buttons,
        )
        self._stack.addWidget(main_menu)                   # index 0

        # PAGE_CATEGORIES
        cat_menu = CategoriesMenuScreen(
            on_category=self._go_category,
            on_back=lambda: self._go_page(PAGE_MAIN),
            button_registry=self._buttons,
            text_label_registry=self._text_labels,
        )
        self._stack.addWidget(cat_menu)                    # index 1

        # PAGE_CATEGORY (placeholder; replaced on each navigation)
        self._category_page_widget = QWidget()
        self._stack.addWidget(self._category_page_widget)  # index 2

    # ==================================================================
    # Navigation
    # ==================================================================

    def _go_page(self, page_index: int) -> None:
        self._reset_inactivity()
        self._fade_transition(page_index)

    def _go_categories(self) -> None:
        self._go_page(PAGE_CATEGORIES)

    def _go_category(self, name: str) -> None:
        self._current_category = name
        # Rebuild category page widget
        old = self._stack.widget(PAGE_CATEGORY)
        new_page = CategoryPageScreen(
            category_name=name,
            on_start_puzzle=self.start_puzzle,
            on_back=lambda: self._go_page(PAGE_CATEGORIES),
            button_registry=self._buttons,
        )
        self._stack.removeWidget(old)
        old.deleteLater()
        self._stack.insertWidget(PAGE_CATEGORY, new_page)
        self._category_page_widget = new_page
        self._go_page(PAGE_CATEGORY)

    # ==================================================================
    # Transition animation
    # ==================================================================

    def _fade_transition(self, target_page: int) -> None:
        effect = QGraphicsOpacityEffect(self._stack)
        self._stack.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(UISettings.FADE_DURATION_MS)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)

        def on_fade_out_done():
            self._stack.setCurrentIndex(target_page)
            anim2 = QPropertyAnimation(effect, b"opacity", self)
            anim2.setDuration(UISettings.FADE_DURATION_MS)
            anim2.setStartValue(0.0)
            anim2.setEndValue(1.0)
            anim2.setEasingCurve(QEasingCurve.InOutQuad)
            anim2.finished.connect(lambda: self._stack.setGraphicsEffect(None))
            anim2.start()
            self._current_anim2 = anim2

        anim.finished.connect(on_fade_out_done)
        anim.start()
        self._current_anim = anim

    # ==================================================================
    # Dialogs
    # ==================================================================

    def _show_hint(self) -> None:
        self._reset_inactivity()
        dlg = HintDialog(self)
        dlg.exec_()

    def _confirm_exit(self) -> None:
        self._reset_inactivity()
        dlg = AdminPasswordDialog(self)
        if dlg.exec_() == AdminPasswordDialog.Accepted:
            QApplication.quit()

    # ==================================================================
    # Puzzle launch / teardown
    # ==================================================================

    def _start_puzzle(self, category_name: str, image_path: str, video_path: str) -> None:
        """Launch the puzzle game in a background thread."""
        if self._game_thread and self._game_thread.is_alive():
            return  # Already running

        self._reset_inactivity()
        self._inactivity_timer.stop()
        self._set_buttons_enabled(False)
        self._show_loading_screen(category_name, image_path)
        self._show_info_dialog()

    def _show_loading_screen(self, category_name: str, image_path: str) -> None:
        game_screen = self._screen_manager.game_screen
        self._loading_screen = LoadingScreen(
            parent=None,
            category_name=category_name,
            image_path=image_path,
            game_screen=game_screen,
        )
        self._loading_screen.earlyPrepare.connect(lambda: None)   # no-op; game starts on loadingFinished
        self._loading_screen.loadingFinished.connect(
            lambda: self._launch_game_thread(
                self._current_category,
                self._stack.widget(PAGE_CATEGORY).findChild(type(None)) or "",
                "",
            )
        )

    # We need to capture image/video_path before closing the reference,
    # so we override the connection with a full closure:
    def _show_loading_and_launch(self, category_name: str, image_path: str, video_path: str) -> None:
        game_screen = self._screen_manager.game_screen
        self._loading_screen = LoadingScreen(
            parent=None,
            category_name=category_name,
            image_path=image_path,
            game_screen=game_screen,
        )
        self._loading_screen.loadingFinished.connect(
            lambda: self._launch_game_thread(category_name, image_path, video_path)
        )

    @pyqtSlot()
    def _launch_game_thread(
        self, category_name: str = "", image_path: str = "", video_path: str = ""
    ) -> None:
        geo = self._screen_manager.game_geometry()

        game = PuzzleGame(
            category_name=category_name,
            image_path=image_path,
            video_path=video_path,
            on_cancel=self._on_game_ended,
            on_complete=self._on_game_ended,
            game_screen_geometry=geo,
        )
        self._current_game = game

        self._game_thread = threading.Thread(target=game.start, daemon=True)
        self._game_thread.start()

    def _on_game_ended(self) -> None:
        """Called from the game thread – must marshal back to the Qt thread."""
        QTimer.singleShot(0, self._cleanup_after_game)

    @pyqtSlot()
    def _cleanup_after_game(self) -> None:
        # Close loading screen
        if self._loading_screen:
            self._loading_screen.close()
            self._loading_screen = None

        # Close info dialog
        if self._info_dialog:
            self._info_dialog.close()
            self._info_dialog = None

        self._current_game = None
        self._set_buttons_enabled(True)
        self._inactivity_timer.start(UISettings.INACTIVITY_TIMEOUT_MS)
        self._go_page(PAGE_MAIN)
        self._setup_second_screen_idle()

    # ==================================================================
    # Info dialog (kiosk screen overlay at game start)
    # ==================================================================

    def _show_info_dialog(self) -> None:
        self._info_dialog = InfoMessageDialog(self)
        kiosk_geo = self._screen_manager.kiosk_screen.geometry()
        self._info_dialog.position_on_screen(kiosk_geo)
        self._info_dialog.show()

    # ==================================================================
    # Second screen idle
    # ==================================================================

    def _setup_second_screen_idle(self) -> None:
        if self._second_screen_label:
            self._second_screen_label.close()
            self._second_screen_label = None

        if not self._screen_manager.is_dual_monitor:
            return

        lbl = QLabel()
        lbl.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        lbl.setAttribute(Qt.WA_TranslucentBackground)
        geo = self._screen_manager.game_screen.geometry()
        lbl.setGeometry(geo)

        bg_path = Paths.SECOND_SCREEN_BG
        if os.path.exists(bg_path):
            px = QPixmap(bg_path).scaled(geo.width(), geo.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(px)
        else:
            lbl.setStyleSheet("background: #141E30;")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont(UISettings.FONT_FAMILY, 40, QFont.Bold))
            lbl.setStyleSheet("color: white; font-size: 40px; background: #141E30;")
            lbl.setText("PuzzleVision\nKonya Bilim Merkezi")

        lbl.show()
        self._second_screen_label = lbl

    # ==================================================================
    # Inactivity timer
    # ==================================================================

    def _reset_inactivity(self) -> None:
        self._inactivity_timer.stop()
        self._inactivity_timer.start(UISettings.INACTIVITY_TIMEOUT_MS)

    def _on_inactivity(self) -> None:
        if self._game_thread and self._game_thread.is_alive():
            return
        current = self._stack.currentIndex()
        if current != PAGE_MAIN:
            self._go_page(PAGE_MAIN)

    # ==================================================================
    # Button enable/disable
    # ==================================================================

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for btn in self._buttons:
            try:
                if enabled:
                    btn.setEnabled(True)
                    # Restore original style (just re-toggle enabled state)
                else:
                    btn.setEnabled(False)
            except RuntimeError:
                pass  # Widget was deleted

    # ==================================================================
    # Event filter (kiosk touch reset)
    # ==================================================================

    def _install_event_filter(self) -> None:
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event) -> bool:
        from PyQt5.QtCore import QEvent
        if event.type() in (
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
            QEvent.MouseMove,
            QEvent.TouchBegin,
            QEvent.TouchEnd,
            QEvent.TouchUpdate,
            QEvent.KeyPress,
        ):
            self._reset_inactivity()
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self._confirm_exit()
        super().keyPressEvent(event)

    # ==================================================================
    # Override start_puzzle with proper closure approach
    # ==================================================================

    # The _start_puzzle method above calls _show_loading_and_launch
    # but loses image/video context. Patch at the point where
    # the PuzzleCard fires the callback:

    def start_puzzle(self, category_name: str, image_path: str, video_path: str) -> None:
        """Public entry-point called by PuzzleCard."""
        if self._game_thread and self._game_thread.is_alive():
            return
        self._reset_inactivity()
        self._inactivity_timer.stop()
        self._set_buttons_enabled(False)
        self._show_loading_and_launch(category_name, image_path, video_path)
        self._show_info_dialog()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        geo = self._screen_manager.kiosk_screen.geometry()
        self._bg_label.setGeometry(0, 0, geo.width(), geo.height())
