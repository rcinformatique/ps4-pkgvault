from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea,
    QGridLayout, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from ui.theme import Colors, Fonts, Dimensions
from ui.widgets.pkg_card import PkgCard, CARD_WIDTH


LIBRARY_STYLE = f"""
    QWidget#library_page {{
        background: {Colors.BG_APP};
    }}
    QScrollArea {{
        background: {Colors.BG_APP};
        border: none;
    }}
    QScrollArea > QWidget > QWidget {{
        background: {Colors.BG_APP};
    }}

    /* Message vide */
    QLabel#empty_title {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_XL}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#empty_sub {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_LG}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""

COLS         = 4
CARD_SPACING = 16
PADDING      = 20


class EmptyState(QWidget):
    """Affiché quand la bibliothèque est vide."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        icon = QLabel("📦")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "font-size: 64px; background: transparent;"
        )

        title = QLabel("Bibliothèque vide")
        title.setObjectName("empty_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel(
            "Cliquez sur  ➕ Ajouter un dossier  pour scanner vos fichiers PKG"
        )
        sub.setObjectName("empty_sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(sub)


class LibraryPage(QWidget):
    """
    Page principale — grille de cartes PKG.

    Signaux :
        pkg_selected(pkg_data)  → carte cliquée
        pkg_deleted(filepath)   → fichier supprimé
        stats_updated(counts)   → stats mises à jour
    """

    pkg_selected  = pyqtSignal(dict)
    pkg_deleted   = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("library_page")
        self.setStyleSheet(LIBRARY_STYLE)

        self._all_packages  = []
        self._filtered      = []
        self._active_filter = "all"
        self._active_sort   = "title"
        self._sort_asc      = True
        self._search_text   = ""
        self._cards         = []
        self._selected_card = None

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Conteneur de la grille
        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(
            f"background: {Colors.BG_APP};"
        )
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(
            PADDING, PADDING, PADDING, PADDING
        )
        self._grid_layout.setSpacing(CARD_SPACING)
        self._grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self._scroll.setWidget(self._grid_container)
        layout.addWidget(self._scroll)

        # État vide
        self._empty_state = EmptyState()
        layout.addWidget(self._empty_state)

        self._show_empty(True)

    # ------------------------------------------------------------------ #
    #  Données                                                             #
    # ------------------------------------------------------------------ #

    def load_packages(self, packages: list[dict]):
        """Charge la liste complète des PKG."""
        self._all_packages = packages
        self._apply_filters()

    def _apply_filters(self):
        """Filtre, trie et rafraîchit la grille."""
        packages = self._all_packages.copy()

        # Filtre par type
        if self._active_filter != "all":
            packages = [
                p for p in packages
                if p.get("type") == self._active_filter
            ]

        # Filtre par recherche
        if self._search_text:
            q = self._search_text.lower()
            packages = [
                p for p in packages
                if q in p.get("title", "").lower()
                or q in p.get("content_id", "").lower()
                or q in p.get("title_api", "").lower()
            ]

        # Tri
        def sort_key(p):
            if self._active_sort == "title":
                return (p.get("title_api") or p.get("title") or "").lower()
            if self._active_sort == "size":
                return p.get("size_bytes", 0)
            if self._active_sort == "type":
                return p.get("type", "")
            if self._active_sort == "date":
                return p.get("date_added", "")
            return ""

        packages.sort(key=sort_key, reverse=not self._sort_asc)
        self._filtered = packages
        self._refresh_grid()

    def _refresh_grid(self):
        """Vide et reconstruit la grille."""

        # Vide les cartes
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
        self._selected_card = None

        if not self._filtered:
            self._show_empty(True)
            self._emit_stats()
            return

        self._show_empty(False)

        for i, pkg in enumerate(self._filtered):
            card = PkgCard(pkg)
            card.clicked.connect(self._on_card_clicked)
            card.deleted.connect(self._on_card_deleted)
            row = i // COLS
            col = i % COLS
            self._grid_layout.addWidget(card, row, col)
            self._cards.append(card)

        self._emit_stats()

    def _emit_stats(self):
        """Émet les stats pour la statusbar."""
        counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
        for pkg in self._all_packages:
            t = pkg.get("type", "game")
            if t in counts:
                counts[t] += 1
        self.stats_updated.emit(counts)

    def _show_empty(self, state: bool):
        """Affiche ou cache l'état vide."""
        self._scroll.setVisible(not state)
        self._empty_state.setVisible(state)

    # ------------------------------------------------------------------ #
    #  Jaquettes                                                           #
    # ------------------------------------------------------------------ #

    def update_cover(self, filepath: str, pixmap: QPixmap):
        """Met à jour la jaquette d'une carte via filepath."""
        for card in self._cards:
            if card.pkg_data.get("filepath") == filepath:
                card.set_cover_pixmap(pixmap)
                break

    def update_cover_by_cid(self, content_id: str, cover_path: str):
        """Met à jour la jaquette d'une carte via content_id."""
        pixmap = QPixmap(cover_path)
        if pixmap.isNull():
            return
        for card in self._cards:
            if card.pkg_data.get("content_id") == content_id:
                card.set_cover_pixmap(pixmap)
                break

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    def _on_card_clicked(self, pkg_data: dict):
        """Sélectionne la carte et émet le signal."""
        # Désélectionne la précédente
        if self._selected_card:
            self._selected_card.set_selected(False)

        # Trouve et sélectionne la nouvelle
        for card in self._cards:
            if card.pkg_data.get("filepath") == pkg_data.get("filepath"):
                card.set_selected(True)
                self._selected_card = card
                break

        self.pkg_selected.emit(pkg_data)

    def _on_card_deleted(self, filepath: str):
        """Retire le PKG supprimé de la liste."""
        self._all_packages = [
            p for p in self._all_packages
            if p.get("filepath") != filepath
        ]
        self._apply_filters()
        self.pkg_deleted.emit(filepath)

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def set_filter(self, key: str):
        """Applique un filtre par type."""
        self._active_filter = key
        self._apply_filters()

    def set_sort(self, key: str, ascending: bool = True):
        """Applique un tri."""
        self._active_sort = key
        self._sort_asc    = ascending
        self._apply_filters()

    def set_search(self, text: str):
        """Applique une recherche."""
        self._search_text = text
        self._apply_filters()

    def get_filtered_count(self) -> int:
        return len(self._filtered)

    def get_filtered_size(self) -> int:
        return sum(
            p.get("size_bytes", 0) for p in self._filtered
        )

    def get_total_size_str(self) -> str:
        total = sum(
            p.get("size_bytes", 0) for p in self._filtered
        )
        if total >= 1_073_741_824:
            return f"{total / 1_073_741_824:.1f} Go"
        if total >= 1_048_576:
            return f"{total / 1_048_576:.1f} Mo"
        return f"{total / 1024:.1f} Ko"