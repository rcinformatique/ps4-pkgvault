#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PS4 PKGVault - Lecteur PKG PS4

Fonctions principales :
- Lire les infos du fichier PKG
- Trouver et parser le param.sfo
- Récupérer Title ID, Content ID, version, firmware, SDK, région, catégorie
- Détecter les PNG embarqués
- Exporter les images dans assets/pkg_images/CUSAxxxxx/
"""

import sys
import struct
import re
from pathlib import Path


# =====================================================================
# CONSTANTES
# =====================================================================

PKG_MAGIC = 0x7F434E54
SFO_MAGIC = b"\x00PSF"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PNG_END = b"IEND"

FMT_UTF8 = 0x0204
FMT_UINT32 = 0x0404


CATEGORY_MAP = {
    "gd": "Jeu complet PS4",
    "gp": "Mise à jour / Patch",
    "ac": "DLC / Add-on",
    "bd": "Blu-ray Disc",
    "hg": "Application",
    "gda": "Jeu PS4 avec contenu additionnel",
}


REGION_MAP = {
    "EP": "Europe",
    "UP": "USA / Amérique du Nord",
    "NP": "Amérique du Nord",
    "JP": "Japon",
    "KP": "Corée",
    "HP": "Hong Kong / Asie",
    "HB": "Hong Kong / Asie",
    "AS": "Asie",
    "PC": "Chine",
    "HC": "Chine / Hong Kong",
    "IP": "International",
}


LANG_MAP = {
    0: "Japonais",
    1: "Anglais US",
    2: "Français",
    3: "Espagnol",
    4: "Allemand",
    5: "Italien",
    6: "Néerlandais",
    7: "Portugais",
    8: "Russe",
    9: "Coréen",
    10: "Chinois traditionnel",
    11: "Chinois simplifié",
    12: "Finnois",
    13: "Suédois",
    14: "Danois",
    15: "Norvégien",
    16: "Polonais",
    17: "Portugais BR",
    18: "Anglais UK",
}


# =====================================================================
# CHEMINS PROJET
# =====================================================================

def get_project_root():
    """
    Retourne la racine du projet.

    read_pkg.py est dans :
        tools/read_pkg.py

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


# =====================================================================
# LECTURE HEADER / SFO
# =====================================================================

def read_content_id_from_header(data):
    """
    Lit le Content-ID situé dans le header du PKG.

    Attention :
    - parfois moins fiable que le CONTENT_ID du param.sfo
    - sert surtout de fallback
    """
    raw = data[0x40:0x40 + 36]
    return raw.split(b"\x00")[0].decode("ascii", errors="ignore")


def parse_sfo(data, offset):
    """
    Parse un param.sfo trouvé dans le PKG.

    Le param.sfo contient :
    - TITLE
    - TITLE_ID
    - CONTENT_ID
    - APP_VER
    - VERSION
    - SYSTEM_VER
    - CATEGORY
    - PUBTOOLINFO
    """
    sfo = data[offset:]

    if sfo[:4] != SFO_MAGIC:
        raise ValueError("Magic SFO invalide")

    key_table_offset = struct.unpack_from("<I", sfo, 0x08)[0]
    data_table_offset = struct.unpack_from("<I", sfo, 0x0C)[0]
    entry_count = struct.unpack_from("<I", sfo, 0x10)[0]

    result = {}

    for i in range(entry_count):
        entry = 0x14 + i * 16

        key_offset = struct.unpack_from("<H", sfo, entry)[0]
        fmt = struct.unpack_from("<H", sfo, entry + 2)[0]
        data_len = struct.unpack_from("<I", sfo, entry + 4)[0]
        data_offset = struct.unpack_from("<I", sfo, entry + 12)[0]

        key_start = key_table_offset + key_offset
        key_end = sfo.index(b"\x00", key_start)
        key = sfo[key_start:key_end].decode("utf-8", errors="ignore")

        value_start = data_table_offset + data_offset
        raw = sfo[value_start:value_start + data_len]

        if fmt == FMT_UTF8:
            value = raw.split(b"\x00")[0].decode("utf-8", errors="ignore")
        elif fmt == FMT_UINT32:
            value = struct.unpack_from("<I", raw, 0)[0]
        else:
            value = raw.hex()

        result[key] = value

    return result


