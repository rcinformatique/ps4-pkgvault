#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PS4 PKGVault - API PKG

Ce script :
- lit les infos locales d'un PKG via tools/read_pkg.py
- interroge RAWG avec le titre du jeu
- récupère les infos API :
    - titre
    - date de sortie
    - genres
    - plateformes
    - développeurs
    - éditeurs
    - description
    - jaquette
    - screenshots
- sauvegarde :
    - la jaquette dans assets/covers/CUSAxxxxx.jpg
    - les screenshots dans assets/screenshots/CUSAxxxxx/
    - le JSON final dans assets/json/CUSAxxxxx.pkgvault.json
"""

import sys
import json
import re
import requests
from pathlib import Path

# Permet d'importer tools/read_pkg.py depuis ce script
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.read_pkg import get_pkg_info


RAWG_API_URL = "https://api.rawg.io/api/games"


# =====================================================================
# CHEMINS PROJET
# =====================================================================

def get_project_root():
    """
    Retourne la racine du projet.

    api_pkg.py est dans :
        tools/api_pkg.py

    donc :
        parent = tools/
        parent.parent = racine du projet
    """
    return Path(__file__).resolve().parent.parent


def get_assets_dir():
    """
    Retourne le dossier assets du projet.
    """
    return get_project_root() / "assets"


def ensure_dir(path):
    """
    Crée un dossier s'il n'existe pas.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# =====================================================================
# NETTOYAGE TITRE
# =====================================================================

