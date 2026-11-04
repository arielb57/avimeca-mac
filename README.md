# AviMeca Mac + Regressi Mac

Équivalents macOS d'**AviMeca** (pointage de vidéos image par image) et de **Regressi**
(graphiques, vitesses/accélérations, modélisation), deux logiciels Windows de TP de physique.

## Lancer

1. Dézipper le dossier (par ex. sur le Bureau).
2. Double-cliquer **`Lancer AviMeca.command`**.
   - Si macOS bloque (« développeur non identifié ») : clic droit → **Ouvrir** → **Ouvrir**.
   - Ou dans le Terminal : `bash ~/Desktop/avimeca-mac/"Lancer AviMeca.command"`
3. La première fois, l'installation prend 1 à 2 minutes. Ensuite c'est immédiat.

Si le script dit que **Tkinter manque**, copier la commande `brew install python-tk@…` qu'il affiche,
puis relancer.

## Utilisation

1. **Ouvrir…** : choisir la vidéo (`.avi`, `.mov`, `.mp4`).
2. **Étalonner** : cliquer deux points de distance connue (ex. la règle), saisir la distance en mètres.
3. *(optionnel)* **Définir l'origine** : cliquer le point (0, 0). Par défaut : coin bas-gauche, y vers le haut.
4. Choisir la piste (1 à 3) et cliquer l'objet : le point est enregistré et la vidéo avance d'une image.
   - `←` `→` : image précédente/suivante (`Maj` = 10 images) · `Suppr` : effacer le point de l'image.
5. **Exporter…** : fichier texte `t(s)  x(m)  y(m)` (un par piste).
6. **Analyser (Regressi)** : ouvre directement Regressi Mac avec les mesures de la piste.

## Regressi Mac

Depuis AviMeca (bouton **Analyser**), ou seul : double-cliquer **`Lancer Regressi.command`** puis
**Ouvrir mesures…** (`.txt` d'AviMeca, ou tout tableau texte/CSV avec une ligne d'en-tête ; virgule décimale acceptée).

- Colonnes calculées automatiquement : `vx`, `vy`, `v`, `ax`, `ay` (différences centrées).
- Choisir l'abscisse et l'ordonnée (ex. `t` / `y`, `t` / `vy`, `x` / `y`).
- **Modèle** : linéaire, affine ou parabole → équation et R² affichés, courbe tracée.
- **Image…** : enregistre le graphique en PNG · **Tableau…** : enregistre toutes les colonnes.
- Barre d'outils du graphique : zoom, déplacement, coordonnées du curseur.

## Limites

- Pointage manuel (pas de suivi automatique).
- Pas de lecture/écriture des fichiers `.rw3` du vrai Regressi.
- Modèles limités à linéaire, affine, parabole (pas d'exponentielle, sinus… pour l'instant).

## Tests

`python3 -m unittest test_core test_analysis -v` (vidéo d'exemple : `AVIMECA_SAMPLE=chemin/video.avi`).
