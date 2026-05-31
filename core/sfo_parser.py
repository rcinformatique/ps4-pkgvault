import struct
from pathlib import Path


# Magic number fichier SFO Sony
SFO_MAGIC = 0x00505346  # "\x00PSF"

# Formats de données SFO
FMT_UTF8_SPECIAL = 0x0004
FMT_UTF8         = 0x0204
FMT_INT32        = 0x0404

# Mapping catégorie SFO → type PKGVault
CATEGORY_MAP = {
    "gd":  "game",
    "gdc": "game",
    "gda": "game",
    "gdo": "game",
    "gp":  "update",
    "gdp": "update",
    "ac":  "dlc",
}

# Bitmask langues PS4
LANG_BITS = {
    0:  "Japonais",
    1:  "Anglais (US)",
    2:  "Français",
    3:  "Espagnol",
    4:  "Allemand",
    5:  "Italien",
    6:  "Néerlandais",
    7:  "Portugais (PT)",
    8:  "Russe",
    9:  "Coréen",
    10: "Chinois (trad.)",
    11: "Chinois (simp.)",
    12: "Finnois",
    13: "Suédois",
    14: "Danois",
    15: "Norvégien",
    16: "Polonais",
    17: "Portugais (BR)",
    18: "Anglais (UK)",
    19: "Turc",
    20: "Espagnol (LA)",
    21: "Arabe",
    22: "Grec",
    23: "Roumain",
    24: "Thaï",
    25: "Vietnamien",
    26: "Indonésien",
}


def _parse_system_ver(raw_int: int) -> str:
    """Convertit SYSTEM_VER entier en version lisible."""
    if raw_int <= 0:
        return ""
    major = (raw_int >> 24) & 0xFF
    minor = (raw_int >> 16) & 0xFF
    return f"{major}.{minor:02d}"


def _parse_languages(lang_mask: int) -> list[str]:
    """Convertit le bitmask LANG en liste de langues."""
    langs = []
    for bit, name in LANG_BITS.items():
        if lang_mask & (1 << bit):
            langs.append(name)
    return langs


def _detect_region(content_id: str) -> str:
    """Détecte la région depuis le Content-ID."""
    if not content_id:
        return ""
    prefix = content_id[:2].upper()
    regions = {
        "EP": "Europe",
        "UP": "USA",
        "JP": "Japon",
        "HP": "Asie",
        "SP": "Asie",
        "IP": "Inde",
    }
    return regions.get(prefix, "")


def parse_sfo(data: bytes) -> dict:
    """
    Parse un fichier SFO depuis ses bytes bruts.
    Retourne un dictionnaire avec toutes les clés trouvées.
    """
    result = {}

    if len(data) < 20:
        return result

    magic, version, key_table_off, data_table_off, entry_count = \
        struct.unpack_from("<IIIII", data, 0)

    if magic != SFO_MAGIC:
        return result

    index_off = 20
    for i in range(entry_count):
        entry_off = index_off + i * 16
        if entry_off + 16 > len(data):
            break

        key_off, data_fmt, data_len, data_maxlen, data_off = \
            struct.unpack_from("<HHIII", data, entry_off)

        abs_key_off = key_table_off + key_off
        try:
            key_end = data.index(b"\x00", abs_key_off)
            key     = data[abs_key_off:key_end].decode(
                "ascii", errors="ignore"
            )
        except ValueError:
            continue

        abs_data_off = data_table_off + data_off
        raw = data[abs_data_off: abs_data_off + data_len]

        if data_fmt in (FMT_UTF8, FMT_UTF8_SPECIAL):
            value = raw.rstrip(b"\x00").decode("utf-8", errors="ignore")
        elif data_fmt == FMT_INT32:
            value = struct.unpack_from("<I", raw)[0] if len(raw) >= 4 else 0
        else:
            value = raw

        result[key] = value

    return result


