#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PS4 PKGVault - Extracteur de jaquettes PKG (tous types)
Usage : python tools/extract_covers.py "F:\PS4 JailBreak\Games"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pkg_reader import read_pkg
from core.cover_loader import extract_icon0, save_cover, get_cached_cover

TYPE_LABELS = {
    "game":     "BASE",
    "backport": "BACKPORT",
    "update":   "UPDATE",
    "dlc":      "DLC",
}


def extract_all_covers(folder: str):
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"❌ Dossier introuvable : {folder}")
        return

    pkg_files = sorted(folder_path.rglob("*.pkg"))
    print(f"📦 {len(pkg_files)} fichiers PKG trouvés\n")

    ok      = 0
    skipped = 0
    failed  = 0

    for pkg_file in pkg_files:
        pkg = read_pkg(pkg_file)
        if not pkg:
            print(f"❌ PKG illisible : {pkg_file.name}\n")
            failed += 1
            continue

        pkg_type   = pkg.get("type", "")
        content_id = pkg.get("content_id", "")
        title      = pkg.get("title", "Inconnu")
        label      = TYPE_LABELS.get(pkg_type, pkg_type.upper())

        if not content_id or content_id == "UNKNOWN":
            print(f"❌ Content-ID manquant : {pkg_file.name}\n")
            failed += 1
            continue

        print(f"→ [{label}] {title}")
        print(f"   {pkg_file.name}")

        # Déjà en cache
        cached = get_cached_cover(content_id)
        if cached:
            print(f"   ✅ Déjà en cache : {cached.name}\n")
            skipped += 1
            continue

        # Extrait icon0.png
        icon_bytes = extract_icon0(str(pkg_file))
        if icon_bytes:
            saved = save_cover(content_id, icon_bytes, ".png")
            print(f"   ✅ Extrait : {saved.name} ({len(icon_bytes) // 1024} Ko)\n")
            ok += 1
        else:
            print(f"   ⚠️  Aucun PNG trouvé dans ce PKG\n")
            failed += 1

    print("=" * 60)
    print(f"✅ Extraits    : {ok}")
    print(f"⏭  Déjà cache : {skipped}")
    print(f"❌ Échecs      : {failed}")
    print(f"📁 Covers dans : {Path('cache/covers').resolve()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage : python tools/extract_covers.py "F:\\PS4 JailBreak\\Games"')
        sys.exit(1)

    extract_all_covers(sys.argv[1])