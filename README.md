# PKGVault

**Gestionnaire de fichiers PKG PS4** — interface Windows 11, base de données locale, jaquettes HD.

---

## Présentation

PKGVault est une application de bureau Windows développée en Python/PyQt6.
Elle permet de scanner, organiser et visualiser vos fichiers PKG PS4 (jeux, DLC, updates, backports)
avec une interface moderne inspirée du Microsoft Store / Windows 11.

### Fonctionnalités principales

- Scan récursif de dossiers PKG
- Lecture directe des métadonnées depuis le fichier `param.sfo` embarqué dans chaque PKG
- Détection automatique du type : BASE / DLC / UPDATE / BACKPORT
- Affichage en grille 4 colonnes avec jaquettes HD
- Extraction automatique de `icon0.png` depuis le PKG
- Téléchargement de jaquettes via PS Store et IGDB dans l’application principale
- Base de données SQLite locale (persistance entre sessions)
- Page de détail complète : description, genres, screenshots, langues, firmware
- Relations automatiques jeu BASE ↔ DLC ↔ UPDATE
- Recherche et filtres par type
- Menu contextuel : ouvrir dossier, copier chemin, renommer, supprimer
- Vue liste triable (alternative à la grille)

---

## Technologies

| Technologie | Version | Usage |
|---|---|---|
| Python | 3.13+ | Langage principal |
| PyQt6 | 6.x | Interface graphique |
| SQLite | 3.x | Base de données locale |
| Pillow | 10.x | Traitement des images |
| Requests | 2.x | Appels API HTTP |
| IGDB API | v4 | Métadonnées des jeux dans l’application principale |
| RAWG API | v2 | Métadonnées via l’outil CLI `tools/api_pkg.py` |
| PS Store API | — | Jaquettes officielles |

---

## Installation

### Prérequis

- Windows 10/11
- Python 3.13+
- pip

### Étapes

```bash
# 1. Cloner ou télécharger le projet
cd PKGVault

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# 3. Installer les dépendances
pip install PyQt6 requests Pillow

# 4. Lancer l'application
python main.py
```

---

## Structure du projet

```
PKGVault/
├── assets/
│   └── icons/              ← Icône de l'application
├── cache/
│   ├── covers/             ← Jaquettes téléchargées
│   └── screenshots/        ← Screenshots téléchargés
├── core/
│   ├── __init__.py
│   ├── sfo_parser.py       ← Lecture param.sfo depuis PKG
│   ├── pkg_reader.py       ← Lecture header PKG
│   ├── scanner.py          ← Scan récursif de dossiers
│   ├── database.py         ← Base de données SQLite
│   ├── settings.py         ← Persistance des préférences
│   ├── cover_loader.py     ← Extraction icon0.png
│   └── api_client.py       ← IGDB pour les métadonnées
├── ui/
│   ├── __init__.py
│   ├── main_window.py      ← Fenêtre principale
│   ├── topbar.py           ← Barre de navigation
│   ├── subbar.py           ← Filtres et tri
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── library_page.py ← Grille des jaquettes
│   │   ├── detail_page.py  ← Page de détail complète
│   │   ├── folders_page.py ← Gestion des dossiers
│   │   ├── settings_page.py← Paramètres
│   │   └── credits_page.py ← À propos
│   └── widgets/
│       ├── __init__.py
│       ├── pkg_card.py     ← Carte jaquette
│       └── status_bar.py   ← Barre de statut
├── main.py                 ← Point d'entrée
├── ps4pkgvault.db          ← Base de données locale (généré, ignoré par Git)
├── settings.json           ← Préférences (généré, ignoré par Git)
└── requirements.txt
```

---

## Format PKG PS4

### Header PKG

| Offset | Taille | Description |
|---|---|---|
| `0x000` | 4 bytes | Magic : `0x7F434E54` |
| `0x010` | 2 bytes | Nombre d'entrées (BE) |
| `0x018` | 4 bytes | Offset table des entrées (BE) |
| `0x018` | 4 bytes | Content type |
| `0x040` | 36 bytes | Content-ID (ASCII) |

