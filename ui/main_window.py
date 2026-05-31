from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QSize
from ui.theme import Colors
from ui.topbar import Topbar
from ui.subbar import Subbar
from ui.widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_ui()

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
        self._layout.addWidget(self.topbar)

        # Subbar
        self.subbar = Subbar()
        self.subbar.update_count(0)
        self.subbar.filter_changed.connect(self._on_filter_changed)
        self.subbar.sort_changed.connect(self._on_sort_changed)
        self._layout.addWidget(self.subbar)

        # StatusBar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.set_ready()

    def _on_tab_changed(self, key: str):
        self.subbar.setVisible(key == "library")

    def _on_add_folder(self):
        print("Ajouter un dossier")

    def _on_filter_changed(self, key: str):
        print(f"Filtre: {key}")

    def _on_sort_changed(self, key: str):
        print(f"Tri: {key}")