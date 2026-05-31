from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QScrollArea,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme import Colors, Fonts, Dimensions


SETTINGS_STYLE = f"""
    QWidget#settings_page {{
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

    /* Section */
    QWidget#settings_section {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_XL}px;
    }}
    QWidget#section_header {{
        background: transparent;
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
    }}
    QLabel#section_title {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_LG}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#section_icon {{
        font-size: 18px;
        background: transparent;
    }}

    /* Ligne de paramètre */
    QWidget#settings_row {{
        background: transparent;
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
    }}
    QLabel#row_label {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#row_desc {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    /* Input */
    QLineEdit#settings_input {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 5px 11px;
        min-width: 220px;
    }}
    QLineEdit#settings_input:focus {{
        border-color: {Colors.ACCENT};
    }}

    /* Combobox */
    QComboBox#settings_combo {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 5px 10px;
        min-width: 180px;
    }}
    QComboBox#settings_combo:hover {{
        border-color: {Colors.ACCENT};
    }}
    QComboBox#settings_combo::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox#settings_combo QAbstractItemView {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        selection-background-color: {Colors.ACCENT_LIGHT};
        color: {Colors.TEXT_PRIMARY};
        padding: 4px;
    }}

    /* Toggle */
    QPushButton#toggle_on {{
        background: {Colors.ACCENT};
        border: none;
        border-radius: 11px;
        min-width: 40px;
        max-width: 40px;
        min-height: 22px;
        max-height: 22px;
    }}
    QPushButton#toggle_off {{
        background: {Colors.BORDER};
        border: none;
        border-radius: 11px;
        min-width: 40px;
        max-width: 40px;
        min-height: 22px;
        max-height: 22px;
    }}

    /* Boutons */
    QPushButton#primary_btn {{
        background: {Colors.ACCENT};
        border: none;
        border-radius: {Dimensions.RADIUS_MD}px;
        color: #ffffff;
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 8px 20px;
        font-weight: 500;
    }}
    QPushButton#primary_btn:hover {{
        background: {Colors.ACCENT_HOVER};
    }}
    QPushButton#secondary_btn {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 7px 14px;
    }}
    QPushButton#secondary_btn:hover {{
        border-color: {Colors.ACCENT};
        color: {Colors.ACCENT};
    }}
    QPushButton#danger_btn {{
        background: {Colors.DANGER_BG};
        border: 1px solid {Colors.DANGER_BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.DANGER_TEXT};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 7px 14px;
    }}
    QPushButton#danger_btn:hover {{
        background: #ffe0e0;
        border-color: {Colors.ERROR};
    }}
    QPushButton#test_btn {{
        background: {Colors.ACCENT_LIGHT};
        border: 1px solid {Colors.ACCENT_BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.ACCENT};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 5px 12px;
    }}
    QPushButton#test_btn:hover {{
        background: {Colors.ACCENT};
        color: #ffffff;
    }}
"""


class Toggle(QPushButton):
    """Bouton toggle on/off."""

    toggled_state = pyqtSignal(bool)

    def __init__(self, initial: bool = True, parent=None):
        super().__init__(parent)
        self._state = initial
        self._update_style()
        self.clicked.connect(self._on_click)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _update_style(self):
        self.setObjectName("toggle_on" if self._state else "toggle_off")
        self.setText("●" if self._state else "○")
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_click(self):
        self._state = not self._state
        self._update_style()
        self.toggled_state.emit(self._state)

    @property
    def is_on(self) -> bool:
        return self._state

    def set_state(self, state: bool):
        self._state = state
        self._update_style()


