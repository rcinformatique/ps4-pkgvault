import os
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox, QInputDialog, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QSize, QObject, pyqtSlot, QUrl
from ui.template_engine import TemplateEngine


SAMPLE_PACKAGES = [
    {
        "title":      "Spider-Man Miles Morales",
        "type":       "game",
        "content_id": "EP9000-CUSA24030_00-SPIDERMANMM00001",
        "size_bytes": 45_432_123_456,
        "size_str":   "42.3 Go",
        "firmware":   "9.00",
        "region":     "Europe",
        "filepath":   "F:/PS4/Spider-Man.pkg",
        "filename":   "Spider-Man.pkg",
        "screenshots": [],
        "languages":  ["Français", "Anglais", "Espagnol", "Allemand"],
    },
    {
        "title":      "Spider-Man MM — Update v1.16",
        "type":       "update",
        "content_id": "EP9000-CUSA24030_00-SPIDERMANMMUPD01",
        "size_bytes": 2_200_000_000,
        "size_str":   "2.1 Go",
        "firmware":   None,
        "region":     "Europe",
        "filepath":   "F:/PS4/Spider-Man_Update.pkg",
        "filename":   "Spider-Man_Update.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "Spider-Man MM — DLC Suits",
        "type":       "dlc",
        "content_id": "EP9000-CUSA24030_00-SPIDERMANMMDLC01",
        "size_bytes": 860_000_000,
        "size_str":   "0.8 Go",
        "firmware":   None,
        "region":     "Europe",
        "filepath":   "F:/PS4/Spider-Man_DLC.pkg",
        "filename":   "Spider-Man_DLC.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "God of War Ragnarök",
        "type":       "game",
        "content_id": "EP9000-CUSA34674_00-GOWR000000000001",
        "size_bytes": 96_821_145_600,
        "size_str":   "90.1 Go",
        "firmware":   "11.00",
        "region":     "Europe",
        "filepath":   "F:/PS4/GoW.pkg",
        "filename":   "GoW.pkg",
        "screenshots": [],
        "languages":  ["Français", "Anglais", "Espagnol"],
    },
    {
        "title":      "God of War Ragnarök — Update v2.0",
        "type":       "update",
        "content_id": "EP9000-CUSA34674_00-GOWRUPDATE00001",
        "size_bytes": 4_500_000_000,
        "size_str":   "4.2 Go",
        "firmware":   None,
        "region":     "Europe",
        "filepath":   "F:/PS4/GoW_Update.pkg",
        "filename":   "GoW_Update.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "The Last of Us Part II",
        "type":       "game",
        "content_id": "EP9000-CUSA07820_00-THELASTOFUS2001",
        "size_bytes": 82_063_114_240,
        "size_str":   "76.4 Go",
        "firmware":   "7.55",
        "region":     "Europe",
        "filepath":   "F:/PS4/TLOU2.pkg",
        "filename":   "TLOU2.pkg",
        "screenshots": [],
        "languages":  ["Français", "Anglais"],
    },
    {
        "title":      "Ghost of Tsushima — Iki Island",
        "type":       "dlc",
        "content_id": "EP9000-CUSA15398_00-GOTDLC000000001",
        "size_bytes": 8_700_000_000,
        "size_str":   "8.1 Go",
        "firmware":   None,
        "region":     "Europe",
        "filepath":   "F:/PS4/GoT_DLC.pkg",
        "filename":   "GoT_DLC.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "Cyberpunk 2077 — Phantom Liberty",
        "type":       "dlc",
        "content_id": "EP9000-CUSA18534_00-CP77DLC00000001",
        "size_bytes": 19_537_895_424,
        "size_str":   "18.2 Go",
        "firmware":   None,
        "region":     "Europe",
        "filepath":   "F:/PS4/CP77_DLC.pkg",
        "filename":   "CP77_DLC.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "Elden Ring — Update v1.10",
        "type":       "update",
        "content_id": "EP9000-CUSA28842_00-ELDENRING000001",
        "size_bytes": 3_435_973_836,
        "size_str":   "3.2 Go",
        "firmware":   None,
        "region":     "Europe",
        "filepath":   "F:/PS4/EldenRing_Update.pkg",
        "filename":   "EldenRing_Update.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "Bloodborne",
        "type":       "backport",
        "content_id": "EP9000-CUSE01264_00-BLOODBORNE00001",
        "size_bytes": 24_268_374_016,
        "size_str":   "22.6 Go",
        "firmware":   "9.00",
        "region":     "Europe",
        "filepath":   "F:/PS4/Bloodborne_BP.pkg",
        "filename":   "Bloodborne_BP.pkg",
        "screenshots": [],
        "languages":  [],
    },
    {
        "title":      "Sekiro: Shadows Die Twice",
        "type":       "backport",
        "content_id": "EP9000-CUSA13610_00-SEKIRO0000000001",
        "size_bytes": 15_032_385_536,
        "size_str":   "14.0 Go",
        "firmware":   "9.00",
        "region":     "Europe",
        "filepath":   "F:/PS4/Sekiro_BP.pkg",
        "filename":   "Sekiro_BP.pkg",
        "screenshots": [],
        "languages":  [],
    },
]