### Entrées PKG (32 bytes chacune)

| Offset | Description |
|---|---|
| `0x00` | Entry ID (uint32 BE) |
| `0x10` | Data offset (uint32 BE) |
| `0x14` | Data size (uint32 BE) |

### IDs importants

| ID | Contenu |
|---|---|
| `0x1000` | `param.sfo` |
| `0x1200` | `icon0.png` |

### param.sfo — clés utilisées

| Clé | Type | Description |
|---|---|---|
| `TITLE` | UTF-8 | Titre du jeu |
| `CONTENT_ID` | UTF-8 | Content-ID complet |
| `APP_VER` | UTF-8 | Version de l'application |
| `SYSTEM_VER` | INT32 | Firmware minimum requis |
| `CATEGORY` | UTF-8 | Type : gd / gp / ac |
| `LANG` | INT32 | Bitmask des langues |

### Types PKG (CATEGORY)

| Valeur | Type PKGVault |
|---|---|
| `gd`, `gda`, `gdo` | BASE |
| `gp`, `gdp` | UPDATE |
| `ac` | DLC |
| Nom fichier `BACKPORT` | BACKPORT |

---

## APIs externes

### IGDB

- Utilisé par l’application principale via `core/api_client.py`
- URL : https://api.igdb.com
- Requiert un compte Twitch Developer gratuit
- Fournit : titre, description, genres, date de sortie, développeur, éditeur, jaquette, screenshots et vidéos
- Identifiants à renseigner dans les paramètres de l’application

### PlayStation Store

- Pas de clé requise
- Utilisé en priorité pour certaines jaquettes officielles quand disponible

### RAWG.io

- Utilisé par l’outil CLI `tools/api_pkg.py`
- URL : https://rawg.io/apidocs
- Fournit : titre, description, genres, rating, date de sortie et screenshots
- La jaquette RAWG est téléchargée uniquement si aucune jaquette locale extraite du PKG n’existe

---

## Base de données

### Table `games`

| Colonne | Type | Description |
|---|---|---|
| `content_id` | TEXT UNIQUE | Identifiant unique PS4 |
| `title` | TEXT | Titre depuis param.sfo |
| `title_api` | TEXT | Titre depuis l’API externe |
| `type` | TEXT | game / dlc / update / backport |
| `firmware` | TEXT | Firmware minimum |
| `cover_path` | TEXT | Chemin local jaquette |
| `description` | TEXT | Description depuis l’API externe |
| `genres` | TEXT | JSON array |
| `languages` | TEXT | JSON array |
| `api_fetched` | INTEGER | 0 = pas encore appelé |

### Table `game_relations`

| Colonne | Description |
|---|---|
| `base_content_id` | Jeu BASE |
| `related_id` | DLC ou UPDATE lié |
| `relation_type` | dlc / update / backport |

### Table `folders`

| Colonne | Description |
|---|---|
| `path` | Chemin absolu |
| `date_added` | Date d'ajout |
| `enabled` | 1 = actif |

---

## Développeur

**Sébastien** — RC Informatique  
6 Place des Halles, 03000 Moulins (Allier), France  
Téléphone : 04 70 44 39 36 / 06 51 97 55 42  
Site : rc-informatique.fr

---

## Crédits

- Interface développée avec l'assistance de **Claude** (Anthropic)
- Design inspiré de **Windows 11 / Microsoft Store**
- Données de jeux via **IGDB** dans l’application principale
- Jaquettes via **PlayStation Store**

---

## Licence

Usage personnel uniquement.  
Ce logiciel ne encourage aucune violation des droits d'auteur.  
Les fichiers PKG utilisés doivent provenir de jeux dont vous êtes propriétaire.

---

*PKGVault v1.0.0 — 2026*
