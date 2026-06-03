# PS4 PKGVault — Guide développeur complet

Guide pas à pas pour un développeur qui clone le projet depuis GitHub
et le fait fonctionner sur sa machine.

---

## Prérequis

Avant de commencer, installer :

| Outil | Version | Lien |
|---|---|---|
| Windows | 10 / 11 64-bit | — |
| Python | 3.13+ | [python.org](https://www.python.org/downloads/) |
| Git | 2.x | [git-scm.com](https://git-scm.com/download/win) |

> ⚠️ Lors de l'installation de Python, **cocher "Add Python to PATH"**.

Vérifier les installations :

```cmd
python --version
git --version
```

---

## Étape 1 — Cloner le dépôt

```cmd
git clone https://github.com/rcinformatique/ps4-pkgvault.git
cd ps4-pkgvault
```

Vérifier la structure du projet :

```cmd
dir
```

Vous devez voir :
```
assets/
core/
data/
templates/
tools/
ui/
main.py
requirements.txt
pkgvault.spec
README.md
CHANGELOG.md
INSTALL.md
GUIDE.md
```

---

## Étape 2 — Créer l'environnement virtuel

```cmd
python -m venv venv
```

Activer l'environnement :

**cmd.exe :**
```cmd
venv\Scripts\activate.bat
```

**PowerShell :**
```powershell
.\venv\Scripts\Activate.ps1
```

Le prompt doit afficher `(venv)` :
```
(venv) C:\...\ps4-pkgvault>
```

---

## Étape 3 — Installer les dépendances

```cmd
pip install -r requirements.txt
```

Vérifier que tout est installé :

```cmd
pip list
```

Vous devez voir entre autres :
```
Jinja2          3.1.6
Pillow          12.2.0
PyQt6           6.11.0
PyQt6-WebEngine 6.11.0
requests        2.34.2
pyinstaller     6.20.0
```

---

## Étape 4 — Installer Font Awesome

### Télécharger

Aller sur [fontawesome.com/download](https://fontawesome.com/download)
→ télécharger **"Free For Web"**

### Placer les fichiers

Créer la structure suivante dans le projet :

```
assets/
└── fontawesome/
    ├── css/
    │   └── all.min.css
    └── webfonts/
        ├── fa-brands-400.ttf
        ├── fa-brands-400.woff2
        ├── fa-regular-400.ttf
        ├── fa-regular-400.woff2
        ├── fa-solid-900.ttf
        └── fa-solid-900.woff2
```

### Vérifier

```cmd
dir assets\fontawesome\css
dir assets\fontawesome\webfonts
```

`all.min.css` doit être présent ainsi que les fichiers `.woff2`.

---

## Étape 5 — Créer les dossiers manquants

Ces dossiers sont ignorés par Git mais nécessaires au lancement :

```cmd
mkdir assets\icons
mkdir cache\covers
mkdir cache\screenshots
mkdir data
```

---

## Étape 6 — Premier lancement

```cmd
python main.py
```

### ✅ Attendu

- La fenêtre PS4 PKGVault s'ouvre
- Interface Windows 11 avec topbar, onglets, barre de statut
- Bibliothèque vide avec message "Ajouter un dossier"
- Les icônes Font Awesome s'affichent correctement

### ❌ Problèmes possibles

**Icônes carrés □**
→ Font Awesome mal installé — vérifier `assets/fontawesome/webfonts/`

**Fenêtre blanche**
→ QWebEngine non installé — relancer `pip install PyQt6-WebEngine`

**ImportError**
→ Dépendance manquante — relancer `pip install -r requirements.txt`

**ModuleNotFoundError: jinja2**
→ Environnement virtuel non activé — relancer `venv\Scripts\activate.bat`

---

## Étape 7 — Tests fonctionnels

### 7.1 Test de l'interface

| Test | Action | Résultat attendu |
|---|---|---|
| Thème sombre | Cliquer 🌙 | Interface passe en sombre |
| Thème clair | Cliquer ☀️ | Interface revient en clair |
| Navigation | Cliquer chaque onglet | Pages s'affichent correctement |
| Recherche | Taper dans la barre | Filtre en temps réel |
| Menu hamburger | Réduire la fenêtre < 780px | Bouton ☰ apparaît |
| Menu hamburger | Cliquer ☰ | Menu déroulant s'ouvre |
| Menu hamburger | Cliquer en dehors | Menu se ferme |

### 7.2 Test du scan

1. Cliquer sur **➕ Ajouter un dossier**
2. Sélectionner un dossier contenant des fichiers `.pkg`
3. Attendre la fin du scan

| Vérification | Résultat attendu |
|---|---|
| PKG apparaissent dans la grille | ✅ |
| Types détectés (BASE/DLC/UPDATE/BACKPORT) | ✅ |
| Tailles affichées | ✅ |
| Régions détectées | ✅ |
| Jaquettes extraites (icon0.png) | ✅ |
| Journal d'activité rempli | ✅ |

### 7.3 Test de la fiche détail

1. Cliquer sur un jeu dans la bibliothèque

| Vérification | Résultat attendu |
|---|---|
| Page de détail s'ouvre | ✅ |
| Bouton "Retour" fonctionne | ✅ |
| Jaquette affichée | ✅ |
| Informations techniques visibles | ✅ |
| Bouton "Ouvrir le dossier" → Explorateur Windows | ✅ |
| Bouton "Copier le chemin" → presse-papier | ✅ |
| Bouton "Copier le CUSA" → presse-papier | ✅ |

### 7.4 Test du menu contextuel

1. Clic droit sur une carte

| Vérification | Résultat attendu |
|---|---|
| Menu contextuel apparaît | ✅ |
| "Ouvrir le dossier" ouvre l'Explorateur | ✅ |
| "Copier le chemin" copie dans presse-papier | ✅ |
| "Copier le Content-ID" copie dans presse-papier | ✅ |
| Clic ailleurs ferme le menu | ✅ |

### 7.5 Test des filtres

| Test | Action | Résultat attendu |
|---|---|---|
| Filtre BASE | Cliquer "BASE" | Seuls les jeux BASE affichés |
| Filtre DLC | Cliquer "DLC" | Seuls les DLC affichés |
| Filtre UPDATE | Cliquer "UPDATE" | Seules les updates affichées |
| Filtre BACKPORT | Cliquer "BACKPORT" | Seuls les backports affichés |
| Filtre Tous | Cliquer "Tous" | Tout s'affiche |
| Tri Nom | Cliquer "Nom" | Tri alphabétique |
| Tri Taille | Cliquer "Taille" | Tri par taille |

### 7.6 Test vue liste

1. Cliquer sur le bouton ☰ en subbar

| Vérification | Résultat attendu |
|---|---|
| Basculement grille → liste | ✅ |
| Colonnes Type, Titre, Firmware, Taille, Région | ✅ |
| Clic sur un item → fiche détail | ✅ |
| Clic droit → menu contextuel | ✅ |

### 7.7 Test IGDB (nécessite les identifiants)

1. Aller dans **Paramètres → APIs & Données**
2. Saisir Client ID et Client Secret Twitch
3. Cliquer **"Tester"**

| Vérification | Résultat attendu |
|---|---|
| Message "Connexion IGDB réussie" | ✅ |
| Activer "Téléchargement automatique" | ✅ |
| Sauvegarder | ✅ |
| Rescanner un dossier | Données IGDB récupérées automatiquement |
| Jaquettes HD téléchargées | ✅ |
| Description affichée dans la fiche | ✅ |
| DLC héritent des données du jeu BASE | ✅ |

### 7.8 Test export

1. Cliquer sur **📤 Exporter**

| Test | Action | Résultat attendu |
|---|---|---|
| Export JSON | Cliquer "Exporter en JSON" | Fichier .json créé et lisible |
| Export CSV | Cliquer "Exporter en CSV" | Fichier .csv ouvrable dans Excel |
| Contenu JSON | Ouvrir le fichier | Tous les jeux avec métadonnées |
| Contenu CSV | Ouvrir dans Excel | Colonnes bien séparées |

### 7.9 Test journal d'activité

1. Aller dans **📋 Activité**

| Vérification | Résultat attendu |
|---|---|
| Événements de scan listés | ✅ |
| Filtre "Scans" fonctionne | ✅ |
| Filtre "API" fonctionne | ✅ |
| Filtre "Erreurs" fonctionne | ✅ |
| Bouton "Vider" efface le journal | ✅ |

### 7.10 Test gestion dossiers

1. Aller dans **📁 Dossiers**

| Vérification | Résultat attendu |
|---|---|
| Dossiers ajoutés listés avec stats | ✅ |
| Bouton "Rescanner" relance le scan | ✅ |
| Bouton "Retirer" supprime le dossier de la liste | ✅ |
| Les fichiers PKG ne sont pas supprimés du disque | ✅ |

---

## Étape 8 — Test de compilation .exe

```cmd
pyinstaller pkgvault.spec
```

### Vérifier le résultat

```cmd
dir dist\PS4PKGVault
```

Doit contenir :
```
PS4PKGVault.exe
templates/
assets/
Qt6WebEngine*.dll
...
```

### Lancer l'exe

```cmd
dist\PS4PKGVault\PS4PKGVault.exe
```

Refaire les tests 7.1 à 7.9 sur l'exe pour s'assurer que tout fonctionne
de la même façon qu'en mode développement.

---

## Étape 9 — Créer le zip de distribution

```cmd
cd dist
powershell Compress-Archive -Path PS4PKGVault -DestinationPath PS4PKGVault-v1.1.0-windows.zip
cd ..
```

Vérifier la taille du zip :
```cmd
dir dist\*.zip
```

---

## Checklist finale avant publication

- [ ] `python main.py` fonctionne sans erreur
- [ ] Scan de dossiers PKG fonctionne
- [ ] Icônes Font Awesome s'affichent
- [ ] Thème clair/sombre fonctionne
- [ ] Menu hamburger fonctionne en petite fenêtre
- [ ] IGDB récupère les données correctement
- [ ] DLC héritent des données du jeu BASE
- [ ] Export JSON et CSV fonctionnent
- [ ] `pyinstaller pkgvault.spec` compile sans erreur
- [ ] L'exe fonctionne sur une machine sans Python installé
- [ ] `data/activity.json` est dans le `.gitignore`
- [ ] Pas de secrets (Client ID/Secret) dans le code
- [ ] `CHANGELOG.md` mis à jour
- [ ] `README.md` mis à jour
- [ ] Version correcte dans `credits.html`

---

## Structure finale attendue du projet

```
ps4-pkgvault/
├── assets/
│   ├── fontawesome/        ← Font Awesome 6 Free (non versionné)
│   │   ├── css/
│   │   └── webfonts/
│   └── icons/              ← Icône .ico (optionnel)
├── cache/                  ← Généré au lancement (ignoré Git)
│   ├── covers/
│   └── screenshots/
├── core/
│   ├── activity_log.py
│   ├── api_client.py
│   ├── cover_loader.py
│   ├── database.py
│   ├── pkg_reader.py
│   ├── scanner.py
│   └── sfo_parser.py
├── data/                   ← Généré au lancement (ignoré Git)
│   └── activity.json
├── templates/
│   ├── activity.html
│   ├── base.html
│   ├── credits.html
│   ├── detail.html
│   ├── folders.html
│   ├── library.html
│   └── settings.html
├── tools/
│   ├── api_pkg.py
│   ├── extract_covers.py
│   ├── inspect_pkg.py
│   └── read_pkg.py
├── ui/
│   ├── main_window.py
│   ├── template_engine.py
│   ├── theme.py
│   ├── topbar.py
│   ├── subbar.py
│   ├── pages/
│   └── widgets/
├── .gitignore
├── CHANGELOG.md
├── DEV_SETUP.md
├── GUIDE.md
├── INSTALL.md
├── README.md
├── main.py
├── pkgvault.spec
└── requirements.txt
```

---

*PS4 PKGVault v1.1.0 — RC Informatique — 2026*
