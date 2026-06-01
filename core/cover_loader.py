import struct
import requests
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


COVERS_DIR      = Path("cache/covers")
SCREENSHOTS_DIR = Path("cache/screenshots")
COVERS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------ #
#  Cache disque                                                        #
# ------------------------------------------------------------------ #

def get_cached_cover(content_id: str) -> Path | None:
    for ext in (".jpg", ".png", ".webp"):
        path = COVERS_DIR / f"{content_id}{ext}"
        if path.exists():
            return path
    return None


def save_cover(content_id: str, data: bytes, ext: str = ".jpg") -> Path:
    path = COVERS_DIR / f"{content_id}{ext}"
    path.write_bytes(data)
    return path


def get_cached_screenshot(content_id: str, index: int) -> Path | None:
    for ext in (".jpg", ".png"):
        path = SCREENSHOTS_DIR / f"{content_id}_{index}{ext}"
        if path.exists():
            return path
    return None


def save_screenshot(
    content_id: str,
    index: int,
    data: bytes,
    ext: str = ".jpg"
) -> Path:
    path = SCREENSHOTS_DIR / f"{content_id}_{index}{ext}"
    path.write_bytes(data)
    return path


# ------------------------------------------------------------------ #
#  Extraction icon0.png depuis le PKG                                 #
# ------------------------------------------------------------------ #

def extract_icon0(pkg_path: str | Path) -> bytes | None:
    """
    Extrait icon0.png depuis le fichier PKG.
    Utilise la détection par signature PNG.
    """
    try:
        from core.pkg_reader import extract_icon0_png
        data = Path(pkg_path).read_bytes()
        return extract_icon0_png(data)
    except OSError:
        return None


# ------------------------------------------------------------------ #
#  PS Store                                                            #
# ------------------------------------------------------------------ #

def fetch_psstore_cover(content_id: str) -> bytes | None:
    """
    Télécharge la jaquette depuis le PS Store.
    Utilise le Content-ID complet pour une meilleure précision.
    """
    if not content_id or content_id == "UNKNOWN":
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    # Régions prioritaires selon le code du Content-ID
    region_code = content_id[:2].upper()
    priority = {
        "EP": [("FR", "fr"), ("GB", "en"), ("DE", "de"), ("IT", "it"), ("ES", "es")],
        "UP": [("US", "en")],
        "JP": [("JP", "ja")],
        "HB": [("HK", "zh"), ("US", "en")],
        "HP": [("HK", "zh"), ("US", "en")],
        "NP": [("US", "en")],
        "KP": [("KR", "ko")],
    }
    regions = priority.get(region_code, [
        ("FR", "fr"), ("US", "en"), ("GB", "en")
    ])

    for country, lang in regions:
        url = (
            f"https://store.playstation.com/store/api/chihiro/00_09_000/"
            f"container/{country}/{lang}/999/{content_id}/image?w=400&h=533"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200 and len(resp.content) > 5000:
                return resp.content
        except requests.RequestException:
            continue

    return None


# ------------------------------------------------------------------ #
#  Thread de chargement asynchrone                                    #
# ------------------------------------------------------------------ #

class CoverLoaderThread(QThread):
    """
    Charge les jaquettes en arrière-plan.
    Flow : cache → icon0.png → PS Store

    Signaux :
        cover_ready(content_id, cover_path)
        progress(current, total)
        finished_all()
    """

    cover_ready  = pyqtSignal(str, str)
    progress     = pyqtSignal(int, int)
    finished_all = pyqtSignal()

    def __init__(self, packages: list[dict], parent=None):
        super().__init__(parent)
        self._packages = packages
        self._running  = True

    def run(self):
        total = len(self._packages)

        for i, pkg in enumerate(self._packages):
            if not self._running:
                break

            self.progress.emit(i + 1, total)

            content_id = pkg.get("content_id", "")
            filepath   = pkg.get("filepath", "")
            pkg_type   = pkg.get("type", "game")

            if not content_id or content_id == "UNKNOWN":
                continue

            cover_path = None

            # 1. Cache disque
            cached = get_cached_cover(content_id)
            if cached:
                cover_path = str(cached)

            # 2. icon0.png depuis le PKG
            if not cover_path and filepath:
                icon_bytes = extract_icon0(filepath)
                if icon_bytes:
                    saved      = save_cover(content_id, icon_bytes, ".png")
                    cover_path = str(saved)

            # 3. PS Store (uniquement jeux et backports)
            if not cover_path and pkg_type in ("game", "backport"):
                store_bytes = fetch_psstore_cover(content_id)
                if store_bytes:
                    saved      = save_cover(content_id, store_bytes, ".jpg")
                    cover_path = str(saved)

            if cover_path:
                self.cover_ready.emit(content_id, cover_path)

        self.finished_all.emit()

    def stop(self):
        self._running = False