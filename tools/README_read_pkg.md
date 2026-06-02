# PS4 PKGVault - read_pkg.py

## Description

`read_pkg.py` est le moteur d'analyse des fichiers PKG PS4 utilisé par PS4 PKGVault.

Il permet de :

* Lire les informations du header PKG
* Trouver et parser le `param.sfo`
* Extraire les métadonnées du jeu
* Détecter les images PNG embarquées
* Exporter automatiquement `icon0.png`
* Identifier la région, le firmware et le SDK

---

## Fonctionnalités

### Lecture du PKG

* Vérification du Magic Number
* Validation du fichier PKG
* Lecture du Content ID
* Recherche automatique du `param.sfo`

### Analyse du param.sfo

Extraction automatique de :

* TITLE
* TITLE_ID
* CONTENT_ID
* APP_VER
* VERSION
* SYSTEM_VER
* CATEGORY
* LANG
* PUBTOOLINFO

### Informations calculées

* Région du Store
* Firmware minimum requis
* Version SDK
* Type de contenu
* Langues disponibles
* Nom interne du produit
* Code éditeur

### Détection des images

* Recherche de tous les PNG présents
* Extraction automatique de `icon0.png`
* Sauvegarde dans `assets/covers/`

---

## Installation

Aucune dépendance externe.

Compatible Python 3.9+

---

## Utilisation

### Analyse simple

```bash
python tools/read_pkg.py "MonJeu.pkg"
```

### Analyse avec extraction de la jaquette

```bash
python tools/read_pkg.py "MonJeu.pkg" --export-images
```

---

## Exemples réels

### Jeu complet

```bash
python tools/read_pkg.py "F:\PS4 JailBreak\Games - Copie\Asterix and Obelix XXL 2 Roman Rumble in Las Vegum\Game\[SuperPSX]-Asterix.and.Obelix.XXL.2.Roman.Rumble.in.Las.Vegum.v1.00-CUSA13367-PS4.pkg"
```

### Jeu complet avec extraction icon0.png

```bash
python tools/read_pkg.py "F:\PS4 JailBreak\Games - Copie\Asterix and Obelix XXL 2 Roman Rumble in Las Vegum\Game\[SuperPSX]-Asterix.and.Obelix.XXL.2.Roman.Rumble.in.Las.Vegum.v1.00-CUSA13367-PS4.pkg" --export-images
```

### Mise à jour

```bash
python tools/read_pkg.py "F:\PS4 JailBreak\Games - Copie\Asterix and Obelix XXL 2 Roman Rumble in Las Vegum\Update\[SuperPSX]-Asterix.and.Obelix.XXL.2.Roman.Rumble.in.Las.Vegum.Update.v1.03-CUSA13367-PS4.pkg"
```

### Backport

```bash
python tools/read_pkg.py "F:\PS4 JailBreak\Games - Copie\Lego Party\Backport\[SuperPSX]-LEGO.Party_CUSA53974_v1.06_BACKPORT_[5.05-6.72-7.xx-9.00-11.00-12.00]-PS4.pkg"
```

### LEGO Party

```bash
python tools/read_pkg.py "F:\PS4 JailBreak\Games - Copie\Lego Party\Game\[SuperPSX]-LEGO.Party_CUSA53974_v1.00_[12.00]-PS4.pkg"
```

---

## Utilisation dans un script Python

```python
from tools.read_pkg import get_pkg_info

pkg = get_pkg_info("MonJeu.pkg")

print(pkg["title"])
print(pkg["title_id"])
print(pkg["content_id"])
```

---

## Jaquettes extraites

```text
assets/
└── covers/
    └── CUSA13367.png
```

---

## Utilisation dans PS4 PKGVault

Ce module constitue la base d'analyse locale de tous les fichiers PKG du projet.
