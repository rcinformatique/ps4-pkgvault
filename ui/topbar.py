from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.theme import Colors, Dimensions, Fonts


TOPBAR_STYLE = f"""
    QWidget#topbar {{
        background-color: {Colors.BG_WHITE};
        border-bottom: 1px solid {Colors.BORDER};
    }}

    /* Logo */
    QLabel#logo {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_XL}px;
        font-weight: 700;
        font-family: {Fonts.FAMILY};
    }}

    /* Onglets */
    QPushButton#tab_btn {{
        background: transparent;
        border: none;
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 6px 13px;
    }}
    QPushButton#tab_btn:hover {{
        background: {Colors.BG_INPUT};
        color: {Colors.TEXT_SECONDARY};
    }}
    QPushButton#tab_btn[active=true] {{
        background: {Colors.ACCENT_LIGHT};
        color: {Colors.ACCENT};
        font-weight: 600;
    }}

    /* Recherche */
    QWidget#search_wrap {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER_STRONG};
        border-radius: 20px;
    }}
    QLineEdit#search_input {{
        background: transparent;
        border: none;
        border-radius: 20px;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 0px;
    }}
    QLineEdit#search_input:focus {{
        border: none;
    }}

    /* Bouton Ajouter */
    QPushButton#add_btn {{
        background: {Colors.ACCENT};
        border: none;
        border-radius: {Dimensions.RADIUS_MD}px;
        color: #ffffff;
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 6px 14px;
        font-weight: 500;
    }}
    QPushButton#add_btn:hover {{
        background: {Colors.ACCENT_HOVER};
    }}
    QPushButton#add_btn:pressed {{
        background: #004f9a;
    }}

    /* Boutons icône */
    QPushButton#icon_btn {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_LG}px;
        padding: 0px;
    }}
    QPushButton#icon_btn:hover {{
        background: {Colors.ACCENT_LIGHT};
        color: {Colors.ACCENT};
        border-color: {Colors.ACCENT_BORDER};
    }}
"""


class TabButton(QPushButton):
    """Bouton onglet de la topbar."""

    def __init__(self, icon: str, label: str, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.setObjectName("tab_btn")
        self.setText(f"{icon}  {label}")
        self.setFixedHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )
        self._active = False

    def set_active(self, state: bool):
        self._active = state
        self.setProperty("active", state)
        self.style().unpolish(self)
        self.style().polish(self)


class Topbar(QWidget):
    """
    Barre de navigation principale.

    Signaux :
        tab_changed(key)      → onglet cliqué
        search_changed(text)  → texte de recherche modifié
        add_requested()       → bouton Ajouter cliqué
        view_toggled()        → toggle grille/liste
    """

    tab_changed    = pyqtSignal(str)
    search_changed = pyqtSignal(str)
    add_requested  = pyqtSignal()
    view_toggled   = pyqtSignal()

    # Onglets : (icône, label, clé de page)
    TABS = [
        ("🗂️",  "Bibliothèque", "library"),
        ("📁",  "Dossiers",     "folders"),
        ("⚙️",  "Paramètres",   "settings"),
        ("ℹ️",  "À propos",     "credits"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(Dimensions.TOPBAR_HEIGHT)
        self.setStyleSheet(TOPBAR_STYLE)

        self._tab_buttons  = {}
        self._active_tab   = "library"

        self._build_ui()
        self._set_active_tab("library")

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(8)

        # Logo
        layout.addWidget(self._make_logo())
        layout.addSpacing(8)

        # Onglets
        for icon, label, key in self.TABS:
            btn = TabButton(icon, label, key)
            btn.clicked.connect(
                lambda checked, k=key: self._on_tab_click(k)
            )
            self._tab_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Recherche
        layout.addWidget(self._make_search())
        layout.addSpacing(6)

        # Bouton Ajouter
        add_btn = QPushButton("➕  Ajouter un dossier")
        add_btn.setObjectName("add_btn")
        add_btn.setFixedHeight(32)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_requested.emit)
        layout.addWidget(add_btn)
        layout.addSpacing(4)

        # Bouton vue liste/grille
        view_btn = QPushButton("☰")
        view_btn.setObjectName("icon_btn")
        view_btn.setFixedSize(32, 32)
        view_btn.setToolTip("Basculer vue liste / grille")
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.clicked.connect(self.view_toggled.emit)
        layout.addWidget(view_btn)

    def _make_logo(self) -> QWidget:
        """Logo PS4 PKGVault."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        h = QHBoxLayout(widget)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        ps4 = QLabel("PS4 PKG")
        ps4.setObjectName("logo")
        ps4_font = QFont(Fonts.FAMILY, Fonts.SIZE_XL, QFont.Weight.Bold)
        ps4.setFont(ps4_font)
        ps4.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; background: transparent;")

        vault = QLabel("Vault")
        vault.setObjectName("logo")
        vault_font = QFont(Fonts.FAMILY, Fonts.SIZE_XL, QFont.Weight.Bold)
        vault.setFont(vault_font)
        vault.setStyleSheet(f"color: {Colors.ACCENT}; background: transparent;")

        h.addWidget(ps4)
        h.addWidget(vault)
        return widget

    def _make_search(self) -> QWidget:
        """Champ de recherche."""
        wrap = QWidget()
        wrap.setObjectName("search_wrap")
        wrap.setFixedSize(200, 32)

        h = QHBoxLayout(wrap)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(6)

        icon = QLabel("🔍")
        icon.setStyleSheet(
            f"background: transparent; font-size: 13px; color: {Colors.TEXT_HINT};"
        )

        self._search_input = QLineEdit()
        self._search_input.setObjectName("search_input")
        self._search_input.setPlaceholderText("Rechercher…")
        self._search_input.textChanged.connect(self.search_changed.emit)

        h.addWidget(icon)
        h.addWidget(self._search_input)
        return wrap

    # ------------------------------------------------------------------ #
    #  Interactions                                                        #
    # ------------------------------------------------------------------ #

    def _on_tab_click(self, key: str):
        self._set_active_tab(key)
        self.tab_changed.emit(key)

    def _set_active_tab(self, key: str):
        if self._active_tab in self._tab_buttons:
            self._tab_buttons[self._active_tab].set_active(False)
        self._active_tab = key
        if key in self._tab_buttons:
            self._tab_buttons[key].set_active(True)

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def set_active_tab(self, key: str):
        """Active un onglet depuis l'extérieur."""
        self._set_active_tab(key)

    def get_search_text(self) -> str:
        return self._search_input.text()

    def clear_search(self):
        self._search_input.clear()