def clean_search_title(title):
    """
    Nettoie le titre pour améliorer la recherche RAWG.

    Exemple :
        LEGO® Party! -> LEGO Party!
    """
    title = title or ""

    title = re.sub(r"™|®|©", "", title)
    title = re.sub(r"\bPS4\b", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bv\d+\.\d+\b", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title)

    return title.strip()


# =====================================================================
# RAWG API
# =====================================================================

def fetch_rawg_game(title, api_key):
    """
    Recherche un jeu sur RAWG.

    Étapes :
    1. Recherche par titre
    2. Récupération du premier résultat
    3. Récupération des détails
    4. Récupération des screenshots
    """
    search_title = clean_search_title(title)

    params = {
        "key": api_key,
        "search": search_title,
        "page_size": 1,
    }

    response = requests.get(RAWG_API_URL, params=params, timeout=20)
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    game = results[0]
    game_id = game.get("id")

    details = {}
    screenshots = []

    if game_id:
        detail_response = requests.get(
            f"{RAWG_API_URL}/{game_id}",
            params={"key": api_key},
            timeout=20
        )
        detail_response.raise_for_status()
        details = detail_response.json()

        screen_response = requests.get(
            f"{RAWG_API_URL}/{game_id}/screenshots",
            params={"key": api_key},
            timeout=20
        )
        screen_response.raise_for_status()
        screenshots = screen_response.json().get("results", [])

    return {
        "api": "RAWG",
        "search_title": search_title,
        "title_api": game.get("name", ""),
        "rawg_id": game.get("id"),
        "slug": game.get("slug", ""),
        "release_date": game.get("released", ""),
        "rating": game.get("rating", ""),
        "cover_url": game.get("background_image", ""),
        "genres": [g.get("name") for g in game.get("genres", [])],
        "platforms": [
            p.get("platform", {}).get("name")
            for p in game.get("platforms", [])
        ],
        "developers": [
            d.get("name") for d in details.get("developers", [])
        ],
        "publishers": [
            p.get("name") for p in details.get("publishers", [])
        ],
        "website": details.get("website", ""),
        "description": details.get("description_raw", ""),
        "screenshots": [
            s.get("image") for s in screenshots if s.get("image")
        ],
    }


# =====================================================================
# TÉLÉCHARGEMENT FICHIERS
# =====================================================================

def get_extension_from_url(url, default=".jpg"):
    """
    Détecte l'extension depuis une URL.
    """
    url = (url or "").lower()

    if ".png" in url:
        return ".png"

    if ".webp" in url:
        return ".webp"

    if ".jpeg" in url:
        return ".jpg"

    if ".jpg" in url:
        return ".jpg"

    return default


def download_file(url, output_path):
    """
    Télécharge un fichier distant.

    Retourne True si OK, False sinon.
    """
    if not url:
        return False

    headers = {
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        output_path.write_bytes(response.content)

        return True

    except requests.RequestException:
        return False


def save_cover(api, title_id):
    """
    Sauvegarde la jaquette RAWG uniquement si aucune jaquette PKG n'existe déjà.

    Priorité :
    1. assets/covers/CUSAxxxxx.png  -> jaquette extraite du PKG / icon0.png
    2. assets/covers/CUSAxxxxx.jpg  -> jaquette API RAWG
    """

    cover_dir = ensure_dir(get_assets_dir() / "covers")

    # Jaquette locale extraite depuis read_pkg.py
    local_pkg_cover_png = cover_dir / f"{title_id}.png"

    if local_pkg_cover_png.exists():
        return {
            "source": "PKG",
            "url": "",
            "path": str(local_pkg_cover_png),
            "filename": local_pkg_cover_png.name,
            "downloaded": False,
        }

    if not api:
        return None

    cover_url = api.get("cover_url", "")

    if not cover_url:
        return None

    ext = get_extension_from_url(cover_url, ".jpg")
    out_file = cover_dir / f"{title_id}{ext}"

    # Si la jaquette API existe déjà, on ne retélécharge pas
    if out_file.exists():
        return {
            "source": "RAWG",
            "url": cover_url,
            "path": str(out_file),
            "filename": out_file.name,
            "downloaded": False,
        }

    if download_file(cover_url, out_file):
        return {
            "source": "RAWG",
            "url": cover_url,
            "path": str(out_file),
            "filename": out_file.name,
            "downloaded": True,
        }

    return None


def save_screenshots(api, title_id, limit=10):
    """
    Sauvegarde les screenshots RAWG dans :
        assets/screenshots/CUSAxxxxx/

    Exemple :
        assets/screenshots/CUSA53974/01.jpg
        assets/screenshots/CUSA53974/02.jpg
    """
    if not api:
        return []

    screenshots = api.get("screenshots", [])

    if not screenshots:
        return []

    out_dir = ensure_dir(get_assets_dir() / "screenshots" / title_id)

    saved = []

    for index, url in enumerate(screenshots[:limit], start=1):
        ext = get_extension_from_url(url, ".jpg")
        out_file = out_dir / f"{index:02d}{ext}"

        if download_file(url, out_file):
            saved.append({
                "index": index,
                "url": url,
                "path": str(out_file),
                "filename": out_file.name,
            })

    return saved


def save_json(pkg, api, cover, screenshots):
    """
    Sauvegarde le JSON final dans :
        assets/json/CUSAxxxxx.pkgvault.json
    """
    title_id = pkg.get("title_id") or "UNKNOWN"

    json_dir = ensure_dir(get_assets_dir() / "json")
    out_file = json_dir / f"{title_id}.pkgvault.json"

    merged = {
        "pkg": pkg,
        "api": api,
        "assets": {
            "cover": cover,
            "screenshots": screenshots,
        }
    }

    out_file.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return out_file


# =====================================================================
# AFFICHAGE CONSOLE
# =====================================================================

def print_row(label, value):
    """
    Affiche une ligne proprement.

    Gère aussi les listes.
    """
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value if v)

    print(f"{label:<24}: {value if value not in [None, '', []] else '—'}")


# =====================================================================
# MAIN
# =====================================================================

def main():
    if len(sys.argv) < 3:
        print('Usage : python tools/api_pkg.py "fichier.pkg" "RAWG_API_KEY"')
        sys.exit(1)

    pkg_path = sys.argv[1]
    api_key = sys.argv[2]

    # 1. Lecture locale du PKG
    pkg = get_pkg_info(pkg_path)

    print("=" * 70)
    print("PKG + API")
    print("=" * 70)

    print_row("Titre PKG", pkg["title"])
    print_row("Title ID", pkg["title_id"])
    print_row("Content ID", pkg["content_id"])
    print_row("Version", pkg["app_ver"])
    print_row("Firmware", pkg["firmware"])
    print_row("Région", pkg["store_region"])
    print_row("Catégorie", pkg["category_label"])

    # 2. Appel API RAWG
    api = fetch_rawg_game(pkg["title_api"], api_key)

    print("\n" + "-" * 70)
    print("RAWG API")
    print("-" * 70)

    if not api:
        print("Aucun résultat trouvé.")
        return

    print_row("Recherche", api["search_title"])
    print_row("Titre API", api["title_api"])
    print_row("RAWG ID", api["rawg_id"])
    print_row("Slug", api["slug"])
    print_row("Date sortie", api["release_date"])
    print_row("Note", api["rating"])
    print_row("Genres", api["genres"])
    print_row("Plateformes", api["platforms"])
    print_row("Développeurs", api["developers"])
    print_row("Éditeurs", api["publishers"])
    print_row("Site web", api["website"])
    print_row("Jaquette URL", api["cover_url"])
    print_row("Screenshots URL", len(api["screenshots"]))

    if api["screenshots"]:
        print("\nScreenshots RAWG :")
        for url in api["screenshots"][:5]:
            print(" -", url)

    if api["description"]:
        print("\nDescription :")
        print(api["description"][:800])

    # 3. Sauvegarde assets
    cover = save_cover(api, pkg["title_id"])
    screenshots = save_screenshots(api, pkg["title_id"])

    print("\n" + "-" * 70)
    print("ASSETS SAUVEGARDÉS")
    print("-" * 70)

    if cover:
        print_row("Jaquette source", cover["source"])
        print_row("Jaquette fichier", cover["path"])
        print_row("Téléchargée", "Oui" if cover["downloaded"] else "Non")
    else:
        print_row("Jaquette", "Non sauvegardée")

    print_row("Screenshots", len(screenshots))

    if screenshots:
        for item in screenshots:
            print(f"- {item['filename']} | {item['path']}")

    # 4. Sauvegarde JSON
    out = save_json(pkg, api, cover, screenshots)

    print("\n" + "-" * 70)
    print("JSON sauvegardé")
    print("-" * 70)
    print(out)


if __name__ == "__main__":
    main()