# =====================================================================
# PARSERS MÉTADONNÉES
# =====================================================================

def parse_system_ver(value):
    """
    Convertit SYSTEM_VER en version lisible.

    Exemple :
        0x05508000 -> 5.80
        0x12008000 -> 18.00
    """
    if not isinstance(value, int):
        return ""

    major = (value >> 24) & 0xFF
    minor = (value >> 16) & 0xFF

    return f"{major}.{minor:02d}" if major else f"0x{value:08X}"


def parse_sdk_from_pubtoolinfo(pubtoolinfo):
    """
    Extrait le sdk_ver depuis PUBTOOLINFO.

    Exemple :
        sdk_ver=12008000 -> 18.00
    """
    if not pubtoolinfo:
        return ""

    match = re.search(r"sdk_ver=([0-9A-Fa-f]+)", pubtoolinfo)

    if not match:
        return ""

    sdk_hex = match.group(1)

    try:
        value = int(sdk_hex, 16)
        return parse_system_ver(value) + f" ({sdk_hex})"
    except ValueError:
        return sdk_hex


def parse_content_id(content_id):
    """
    Parse le CONTENT_ID PS4.

    Exemple :
        EP4295-CUSA13367_00-ASTERIXXXL2EUR00

    Donne :
        Store Code      : EP
        Code éditeur    : 4295
        Title ID        : CUSA13367
        Code produit    : 00
        Nom interne     : ASTERIXXXL2EUR00
    """
    result = {
        "region_code": "",
        "region": "",
        "publisher_code": "",
        "title_id": "",
        "product_code": "",
        "internal_name": "",
    }

    content_id = str(content_id or "").strip().replace("\x00", "")

    match = re.match(
        r"^([A-Z]{2})(\d{4})-(CUSA\d{5})_([A-Z0-9]{2})-(.+)$",
        content_id
    )

    if not match:
        return result

    region_code, publisher_code, title_id, product_code, internal_name = match.groups()

    result["region_code"] = region_code
    result["region"] = REGION_MAP.get(region_code, "Inconnue")
    result["publisher_code"] = publisher_code
    result["title_id"] = title_id
    result["product_code"] = product_code
    result["internal_name"] = internal_name

    return result


def parse_languages(mask):
    """
    Décode le champ LANG du param.sfo.

    Attention :
    - beaucoup de PKG récents ne renseignent pas LANG
    - dans ce cas, mask = 0
    """
    if not isinstance(mask, int):
        return []

    return [name for bit, name in LANG_MAP.items() if mask & (1 << bit)]


def get_localized_titles(sfo):
    """
    Récupère uniquement les titres localisés :
        TITLE_01
        TITLE_02
        TITLE_03
        etc.

    Évite de confondre TITLE_ID avec un titre localisé.
    """
    return {
        key: sfo[key]
        for key in sorted(sfo.keys())
        if re.match(r"^TITLE_\d{2}$", key)
    }


def clean_title_for_api(title):
    """
    Nettoie le titre pour les recherches API.
    """
    if not title:
        return ""

    title = re.sub(r"™|®|©", "", title)
    title = re.sub(r"\s+", " ", title)

    return title.strip()


# =====================================================================
# IMAGES EMBARQUÉES
# =====================================================================

def find_png_offsets(data):
    """
    Recherche toutes les signatures PNG dans le PKG.
    """
    offsets = []
    pos = 0

    while True:
        pos = data.find(PNG_MAGIC, pos)

        if pos == -1:
            break

        offsets.append(pos)
        pos += len(PNG_MAGIC)

    return offsets


def extract_png(data, offset):
    """
    Extrait un PNG depuis un offset donné.

    On cherche le chunk final IEND.
    """
    end = data.find(PNG_END, offset)

    if end == -1:
        return None

    # IEND + CRC = 8 octets après le mot IEND
    end += 8

    return data[offset:end]


