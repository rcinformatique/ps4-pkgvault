import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QApplication
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot, QUrl
from ui.theme import Colors, Fonts, Dimensions
from ui.template_engine import TemplateEngine


class PyBridge(QObject):
    """
    Pont Python ↔ JavaScript pour les actions
    déclenchées depuis le HTML (boutons, clics).
    """

    open_folder_requested  = pyqtSignal(str)
    copy_path_requested    = pyqtSignal(str)
    copy_cid_requested     = pyqtSignal(str)
    open_related_requested = pyqtSignal(str)

    @pyqtSlot(str)
    def open_folder(self, filepath: str):
        self.open_folder_requested.emit(filepath)

    @pyqtSlot(str)
    def copy_path(self, filepath: str):
        self.copy_path_requested.emit(filepath)

    @pyqtSlot(str)
    def copy_cid(self, cid: str):
        self.copy_cid_requested.emit(cid)

    @pyqtSlot(str)
    def open_related(self, content_id: str):
        self.open_related_requested.emit(content_id)


BACK_BAR_STYLE = f"""
    QWidget#back_bar {{
        background: {Colors.BG_WHITE};
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
    }}
    QPushButton#back_btn {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 5px 13px;
    }}
    QPushButton#back_btn:hover {{
        border-color: {Colors.ACCENT};
        color: {Colors.ACCENT};
    }}
    QLabel#breadcrumb {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""


class DetailPage(QWidget):
    """
    Page de détail utilisant QWebEngineView + Jinja2.
    """

    back_requested   = pyqtSignal()
    relation_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_pkg  = {}
        self._related_pkgs = []
        self._engine       = TemplateEngine()
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._make_back_bar())

        # WebEngine
        self._web_view = QWebEngineView()
        self._web_view.setStyleSheet("background: #f0f2f5;")

        # Pont Python ↔ JS
        self._bridge  = PyBridge()
        self._channel = QWebChannel()
        self._channel.registerObject("pybridge", self._bridge)
        self._web_view.page().setWebChannel(self._channel)

        # Connexions bridge
        self._bridge.open_folder_requested.connect(
            self._on_open_folder
        )
        self._bridge.copy_path_requested.connect(
            self._on_copy_path
        )
        self._bridge.copy_cid_requested.connect(
            self._on_copy_cid
        )
        self._bridge.open_related_requested.connect(
            self.relation_clicked.emit
        )

        layout.addWidget(self._web_view)

    def _make_back_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("back_bar")
        bar.setFixedHeight(40)
        bar.setStyleSheet(BACK_BAR_STYLE)

        h = QHBoxLayout(bar)
        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(10)

        back_btn = QPushButton("← Retour")
        back_btn.setObjectName("back_btn")
        back_btn.setFixedHeight(28)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.back_requested.emit)
        h.addWidget(back_btn)

        self._breadcrumb = QLabel("Bibliothèque")
        self._breadcrumb.setObjectName("breadcrumb")
        h.addWidget(self._breadcrumb)
        h.addStretch()

        return bar

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def show_pkg(self, pkg_data: dict, related: list = None):
        """Génère et affiche le HTML de la page de détail."""
        self._current_pkg  = pkg_data
        self._related_pkgs = related or []

        # Breadcrumb
        title = (
            pkg_data.get("title_api")
            or pkg_data.get("title")
            or "Inconnu"
        )
        self._breadcrumb.setText(
            f"Bibliothèque  ›  {title[:60]}"
        )

        # Génère le HTML via Jinja2
        html = self._engine.render_detail(pkg_data, related)

        # Injecte le WebChannel JS
        html = self._inject_webchannel(html)

        # Charge le HTML
        self._web_view.setHtml(
            html,
            QUrl("file:///")
        )

    def update_cover(self, cover_path: str):
        """Recharge la page si la jaquette change."""
        if self._current_pkg:
            self._current_pkg["cover_path"] = cover_path
            self.show_pkg(self._current_pkg, self._related_pkgs)

    def _inject_webchannel(self, html: str) -> str:
        """
        Injecte le script qwebchannel.js nécessaire
        pour la communication Python ↔ JS.
        """
        webchannel_script = """
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof QWebChannel !== 'undefined') {
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.pybridge = channel.objects.pybridge;
                });
            }
        });
        </script>
        """
        return html.replace("</head>", webchannel_script + "</head>")

    # ------------------------------------------------------------------ #
    #  Actions                                                             #
    # ------------------------------------------------------------------ #

    def _on_open_folder(self, filepath: str):
        if filepath:
            folder = os.path.dirname(filepath)
            subprocess.Popen(f'explorer "{folder}"')

    def _on_copy_path(self, filepath: str):
        if filepath:
            QApplication.clipboard().setText(filepath)

    def _on_copy_cid(self, cid: str):
        if cid:
            QApplication.clipboard().setText(cid)