SAMPLE_FOLDERS = [
    {"path": "F:/PS4 JailBreak/Games", "total": 6, "game": 3, "dlc": 1, "update": 1, "backport": 1, "size_str": "261 Go", "date_added": "2026-05-31"},
    {"path": "E:/Backups/PKG",         "total": 2, "game": 0, "dlc": 1, "update": 0, "backport": 1, "size_str": "36 Go",  "date_added": "2026-05-31"},
]


def _compute_stats(packages: list[dict]) -> dict:
    counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
    total_bytes = 0
    for pkg in packages:
        t = pkg.get("type", "game")
        if t in counts:
            counts[t] += 1
        total_bytes += pkg.get("size_bytes", 0)
    if total_bytes >= 1_073_741_824:
        size_str = f"{total_bytes / 1_073_741_824:.1f} Go"
        total_go = f"{total_bytes / 1_073_741_824:.0f}"
    else:
        size_str = f"{total_bytes / 1_048_576:.0f} Mo"
        total_go = "0"
    return {**counts, "total_size": size_str, "total_go": total_go}


class PyBridge(QObject):
    """Pont Python ↔ JavaScript."""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._win = window

    # Navigation
    @pyqtSlot(str)
    def navigate(self, page: str):
        self._win.navigate(page)

    # Recherche / filtres
    @pyqtSlot(str)
    def search(self, text: str):
        self._win.on_search(text)

    @pyqtSlot(str)
    def set_filter(self, key: str):
        self._win.on_filter(key)

    @pyqtSlot(str)
    def set_sort(self, key: str):
        self._win.on_sort(key)

    # Cartes
    @pyqtSlot(str)
    def card_clicked(self, filepath: str):
        self._win.on_card_clicked(filepath)

    # Actions fichiers
    @pyqtSlot(str)
    def open_folder(self, filepath: str):
        if filepath:
            folder = os.path.dirname(filepath)
            subprocess.Popen(f'explorer "{folder}"')

    @pyqtSlot(str)
    def copy_path(self, filepath: str):
        if filepath:
            QApplication.clipboard().setText(filepath)

    @pyqtSlot(str)
    def copy_cid(self, cid: str):
        if cid:
            QApplication.clipboard().setText(cid)

    @pyqtSlot(str)
    def rename_file(self, filepath: str):
        self._win.on_rename(filepath)

    @pyqtSlot(str)
    def delete_file(self, filepath: str):
        self._win.on_delete(filepath)

    # Dossiers
    @pyqtSlot()
    def add_folder(self):
        self._win.on_add_folder()

    @pyqtSlot(str)
    def rescan_folder(self, path: str):
        print(f"Rescan : {path}")

    @pyqtSlot(str)
    def delete_folder(self, path: str):
        self._win.on_delete_folder(path)

    # Paramètres
    @pyqtSlot(str)
    def save_settings(self, json_str: str):
        try:
            data = json.loads(json_str)
            print(f"Paramètres sauvegardés : {data}")
        except json.JSONDecodeError:
            pass

    @pyqtSlot(str)
    def test_rawg(self, key: str):
        print(f"Test RAWG : {key[:8]}…")

    @pyqtSlot()
    def clear_cache(self):
        print("Vider le cache")

    @pyqtSlot()
    def reset_db(self):
        print("Réinitialiser la BDD")

    @pyqtSlot()
    def toggle_view(self):
        print("Toggle vue")

    # Détail
    @pyqtSlot(str)
    def open_related(self, content_id: str):
        self._win.on_open_related(content_id)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._engine       = TemplateEngine()
        self._packages     = list(SAMPLE_PACKAGES)
        self._folders      = list(SAMPLE_FOLDERS)
        self._settings     = {}
        self._active_page  = "library"
        self._active_filter = "game"
        self._active_sort  = "title"
        self._search_text  = ""
        self._status_msg   = "8 PKG chargés"

        self._init_window()
        self._init_ui()
        self._show_library()

    def _init_window(self):
        self.setWindowTitle("PS4 PKGVault")
        self.setMinimumSize(QSize(900, 580))
        self.resize(1200, 720)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # WebEngine
        self._web = QWebEngineView()

        # WebChannel
        self._bridge  = PyBridge(self)
        self._channel = QWebChannel()
        self._channel.registerObject("pybridge", self._bridge)
        self._web.page().setWebChannel(self._channel)

        layout.addWidget(self._web)

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def navigate(self, page: str):
        self._active_page = page
        if page == "library":
            self._show_library()
        elif page == "folders":
            self._show_folders()
        elif page == "settings":
            self._show_settings()
        elif page == "credits":
            self._show_credits()
        elif page == "detail":
            pass  # géré par on_card_clicked

    def _load_html(self, html: str):
        """Charge le HTML dans le WebEngine."""
        html = self._inject_webchannel(html)
        self._web.setHtml(html, QUrl("file:///"))

    def _inject_webchannel(self, html: str) -> str:
        script = """
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.pybridge = channel.objects.pybridge;
        });
        </script>
        """
        return html.replace("</head>", script + "</head>", 1)

    def _get_stats(self) -> dict:
        return _compute_stats(self._packages)

    def _get_filtered_packages(self) -> list[dict]:
        pkgs = self._packages.copy()
        if self._active_filter != "all":
            pkgs = [p for p in pkgs if p.get("type") == self._active_filter]
        if self._search_text:
            q = self._search_text.lower()
            pkgs = [
                p for p in pkgs
                if q in p.get("title", "").lower()
                or q in p.get("content_id", "").lower()
            ]
        def sort_key(p):
            if self._active_sort == "title":
                return p.get("title", "").lower()
            if self._active_sort == "size":
                return p.get("size_bytes", 0)
            if self._active_sort == "type":
                return p.get("type", "")
            return p.get("date_added", "")
        pkgs.sort(key=sort_key)
        return pkgs

    # ------------------------------------------------------------------ #
    #  Pages                                                               #
    # ------------------------------------------------------------------ #

    def _show_library(self):
        pkgs  = self._get_filtered_packages()
        stats = self._get_stats()
        html  = self._engine.render_library(
            packages      = pkgs,
            stats         = stats,
            active_filter = self._active_filter,
            active_sort   = self._active_sort,
            last_scan     = "il y a 2 minutes",
            active_folder = "F:/PS4 JailBreak/Games",
            status_msg    = self._status_msg,
        )
        self._load_html(html)

    def _show_folders(self):
        html = self._engine.render_folders(
            folders    = self._folders,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html)

    def _show_settings(self):
        html = self._engine.render_settings(
            settings   = self._settings,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html)

    def _show_credits(self):
        html = self._engine.render_credits(
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html)

    def _show_detail(self, pkg_data: dict):
        """Affiche le détail d'un jeu avec son contenu associé."""

        base_cid = pkg_data.get("content_id", "")

        # Extrait le CUSA du content_id
        # Format : EP9000-CUSA24030_00-XXXXX
        # On cherche le CUSA dans tous les packages
        cusa = ""
        for part in base_cid.replace("-", "_").split("_"):
            if part.startswith("CUSA") or part.startswith("CUSE"):
                cusa = part
                break

        # Trouve les contenus liés par CUSA identique
        if cusa:
            related = [
                p for p in self._packages
                if p.get("filepath") != pkg_data.get("filepath")
                   and cusa in p.get("content_id", "")
            ]
        else:
            related = []

        html = self._engine.render_detail(
            pkg_data=pkg_data,
            related=related,
            stats=self._get_stats(),
            status_msg=self._status_msg,
        )
        self._load_html(html)

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    def on_card_clicked(self, filepath: str):
        pkg = next(
            (p for p in self._packages if p.get("filepath") == filepath),
            None
        )
        if pkg:
            self._show_detail(pkg)

    def on_search(self, text: str):
        self._search_text = text
        self._show_library()

    def on_filter(self, key: str):
        self._active_filter = key
        self._show_library()

    def on_sort(self, key: str):
        self._active_sort = key
        self._show_library()

    def on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionner un dossier PKG", "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            print(f"Dossier ajouté : {folder}")

    def on_delete_folder(self, path: str):
        reply = QMessageBox.question(
            self, "Retirer le dossier",
            f"Retirer ce dossier de la bibliothèque ?\n\n{path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._folders = [f for f in self._folders if f["path"] != path]
            self._show_folders()

    def on_rename(self, filepath: str):
        old_name = os.path.basename(filepath)
        new_name, ok = QInputDialog.getText(
            self, "Renommer", "Nouveau nom :", text=old_name
        )
        if ok and new_name.strip() and new_name != old_name:
            print(f"Renommer : {filepath} → {new_name}")

    def on_delete(self, filepath: str):
        reply = QMessageBox.warning(
            self, "Supprimer",
            f"Supprimer définitivement ?\n\n{os.path.basename(filepath)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._packages = [
                p for p in self._packages
                if p.get("filepath") != filepath
            ]
            self._show_library()

    def on_open_related(self, content_id: str):
        pkg = next(
            (p for p in self._packages if p.get("content_id") == content_id),
            None
        )
        if pkg:
            self._show_detail(pkg)