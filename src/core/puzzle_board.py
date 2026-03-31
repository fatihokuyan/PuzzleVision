"""
puzzle_board.py
===============
Pure puzzle-logic layer: pieces, slots, placement, and collision detection.

Responsibilities
----------------
* Split an image into piece dicts.
* Create centre grid slots and edge holding slots.
* Handle slot assignment, vacancy checks, and snap logic.
* Decide when the puzzle is complete.

There is **no** rendering, input handling, or sound in this module.
"""

from __future__ import annotations

import math
import random
from typing import TypedDict

import cv2
import numpy as np

from src.config import GameSettings


# ---------------------------------------------------------------------------
# Type aliases (TypedDicts for clarity)
# ---------------------------------------------------------------------------

class Piece(TypedDict):
    id: int
    img: np.ndarray
    correct_row: int
    correct_col: int
    x: float
    y: float
    w: int
    h: int
    is_dragging: bool
    offset_x: float
    offset_y: float
    placed_correctly: bool
    current_slot: int | None


class Slot(TypedDict):
    id: int
    x: int
    y: int
    w: int
    h: int
    occupied_by: int | None   # piece id or None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EDGE_SLOT_ID_START = 1000  # Edge slot IDs start here; centre slots use 0..N-1


# ---------------------------------------------------------------------------
# PuzzleBoard
# ---------------------------------------------------------------------------

