"""
loading_screen.py
=================
Loading screen widget displayed on the secondary monitor while a puzzle starts.

Extracted from the monolithic LoadingScreen class.
Emits two signals:
- earlyPrepare  → fired at 1.5 s (camera/MediaPipe initialisation time)
- loadingFinished → fired at 3.0 s (close the screen)
"""

from __future__ import annotations

import os

from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QProgressBar,
    QGraphicsDropShadowEffect,
)

from src.config import Paths, UISettings
from src.ui import styles


class LoadingScreen(QWidget):
    """Full-screen loading overlay shown on the game (secondary) monitor."""

    loadingFinished = pyqtSignal()   # Fired at 3 s
    earlyPrepare    = pyqtSignal()   # Fired at 1.5 s

    def __init__(
        self,
        parent=None,
        category_name: str = "",
        image_path: str = "",
        game_screen=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Position on the game screen
        if game_screen:
            geo = game_screen.geometry()
            self.setGeometry(geo)

        self.showFullScreen()
        self.raise_()
        self.activateWindow()

        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        self._build_ui(category_name, image_path)
        self._setup_timers()
        self._draw_watermark()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self, category_name: str, image_path: str) -> None:
        self.setStyleSheet(styles.LOADING_SCREEN)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Background panel
        self.bg_panel = QWidget(self)
        self.bg_panel.setObjectName("bgPanel")
        bg_layout = QVBoxLayout(self.bg_panel)
        bg_layout.setContentsMargins(60, 40, 60, 40)
        bg_layout.setSpacing(0)

        bg_layout.addWidget(self._build_header())
        bg_layout.addWidget(self._build_content(category_name, image_path), 1)
        bg_layout.addWidget(self._build_footer())

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        self.bg_panel.setGraphicsEffect(shadow)

        self.main_layout.addWidget(self.bg_panel)

    def _build_header(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("headerBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("PUZZLE VISION")
        logo.setObjectName("logoLabel")

        inst = QLabel("Konya Bilim Merkezi")
        inst.setObjectName("institutionLabel")
        inst.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(logo)
        layout.addWidget(inst)
        return bar

    def _build_content(self, category_name: str, image_path: str) -> QWidget:
        panel = QWidget()
        panel.setObjectName("contentPanel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        layout.addWidget(self._build_left_panel(category_name, image_path), 65)
        layout.addWidget(self._build_right_panel(), 35)
        return panel

    def _build_left_panel(self, category_name: str, image_path: str) -> QWidget:
        panel = QWidget()
        panel.setObjectName("leftPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)

        # Image frame
        img_frame = QFrame()
        img_frame.setObjectName("imageFrame")
        img_frame.setMinimumSize(600, 450)
        frame_layout = QVBoxLayout(img_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)

        img_label = QLabel()
        img_label.setObjectName("imageLabel")
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setScaledContents(False)

        if os.path.exists(image_path):
            px = QPixmap(image_path)
            img_label.setPixmap(px.scaled(580, 430, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.category_title = QLabel((category_name or "PUZZLE").upper())
        self.category_title.setObjectName("categoryTitle")
        self.category_title.setAlignment(Qt.AlignCenter)

        frame_layout.addWidget(img_label, 0, Qt.AlignCenter)
        frame_layout.addWidget(self.category_title, 1, Qt.AlignCenter)
        layout.addWidget(img_frame, 1, Qt.AlignCenter)
        return panel

    def _build_right_panel(self) -> QWidget:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QMovie

        panel = QWidget()
        panel.setObjectName("rightPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        top_deco = QFrame()
        top_deco.setObjectName("topDecoration")
        top_deco.setFixedHeight(4)

        # Puzzle icon
        puzzle_icon = QLabel()
        puzzle_icon.setObjectName("puzzleIcon")
        puzzle_icon.setFixedSize(80, 80)
        puzzle_icon.setAlignment(Qt.AlignCenter)
        if os.path.exists(Paths.PUZZLE_ICON):
            px = QPixmap(Paths.PUZZLE_ICON)
            puzzle_icon.setPixmap(px.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # GIF
        anim_container = QWidget()
        anim_container.setObjectName("loadingAnimationContainer")
        anim_layout = QVBoxLayout(anim_container)
        anim_layout.setContentsMargins(0, 0, 0, 0)
        anim_layout.setAlignment(Qt.AlignCenter)

        self.loading_animation = QLabel()
        self.loading_animation.setObjectName("loadingAnimation")
        self.loading_animation.setAlignment(Qt.AlignCenter)
        self.loading_animation.setFixedSize(360, 360)

        self.loading_movie = QMovie(Paths.LOADING_GIF)
        self.loading_movie.setScaledSize(QSize(360, 360))
        self.loading_animation.setMovie(self.loading_movie)
        self.loading_movie.start()
        anim_layout.addWidget(self.loading_animation)

        # Text labels
        self.loading_text = QLabel("LOADING...")
        self.loading_text.setObjectName("loadingText")
        self.loading_text.setAlignment(Qt.AlignCenter)

        prepare_text = QLabel("PUZZLE HAZIRLANIYOR")
        prepare_text.setObjectName("prepareText")
        prepare_text.setAlignment(Qt.AlignCenter)

        bottom_deco = QFrame()
        bottom_deco.setObjectName("bottomDecoration")
        bottom_deco.setFixedHeight(4)

        layout.addWidget(top_deco)
        layout.addWidget(puzzle_icon, 0, Qt.AlignCenter)
        layout.addWidget(anim_container, 1)
        layout.addWidget(self.loading_text, 0, Qt.AlignCenter)
        layout.addWidget(prepare_text, 0, Qt.AlignCenter)
        layout.addWidget(bottom_deco)
        return panel

    def _build_footer(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("footerBar")
        bar.setFixedHeight(50)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        self.info_text = QLabel("Parçaları doğru yerleştirmek için sürükleyin")
        self.info_text.setObjectName("infoText")
        self.info_text.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        layout.addWidget(self.info_text)
        layout.addWidget(self.progress_bar, 0, Qt.AlignRight)
        return bar

    # ------------------------------------------------------------------
    # Timers
    # ------------------------------------------------------------------

    def _setup_timers(self) -> None:
        # Completion
        self._finish_timer = QTimer(self)
        self._finish_timer.setSingleShot(True)
        self._finish_timer.timeout.connect(self._on_loading_finished)
        self._finish_timer.start(UISettings.LOADING_TOTAL_MS)

        # Early prepare
        self._early_timer = QTimer(self)
        self._early_timer.setSingleShot(True)
        self._early_timer.timeout.connect(self._on_early_prepare)
        self._early_timer.start(UISettings.LOADING_EARLY_PREP_MS)

        # Pulse
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(40)
        self._pulse_value     = 0.0
        self._pulse_direction = 1

        # Progress bar
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(50)
        self._progress_value = 0

    def _on_loading_finished(self) -> None:
        print("LoadingScreen: emitting loadingFinished.")
        self.loadingFinished.emit()

    def _on_early_prepare(self) -> None:
        print("LoadingScreen: emitting earlyPrepare.")
        self.raise_()
        self.activateWindow()
        self.earlyPrepare.emit()

    def _update_pulse(self) -> None:
        self._pulse_value += 0.05 * self._pulse_direction
        if self._pulse_value >= 1.0:
            self._pulse_value = 1.0
            self._pulse_direction = -1
        elif self._pulse_value <= 0.0:
            self._pulse_value = 0.0
            self._pulse_direction = 1

        glow = 10 + int(20 * self._pulse_value)
        r = 120 + int(60 * self._pulse_value)
        g = 180 + int(30 * self._pulse_value)
        self.loading_text.setStyleSheet(
            f"color: white; font-size: 38px; font-weight: bold; "
            f"letter-spacing: 4px; "
            f"text-shadow: 0px 0px {glow}px rgba({r},{g},255,0.9);"
        )

        if hasattr(self, "category_title"):
            tg = 5 + int(12 * self._pulse_value)
            self.category_title.setStyleSheet(
                f"color: white; font-size: 32px; font-weight: bold; "
                f"letter-spacing: 3px; padding: 15px 0px 5px 0px; "
                f"text-shadow: 0px 0px {tg}px rgba(100,180,255,0.7);"
            )

        opa = 0.7 + 0.3 * self._pulse_value
        self.info_text.setStyleSheet(
            f"color: rgba(255,255,255,{opa:.2f}); font-size: 17px; "
            f"font-style: italic; letter-spacing: 1px;"
        )

    def _update_progress(self) -> None:
        if self._progress_value < 98:
            inc = max(1, int((100 - self._progress_value) / 20))
            self._progress_value = min(98, self._progress_value + inc)
            self.progress_bar.setValue(self._progress_value)
        else:
            self._progress_timer.stop()

    # ------------------------------------------------------------------
    # Watermark
    # ------------------------------------------------------------------

    def _draw_watermark(self) -> None:
        pixmap = QPixmap(self.width(), self.height())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("Segoe UI", 120, QFont.Bold))
        painter.setPen(QColor(255, 255, 255, 12))
        painter.drawText(self.rect(), Qt.AlignCenter, "PuzzleVision\nKonya Bilim Merkezi")
        painter.end()

        wm = QLabel(self)
        wm.setPixmap(pixmap)
        wm.setGeometry(0, 0, self.width(), self.height())
        wm.setAttribute(Qt.WA_TransparentForMouseEvents)
        wm.lower()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._draw_watermark()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        for timer_name in ("_finish_timer", "_early_timer", "_pulse_timer", "_progress_timer"):
            t = getattr(self, timer_name, None)
            if t and t.isActive():
                t.stop()
        if hasattr(self, "loading_movie") and self.loading_movie:
            self.loading_movie.stop()
        event.accept()
