from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme import Colors, Dimensions, Fonts


SUBBAR_STYLE = f"""
    QWidget#subbar {{
        background-color: {Colors.BG_WHITE};
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
    }}

    /* Filtres pills */
    QPushButton#filter_pill {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER_STRONG};
        border-radius: 14px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        padding: 3px 13px;
    }}
    QPushButton#filter_pill:hover {{
        border-color: {Colors.ACCENT};
        color: {Colors.ACCENT};
    }}
    QPushButton#filter_pill[active=true] {{
        background: {Colors.ACCENT};
        border-color: {Colors.ACCENT};
        color: #ffffff;
        font-weight: 600;
    }}

    /* Tri */
    QPushButton#sort_btn {{
        background: transparent;
        border: none;
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        padding: 3px 6px;
    }}
    QPushButton#sort_btn:hover {{
        color: {Colors.ACCENT};
    }}

    /* Compteur */
    QLabel#count_label {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
    }}
"""


class FilterPill(QPushButton):
    """Bouton filtre pill."""

    def __init__(self, label: str, key: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("filter_pill")
        self.setText(label)
        self.setFixedHeight(26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

    def set_active(self, state: bool):
        self.setProperty("active", state)
        self.style().unpolish(self)
        self.style().polish(self)


class Subbar(QWidget):
    """
    Barre de filtres et tri sous la topbar.
    Visible uniquement sur la page Bibliothèque.

    Signaux :
        filter_changed(key)  → filtre sélectionné
        sort_changed(key)    → tri sélectionné
    """

    filter_changed = pyqtSignal(str)
    sort_changed   = pyqtSignal(str)

    # Filtres disponibles : (label, clé)
    FILTERS = [
        ("Tous",      "all"),
        ("BASE",      "game"),
        ("DLC",       "dlc"),
        ("UPDATE",    "update"),
        ("BACKPORT",  "backport"),
    ]

    # Options de tri : (label, clé)
    SORT_OPTIONS = [
        ("Nom",       "title"),
        ("Taille",    "size"),
        ("Type",      "type"),
        ("Date",      "date"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("subbar")
        self.setFixedHeight(Dimensions.SUBBAR_HEIGHT)
        self.setStyleSheet(SUBBAR_STYLE)

        self._filter_pills  = {}
        self._active_filter = "all"
        self._active_sort   = "title"
        self._sort_asc      = True

        self._build_ui()
        self._set_active_filter("all")

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(6)

        # Filtres
        for label, key in self.FILTERS:
            pill = FilterPill(label, key)
            pill.clicked.connect(
                lambda checked, k=key: self._on_filter_click(k)
            )
            self._filter_pills[key] = pill
            layout.addWidget(pill)

        layout.addStretch()

        # Tri
        sort_lbl = QLabel("Trier :")
        sort_lbl.setStyleSheet(
            f"color: {Colors.TEXT_HINT}; font-size: {Fonts.SIZE_SM}px; background: transparent;"
        )
        layout.addWidget(sort_lbl)

        for label, key in self.SORT_OPTIONS:
            btn = QPushButton(label)
            btn.setObjectName("sort_btn")
            btn.setFixedHeight(26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, k=key: self._on_sort_click(k)
            )
            layout.addWidget(btn)

        # Séparateur
        sep = QLabel("|")
        sep.setStyleSheet(
            f"color: {Colors.BORDER}; font-size: 14px; background: transparent;"
        )
        layout.addWidget(sep)

        # Compteur
        self._count_label = QLabel("0 fichiers")
        self._count_label.setObjectName("count_label")
        layout.addWidget(self._count_label)

    # ------------------------------------------------------------------ #
    #  Interactions                                                        #
    # ------------------------------------------------------------------ #

    def _on_filter_click(self, key: str):
        self._set_active_filter(key)
        self.filter_changed.emit(key)

    def _on_sort_click(self, key: str):
        if self._active_sort == key:
            self._sort_asc = not self._sort_asc
        else:
            self._active_sort = key
            self._sort_asc    = True
        self.sort_changed.emit(key)

    def _set_active_filter(self, key: str):
        if self._active_filter in self._filter_pills:
            self._filter_pills[self._active_filter].set_active(False)
        self._active_filter = key
        if key in self._filter_pills:
            self._filter_pills[key].set_active(True)

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def set_filter(self, key: str):
        """Active un filtre depuis l'extérieur."""
        self._set_active_filter(key)

    def update_count(self, total: int, size_str: str = ""):
        """Met à jour le compteur de fichiers."""
        text = f"{total} fichier{'s' if total > 1 else ''}"
        if size_str:
            text += f" · {size_str}"
        self._count_label.setText(text)

    @property
    def active_filter(self) -> str:
        return self._active_filter

    @property
    def active_sort(self) -> str:
        return self._active_sort

    @property
    def sort_ascending(self) -> bool:
        return self._sort_asc