class PuzzleBoard:
    """Manages the state of a single puzzle game board.

    Parameters
    ----------
    image_path : str
        Path to the source image file.
    rows, cols : int
        Grid dimensions (default 4×4 from GameSettings).
    frame_w, frame_h : int
        Full game-window dimensions used to position slots.
    """

    def __init__(
        self,
        image_path: str,
        rows: int = GameSettings.PUZZLE_SIZE,
        cols: int = GameSettings.PUZZLE_SIZE,
        frame_w: int = GameSettings.FRAME_WIDTH,
        frame_h: int = GameSettings.FRAME_HEIGHT,
    ) -> None:
        self.image_path = image_path
        self.rows = rows
        self.cols = cols
        self.frame_w = frame_w
        self.frame_h = frame_h

        self.pieces: list[Piece] = []
        self.center_slots: list[Slot] = []
        self.edge_slots: list[Slot] = []
        self.full_image: np.ndarray | None = None
        self.is_ready = False

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def setup(self) -> bool:
        """Load the image, create pieces and slots.  Returns True on success."""
        original = cv2.imread(self.image_path)
        if original is None:
            print(f"PuzzleBoard: cannot read image – {self.image_path}")
            return False

        scale = GameSettings.SCALE_PERCENT / 100.0
        new_w = int(original.shape[1] * scale)
        new_h = int(original.shape[0] * scale)
        # Snap dimensions to grid multiples
        new_w = (new_w // self.cols) * self.cols
        new_h = (new_h // self.rows) * self.rows

        resized = cv2.resize(original, (new_w, new_h), interpolation=cv2.INTER_AREA)
        self.full_image = resized.copy()

        piece_w = new_w // self.cols
        piece_h = new_h // self.rows
        puzzle_w = self.cols * piece_w
        puzzle_h = self.rows * piece_h
        start_x = (self.frame_w - puzzle_w) // 2
        start_y = (self.frame_h - puzzle_h) // 2

        self.pieces = self._split_image(resized, piece_w, piece_h)
        self.center_slots = self._make_center_slots(start_x, start_y, piece_w, piece_h)
        self.edge_slots = self._make_edge_slots(
            start_x, start_y, puzzle_w, puzzle_h, piece_w, piece_h
        )

        # Randomly assign pieces to edge slots
        random.shuffle(self.pieces)
        for i, slot in enumerate(self.edge_slots):
            if i < len(self.pieces):
                p = self.pieces[i]
                p["x"] = float(slot["x"])
                p["y"] = float(slot["y"])
                p["current_slot"] = slot["id"]
                slot["occupied_by"] = p["id"]

        self.is_ready = True
        return True

    # ------------------------------------------------------------------
    # Slot helpers
    # ------------------------------------------------------------------

    def is_center_slot(self, slot_id: int) -> bool:
        return 0 <= slot_id < self.rows * self.cols

    def find_slot_by_id(self, slot_id: int) -> Slot | None:
        if self.is_center_slot(slot_id):
            return self.center_slots[slot_id]
        for s in self.edge_slots:
            if s["id"] == slot_id:
                return s
        return None

    def vacancy_count(self) -> tuple[int, int]:
        """Return (free_center, free_edge) slot counts."""
        free_c = sum(1 for s in self.center_slots if s["occupied_by"] is None)
        free_e = sum(1 for s in self.edge_slots   if s["occupied_by"] is None)
        return free_c, free_e

    # ------------------------------------------------------------------
    # Drag helpers
    # ------------------------------------------------------------------

    def smooth_move(self, current: float, target: float) -> float:
        return current + (target - current) * GameSettings.SMOOTHING_FACTOR

    def find_best_slot_on_drop(
        self,
        piece: Piece,
        in_center_area: bool,
        colliding_with: Piece | None,
    ) -> Slot | None:
        """Return the best empty slot for *piece* after a drop gesture."""
        piece_cx = piece["x"] + piece["w"] / 2
        piece_cy = piece["y"] + piece["h"] / 2

        candidates: list[Slot]
        if in_center_area:
            candidates = self.center_slots
        else:
            candidates = self.center_slots + self.edge_slots

        if colliding_with and colliding_with["current_slot"] is not None:
            is_colliding_center = self.is_center_slot(colliding_with["current_slot"])
            candidates = [
                s for s in candidates
                if s["occupied_by"] is None
                and self.is_center_slot(s["id"]) == is_colliding_center
            ]
            return self._nearest_slot(piece_cx, piece_cy, candidates)

        # Normal drop – respect snap threshold
        best: Slot | None = None
        best_dist = float("inf")
        snap = GameSettings.SNAP_THRESHOLD

        for slot in candidates:
            # Skip occupied slots (unless occupied by a non-correctly-placed piece)
            occ = slot["occupied_by"]
            if occ is not None:
                placed = next((p["placed_correctly"] for p in self.pieces if p["id"] == occ), False)
                if placed:
                    continue

            sx = slot["x"] + slot["w"] / 2
            sy = slot["y"] + slot["h"] / 2
            d  = math.hypot(piece_cx - sx, piece_cy - sy)

            effective_snap = snap * 4.0 if (not in_center_area and not self.is_center_slot(slot["id"])) else snap
            if d < effective_snap and d < best_dist:
                best_dist = d
                best = slot

        # Fallback: any empty slot
        if best is None:
            for slot in self.edge_slots + self.center_slots:
                if slot["occupied_by"] is None:
                    return slot

        return best

    def place_piece(self, piece: Piece, slot: Slot) -> None:
        """Move *piece* to *slot*, updating both objects."""
        # Clear old slot
        if piece["current_slot"] is not None:
            old = self.find_slot_by_id(piece["current_slot"])
            if old and old["occupied_by"] == piece["id"]:
                old["occupied_by"] = None

        # Centre pieces snap to slot centre
        if self.is_center_slot(slot["id"]):
            piece["x"] = float(slot["x"] + (slot["w"] - piece["w"]) // 2)
            piece["y"] = float(slot["y"] + (slot["h"] - piece["h"]) // 2)
        else:
            piece["x"] = float(slot["x"])
            piece["y"] = float(slot["y"])

        piece["current_slot"] = slot["id"]
        slot["occupied_by"] = piece["id"]

        if self.is_center_slot(slot["id"]):
            correct_id = piece["correct_row"] * self.cols + piece["correct_col"]
            piece["placed_correctly"] = slot["id"] == correct_id
        else:
            piece["placed_correctly"] = False

    def is_complete(self) -> bool:
        return all(p["placed_correctly"] for p in self.pieces)

    def auto_solve(self) -> None:
        """Instantly place every piece in its correct slot (cheat / + key)."""
        for p in self.pieces:
            correct_id   = p["correct_row"] * self.cols + p["correct_col"]
            correct_slot = self.center_slots[correct_id]

            # Free old slot
            if p["current_slot"] is not None:
                old = self.find_slot_by_id(p["current_slot"])
                if old and old["occupied_by"] == p["id"]:
                    old["occupied_by"] = None

            p["x"] = float(correct_slot["x"])
            p["y"] = float(correct_slot["y"])
            p["current_slot"] = correct_id
            p["placed_correctly"] = True
            correct_slot["occupied_by"] = p["id"]

    # ------------------------------------------------------------------
    # Rendering helpers (no Qt, pure OpenCV)
    # ------------------------------------------------------------------

    def draw_puzzle_area(self, frame: np.ndarray) -> None:
        """Darken the centre area and draw grid lines."""
        if self.full_image is None:
            return
        pw = self.full_image.shape[1] // self.cols
        ph = self.full_image.shape[0] // self.rows
        area_w = self.cols * pw
        area_h = self.rows * ph
        sx = (self.frame_w - area_w) // 2
        sy = (self.frame_h - area_h) // 2

        overlay = frame.copy()
        cv2.rectangle(overlay, (sx, sy), (sx + area_w, sy + area_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

        grey = (180, 180, 180)
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = sx + c * pw
                y1 = sy + r * ph
                cv2.rectangle(frame, (x1, y1), (x1 + pw, y1 + ph), grey, 1)

    def draw_pieces(self, frame: np.ndarray) -> None:
        """Draw all pieces, with dragging pieces rendered on top."""
        for p in sorted(self.pieces, key=lambda x: (not x["placed_correctly"], not x["is_dragging"])):
            pw, ph = p["w"], p["h"]
            px = int(max(0, min(p["x"], self.frame_w - pw)))
            py = int(max(0, min(p["y"], self.frame_h - ph)))

            if px >= self.frame_w or py >= self.frame_h or px + pw <= 0 or py + ph <= 0:
                continue

            alpha = 1.0 if (p["is_dragging"] or p["placed_correctly"]) else 0.75
            try:
                if alpha == 1.0:
                    frame[py:py+ph, px:px+pw] = p["img"]
                else:
                    bg = frame[py:py+ph, px:px+pw].copy()
                    frame[py:py+ph, px:px+pw] = cv2.addWeighted(p["img"], alpha, bg, 1 - alpha, 0)
            except Exception:
                continue

            # Border colour
            if p["is_dragging"]:
                color, thick = (255, 241, 198), 2
            elif p["placed_correctly"]:
                color, thick = (0, 255, 0), 1
            elif p["current_slot"] is not None and self.is_center_slot(p["current_slot"]):
                color, thick = (0, 0, 255), 1
            else:
                color, thick = (230, 216, 173), 2

            cv2.rectangle(frame, (px, py), (px + pw, py + ph), color, thick)

    # ------------------------------------------------------------------
    # Private builders
    # ------------------------------------------------------------------

    def _split_image(self, img: np.ndarray, pw: int, ph: int) -> list[Piece]:
        pieces: list[Piece] = []
        pid = 0
        for r in range(self.rows):
            for c in range(self.cols):
                y1, y2 = r * ph, r * ph + ph
                x1, x2 = c * pw, c * pw + pw
                piece_img = img[y1:y2, x1:x2].copy()
                pieces.append(
                    Piece(
                        id=pid,
                        img=piece_img,
                        correct_row=r,
                        correct_col=c,
                        x=0.0,
                        y=0.0,
                        w=pw,
                        h=ph,
                        is_dragging=False,
                        offset_x=0.0,
                        offset_y=0.0,
                        placed_correctly=False,
                        current_slot=None,
                    )
                )
                pid += 1
        return pieces

    def _make_center_slots(self, start_x: int, start_y: int, pw: int, ph: int) -> list[Slot]:
        slots: list[Slot] = []
        for r in range(self.rows):
            for c in range(self.cols):
                slots.append(
                    Slot(
                        id=r * self.cols + c,
                        x=start_x + c * pw,
                        y=start_y + r * ph,
                        w=pw,
                        h=ph,
                        occupied_by=None,
                    )
                )
        return slots

    def _make_edge_slots(
        self,
        px: int, py: int, pw: int, ph: int,
        piece_w: int, piece_h: int,
    ) -> list[Slot]:
        """Distribute slots evenly around the four sides of the puzzle area."""
        total   = self.rows * self.cols
        per_side = total // 4
        extra    = total % 4

        margin  = 30
        spacing = 10
        sid     = _EDGE_SLOT_ID_START

        slots: list[Slot] = []

        top_count    = per_side + (1 if extra > 0 else 0)
        right_count  = per_side + (1 if extra > 1 else 0)
        bottom_count = per_side + (1 if extra > 2 else 0)
        left_count   = per_side

        # Top
        total_w = top_count * piece_w + (top_count - 1) * spacing
        sx = px + (pw - total_w) // 2
        for i in range(top_count):
            slots.append(Slot(id=sid, x=sx + i * (piece_w + spacing), y=py - margin - piece_h, w=piece_w, h=piece_h, occupied_by=None))
            sid += 1

        # Right
        total_h = right_count * piece_h + (right_count - 1) * spacing
        sy = py + (ph - total_h) // 2
        for i in range(right_count):
            slots.append(Slot(id=sid, x=px + pw + margin, y=sy + i * (piece_h + spacing), w=piece_w, h=piece_h, occupied_by=None))
            sid += 1

        # Bottom
        total_w = bottom_count * piece_w + (bottom_count - 1) * spacing
        sx = px + (pw - total_w) // 2
        for i in range(bottom_count):
            slots.append(Slot(id=sid, x=sx + i * (piece_w + spacing), y=py + ph + margin, w=piece_w, h=piece_h, occupied_by=None))
            sid += 1

        # Left
        total_h = left_count * piece_h + (left_count - 1) * spacing
        sy = py + (ph - total_h) // 2
        for i in range(left_count):
            slots.append(Slot(id=sid, x=px - margin - piece_w, y=sy + i * (piece_h + spacing), w=piece_w, h=piece_h, occupied_by=None))
            sid += 1

        return slots

    @staticmethod
    def _nearest_slot(cx: float, cy: float, slots: list[Slot]) -> Slot | None:
        best: Slot | None = None
        best_dist = float("inf")
        for s in slots:
            d = math.hypot(cx - (s["x"] + s["w"] / 2), cy - (s["y"] + s["h"] / 2))
            if d < best_dist:
                best_dist = d
                best = s
        return best
