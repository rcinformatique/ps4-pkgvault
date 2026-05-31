import os
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox, QInputDialog, QApplication
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QSize, QObject, pyqtSlot, QUrl
from ui.template_engine import TemplateEngine


SAMPLE_PACKAGES = [
    {
        "title":        "Spider-Man Miles Morales",
        "title_api":    "Marvel's Spider-Man: Miles Morales",
        "type":         "game",
        "content_id":   "EP9000-CUSA24030_00-SPIDERMANMM00001",
        "size_bytes":   45_432_123_456,
        "size_str":     "42.3 Go",
        "firmware":     "9.00",
        "region":       "Europe",
        "filepath":     "F:/PS4/Spider-Man.pkg",
        "filename":     "Spider-Man.pkg",
        "app_ver":      "01.00",
        "category":     "gd",
        "developer":    "Insomniac Games",
        "publisher":    "Sony Interactive Entertainment",
        "release_date": "12 Novembre 2020",
        "rating":       4.5,
        "genres":       ["Action-Aventure", "Open World", "Super-héros"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Allemand", "Italien"],
        "description":  "Dans Marvel's Spider-Man: Miles Morales, une nouvelle aventure épique prend vie dans les rues enneigées de New York. Lors d'un conflit entre une société d'énergie corrompue et une armée high-tech, Miles doit embrasser son rôle de Spider-Man.\n\nVivez les pouvoirs uniques de Miles, notamment sa bioélectricité et son camouflage, pour combattre des ennemis redoutables.",
        "screenshots":  [],
        "cover_path":   "",
    },
    {
        "title":        "Spider-Man MM — Update v1.16",
        "type":         "update",
        "content_id":   "EP9000-CUSA24030_00-SPIDERMANMMUPD01",
        "size_bytes":   2_200_000_000,
        "size_str":     "2.1 Go",
        "firmware":     None,
        "region":       "Europe",
        "filepath":     "F:/PS4/Spider-Man_Update.pkg",
        "filename":     "Spider-Man_Update.pkg",
        "app_ver":      "01.16",
        "category":     "gp",
        "screenshots":  [],
        "languages":    [],
        "cover_path":   "",
    },
    {
        "title":        "Spider-Man MM — DLC Suits Pack",
        "type":         "dlc",
        "content_id":   "EP9000-CUSA24030_00-SPIDERMANMMDLC01",
        "size_bytes":   860_000_000,
        "size_str":     "0.8 Go",
        "firmware":     None,
        "region":       "Europe",
        "filepath":     "F:/PS4/Spider-Man_DLC.pkg",
        "filename":     "Spider-Man_DLC.pkg",
        "app_ver":      "",
        "category":     "ac",
        "screenshots":  [],
        "languages":    [],
        "cover_path":   "",
    },
    {
        "title":        "God of War Ragnarök",
        "title_api":    "God of War: Ragnarök",
        "type":         "game",
        "content_id":   "EP9000-CUSA34674_00-GOWR000000000001",
        "size_bytes":   96_821_145_600,
        "size_str":     "90.1 Go",
        "firmware":     "11.00",
        "region":       "Europe",
        "filepath":     "F:/PS4/GoW.pkg",
        "filename":     "GoW.pkg",
        "app_ver":      "01.00",
        "category":     "gd",
        "developer":    "Santa Monica Studio",
        "publisher":    "Sony Interactive Entertainment",
        "release_date": "9 Novembre 2022",
        "rating":       4.8,
        "genres":       ["Action-Aventure", "Mythologie nordique", "RPG"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Allemand", "Italien", "Portugais (BR)", "Russe"],
        "description":  "Kratos et Atreus doivent voyager à travers les neuf royaumes pour trouver les réponses nécessaires à la survie du monde contre le Fimbulwinter imminent et le début du Ragnarök.\n\nContinuant l'histoire de God of War (2018), ce nouvel opus offre une aventure épique mêlant mythologie nordique, combats intenses et une relation père-fils au coeur du récit.",
        "screenshots":  [],
        "cover_path":   "",
    },
    {
        "title":        "God of War Ragnarök — Update v2.0",
        "type":         "update",
        "content_id":   "EP9000-CUSA34674_00-GOWRUPDATE00001",
        "size_bytes":   4_500_000_000,
        "size_str":     "4.2 Go",
        "firmware":     None,
        "region":       "Europe",
        "filepath":     "F:/PS4/GoW_Update.pkg",
        "filename":     "GoW_Update.pkg",
        "app_ver":      "02.00",
        "category":     "gp",
        "screenshots":  [],
        "languages":    [],
        "cover_path":   "",
    },
    {
        "title":        "The Last of Us Part II",
        "title_api":    "The Last of Us Part II",
        "type":         "game",
        "content_id":   "EP9000-CUSA07820_00-THELASTOFUS2001",
        "size_bytes":   82_063_114_240,
        "size_str":     "76.4 Go",
        "firmware":     "7.55",
        "region":       "Europe",
        "filepath":     "F:/PS4/TLOU2.pkg",
        "filename":     "TLOU2.pkg",
        "app_ver":      "01.00",
        "category":     "gd",
        "developer":    "Naughty Dog",
        "publisher":    "Sony Interactive Entertainment",
        "release_date": "19 Juin 2020",
        "rating":       4.2,
        "genres":       ["Action-Aventure", "Survival Horror", "Post-apocalyptique"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Allemand", "Italien", "Japonais"],
        "description":  "Cinq ans après leur périlleux voyage à travers les États-Unis post-pandémie, Ellie et Joel se sont installés à Jackson, Wyoming. En vivant parmi une communauté florissante de survivants, ils créent des liens, s'affrontent à des conflits et endurent des souffrances.\n\nWhen a violent event disrupts that peace, Ellie embarks on a relentless journey to carry out justice and find closure.",
        "screenshots":  [],
        "cover_path":   "",
    },
    {
        "title":        "Ghost of Tsushima — Iki Island",
        "title_api":    "Ghost of Tsushima — Iki Island DLC",
        "type":         "dlc",
        "content_id":   "EP9000-CUSA15398_00-GOTDLC000000001",
        "size_bytes":   8_700_000_000,
        "size_str":     "8.1 Go",
        "firmware":     None,
        "region":       "Europe",
        "filepath":     "F:/PS4/GoT_DLC.pkg",
        "filename":     "GoT_DLC.pkg",
        "app_ver":      "",
        "category":     "ac",
        "developer":    "Sucker Punch Productions",
        "publisher":    "Sony Interactive Entertainment",
        "release_date": "16 Août 2021",
        "rating":       4.3,
        "genres":       ["Action-Aventure", "Monde ouvert", "Samouraï"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Japonais"],
        "description":  "Explorez l'île d'Iki dans cette extension majeure de Ghost of Tsushima. Jin Sakai se rend sur cette île mystérieuse pour affronter une nouvelle menace mongole, tout en découvrant des secrets douloureux de son passé.",
        "screenshots":  [],
        "cover_path":   "",
    },
    {
        "title":        "Cyberpunk 2077 — Phantom Liberty",
        "title_api":    "Cyberpunk 2077: Phantom Liberty",
        "type":         "dlc",
        "content_id":   "EP9000-CUSA18534_00-CP77DLC00000001",
        "size_bytes":   19_537_895_424,
        "size_str":     "18.2 Go",
        "firmware":     None,
        "region":       "Europe",
        "filepath":     "F:/PS4/CP77_DLC.pkg",
        "filename":     "CP77_DLC.pkg",
        "app_ver":      "",
        "category":     "ac",
        "developer":    "CD Projekt Red",
        "publisher":    "CD Projekt",
        "release_date": "26 Septembre 2023",
        "rating":       4.4,
        "genres":       ["RPG", "Action", "Cyberpunk", "Open World"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Allemand", "Polonais", "Russe"],
        "description":  "Phantom Liberty est une nouvelle extension spy-thriller pour Cyberpunk 2077. Quand le vaisseau spatial de la présidente des États-Unis Unifiés d'Amérique est abattu au-dessus du district le plus dangereux de Night City, V est engagé pour une mission de sauvetage.",
        "screenshots":  [],
        "cover_path":   "",
    },
    {
        "title":        "Elden Ring — Update v1.10",
        "type":         "update",
        "content_id":   "EP9000-CUSA28842_00-ELDENRING000001",
        "size_bytes":   3_435_973_836,
        "size_str":     "3.2 Go",
        "firmware":     None,
        "region":       "Europe",
        "filepath":     "F:/PS4/EldenRing_Update.pkg",
        "filename":     "EldenRing_Update.pkg",
        "app_ver":      "01.10",
        "category":     "gp",
        "screenshots":  [],
        "languages":    [],
        "cover_path":   "",
    },
    {
        "title":        "Bloodborne",
        "title_api":    "Bloodborne",
        "type":         "backport",
        "content_id":   "EP9000-CUSE01264_00-BLOODBORNE00001",
        "size_bytes":   24_268_374_016,
        "size_str":     "22.6 Go",
        "firmware":     "9.00",
        "region":       "Europe",
        "filepath":     "F:/PS4/Bloodborne_BP.pkg",
        "filename":     "Bloodborne_BP.pkg",
        "app_ver":      "01.09",
        "category":     "gd",
        "developer":    "FromSoftware",
        "publisher":    "Sony Interactive Entertainment",
        "release_date": "24 Mars 2015",
        "rating":       4.7,
        "genres":       ["Action-RPG", "Souls-like", "Horreur gothique"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Allemand", "Japonais"],
        "description":  "Explorez les rues cauchemardesque de Yharnam, une ville antique rongée par une maladie du sang endémique. En tant que chasseur, découvrez ses mystères et combattez ses habitants devenus fous.\n\nBloodborne est un action-RPG intense qui récompense la bravoure et la maîtrise. Ce backport vous permet de jouer sur firmware 9.00.",
        "screenshots":  [],
        "cover_path":   "",
    },
    {
        "title":        "Sekiro: Shadows Die Twice",
        "title_api":    "Sekiro: Shadows Die Twice",
        "type":         "backport",
        "content_id":   "EP9000-CUSA13610_00-SEKIRO0000000001",
        "size_bytes":   15_032_385_536,
        "size_str":     "14.0 Go",
        "firmware":     "9.00",
        "region":       "Europe",
        "filepath":     "F:/PS4/Sekiro_BP.pkg",
        "filename":     "Sekiro_BP.pkg",
        "app_ver":      "01.06",
        "category":     "gd",
        "developer":    "FromSoftware",
        "publisher":    "Activision",
        "release_date": "22 Mars 2019",
        "rating":       4.6,
        "genres":       ["Action-Aventure", "Souls-like", "Japon féodal"],
        "languages":    ["Français", "Anglais (US)", "Espagnol", "Allemand", "Japonais"],
        "description":  "Sekiro: Shadows Die Twice vous plonge dans le Japon féodal du XVIème siècle. Incarnez un shinobi déterminé à venger son seigneur et à briser la malédiction de la mort.\n\nMaîtrisez l'art du combat au katana, utilisez vos outils de shinobi et explorez un monde magnifique et brutal. Ce backport vous permet de profiter du jeu sur firmware 9.00.",
        "screenshots":  [],
        "cover_path":   "",
    },
]

SAMPLE_FOLDERS = [
    {
        "path":       "F:/PS4 JailBreak/Games",
        "total":      8,
        "game":       3,
        "dlc":        2,
        "update":     2,
        "backport":   2,
        "size_str":   "261 Go",
        "date_added": "2026-05-31",
    },
    {
        "path":       "E:/Backups/PKG",
        "total":      3,
        "game":       0,
        "dlc":        1,
        "update":     1,
        "backport":   0,
        "size_str":   "36 Go",
        "date_added": "2026-05-31",
    },
]


def _compute_stats(packages: list[dict]) -> dict:
    counts      = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
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

    @pyqtSlot(str)
    def navigate(self, page: str):
        self._win.navigate(page)

    @pyqtSlot()
    def go_back(self):
        self._win.go_back()

    @pyqtSlot(str)
    def search(self, text: str):
        self._win.on_search(text)

    @pyqtSlot(str)
    def set_filter(self, key: str):
        self._win.on_filter(key)

    @pyqtSlot(str)
    def set_sort(self, key: str):
        self._win.on_sort(key)

    @pyqtSlot(str)
    def card_clicked(self, filepath: str):
        self._win.on_card_clicked(filepath)

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

    @pyqtSlot()
    def add_folder(self):
        self._win.on_add_folder()

    @pyqtSlot(str)
    def rescan_folder(self, path: str):
        print(f"Rescan : {path}")

    @pyqtSlot(str)
    def delete_folder(self, path: str):
        self._win.on_delete_folder(path)

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

    @pyqtSlot(str)
    def open_related(self, content_id: str):
        self._win.on_open_related(content_id)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._engine        = TemplateEngine()
        self._packages      = list(SAMPLE_PACKAGES)
        self._folders       = list(SAMPLE_FOLDERS)
        self._settings      = {}
        self._active_page   = "library"
        self._previous_page = "library"
        self._active_filter = "game"
        self._active_sort   = "title"
        self._search_text   = ""
        self._status_msg    = "11 PKG chargés"

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

        self._web     = QWebEngineView()
        self._bridge  = PyBridge(self)
        self._channel = QWebChannel()
        self._channel.registerObject("pybridge", self._bridge)
        self._web.page().setWebChannel(self._channel)

        layout.addWidget(self._web)

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def navigate(self, page: str):
        if page != self._active_page:
            self._previous_page = self._active_page
        self._active_page = page
        if page == "library":
            self._show_library()
        elif page == "folders":
            self._show_folders()
        elif page == "settings":
            self._show_settings()
        elif page == "credits":
            self._show_credits()

    def go_back(self):
        self.navigate(self._previous_page)

    def _load_html(self, html: str, show_back: bool = False):
        html = self._inject_webchannel(html)
        self._web.setHtml(html, QUrl("file:///"))
        if show_back:
            try:
                self._web.loadFinished.disconnect(self._on_detail_loaded)
            except Exception:
                pass
            self._web.loadFinished.connect(self._on_detail_loaded)

    def _on_detail_loaded(self, ok: bool):
        try:
            self._web.loadFinished.disconnect(self._on_detail_loaded)
        except Exception:
            pass
        self._web.page().runJavaScript("showBackBtn(true);")

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

    # ------------------------------------------------------------------ #
    #  Stats & filtres                                                     #
    # ------------------------------------------------------------------ #

    def _get_stats(self) -> dict:
        return _compute_stats(self._packages)

    def _get_filtered_packages(self) -> list[dict]:
        pkgs = self._packages.copy()

        if self._active_filter != "all":
            pkgs = [
                p for p in pkgs
                if p.get("type") == self._active_filter
            ]

        if self._search_text:
            q = self._search_text.lower()
            pkgs = [
                p for p in pkgs
                if q in p.get("title", "").lower()
                or q in p.get("title_api", "").lower()
                or q in p.get("content_id", "").lower()
            ]

        def sort_key(p):
            if self._active_sort == "title":
                return (
                    p.get("title_api") or p.get("title") or ""
                ).lower()
            if self._active_sort == "size":
                return p.get("size_bytes", 0)
            if self._active_sort == "type":
                return p.get("type", "")
            return p.get("date_added", "")

        pkgs.sort(key=sort_key)
        return pkgs

    def _extract_cusa(self, content_id: str) -> str:
        """Extrait le CUSA/CUSE depuis un content_id."""
        for part in content_id.replace("-", "_").split("_"):
            if part.startswith("CUSA") or part.startswith("CUSE"):
                return part
        return ""

    # ------------------------------------------------------------------ #
    #  Pages                                                               #
    # ------------------------------------------------------------------ #

    def _show_library(self):
        pkgs  = self._get_filtered_packages()
        stats = self._get_stats()
        total = len(pkgs)
        size  = stats.get("total_size", "0 Go")
        count_str = f"{total} fichier{'s' if total > 1 else ''} · {size}"

        html = self._engine.render_library(
            packages      = pkgs,
            stats         = stats,
            active_filter = self._active_filter,
            active_sort   = self._active_sort,
            status_msg    = self._status_msg,
            count_str     = count_str,
        )
        self._load_html(html, show_back=False)

    def _show_folders(self):
        html = self._engine.render_folders(
            folders    = self._folders,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html, show_back=False)

    def _show_settings(self):
        html = self._engine.render_settings(
            settings   = self._settings,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html, show_back=False)

    def _show_credits(self):
        html = self._engine.render_credits(
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html, show_back=False)

    def _show_detail(self, pkg_data: dict):
        """Affiche le détail avec les contenus associés."""
        cusa = self._extract_cusa(pkg_data.get("content_id", ""))

        if cusa:
            related = [
                p for p in self._packages
                if p.get("filepath") != pkg_data.get("filepath")
                and cusa in p.get("content_id", "")
            ]
        else:
            related = []

        html = self._engine.render_detail(
            pkg_data   = pkg_data,
            related    = related,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html, show_back=True)

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    def on_card_clicked(self, filepath: str):
        pkg = next(
            (p for p in self._packages
             if p.get("filepath") == filepath),
            None
        )
        if pkg:
            self._previous_page = "library"
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
            self,
            "Sélectionner un dossier PKG",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            print(f"Dossier ajouté : {folder}")

    def on_delete_folder(self, path: str):
        reply = QMessageBox.question(
            self,
            "Retirer le dossier",
            f"Retirer ce dossier de la bibliothèque ?\n\n{path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._folders = [
                f for f in self._folders
                if f["path"] != path
            ]
            self._show_folders()

    def on_rename(self, filepath: str):
        old_name = os.path.basename(filepath)
        new_name, ok = QInputDialog.getText(
            self,
            "Renommer le fichier",
            "Nouveau nom :",
            text=old_name
        )
        if ok and new_name.strip() and new_name != old_name:
            if not new_name.lower().endswith(".pkg"):
                new_name += ".pkg"
            print(f"Renommer : {filepath} → {new_name}")

    def on_delete(self, filepath: str):
        reply = QMessageBox.warning(
            self,
            "Supprimer le fichier",
            f"Supprimer définitivement ?\n\n"
            f"{os.path.basename(filepath)}\n\n"
            f"Cette action est irréversible.",
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
            (p for p in self._packages
             if p.get("content_id") == content_id),
            None
        )
        if pkg:
            self._show_detail(pkg)

    def closeEvent(self, event):
        event.accept()