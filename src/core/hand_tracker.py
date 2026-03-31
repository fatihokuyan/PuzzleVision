"""
hand_tracker.py
===============
MediaPipe hand-tracking wrapper.

Responsibilities
----------------
* Initialise and close the MediaPipe Hands solution.
* Process a (small) RGB frame and return raw landmark results.
* Provide helper methods: pinch detection, landmark pixel coordinates.

Design note
-----------
The tracker operates on a *down-scaled* frame to save CPU.  The caller is
responsible for passing ``display_w`` / ``display_h`` so that landmark
coordinates are scaled back to full-resolution display space.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import mediapipe as mp
import cv2
import numpy as np

from src.config import GameSettings


@dataclass
class HandResult:
    """Per-hand result returned by HandTracker.process()."""

    index: int                        # 0 or 1
    thumb_tip: tuple[int, int]        # (x, y) in display pixels
    index_tip: tuple[int, int]        # (x, y) in display pixels
    distance: float                   # thumb–index pixel distance
    is_pinching: bool
    landmarks: list[tuple[int, int]]  # all 21 points in display pixels


class HandTracker:
    """Thin wrapper around MediaPipe Hands for the puzzle game."""

    def __init__(self) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=GameSettings.MAX_HANDS,
            min_detection_confidence=GameSettings.DETECTION_CONFIDENCE,
            min_tracking_confidence=GameSettings.TRACKING_CONFIDENCE,
            model_complexity=GameSettings.MODEL_COMPLEXITY,
        )

        # Custom palm connections for the skeleton overlay
        self._custom_connections: list[tuple[int, int]] = [
            (0, 9),   # wrist → middle finger MCP
            (0, 13),  # wrist → ring finger MCP
        ]
        self.all_connections: list[tuple[int, int]] = (
            list(self._mp_hands.HAND_CONNECTIONS) + self._custom_connections
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def process(
        self,
        small_bgr_frame: np.ndarray,
        display_w: int,
        display_h: int,
    ) -> list[HandResult]:
        """Detect hands in *small_bgr_frame* and return scaled results.

        Parameters
        ----------
        small_bgr_frame:
            Already flipped, small BGR frame (e.g. 240×180).
        display_w, display_h:
            Full-resolution display dimensions used to scale landmarks.
        """
        if self._hands is None:
            return []

        rgb = cv2.cvtColor(small_bgr_frame, cv2.COLOR_BGR2RGB)
        raw = self._hands.process(rgb)

        results: list[HandResult] = []
        if not raw.multi_hand_landmarks:
            return results

        for i, hand_lm in enumerate(raw.multi_hand_landmarks):
            landmarks = [
                (int(lm.x * display_w), int(lm.y * display_h))
                for lm in hand_lm.landmark
            ]
            thumb  = landmarks[4]
            index  = landmarks[8]
            dist   = math.hypot(index[0] - thumb[0], index[1] - thumb[1])
            pinch  = dist < GameSettings.PINCH_THRESHOLD

            results.append(
                HandResult(
                    index=i,
                    thumb_tip=thumb,
                    index_tip=index,
                    distance=dist,
                    is_pinching=pinch,
                    landmarks=landmarks,
                )
            )

        return results

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._hands is not None:
            try:
                self._hands.close()
            except Exception as exc:
                print(f"HandTracker: close() error – {exc}")
            self._hands = None

    def is_alive(self) -> bool:
        return self._hands is not None
