"""Logique de pointage vidéo (équivalent AviMeca) — sans interface graphique.

Modèle :
- une vidéo à fps constant ;
- un étalonnage : deux points pixel + distance réelle en mètres -> mètres par pixel ;
- une origine en pixels (par défaut : coin bas-gauche de l'image) ; y est orienté vers le haut ;
- des « pistes » (1 à 3), chacune = {numéro d'image: (px, py)}.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import cv2


@dataclass
class Calibration:
    p1: tuple[float, float]
    p2: tuple[float, float]
    distance_m: float

    @property
    def m_per_px(self) -> float:
        d_px = math.dist(self.p1, self.p2)
        if d_px == 0 or self.distance_m <= 0:
            raise ValueError("Étalonnage invalide : les deux points doivent être distincts et la distance > 0.")
        return self.distance_m / d_px


@dataclass
class Session:
    fps: float
    width: int
    height: int
    n_frames: int
    calibration: Calibration | None = None
    origin_px: tuple[float, float] | None = None  # None -> coin bas-gauche
    tracks: dict[int, dict[int, tuple[float, float]]] = field(default_factory=lambda: {1: {}})

    # --- pointage -------------------------------------------------------
    def set_point(self, track: int, frame: int, px: float, py: float) -> None:
        self.tracks.setdefault(track, {})[frame] = (px, py)

    def delete_point(self, track: int, frame: int) -> None:
        self.tracks.get(track, {}).pop(frame, None)

    # --- conversion -----------------------------------------------------
    def to_physical(self, px: float, py: float) -> tuple[float, float]:
        if self.calibration is None:
            raise ValueError("Étalonnez d'abord la vidéo (deux points + distance réelle).")
        s = self.calibration.m_per_px
        ox, oy = self.origin_px if self.origin_px is not None else (0.0, float(self.height))
        return (px - ox) * s, (oy - py) * s  # y vers le haut

    def rows(self, track: int) -> list[tuple[float, float, float]]:
        """Lignes (t, x, y) triées par temps pour une piste."""
        out = []
        for frame in sorted(self.tracks.get(track, {})):
            px, py = self.tracks[track][frame]
            x, y = self.to_physical(px, py)
            out.append((frame / self.fps, x, y))
        return out

    # --- export ---------------------------------------------------------
    def export_track(self, track: int, path: str | Path) -> int:
        rows = self.rows(track)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("t(s)\tx(m)\ty(m)\n")
            for t, x, y in rows:
                f.write(f"{t:.4f}\t{x:.5f}\t{y:.5f}\n")
        return len(rows)


def open_video(path: str | Path) -> tuple[cv2.VideoCapture, Session]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise OSError(f"Impossible d'ouvrir la vidéo : {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return cap, Session(fps=fps, width=w, height=h, n_frames=n)


def read_frame(cap: cv2.VideoCapture, index: int):
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    return frame if ok else None