def export_cover_image(data, title_id):
    """
    Exporte uniquement la jaquette (icon0.png)
    dans :

        assets/covers/CUSAxxxxx.png
    """

    png_offsets = find_png_offsets(data)

    if not png_offsets:
        return None

    # Le premier PNG trouvé dans un PKG PS4 est généralement icon0.png
    icon_offset = png_offsets[0]

    png = extract_png(data, icon_offset)

    if not png:
        return None

    cover_dir = get_assets_dir() / "covers"
    cover_dir.mkdir(parents=True, exist_ok=True)

    out_file = cover_dir / f"{title_id}.png"

    out_file.write_bytes(png)

    return {
        "offset": icon_offset,
        "size": len(png),
        "path": str(out_file),
    }


# =====================================================================
# OUTILS AFFICHAGE
# =====================================================================

def print_row(label, value):
    """
    Affiche une ligne formatée.
    """
    print(f"{label:<24}: {value if value not in [None, ''] else '—'}")


# =====================================================================
# LECTURE PKG PRINCIPALE
# =====================================================================

def build_pkg_info(pkg_path, export_images=False):
    """
    Lit un PKG PS4 et retourne toutes les informations utiles sous forme dict.

    Cette fonction est utilisée par :
    - read_pkg.py
    - api_pkg.py
    """
    path = Path(pkg_path)

    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    data = path.read_bytes()

    magic = struct.unpack_from(">I", data, 0)[0]
    content_id_header = read_content_id_from_header(data)

    # On ne dépend pas d'un offset fixe : on cherche la signature du SFO
    sfo_offset = data.find(SFO_MAGIC)

    if sfo_offset == -1:
        raise ValueError("param.sfo introuvable dans ce PKG")

    sfo = parse_sfo(data, sfo_offset)

    title = sfo.get("TITLE", "")
    title_id = sfo.get("TITLE_ID", "")

    # Le CONTENT_ID du SFO est prioritaire
    content_id = str(sfo.get("CONTENT_ID", "")).strip() or content_id_header.strip()

    app_ver = sfo.get("APP_VER", "")
    version = sfo.get("VERSION", "")
    category = sfo.get("CATEGORY", "")
    system_ver = sfo.get("SYSTEM_VER", "")
    pubtoolinfo = sfo.get("PUBTOOLINFO", "")
    lang_mask = sfo.get("LANG", 0)

    cid_info = parse_content_id(content_id)
    languages = parse_languages(lang_mask)
    localized_titles = get_localized_titles(sfo)

    final_title_id = title_id or cid_info["title_id"]

    png_offsets = find_png_offsets(data)
    cover = None

    if export_images:
        cover = export_cover_image(data, final_title_id)

    return {
        "filename": path.name,
        "path": str(path),
        "size": path.stat().st_size,
        "magic": f"0x{magic:08X}",
        "pkg_valid": magic == PKG_MAGIC,
        "content_id_header": content_id_header,
        "sfo_offset": sfo_offset,

        "title": title,
        "title_api": clean_title_for_api(title),
        "title_id": final_title_id,
        "content_id": content_id,

        "internal_name": cid_info["internal_name"],
        "product_code": cid_info["product_code"],
        "publisher_code": cid_info["publisher_code"],
        "store_code": cid_info["region_code"],
        "store_region": cid_info["region"],

        "app_ver": app_ver,
        "version": version,
        "category": category,
        "category_label": CATEGORY_MAP.get(category, "Inconnu"),

        "firmware": parse_system_ver(system_ver),
        "system_ver_hex": f"0x{system_ver:08X}" if isinstance(system_ver, int) else "",
        "sdk": parse_sdk_from_pubtoolinfo(pubtoolinfo),

        "platform": "PS4",
        "distribution": "Digital" if "digital" in pubtoolinfo.lower() else "Inconnue",

        "lang_mask": f"0x{lang_mask:08X}" if isinstance(lang_mask, int) else lang_mask,
        "languages": languages,
        "localized_titles_count": len(localized_titles),
        "localized_titles": localized_titles,

        "png_count": len(png_offsets),
        "png_offsets": png_offsets,
        "cover": cover,

        "pubtoolinfo": pubtoolinfo,
        "sfo": sfo,
    }


