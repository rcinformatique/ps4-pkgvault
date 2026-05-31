from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtCore import QSize
from ui.theme import Colors
from ui.topbar import Topbar
from ui.subbar import Subbar
from ui.widgets.status_bar import StatusBar
from ui.pages.library_page import LibraryPage
from ui.pages.detail_page import DetailPage
from ui.pages.folders_page import FoldersPage
from ui.pages.settings_page import SettingsPage


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
    },
]

SAMPLE_FOLDERS = {
    "F:/PS4 JailBreak/Games": {
        "game": 3, "dlc": 2, "update": 1,
        "backport": 2, "total": 8,
        "size_str": "297 Go",
        "date_added": "2026-05-31"
    },
    "E:/Backups/PKG": {
        "game": 1, "dlc": 0, "update": 0,
        "backport": 1, "total": 2,
        "size_str": "36 Go",
        "date_added": "2026-05-31"
    },
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_ui()
        self._load_sample_data()

    def _init_window(self):
        self.setWindowTitle("PS4 PKGVault")
        self.setMinimumSize(QSize(900, 580))
        self.resize(1200, 720)

    def _init_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {Colors.BG_APP};")
        self.setCentralWidget(central)

        self._layout = QVBoxLayout(central)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Topbar
        self.topbar = Topbar()
        self.topbar.tab_changed.connect(self._on_tab_changed)
        self.topbar.add_requested.connect(self._on_add_folder)
        self.topbar.search_changed.connect(self._on_search)
        self.topbar.view_toggled.connect(self._on_view_toggle)
        self._layout.addWidget(self.topbar)

        # Subbar
        self.subbar = Subbar()
        self.subbar.filter_changed.connect(self._on_filter_changed)
        self.subbar.sort_changed.connect(self._on_sort_changed)
        self._layout.addWidget(self.subbar)

        # Stack de pages
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {Colors.BG_APP};")
        self._layout.addWidget(self._stack)

        # Library page
        self.library_page = LibraryPage()
        self.library_page.pkg_selected.connect(self._on_pkg_selected)
        self.library_page.pkg_deleted.connect(self._on_pkg_deleted)
        self.library_page.stats_updated.connect(self._on_stats_updated)
        self._stack.addWidget(self.library_page)

        # Detail page
        self.detail_page = DetailPage()
        self.detail_page.back_requested.connect(self._on_detail_back)
        self.detail_page.relation_clicked.connect(self._on_pkg_selected)
        self._stack.addWidget(self.detail_page)

        # Folders page
        self.folders_page = FoldersPage()
        self.folders_page.add_requested.connect(self._on_add_folder)
        self.folders_page.scan_requested.connect(self._on_rescan_folder)
        self.folders_page.delete_requested.connect(self._on_delete_folder)
        self._stack.addWidget(self.folders_page)

        # Settings page
        self.settings_page = SettingsPage()
        self.settings_page.settings_saved.connect(self._on_settings_saved)
        self.settings_page.cache_clear_requested.connect(
            self._on_cache_clear
        )
        self.settings_page.db_reset_requested.connect(
            self._on_db_reset
        )
        self._stack.addWidget(self.settings_page)

        # StatusBar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.set_ready()

    def _load_sample_data(self):
        """Charge les données de test."""
        self.library_page.load_packages(SAMPLE_PACKAGES)
        self.status_bar.update_stats(SAMPLE_PACKAGES)
        self.subbar.update_count(
            len(SAMPLE_PACKAGES),
            self.library_page.get_total_size_str()
        )
        self.status_bar.set_message(
            f"{len(SAMPLE_PACKAGES)} PKG chargés", "ok"
        )
        self.folders_page.set_folders(
            list(SAMPLE_FOLDERS.keys()),
            SAMPLE_FOLDERS
        )

    # ------------------------------------------------------------------ #
    #  Navigation                                                          #
    # ------------------------------------------------------------------ #

    def _on_tab_changed(self, key: str):
        self.subbar.setVisible(key == "library")
        if key == "library":
            self._stack.setCurrentWidget(self.library_page)
        elif key == "folders":
            self._stack.setCurrentWidget(self.folders_page)
        elif key == "settings":
            self._stack.setCurrentWidget(self.settings_page)
        elif key == "credits":
            print("Credits — à venir")

    def _on_settings_saved(self, data: dict):
        print(f"Paramètres sauvegardés : {data}")
        self.status_bar.set_message(
            "Paramètres sauvegardés", "ok"
        )

    def _on_cache_clear(self):
        print("Vider le cache")

    def _on_db_reset(self):
        print("Réinitialiser la BDD")

    def _on_pkg_selected(self, pkg_data: dict):
        """Ouvre la page de détail."""
        self.detail_page.show_pkg(pkg_data, [])
        self._stack.setCurrentWidget(self.detail_page)
        self.subbar.setVisible(False)

    def _on_detail_back(self):
        """Retour à la bibliothèque."""
        self._stack.setCurrentWidget(self.library_page)
        self.subbar.setVisible(True)
        self.topbar.set_active_tab("library")

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    def _on_add_folder(self):
        print("Ajouter un dossier")

    def _on_rescan_folder(self, path: str):
        print(f"Rescan : {path}")

    def _on_delete_folder(self, path: str):
        print(f"Supprimer : {path}")

    def _on_search(self, text: str):
        self.library_page.set_search(text)
        self._update_count()

    def _on_filter_changed(self, key: str):
        self.library_page.set_filter(key)
        self._update_count()

    def _on_sort_changed(self, key: str):
        self.library_page.set_sort(
            key, self.subbar.sort_ascending
        )

    def _on_view_toggle(self):
        print("Toggle vue")

    def _on_pkg_deleted(self, filepath: str):
        self.status_bar.set_message("Fichier supprimé", "warn")
        self._update_count()

    def _on_stats_updated(self, counts: dict):
        self.status_bar.update_counts(counts)

    def _update_count(self):
        self.subbar.update_count(
            self.library_page.get_filtered_count(),
            self.library_page.get_total_size_str()
        )

    # ------------------------------------------------------------------ #
    #  Fermeture                                                           #
    # ------------------------------------------------------------------ #

    def closeEvent(self, event):
        event.accept()