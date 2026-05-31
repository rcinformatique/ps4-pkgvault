from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea,
    QLabel, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap
from ui.theme import Colors, Fonts
from ui.widgets.pkg_card import PkgCard


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
    QLabel#empty_title {{
        color: {Colors.TEXT_MUTED};
        font-size: 18px;
        font-weight: 600;
        font-family: Segoe UI;
        background: transparent;
    }}
    QLabel#empty_sub {{
        color: {Colors.TEXT_HINT};
        font-size: 14px;
        font-family: Segoe UI;
        background: transparent;
    }}
"""

# Largeur minimale d'une carte en pixels
CARD_MIN_WIDTH = 180
PADDING        = 20
SPACING        = 14


class EmptyState(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon = QLabel("📦")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "font-size: 72px; background: transparent;"
        )

        title = QLabel("Bibliothèque vide")
        title.setObjectName("empty_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel(
            "Cliquez sur  ➕ Ajouter un dossier  "
            "pour scanner vos fichiers PKG"
        )
        sub.setObjectName("empty_sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(sub)


class LibraryPage(QWidget):

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
        self._current_cols  = 0

        # Timer pour debounce du resize
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_done)

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(
            f"background: {Colors.BG_APP};"
        )

        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(
            PADDING, PADDING, PADDING, PADDING
        )
        self._grid_layout.setSpacing(SPACING)
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
    #  Calcul du nombre de colonnes                                       #
    # ------------------------------------------------------------------ #

    def _compute_cols(self) -> int:
        """
        Calcule le nombre de colonnes selon la largeur disponible.
        Largeur disponible = largeur du scroll - 2 * padding.
        """
        available = self._scroll.width() - 2 * PADDING
        if available <= 0:
            return 4  # valeur par défaut

        # Nombre de colonnes = floor(available / (min_width + spacing))
        cols = max(2, available // (CARD_MIN_WIDTH + SPACING))
        cols = min(cols, 8)  # max 8 colonnes
        return int(cols)

    # ------------------------------------------------------------------ #
    #  Données                                                             #
    # ------------------------------------------------------------------ #

    def load_packages(self, packages: list[dict]):
        self._all_packages = packages
        self._apply_filters()

    def _apply_filters(self):
        packages = self._all_packages.copy()

        if self._active_filter != "all":
            packages = [
                p for p in packages
                if p.get("type") == self._active_filter
            ]

        if self._search_text:
            q = self._search_text.lower()
            packages = [
                p for p in packages
                if q in p.get("title", "").lower()
                or q in p.get("content_id", "").lower()
                or q in p.get("title_api", "").lower()
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
            if self._active_sort == "date":
                return p.get("date_added", "")
            return ""

        packages.sort(key=sort_key, reverse=not self._sort_asc)
        self._filtered = packages
        self._refresh_grid()

    def _refresh_grid(self):
        """Vide et reconstruit la grille."""
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

        cols = self._compute_cols()
        self._current_cols = cols

        # Colonnes de stretch égal
        for col in range(cols):
            self._grid_layout.setColumnStretch(col, 1)

        for i, pkg in enumerate(self._filtered):
            card = PkgCard(pkg)
            card.clicked.connect(self._on_card_clicked)
            card.deleted.connect(self._on_card_deleted)

            # Force toutes les cartes à la même hauteur
            card.setFixedHeight(300)

            row = i // cols
            col = i % cols
            self._grid_layout.addWidget(card, row, col)
            self._cards.append(card)

        self._emit_stats()

    def _reflow_grid(self):
        """
        Repositionne les cartes existantes dans la grille
        sans les recréer — plus rapide qu'un refresh complet.
        """
        cols = self._compute_cols()

        if cols == self._current_cols:
            return  # Rien à faire

        self._current_cols = cols

        # Retire toutes les cartes du layout
        for card in self._cards:
            self._grid_layout.removeWidget(card)

        # Remet les colonnes de stretch
        for col in range(8):
            self._grid_layout.setColumnStretch(col, 0)
        for col in range(cols):
            self._grid_layout.setColumnStretch(col, 1)

        # Replace les cartes
        for i, card in enumerate(self._cards):
            card.setFixedHeight(300)
            row = i // cols
            col = i % cols
            self._grid_layout.addWidget(card, row, col)

    # ------------------------------------------------------------------ #
    #  Resize responsive                                                   #
    # ------------------------------------------------------------------ #

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Debounce : attend 150ms après le dernier resize
        self._resize_timer.start(150)

    def _on_resize_done(self):
        """Appelé 150ms après le dernier resize."""
        self._reflow_grid()

    # ------------------------------------------------------------------ #
    #  Jaquettes                                                           #
    # ------------------------------------------------------------------ #

    def update_cover(self, filepath: str, pixmap: QPixmap):
        for card in self._cards:
            if card.pkg_data.get("filepath") == filepath:
                card.set_cover_pixmap(pixmap)
                break

    def update_cover_by_cid(self, content_id: str, cover_path: str):
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
        if self._selected_card:
            self._selected_card.set_selected(False)
        for card in self._cards:
            if card.pkg_data.get("filepath") == pkg_data.get("filepath"):
                card.set_selected(True)
                self._selected_card = card
                break
        self.pkg_selected.emit(pkg_data)

    def _on_card_deleted(self, filepath: str):
        self._all_packages = [
            p for p in self._all_packages
            if p.get("filepath") != filepath
        ]
        self._apply_filters()
        self.pkg_deleted.emit(filepath)

    def _emit_stats(self):
        counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
        for pkg in self._all_packages:
            t = pkg.get("type", "game")
            if t in counts:
                counts[t] += 1
        self.stats_updated.emit(counts)

    def _show_empty(self, state: bool):
        self._scroll.setVisible(not state)
        self._empty_state.setVisible(state)

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def set_filter(self, key: str):
        self._active_filter = key
        self._apply_filters()

    def set_sort(self, key: str, ascending: bool = True):
        self._active_sort = key
        self._sort_asc    = ascending
        self._apply_filters()

    def set_search(self, text: str):
        self._search_text = text
        self._apply_filters()

    def get_filtered_count(self) -> int:
        return len(self._filtered)

    def get_filtered_size(self) -> int:
        return sum(
            p.get("size_bytes", 0) for p in self._filtered
        )

    def get_total_size_str(self) -> str:
        total = self.get_filtered_size()
        if total >= 1_073_741_824:
            return f"{total / 1_073_741_824:.1f} Go"
        if total >= 1_048_576:
            return f"{total / 1_048_576:.1f} Mo"
        return f"{total / 1024:.1f} Ko"