def get_pkg_info(pkg_path):
    """
    Fonction simple utilisée par api_pkg.py.

    Elle lit le PKG sans exporter les images.
    """
    return build_pkg_info(pkg_path, export_images=False)


# =====================================================================
# MODE CONSOLE
# =====================================================================

def main():
    if len(sys.argv) < 2:
        print('Usage : python tools/read_pkg.py "fichier.pkg"')
        print('Option : python tools/read_pkg.py "fichier.pkg" --export-images')
        sys.exit(1)

    pkg_path = sys.argv[1]
    export_images = "--export-images" in sys.argv

    info = build_pkg_info(pkg_path, export_images=export_images)

    print("=" * 70)
    print("LECTURE PKG PS4 — MAX INFOS")
    print("=" * 70)

    print_row("Fichier", info["filename"])
    print_row("Chemin", info["path"])
    print_row("Taille", f'{info["size"]:,} octets')
    print_row("Magic", info["magic"])
    print_row("PKG valide", "Oui" if info["pkg_valid"] else "Non")
    print_row("Content-ID header", info["content_id_header"])
    print_row("Offset param.sfo", info["sfo_offset"])

    print("\n" + "-" * 70)
    print("INFOS PRINCIPALES")
    print("-" * 70)

    print_row("Titre", info["title"])
    print_row("Titre API nettoyé", info["title_api"])
    print_row("Title ID", info["title_id"])
    print_row("Content ID", info["content_id"])
    print_row("Nom interne produit", info["internal_name"])
    print_row("Code produit", info["product_code"])
    print_row("Version APP_VER", info["app_ver"])
    print_row("Version VERSION", info["version"])
    print_row("Firmware minimum", info["firmware"])
    print_row("SYSTEM_VER hex", info["system_ver_hex"])
    print_row("SDK", info["sdk"])

    print("\n" + "-" * 70)
    print("CATÉGORIE / TYPE")
    print("-" * 70)

    print_row("Code catégorie", info["category"])
    print_row("Type détecté", info["category_label"])

    print("\n" + "-" * 70)
    print("RÉGION / IDENTIFIANTS")
    print("-" * 70)

    print_row("Store Code", info["store_code"])
    print_row("Store Region", info["store_region"])
    print_row("Code éditeur", info["publisher_code"])
    print_row("Title ID", info["title_id"])
    print_row("Plateforme", info["platform"])
    print_row("Distribution", info["distribution"])
    print_row("Nom interne produit", info["internal_name"])

    print("\n" + "-" * 70)
    print("LANGUES")
    print("-" * 70)

    print_row("LANG bitmask", info["lang_mask"])

    if info["languages"]:
        print_row("Langues SFO", ", ".join(info["languages"]))
    else:
        print_row("Langues SFO", "Non présentes dans le param.sfo")

    print_row("Titres localisés", info["localized_titles_count"])

    print("\n" + "-" * 70)
    print("TITRES LOCALISÉS")
    print("-" * 70)

    if info["localized_titles"]:
        for key, value in info["localized_titles"].items():
            print_row(key, value)
    else:
        print("Aucun titre localisé trouvé.")

    print("\n" + "-" * 70)
    print("IMAGES EMBARQUÉES")
    print("-" * 70)

    print_row("PNG trouvés", info["png_count"])

    for index, offset in enumerate(info["png_offsets"][:10], start=1):
        print_row(f"PNG #{index}", offset)

    if export_images:
        print("\nJAQUETTE")

        if info["cover"]:
            print(f"Fichier : {info['cover']['path']}")
            print(f"Taille  : {info['cover']['size']} octets")
            print(f"Offset  : {info['cover']['offset']}")
        else:
            print("Aucune jaquette trouvée.")

    print("\n" + "-" * 70)
    print("PUBTOOLINFO")
    print("-" * 70)

    print(info["pubtoolinfo"] if info["pubtoolinfo"] else "—")

    print("\n" + "-" * 70)
    print("TOUTES LES CLÉS SFO")
    print("-" * 70)

    for key, value in sorted(info["sfo"].items()):
        if isinstance(value, int):
            print(f"{key:<28} = {value} / 0x{value:08X}")
        else:
            print(f"{key:<28} = {value}")


if __name__ == "__main__":
    main()