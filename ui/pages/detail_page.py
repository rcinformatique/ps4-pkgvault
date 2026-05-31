import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from ui.theme import Colors, Fonts, Dimensions, PKG_TYPES


DETAIL_STYLE = f"""
    QWidget#detail_page {{
        background: {Colors.BG_APP};
    }}

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

    QWidget#hero_widget {{
        background: {Colors.BG_WHITE};
        border-bottom: 1px solid {Colors.BORDER_LIGHT};
    }}

    QLabel#game_title {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_XXL}px;
        font-weight: 700;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#game_subtitle {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_LG}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#dev_label {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#rating_label {{
        color: {Colors.WARNING};
        font-size: {Fonts.SIZE_LG}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#quick_info {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    QPushButton#act_primary {{
        background: {Colors.ACCENT};
        border: none;
        border-radius: {Dimensions.RADIUS_MD}px;
        color: #ffffff;
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 7px 16px;
        font-weight: 500;
    }}
    QPushButton#act_primary:hover {{
        background: {Colors.ACCENT_HOVER};
    }}
    QPushButton#act_secondary {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 7px 13px;
    }}
    QPushButton#act_secondary:hover {{
        border-color: {Colors.ACCENT};
        color: {Colors.ACCENT};
    }}

    QWidget#section_card {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_LG}px;
    }}
    QLabel#section_label {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-weight: 700;
        font-family: {Fonts.FAMILY};
        letter-spacing: 1px;
        background: transparent;
    }}

    QLabel#description {{
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    QLabel#info_key {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#info_val {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-weight: 500;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    QScrollArea {{
        background: {Colors.BG_APP};
        border: none;
    }}
    QScrollArea > QWidget > QWidget {{
        background: {Colors.BG_APP};
    }}
"""


class InfoRow(QWidget):
    def __init__(self, key: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(12)

        self._key = QLabel(key)
        self._key.setObjectName("info_key")
        self._key.setFixedWidth(110)
        self._key.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        self._val = QLabel(value or "—")
        self._val.setObjectName("info_val")
        self._val.setWordWrap(True)

        layout.addWidget(self._key)
        layout.addWidget(self._val, 1)

    def set_value(self, value: str):
        self._val.setText(value or "—")


class SectionCard(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("section_card")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 16)
        self._layout.setSpacing(10)

        lbl = QLabel(title.upper())
        lbl.setObjectName("section_label")
        self._layout.addWidget(lbl)

    def add_widget(self, widget: QWidget):
        self._layout.addWidget(widget)

    def add_layout(self, layout):
        self._layout.addLayout(layout)


class TagBadge(QLabel):
    def __init__(self, text: str, bg: str, color: str,
                 border: str = "", parent=None):
        super().__init__(text, parent)
        border_css = f"border: 1px solid {border};" if border else ""
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {color};
                {border_css}
                border-radius: 12px;
                font-size: {Fonts.SIZE_SM}px;
                padding: 3px 10px;
                font-family: {Fonts.FAMILY};
            }}
        """)


class RelationItem(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, pkg_data: dict, parent=None):
        super().__init__(parent)
        self.pkg_data = pkg_data
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BG_ROW_ALT};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: {Dimensions.RADIUS_MD}px;
            }}
            QWidget:hover {{
                border-color: {Colors.ACCENT};
                background: {Colors.ACCENT_LIGHT};
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        pkg_type = self.pkg_data.get("type", "game")
        info     = PKG_TYPES.get(pkg_type, PKG_TYPES["game"])

        icon = QLabel(info["icon"])
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"""
            background: {info['bg']};
            border-radius: 6px;
            font-size: 16px;
        """)
        layout.addWidget(icon)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        title = QLabel(self.pkg_data.get("title", ""))
        title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: {Fonts.SIZE_MD}px;
            font-weight: 500;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)

        badge = QLabel(info["label"])
        badge.setStyleSheet(f"""
            color: {info['badge']};
            font-size: {Fonts.SIZE_SM}px;
            font-weight: 700;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)

        info_col.addWidget(title)
        info_col.addWidget(badge)
        layout.addLayout(info_col, 1)

        size = QLabel(self.pkg_data.get("size_str", ""))
        size.setStyleSheet(f"""
            color: {Colors.TEXT_HINT};
            font-size: {Fonts.SIZE_SM}px;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)
        layout.addWidget(size)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.pkg_data)


class ScreenshotItem(QLabel):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 90)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            background: {Colors.BG_INPUT};
            border: 1px solid {Colors.BORDER};
            border-radius: {Dimensions.RADIUS_MD}px;
        """)
        if path and Path(path).exists():
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    160, 90,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled)
        else:
            self.setText("🖼️")
            self.setStyleSheet(
                self.styleSheet() + "font-size: 24px;"
            )


