import struct
import requests
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal


COVERS_DIR      = Path("cache/covers").resolve()
SCREENSHOTS_DIR = Path("cache/screenshots").resolve()
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
    Lit uniquement les premiers Mo pour trouver le PNG.
    """
    try:
        path = Path(pkg_path)
        with open(path, "rb") as f:
            # Lit par chunks jusqu'à trouver le PNG
            chunk_size = 1024 * 1024  # 1 Mo
            buffer     = b""
            for _ in range(20):  # max 20 Mo
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                buffer += chunk
                idx = buffer.find(b"\x89PNG\r\n\x1a\n")
                if idx != -1:
                    # Trouve la fin du PNG
                    end = buffer.find(b"IEND", idx)
                    if end != -1:
                        return buffer[idx:end + 8]
                    # Lit encore pour avoir la fin
                    extra = f.read(chunk_size)
                    buffer += extra
                    end = buffer.find(b"IEND", idx)
                    if end != -1:
                        return buffer[idx:end + 8]
                    break
    except OSError:
        pass
    return None


# ------------------------------------------------------------------ #
#  Thread de chargement asynchrone                                    #
# ------------------------------------------------------------------ #

class CoverLoaderThread(QThread):
    """
    Charge les jaquettes en arrière-plan.
    Flow : cache disque → icon0.png extrait du PKG

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

            if not content_id or content_id == "UNKNOWN":
                continue

            cover_path = None

            # 1. Cache disque — ne retélécharge pas si déjà présent
            cached = get_cached_cover(content_id)
            if cached:
                cover_path = str(cached.resolve())

            # 2. icon0.png depuis le PKG
            if not cover_path and filepath and Path(filepath).exists():
                icon_bytes = extract_icon0(filepath)
                if icon_bytes:
                    saved      = save_cover(content_id, icon_bytes, ".png")
                    cover_path = str(saved.resolve())

            if cover_path:
                self.cover_ready.emit(content_id, cover_path)

        self.finished_all.emit()

    def stop(self):
        self._running = False