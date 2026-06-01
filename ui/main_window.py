import os
import subprocess
import json
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox, QInputDialog, QApplication
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QSize, QObject, pyqtSlot, QUrl, QThread, pyqtSignal
from ui.template_engine import TemplateEngine
from core.database import Database
from core.scanner import scan_folder
from core.cover_loader import CoverLoaderThread
from core.api_client import ApiWorkerThread


# ------------------------------------------------------------------ #
#  Thread de scan                                                      #
# ------------------------------------------------------------------ #

class ScanThread(QThread):
    scan_done = pyqtSignal(list, list)
    progress  = pyqtSignal(int, int)

    def __init__(self, folders: list[str], db: Database, parent=None):
        super().__init__(parent)
        self._folders = folders
        self._db      = db

    def run(self):
        all_packages = []
        all_errors   = []
        for folder in self._folders:
            pkgs, errors = scan_folder(
                folder,
                db=self._db,
                progress_callback=lambda c, t: self.progress.emit(c, t)
            )
            all_packages.extend(pkgs)
            all_errors.extend(errors)
        self.scan_done.emit(all_packages, all_errors)


# ------------------------------------------------------------------ #
#  PyBridge                                                            #
# ------------------------------------------------------------------ #

class PyBridge(QObject):

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
        self._win.on_rescan_folder(path)

    @pyqtSlot(str)
    def delete_folder(self, path: str):
        self._win.on_delete_folder(path)

    @pyqtSlot(str)
    def save_settings(self, json_str: str):
        self._win.on_save_settings(json_str)

    @pyqtSlot(str)
    def test_rawg(self, key: str):
        self._win.on_test_rawg(key)

    @pyqtSlot()
    def clear_cache(self):
        self._win.on_clear_cache()

    @pyqtSlot()
    def reset_db(self):
        self._win.on_reset_db()

    @pyqtSlot()
    def toggle_view(self):
        self._win.on_toggle_view()

    @pyqtSlot(str)
    def open_related(self, content_id: str):
        self._win.on_open_related(content_id)


