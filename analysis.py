"""Calculs façon Regressi : lecture des mesures, dérivées, modélisation (sans interface)."""
from __future__ import annotations

import numpy as np

MODELS = {
    "linéaire  y = a·x": "lin",
    "affine  y = a·x + b": "aff",
    "parabole  y = a·x² + b·x + c": "par",
}


def load_txt(path: str) -> dict[str, np.ndarray]:
    """Lit un texte tabulé (ou ; ou espaces) avec une ligne d'en-tête. Accepte la virgule décimale."""
    with open(path, encoding="utf-8-sig") as f:
        lines = [l.strip() for l in f if l.strip()]
    if len(lines) < 2:
        raise ValueError("Fichier vide ou sans données.")
    sep = "\t" if "\t" in lines[0] else (";" if ";" in lines[0] else None)
    header = [h.strip() for h in lines[0].split(sep)]
    rows = []
    for l in lines[1:]:
        cells = [c.strip().replace(",", ".") for c in l.split(sep)]
        try:
            rows.append([float(c) for c in cells[: len(header)]])
        except ValueError:
            continue  # ligne non numérique ignorée
    if not rows:
        raise ValueError("Aucune ligne numérique trouvée.")
    data = np.array(rows)
    return {name: data[:, i] for i, name in enumerate(header)}


def derivative(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Dérivée par différences centrées (comme Regressi), décentrées aux bords."""
    if len(t) < 2:
        return np.full_like(y, np.nan, dtype=float)
    return np.gradient(y, t)


def add_kinematics(cols: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Ajoute vx, vy, v, ax, ay si les colonnes t, x, y existent (noms avec ou sans unité)."""
    def find(prefix):
        for k in cols:
            if k.split("(")[0].strip().lower() == prefix:
                return k
        return None

    kt, kx, ky = find("t"), find("x"), find("y")
    out = dict(cols)
    if kt is None:
        return out
    t = cols[kt]
    if kx:
        out["vx(m/s)"] = derivative(t, cols[kx])
        out["ax(m/s²)"] = derivative(t, out["vx(m/s)"])
    if ky:
        out["vy(m/s)"] = derivative(t, cols[ky])
        out["ay(m/s²)"] = derivative(t, out["vy(m/s)"])
    if kx and ky:
        out["v(m/s)"] = np.hypot(out["vx(m/s)"], out["vy(m/s)"])
    return out


def fit(kind: str, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    """Ajuste le modèle. Renvoie (coefficients, R²). lin: [a] ; aff: [a, b] ; par: [a, b, c]."""
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    need = {"lin": 1, "aff": 2, "par": 3}[kind]
    if len(x) < need:
        raise ValueError(f"Il faut au moins {need} points pour ce modèle.")
    if kind == "lin":
        a = float(np.dot(x, y) / np.dot(x, x))
        coefs = np.array([a])
    else:
        coefs = np.polyfit(x, y, need - 1)
    yp = predict(kind, coefs, x)
    ss_res = float(np.sum((y - yp) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return coefs, r2


def predict(kind: str, coefs: np.ndarray, x: np.ndarray) -> np.ndarray:
    return coefs[0] * x if kind == "lin" else np.polyval(coefs, x)


def equation(kind: str, coefs: np.ndarray, r2: float) -> str:
    f = lambda v: f"{v:.4g}"
    if kind == "lin":
        s = f"y = {f(coefs[0])}·x"
    elif kind == "aff":
        s = f"y = {f(coefs[0])}·x + {f(coefs[1])}"
    else:
        s = f"y = {f(coefs[0])}·x² + {f(coefs[1])}·x + {f(coefs[2])}"
    return f"{s}    (R² = {r2:.4f})".replace("+ -", "− ")
