from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from ui.theme import Colors, Fonts, Dimensions


FOLDERS_STYLE = f"""
    QWidget#folders_page {{
        background: {Colors.BG_APP};
    }}

    QScrollArea {{
        background: {Colors.BG_APP};
        border: none;
    }}
    QScrollArea > QWidget > QWidget {{
        background: {Colors.BG_APP};
    }}

    /* Titre de page */
    QLabel#page_title {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_XL}px;
        font-weight: 700;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#page_subtitle {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    /* Carte dossier */
    QWidget#folder_card {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_XL}px;
    }}
    QWidget#folder_card:hover {{
        border-color: {Colors.ACCENT};
        background: {Colors.BG_HOVER};
    }}

    /* Icône dossier */
    QWidget#folder_icon {{
        background: {Colors.ACCENT_LIGHT};
        border-radius: {Dimensions.RADIUS_LG}px;
    }}

    /* Infos dossier */
    QLabel#folder_path {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_LG}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#folder_meta {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    /* Stats pills */
    QLabel#stat_pill {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: 12px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        padding: 3px 10px;
    }}

    /* Bouton supprimer */
    QPushButton#delete_btn {{
        background: {Colors.DANGER_BG};
        border: 1px solid {Colors.DANGER_BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.DANGER_TEXT};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 5px 10px;
    }}
    QPushButton#delete_btn:hover {{
        background: #ffe0e0;
        border-color: {Colors.ERROR};
    }}

    /* Bouton scanner */
    QPushButton#scan_btn {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 5px 10px;
    }}
    QPushButton#scan_btn:hover {{
        border-color: {Colors.ACCENT};
        color: {Colors.ACCENT};
    }}

    /* Carte ajouter */
    QWidget#add_card {{
        background: {Colors.BG_WHITE};
        border: 2px dashed {Colors.ACCENT_BORDER};
        border-radius: {Dimensions.RADIUS_XL}px;
    }}
    QWidget#add_card:hover {{
        background: {Colors.ACCENT_LIGHT};
        border-color: {Colors.ACCENT};
    }}
    QLabel#add_label {{
        color: {Colors.ACCENT};
        font-size: {Fonts.SIZE_LG}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""


class StatPill(QLabel):
    """Badge de stat (ex: 🎮 3 Jeux)."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("stat_pill")


class FolderCard(QWidget):
    """
    Carte représentant un dossier scanné.

    Signaux :
        scan_requested(path)    → rescan demandé
        delete_requested(path)  → suppression demandée
    """

    scan_requested   = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, folder_path: str, stats: dict = None, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.stats       = stats or {}
        self.setObjectName("folder_card")
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(16)

        # Icône
        icon_widget = QWidget()
        icon_widget.setObjectName("folder_icon")
        icon_widget.setFixedSize(48, 48)
        icon_layout = QVBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel("📁")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(
            "font-size: 24px; background: transparent;"
        )
        icon_layout.addWidget(icon_lbl)
        layout.addWidget(icon_widget)

        # Infos
        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        # Chemin
        path_lbl = QLabel(self.folder_path)
        path_lbl.setObjectName("folder_path")
        info_col.addWidget(path_lbl)

        # Meta
        total = self.stats.get("total", 0)
        size  = self.stats.get("size_str", "—")
        date  = self.stats.get("date_added", "")
        meta  = f"{total} fichier{'s' if total > 1 else ''} · {size}"
        if date:
            meta += f" · Ajouté le {date[:10]}"
        meta_lbl = QLabel(meta)
        meta_lbl.setObjectName("folder_meta")
        info_col.addWidget(meta_lbl)

        # Stats pills
        pills_row = QHBoxLayout()
        pills_row.setSpacing(6)
        pills_row.setContentsMargins(0, 4, 0, 0)

        pill_data = [
            ("🎮", "Jeux",      self.stats.get("game",     0)),
            ("🧩", "DLC",       self.stats.get("dlc",      0)),
            ("⬆",  "Updates",   self.stats.get("update",   0)),
            ("⏮",  "Backports", self.stats.get("backport", 0)),
        ]
        for icon, label, count in pill_data:
            pill = StatPill(f"{icon} {count} {label}")
            pills_row.addWidget(pill)
        pills_row.addStretch()
        info_col.addLayout(pills_row)

        layout.addLayout(info_col, 1)

        # Boutons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        btn_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        scan_btn = QPushButton("🔄  Rescanner")
        scan_btn.setObjectName("scan_btn")
        scan_btn.setFixedHeight(30)
        scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        scan_btn.clicked.connect(
            lambda: self.scan_requested.emit(self.folder_path)
        )

        del_btn = QPushButton("🗑️  Retirer")
        del_btn.setObjectName("delete_btn")
        del_btn.setFixedHeight(30)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(
            lambda: self.delete_requested.emit(self.folder_path)
        )

        btn_col.addWidget(scan_btn)
        btn_col.addWidget(del_btn)
        layout.addLayout(btn_col)

    def update_stats(self, stats: dict):
        """Met à jour les stats affichées."""
        self.stats = stats
        # Recrée l'UI
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._build_ui()


