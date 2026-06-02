# PS4 PKGVault - api_pkg.py

## Description

`api_pkg.py` enrichit les informations locales récupérées par `read_pkg.py` grâce à l'API RAWG.

Le script permet :

* Lecture du PKG
* Recherche RAWG
* Téléchargement de la jaquette
* Téléchargement des screenshots
* Génération d'un fichier JSON complet

---

## Fonctionnalités

### Lecture locale

Utilise :

```python
get_pkg_info()
```

pour récupérer :

* Titre
* Title ID
* Content ID
* Firmware
* Région
* Version

### Recherche RAWG

Recherche automatique du jeu à partir du titre nettoyé.

Exemple :

```text
LEGO® Party™ PS4
```

devient :

```text
LEGO Party
```

### Informations récupérées

* Nom officiel
* Date de sortie
* Note RAWG
* Genres
* Plateformes
* Développeurs
* Éditeurs
* Site web
* Description
* Jaquette
* Screenshots

---

## Priorité des jaquettes

### Priorité 1

Jaquette extraite du PKG :

```text
assets/covers/CUSAxxxxx.png
```

(issue de `icon0.png`)

### Priorité 2

Jaquette RAWG :

```text
assets/covers/CUSAxxxxx.jpg
```

Uniquement si aucune jaquette locale n'existe.

---

## Screenshots

Les screenshots sont enregistrés dans :

```text
assets/screenshots/CUSAxxxxx/
```

Exemple :

```text
assets/screenshots/CUSA13367/
├── 01.jpg
├── 02.jpg
├── 03.jpg
```

---

## JSON généré

```text
assets/json/CUSA13367.pkgvault.json
```

Structure :

```json
{
  "pkg": {},
  "api": {},
  "assets": {}
}
```

---

## Installation

```bash
pip install requests
```

---

## Utilisation

### Asterix XXL 2

```bash
python tools/api_pkg.py "F:\PS4 JailBreak\Games - Copie\Asterix and Obelix XXL 2 Roman Rumble in Las Vegum\Game\[SuperPSX]-Asterix.and.Obelix.XXL.2.Roman.Rumble.in.Las.Vegum.v1.00-CUSA13367-PS4.pkg" "VOTRE_CLE_RAWG"
```

### Mise à jour

```bash
python tools/api_pkg.py "F:\PS4 JailBreak\Games - Copie\Asterix and Obelix XXL 2 Roman Rumble in Las Vegum\Update\[SuperPSX]-Asterix.and.Obelix.XXL.2.Roman.Rumble.in.Las.Vegum.Update.v1.03-CUSA13367-PS4.pkg" "VOTRE_CLE_RAWG"
```

### LEGO Party

```bash
python tools/api_pkg.py "F:\PS4 JailBreak\Games - Copie\Lego Party\Game\[SuperPSX]-LEGO.Party_CUSA53974_v1.00_[12.00]-PS4.pkg" "VOTRE_CLE_RAWG"
```

### LEGO Party Backport

```bash
python tools/api_pkg.py "F:\PS4 JailBreak\Games - Copie\Lego Party\Backport\[SuperPSX]-LEGO.Party_CUSA53974_v1.06_BACKPORT_[5.05-6.72-7.xx-9.00-11.00-12.00]-PS4.pkg" "VOTRE_CLE_RAWG"
```

---

## Arborescence du projet

```text
project/
│
├── assets/
│   ├── covers/
│   ├── screenshots/
│   └── json/
│
└── tools/
    ├── read_pkg.py
    └── api_pkg.py
```

---

## Workflow

1. Lecture du PKG
2. Extraction des informations locales
3. Recherche RAWG
4. Téléchargement de la jaquette si nécessaire
5. Téléchargement des screenshots
6. Génération du JSON final

---

## Utilisation dans PS4 PKGVault

Ce module est le connecteur de métadonnées externes du projet.

Il permet de créer automatiquement des fiches complètes pour les jeux PS4 avec médias et métadonnées.
