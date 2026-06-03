# PKGVault — Guide utilisateur

---

## Table des matières

1. [Premier lancement](#premier-lancement)
2. [Ajouter des dossiers](#ajouter-des-dossiers)
3. [La bibliothèque](#la-bibliothèque)
4. [Fiche détail d'un jeu](#fiche-détail-dun-jeu)
5. [Récupérer les informations des jeux](#récupérer-les-informations-des-jeux)
6. [Gérer les dossiers](#gérer-les-dossiers)
7. [Recherche et filtres](#recherche-et-filtres)
8. [Menu contextuel](#menu-contextuel)
9. [Thème clair / sombre](#thème-clair--sombre)
10. [Exporter la bibliothèque](#exporter-la-bibliothèque)
11. [Journal d'activité](#journal-dactivité)
12. [Paramètres](#paramètres)

---

## Premier lancement

Au premier lancement, la bibliothèque est vide.

![Bibliothèque vide]

PKGVault ne déplace ni ne modifie vos fichiers PKG — il les **indexe uniquement**.
Vos fichiers restent exactement là où ils sont.

---

## Ajouter des dossiers

### Ajouter un dossier

1. Cliquer sur **➕ Ajouter un dossier** en haut à droite
2. Sélectionner le dossier contenant vos fichiers PKG
3. PKGVault scanne automatiquement **tous les sous-dossiers**

> Le scan peut prendre quelques secondes selon le nombre de fichiers.
> La barre de statut en bas indique la progression.

### Plusieurs dossiers

Vous pouvez ajouter autant de dossiers que vous voulez.
PKGVault les scanne tous et les regroupe dans une seule bibliothèque.

### Scan automatique au démarrage

À chaque lancement, PKGVault vérifie intelligemment vos dossiers :
- **Nouveaux fichiers** → ajoutés automatiquement
- **Fichiers supprimés** → retirés de la bibliothèque
- **Fichiers déjà connus** → ignorés (pas de re-scan inutile)

---

## La bibliothèque

### Vue grille

Les jeux s'affichent sous forme de cartes avec leur jaquette.
Chaque carte montre :
- La **jaquette** du jeu
- Le **type** (BASE, DLC, UPDATE, BACKPORT)
- Le **titre**
- Le **Content-ID**
- La **taille** du fichier
- La **région** (Europe, USA, Japon…)

### Vue liste

Cliquer sur le bouton ☰ en haut à droite pour basculer en vue liste.
La liste affiche les mêmes informations en format compact avec le firmware.

### Filtres par type

La barre de filtres permet d'afficher uniquement :
- **Tous** — tous les fichiers PKG
- **BASE** — jeux complets
- **DLC** — contenus téléchargeables
- **UPDATE** — mises à jour
- **BACKPORT** — versions adaptées pour firmware inférieur

### Tri

Trier par **Nom**, **Taille** ou **Type** via les boutons en haut à droite.

### Couleurs par type

| Couleur | Type |
|---|---|
| 🔵 Bleu | BASE |
| 🟢 Vert | DLC |
| 🔷 Bleu clair | UPDATE |
| 🟠 Orange | BACKPORT |

---

## Fiche détail d'un jeu

Cliquer sur une carte pour ouvrir la fiche complète.

### Informations affichées

- **Jaquette HD** — cliquer pour agrandir
- **Type, région, firmware, version**
- **Note IGDB** avec étoiles
- **Date de sortie**
- **Développeur et éditeur**
- **Description complète**
- **Genres**
- **Screenshots** — cliquer pour agrandir, naviguer avec les flèches ou ← →
- **Contenu associé** — DLC et updates liés au même jeu
- **Langues supportées**
- **Informations techniques** — Content-ID, taille, catégorie SFO, nom du fichier

### Boutons d'action

| Bouton | Action |
|---|---|
| **Ouvrir le dossier** | Ouvre l'Explorateur Windows au bon endroit |
| **Copier le chemin** | Copie le chemin complet dans le presse-papier |
| **Copier le CUSA** | Copie le Content-ID (ex: CUSA13367) |
| **Rafraîchir IGDB** | Force une nouvelle recherche IGDB pour ce jeu |

> Le bouton **Rafraîchir IGDB** est disponible uniquement pour les jeux BASE et DLC.

### Lightbox screenshots

- **Clic** sur un screenshot → agrandissement
- **Flèches ← →** ou boutons de navigation → image précédente / suivante
- **Échap** → fermer

---

## Récupérer les informations des jeux

PKGVault peut récupérer automatiquement depuis **IGDB** :
- Titre officiel
- Description
- Genres
- Date de sortie
- Développeur et éditeur
- Note
- Jaquette HD
- Screenshots

### Configuration requise

Les identifiants IGDB doivent être renseignés dans les **Paramètres**.
Voir la section [Paramètres](#paramètres).

### Récupération automatique

Si l'option **"Téléchargement automatique"** est activée dans les Paramètres,
les données IGDB sont récupérées automatiquement après chaque scan.

### Récupération manuelle

Cliquer sur **🔄 Données API** en haut de la fenêtre pour lancer la récupération
sur tous les jeux qui n'ont pas encore été traités.

### Propagation aux DLC

Quand un jeu BASE est traité, PKGVault propage automatiquement
la description, les genres et la jaquette à tous ses DLC liés.
Les DLC héritent des informations du jeu principal.

---

## Gérer les dossiers

Aller dans l'onglet **📁 Dossiers** pour gérer vos dossiers.

### Informations affichées

Pour chaque dossier :
- Chemin complet
- Nombre de fichiers (BASE, DLC, UPDATE, BACKPORT)
- Taille totale
- Date d'ajout

### Rescanner un dossier

Cliquer sur **🔄 Rescanner** pour forcer un nouveau scan complet du dossier.
Utile si vous avez ajouté ou supprimé des fichiers PKG manuellement.

### Retirer un dossier

Cliquer sur **🗑️ Retirer** pour supprimer le dossier de la bibliothèque.

> ⚠️ Retirer un dossier supprime uniquement l'indexation.
> Vos fichiers PKG ne sont **pas** supprimés du disque.

---

## Recherche et filtres

### Barre de recherche

La barre de recherche en haut à droite permet de chercher par :
- **Titre** du jeu
- **Content-ID** (ex: EP4295-CUSA13367)
- **Title ID** (ex: CUSA13367)
- **Nom du fichier**

La recherche est instantanée — les résultats se mettent à jour en temps réel.

### Combiner recherche et filtre

Vous pouvez combiner la recherche avec un filtre de type.
Exemple : filtre **DLC** + recherche **"Uncharted"** → tous les DLC Uncharted.

---

## Menu contextuel

Faire un **clic droit** sur une carte ou un élément de liste pour accéder au menu contextuel.

| Option | Description |
|---|---|
| **Ouvrir le dossier** | Ouvre le dossier contenant le fichier dans l'Explorateur |
| **Copier le chemin** | Copie le chemin complet du fichier |
| **Copier le Content-ID** | Copie le Content-ID complet |
| **Renommer** | Renomme le fichier PKG sur le disque |
| **Supprimer** | Supprime définitivement le fichier PKG du disque |

> ⚠️ La suppression est **irréversible** — le fichier est supprimé du disque dur.

---

## Thème clair / sombre

Cliquer sur le bouton 🌙 en haut à droite pour basculer entre le thème clair et sombre.
La préférence est sauvegardée automatiquement.

---

## Exporter la bibliothèque

Cliquer sur **📤 Exporter** en haut de la fenêtre.

### Format JSON

Export complet avec toutes les métadonnées :
titre, Content-ID, type, firmware, région, taille, développeur, éditeur, genres, note, date de sortie.

Utile pour importer dans un autre outil ou faire des statistiques.

### Format CSV

Export tableur compatible Excel, LibreOffice Calc, Google Sheets.
Mêmes informations que le JSON, une ligne par fichier PKG.

---

## Journal d'activité

L'onglet **📋 Activité** affiche l'historique de toutes les opérations :

| Type | Description |
|---|---|
| **Scan** | Fichier PKG détecté et indexé |
| **API** | Données IGDB récupérées pour un jeu |
| **Erreur** | Fichier ignoré ou problème de lecture |

### Filtres

Les chips en haut permettent de filtrer par type d'événement.

### Vider le journal

Cliquer sur **🗑️ Vider** pour effacer tout l'historique.

---

## Paramètres

Aller dans l'onglet **⚙️ Paramètres**.

### APIs & Données

| Champ | Description |
|---|---|
| **Twitch Client ID** | Identifiant de votre application Twitch |
| **Twitch Client Secret** | Secret de votre application Twitch |
| **Téléchargement automatique** | Lance IGDB automatiquement après chaque scan |

Cliquer sur **"Tester"** pour vérifier que vos identifiants IGDB sont corrects.

### Base de données & Cache

| Action | Description |
|---|---|
| **Vider le cache** | Supprime toutes les jaquettes téléchargées (elles seront re-téléchargées) |
| **Réinitialiser la BDD** | Supprime tous les jeux indexés — vos fichiers PKG ne sont pas affectés |

> ⚠️ La réinitialisation de la base de données supprime toutes les métadonnées.
> Un nouveau scan complet sera nécessaire.

### Sauvegarder

Toujours cliquer sur **💾 Sauvegarder les paramètres** après modification.

---

## Conseils

- **Organisation des dossiers** — PKGVault scanne récursivement, vous pouvez organiser vos PKG dans des sous-dossiers par jeu (Game/, DLC/, Update/) sans problème.
- **Jaquettes manquantes** — Si un jeu n'a pas de jaquette après le scan, lancer **🔄 Données API** pour récupérer les images depuis IGDB.
- **Performances** — Sur une grande collection (500+ fichiers), la première indexation peut prendre quelques minutes. Les lancements suivants sont quasi-instantanés grâce au smart scan.

---

*PKGVault v1.1.0 — RC Informatique — 2026*
