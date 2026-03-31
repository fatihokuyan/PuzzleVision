"""
admin_password.py
=================
Admin password dialog with numeric keypad and lockout protection.

Extracts AdminPasswordDialog from the monolithic file.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QGraphicsDropShadowEffect,
)

from src.config import UISettings
from src.ui import styles


class AdminPasswordDialog(QDialog):
    """Numeric-keypad password dialog protecting the exit action."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Yönetici İzni Gerekli")
        self.setFixedSize(500, 550)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # State
        self.attempts         = 0
        self.max_attempts     = UISettings.MAX_LOGIN_ATTEMPTS
        self.is_locked        = False
        self.lock_timer: QTimer | None = None
        self.remaining_lock_time       = 0
        self.password                  = ""

        # Delayed check timer
        self.check_timer = QTimer()
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.check_password)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        bg_widget = QWidget()
        bg_widget.setObjectName("bgWidget")
        bg_widget.setStyleSheet(styles.DIALOG_BG_DARK)

        bg_layout = QVBoxLayout(bg_widget)
        bg_layout.setSpacing(15)
        bg_layout.setContentsMargins(20, 20, 20, 20)

        # --- Header ---
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setSpacing(15)

        icon_label = QLabel()
        try:
            from src.config import Paths
            pixmap = QPixmap(Paths.LOCK_ICON)
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception:
            pass
        icon_label.setAlignment(Qt.AlignCenter)

        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(5)

        title = QLabel("Yönetici İzni Gerekli")
        title.setFont(QFont(UISettings.FONT_FAMILY, 14, QFont.Bold))
        title.setStyleSheet("color: white;")

        subtitle = QLabel("Çıkış yapmak için yönetici şifresini giriniz")
        subtitle.setFont(QFont(UISettings.FONT_FAMILY, 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.7);")
        subtitle.setWordWrap(True)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        top_layout.addWidget(icon_label)
        top_layout.addWidget(title_widget, 1)

        # --- Password display ---
        self.password_display = QLineEdit()
        self.password_display.setEchoMode(QLineEdit.Password)
        self.password_display.setAlignment(Qt.AlignCenter)
        self.password_display.setFont(QFont(UISettings.FONT_FAMILY, 24))
        self.password_display.setFixedHeight(60)
        self.password_display.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 15px;
                padding: 10px;
                color: white;
            }
        """)
        self.password_display.setReadOnly(True)

        # --- Error label ---
        self.error_label = QLabel("")
        self.error_label.setFont(QFont(UISettings.FONT_FAMILY, 9))
        self.error_label.setStyleSheet("color: #E74C3C;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)

        # --- Numpad ---
        numpad = self._build_numpad()

        # Assemble
        bg_layout.addWidget(top_widget)
        bg_layout.addWidget(self.password_display)
        bg_layout.addWidget(self.error_label)
        bg_layout.addWidget(numpad)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        bg_widget.setGraphicsEffect(shadow)

        layout.addWidget(bg_widget)
        self.setLayout(layout)

    def _build_numpad(self) -> QWidget:
        numpad = QWidget()
        grid   = QGridLayout(numpad)
        grid.setSpacing(10)

        font = QFont(UISettings.FONT_FAMILY, 16, QFont.Bold)

        for i in range(9):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(80, 80)
            btn.setFont(font)
            btn.setStyleSheet(styles.BTN_NUMPAD)
            n = str(i + 1)
            btn.clicked.connect(lambda _, num=n: self.add_number(num))
            grid.addWidget(btn, i // 3, i % 3)

        zero_btn = QPushButton("0")
        zero_btn.setFixedSize(80, 80)
        zero_btn.setFont(font)
        zero_btn.setStyleSheet(styles.BTN_NUMPAD)
        zero_btn.clicked.connect(lambda: self.add_number("0"))

        del_btn = QPushButton("⌫")
        del_btn.setFixedSize(80, 80)
        del_btn.setFont(font)
        del_btn.setStyleSheet(styles.BTN_NUMPAD)
        del_btn.clicked.connect(self.delete_number)

        cancel_btn = QPushButton("İptal")
        cancel_btn.setFixedSize(80, 80)
        cancel_btn.setFont(QFont(UISettings.FONT_FAMILY, 14, QFont.Bold))
        cancel_btn.setStyleSheet(styles.BTN_NUMPAD_CANCEL)
        cancel_btn.clicked.connect(self.reject)

        grid.addWidget(cancel_btn, 3, 0)
        grid.addWidget(zero_btn,   3, 1)
        grid.addWidget(del_btn,    3, 2)
        return numpad

    # ------------------------------------------------------------------
    # Logic
    # ------------------------------------------------------------------

    def add_number(self, num: str) -> None:
        if self.is_locked or len(self.password) >= 4:
            return
        self.password += num
        self.password_display.setText("•" * len(self.password))
        if len(self.password) == 4:
            self.check_timer.start(300)

    def delete_number(self) -> None:
        if not self.is_locked:
            self.password = self.password[:-1]
            self.password_display.setText("•" * len(self.password))

    def check_password(self) -> None:
        if self.password == UISettings.ADMIN_PASSWORD:
            self.accept()
            return

        self.attempts += 1
        remaining = self.max_attempts - self.attempts

        if remaining > 0:
            self.error_label.setText(f"Hatalı şifre! {remaining} deneme hakkınız kaldı.")
            self.password = ""
            self.password_display.setText("")
        else:
            self._lock()
            self.attempts = 0

    def _lock(self) -> None:
        self.is_locked = True
        self.remaining_lock_time = UISettings.LOCKOUT_SECONDS
        self.password = ""
        self.password_display.setText("")
        for child in self.findChildren(QPushButton):
            if child.text() != "İptal":
                child.setEnabled(False)
        if not self.lock_timer:
            self.lock_timer = QTimer()
            self.lock_timer.timeout.connect(self._tick_lock)
        self.lock_timer.start(1000)
        self._update_lock_label()

    def _tick_lock(self) -> None:
        self.remaining_lock_time -= 1
        if self.remaining_lock_time <= 0:
            self._unlock()
        else:
            self._update_lock_label()

    def _update_lock_label(self) -> None:
        self.error_label.setText(
            f"Çok fazla yanlış deneme! {self.remaining_lock_time} saniye bekleyin."
        )

    def _unlock(self) -> None:
        self.is_locked = False
        self.error_label.setText("")
        for child in self.findChildren(QPushButton):
            child.setEnabled(True)
        if self.lock_timer:
            self.lock_timer.stop()
