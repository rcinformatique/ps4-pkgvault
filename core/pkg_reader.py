import struct
import re
from pathlib import Path
from core.sfo_parser import get_pkg_metadata, CATEGORY_MAP


# Magic PKG PS4
PKG_MAGIC = 0x7F434E54

# Content types depuis le header (fallback si SFO absent)
CONTENT_TYPES = {
    0x18: "game",
    0x19: "game",
    0x1A: "game",
    0x1B: "game",
    0x1C: "dlc",
    0x1D: "dlc",
    0x1E: "update",
    0x1F: "update",
    0x20: "update",
}


def _detect_type_by_filename(filename: str) -> str:
    """Détection du type par le nom de fichier en fallback."""
    name = filename.upper()
    if any(p in name for p in [
        "BACKPORT", "[BP]", "_BP_", "-BP-", ".BP.", "BP9.", "BP7."
    ]):
        return "backport"
    if any(p in name for p in ["UPDATE", "_UP_", "PATCH"]):
        return "update"
    if any(p in name for p in ["DLC", "ADDON"]):
        return "dlc"
    return "game"


def _clean_title(stem: str) -> str:
    """Nettoie le nom de fichier pour en extraire un titre lisible."""
    title = stem
    title = re.sub(r'^\[.*?\]\s*-?\s*', '', title)
    title = re.sub(
        r'[_\-]?(CUSA|CUSE|EP|HB|HP|NPEA|NPUB|BLES|BLUS)\w+',
        '', title, flags=re.IGNORECASE
    )
    title = re.sub(r'[-_]?v?\d+\.\d+[\d\.]*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[-_]?app[_\-]ver.*', '', title, flags=re.IGNORECASE)
    for pattern in [
        r'\bBACKPORT\b', r'\bUPDATE\b', r'\bPATCH\b',
        r'\bDLC\b', r'\bADDON\b', r'\bPS4\b', r'\bPKG\b', r'\bFW\b',
    ]:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    title = re.sub(r'[_\-\.]+', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    title = ' '.join(w.capitalize() for w in title.split())
    return title if title else stem


def _format_size(size_bytes: int) -> str:
    """Convertit un nombre d'octets en chaîne lisible."""
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.1f} Go"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} Mo"
    return f"{size_bytes / 1024:.1f} Ko"


def _extract_firmware_from_filename(stem: str) -> str:
    """Extrait la version firmware depuis le nom de fichier."""
    patterns = [
        r'fw[-_]?(\d+\.\d+)',
        r'firmware[-_]?(\d+\.\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, stem, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def read_pkg(filepath: str | Path) -> dict | None:
    """
    Lit un fichier PKG et retourne ses métadonnées complètes.
    Priorité : param.sfo > header PKG > nom de fichier.
    Retourne None si le fichier n'est pas un PKG valide.
    """
    filepath = Path(filepath)

    try:
        file_size = filepath.stat().st_size

        with open(filepath, "rb") as f:
            # Vérifie la signature magic
            magic = struct.unpack(">I", f.read(4))[0]
            if magic != PKG_MAGIC:
                return None

            # Content type depuis le header
            f.seek(0x018)
            content_type = struct.unpack(">I", f.read(4))[0]

            # Content-ID depuis le header
            f.seek(0x040)
            raw_cid    = f.read(36)
            header_cid = raw_cid.split(b"\x00")[0].decode(
                "ascii", errors="ignore"
            ).strip()

        # Métadonnées depuis param.sfo
        sfo_meta = get_pkg_metadata(filepath)

        # Titre : SFO > nom de fichier nettoyé
        title = sfo_meta.get("title") or _clean_title(filepath.stem)

        # Content-ID : SFO > header
        content_id = sfo_meta.get("content_id") or header_cid or "UNKNOWN"

        # Type : SFO > header > nom de fichier
        pkg_type = sfo_meta.get("pkg_type")
        if not pkg_type:
            pkg_type = CONTENT_TYPES.get(content_type)
        if not pkg_type:
            pkg_type = _detect_type_by_filename(filepath.name)

        # Détection backport par nom de fichier
        if pkg_type == "game":
            name_upper = filepath.name.upper()
            if any(p in name_upper for p in [
                "BACKPORT", "[BP]", "_BP_", "-BP-", ".BP.", "BP9.", "BP7."
            ]):
                pkg_type = "backport"

        # Firmware : SFO > nom de fichier
        firmware = sfo_meta.get("firmware") or \
                   _extract_firmware_from_filename(filepath.stem)

        return {
            "title":      title,
            "title_api":  "",
            "type":       pkg_type,
            "content_id": content_id,
            "app_ver":    sfo_meta.get("app_ver", ""),
            "version":    sfo_meta.get("version", ""),
            "firmware":   firmware,
            "region":     sfo_meta.get("region", ""),
            "languages":  sfo_meta.get("languages", []),
            "category":   sfo_meta.get("category", ""),
            "size_bytes": file_size,
            "size_str":   _format_size(file_size),
            "filepath":   str(filepath),
            "filename":   filepath.name,
            "cover_path": "",
            "screenshots": [],
            "description": "",
            "developer":   "",
            "publisher":   "",
            "release_date": "",
            "genres":      [],
            "rating":      0,
            "api_fetched": 0,
        }

    except (OSError, struct.error):
        return None