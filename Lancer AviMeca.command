#!/bin/bash
# Double-cliquer pour lancer AviMeca Mac. La 1re fois, installe ce qu'il faut (1-2 min).
cd "$(dirname "$0")" || exit 1
# Environnement Python hors du dossier : le Bureau/Documents synchronisés par iCloud
# rendent les fichiers de .venv illisibles (« Operation timed out »).
VENV="$HOME/Library/Application Support/AviMeca-Mac/venv"
mkdir -p "$(dirname "$VENV")"
PY=""
for c in /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Python 3 introuvable. Installez-le : https://www.python.org/downloads/macos/"; read -r -p "Entrée pour fermer"; exit 1
fi
if ! "$PY" -c "import tkinter" 2>/dev/null; then
  V=$("$PY" -c 'import sys;print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
  echo "Tkinter manque pour Python $V. Dans le Terminal, tapez :"
  echo "    brew install python-tk@$V"
  echo "puis relancez ce fichier."; read -r -p "Entrée pour fermer"; exit 1
fi
if ! "$VENV/bin/python" -c "" 2>/dev/null; then
  echo "Première installation…"
  rm -rf "$VENV"
  if ! "$PY" -m venv "$VENV" 2>/dev/null; then
    rm -rf "$VENV"
    "$PY" -m venv --without-pip "$VENV" || { echo "Création de l'environnement impossible."; read -r -p "Entrée"; exit 1; }
    curl -fsSL https://bootstrap.pypa.io/get-pip.py | "$VENV/bin/python" - -q || { echo "Installation de pip impossible."; read -r -p "Entrée"; exit 1; }
  fi
fi
if ! "$VENV/bin/python" -c "import cv2, matplotlib" 2>/dev/null; then
  "$VENV/bin/python" -m pip install -q -r requirements.txt || { echo "Installation des dépendances impossible."; read -r -p "Entrée"; exit 1; }
fi
exec "$VENV/bin/python" app.py "$@"