class SettingsRow(QWidget):
    """Ligne de paramètre avec label + description + contrôle."""

    def __init__(
        self,
        label: str,
        description: str = "",
        control: QWidget = None,
        last: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("settings_row" if not last else "")
        if not last:
            self.setStyleSheet(
                f"border-bottom: 1px solid {Colors.BORDER_LIGHT};"
            )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(16)

        # Textes
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        lbl = QLabel(label)
        lbl.setObjectName("row_label")
        text_col.addWidget(lbl)

        if description:
            desc = QLabel(description)
            desc.setObjectName("row_desc")
            text_col.addWidget(desc)

        layout.addLayout(text_col, 1)

        # Contrôle
        if control:
            layout.addWidget(control)


class SettingsSection(QWidget):
    """Section de paramètres avec titre."""

    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_section")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("section_header")
        header.setFixedHeight(48)
        h = QHBoxLayout(header)
        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("section_icon")

        title_lbl = QLabel(title)
        title_lbl.setObjectName("section_title")

        h.addWidget(icon_lbl)
        h.addWidget(title_lbl)
        h.addStretch()

        self._layout.addWidget(header)

    def add_row(self, row: QWidget):
        self._layout.addWidget(row)


class SettingsPage(QWidget):
    """
    Page de paramètres.

    Signaux :
        settings_saved(data)   → paramètres sauvegardés
        cache_clear_requested  → vider le cache
        db_reset_requested     → réinitialiser la BDD
    """

    settings_saved       = pyqtSignal(dict)
    cache_clear_requested = pyqtSignal()
    db_reset_requested    = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_page")
        self.setStyleSheet(SETTINGS_STYLE)
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setStyleSheet(f"background: {Colors.BG_APP};")
        self._content = QVBoxLayout(content)
        self._content.setContentsMargins(24, 24, 24, 24)
        self._content.setSpacing(16)

        # En-tête
        self._content.addWidget(self._make_header())
        self._content.addSpacing(4)

        # Sections
        self._content.addWidget(self._make_api_section())
        self._content.addWidget(self._make_display_section())
        self._content.addWidget(self._make_data_section())

        # Bouton sauvegarder
        save_row = QHBoxLayout()
        save_btn = QPushButton("💾  Sauvegarder les paramètres")
        save_btn.setObjectName("primary_btn")
        save_btn.setFixedHeight(38)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        save_row.addWidget(save_btn)
        save_row.addStretch()
        self._content.addLayout(save_row)
        self._content.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _make_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        title = QLabel("Paramètres")
        title.setObjectName("page_title")

        sub = QLabel(
            "Configurez PS4 PKGVault selon vos préférences."
        )
        sub.setObjectName("page_subtitle")

        v.addWidget(title)
        v.addWidget(sub)
        return w

    def _make_api_section(self) -> QWidget:
        section = SettingsSection("🔌", "APIs & Données")

        # RAWG
        rawg_wrap = QHBoxLayout()
        rawg_wrap.setSpacing(6)
        self._rawg_input = QLineEdit()
        self._rawg_input.setObjectName("settings_input")
        self._rawg_input.setPlaceholderText("Votre clé RAWG.io…")
        self._rawg_input.setFixedHeight(32)
        rawg_test = QPushButton("Tester")
        rawg_test.setObjectName("test_btn")
        rawg_test.setFixedHeight(32)
        rawg_test.setCursor(Qt.CursorShape.PointingHandCursor)
        rawg_test.clicked.connect(self._on_test_rawg)
        rawg_wrap.addWidget(self._rawg_input)
        rawg_wrap.addWidget(rawg_test)
        rawg_widget = QWidget()
        rawg_widget.setStyleSheet("background: transparent;")
        rawg_widget.setLayout(rawg_wrap)
        section.add_row(SettingsRow(
            "Clé API RAWG.io",
            "Descriptions, genres, ratings et screenshots · rawg.io/apidocs",
            rawg_widget
        ))

        # IGDB
        igdb_wrap = QHBoxLayout()
        igdb_wrap.setSpacing(6)
        self._igdb_input = QLineEdit()
        self._igdb_input.setObjectName("settings_input")
        self._igdb_input.setPlaceholderText("Twitch Client ID…")
        self._igdb_input.setFixedHeight(32)
        igdb_wrap.addWidget(self._igdb_input)
        igdb_widget = QWidget()
        igdb_widget.setStyleSheet("background: transparent;")
        igdb_widget.setLayout(igdb_wrap)
        section.add_row(SettingsRow(
            "Clé API IGDB",
            "Vidéos et artworks · dev.twitch.tv (gratuit)",
            igdb_widget
        ))

        # Auto-fetch
        self._auto_fetch_toggle = Toggle(True)
        section.add_row(SettingsRow(
            "Téléchargement automatique",
            "Lance la récupération API après chaque scan",
            self._auto_fetch_toggle,
            last=True
        ))

        return section

    def _make_display_section(self) -> QWidget:
        section = SettingsSection("🎨", "Affichage")

        # Colonnes
        self._cols_combo = QComboBox()
        self._cols_combo.setObjectName("settings_combo")
        self._cols_combo.addItems([
            "4 colonnes (défaut)",
            "3 colonnes (grandes cartes)",
            "5 colonnes (petites cartes)",
            "6 colonnes (mini cartes)",
        ])
        self._cols_combo.setFixedHeight(32)
        section.add_row(SettingsRow(
            "Taille des cartes",
            "Nombre de colonnes dans la grille",
            self._cols_combo
        ))

        # Langue
        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("settings_combo")
        self._lang_combo.addItems([
            "Français",
            "English",
            "Español",
            "Deutsch",
        ])
        self._lang_combo.setFixedHeight(32)
        section.add_row(SettingsRow(
            "Langue de l'interface",
            "Redémarrage requis pour appliquer",
            self._lang_combo
        ))

        # Thème
        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("settings_combo")
        self._theme_combo.addItems([
            "Clair (Windows 11)",
            "Sombre",
            "Automatique (système)",
        ])
        self._theme_combo.setFixedHeight(32)
        section.add_row(SettingsRow(
            "Thème",
            "Apparence de l'interface",
            self._theme_combo,
            last=True
        ))

        return section

    def _make_data_section(self) -> QWidget:
        section = SettingsSection("🗄️", "Base de données & Cache")

        # Cache info
        cache_wrap = QHBoxLayout()
        cache_wrap.setSpacing(8)
        self._cache_info = QLabel("cache/covers/ · 0 fichiers")
        self._cache_info.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: {Fonts.SIZE_MD}px;"
            f"background: transparent;"
        )
        clear_btn = QPushButton("🗑️  Vider")
        clear_btn.setObjectName("danger_btn")
        clear_btn.setFixedHeight(30)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.cache_clear_requested.emit)
        cache_wrap.addWidget(self._cache_info)
        cache_wrap.addStretch()
        cache_wrap.addWidget(clear_btn)
        cache_widget = QWidget()
        cache_widget.setStyleSheet("background: transparent;")
        cache_widget.setLayout(cache_wrap)
        section.add_row(SettingsRow(
            "Cache des jaquettes",
            "Jaquettes téléchargées depuis PS Store et RAWG",
            cache_widget
        ))

        # Reset BDD
        reset_btn = QPushButton("⚠️  Réinitialiser")
        reset_btn.setObjectName("danger_btn")
        reset_btn.setFixedHeight(30)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self.db_reset_requested.emit)
        section.add_row(SettingsRow(
            "Réinitialiser la base de données",
            "Supprime tous les jeux indexés — les fichiers PKG ne sont pas affectés",
            reset_btn,
            last=True
        ))

        return section

    # ------------------------------------------------------------------ #
    #  Slots                                                               #
    # ------------------------------------------------------------------ #

    def _on_save(self):
        data = {
            "rawg_api_key":  self._rawg_input.text().strip(),
            "igdb_client_id": self._igdb_input.text().strip(),
            "auto_fetch":    self._auto_fetch_toggle.is_on,
            "card_cols":     self._cols_combo.currentIndex() + 3,
            "language":      self._lang_combo.currentText(),
            "theme":         self._theme_combo.currentText(),
        }
        self.settings_saved.emit(data)

    def _on_test_rawg(self):
        key = self._rawg_input.text().strip()
        if not key:
            return
        print(f"Test RAWG avec clé : {key[:8]}…")

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def load_settings(self, data: dict):
        """Charge les paramètres existants dans les contrôles."""
        if data.get("rawg_api_key"):
            self._rawg_input.setText(data["rawg_api_key"])
        if data.get("igdb_client_id"):
            self._igdb_input.setText(data["igdb_client_id"])
        if "auto_fetch" in data:
            self._auto_fetch_toggle.set_state(data["auto_fetch"])
        cols = data.get("card_cols", 4)
        self._cols_combo.setCurrentIndex(max(0, cols - 3))
        if data.get("language"):
            idx = self._lang_combo.findText(data["language"])
            if idx >= 0:
                self._lang_combo.setCurrentIndex(idx)

    def update_cache_info(self, count: int, size_str: str):
        """Met à jour l'info du cache."""
        self._cache_info.setText(
            f"cache/covers/ · {count} fichiers · {size_str}"
        )