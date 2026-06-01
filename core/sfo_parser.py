"""
Wrapper de compatibilité — la logique est dans pkg_reader.py
"""
from pathlib import Path
import struct

from core.pkg_reader import (
    _parse_sfo,
    _parse_system_ver,
    _parse_languages,
    REGION_MAP,
    LANG_MAP,
)


def extract_sfo_from_pkg(pkg_path) -> dict | None:
    """Extrait et retourne le dict SFO brut d'un PKG."""
    path = Path(pkg_path)
    try:
        data       = path.read_bytes()
        magic      = struct.unpack_from(">I", data, 0)[0]
        if magic != 0x7F434E54:
            return None
        sfo_offset = data.find(b"\x00PSF")
        if sfo_offset == -1:
            return None
        return _parse_sfo(data, sfo_offset)
    except OSError:
        return None


def get_pkg_metadata(pkg_path) -> dict:
    """Retourne les métadonnées normalisées d'un PKG."""
    from core.pkg_reader import read_pkg
    result = read_pkg(pkg_path)
    return result or {}


def _detect_region(content_id: str) -> str:
    prefix = content_id[:2].upper()
    return REGION_MAP.get(prefix, "")