"""AviMeca pour Mac — pointage de vidéos pour l'analyse de mouvement (Tkinter + OpenCV).

Lancer : python3 app.py [video.avi]
Raccourcis : ← → image précédente/suivante ; Maj+← → 10 images ; Suppr = effacer le point de l'image.
"""
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import cv2

from core import Calibration, Session, open_video, read_frame

TRACK_COLORS = ["#e53935", "#1e88e5", "#43a047"]
MODE_IDLE, MODE_CAL1, MODE_CAL2, MODE_ORIGIN = "idle", "cal1", "cal2", "origin"


def frame_to_ppm(frame_bgr, w, h) -> bytes:
    """Convertit une image OpenCV en PPM (format lu nativement par tk.PhotoImage)."""
    rgb = cv2.cvtColor(cv2.resize(frame_bgr, (w, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    return b"P6 %d %d 255\n" % (w, h) + rgb.tobytes()


class App(tk.Tk):
    def __init__(self, video_path=None):
        super().__init__()
        self.title("AviMeca Mac")
        self.geometry("1100x760")
        self.cap = None
        self.session: Session | None = None
        self.frame_idx = 0
        self.track = tk.IntVar(value=1)
        self.mode = MODE_IDLE
        self.cal_points: list[tuple[float, float]] = []
        self.scale = 1.0  # écran = image * scale
        self.offset = (0, 0)
        self.current_frame = None
        self._build_ui()
        self.bind("<Left>", lambda e: self.step(-1))
        self.bind("<Right>", lambda e: self.step(1))
        self.bind("<Shift-Left>", lambda e: self.step(-10))
        self.bind("<Shift-Right>", lambda e: self.step(10))
        self.bind("<Delete>", lambda e: self.delete_here())
        self.bind("<BackSpace>", lambda e: self.delete_here())
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", lambda e: self.show())
        if video_path:
            self.load(video_path)

    # ---------- interface ----------
    def _build_ui(self):
        bar = ttk.Frame(self, padding=6)
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(bar, text="Ouvrir…", command=self.open_dialog).pack(side=tk.LEFT)
        ttk.Button(bar, text="Étalonner", command=self.start_calibration).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="Définir l'origine", command=self.start_origin).pack(side=tk.LEFT)
        ttk.Label(bar, text="Piste :").pack(side=tk.LEFT, padx=(14, 2))
        for i in (1, 2, 3):
            ttk.Radiobutton(bar, text=str(i), value=i, variable=self.track, command=self.show).pack(side=tk.LEFT)
        ttk.Button(bar, text="Exporter…", command=self.export).pack(side=tk.RIGHT)
        ttk.Button(bar, text="Analyser (Regressi)", command=self.analyse).pack(side=tk.RIGHT, padx=4)

        self.canvas = tk.Canvas(self, bg="#222", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        nav = ttk.Frame(self, padding=6)
        nav.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(nav, text="◀", width=3, command=lambda: self.step(-1)).pack(side=tk.LEFT)
        ttk.Button(nav, text="▶", width=3, command=lambda: self.step(1)).pack(side=tk.LEFT, padx=4)
        self.slider = ttk.Scale(nav, from_=0, to=0, command=self._on_slider)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.info = ttk.Label(nav, text="Ouvrez une vidéo pour commencer.", width=48)
        self.info.pack(side=tk.LEFT)
        self.status = ttk.Label(self, text="", anchor="w", padding=(6, 2))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, text):
        self.status.config(text=text)

    # ---------- vidéo ----------
    def open_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Vidéos", "*.avi *.mov *.mp4 *.mkv"), ("Tous", "*.*")])
        if path:
            self.load(path)

    def load(self, path):
        try:
            cap, session = open_video(path)
        except OSError as e:
            messagebox.showerror("Erreur", str(e))
            return
        if self.cap:
            self.cap.release()
        self.cap, self.session = cap, session
        self.slider.config(to=max(session.n_frames - 1, 1))
        self.frame_idx = 0
        self.show()
        self.set_status(f"{path} — {session.width}×{session.height}, {session.fps:.2f} i/s, {session.n_frames} images")

    def step(self, n):
        if not self.session:
            return
        self.goto(min(max(self.frame_idx + n, 0), self.session.n_frames - 1))

    def goto(self, idx):
        self.frame_idx = idx
        self.slider.set(idx)
        self.show()

    def _on_slider(self, value):
        if self.session and int(float(value)) != self.frame_idx:
            self.frame_idx = int(float(value))
            self.show()

    # ---------- affichage ----------
    def show(self):
        if not self.session:
            return
        frame = read_frame(self.cap, self.frame_idx)
        if frame is None:
            return
        self.current_frame = frame
        cw, ch = max(self.canvas.winfo_width(), 10), max(self.canvas.winfo_height(), 10)
        s = self.session
        self.scale = min(cw / s.width, ch / s.height)
        dw, dh = int(s.width * self.scale), int(s.height * self.scale)
        self.offset = ((cw - dw) // 2, (ch - dh) // 2)
        self.photo = tk.PhotoImage(data=frame_to_ppm(frame, dw, dh), format="PPM")
        self.canvas.delete("all")
        self.canvas.create_image(self.offset[0], self.offset[1], anchor="nw", image=self.photo)
        self._draw_overlays()
        self.info.config(text=f"Image {self.frame_idx + 1}/{s.n_frames}   t = {self.frame_idx / s.fps:.3f} s")

    def _to_screen(self, px, py):
        return self.offset[0] + px * self.scale, self.offset[1] + py * self.scale

    def _draw_overlays(self):
        s = self.session
        for tnum, pts in s.tracks.items():
            color = TRACK_COLORS[(tnum - 1) % 3]
            prev = None
            for f in sorted(pts):
                x, y = self._to_screen(*pts[f])
                r = 6 if f == self.frame_idx else 3
                self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color,
                                        fill=color if f == self.frame_idx else "", width=2)
                if prev:
                    self.canvas.create_line(*prev, x, y, fill=color, width=1)
                prev = (x, y)
        for i, (px, py) in enumerate(self.cal_points):
            x, y = self._to_screen(px, py)
            self.canvas.create_line(x - 8, y, x + 8, y, fill="#ffeb3b", width=2)
            self.canvas.create_line(x, y - 8, x, y + 8, fill="#ffeb3b", width=2)
        if s.calibration:
            p1 = self._to_screen(*s.calibration.p1)
            p2 = self._to_screen(*s.calibration.p2)
            self.canvas.create_line(*p1, *p2, fill="#ffeb3b", dash=(4, 3))
        if s.origin_px:
            x, y = self._to_screen(*s.origin_px)
            self.canvas.create_text(x + 8, y - 8, text="O", fill="#ffeb3b", anchor="sw")

    # ---------- clics ----------
    def _screen_to_image(self, x, y):
        px = (x - self.offset[0]) / self.scale
        py = (y - self.offset[1]) / self.scale
        if 0 <= px < self.session.width and 0 <= py < self.session.height:
            return px, py
        return None

    def on_click(self, event):
        if not self.session:
            return
        pt = self._screen_to_image(event.x, event.y)
        if pt is None:
            return
        if self.mode == MODE_CAL1:
            self.cal_points = [pt]
            self.mode = MODE_CAL2
            self.set_status("Étalonnage : cliquez le second point (distance connue).")
        elif self.mode == MODE_CAL2:
            self.cal_points.append(pt)
            self.mode = MODE_IDLE
            dist = simpledialog.askfloat("Étalonnage", "Distance réelle entre les deux points (m) :",
                                         minvalue=1e-6, parent=self)
            if dist:
                self.session.calibration = Calibration(self.cal_points[0], self.cal_points[1], dist)
                self.set_status(f"Étalonné : {self.session.calibration.m_per_px * 1000:.3f} mm/px")
            else:
                self.set_status("Étalonnage annulé.")
            self.cal_points = []
        elif self.mode == MODE_ORIGIN:
            self.session.origin_px = pt
            self.mode = MODE_IDLE
            self.set_status("Origine définie.")
        else:
            self.session.set_point(self.track.get(), self.frame_idx, *pt)
            self.set_status(f"Piste {self.track.get()} : point image {self.frame_idx + 1} enregistré.")
            self.step(1)  # passe à l'image suivante, pratique pour pointer toute la vidéo
            return
        self.show()

    def start_calibration(self):
        if not self.session:
            return
        self.mode = MODE_CAL1
        self.set_status("Étalonnage : cliquez le premier point.")

    def start_origin(self):
        if not self.session:
            return
        self.mode = MODE_ORIGIN
        self.set_status("Cliquez sur l'origine (x = 0, y = 0).")

    def delete_here(self):
        if self.session:
            self.session.delete_point(self.track.get(), self.frame_idx)
            self.show()

    # ---------- analyse ----------
    def analyse(self):
        """Ouvre Regressi Mac avec les mesures de la piste courante."""
        if not self.session:
            return
        if not self.session.calibration:
            messagebox.showwarning("Analyse", "Étalonnez d'abord la vidéo.")
            return
        rows = self.session.rows(self.track.get())
        if len(rows) < 2:
            messagebox.showwarning("Analyse", "Pointez au moins 2 images sur cette piste.")
            return
        import numpy as np
        from regressi import RegressiWindow
        a = np.array(rows)
        RegressiWindow(self, {"t(s)": a[:, 0], "x(m)": a[:, 1], "y(m)": a[:, 2]},
                       title=f"Regressi Mac — piste {self.track.get()}")

    # ---------- export ----------
    def export(self):
        if not self.session:
            return
        if not self.session.calibration:
            messagebox.showwarning("Export", "Étalonnez d'abord la vidéo.")
            return
        base = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="mesures.txt",
                                            filetypes=[("Texte tabulé", "*.txt")])
        if not base:
            return
        stem = base[:-4] if base.lower().endswith(".txt") else base
        written = []
        for tnum in sorted(self.session.tracks):
            if not self.session.tracks[tnum]:
                continue
            path = f"{stem}_piste{tnum}.txt" if len(self.session.tracks) > 1 else base
            n = self.session.export_track(tnum, path)
            written.append(f"{path} ({n} points)")
        if written:
            messagebox.showinfo("Export", "Fichiers écrits :\n" + "\n".join(written))
        else:
            messagebox.showwarning("Export", "Aucun point à exporter.")


if __name__ == "__main__":
    App(sys.argv[1] if len(sys.argv) > 1 else None).mainloop()