# ------------------------------------------------------------------ #
#  MainWindow                                                          #
# ------------------------------------------------------------------ #

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._engine        = TemplateEngine()
        self._db            = Database()
        self._packages      = []
        self._active_page   = "library"
        self._previous_page = "library"
        self._active_filter = "game"
        self._active_sort   = "title"
        self._search_text   = ""
        self._status_msg    = "Prêt"
        self._view_mode     = "grid"
        self._scan_thread   = None
        self._cover_thread  = None
        self._api_thread    = None

        self._init_window()
        self._init_ui()
        self._restore_session()

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
    #  Session                                                             #
    # ------------------------------------------------------------------ #

    def _restore_session(self):
        self._active_filter = self._db.get_setting("active_filter", "game")
        self._view_mode     = self._db.get_setting("view_mode", "grid")

        cached = self._db.get_all_games()
        if cached:
            self._packages   = cached
            self._status_msg = f"{len(cached)} PKG chargés depuis la base de données"

        self._show_library()

        folders = self._db.get_folders()
        if folders:
            self._start_scan(folders)

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
    #  Stats                                                               #
    # ------------------------------------------------------------------ #

    def _get_stats(self) -> dict:
        counts      = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
        total_bytes = 0
        for pkg in self._packages:
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

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes >= 1_073_741_824:
            return f"{size_bytes / 1_073_741_824:.1f} Go"
        if size_bytes >= 1_048_576:
            return f"{size_bytes / 1_048_576:.0f} Mo"
        return f"{size_bytes / 1024:.0f} Ko"

    def _get_filtered_packages(self) -> list[dict]:
        pkgs = self._packages.copy()

        if self._active_filter != "all":
            pkgs = [p for p in pkgs if p.get("type") == self._active_filter]

        if self._search_text:
            q = self._search_text.lower()
            pkgs = [
                p for p in pkgs
                if q in (p.get("title") or "").lower()
                or q in (p.get("title_api") or "").lower()
                or q in (p.get("content_id") or "").lower()
            ]

        def sort_key(p):
            if self._active_sort == "title":
                return (p.get("title_api") or p.get("title") or "").lower()
            if self._active_sort == "size":
                return p.get("size_bytes", 0)
            if self._active_sort == "type":
                return p.get("type", "")
            return p.get("date_added", "")

        pkgs.sort(key=sort_key)
        return pkgs

    def _extract_cusa(self, content_id: str) -> str:
        for part in content_id.replace("-", "_").split("_"):
            if part.startswith("CUSA") or part.startswith("CUSE"):
                return part
        return ""

    # ------------------------------------------------------------------ #
    #  Pages                                                               #
    # ------------------------------------------------------------------ #

    def _show_library(self):
        pkgs           = self._get_filtered_packages()
        stats          = self._get_stats()
        total          = len(pkgs)
        size           = stats.get("total_size", "0 Go")
        count_str      = f"{total} fichier{'s' if total > 1 else ''} · {size}"
        card_min_width = int(self._db.get_setting("card_min_width", "180"))

        html = self._engine.render_library(
            packages       = pkgs,
            stats          = stats,
            active_filter  = self._active_filter,
            active_sort    = self._active_sort,
            status_msg     = self._status_msg,
            count_str      = count_str,
            view_mode      = self._view_mode,
            card_min_width = card_min_width,
        )
        self._load_html(html, show_back=False)

    def _show_folders(self):
        folders = self._db.get_folders_full()
        html = self._engine.render_folders(
            folders    = folders,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html, show_back=False)

    def _show_settings(self):
        settings = self._db.get_all_settings()
        html = self._engine.render_settings(
            settings   = settings,
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
        cusa    = self._extract_cusa(pkg_data.get("content_id", ""))
        related = []
        if cusa:
            related = [
                p for p in self._packages
                if p.get("filepath") != pkg_data.get("filepath")
                and cusa in p.get("content_id", "")
            ]
        html = self._engine.render_detail(
            pkg_data   = pkg_data,
            related    = related,
            stats      = self._get_stats(),
            status_msg = self._status_msg,
        )
        self._load_html(html, show_back=True)

    # ------------------------------------------------------------------ #
    #  Scan                                                                #
    # ------------------------------------------------------------------ #

    def _start_scan(self, folders: list[str]):
        if self._scan_thread and self._scan_thread.isRunning():
            self._scan_thread.quit()
            self._scan_thread.wait()

        self._status_msg = "Scan en cours…"
        self._show_library()

        self._scan_thread = ScanThread(folders, self._db)
        self._scan_thread.scan_done.connect(self._on_scan_done)
        self._scan_thread.start()

    def _on_scan_done(self, packages: list, errors: list):
        self._packages   = self._db.get_all_games()
        count            = len(self._packages)
        self._status_msg = f"{count} PKG chargés"
        if errors:
            self._status_msg += f" · {len(errors)} ignorés"
        self._show_library()
        self._start_cover_loader(self._packages)
        self._start_api_worker()

    # ------------------------------------------------------------------ #
    #  Covers                                                              #
    # ------------------------------------------------------------------ #

    def _start_cover_loader(self, packages: list[dict]):
        if self._cover_thread and self._cover_thread.isRunning():
            self._cover_thread.stop()
            self._cover_thread.wait()
        self._cover_thread = CoverLoaderThread(packages)
        self._cover_thread.cover_ready.connect(self._on_cover_ready)
        self._cover_thread.start()

    def _on_cover_ready(self, content_id: str, cover_path: str):
        self._db.update_cover(content_id, cover_path)
        for pkg in self._packages:
            if pkg.get("content_id") == content_id:
                pkg["cover_path"] = cover_path
                break

    # ------------------------------------------------------------------ #
    #  API Worker                                                          #
    # ------------------------------------------------------------------ #

    def _start_api_worker(self):
        rawg_key       = self._db.get_setting("rawg_api_key", "")
        igdb_client_id = self._db.get_setting("igdb_client_id", "")
        igdb_secret    = self._db.get_setting("igdb_client_secret", "")
        auto_fetch     = self._db.get_setting("auto_fetch", "1")

        if auto_fetch != "1" or not rawg_key:
            return

        unfetched = self._db.get_unfetched()
        if not unfetched:
            return

        if self._api_thread and self._api_thread.isRunning():
            self._api_thread.stop()
            self._api_thread.wait()

        self._api_thread = ApiWorkerThread(
            games              = unfetched,
            rawg_api_key       = rawg_key,
            igdb_client_id     = igdb_client_id,
            igdb_client_secret = igdb_secret,
        )
        self._api_thread.game_updated.connect(self._on_game_updated)
        self._api_thread.cover_ready.connect(self._on_cover_ready)
        self._api_thread.status_message.connect(self._on_api_status)
        self._api_thread.finished_all.connect(self._on_api_finished)
        self._api_thread.start()

    def _on_game_updated(self, content_id: str, api_data: dict):
        self._db.update_api_data(content_id, api_data)
        for pkg in self._packages:
            if pkg.get("content_id") == content_id:
                pkg.update({
                    "title_api":    api_data.get("title_api", ""),
                    "description":  api_data.get("description", ""),
                    "developer":    api_data.get("developer", ""),
                    "publisher":    api_data.get("publisher", ""),
                    "release_date": api_data.get("release_date", ""),
                    "genres":       api_data.get("genres", []),
                    "rating":       api_data.get("rating", 0),
                    "screenshots":  api_data.get("screenshots", []),
                    "video_url":    api_data.get("video_url", ""),
                })
                break

    def _on_api_status(self, msg: str):
        self._status_msg = msg

    def _on_api_finished(self):
        self._status_msg = "Données API récupérées"
        self._packages   = self._db.get_all_games()
        self._show_library()

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    def on_card_clicked(self, filepath: str):
        pkg = self._db.get_game_by_filepath(filepath)
        if not pkg:
            pkg = next(
                (p for p in self._packages if p.get("filepath") == filepath),
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
        self._db.set_setting("active_filter", key)
        self._show_library()

    def on_sort(self, key: str):
        self._active_sort = key
        self._show_library()

    def on_toggle_view(self):
        self._view_mode = "list" if self._view_mode == "grid" else "grid"
        self._db.set_setting("view_mode", self._view_mode)
        self._show_library()

    def on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier PKG",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if not folder:
            return
        added = self._db.add_folder(folder)
        if not added:
            QMessageBox.information(
                self,
                "Dossier déjà présent",
                f"Ce dossier est déjà dans votre bibliothèque :\n{folder}"
            )
            return
        folders = self._db.get_folders()
        self._start_scan(folders)

    def on_rescan_folder(self, path: str):
        folders = self._db.get_folders()
        if path in folders:
            self._start_scan([path])

    def on_delete_folder(self, path: str):
        reply = QMessageBox.question(
            self,
            "Retirer le dossier",
            f"Retirer ce dossier de la bibliothèque ?\n\n{path}\n\n"
            f"Les fichiers PKG ne seront pas supprimés.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._db.remove_folder(path)
        self._packages = self._db.get_all_games()
        self._show_folders()

    def on_rename(self, filepath: str):
        old_name = os.path.basename(filepath)
        new_name, ok = QInputDialog.getText(
            self, "Renommer le fichier",
            "Nouveau nom :", text=old_name
        )
        if not ok or not new_name.strip() or new_name == old_name:
            return
        if not new_name.lower().endswith(".pkg"):
            new_name += ".pkg"
        new_path = os.path.join(os.path.dirname(filepath), new_name)
        try:
            os.rename(filepath, new_path)
            for pkg in self._packages:
                if pkg.get("filepath") == filepath:
                    pkg["filepath"] = new_path
                    pkg["filename"] = new_name
                    break
            self._db.delete_by_filepath(filepath)
        except OSError as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de renommer :\n{e}")

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
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            os.remove(filepath)
            self._db.delete_by_filepath(filepath)
            self._packages = [
                p for p in self._packages
                if p.get("filepath") != filepath
            ]
            self._show_library()
        except OSError as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de supprimer :\n{e}")

    def on_open_related(self, content_id: str):
        pkg = self._db.get_game(content_id)
        if not pkg:
            pkg = next(
                (p for p in self._packages if p.get("content_id") == content_id),
                None
            )
        if pkg:
            self._show_detail(pkg)

    def on_save_settings(self, json_str: str):
        try:
            data = json.loads(json_str)
            for key, value in data.items():
                self._db.set_setting(key, str(value))
            self._status_msg = "Paramètres sauvegardés"
            self._show_settings()
        except json.JSONDecodeError:
            pass

    def on_test_rawg(self, key: str):
        if not key:
            return
        try:
            resp = requests.get(
                "https://api.rawg.io/api/games",
                params={"key": key, "page_size": 1},
                timeout=5
            )
            if resp.status_code == 200:
                QMessageBox.information(self, "RAWG.io", "✅ Clé API valide !")
            else:
                QMessageBox.warning(self, "RAWG.io", f"❌ Clé invalide (code {resp.status_code})")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def on_clear_cache(self):
        reply = QMessageBox.question(
            self, "Vider le cache",
            "Supprimer toutes les jaquettes en cache ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        from core.cover_loader import COVERS_DIR, SCREENSHOTS_DIR
        import shutil
        for d in [COVERS_DIR, SCREENSHOTS_DIR]:
            if d.exists():
                shutil.rmtree(d)
                d.mkdir(parents=True)
        self._status_msg = "Cache vidé"
        self._show_settings()

    def on_reset_db(self):
        reply = QMessageBox.warning(
            self, "Réinitialiser la base de données",
            "Supprimer tous les jeux indexés ?\n\nLes fichiers PKG ne seront pas affectés.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._db.close()
        from core.database import DB_PATH
        if DB_PATH.exists():
            DB_PATH.unlink()
        self._db          = Database()
        self._packages    = []
        self._status_msg  = "Base de données réinitialisée"
        self._show_library()

    # ------------------------------------------------------------------ #
    #  Fermeture                                                           #
    # ------------------------------------------------------------------ #

    def closeEvent(self, event):
        for thread in [self._scan_thread, self._cover_thread, self._api_thread]:
            if thread and thread.isRunning():
                if hasattr(thread, "stop"):
                    thread.stop()
                thread.quit()
                thread.wait()
        self._db.close()
        event.accept()