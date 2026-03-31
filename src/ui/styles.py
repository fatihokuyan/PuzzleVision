"""
styles.py
=========
Centralised QSS style constants for PuzzleVision.

All QPushButton, QScrollArea, QLabel and QDialog styles used across
screens and dialogs are defined here as module-level string constants.
Importing from this module instead of embedding inline strings eliminates
duplication and makes theming trivial.
"""

from src.config import UISettings

_FONT = UISettings.FONT_FAMILY

# ---------------------------------------------------------------------------
# Button Styles
# ---------------------------------------------------------------------------

BTN_START = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #0D47A1, stop:1 #1565C0);
        color: white;
        border-radius: 70px;
        margin: 10px;
        border: 5px solid rgba(255,255,255,0.8);
        letter-spacing: 3px;
        font-family: '{_FONT}';
        font-weight: bold;
        padding: 5px 10px;
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #1565C0, stop:0.5 #0D47A1, stop:1 #1565C0);
        color: rgba(255,255,255,0.8);
    }}
"""

BTN_HINT = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #1976D2, stop:1 #2196F3);
        color: white;
        border-radius: 60px;
        margin: 10px;
        border: 5px solid rgba(255,255,255,0.8);
        letter-spacing: 2px;
        font-family: '{_FONT}';
        font-weight: bold;
        padding: 5px;
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #2196F3, stop:0.5 #1976D2, stop:1 #2196F3);
        color: rgba(255,255,255,0.8);
    }}
"""

BTN_EXIT = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #E53935, stop:1 #C62828);
        color: white;
        border-radius: 60px;
        margin: 10px;
        border: 5px solid rgba(255,255,255,0.8);
        letter-spacing: 2px;
        font-family: '{_FONT}';
        font-weight: bold;
        padding: 5px;
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #C62828, stop:0.5 #B71C1C, stop:1 #C62828);
        color: rgba(255,255,255,0.8);
    }}
"""

BTN_BACK = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #C0392B, stop:1 #A02B1F);
        color: white;
        border-radius: 30px;
        margin: 10px;
        border: 3px solid rgba(255,255,255,0.5);
        font-family: '{_FONT}';
        font-weight: bold;
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #A02B1F, stop:1 #831F15);
    }}
"""

BTN_PUZZLE_START = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #0D47A1, stop:1 #1565C0);
        color: white;
        border-radius: 40px;
        margin: 10px;
        border: 5px solid rgba(255,255,255,0.8);
        letter-spacing: 3px;
        font-family: '{_FONT}';
        font-weight: bold;
        padding: 5px 10px;
    }}
    QPushButton:disabled {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #94A6AB, stop:1 #7A8C91);
        color: rgba(255,255,255,0.5);
        border: 4px solid rgba(200,200,200,0.3);
    }}
"""

BTN_CANCEL_PUZZLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #FF0000, stop:1 #D30000);
        color: white;
        border-radius: 28px;
        margin: 5px;
        border: 2px solid rgba(255,255,255,0.5);
        letter-spacing: 1.5px;
        font-weight: bold;
        padding: 5px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #FF1A1A, stop:1 #E70000);
        border: 2px solid rgba(255,255,255,0.7);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #D30000, stop:0.5 #B70000, stop:1 #D30000);
        color: rgba(255,255,255,0.9);
    }
"""

BTN_CATEGORY_CARD = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(38,63,105,1), stop:1 rgba(26,45,80,1));
        border-radius: 20px;
        border: 2px solid rgba(50,80,120,1);
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(48,73,115,1), stop:1 rgba(36,55,90,1));
        border: 2px solid rgba(60,90,130,1);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(26,45,80,1), stop:0.5 rgba(38,63,105,1), stop:1 rgba(26,45,80,1));
        border: 2px solid rgba(40,70,110,1);
    }
"""

BTN_NUMPAD = """
    QPushButton {
        background: rgba(255,255,255,0.1);
        border: none;
        border-radius: 40px;
        color: white;
    }
    QPushButton:hover  { background: rgba(255,255,255,0.2); }
    QPushButton:pressed{ background: rgba(255,255,255,0.15); }
"""

BTN_NUMPAD_CANCEL = """
    QPushButton {
        background: rgba(231,76,60,0.2);
        border: none;
        border-radius: 40px;
        color: #E74C3C;
    }
    QPushButton:hover  { background: rgba(231,76,60,0.3); }
    QPushButton:pressed{ background: rgba(231,76,60,0.25); }
