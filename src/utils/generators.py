"""
generators.py
=============
Static asset generators: logo bytes, lock icon, background path resolver.

These were previously scattered across LogoGenerator, LockLogoGenerator,
and BackgroundGenerator classes in the monolithic file.
"""

from __future__ import annotations

import io
import os

from PIL import Image, ImageDraw

from src.config import Paths


class LogoGenerator:
    """Returns an empty byte-string placeholder for the window icon.

    The original implementation was already a stub; kept for compatibility.
    """

    @staticmethod
    def create_logo() -> bytes:
        return b""


class LockLogoGenerator:
    """Generates (or loads) the lock icon used by AdminPasswordDialog."""

    @staticmethod
    def create_lock_logo() -> bytes:
        """Return PNG bytes for the lock icon.

        Loads from ``icon_images/lock_icon.png`` when available; otherwise
        draws a simple lock shape programmatically and caches it to disk.
        """
        logo_path = Paths.LOCK_ICON

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as fh:
                return fh.read()

        return LockLogoGenerator._draw_lock_icon(logo_path)

    # ------------------------------------------------------------------
    @staticmethod
    def _draw_lock_icon(save_path: str) -> bytes:
        """Draw a simple lock icon and save it, then return PNG bytes."""
        width, height = 200, 200
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        primary   = (52, 152, 219)
        secondary = (41, 128, 185)
        highlight = (133, 193, 233)

        # --- Shackle ---
        ring_r   = 40
        ring_cx  = width // 2
        ring_cy  = height // 2 - 10

        draw.ellipse(
            (ring_cx - ring_r, ring_cy - ring_r, ring_cx + ring_r, ring_cy + ring_r),
            fill=primary,
        )
        inner_r = ring_r - 20
        draw.ellipse(
            (ring_cx - inner_r, ring_cy - inner_r, ring_cx + inner_r, ring_cy + inner_r),
            fill=(0, 0, 0, 0),
        )

        # --- Body ---
        body_w, body_h = 100, 80
        body_x = (width - body_w) // 2
        body_y = ring_cy + ring_r - 10

        draw.rounded_rectangle(
            (body_x, body_y, body_x + body_w, body_y + body_h),
            radius=20,
            fill=primary,
        )

        # --- Keyhole ---
        kh_y = body_y + 25
        draw.ellipse((width // 2 - 10, kh_y, width // 2 + 10, kh_y + 20), fill=secondary)
        draw.rectangle((width // 2 - 4, kh_y + 13, width // 2 + 4, kh_y + 36), fill=secondary)

        # --- Highlight ---
        draw.rounded_rectangle(
            (body_x + 10, body_y + 5, body_x + body_w - 40, body_y + 15),
            radius=5,
            fill=(*highlight, 80),
        )

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as fh:
            fh.write(data)

        return data


class BackgroundGenerator:
    """Resolves the path to the game background image."""

    @staticmethod
    def get_path() -> str | None:
        """Return the background image path, or *None* if not found."""
        if os.path.exists(Paths.GAME_BACKGROUND):
            return Paths.GAME_BACKGROUND
        print(f"WARNING: Background image not found at {Paths.GAME_BACKGROUND}")
        return None