def _find_sfo_via_table(f, file_size: int) -> bytes | None:
    """
    Cherche param.sfo via la table des entrées PKG.
    Entry ID 0x1000 = param.sfo
    """
    try:
        # entry_count à 0x10 (uint16 BE)
        f.seek(0x10)
        entry_count = struct.unpack(">H", f.read(2))[0]

        # table offset à 0x18 (uint32 BE)
        f.seek(0x18)
        table_offset = struct.unpack(">I", f.read(4))[0]

        if entry_count == 0 or table_offset == 0:
            return None

        for i in range(entry_count):
            entry_base = table_offset + i * 32
            if entry_base + 32 > file_size:
                break

            f.seek(entry_base)
            entry_id = struct.unpack(">I", f.read(4))[0]
            f.read(12)
            data_offset = struct.unpack(">I", f.read(4))[0]
            data_size   = struct.unpack(">I", f.read(4))[0]

            if entry_id == 0x1000 and data_size > 0:
                if data_offset + data_size <= file_size:
                    f.seek(data_offset)
                    return f.read(data_size)
    except (struct.error, OSError):
        pass

    return None


def _find_sfo_by_scan(f, file_size: int) -> bytes | None:
    """
    Fallback : cherche la signature 0x00PSF
    dans les 20 premiers Mo du fichier.
    """
    SIGNATURE  = b"\x00PSF"
    scan_limit = min(file_size, 20 * 1024 * 1024)
    chunk_size = 1024 * 1024
    offset     = 0

    while offset < scan_limit:
        f.seek(offset)
        chunk = f.read(chunk_size)
        if not chunk:
            break

        idx = chunk.find(SIGNATURE)
        if idx != -1:
            sfo_offset = offset + idx
            f.seek(sfo_offset)
            sfo_data = f.read(65536)
            parsed   = parse_sfo(sfo_data)
            if parsed:
                return sfo_data

        offset += chunk_size - 4

    return None


def extract_sfo_from_pkg(pkg_path: str | Path) -> dict | None:
    """
    Extrait et parse le param.sfo depuis un fichier PKG PS4.
    Essaie d'abord via la table des entrées,
    puis par scan direct si la table échoue.
    Retourne le dict SFO ou None.
    """
    try:
        pkg_path  = Path(pkg_path)
        file_size = pkg_path.stat().st_size

        with open(pkg_path, "rb") as f:
            # Vérifie le magic PKG
            magic = struct.unpack(">I", f.read(4))[0]
            if magic != 0x7F434E54:
                return None

            # Méthode 1 : table des entrées
            sfo_data = _find_sfo_via_table(f, file_size)

            # Méthode 2 : scan direct
            if not sfo_data:
                sfo_data = _find_sfo_by_scan(f, file_size)

            if not sfo_data:
                return None

            return parse_sfo(sfo_data)

    except (OSError, struct.error):
        return None


def get_pkg_metadata(pkg_path: str | Path) -> dict:
    """
    Extrait toutes les métadonnées utiles d'un PKG.
    Retourne un dict normalisé prêt pour la BDD.
    """
    sfo = extract_sfo_from_pkg(pkg_path) or {}

    # Titre
    title = sfo.get("TITLE", "").strip()

    # Content-ID
    content_id = sfo.get("CONTENT_ID", "").strip()
    if not content_id:
        content_id = sfo.get("TITLE_ID", "").strip()

    # Versions
    app_ver = sfo.get("APP_VER", "").strip()
    version = sfo.get("VERSION", "").strip()

    # Firmware
    sys_ver_raw = sfo.get("SYSTEM_VER", 0)
    firmware    = _parse_system_ver(sys_ver_raw) if sys_ver_raw else ""

    # Type via catégorie SFO
    category = sfo.get("CATEGORY", "").strip().lower()
    pkg_type = CATEGORY_MAP.get(category)

    # Langues
    lang_mask = sfo.get("LANG", 0)
    languages = _parse_languages(lang_mask) if lang_mask else []

    # Région
    region = _detect_region(content_id)

    return {
        "title":      title,
        "content_id": content_id,
        "app_ver":    app_ver,
        "version":    version,
        "firmware":   firmware,
        "pkg_type":   pkg_type,
        "category":   category,
        "languages":  languages,
        "region":     region,
        "sfo_raw":    sfo,
    }