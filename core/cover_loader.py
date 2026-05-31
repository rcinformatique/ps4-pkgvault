import struct
import requests
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QByteArray


COVERS_DIR      = Path("cache/covers")
SCREENSHOTS_DIR = Path("cache/screenshots")
COVERS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------ #
#  Extraction icon0.png depuis le PKG                                 #
# ------------------------------------------------------------------ #

def extract_icon0(pkg_path: str | Path) -> bytes | None:
    """
    Extrait icon0.png depuis le fichier PKG.
    Entry ID 0x1200 = icon0.png
    Retourne les bytes de l'image ou None.
    """
    try:
        pkg_path = Path(pkg_path)
        with open(pkg_path, "rb") as f:

            # Vérifie le magic
            magic = struct.unpack(">I", f.read(4))[0]
            if magic != 0x7F434E54:
                return None

            # entry_count à 0x10
            f.seek(0x10)
            entry_count = struct.unpack(">H", f.read(2))[0]

            # table_offset à 0x18
            f.seek(0x18)
            table_offset = struct.unpack(">I", f.read(4))[0]

            for i in range(entry_count):
                entry_base = table_offset + i * 32
                f.seek(entry_base)
                entry_id = struct.unpack(">I", f.read(4))[0]
                f.read(12)
                data_off  = struct.unpack(">I", f.read(4))[0]
                data_size = struct.unpack(">I", f.read(4))[0]

                # 0x1200 = icon0.png
                if entry_id == 0x1200 and data_size > 0:
                    f.seek(data_off)
                    return f.read(data_size)

    except (OSError, struct.error):
        pass

    return None


# ------------------------------------------------------------------ #
#  Cache disque                                                        #
# ------------------------------------------------------------------ #

def get_cached_cover(content_id: str) -> Path | None:
    """Retourne le chemin du cache si la jaquette existe."""
    for ext in (".jpg", ".png", ".webp"):
        path = COVERS_DIR / f"{content_id}{ext}"
        if path.exists():
            return path
    return None


def save_cover(content_id: str, data: bytes, ext: str = ".jpg") -> Path:
    """Sauvegarde une jaquette dans le cache."""
    path = COVERS_DIR / f"{content_id}{ext}"
    path.write_bytes(data)
    return path


def get_cached_screenshot(content_id: str, index: int) -> Path | None:
    """Retourne le chemin d'un screenshot en cache."""
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
    """Sauvegarde un screenshot dans le cache."""
    path = SCREENSHOTS_DIR / f"{content_id}_{index}{ext}"
    path.write_bytes(data)
    return path


# ------------------------------------------------------------------ #
#  Téléchargement PS Store                                            #
# ------------------------------------------------------------------ #

def fetch_psstore_cover(content_id: str) -> bytes | None:
    """
    Télécharge la jaquette depuis le PS Store.
    Retourne les bytes ou None.
    """
    urls = [
        f"https://store.playstation.com/store/api/chihiro/00_09_000/"
        f"container/FR/fr/999/{content_id}/image?w=400&h=533",
        f"https://store.playstation.com/store/api/chihiro/00_09_000/"
        f"container/US/en/999/{content_id}/image?w=400&h=533",
    ]

    for url in urls:
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200 and len(resp.content) > 5000:
                return resp.content
        except requests.RequestException:
            continue

    return None


# ------------------------------------------------------------------ #
#  Conversion bytes → QPixmap                                         #
# ------------------------------------------------------------------ #

def bytes_to_pixmap(data: bytes) -> QPixmap | None:
    """Convertit des bytes image en QPixmap."""
    if not data:
        return None
    ba  = QByteArray(data)
    img = QImage.fromData(ba)
    if img.isNull():
        return None
    return QPixmap.fromImage(img)


def path_to_pixmap(path: str | Path) -> QPixmap | None:
    """Charge un QPixmap depuis un chemin fichier."""
    path = Path(path)
    if not path.exists():
        return None
    pixmap = QPixmap(str(path))
    return pixmap if not pixmap.isNull() else None


# ------------------------------------------------------------------ #
#  Thread de chargement asynchrone                                    #
# ------------------------------------------------------------------ #

class CoverLoaderThread(QThread):
    """
    Charge les jaquettes en arrière-plan.

    Signaux :
        cover_ready(content_id, cover_path)  → jaquette disponible
        progress(current, total)             → avancement
        finished_all()                       → tout terminé
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

            # 1. Cache disque existant
            cached = get_cached_cover(content_id)
            if cached:
                cover_path = str(cached)

            # 2. Extraction icon0.png depuis le PKG
            if not cover_path and filepath:
                icon_bytes = extract_icon0(filepath)
                if icon_bytes:
                    saved      = save_cover(content_id, icon_bytes, ".png")
                    cover_path = str(saved)

            # 3. PS Store (uniquement pour les jeux BASE)
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