class AddFolderCard(QWidget):
    """Carte pour ajouter un nouveau dossier."""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("add_card")
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        icon = QLabel("➕")
        icon.setStyleSheet("font-size: 20px; background: transparent;")

        lbl = QLabel("Ajouter un dossier PKG")
        lbl.setObjectName("add_label")

        layout.addWidget(icon)
        layout.addWidget(lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class FoldersPage(QWidget):
    """
    Page de gestion des dossiers.

    Signaux :
        add_requested()          → ajouter un dossier
        scan_requested(path)     → rescanner un dossier
        delete_requested(path)   → supprimer un dossier
    """

    add_requested    = pyqtSignal()
    scan_requested   = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("folders_page")
        self.setStyleSheet(FOLDERS_STYLE)

        self._folder_cards = {}
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setStyleSheet(f"background: {Colors.BG_APP};")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(24, 24, 24, 24)
        self._content_layout.setSpacing(12)

        # En-tête
        self._content_layout.addWidget(self._make_header())
        self._content_layout.addSpacing(8)

        # Zone des cartes dossier
        self._cards_layout = QVBoxLayout()
        self._cards_layout.setSpacing(10)
        self._content_layout.addLayout(self._cards_layout)

        # Carte Ajouter
        add_card = AddFolderCard()
        add_card.clicked.connect(self.add_requested.emit)
        self._content_layout.addWidget(add_card)
        self._content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _make_header(self) -> QWidget:
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        v = QVBoxLayout(header)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        title = QLabel("Dossiers")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "Gérez les dossiers contenant vos fichiers PKG. "
            "PKGVault scanne automatiquement tous les sous-dossiers."
        )
        subtitle.setObjectName("page_subtitle")
        subtitle.setWordWrap(True)

        v.addWidget(title)
        v.addWidget(subtitle)
        return header

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def set_folders(self, folders: list[str], stats: dict = None):
        """
        Met à jour la liste des dossiers affichés.
        stats = { path: { game, dlc, update, backport, total, size_str } }
        """
        stats = stats or {}

        # Vide les cartes existantes
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._folder_cards.clear()

        if not folders:
            empty = QLabel("Aucun dossier ajouté pour l'instant.")
            empty.setStyleSheet(
                f"color: {Colors.TEXT_HINT}; font-size: {Fonts.SIZE_MD}px;"
                f"background: transparent;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._cards_layout.addWidget(empty)
            return

        for path in folders:
            card = FolderCard(path, stats.get(path, {}))
            card.scan_requested.connect(self.scan_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)
            self._cards_layout.addWidget(card)
            self._folder_cards[path] = card

    def update_folder_stats(self, path: str, stats: dict):
        """Met à jour les stats d'un dossier spécifique."""
        if path in self._folder_cards:
            self._folder_cards[path].update_stats(stats)