"""

BTN_HINT_CLOSE = """
    QPushButton {
        background: #E74C3C;
        color: white;
        border: 2px solid white;
        border-radius: 25px;
        padding: 10px;
    }
    QPushButton:hover  { background: #C0392B; }
    QPushButton:pressed{ background: #A93226; }
"""

# ---------------------------------------------------------------------------
# Label / Container Styles
# ---------------------------------------------------------------------------

TITLE_LABEL = """
    QLabel {
        color: white;
        margin: 5px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(41,128,185,0.6),
            stop:0.5 rgba(52,152,219,0.6),
            stop:1 rgba(41,128,185,0.6));
        padding: 4px;
        border-radius: 15px;
    }
"""

CATEGORY_TEXT_LABEL = """
    QLabel {
        color: white;
        margin-top: 5px;
        background: qradialgradient(
            cx:0.5, cy:0.3, radius:0.8,
            fx:0.5, fy:0.2,
            stop:0 rgba(255,255,255,100),
            stop:0.3 rgba(255,255,255,70),
            stop:0.5 rgba(255,255,255,40),
            stop:0.7 rgba(255,255,255,20),
            stop:0.9 rgba(255,255,255,10),
            stop:1 rgba(255,255,255,0));
        padding: 5px;
        border-radius: 10px;
    }
"""

IMG_CONTAINER = """
    QWidget {
        background: rgba(55,90,130,0.8);
        border-radius: 14px;
        border: none;
    }
"""

PUZZLE_CARD_IMG_FRAME = """
    QLabel {
        background-color: rgba(55,90,130,0.8);
        border-radius: 15px;
        padding: 10px;
        margin-top: 15px;
    }
"""

# ---------------------------------------------------------------------------
# Dialog / Window Styles
# ---------------------------------------------------------------------------

DIALOG_BG_DARK = """
    QWidget#bgWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #2C3E50, stop:1 #34495E);
        border-radius: 20px;
        border: 2px solid rgba(255,255,255,0.1);
    }
"""

INFO_MESSAGE_WIDGET = """
    QWidget#infoMessageWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #2b5876, stop:1 #4e4376);
        border-radius: 18px;
        border: 2px solid #fff;
    }
    QLabel {
        color: white;
        background: transparent;
    }
"""

# ---------------------------------------------------------------------------
# Scroll Area Style
# ---------------------------------------------------------------------------

SCROLL_AREA = """
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        border: none;
        background: rgba(255,255,255,0.1);
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: rgba(52,152,219,0.5);
        min-height: 30px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
"""

# ---------------------------------------------------------------------------
# Main Window / App Style
# ---------------------------------------------------------------------------

APP_STYLE = f"""
    QMainWindow, QWidget {{
        background: transparent;
    }}
    QPushButton {{
        font-family: '{_FONT}';
        font-weight: bold;
        padding: 10px;
        border: none;
        color: white;
    }}
"""

APP_STYLE_FALLBACK = f"""
    QMainWindow {{
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.45,
            stop:0 #5A9ACB, stop:0.2 #4883B8,
            stop:0.4 #386EA4, stop:0.6 #2A5A8D,
            stop:0.8 #1F4776, stop:1 #163860);
    }}
    QPushButton {{
        font-family: '{_FONT}';
        font-weight: bold;
        padding: 10px;
        border: none;
        color: white;
    }}
"""

TRANSPARENT_BG = "QWidget { background: transparent; }"

GRADIENT_BG = """
    QWidget {
        background: qradialgradient(
            cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.45,
            stop:0 #5A9ACB, stop:0.2 #4883B8,
            stop:0.4 #386EA4, stop:0.6 #2A5A8D,
            stop:0.8 #1F4776, stop:1 #163860);
    }
"""

# ---------------------------------------------------------------------------
# Loading Screen Styles
# ---------------------------------------------------------------------------

LOADING_SCREEN = """
    QWidget { font-family: "Segoe UI", Arial, sans-serif; }

    #bgPanel {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                     stop:0 #243B55, stop:1 #141E30);
        border: none;
        border-radius: 15px;
    }
    #headerBar {
        background-color: rgba(0,0,0,0.3);
        border-top-left-radius: 15px;
        border-top-right-radius: 15px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    #logoLabel {
        color: white; font-size: 22px; font-weight: bold;
        letter-spacing: 2px;
    }
    #institutionLabel {
        color: white; font-size: 18px;
    }
    #contentPanel { background-color: transparent; border: none; }
    #leftPanel {
        background-color: rgba(0,20,40,0.3);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.08);
        margin: 10px;
    }
    #categoryTitle {
        color: white; font-size: 32px; font-weight: bold;
        letter-spacing: 3px; padding: 15px 0px 5px 0px;
        text-shadow: 0px 0px 12px rgba(100,180,255,0.5);
    }
    #imageFrame {
        background-color: rgba(10,30,50,0.6);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.12);
    }
    #imageLabel { border-radius: 8px; }
    #rightPanel {
        background-color: rgba(10,30,50,0.4);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.08);
        margin: 10px;
    }
    #topDecoration, #bottomDecoration {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 transparent, stop:0.4 #4f93ce,
            stop:0.6 #4f93ce, stop:1 transparent);
        border-radius: 2px;
    }
    #loadingAnimationContainer { background-color: transparent; }
    #loadingText {
        color: white; font-size: 38px; font-weight: bold; letter-spacing: 4px;
    }
    #prepareText {
        color: rgba(255,255,255,0.9); font-size: 20px; letter-spacing: 2px;
    }
    #footerBar {
        background-color: rgba(0,0,0,0.3);
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    #infoText {
        color: rgba(255,255,255,0.9); font-size: 17px;
        font-style: italic; letter-spacing: 1px;
    }
"""

# ---------------------------------------------------------------------------
# Disabled-button overlay (appended when puzzle is active)
# ---------------------------------------------------------------------------

BTN_DISABLED_OVERLAY = """
    QPushButton {
        background-color: rgba(128,128,128,0.7) !important;
        color: rgba(200,200,200,0.7) !important;
        border: 2px solid rgba(100,100,100,0.5) !important;
    }
    QPushButton:hover {
        background-color: rgba(128,128,128,0.7) !important;
        color: rgba(200,200,200,0.7) !important;
    }
"""
