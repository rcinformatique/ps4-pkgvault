from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from ui.theme import Colors, Fonts, Dimensions


CREDITS_STYLE = f"""
    QWidget#credits_page {{
        background: {Colors.BG_APP};
    }}

    QScrollArea {{
        background: {Colors.BG_APP};
        border: none;
    }}
    QScrollArea > QWidget > QWidget {{
        background: {Colors.BG_APP};
    }}

    /* Hero */
    QWidget#credits_hero {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_XL}px;
    }}
    QLabel#app_name {{
        color: {Colors.TEXT_PRIMARY};
        font-size: 32px;
        font-weight: 800;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#app_name_accent {{
        color: {Colors.ACCENT};
        font-size: 32px;
        font-weight: 800;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#app_version {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#app_tagline {{
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_LG}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    /* Cartes crédit */
    QWidget#credit_card {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_XL}px;
    }}
    QLabel#credit_icon {{
        font-size: 28px;
        background: transparent;
    }}
    QLabel#credit_title {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#credit_value {{
        color: {Colors.TEXT_MUTED};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    /* Technologies */
    QWidget#tech_section {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_XL}px;
    }}
    QLabel#tech_section_title {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-weight: 700;
        letter-spacing: 1px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QWidget#tech_item {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER_LIGHT};
        border-radius: {Dimensions.RADIUS_MD}px;
    }}
    QLabel#tech_icon {{
        font-size: 18px;
        background: transparent;
    }}
    QLabel#tech_name {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        font-weight: 500;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#tech_ver {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}

    /* Liens */
    QPushButton#link_btn {{
        background: {Colors.ACCENT_LIGHT};
        border: 1px solid {Colors.ACCENT_BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        color: {Colors.ACCENT};
        font-size: {Fonts.SIZE_MD}px;
        font-family: {Fonts.FAMILY};
        padding: 6px 14px;
    }}
    QPushButton#link_btn:hover {{
        background: {Colors.ACCENT};
        color: #ffffff;
    }}

    /* Footer */
    QFrame#credits_divider {{
        background: {Colors.BORDER_LIGHT};
        border: none;
        max-height: 1px;
    }}
    QLabel#footer_text {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#footer_accent {{
        color: {Colors.ACCENT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#disclaimer {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""


class CreditCard(QWidget):
    """Carte de crédit (développeur, tech, assistant)."""

    def __init__(
        self,
        icon: str,
        title: str,
        lines: list[str],
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("credit_card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("credit_icon")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("credit_title")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        for line in lines:
            lbl = QLabel(line)
            lbl.setObjectName("credit_value")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setWordWrap(True)
            layout.addWidget(lbl)


class TechItem(QWidget):
    """Item technologie utilisée."""

    def __init__(
        self,
        icon: str,
        name: str,
        version: str,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("tech_item")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("tech_icon")
        icon_lbl.setFixedWidth(24)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        info = QVBoxLayout()
        info.setSpacing(1)

        name_lbl = QLabel(name)
        name_lbl.setObjectName("tech_name")

        ver_lbl = QLabel(version)
        ver_lbl.setObjectName("tech_ver")

        info.addWidget(name_lbl)
        info.addWidget(ver_lbl)
        layout.addLayout(info)


class CreditsPage(QWidget):
    """Page À propos / Crédits."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("credits_page")
        self.setStyleSheet(CREDITS_STYLE)
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
        v = QVBoxLayout(content)
        v.setContentsMargins(24, 24, 24, 24)
        v.setSpacing(16)

        v.addWidget(self._make_hero())
        v.addWidget(self._make_credits_grid())
        v.addWidget(self._make_tech_section())
        v.addWidget(self._make_footer())
        v.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _make_hero(self) -> QWidget:
        hero = QWidget()
        hero.setObjectName("credits_hero")

        v = QVBoxLayout(hero)
        v.setContentsMargins(32, 28, 32, 28)
        v.setSpacing(8)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setSpacing(0)
        logo_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pkg_lbl = QLabel("📦  PS4 PKG")
        pkg_lbl.setObjectName("app_name")

        vault_lbl = QLabel("Vault")
        vault_lbl.setObjectName("app_name_accent")

        logo_row.addWidget(pkg_lbl)
        logo_row.addWidget(vault_lbl)
        v.addLayout(logo_row)

        # Version
        ver = QLabel("Version 1.0.0  ·  Build 2026.05.31")
        ver.setObjectName("app_version")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(ver)

        v.addSpacing(4)

        # Tagline
        tagline = QLabel(
            "Gestionnaire de fichiers PKG PS4\n"
            "Lecture directe des métadonnées SFO · Jaquettes HD · Base de données locale"
        )
        tagline.setObjectName("app_tagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setWordWrap(True)
        v.addWidget(tagline)

        v.addSpacing(8)

        # Boutons liens
        links_row = QHBoxLayout()
        links_row.setSpacing(8)
        links_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        github_btn = QPushButton("🐙  GitHub")
        github_btn.setObjectName("link_btn")
        github_btn.setFixedHeight(32)
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/tonusername/ps4-pkgvault")
            )
        )

        rawg_btn = QPushButton("🎮  RAWG.io")
        rawg_btn.setObjectName("link_btn")
        rawg_btn.setFixedHeight(32)
        rawg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rawg_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://rawg.io/apidocs")
            )
        )

        rc_btn = QPushButton("🏪  RC Informatique")
        rc_btn.setObjectName("link_btn")
        rc_btn.setFixedHeight(32)
        rc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rc_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://rc-informatique.fr")
            )
        )

        links_row.addWidget(github_btn)
        links_row.addWidget(rawg_btn)
        links_row.addWidget(rc_btn)
        v.addLayout(links_row)

        return hero

    def _make_credits_grid(self) -> QWidget:
        """Grille 3 colonnes de cartes crédit."""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        h = QHBoxLayout(wrapper)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        cards = [
            CreditCard(
                "👨‍💻",
                "Développeur",
                [
                    "Sébastien",
                    "RC Informatique",
                    "Moulins, Allier — France",
                    "rc-informatique.fr",
                ]
            ),
            CreditCard(
                "🤖",
                "Assisté par",
                [
                    "Claude (Anthropic)",
                    "IA générative",
                    "claude.ai",
                    "Sonnet 4.6",
                ]
            ),
            CreditCard(
                "🎨",
                "Design inspiré de",
                [
                    "Windows 11",
                    "Microsoft Store",
                    "Fluent Design System",
                    "WinUI 3",
                ]
            ),
        ]

        for card in cards:
            h.addWidget(card, 1)

        return wrapper

    def _make_tech_section(self) -> QWidget:
        """Section technologies utilisées."""
        section = QWidget()
        section.setObjectName("tech_section")

        v = QVBoxLayout(section)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(12)

        title = QLabel("TECHNOLOGIES UTILISÉES")
        title.setObjectName("tech_section_title")
        v.addWidget(title)

        # Grille 3 colonnes
        techs = [
            ("🐍", "Python",     "3.13+"),
            ("🖥️",  "PyQt6",     "6.x"),
            ("🗄️",  "SQLite",    "3.x"),
            ("🖼️",  "Pillow",    "10.x"),
            ("🌐",  "Requests",  "2.x"),
            ("🎮",  "RAWG API",  "v2"),
            ("🎮",  "PS Store",  "API publique"),
            ("📦",  "PyInstaller","6.x"),
            ("🔧",  "PyCharm",   "IDE"),
        ]

        # 3 colonnes
        grid_rows = [techs[i:i+3] for i in range(0, len(techs), 3)]
        for row_items in grid_rows:
            row = QHBoxLayout()
            row.setSpacing(8)
            for icon, name, ver in row_items:
                item = TechItem(icon, name, ver)
                row.addWidget(item, 1)
            # Complète si moins de 3
            while len(row_items) < 3:
                spacer = QWidget()
                spacer.setStyleSheet("background: transparent;")
                row.addWidget(spacer, 1)
                row_items.append(("", "", ""))
            v.addLayout(row)

        return section

    def _make_footer(self) -> QWidget:
        """Footer avec mentions légales."""
        footer = QWidget()
        footer.setStyleSheet("background: transparent;")

        v = QVBoxLayout(footer)
        v.setContentsMargins(0, 8, 0, 0)
        v.setSpacing(6)

        # Séparateur
        divider = QFrame()
        divider.setObjectName("credits_divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        v.addWidget(divider)
        v.addSpacing(4)

        # Copyright
        copy_row = QHBoxLayout()
        copy_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy_row.setSpacing(4)

        copy1 = QLabel("Fait avec ❤️ pour la communauté PS4  ·")
        copy1.setObjectName("footer_text")

        copy2 = QLabel("PS4 PKGVault © 2026")
        copy2.setObjectName("footer_accent")

        copy3 = QLabel("· Tous droits réservés")
        copy3.setObjectName("footer_text")

        copy_row.addWidget(copy1)
        copy_row.addWidget(copy2)
        copy_row.addWidget(copy3)
        v.addLayout(copy_row)

        # Disclaimer
        disclaimer = QLabel(
            "Ce logiciel est destiné à un usage personnel uniquement. "
            "Aucune violation des droits d'auteur n'est encouragée. "
            "Les fichiers PKG utilisés doivent provenir de jeux dont vous êtes propriétaire."
        )
        disclaimer.setObjectName("disclaimer")
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disclaimer.setWordWrap(True)
        v.addWidget(disclaimer)

        return footer