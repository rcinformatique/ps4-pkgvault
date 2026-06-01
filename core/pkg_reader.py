import re
import struct
from pathlib import Path


# ------------------------------------------------------------------ #
#  Constantes                                                          #
# ------------------------------------------------------------------ #

PKG_MAGIC  = 0x7F434E54
SFO_MAGIC  = b"\x00PSF"
PNG_MAGIC  = b"\x89PNG\r\n\x1a\n"
PNG_END    = b"IEND"
FMT_UTF8   = 0x0204
FMT_UINT32 = 0x0404

CATEGORY_MAP = {
    "gd":  "game",
    "gdc": "game",
    "gda": "game",
    "gdo": "game",
    "gp":  "update",
    "gdp": "update",
    "ac":  "dlc",
    "bd":  "game",
    "hg":  "game",
}

CATEGORY_LABEL_MAP = {
    "gd":  "Jeu complet PS4",
    "gp":  "Mise à jour / Patch",
    "ac":  "DLC / Add-on",
    "bd":  "Blu-ray Disc",
    "hg":  "Application",
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
    0:  "Japonais",
    1:  "Anglais US",
    2:  "Français",
    3:  "Espagnol",
    4:  "Allemand",
    5:  "Italien",
    6:  "Néerlandais",
    7:  "Portugais",
    8:  "Russe",
    9:  "Coréen",
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


# ------------------------------------------------------------------ #
#  Parsers SFO                                                         #
# ------------------------------------------------------------------ #

def _read_content_id_from_header(data: bytes) -> str:
    raw = data[0x40:0x40 + 36]
    return raw.split(b"\x00")[0].decode("ascii", errors="ignore")


def _parse_sfo(data: bytes, offset: int) -> dict:
    sfo = data[offset:]
    if sfo[:4] != SFO_MAGIC:
        return {}

    key_table_offset  = struct.unpack_from("<I", sfo, 0x08)[0]
    data_table_offset = struct.unpack_from("<I", sfo, 0x0C)[0]
    entry_count       = struct.unpack_from("<I", sfo, 0x10)[0]

    result = {}
    for i in range(entry_count):
        entry       = 0x14 + i * 16
        key_offset  = struct.unpack_from("<H", sfo, entry)[0]
        fmt         = struct.unpack_from("<H", sfo, entry + 2)[0]
        data_len    = struct.unpack_from("<I", sfo, entry + 4)[0]
        data_offset = struct.unpack_from("<I", sfo, entry + 12)[0]

        key_start = key_table_offset + key_offset
        key_end   = sfo.index(b"\x00", key_start)
        key       = sfo[key_start:key_end].decode("utf-8", errors="ignore")

        value_start = data_table_offset + data_offset
        raw         = sfo[value_start:value_start + data_len]

        if fmt == FMT_UTF8:
            value = raw.split(b"\x00")[0].decode("utf-8", errors="ignore")
        elif fmt == FMT_UINT32:
            value = struct.unpack_from("<I", raw, 0)[0]
        else:
            value = raw.hex()

        result[key] = value

    return result


def _parse_system_ver(value: int) -> str:
    if not isinstance(value, int) or value == 0:
        return ""
    major = (value >> 24) & 0xFF
    minor = (value >> 16) & 0xFF
    return f"{major}.{minor:02d}" if major else f"0x{value:08X}"


def _parse_sdk(pubtoolinfo: str) -> str:
    if not pubtoolinfo:
        return ""
    match = re.search(r"sdk_ver=([0-9A-Fa-f]+)", pubtoolinfo)
    if not match:
        return ""
    try:
        value = int(match.group(1), 16)
        return _parse_system_ver(value)
    except ValueError:
        return match.group(1)


def _parse_content_id(content_id: str) -> dict:
    result = {
        "region_code":    "",
        "region":         "",
        "publisher_code": "",
        "title_id":       "",
        "product_code":   "",
        "internal_name":  "",
    }
    content_id = str(content_id or "").strip().replace("\x00", "")
    match = re.match(
        r"^([A-Z]{2})(\d{4})-((?:CUSA|CUSE)\d{5})_([A-Z0-9]{2})-(.+)$",
        content_id
    )
    if not match:
        return result
    rc, pub, tid, pc, name = match.groups()
    result["region_code"]    = rc
    result["region"]         = REGION_MAP.get(rc, "Inconnue")
    result["publisher_code"] = pub
    result["title_id"]       = tid
    result["product_code"]   = pc
    result["internal_name"]  = name
    return result


def _parse_languages(mask: int) -> list[str]:
    if not isinstance(mask, int):
        return []
    return [name for bit, name in LANG_MAP.items() if mask & (1 << bit)]


def _get_localized_titles(sfo: dict) -> dict:
    return {
        k: sfo[k]
        for k in sorted(sfo.keys())
        if re.match(r"^TITLE_\d{2}$", k)
    }


def _clean_title_for_api(title: str) -> str:
    if not title:
        return ""
    title = re.sub(r"™|®|©", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


# ------------------------------------------------------------------ #
#  Extraction PNG                                                      #
# ------------------------------------------------------------------ #

def _find_png_offsets(data: bytes) -> list[int]:
    offsets = []
    pos     = 0
    while True:
        pos = data.find(PNG_MAGIC, pos)
        if pos == -1:
            break
        offsets.append(pos)
        pos += len(PNG_MAGIC)
    return offsets


def _extract_png(data: bytes, offset: int) -> bytes | None:
    end = data.find(PNG_END, offset)
    if end == -1:
        return None
    return data[offset:end + 8]


def extract_icon0_png(data: bytes) -> bytes | None:
    """Extrait icon0.png (premier PNG) depuis les bytes du PKG."""
    offsets = _find_png_offsets(data)
    if not offsets:
        return None
    return _extract_png(data, offsets[0])


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def _detect_backport_from_sfo(
    category: str,
    system_ver: int,
    pubtoolinfo: str
) -> bool:
    """
    Détecte un backport depuis les données SFO uniquement.
    Un backport a un sdk_ver inférieur au system_ver.
    Ex: system_ver=6.80, sdk_ver=5.05 → backport
    """
    if category not in ("gp", "gd"):
        return False

    if not pubtoolinfo:
        return False

    import re
    match = re.search(r"sdk_ver=([0-9A-Fa-f]+)", pubtoolinfo)
    if not match:
        return False

    try:
        sdk_int = int(match.group(1), 16)
    except ValueError:
        return False

    # sdk_ver et system_ver ont le même format 0xMMmmxxxx
    # Si le SDK est significativement inférieur au firmware → backport
    sdk_major    = (sdk_int    >> 24) & 0xFF
    system_major = (system_ver >> 24) & 0xFF if isinstance(system_ver, int) else 0

    if system_major == 0:
        return False

    # Backport si SDK au moins 1 version majeure en dessous
    return sdk_major < system_major


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.1f} Go"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} Mo"
    return f"{size_bytes / 1024:.1f} Ko"


# ------------------------------------------------------------------ #
#  Fonction principale                                                 #
# ------------------------------------------------------------------ #

def read_pkg(filepath: str | Path) -> dict | None:
    """
    Lit un fichier PKG PS4 sans le charger entièrement en mémoire.
    Retourne None si le fichier n'est pas un PKG valide.
    """
    path = Path(filepath)

    try:
        file_size = path.stat().st_size

        with open(path, "rb") as f:

            # Vérifie le magic (4 bytes)
            magic = struct.unpack_from(">I", f.read(4))[0]
            if magic != PKG_MAGIC:
                return None

            # Content-ID header (offset 0x40)
            f.seek(0x40)
            raw_cid           = f.read(36)
            content_id_header = raw_cid.split(b"\x00")[0].decode(
                "ascii", errors="ignore"
            )

            # Lit les premiers 512 Ko — contient toujours le SFO
            f.seek(0)
            header_data = f.read(512 * 1024)

        # Cherche le SFO dans les 512 Ko
        sfo_offset = header_data.find(SFO_MAGIC)

        # Si pas trouvé, essaie dans 2 Mo
        if sfo_offset == -1:
            with open(path, "rb") as f:
                header_data = f.read(2 * 1024 * 1024)
            sfo_offset = header_data.find(SFO_MAGIC)

        if sfo_offset == -1:
            return None

        sfo = _parse_sfo(header_data, sfo_offset)
        if not sfo:
            return None

    except OSError:
        return None

    # Champs SFO
    title       = sfo.get("TITLE", "")
    title_id    = sfo.get("TITLE_ID", "")
    content_id  = str(sfo.get("CONTENT_ID", "")).strip() or content_id_header.strip()
    app_ver     = sfo.get("APP_VER", "")
    version     = sfo.get("VERSION", "")
    category    = sfo.get("CATEGORY", "").lower()
    system_ver  = sfo.get("SYSTEM_VER", 0)
    pubtoolinfo = sfo.get("PUBTOOLINFO", "")
    lang_mask   = sfo.get("LANG", 0)

    # Parse Content-ID
    cid_info       = _parse_content_id(content_id)
    final_title_id = title_id or cid_info["title_id"]

    # Type PKG
    pkg_type = CATEGORY_MAP.get(category, "game")
    if pkg_type in ("game", "update"):
        if _detect_backport_from_sfo(category, system_ver, pubtoolinfo):
            pkg_type = "backport"

    # Région
    region = cid_info["region"] or REGION_MAP.get(content_id[:2], "")

    return {
        "filepath":    str(path),
        "filename":    path.name,
        "size_bytes":  file_size,
        "size_str":    _format_size(file_size),

        "title":           title,
        "title_api":       _clean_title_for_api(title),
        "title_id":        final_title_id,
        "content_id":      content_id,
        "internal_name":   cid_info["internal_name"],
        "product_code":    cid_info["product_code"],
        "publisher_code":  cid_info["publisher_code"],

        "type":            pkg_type,
        "category":        category,
        "category_label":  CATEGORY_LABEL_MAP.get(category, "Inconnu"),

        "app_ver":         app_ver,
        "version":         version,
        "firmware":        _parse_system_ver(system_ver),
        "system_ver_hex":  f"0x{system_ver:08X}" if isinstance(system_ver, int) else "",
        "sdk":             _parse_sdk(pubtoolinfo),

        "region":          region,
        "store_code":      cid_info["region_code"],
        "platform":        "PS4",
        "distribution":    "Digital" if "digital" in pubtoolinfo.lower() else "Inconnue",
        "pubtoolinfo":     pubtoolinfo,

        "languages":        _parse_languages(lang_mask),
        "lang_mask":        f"0x{lang_mask:08X}" if isinstance(lang_mask, int) else "",
        "localized_titles": _get_localized_titles(sfo),

        "title_api_result": "",
        "description":      "",
        "developer":        "",
        "publisher":        "",
        "release_date":     "",
        "genres":           [],
        "rating":           0,
        "cover_path":       "",
        "screenshots":      [],
        "video_url":        "",
        "api_fetched":      0,
    }