class DetailPage(QWidget):
    """
    Page de détail complète d'un PKG.

    Signaux :
        back_requested()         → retour à la bibliothèque
        relation_clicked(data)   → clic sur contenu associé
    """

    back_requested   = pyqtSignal()
    relation_clicked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detail_page")
        self.setStyleSheet(DETAIL_STYLE)

        self._current_pkg  = {}
        self._related_pkgs = []

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._make_back_bar())
        layout.addWidget(self._make_hero())

        # Scroll principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        body = QWidget()
        body.setStyleSheet(f"background: {Colors.BG_APP};")
        body_h = QHBoxLayout(body)
        body_h.setContentsMargins(
            Dimensions.PADDING_LG,
            Dimensions.PADDING_LG,
            Dimensions.PADDING_LG,
            Dimensions.PADDING_LG
        )
        body_h.setSpacing(16)

        # Colonne principale
        main_widget = QWidget()
        main_widget.setStyleSheet("background: transparent;")
        self._main_col = QVBoxLayout(main_widget)
        self._main_col.setContentsMargins(0, 0, 0, 0)
        self._main_col.setSpacing(14)
        body_h.addWidget(main_widget, 1)

        # Colonne aside — largeur fixe
        self._aside_widget = QWidget()
        self._aside_widget.setFixedWidth(240)
        self._aside_widget.setStyleSheet("background: transparent;")
        self._aside_col = QVBoxLayout(self._aside_widget)
        self._aside_col.setContentsMargins(0, 0, 0, 0)
        self._aside_col.setSpacing(12)
        body_h.addWidget(self._aside_widget)

        scroll.setWidget(body)
        layout.addWidget(scroll)

    def _make_back_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("back_bar")
        bar.setFixedHeight(Dimensions.BACK_BAR_HEIGHT)

        h = QHBoxLayout(bar)
        h.setContentsMargins(18, 0, 18, 0)
        h.setSpacing(10)

        back_btn = QPushButton("← Retour")
        back_btn.setObjectName("back_btn")
        back_btn.setFixedHeight(30)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.back_requested.emit)
        h.addWidget(back_btn)

        self._breadcrumb = QLabel("Bibliothèque")
        self._breadcrumb.setStyleSheet(
            f"color: {Colors.TEXT_HINT}; font-size: {Fonts.SIZE_MD}px;"
            f"background: transparent;"
        )
        h.addWidget(self._breadcrumb)
        h.addStretch()

        self._header_badge = QLabel()
        self._header_badge.setStyleSheet(f"""
            color: {Colors.TEXT_HINT};
            font-size: {Fonts.SIZE_SM}px;
            padding: 2px 8px;
            border: 1px solid {Colors.BORDER};
            border-radius: 4px;
            background: transparent;
        """)
        h.addWidget(self._header_badge)

        return bar

    def _make_hero(self) -> QWidget:
        hero = QWidget()
        hero.setObjectName("hero_widget")

        h = QHBoxLayout(hero)
        h.setContentsMargins(
            Dimensions.PADDING_XL,
            Dimensions.PADDING_XL,
            Dimensions.PADDING_XL,
            Dimensions.PADDING_LG
        )
        h.setSpacing(28)

        # Jaquette
        self._cover_label = QLabel()
        self._cover_label.setFixedSize(160, 214)
        self._cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_label.setStyleSheet(f"""
            background: {Colors.BG_APP};
            border-radius: {Dimensions.RADIUS_LG}px;
            border: 1px solid {Colors.BORDER};
            font-size: 52px;
        """)
        h.addWidget(self._cover_label, 0, Qt.AlignmentFlag.AlignTop)

        # Infos droite
        right = QVBoxLayout()
        right.setSpacing(6)

        # Badge type
        self._type_badge = QLabel()
        self._type_badge.setFixedHeight(24)
        self._type_badge.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )
        right.addWidget(self._type_badge)
        right.addSpacing(4)

        # Titre
        self._title_label = QLabel()
        self._title_label.setObjectName("game_title")
        self._title_label.setWordWrap(True)
        right.addWidget(self._title_label)

        # Sous-titre
        self._subtitle_label = QLabel()
        self._subtitle_label.setObjectName("game_subtitle")
        self._subtitle_label.setWordWrap(True)
        right.addWidget(self._subtitle_label)
        right.addSpacing(6)

        # Infos rapides
        quick_row = QHBoxLayout()
        quick_row.setSpacing(16)

        self._rating_label = QLabel()
        self._rating_label.setObjectName("rating_label")

        self._date_label = QLabel()
        self._date_label.setObjectName("quick_info")

        self._fw_label = QLabel()
        self._fw_label.setObjectName("quick_info")

        self._ver_label = QLabel()
        self._ver_label.setObjectName("quick_info")

        for lbl in [
            self._rating_label,
            self._date_label,
            self._fw_label,
            self._ver_label,
        ]:
            quick_row.addWidget(lbl)
        quick_row.addStretch()
        right.addLayout(quick_row)
        right.addSpacing(4)

        # Dev / Publisher
        self._dev_label = QLabel()
        self._dev_label.setObjectName("dev_label")
        right.addWidget(self._dev_label)
        right.addSpacing(12)

        # Actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        self._btn_open = QPushButton("📁  Ouvrir le dossier")
        self._btn_open.setObjectName("act_primary")
        self._btn_open.setFixedHeight(34)
        self._btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_open.clicked.connect(self._on_open_folder)

        self._btn_copy_path = QPushButton("📋  Copier le chemin")
        self._btn_copy_path.setObjectName("act_secondary")
        self._btn_copy_path.setFixedHeight(34)
        self._btn_copy_path.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_path.clicked.connect(self._on_copy_path)

        self._btn_copy_cid = QPushButton("🔑  Copier le CUSA")
        self._btn_copy_cid.setObjectName("act_secondary")
        self._btn_copy_cid.setFixedHeight(34)
        self._btn_copy_cid.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy_cid.clicked.connect(self._on_copy_cid)

        self._btn_more = QPushButton("•••")
        self._btn_more.setObjectName("act_secondary")
        self._btn_more.setFixedSize(34, 34)
        self._btn_more.setCursor(Qt.CursorShape.PointingHandCursor)

        for btn in [
            self._btn_open,
            self._btn_copy_path,
            self._btn_copy_cid,
            self._btn_more,
        ]:
            actions_row.addWidget(btn)
        actions_row.addStretch()

        right.addLayout(actions_row)
        right.addStretch()

        h.addLayout(right, 1)
        return hero

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def show_pkg(self, pkg_data: dict, related: list = None):
        self._current_pkg  = pkg_data
        self._related_pkgs = related or []
        self._populate_hero()
        self._populate_body()

    def set_cover_pixmap(self, pixmap: QPixmap):
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(
                160, 214,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._cover_label.setPixmap(scaled)
            self._cover_label.setText("")

    def update_cover(self, cover_path: str):
        if Path(cover_path).exists():
            self.set_cover_pixmap(QPixmap(cover_path))

    # ------------------------------------------------------------------ #
    #  Population                                                          #
    # ------------------------------------------------------------------ #

    def _populate_hero(self):
        pkg_type = self._current_pkg.get("type", "game")
        info     = PKG_TYPES.get(pkg_type, PKG_TYPES["game"])

        title = (
            self._current_pkg.get("title_api")
            or self._current_pkg.get("title")
            or "Inconnu"
        )
        self._breadcrumb.setText(f"Bibliothèque  ›  {title[:50]}")
        self._header_badge.setText(info["label"])

        # Cover placeholder
        self._cover_label.setText(info["icon"])
        self._cover_label.setPixmap(QPixmap())
        self._cover_label.setStyleSheet(f"""
            background: {info['bg']};
            border-radius: {Dimensions.RADIUS_LG}px;
            border: 1px solid {Colors.BORDER};
            font-size: 52px;
        """)

        cover_path = self._current_pkg.get("cover_path", "")
        if cover_path and Path(cover_path).exists():
            self.set_cover_pixmap(QPixmap(cover_path))

        # Badge type
        self._type_badge.setText(info["label"])
        self._type_badge.setStyleSheet(f"""
            background: {info['bg']};
            color: {info['badge']};
            border: 1px solid {info['badge']}44;
            border-radius: 5px;
            font-size: {Fonts.SIZE_SM}px;
            font-weight: 700;
            padding: 3px 10px;
            font-family: {Fonts.FAMILY};
        """)

        self._title_label.setText(title)

        title_sfo = self._current_pkg.get("title", "")
        title_api = self._current_pkg.get("title_api", "")
        if title_api and title_sfo and title_api != title_sfo:
            self._subtitle_label.setText(f"({title_sfo})")
        else:
            self._subtitle_label.setText("")

        rating = self._current_pkg.get("rating", 0)
        self._rating_label.setText(
            f"★ {rating:.1f}" if rating else ""
        )

        release = self._current_pkg.get("release_date", "")
        self._date_label.setText(
            f"📅 {release}" if release else ""
        )

        firmware = self._current_pkg.get("firmware", "")
        self._fw_label.setText(
            f"🛡 FW {firmware}"
            if firmware and firmware != "—" else ""
        )

        app_ver = self._current_pkg.get("app_ver", "")
        self._ver_label.setText(
            f"📦 v{app_ver}" if app_ver else ""
        )

        dev = self._current_pkg.get("developer", "")
        pub = self._current_pkg.get("publisher", "")
        parts = []
        if dev:
            parts.append(f"Développeur : {dev}")
        if pub and pub != dev:
            parts.append(f"Éditeur : {pub}")
        self._dev_label.setText("  ·  ".join(parts))

    def _populate_body(self):
        """Vide et reconstruit le corps de la page."""

        # Vide proprement
        self._clear_layout(self._main_col)
        self._clear_layout(self._aside_col)

        # Force le garbage collector
        import gc
        gc.collect()

        # === COLONNE PRINCIPALE ===

        # Description
        desc_card = SectionCard("Description")
        desc_text = self._current_pkg.get("description", "")
        desc_lbl = QLabel(
            desc_text if desc_text
            else "Aucune description disponible."
        )
        desc_lbl.setObjectName("description")
        desc_lbl.setWordWrap(True)
        desc_lbl.setTextFormat(Qt.TextFormat.PlainText)
        desc_card.add_widget(desc_lbl)
        self._main_col.addWidget(desc_card)

        # Genres
        genres_card = SectionCard("Genres")
        genres = self._current_pkg.get("genres", [])
        genres_wrap = QWidget()
        genres_wrap.setStyleSheet("background: transparent;")
        genres_h = QHBoxLayout(genres_wrap)
        genres_h.setContentsMargins(0, 0, 0, 0)
        genres_h.setSpacing(6)
        if genres:
            for g in genres:
                badge = TagBadge(
                    g,
                    Colors.ACCENT_LIGHT,
                    Colors.ACCENT,
                    Colors.ACCENT_BORDER
                )
                genres_h.addWidget(badge)
        else:
            empty = QLabel("—")
            empty.setStyleSheet(
                f"color: {Colors.TEXT_HINT}; background: transparent;"
            )
            genres_h.addWidget(empty)
        genres_h.addStretch()
        genres_card.add_widget(genres_wrap)
        self._main_col.addWidget(genres_card)

        # Screenshots
        screens_card = SectionCard("Screenshots")
        screenshots = self._current_pkg.get("screenshots", [])
        screens_wrap = QWidget()
        screens_wrap.setStyleSheet("background: transparent;")
        screens_h = QHBoxLayout(screens_wrap)
        screens_h.setContentsMargins(0, 0, 0, 0)
        screens_h.setSpacing(8)
        if screenshots:
            for path in screenshots[:4]:
                screens_h.addWidget(ScreenshotItem(path))
        else:
            for _ in range(4):
                screens_h.addWidget(ScreenshotItem(""))
        screens_h.addStretch()
        screens_card.add_widget(screens_wrap)
        self._main_col.addWidget(screens_card)
        self._main_col.addStretch()

        # === ASIDE ===

        # Informations techniques
        info_card = SectionCard("Informations")
        rows = [
            ("Content-ID", self._current_pkg.get("content_id", "")),
            ("Version app", self._current_pkg.get("app_ver", "")),
            ("Firmware", self._current_pkg.get("firmware", "")),
            ("Taille", self._current_pkg.get("size_str", "")),
            ("Région", self._current_pkg.get("region", "")),
            ("Catégorie SFO", self._current_pkg.get("category", "")),
            ("Fichier", self._current_pkg.get("filename", "")),
        ]
        for key, val in rows:
            row = InfoRow(key, str(val) if val else "—")
            info_card.add_widget(row)
        self._aside_col.addWidget(info_card)

        # Langues
        langs_card = SectionCard("Langues supportées")
        langs = self._current_pkg.get("languages", [])
        langs_wrap = QWidget()
        langs_wrap.setStyleSheet("background: transparent;")
        langs_flow = QHBoxLayout(langs_wrap)
        langs_flow.setContentsMargins(0, 0, 0, 0)
        langs_flow.setSpacing(5)
        langs_flow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if langs:
            for lang in langs[:6]:
                badge = TagBadge(
                    lang,
                    Colors.ACCENT_LIGHT,
                    Colors.ACCENT,
                    Colors.ACCENT_BORDER
                )
                langs_flow.addWidget(badge)
            if len(langs) > 6:
                more = QLabel(f"+{len(langs) - 6}")
                more.setStyleSheet(
                    f"color: {Colors.TEXT_HINT}; background: transparent;"
                )
                langs_flow.addWidget(more)
        else:
            empty = QLabel("—")
            empty.setStyleSheet(
                f"color: {Colors.TEXT_HINT}; background: transparent;"
            )
            langs_flow.addWidget(empty)
        langs_card.add_widget(langs_wrap)
        self._aside_col.addWidget(langs_card)

        # Contenu associé
        related_card = SectionCard("Contenu associé")
        if self._related_pkgs:
            for pkg in self._related_pkgs:
                item = RelationItem(pkg)
                item.clicked.connect(self.relation_clicked.emit)
                related_card.add_widget(item)
        else:
            empty = QLabel(
                "Aucun contenu associé\ntrouvé dans la bibliothèque."
            )
            empty.setStyleSheet(
                f"color: {Colors.TEXT_HINT}; font-size: {Fonts.SIZE_MD}px;"
                f"background: transparent;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            related_card.add_widget(empty)
        self._aside_col.addWidget(related_card)
        self._aside_col.addStretch()

    def _clear_layout(self, layout):
        """Vide un layout proprement sans crash."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
            elif item.layout() is not None:
                self._clear_layout(item.layout())

    # ------------------------------------------------------------------ #
    #  Actions                                                             #
    # ------------------------------------------------------------------ #

    def _on_open_folder(self):
        filepath = self._current_pkg.get("filepath", "")
        if filepath:
            folder = os.path.dirname(filepath)
            subprocess.Popen(f'explorer "{folder}"')

    def _on_copy_path(self):
        filepath = self._current_pkg.get("filepath", "")
        if filepath:
            QApplication.clipboard().setText(filepath)

    def _on_copy_cid(self):
        cid = self._current_pkg.get("content_id", "")
        if cid:
            QApplication.clipboard().setText(cid)