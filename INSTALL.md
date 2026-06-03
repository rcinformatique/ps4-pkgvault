# PKGVault — Documentation d'installation

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation pour développement](#installation-pour-développement)
3. [Installation Font Awesome](#installation-font-awesome)
4. [Configuration IGDB](#configuration-igdb)
5. [Compilation en .exe](#compilation-en-exe)
6. [Ajouter une icône](#ajouter-une-icône)
7. [Structure des dossiers générés](#structure-des-dossiers-générés)
8. [Résolution des problèmes courants](#résolution-des-problèmes-courants)

---

## Prérequis

| Outil | Version minimale | Téléchargement |
|---|---|---|
| Windows | 10 / 11 | — |
| Python | 3.13+ | [python.org](https://www.python.org/downloads/) |
| Git | 2.x | [git-scm.com](https://git-scm.com/) |
| Font Awesome | 6 Free | [fontawesome.com/download](https://fontawesome.com/download) |

> ⚠️ Lors de l'installation de Python, cocher **"Add Python to PATH"**.

---

## Installation pour développement

### 1. Cloner le dépôt

```cmd
git clone https://github.com/rcinformatique/ps4-pkgvault.git
cd ps4-pkgvault
```

### 2. Créer l'environnement virtuel

```cmd
python -m venv venv
```

### 3. Activer l'environnement virtuel

**cmd.exe :**
```cmd
venv\Scripts\activate.bat
```

**PowerShell :**
```powershell
.\venv\Scripts\Activate.ps1
```

> Si PowerShell bloque l'exécution :
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> .\venv\Scripts\Activate.ps1
> ```

Le prompt doit afficher `(venv)` devant le chemin.

### 4. Installer les dépendances

```cmd
pip install -r requirements.txt
```

### 5. Installer Font Awesome

Voir la section [Installation Font Awesome](#installation-font-awesome).

### 6. Configurer IGDB

Voir la section [Configuration IGDB](#configuration-igdb).

### 7. Lancer l'application

```cmd
python main.py
```

---

## Installation Font Awesome

Font Awesome est utilisé en **local** — aucune connexion internet requise pour les icônes.

### 1. Télécharger

Aller sur [fontawesome.com/download](https://fontawesome.com/download) et télécharger **"Free For Web"**.

### 2. Extraire et placer les fichiers

Depuis l'archive téléchargée, copier uniquement ces deux dossiers :

```
fontawesome-free-6.x.x-web/
├── css/
│   └── all.min.css        ← copier ce fichier
└── webfonts/              ← copier tout ce dossier
    ├── fa-solid-900.woff2
    ├── fa-solid-900.ttf
    ├── fa-regular-400.woff2
    ├── fa-regular-400.ttf
    ├── fa-brands-400.woff2
    └── fa-brands-400.ttf
```

Vers cette structure dans le projet :

```
ps4-pkgvault/
└── assets/
    └── fontawesome/
        ├── css/
        │   └── all.min.css
        └── webfonts/
            ├── fa-solid-900.woff2
            ├── fa-solid-900.ttf
            ├── fa-regular-400.woff2
            ├── fa-regular-400.ttf
            ├── fa-brands-400.woff2
            └── fa-brands-400.ttf
```

### 3. Vérifier dans template_engine.py

Le chemin est calculé automatiquement depuis `ui/template_engine.py` :

```python
fa_path = str(
    Path(__file__).parent.parent / "assets" / "fontawesome" / "css" / "all.min.css"
).replace("\\", "/")
```

Aucune modification manuelle nécessaire.

---

## Configuration IGDB

IGDB fournit les métadonnées des jeux (description, genres, jaquettes, screenshots).
Un compte **Twitch Developer gratuit** est requis.

### 1. Créer l'application Twitch

1. Aller sur [dev.twitch.tv/console](https://dev.twitch.tv/console)
2. Se connecter avec un compte Twitch (ou en créer un)
3. Cliquer sur **"Enregistrer votre application"**
4. Remplir :
   - **Nom** : ce que vous voulez (ex: `PKGVault`)
   - **URL de redirection OAuth** : `http://localhost`
   - **Catégorie** : `Application Integration`
5. Cliquer sur **"Créer"**

### 2. Récupérer les identifiants

1. Dans la liste de vos applications, cliquer sur **"Gérer"**
2. Copier le **Client ID**
3. Cliquer sur **"Nouveau secret"** → copier le **Client Secret**

> ⚠️ Ne partagez jamais votre Client Secret.

### 3. Renseigner dans PKGVault

1. Lancer PKGVault
2. Aller dans **Paramètres → APIs & Données**
3. Coller le **Client ID** et le **Client Secret**
4. Cliquer sur **"Tester"** pour vérifier la connexion
5. Sauvegarder

---

## Compilation en .exe

### Prérequis

L'environnement virtuel doit être activé et toutes les dépendances installées (voir [Installation pour développement](#installation-pour-développement)).

### 1. Vérifier que pkgvault.spec est à la racine

```
ps4-pkgvault/
├── main.py
├── pkgvault.spec    ← doit être ici
└── ...
```

### 2. Lancer la compilation

```cmd
pyinstaller pkgvault.spec
```

La compilation dure environ **1 à 3 minutes**.

### 3. Résultat

```
ps4-pkgvault/
├── build/           ← fichiers temporaires (ignoré par Git)
└── dist/
    └── PKGVault/
        ├── PKGVault.exe    ← exécutable principal
        ├── templates/      ← templates Jinja2 embarqués
        ├── assets/         ← Font Awesome embarqué
        └── (DLL Qt6...)    ← librairies PyQt6
```

> Le dossier `dist/PKGVault/` contient **tout ce qu'il faut** pour lancer l'app.
> Pour distribuer, zipper ce dossier entier.

### 4. Recompiler après modification

```cmd
pyinstaller pkgvault.spec
```

PyInstaller détecte automatiquement les changements.

---

## Ajouter une icône

### 1. Préparer le fichier .ico

- Format : `.ico`
- Taille recommandée : 256×256 pixels minimum
- Outil en ligne gratuit : [icoconvert.com](https://icoconvert.com)

### 2. Placer l'icône

```
assets/
└── icons/
    └── app.ico
```

### 3. Modifier pkgvault.spec

Remplacer :
```python
icon=None,
```
par :
```python
icon="assets/icons/app.ico",
```

### 4. Recompiler

```cmd
pyinstaller pkgvault.spec
```

---

## Structure des dossiers générés

Ces dossiers sont créés automatiquement au premier lancement et sont ignorés par Git :

```
ps4-pkgvault/
├── cache/
│   ├── covers/          ← jaquettes téléchargées (PNG/JPG)
│   └── screenshots/     ← screenshots IGDB
├── data/
│   └── activity.json    ← journal d'activité
└── ps4pkgvault.db       ← base de données SQLite
```

---

## Résolution des problèmes courants

### L'exe plante au démarrage sans message

Activer la console dans `pkgvault.spec` :
```python
console=True,
```
Recompiler et relancer — l'erreur s'affichera dans la fenêtre noire.

### `ModuleNotFoundError: No module named 'urllib'`

`urllib` a été exclu par erreur. Vérifier dans `pkgvault.spec` que `urllib` n'est **pas** dans la liste `excludes`.

### Les icônes Font Awesome ne s'affichent pas (carrés □)

Vérifier que le dossier `assets/fontawesome/webfonts/` contient bien les fichiers `.woff2` et `.ttf`.

### Fenêtre blanche au lancement

Problème QWebEngine. Vérifier que `PyQt6-WebEngine` est bien installé :
```cmd
pip show PyQt6-WebEngine
```

### `ERROR: Unable to find 'assets/icons'`

Créer le dossier même s'il est vide :
```cmd
mkdir assets\icons
```

### L'API IGDB ne fonctionne pas

1. Vérifier les identifiants dans **Paramètres → APIs & Données**
2. Cliquer sur **"Tester"** — si erreur, régénérer le Client Secret sur dev.twitch.tv
3. Vérifier la connexion internet

---

*PKGVault v1.1.0 — RC Informatique — 2026*
