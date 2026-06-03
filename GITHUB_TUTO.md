# Tutoriel GitHub — PKGVault

Guide complet pour gérer et publier PKGVault sur GitHub.

---

## Table des matières

1. [Créer un compte GitHub](#1-créer-un-compte-github)
2. [Créer le dépôt](#2-créer-le-dépôt)
3. [Installer Git sur Windows](#3-installer-git-sur-windows)
4. [Configurer Git](#4-configurer-git)
5. [Connecter le projet à GitHub](#5-connecter-le-projet-à-github)
6. [Workflow quotidien](#6-workflow-quotidien)
7. [Passer le dépôt en Public](#7-passer-le-dépôt-en-public)
8. [Créer une Release avec le .exe](#8-créer-une-release-avec-le-exe)
9. [Mettre à jour une version](#9-mettre-à-jour-une-version)
10. [Commandes Git utiles](#10-commandes-git-utiles)

---

## 1. Créer un compte GitHub

1. Aller sur [github.com](https://github.com)
2. Cliquer sur **"Sign up"**
3. Renseigner email, mot de passe, nom d'utilisateur
4. Confirmer l'email

---

## 2. Créer le dépôt

1. Une fois connecté, cliquer sur **"New"** (bouton vert) ou le **+** en haut à droite
2. Remplir :
   - **Repository name** : `ps4-pkgvault`
   - **Description** : `Gestionnaire de fichiers PKG PS4`
   - **Visibility** : `Private` pour commencer (on passera en Public plus tard)
   - **Ne pas cocher** "Add a README file" (on a déjà le nôtre)
3. Cliquer sur **"Create repository"**

GitHub affiche ensuite les commandes pour connecter ton projet local.

---

## 3. Installer Git sur Windows

1. Télécharger Git sur [git-scm.com](https://git-scm.com/download/win)
2. Lancer l'installateur
3. Laisser toutes les options par défaut
4. Vérifier l'installation dans cmd :

```cmd
git --version
```

Doit afficher quelque chose comme `git version 2.x.x`

---

## 4. Configurer Git

À faire une seule fois après l'installation :

```cmd
git config --global user.name "Sébastien"
git config --global user.email "ton@email.com"
```

---

## 5. Connecter le projet à GitHub

Dans le dossier de ton projet (`F:\ps4-pkgvault`) :

```cmd
git init
git add .
git commit -m "Initial commit - PKGVault v1.0.0"
git branch -M main
git remote add origin https://github.com/rcinformatique/ps4-pkgvault.git
git push -u origin main
```

GitHub va demander tes identifiants la première fois.

> **Conseil** : utiliser un **Personal Access Token** à la place du mot de passe.
> Voir [github.com/settings/tokens](https://github.com/settings/tokens) → "Generate new token (classic)"
> Cocher `repo` → générer → copier le token → l'utiliser comme mot de passe.

---

## 6. Workflow quotidien

### Voir l'état des modifications

```cmd
git status
```

Affiche les fichiers modifiés, ajoutés, supprimés.

### Ajouter les modifications

```cmd
git add .
```

Ajoute **tous** les fichiers modifiés.

Ou fichier par fichier :
```cmd
git add templates/credits.html
git add core/api_client.py
```

### Créer un commit

```cmd
git commit -m "Description courte de ce qui a changé"
```

Exemples de bons messages :
```
git commit -m "Ajouter propagation IGDB vers DLC"
git commit -m "Corriger affichage menu en petite fenetre"
git commit -m "v1.2.0 - Nouvelle page statistiques"
```

### Envoyer sur GitHub

```cmd
git push
```

### Récupérer les modifications depuis GitHub

```cmd
git pull
```

---

## 7. Passer le dépôt en Public

Quand tu es prêt à partager le projet :

1. Aller sur `https://github.com/rcinformatique/ps4-pkgvault`
2. Cliquer sur **Settings** (onglet en haut)
3. Descendre jusqu'à **Danger Zone** (tout en bas)
4. Cliquer sur **"Change repository visibility"**
5. Sélectionner **"Make public"**
6. Taper le nom du dépôt pour confirmer
7. Cliquer sur **"I understand, change repository visibility"**

> ⚠️ Vérifier avant de passer en public que le `.gitignore` exclut bien
> `data/activity.json` (contient tes chemins locaux) et `.env` (secrets).

---

## 8. Créer une Release avec le .exe

Une **Release** permet aux utilisateurs de télécharger directement le `.exe`
sans avoir à installer Python.

### Étape 1 — Compiler le .exe

```cmd
pyinstaller pkgvault.spec
```

Le résultat est dans `dist/PKGVault/`.

### Étape 2 — Créer le zip

```cmd
cd dist
powershell Compress-Archive -Path PKGVault -DestinationPath PKGVault-v1.1.0-windows.zip
```

### Étape 3 — Créer un tag Git

```cmd
git tag v1.1.0
git push origin v1.1.0
```

### Étape 4 — Créer la Release sur GitHub

1. Aller sur ton dépôt GitHub
2. Cliquer sur **"Releases"** dans la colonne de droite
3. Cliquer sur **"Create a new release"**
4. Remplir :
   - **Choose a tag** : sélectionner `v1.1.0`
   - **Release title** : `PKGVault v1.1.0`
   - **Description** : coller le contenu du `CHANGELOG.md`
5. Dans la zone **"Attach binaries"** → glisser-déposer `PKGVault-v1.1.0-windows.zip`
6. Cliquer sur **"Publish release"**

### Ce que voient les utilisateurs

Sur la page du dépôt, ils verront :

```
Releases
  PKGVault v1.1.0          [Latest]
  Assets:
    📦 PKGVault-v1.1.0-windows.zip    (XX MB)
    Source code (zip)
    Source code (tar.gz)
```

Ils téléchargent le zip, l'extraient, et lancent `PKGVault.exe`. C'est tout.

---

## 9. Mettre à jour une version

Pour chaque nouvelle version :

### 1. Modifier les fichiers

- `credits.html` → numéro de version
- `CHANGELOG.md` → ajouter la nouvelle section
- `README.md` → mettre à jour si nécessaire

### 2. Commit et push

```cmd
git add .
git commit -m "v1.2.0 - Description des changements"
git push
```

### 3. Recompiler

```cmd
pyinstaller pkgvault.spec
cd dist
powershell Compress-Archive -Path PKGVault -DestinationPath PKGVault-v1.2.0-windows.zip
```

### 4. Nouveau tag et Release

```cmd
git tag v1.2.0
git push origin v1.2.0
```

Puis créer la Release sur GitHub comme à l'étape 8.

---

## 10. Commandes Git utiles

### Voir l'historique des commits

```cmd
git log --oneline
```

Affiche la liste des commits avec leur message.

### Annuler les modifications non commitées

```cmd
git checkout -- .
```

⚠️ Irréversible — annule toutes les modifications depuis le dernier commit.

### Voir les différences

```cmd
git diff
```

Affiche ce qui a changé depuis le dernier commit.

### Voir les branches

```cmd
git branch
```

### Créer une branche

Utile pour développer une fonctionnalité sans toucher au code principal :

```cmd
git checkout -b ma-nouvelle-fonctionnalite
```

Puis pour fusionner dans main :

```cmd
git checkout main
git merge ma-nouvelle-fonctionnalite
```

### Supprimer une branche

```cmd
git branch -d ma-nouvelle-fonctionnalite
```

---

## Résumé — commandes du quotidien

```cmd
git status                          ← voir ce qui a changé
git add .                           ← préparer tous les changements
git commit -m "message"             ← sauvegarder
git push                            ← envoyer sur GitHub
git pull                            ← récupérer depuis GitHub
git log --oneline                   ← voir l'historique
```

---

*PKGVault — RC Informatique — 2026*
