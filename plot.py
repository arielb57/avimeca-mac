"""Tracé des mesures et du modèle (matplotlib, sans Tkinter)."""
import numpy as np
from matplotlib.figure import Figure

from analysis import MODELS, equation, fit, predict


def draw(fig: Figure, cols, xk: str, yk: str, model_label: str | None) -> str:
    """Trace y(x) et le modèle éventuel sur fig. Renvoie le texte de l'équation ('' sans modèle)."""
    fig.clear()
    ax = fig.add_subplot(111)
    x, y = cols[xk], cols[yk]
    ax.plot(x, y, "+", color="#1e66d0", markersize=9, mew=1.6, label="mesures")
    eq = ""
    if model_label:
        kind = MODELS[model_label]
        coefs, r2 = fit(kind, x, y)
        xs = np.linspace(np.nanmin(x), np.nanmax(x), 200)
        ax.plot(xs, predict(kind, coefs, xs), "-", color="#d32f2f", label="modèle")
        eq = equation(kind, coefs, r2)
        ax.set_title(eq, fontsize=10)
    ax.set_xlabel(xk)
    ax.set_ylabel(yk)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    return eq
