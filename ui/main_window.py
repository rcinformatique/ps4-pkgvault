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
from core.activity_log import activity, EVENT_SCAN, EVENT_API, EVENT_ERROR

# ------------------------------------------------------------------ #
#  Thread de scan complet                                              #
# ------------------------------------------------------------------ #

class ScanThread(QThread):
    scan_done   = pyqtSignal(list, list)
    progress    = pyqtSignal(int, int)
    pkg_scanned = pyqtSignal(dict)  # ← nouveau

    def __init__(self, folders: list[str], db: Database, parent=None):
        super().__init__(parent)
        self._folders = folders
        self._db      = db
        self._running = True

    def run(self):
        all_packages = []
        all_errors   = []
        for folder in self._folders:
            pkgs, errors = scan_folder(
                folder,
                db=self._db,
                progress_callback=lambda c, t: self.progress.emit(c, t),
                pkg_callback=lambda p: self.pkg_scanned.emit(p),  # ← nouveau
            )
            all_packages.extend(pkgs)
            all_errors.extend(errors)
        self.scan_done.emit(all_packages, all_errors)

    def stop(self):
        self._running = False


# ------------------------------------------------------------------ #
#  Thread de scan fichiers spécifiques                                 #
# ------------------------------------------------------------------ #

class ScanFilesThread(QThread):
    scan_done    = pyqtSignal(list, list)
    pkg_scanned  = pyqtSignal(dict)  # ← nouveau signal par PKG

    def __init__(self, filepaths: list[str], db: Database, parent=None):
        super().__init__(parent)
        self._filepaths = filepaths
        self._db        = db
        self._running   = True

    def run(self):
        from core.pkg_reader import read_pkg
        packages = []
        errors = []
        for filepath in self._filepaths:
            if not self._running:
                break
            result = read_pkg(filepath)
            if result:
                self._db.upsert_game(result)
                packages.append(result)
                self.pkg_scanned.emit(result)
            else:
                errors.append(filepath)
        self.scan_done.emit(packages, errors)

    def stop(self):
        self._running = False


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

    @pyqtSlot()
    def fetch_api(self):
        self._win.on_fetch_api()

    @pyqtSlot(str)
    def refetch_api(self, content_id: str):
        self._win.on_refetch_api(content_id)

    @pyqtSlot()
    def clear_activity(self):
        self._win.on_clear_activity()

    @pyqtSlot(str)
    def navigate_activity(self, filter_type: str = "all"):
        self._win.navigate("activity")


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
        """Charge les données au démarrage et ne rescanne que les nouveaux fichiers."""
        self._active_filter = self._db.get_setting("active_filter", "game")
        self._view_mode = self._db.get_setting("view_mode", "grid")

        cached = self._db.get_all_games()
        if cached:
            self._packages = cached
            self._status_msg = f"{len(cached)} PKG chargés"

        self._show_library()

        folders = self._db.get_folders()
        if folders:
            self._start_smart_scan(folders)
        else:
            # Pas de dossiers mais des PKG en base — lance quand même le cover loader
            if self._packages:
                self._start_cover_loader(self._packages)

    def _start_smart_scan(self, folders: list[str]):
        """Scanne uniquement les nouveaux fichiers."""

        known_paths = set(
            os.path.normcase(os.path.abspath(p.get("filepath", "")))
            for p in self._packages
            if p.get("filepath")
        )

        disk_files = []
        for folder in folders:
            folder_path = Path(folder)
            if folder_path.exists():
                for f in folder_path.rglob("*.pkg"):
                    disk_files.append(
                        os.path.normcase(os.path.abspath(str(f)))
                    )

        new_files = [f for f in disk_files if f not in known_paths]
        missing = [p for p in known_paths if p and not Path(p).exists()]

        print(f"Smart scan : {len(new_files)} nouveaux, {len(missing)} manquants")

        for filepath in missing:
            self._db.delete_by_filepath(filepath)
            self._packages = [
                p for p in self._packages
                if os.path.normcase(os.path.abspath(
                    p.get("filepath", "")
                )) != filepath
            ]

        if missing:
            self._packages = self._db.get_all_games()
            self._show_library()

        if new_files:
            self._status_msg = f"Nouveaux fichiers : {len(new_files)}"
            self._show_library()
            self._start_scan_files(new_files)
        else:
            self._status_msg = f"{len(self._packages)} PKG chargés"
            self._show_library()
            self._start_cover_loader(self._packages)

    def _start_scan_files(self, filepaths: list[str]):
        if self._scan_thread and self._scan_thread.isRunning():
            self._scan_thread.quit()
            self._scan_thread.wait()

        self._scan_thread = ScanFilesThread(filepaths, self._db)
        self._scan_thread.pkg_scanned.connect(self._on_pkg_scanned)  # ← nouveau
        self._scan_thread.scan_done.connect(self._on_scan_done)
        self._scan_thread.start()

    def _on_pkg_scanned(self, pkg_data: dict):
        """
        Appelé pour chaque PKG scanné — ajoute la carte
        directement dans le DOM sans recharger la page.
        """
        import json as _json
        from ui.template_engine import TYPE_INFO

        # Ne logue que si vraiment nouveau (pas déjà en mémoire)
        filepath_resolved = str(Path(pkg_data.get("filepath", "")).resolve())
        already_known = any(
            str(Path(p.get("filepath", "")).resolve()) == filepath_resolved
            for p in self._packages
        )
        if not already_known:
            activity.log_scan(pkg_data)

        # Ajoute au tableau en mémoire si pas déjà présent
        exists = any(
            str(Path(p.get("filepath", "")).resolve()) == filepath_resolved
            for p in self._packages
        )
        if not exists:
            self._packages.append(pkg_data)

        # Prépare les données pour le template
        pkg_type = pkg_data.get("type", "game")
        info = TYPE_INFO.get(pkg_type, TYPE_INFO["game"])
        cover = (pkg_data.get("cover_path") or "").replace("\\", "/")

        normalized = {
            **pkg_data,
            "type_label": info["label"],
            "type_icon": info["icon"],
            "cover_path": cover,
            "screenshots": [],
        }

        # Sérialise pour injection JS
        pkg_json = _json.dumps(normalized, ensure_ascii=False)
        index = len(self._packages) - 1
        firmware = pkg_data.get("firmware", "")
        fw_badge = f'<span class="fw-badge">FW {firmware}</span>' if firmware else ""
        cover_html = (
            f'<img src="file:///{cover}" alt="{pkg_data.get("title", "")}" />'
            if cover else
            f'<div class="cover-inner">{info["icon"]}</div>'
        )

        # Échappe les caractères dangereux pour l'injection JS
        title = (pkg_data.get("title_api") or pkg_data.get("title") or "")
        title = title.replace("\\", "\\\\").replace("`", "\\`").replace("'", "\\'")
        cid = (pkg_data.get("content_id") or "")[:20]
        size_str = pkg_data.get("size_str", "")
        region = pkg_data.get("region", "")

        js = f"""
        (function() {{
            // Met à jour le tableau JS
            if (typeof _packages !== 'undefined') {{
                _packages.push({pkg_json});
            }}

            var grid  = document.getElementById('view-grid');
            var empty = document.querySelector('.empty-state');

            // Cache l'état vide
            if (empty) empty.style.display = 'none';

            // Ajoute dans la grille
            if (grid) {{
                grid.style.display = 'grid';
                var card = document.createElement('div');
                card.className = 'pkg-card scanning';
                card.id = 'card-{index}';
                card.onclick = function() {{ onCardClick({index}); }};
                card.oncontextmenu = function(e) {{ showCtxMenu(e, {index}); }};
                card.innerHTML = `
                    <div class="cover cover-bg-{pkg_type}">
                        {cover_html}
                        <span class="type-badge badge-{pkg_type}">{info["label"]}</span>
                        {fw_badge}
                    </div>
                    <div class="card-info">
                        <div class="card-title">{title}</div>
                        <div class="card-cid">{cid}</div>
                        <div class="card-bottom">
                            <span class="card-size">{size_str}</span>
                            <span class="card-region">{region}</span>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
                card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}

            // Met à jour le statusbar
            var msg = document.getElementById('sb-msg');
            if (msg) {{
                var count = typeof _packages !== 'undefined' ? _packages.length : '';
                msg.innerHTML = '📦 Scan en cours… ' + count + ' PKG';
            }}
        }})();
        """

        self._web.page().runJavaScript(js)

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
        elif page == "activity":
            self._show_activity()

    def _show_activity(self):
        html = self._engine.render_activity(
            stats=self._get_stats(),
            status_msg=self._status_msg,
        )
        self._load_html(html, show_back=False)

    def on_clear_activity(self):
        activity.clear()
        self._show_activity()

    def go_back(self):
        self.navigate(self._previous_page)

    def _load_html(self, html: str, show_back: bool = False):
        # Plus besoin d'injecter le webchannel — base.html le gère
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
        # Garde pour compatibilité mais ne fait plus rien
        # base.html contient déjà le script WebChannel
        return html

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
                   or q in (p.get("title_id") or "").lower()
                   or q in (p.get("filename") or "").lower()
            ]

        def sort_key(p):
            if self._active_sort == "title":
                return (p.get("title_api") or p.get("title") or "").lower()
            if self._active_sort == "size":
                return p.get("size_bytes", 0)
            if self._active_sort == "type":
                return p.get("type", "")
            if self._active_sort == "date":
                return (
                        p.get("date_added")
                        or p.get("last_scanned")
                        or p.get("filepath", "")
                )
            return ""

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
        self._scan_thread.pkg_scanned.connect(self._on_pkg_scanned)  # ← nouveau
        self._scan_thread.scan_done.connect(self._on_scan_done)
        self._scan_thread.start()

    def _on_scan_done(self, packages: list, errors: list):

        for filepath in errors:
            activity.log_error(filepath, "Magic inconnu ou SFO introuvable")

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
            self._cover_thread.quit()
            self._cover_thread.wait(3000)

        # Sépare les PKG sans cover des autres
        without_cover = [
            p for p in packages
            if not p.get("cover_path")
               or not Path(p.get("cover_path", "")).exists()
        ]

        if not without_cover:
            return

        print(f"Cover loader : {len(without_cover)} PKG sans jaquette")

        self._cover_thread = CoverLoaderThread(without_cover)
        self._cover_thread.cover_ready.connect(self._on_cover_ready)
        self._cover_thread.finished_all.connect(self._on_cover_finished)
        self._cover_thread.start()

    def _on_cover_finished(self):
        """Appelé quand toutes les covers sont chargées."""
        print("Cover loader terminé")
        # Rafraîchit la bibliothèque pour afficher les nouvelles covers
        self._packages = self._db.get_all_games()
        self._show_library()

    def _on_cover_ready(self, content_id: str, cover_path: str):
        # Normalise en absolu
        cover_abs = str(Path(cover_path).resolve())

        # Sauvegarde en base
        self._db.update_cover(content_id, cover_abs)

        # Met à jour en mémoire
        for pkg in self._packages:
            if pkg.get("content_id") == content_id:
                pkg["cover_path"] = cover_abs
                break

        # Met à jour la carte dans le DOM sans recharger la page
        cover_url = cover_abs.replace("\\", "/")
        js = f"""
        (function() {{
            var cards = document.querySelectorAll('.pkg-card, .list-item');
            cards.forEach(function(card) {{
                var cid = card.querySelector('.card-cid, .list-title-sub');
                if (cid && cid.textContent.includes('{content_id[:20]}')) {{
                    var img = card.querySelector('img');
                    var inner = card.querySelector('.cover-inner');
                    if (img) {{
                        img.src = 'file:///{cover_url}';
                    }} else if (inner) {{
                        var cover = inner.parentElement;
                        cover.innerHTML = '<img src="file:///{cover_url}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" />'
                            + cover.innerHTML.replace(inner.outerHTML, '');
                    }}
                }}
            }});
        }})();
        """
        self._web.page().runJavaScript(js)

    # ------------------------------------------------------------------ #
    #  API Worker                                                          #
    # ------------------------------------------------------------------ #

    def _start_api_worker(self):
        """Lance la récupération API automatique."""
        rawg_key       = self._db.get_setting("rawg_api_key", "")
        igdb_client_id = self._db.get_setting("igdb_client_id", "")
        igdb_secret    = self._db.get_setting("igdb_client_secret", "")
        auto_fetch     = self._db.get_setting("auto_fetch", "1")

        if auto_fetch != "1" or not rawg_key:
            return

        unfetched = self._db.get_unfetched()
        if not unfetched:
            return

        self._start_api_worker_manual(unfetched)

    def _start_api_worker_manual(self, games: list[dict]):
        """Lance le worker API avec une liste spécifique."""
        rawg_key       = self._db.get_setting("rawg_api_key", "")
        igdb_client_id = self._db.get_setting("igdb_client_id", "")
        igdb_secret    = self._db.get_setting("igdb_client_secret", "")

        if not rawg_key:
            return

        if self._api_thread and self._api_thread.isRunning():
            self._api_thread.stop()
            self._api_thread.wait()

        self._api_thread = ApiWorkerThread(
            games              = games,
            rawg_api_key       = rawg_key,
            igdb_client_id     = igdb_client_id,
            igdb_client_secret = igdb_secret,
        )
        self._api_thread.game_updated.connect(self._on_game_updated)
        self._api_thread.cover_ready.connect(self._on_cover_ready)
        self._api_thread.progress.connect(self._on_api_progress)
        self._api_thread.status_message.connect(self._on_api_status)
        self._api_thread.finished_all.connect(self._on_api_finished)
        self._api_thread.start()

    def _on_game_updated(self, content_id: str, api_data: dict):

        title = api_data.get("title_api", "") or content_id
        source = "RAWG" if api_data.get("rating") is not None else "IGDB"
        activity.log_api(title, source=source, content_id=content_id)

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

    def _on_api_progress(self, current: int, total: int):
        """Met à jour la progression dans la statusbar via JS."""
        self._web.page().runJavaScript(f"""
            var el  = document.getElementById('sb-progress');
            var txt = document.getElementById('sb-progress-text');
            if (el)  el.style.display = 'inline';
            if (txt) txt.textContent  = 'API {current}/{total}';
        """)

    def _on_api_status(self, msg: str):
        """Met à jour le message de statut via JS."""
        safe_msg = msg[:50].replace("'", "\\'").replace("\n", " ")
        self._web.page().runJavaScript(f"""
            var txt = document.getElementById('sb-progress-text');
            if (txt) txt.textContent = '{safe_msg}';
        """)

    def _on_api_finished(self):
        """Cache la progression et rafraîchit."""
        self._web.page().runJavaScript("""
            var el = document.getElementById('sb-progress');
            if (el) el.style.display = 'none';
        """)
        self._status_msg = "✅ Données API récupérées"
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
        # self._show_library()

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

    def on_fetch_api(self):
        """Lance la récupération API manuellement."""
        rawg_key = self._db.get_setting("rawg_api_key", "")
        if not rawg_key:
            QMessageBox.warning(
                self,
                "Clé API manquante",
                "Configurez votre clé RAWG.io dans Paramètres."
            )
            return

        unfetched = self._db.get_unfetched()
        if not unfetched:
            QMessageBox.information(
                self,
                "Données API",
                "✅ Toutes les données API sont déjà récupérées !"
            )
            return

        self._status_msg = f"Récupération API — {len(unfetched)} jeux…"
        self._show_library()
        self._start_api_worker_manual(unfetched)

    def on_refetch_api(self, content_id: str):
        """Force la re-récupération API pour un jeu spécifique."""
        rawg_key = self._db.get_setting("rawg_api_key", "")
        if not rawg_key:
            QMessageBox.warning(
                self,
                "Clé API manquante",
                "Configurez votre clé RAWG.io dans Paramètres."
            )
            return

        # Remet api_fetched à 0
        self._db._conn.execute(
            "UPDATE games SET api_fetched = 0 WHERE content_id = ?",
            (content_id,)
        )
        self._db._conn.commit()

        # Met à jour en mémoire et relance
        for pkg in self._packages:
            if pkg.get("content_id") == content_id:
                pkg["api_fetched"] = 0
                self._start_api_worker_manual([pkg])
                break

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
        if path not in folders:
            return
        # Délai pour laisser le WebChannel terminer son callback JS
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._do_rescan_folder(path))

    def _do_rescan_folder(self, path: str):
        """Logique de rescan — appelée après délai WebChannel."""

        # Stoppe les threads en cours
        for thread in [self._scan_thread, self._cover_thread, self._api_thread]:
            if thread and thread.isRunning():
                if hasattr(thread, "stop"):
                    thread.stop()
                thread.quit()
                thread.wait(3000)

        self._scan_thread = None
        self._cover_thread = None
        self._api_thread = None

        try:
            path_norm = os.path.normcase(os.path.abspath(path))

            disk_files = set(
                os.path.normcase(os.path.abspath(str(f)))
                for f in Path(path).rglob("*.pkg")
            )

            folder_pkgs = [
                p for p in self._packages
                if os.path.normcase(os.path.abspath(
                    p.get("filepath", "")
                )).startswith(path_norm)
            ]

            missing = [
                p for p in folder_pkgs
                if os.path.normcase(os.path.abspath(
                    p.get("filepath", "")
                )) not in disk_files
            ]

            for pkg in missing:
                filepath = pkg.get("filepath", "")
                self._db.delete_by_filepath(filepath)
                self._packages = [
                    p for p in self._packages
                    if p.get("filepath") != filepath
                ]

            if missing:
                print(f"Rescanner : {len(missing)} PKG manquants supprimés")
                self._packages = self._db.get_all_games()

        except Exception as e:
            print(f"_do_rescan_folder erreur : {e}")

        self._status_msg = "Scan en cours…"
        self._show_library()

        self._scan_thread = ScanThread([path], self._db)
        self._scan_thread.pkg_scanned.connect(self._on_pkg_scanned)
        self._scan_thread.scan_done.connect(self._on_scan_done)
        self._scan_thread.start()

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
                QMessageBox.warning(
                    self, "RAWG.io",
                    f"❌ Clé invalide (code {resp.status_code})"
                )
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
            "Supprimer tous les jeux indexés ?\n\n"
            "Les fichiers PKG ne seront pas affectés.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._db.close()
        from core.database import DB_PATH
        if DB_PATH.exists():
            DB_PATH.unlink()

        self._db = Database()
        self._packages = []
        self._status_msg = "Base de données réinitialisée"

        # Réinitialise aussi le journal d'activité
        activity.reset()

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