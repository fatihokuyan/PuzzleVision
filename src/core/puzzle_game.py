"""
puzzle_game.py
==============
Orchestrates a single play-session of PuzzleVision.

This class wires together PuzzleBoard, HandTracker, SoundManager, and
VideoPlayer into the main game loop.  It intentionally owns no Qt widgets –
all communication with the parent window uses callbacks supplied at
construction time.

Callbacks
---------
on_cancel():
    Called when the player presses Q/ESC or the time limit is reached.
on_complete():
    Called after the completion video has finished.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Callable

import cv2
import keyboard
import numpy as np
from PyQt5.QtWidgets import QApplication

from src.config import GameSettings, CameraSettings, Paths
from src.core.puzzle_board import PuzzleBoard
from src.core.hand_tracker import HandTracker
from src.core.sound_manager import SoundManager
from src.core.video_player import VideoPlayer


class PuzzleGame:
    """Single-session puzzle game orchestrator.

    Parameters
    ----------
    category_name : str
        Display name of the selected category.
    image_path : str
        Absolute path to the puzzle source image.
    video_path : str | None
        Absolute path to the completion video (optional).
    on_cancel : Callable
        Invoked when the game is cancelled (ESC / timeout / error).
    on_complete : Callable
        Invoked after the completion video finishes.
    game_screen_geometry : tuple[int,int,int,int] | None
        (x, y, w, h) of the secondary monitor – used to position the window.
    """

    WINDOW_NAME = "Puzzle Game"

    def __init__(
        self,
        category_name: str,
        image_path: str,
        video_path: str | None,
        on_cancel: Callable[[], None],
        on_complete: Callable[[], None],
        game_screen_geometry: tuple[int, int, int, int] | None = None,
    ) -> None:
        self.category_name        = category_name
        self.image_path           = image_path
        self.video_path           = video_path
        self._on_cancel           = on_cancel
        self._on_complete         = on_complete
        self._game_screen_geometry = game_screen_geometry

        self.is_running = False

        # Sub-systems  (initialised in start())
        self._board:   PuzzleBoard   | None = None
        self._tracker: HandTracker   | None = None
        self._sounds:  SoundManager  | None = None
        self._video:   VideoPlayer   | None = None
        self._cap:     cv2.VideoCapture | None = None

        # Per-frame state
        self._start_time:       float = 0.0
        self._frame_count:      int   = 0
        self._fps_values:       list[float] = []
        self._prev_time:        float = 0.0
        self._dragging_pieces:  dict[int, dict | None] = {}
        self._piece_timestamps: dict[int, float] = {}

        # Completion transition state machine
        self._transition_state:      str | None = None
        self._transition_start_time: float = 0.0
        self._puzzle_completed       = False

        # Background frame (loaded once)
        self._bg_frame: np.ndarray | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Initialise all subsystems and run the blocking game loop."""
        self._sounds  = SoundManager()
        self._tracker = HandTracker()
        self._board   = PuzzleBoard(self.image_path)

        if not self._board.setup():
            print("PuzzleGame: board setup failed – aborting.")
            self._cleanup()
            self._on_cancel()
            return

        if not self._open_camera():
            self._cleanup()
            self._on_cancel()
            return

        self._video = VideoPlayer(on_finished=self._on_video_finished)
        self._piece_timestamps = {p["id"]: 0.0 for p in self._board.pieces}
        self._create_window()
        self._sounds.play("start")
        self._start_time = time.time()
        self.is_running  = True

        self._game_loop()
        self._cleanup()
        if not self._puzzle_completed:
            self._on_cancel()

    def force_quit(self) -> None:
        """Signal the game loop to exit on the next iteration."""
        self.is_running = False

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _open_camera(self) -> bool:
        cap = cv2.VideoCapture(CameraSettings.INDEX, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CameraSettings.WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CameraSettings.HEIGHT)
        cap.set(cv2.CAP_PROP_FPS,          CameraSettings.FPS)
        cap.set(cv2.CAP_PROP_FOURCC,       cv2.VideoWriter_fourcc(*CameraSettings.FOURCC))
        cap.set(cv2.CAP_PROP_BUFFERSIZE,   CameraSettings.BUFFER_SIZE)
        if not cap.isOpened():
            print("PuzzleGame: could not open camera.")
            cap.release()
            return False
        self._cap = cap
        return True

    def _create_window(self) -> None:
        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_TOPMOST, 0)
        empty = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imshow(self.WINDOW_NAME, empty)
        cv2.setWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------

    def _game_loop(self) -> None:
        frame_interval = 1.0 / GameSettings.FRAME_RATE
        last_frame_time = time.time()

        while self.is_running:
            # --- Frame rate limiter ---
            elapsed = time.time() - last_frame_time
            if elapsed < frame_interval:
                time.sleep((frame_interval - elapsed) * 0.8)
            last_frame_time = time.time()

            current_time = time.time()

            # --- Keyboard shortcuts ---
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27) or keyboard.is_pressed("esc"):
                self.is_running = False
                break
            if key == ord("r") or keyboard.is_pressed("r"):
                self.is_running = False
                break
            if key == ord("+") or keyboard.is_pressed("+"):
                self._board.auto_solve()
                self._sounds.play("complete")
                self._puzzle_completed = True
                self._begin_transition()

            # --- Time limit ---
            if not self._puzzle_completed:
                if current_time - self._start_time >= GameSettings.TIME_LIMIT_SECONDS:
                    print("PuzzleGame: time limit reached.")
                    self.is_running = False
                    break

            # --- Background frame ---
            if self._bg_frame is None:
                self._bg_frame = self._load_background()
            display = self._bg_frame.copy()

            # --- Timer overlay ---
            remaining = max(0, GameSettings.TIME_LIMIT_SECONDS - (current_time - self._start_time))
            cv2.putText(display, str(int(remaining)),
                        (GameSettings.FRAME_WIDTH - 100, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # --- Completion transition ---
            if self._puzzle_completed:
                if self._run_transition(display):
                    self.is_running = False
                    break
            else:
                self._process_frame(display, current_time)

            # --- FPS overlay ---
            self._update_fps(current_time)
            avg_fps = sum(self._fps_values) / len(self._fps_values) if self._fps_values else 0
            cv2.putText(display, f"FPS: {avg_fps:.1f}", (5, 15),
                        cv2.FONT_HERSHEY_PLAIN, 0.8, (208, 224, 68), 1)

            # --- Display ---
            cv2.imshow(self.WINDOW_NAME, display)
            self._frame_count += 1

    # ------------------------------------------------------------------
    # Frame processing (camera + hand tracking + drag)
    # ------------------------------------------------------------------

    def _process_frame(self, display: np.ndarray, current_time: float) -> None:
        assert self._cap and self._tracker and self._board

        ret, raw_frame = self._cap.read()
        if not ret or raw_frame is None:
            print("PuzzleGame: Camera frame dropped. Retrying...")
            time.sleep(0.01)
            return

        # Flip and downscale for MediaPipe
        raw_frame = cv2.flip(raw_frame, 1)
        small = cv2.resize(
            raw_frame,
            (GameSettings.MEDIAPIPE_WIDTH, GameSettings.MEDIAPIPE_HEIGHT),
            interpolation=cv2.INTER_AREA,
        )

        hand_results = self._tracker.process(small, GameSettings.FRAME_WIDTH, GameSettings.FRAME_HEIGHT)

        # Draw X-ray skeleton
        for hr in hand_results:
            self._draw_xray(display, hr.landmarks, hr.is_pinching, hr.thumb_tip, hr.index_tip)

        # Drag-and-drop logic
        if self._board.is_ready:
            for hr in hand_results:
                self._handle_hand(hr, current_time)

        self._board.draw_puzzle_area(display)
        self._board.draw_pieces(display)

        # Check puzzle completion
        if self._board.is_complete() and not self._puzzle_completed:
            self._sounds.play("complete")
            self._puzzle_completed = True
            self._begin_transition()

    def _handle_hand(self, hr, current_time: float) -> None:
        assert self._board and self._sounds
        dragging = self._dragging_pieces.get(hr.index, None)
        ix, iy   = hr.index_tip

        if hr.distance < GameSettings.PINCH_THRESHOLD:
            if dragging is None:
                # Try to pick up a piece
                for p in self._board.pieces:
                    if p["placed_correctly"] or p["is_dragging"]:
                        continue
                    cx = p["x"] + p["w"] / 2
                    cy = p["y"] + p["h"] / 2
                    import math
                    if math.hypot(cx - ix, cy - iy) < GameSettings.PICK_RANGE:
                        self._sounds.play("pick")
                        p["is_dragging"] = True
                        p["offset_x"] = p["x"] - ix
                        p["offset_y"] = p["y"] - iy
                        if p["current_slot"] is not None:
                            old = self._board.find_slot_by_id(p["current_slot"])
                            if old and old["occupied_by"] == p["id"]:
                                old["occupied_by"] = None
                            p["current_slot"] = None
                        self._dragging_pieces[hr.index] = p
                        self._piece_timestamps[p["id"]] = current_time
                        break
            else:
                # Move the held piece
                dragging["x"] = self._board.smooth_move(dragging["x"], ix + dragging["offset_x"])
                dragging["y"] = self._board.smooth_move(dragging["y"], iy + dragging["offset_y"])

        elif hr.distance >= GameSettings.PINCH_RELEASE_THRESHOLD and dragging is not None:
            # Drop
            p = dragging
            px_area_w  = self._board.cols * p["w"]
            px_area_h  = self._board.rows * p["h"]
            cx_start   = (GameSettings.FRAME_WIDTH  - px_area_w) // 2
            cy_start   = (GameSettings.FRAME_HEIGHT - px_area_h) // 2
            piece_cx   = p["x"] + p["w"] / 2
            piece_cy   = p["y"] + p["h"] / 2
            in_center  = (cx_start <= piece_cx <= cx_start + px_area_w and
                          cy_start <= piece_cy <= cy_start + px_area_h)

            # Check collision with other pieces
            import math
            colliding_with = None
            px0, py0, px1, py1 = p["x"], p["y"], p["x"]+p["w"], p["y"]+p["h"]
            for other in self._board.pieces:
                if other["id"] == p["id"] or not other["current_slot"]:
                    continue
                ox0, oy0, ox1, oy1 = other["x"], other["y"], other["x"]+other["w"], other["y"]+other["h"]
                if px0 < ox1 and px1 > ox0 and py0 < oy1 and py1 > oy0:
                    colliding_with = other
                    break

            best_slot = self._board.find_best_slot_on_drop(p, in_center, colliding_with)

            if best_slot is not None:
                was_correct = p["placed_correctly"]
                self._board.place_piece(p, best_slot)
                if p["placed_correctly"] and not was_correct:
                    self._sounds.play("correct")
                    self._piece_timestamps[p["id"]] = float("-inf")
                else:
                    self._piece_timestamps[p["id"]] = current_time
            else:
                if p["current_slot"] is not None:
                    old = self._board.find_slot_by_id(p["current_slot"])
                    if old and old["occupied_by"] == p["id"]:
                        old["occupied_by"] = None
                p["current_slot"] = None

            self._sounds.play("drop")
            p["is_dragging"] = False
            self._dragging_pieces[hr.index] = None

    # ------------------------------------------------------------------
    # X-ray hand skeleton
    # ------------------------------------------------------------------

    def _draw_xray(self, display, landmarks, is_pinching, thumb_tip, index_tip):
        assert self._tracker
        overlay = np.zeros_like(display, dtype=np.uint8)
        bone    = (255, 255, 255)
        joint   = (200, 200, 200)
        shadow  = (80, 80, 80)

        for s_idx, e_idx in self._tracker.all_connections:
            pt1, pt2 = landmarks[s_idx], landmarks[e_idx]
            cv2.line(overlay, (pt1[0]+2, pt1[1]+2), (pt2[0]+2, pt2[1]+2), shadow, 8, cv2.LINE_AA)
            cv2.line(overlay, pt1, pt2, bone, 6, cv2.LINE_AA)
            cv2.line(overlay, pt1, pt2, joint, 2, cv2.LINE_AA)

        for pt in landmarks:
            cv2.circle(overlay, (pt[0]+2, pt[1]+2), 6, shadow, -1, cv2.LINE_AA)
            cv2.circle(overlay, pt, 5, bone, -1, cv2.LINE_AA)
            cv2.circle(overlay, pt, 6, joint, 1, cv2.LINE_AA)

        if is_pinching:
            for tip in (thumb_tip, index_tip):
                cv2.circle(overlay, (tip[0]+2, tip[1]+2), 8, shadow, -1, cv2.LINE_AA)
                cv2.circle(overlay, tip, 7, bone, 2, cv2.LINE_AA)
                cv2.circle(overlay, tip, 5, joint, -1, cv2.LINE_AA)

        mask = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY) > 0
        display[mask] = (display[mask] * 0.7).astype(np.uint8)
        cv2.addWeighted(overlay, 0.8, display, 1, 0, display)

    # ------------------------------------------------------------------
    # Completion transition state machine
    # ------------------------------------------------------------------

    def _begin_transition(self) -> None:
        self._transition_state      = "show_original_size"
        self._transition_start_time = time.time()

    def _run_transition(self, frame: np.ndarray) -> bool:
        """Animate the completion sequence. Returns True when done."""
        assert self._board and self._board.full_image is not None
        state   = self._transition_state
        elapsed = time.time() - self._transition_start_time
        fi      = self._board.full_image

        pw = fi.shape[1] // self._board.cols
        ph = fi.shape[0] // self._board.rows
        area_w = self._board.cols * pw
        area_h = self._board.rows * ph
        sx = (GameSettings.FRAME_WIDTH  - area_w) // 2
        sy = (GameSettings.FRAME_HEIGHT - area_h) // 2

        if state == "show_original_size":
            resized = cv2.resize(fi, (area_w, area_h))
            frame[sy:sy+area_h, sx:sx+area_w] = resized
            if elapsed >= GameSettings.TRANSITION_SHOW_ORIGINAL:
                self._transition_state      = "fade_to_fullscreen"
                self._transition_start_time = time.time()

        elif state == "fade_to_fullscreen":
            alpha   = min(1.0, elapsed / GameSettings.TRANSITION_FADE_FULLSCREEN)
            h, w    = frame.shape[:2]
            cur_w   = int(fi.shape[1] + (w - fi.shape[1]) * alpha)
            cur_h   = int(fi.shape[0] + (h - fi.shape[0]) * alpha)
            cur_x   = (w - cur_w) // 2
            cur_y   = (h - cur_h) // 2
            try:
                frame[cur_y:cur_y+cur_h, cur_x:cur_x+cur_w] = cv2.resize(fi, (cur_w, cur_h))
            except Exception:
                frame[:] = cv2.resize(fi, (w, h))
            if elapsed >= GameSettings.TRANSITION_FADE_FULLSCREEN:
                self._transition_state      = "show_fullscreen"
                self._transition_start_time = time.time()

        elif state == "show_fullscreen":
            h, w = frame.shape[:2]
            frame[:] = cv2.resize(fi, (w, h))
            if elapsed >= GameSettings.TRANSITION_SHOW_FULLSCREEN:
                # Tear down window + camera, then play video
                self._teardown_cv()
                if self.video_path:
                    geo = self._game_screen_geometry or (0, 0, 1920, 1080)
                    self._video.play(self.video_path, *geo)
                else:
                    self._on_complete()
                return True

        return False

    def _on_video_finished(self, success: bool) -> None:
        self._on_complete()

    # ------------------------------------------------------------------
    # FPS bookkeeping
    # ------------------------------------------------------------------

    def _update_fps(self, current_time: float) -> None:
        if self._prev_time > 0:
            fps = 1.0 / max(current_time - self._prev_time, 1e-9)
            self._fps_values.append(fps)
            if len(self._fps_values) > 30:
                self._fps_values.pop(0)
        self._prev_time = current_time

    # ------------------------------------------------------------------
    # Background
    # ------------------------------------------------------------------

    def _load_background(self) -> np.ndarray:
        path = Paths.GAME_BACKGROUND
        if os.path.exists(path):
            bg = cv2.imread(path)
            if bg is not None:
                return cv2.resize(bg, (GameSettings.FRAME_WIDTH, GameSettings.FRAME_HEIGHT))
        # Fallback: dark gradient
        img = np.zeros((GameSettings.FRAME_HEIGHT, GameSettings.FRAME_WIDTH, 3), dtype=np.uint8)
        img[:] = (40, 30, 20)
        return img

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _teardown_cv(self) -> None:
        """Destroy the OpenCV window and release the camera."""
        try:
            cv2.destroyWindow(self.WINDOW_NAME)
            cv2.waitKey(1)
        except Exception:
            pass
        if self._cap:
            self._cap.release()
            self._cap = None
        if self._tracker:
            self._tracker.close()
            self._tracker = None

    def _cleanup(self) -> None:
        print("PuzzleGame: cleanup started.")
        self.is_running = False
        self._teardown_cv()

        if self._video and self._video.is_playing:
            self._video.stop()

        if self._sounds:
            self._sounds.close()
            self._sounds = None

        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
        print("PuzzleGame: cleanup finished.")
