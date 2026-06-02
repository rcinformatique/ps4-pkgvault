#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PS4 PKGVault — Inspecteur de fichier PKG
Usage : python tools/inspect_pkg.py "chemin/vers/fichier.pkg"
"""

import sys
import os
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pkg_reader import (
    read_pkg,
    _parse_sfo,
    _parse_system_ver,
    _parse_languages,
    _find_png_offsets,
    extract_icon0_png,
    REGION_MAP,
    LANG_MAP,
    SFO_MAGIC,
)


# ------------------------------------------------------------------ #
#  Couleurs terminal                                                   #
# ------------------------------------------------------------------ #

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    BLUE   = "\033[94m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"

def bold(s):   return f"{C.BOLD}{s}{C.RESET}"
def blue(s):   return f"{C.BLUE}{s}{C.RESET}"
def green(s):  return f"{C.GREEN}{s}{C.RESET}"
def yellow(s): return f"{C.YELLOW}{s}{C.RESET}"
def red(s):    return f"{C.RED}{s}{C.RESET}"
def cyan(s):   return f"{C.CYAN}{s}{C.RESET}"
def gray(s):   return f"{C.GRAY}{s}{C.RESET}"
def white(s):  return f"{C.WHITE}{s}{C.RESET}"


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def format_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.2f} Go ({size_bytes:,} bytes)"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.2f} Mo ({size_bytes:,} bytes)"
    return f"{size_bytes / 1024:.2f} Ko ({size_bytes:,} bytes)"


def hex_dump(data: bytes, max_bytes: int = 64) -> str:
    lines = []
    for i in range(0, min(len(data), max_bytes), 16):
        chunk    = data[i:i+16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"  {i:04X}  {hex_part:<48}  {asc_part}")
    return "\n".join(lines)


def print_section(title: str):
    width = 60
    print(f"\n{bold(cyan('─' * width))}")
    print(f"  {bold(white(title))}")
    print(f"{bold(cyan('─' * width))}")


def print_row(key: str, value, color=None):
    k = f"{gray(key + ':'):<30}"
    if value is None or value == "" or value == [] or value == {}:
        v = gray("—")
    elif color:
        v = color(str(value))
    else:
        v = bold(str(value))
    print(f"  {k} {v}")


# ------------------------------------------------------------------ #
#  Entrées PKG                                                         #
# ------------------------------------------------------------------ #

ENTRY_IDS = {
    0x0001: "param.pfd",
    0x0010: "param.sfo",
    0x0400: "icon0.png",
    0x0401: "icon1.png",
    0x0402: "icon2.png",
    0x0403: "pic0.png",
    0x0404: "pic1.png",
    0x1000: "param.sfo (alt)",
    0x1200: "icon0.png (alt)",
    0x1201: "icon1.png (alt)",
    0x1220: "pic0.png (alt)",
    0x1240: "snd0.at9",
    0x1260: "changeinfo.xml",
}


def inspect_entries(data: bytes) -> list[dict]:
    entries = []
    try:
        entry_count  = struct.unpack_from(">H", data, 0x10)[0]
        table_offset = struct.unpack_from(">I", data, 0x18)[0]

        for i in range(min(entry_count, 50)):
            base     = table_offset + i * 32
            entry_id = struct.unpack_from(">I", data, base)[0]
            data_off = struct.unpack_from(">I", data, base + 16)[0]
            data_size= struct.unpack_from(">I", data, base + 20)[0]

            entries.append({
                "id":       f"0x{entry_id:04X}",
                "name":     ENTRY_IDS.get(entry_id, f"unknown_0x{entry_id:04X}"),
                "offset":   f"0x{data_off:08X}",
                "size":     data_size,
                "size_str": format_size(data_size) if data_size > 0 else "0",
            })
    except struct.error:
        pass
    return entries


# ------------------------------------------------------------------ #
#  Inspection principale                                               #
# ------------------------------------------------------------------ #

def inspect(pkg_path: str):
    path = Path(pkg_path)

    if not path.exists():
        print(red(f"\n❌ Fichier introuvable : {pkg_path}"))
        sys.exit(1)

    print(f"\n{bold(blue('═' * 60))}")
    print(f"  {bold(white('PS4 PKGVault — Inspecteur PKG'))}")
    print(f"{bold(blue('═' * 60))}")

    # Charge les bytes
    data      = path.read_bytes()
    file_size = len(data)

    # ── Fichier ──────────────────────────────────────────────────
    print_section("FICHIER")
    print_row("Nom",            path.name,           yellow)
    print_row("Chemin",         str(path.parent))
    print_row("Taille",         format_size(file_size), green)

    # ── Header PKG ───────────────────────────────────────────────
    print_section("HEADER PKG")
    magic = struct.unpack_from(">I", data, 0)[0]
    valid = magic == 0x7F434E54
    print_row("Magic",         f"0x{magic:08X}",     green if valid else red)
    print_row("Magic valide",  "✅ OUI" if valid else "❌ NON")

    content_id_header = data[0x40:0x76].split(b"\x00")[0].decode("ascii", errors="ignore")
    print_row("Content-ID header", content_id_header, yellow)

    entry_count  = struct.unpack_from(">H", data, 0x10)[0]
    table_offset = struct.unpack_from(">I", data, 0x18)[0]
    print_row("Nb entrées",    entry_count)
    print_row("Offset table",  f"0x{table_offset:08X}")

    print(f"\n  {gray('Header hex (64 premiers bytes) :')}")
    print(gray(hex_dump(data[:64])))

    # ── Table des entrées ─────────────────────────────────────────
    print_section("TABLE DES ENTRÉES")
    entries = inspect_entries(data)
    if entries:
        print(f"  {'ID':<12} {'Nom':<28} {'Offset':<14} {'Taille'}")
        print(f"  {gray('─'*12)} {gray('─'*28)} {gray('─'*14)} {gray('─'*20)}")
        for e in entries:
            known    = not e["name"].startswith("unknown")
            name_col = green(e["name"]) if known else gray(e["name"])
            size_col = cyan(e["size_str"]) if e["size"] > 0 else gray("0")
            print(f"  {yellow(e['id']):<20} {name_col:<38} {gray(e['offset']):<14} {size_col}")
    else:
        print(f"  {gray('Aucune entrée trouvée')}")

    # ── param.sfo ─────────────────────────────────────────────────
    print_section("PARAM.SFO — MÉTADONNÉES")
    sfo_offset = data.find(SFO_MAGIC)
    if sfo_offset != -1:
        sfo = _parse_sfo(data, sfo_offset)
        print(f"  {green('✅ param.sfo trouvé')} {gray(f'@ offset {sfo_offset}')}\n")

        main_keys = [
            ("TITLE",      "Titre",           yellow),
            ("CONTENT_ID", "Content-ID",      yellow),
            ("TITLE_ID",   "Title ID",        None),
            ("APP_VER",    "Version app",     None),
            ("VERSION",    "Version pkg",     None),
            ("CATEGORY",   "Catégorie",       cyan),
        ]
        for key, label, color in main_keys:
            print_row(label, sfo.get(key, ""), color)

        sys_ver = sfo.get("SYSTEM_VER", 0)
        print_row("Firmware minimum", _parse_system_ver(sys_ver) if sys_ver else "", green)
        print_row("SYSTEM_VER (hex)", f"0x{sys_ver:08X}" if isinstance(sys_ver, int) else "")

        lang_mask = sfo.get("LANG", 0)
        if lang_mask:
            langs = _parse_languages(lang_mask)
            print_row("LANG bitmask",     f"0x{lang_mask:08X}")
            print_row("Langues",          ", ".join(langs) if langs else "", cyan)

        pubtoolinfo = sfo.get("PUBTOOLINFO", "")
        if pubtoolinfo:
            print_row("PUBTOOLINFO", pubtoolinfo, gray)

        print(f"\n  {bold(gray('── Toutes les clés SFO ──'))}")
        for k, v in sorted(sfo.items()):
            if isinstance(v, int):
                display = f"{v}  (0x{v:08X})"
            elif isinstance(v, bytes):
                display = f"<bytes {len(v)} octets>"
            else:
                display = str(v)
            print(f"    {cyan(k):<25} = {display}")
    else:
        print(f"  {red('❌ param.sfo non trouvé')}")

    # ── Images PNG ────────────────────────────────────────────────
    print_section("IMAGES EMBARQUÉES")
    png_offsets = _find_png_offsets(data)
    print_row("PNG trouvés", len(png_offsets))
    for i, offset in enumerate(png_offsets[:10], 1):
        print(f"    {gray(f'PNG #{i}:')} offset {offset} ({offset:#010x})")

    # icon0.png
    icon_bytes = extract_icon0_png(data)
    if icon_bytes:
        print_row("icon0.png", f"{len(icon_bytes) / 1024:.1f} Ko", green)
        print(f"\n  {gray('Sauvegarder icon0.png ? (o/n) :')}", end=" ")
        try:
            save = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            save = "n"
        if save == "o":
            out = path.parent / f"{path.stem}_icon0.png"
            out.write_bytes(icon_bytes)
            print(f"  {green(f'✅ Sauvegardé : {out}')}")
    else:
        print_row("icon0.png", "Non trouvé", yellow)

    # ── Résultat read_pkg ─────────────────────────────────────────
    print_section("RÉSULTAT FINAL — read_pkg()")
    result = read_pkg(path)
    if result:
        print(f"  {green('✅ PKG lu avec succès')}\n")
        fields = [
            ("title",          "Titre",           yellow),
            ("title_api",      "Titre API",        yellow),
            ("title_id",       "Title ID",         None),
            ("content_id",     "Content-ID",       yellow),
            ("internal_name",  "Nom interne",      None),
            ("type",           "Type PKGVault",    cyan),
            ("category",       "Catégorie SFO",    None),
            ("category_label", "Type label",       None),
            ("app_ver",        "Version app",      None),
            ("firmware",       "Firmware",         green),
            ("sdk",            "SDK",              None),
            ("region",         "Région",           blue),
            ("store_code",     "Store code",       None),
            ("distribution",   "Distribution",     None),
            ("size_str",       "Taille",           green),
            ("filename",       "Fichier",          None),
        ]
        for key, label, color in fields:
            print_row(label, result.get(key, ""), color)

        langs = result.get("languages", [])
        if langs:
            print_row("Langues", ", ".join(langs[:6]) + (f" +{len(langs)-6}" if len(langs) > 6 else ""), cyan)

        loc = result.get("localized_titles", {})
        if loc:
            print(f"\n  {bold(gray('── Titres localisés ──'))}")
            for k, v in loc.items():
                print(f"    {cyan(k):<15} = {v}")
    else:
        print(f"  {red('❌ Impossible de lire ce PKG')}")

    # ── API RAWG ──────────────────────────────────────────────────
    print_section("RÉCUPÉRATION API RAWG")

    rawg_key = ""
    try:
        from core.database import Database
        db       = Database()
        rawg_key = db.get_setting("rawg_api_key", "")
        db.close()
    except Exception:
        pass

    if not rawg_key:
        rawg_key = os.environ.get("RAWG_API_KEY", "")

    if not rawg_key:
        print(f"  {gray('Entrez votre clé RAWG.io (Entrée pour ignorer) :')}", end=" ")
        try:
            rawg_key = input().strip()
        except (EOFError, KeyboardInterrupt):
            rawg_key = ""

    if rawg_key and result:
        title = result.get("title_api") or result.get("title", "")
        print(f"\n  {gray('Recherche RAWG pour :')} {yellow(title)}")
        print(f"  {gray('Appel API en cours…')}\n")

        from core.api_client import fetch_rawg_data
        rawg = fetch_rawg_data(title, rawg_key)

        if rawg:
            print(f"  {green('✅ RAWG — données trouvées')}\n")
            rawg_fields = [
                ("title_api",    "Titre API",      yellow),
                ("developer",    "Développeur",    None),
                ("publisher",    "Éditeur",        None),
                ("release_date", "Date sortie",    None),
                ("rating",       "Note",           green),
                ("cover_url",    "URL jaquette",   cyan),
                ("video_url",    "URL vidéo",      cyan),
            ]
            for key, label, color in rawg_fields:
                print_row(label, rawg.get(key, ""), color)

            genres = rawg.get("genres", [])
            if genres:
                print_row("Genres", ", ".join(genres), cyan)

            screens = rawg.get("screenshot_urls", [])
            print_row("Screenshots", f"{len(screens)} URL(s)")
            for i, url in enumerate(screens[:3]):
                print(f"    {gray(f'[{i+1}]')} {url}")

            desc = rawg.get("description", "")
            if desc:
                short = desc[:300] + "…" if len(desc) > 300 else desc
                print(f"\n  {gray('Description :')}")
                print(f"  {short}")
        else:
            print(f"  {red('❌ RAWG — aucun résultat')}")

    elif not rawg_key:
        print(f"  {gray('Test RAWG ignoré — pas de clé')}")

    # ── PS Store ──────────────────────────────────────────────────
    print_section("PS STORE — JAQUETTE")
    if result:
        content_id = result.get("content_id", "")
        print_row("Content-ID utilisé", content_id, yellow)
        print(f"\n  {gray('Test PS Store en cours…')}")

        from core.cover_loader import fetch_psstore_cover
        cover_bytes = fetch_psstore_cover(content_id)
        if cover_bytes:
            size_kb = len(cover_bytes) / 1024
            print(f"  {green(f'✅ Jaquette PS Store trouvée ({size_kb:.1f} Ko)')}")

            print(f"\n  {gray('Sauvegarder la jaquette ? (o/n) :')}", end=" ")
            try:
                save = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                save = "n"
            if save == "o":
                out = path.parent / f"{path.stem}_cover.jpg"
                out.write_bytes(cover_bytes)
                print(f"  {green(f'✅ Sauvegardé : {out}')}")
        else:
            print(f"  {yellow('⚠️  Jaquette PS Store non trouvée')}")

    print(f"\n{bold(blue('═' * 60))}\n")


# ------------------------------------------------------------------ #
#  Point d'entrée                                                      #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"\n{yellow('Usage :')} python tools/inspect_pkg.py \"chemin/vers/fichier.pkg\"")
        print(f"\n{gray('Exemple :')}")
        print(f"  python tools/inspect_pkg.py \"F:/PS4/Spider-Man.pkg\"\n")
        sys.exit(0)

    inspect(sys.argv[1])