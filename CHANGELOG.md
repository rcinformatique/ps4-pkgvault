# Changelog

Toutes les modifications notables de PKGVault sont documentées ici.

---

## [1.1.0] — 2026-06-03

### Ajouté

- **Font Awesome 6 Free** intégré en local — tous les emojis de l'interface remplacés par des icônes vectorielles
- **Menu hamburger responsive** — en petite fenêtre, la navigation se replie dans un menu déroulant ☰
- **Thème clair / sombre** — bascule via le bouton 🌙 en topbar, préférence sauvegardée en base
- **Propagation IGDB → DLC** — après récupération des données d'un jeu BASE, description, genres, jaquette et développeur sont automatiquement hérités par les DLC liés via le CUSA commun
- **Journal d'activité** (`activity.html`) — historique des scans, appels API et erreurs avec filtres par type
- **Export bibliothèque** — export en JSON ou CSV depuis le bouton Exporter en topbar
- **Contenu associé** déplacé sous les Screenshots dans la page de détail
- **Bloc Informations redesigné** — labels à gauche avec icônes FA, valeurs à droite
- `data/activity.json` ajouté au `.gitignore`

### Modifié

- **API IGDB** — traite uniquement les jeux de type `game` (plus `backport`) ; les `update` sont ignorés
- **Bouton "Rafraîchir IGDB"** — visible uniquement pour les types `game` et `dlc`, caché pour `update` et `backport`
- **Topbar responsive** — labels des onglets masqués sous 1100px, texte des boutons masqué sous 920px, boutons secondaires masqués sous 780px
- **Page Crédits** — lien GitHub corrigé (`rcinformatique/ps4-pkgvault`), RAWG remplacé par IGDB, technologies mises à jour (Pillow 12.x, ajout Twitch OAuth, Requests, PS Store API, Font Awesome, PyInstaller, QWebEngine)
- **Page Paramètres** — section Affichage supprimée, icônes FA ajoutées
- **Page Dossiers** — icônes FA sur les pills de stats et boutons d'action
- **README.md** — mis à jour avec la nouvelle structure, Font Awesome, IGDB uniquement

### Corrigé

- Placeholder de jaquette manquant en mode liste (vue list-thumb)
- Icônes de type dans le contenu associé (sidebar → colonne principale)
- `overflow: hidden` sur `.nav-tabs` qui masquait les onglets en petite fenêtre

---

## [1.0.0] — 2026-05-31

### Initial

- Scan récursif de dossiers PKG
- Lecture directe des métadonnées `param.sfo` depuis le binaire PKG
- Détection automatique BASE / DLC / UPDATE / BACKPORT
- Extraction automatique de `icon0.png`
- Récupération IGDB via Twitch OAuth
- Base de données SQLite locale
- Vue grille et vue liste
- Page de détail avec screenshots, genres, langues
- Relations automatiques BASE ↔ DLC ↔ UPDATE via CUSA
- Menu contextuel (ouvrir, copier, renommer, supprimer)
- Smart scan au démarrage (nouveaux fichiers uniquement)
- Export JSON / CSV
