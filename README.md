# AviMeca Mac

Équivalent macOS d'**AviMeca** (Windows) : pointage de vidéos image par image pour l'analyse
de mouvement en physique, avec export texte pour Regressi.

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
5. **Exporter…** : fichier texte `t(s)  x(m)  y(m)` (un par piste), à ouvrir dans Regressi ou un tableur.

## Limites

- Pointage manuel (pas de suivi automatique).
- Pas d'export `.rw3` natif Regressi ; l'import du `.txt` dans Regressi n'a pas encore été vérifié.

## Tests

`python3 -m unittest test_core -v` (vidéo d'exemple : `AVIMECA_SAMPLE=chemin/video.avi`).
