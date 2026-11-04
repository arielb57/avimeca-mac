#!/bin/bash
# Double-cliquer pour lancer Regressi Mac. La 1re fois, installe ce qu'il faut (1-2 min).
cd "$(dirname "$0")" || exit 1
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
if [ ! -x .venv/bin/python ]; then
  echo "Première installation…"
  rm -rf .venv
  if ! "$PY" -m venv .venv 2>/dev/null; then
    rm -rf .venv
    "$PY" -m venv --without-pip .venv || { echo "Création de l'environnement impossible."; read -r -p "Entrée"; exit 1; }
    curl -fsSL https://bootstrap.pypa.io/get-pip.py | .venv/bin/python - -q || { echo "Installation de pip impossible."; read -r -p "Entrée"; exit 1; }
  fi
fi
if ! .venv/bin/python -c "import cv2, matplotlib" 2>/dev/null; then
  .venv/bin/python -m pip install -q -r requirements.txt || { echo "Installation des dépendances impossible."; read -r -p "Entrée"; exit 1; }
fi
exec .venv/bin/python regressi.py "$@"
