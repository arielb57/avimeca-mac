"""Regressi Mac — graphiques, vitesses/accélérations et modélisation des mesures.

Lancer seul : python3 regressi.py [mesures.txt]   (ou depuis AviMeca : bouton « Analyser »)
"""
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.figure import Figure

from analysis import MODELS, add_kinematics, load_txt
from plot import draw


class RegressiWindow(tk.Toplevel):
    def __init__(self, master, cols=None, title="Regressi Mac"):
        super().__init__(master)
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        self.title(title)
        self.geometry("980x700")
        self.cols = {}
        bar = ttk.Frame(self, padding=6)
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(bar, text="Ouvrir mesures…", command=self.open_dialog).pack(side=tk.LEFT)
        ttk.Label(bar, text="  Abscisse :").pack(side=tk.LEFT)
        self.xvar, self.yvar = tk.StringVar(), tk.StringVar()
        self.xbox = ttk.Combobox(bar, textvariable=self.xvar, width=10, state="readonly")
        self.xbox.pack(side=tk.LEFT)
        ttk.Label(bar, text="  Ordonnée :").pack(side=tk.LEFT)
        self.ybox = ttk.Combobox(bar, textvariable=self.yvar, width=10, state="readonly")
        self.ybox.pack(side=tk.LEFT)
        ttk.Label(bar, text="  Modèle :").pack(side=tk.LEFT)
        self.mvar = tk.StringVar(value="aucun")
        self.mbox = ttk.Combobox(bar, textvariable=self.mvar, values=["aucun", *MODELS],
                                 width=26, state="readonly")
        self.mbox.pack(side=tk.LEFT)
        ttk.Button(bar, text="Image…", command=self.save_png).pack(side=tk.RIGHT)
        ttk.Button(bar, text="Tableau…", command=self.save_table).pack(side=tk.RIGHT, padx=4)
        for box in (self.xbox, self.ybox, self.mbox):
            box.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        self.fig = Figure(figsize=(8, 5.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        NavigationToolbar2Tk(self.canvas, self).update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.eq = ttk.Label(self, text="", padding=6, font=("Menlo", 13))
        self.eq.pack(side=tk.BOTTOM, fill=tk.X)
        if cols:
            self.set_data(cols)

    def set_data(self, cols):
        self.cols = add_kinematics(cols)
        names = list(self.cols)
        self.xbox["values"] = self.ybox["values"] = names
        tk_ = next((n for n in names if n.lower().startswith("t")), names[0])
        yk = next((n for n in names if n.lower().startswith("y")), names[-1])
        self.xvar.set(tk_)
        self.yvar.set(yk)
        self.refresh()

    def open_dialog(self):
        p = filedialog.askopenfilename(parent=self, filetypes=[("Mesures", "*.txt *.csv"), ("Tous", "*.*")])
        if p:
            try:
                self.set_data(load_txt(p))
            except (OSError, ValueError) as e:
                messagebox.showerror("Erreur", str(e), parent=self)

    def refresh(self):
        if not self.cols:
            return
        m = None if self.mvar.get() == "aucun" else self.mvar.get()
        try:
            eq = draw(self.fig, self.cols, self.xvar.get(), self.yvar.get(), m)
        except ValueError as e:
            eq = str(e)
            draw(self.fig, self.cols, self.xvar.get(), self.yvar.get(), None)
        self.eq.config(text=eq)
        self.canvas.draw()

    def save_png(self):
        p = filedialog.asksaveasfilename(parent=self, defaultextension=".png", initialfile="graphique.png")
        if p:
            self.fig.savefig(p, dpi=150)

    def save_table(self):
        if not self.cols:
            return
        p = filedialog.asksaveasfilename(parent=self, defaultextension=".txt", initialfile="tableau.txt")
        if p:
            names = list(self.cols)
            data = np.column_stack([self.cols[n] for n in names])
            np.savetxt(p, data, delimiter="\t", header="\t".join(names), comments="", fmt="%.5g")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    w = RegressiWindow(root)
    w.protocol("WM_DELETE_WINDOW", root.destroy)
    if len(sys.argv) > 1:
        w.set_data(load_txt(sys.argv[1]))
    root.mainloop()
