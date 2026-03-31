"""
screen_manager.py
=================
Detects and exposes the kiosk (touch) screen and the game (secondary) screen.

Responsibilities
----------------
* Enumerate connected QScreen objects at startup.
* Provide ``kiosk_screen`` and ``game_screen`` properties.
* Show a warning dialog when only one monitor is detected.
"""

from __future__ import annotations

from PyQt5.QtWidgets import QApplication, QMessageBox


class ScreenManager:
    """Detects dual-monitor setup and exposes screen references.

    Attributes
    ----------
    kiosk_screen : QScreen
        The primary (touch/kiosk) display.
    game_screen : QScreen
        The secondary display used for the puzzle window.
        Equals ``kiosk_screen`` in single-monitor mode.
    is_dual_monitor : bool
        True when two or more monitors are detected.
    """

    def __init__(self) -> None:
        screens = QApplication.screens()

        if len(screens) >= 2:
            self.kiosk_screen     = screens[0]
            self.game_screen      = screens[1]
            self.is_dual_monitor  = True
            print(
                f"ScreenManager: dual-monitor – "
                f"kiosk={self.kiosk_screen.name()} "
                f"({self.kiosk_screen.geometry().width()}×{self.kiosk_screen.geometry().height()}), "
                f"game={self.game_screen.name()} "
                f"({self.game_screen.geometry().width()}×{self.game_screen.geometry().height()})"
            )
        else:
            self.kiosk_screen     = screens[0]
            self.game_screen      = screens[0]
            self.is_dual_monitor  = False
            print("ScreenManager: single-monitor mode.")
            self._warn_single_monitor()

    # ------------------------------------------------------------------

    def game_geometry(self) -> tuple[int, int, int, int]:
        """Return (x, y, width, height) of the game screen."""
        geo = self.game_screen.geometry()
        return geo.x(), geo.y(), geo.width(), geo.height()

    # ------------------------------------------------------------------

    @staticmethod
    def _warn_single_monitor() -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Ekran Yapılandırması")
        msg.setText("İkinci ekran bulunamadı!")
        msg.setInformativeText("Program tek ekranda çalışacak.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
