# ------------------------------------------------------------------ #
#  PS4 PKGVault — Thème global Windows 11                            #
# ------------------------------------------------------------------ #

# ------------------------------------------------------------------ #
#  Couleurs                                                           #
# ------------------------------------------------------------------ #

class Colors:
    # Fonds
    BG_APP        = "#f0f2f5"   # fond général
    BG_WHITE      = "#ffffff"   # surfaces blanches
    BG_HOVER      = "#f8f9ff"   # survol léger
    BG_SELECTED   = "#e8f0fe"   # sélection / actif
    BG_INPUT      = "#f5f7fa"   # champs de saisie
    BG_ROW_ALT    = "#f8f9fb"   # lignes alternées

    # Accents bleu Windows 11
    ACCENT        = "#0067c0"   # bleu principal
    ACCENT_HOVER  = "#005ba3"   # bleu survol
    ACCENT_LIGHT  = "#e8f0fe"   # bleu très clair
    ACCENT_BORDER = "#b8d0f5"   # bordure bleue

    # Textes
    TEXT_PRIMARY   = "#1a1a2e"  # texte principal
    TEXT_SECONDARY = "#666666"  # texte secondaire
    TEXT_MUTED     = "#aaaaaa"  # texte discret
    TEXT_HINT      = "#cccccc"  # placeholder

    # Bordures
    BORDER         = "#e4e7ec"  # bordure standard
    BORDER_LIGHT   = "#eef0f4"  # bordure légère
    BORDER_STRONG  = "#dde1e8"  # bordure forte

    # Types PKG
    GAME_BG        = "#dce8f8"
    GAME_BADGE     = "#0067c0"
    GAME_TEXT      = "#ffffff"

    DLC_BG         = "#d4ecd4"
    DLC_BADGE      = "#107c10"
    DLC_TEXT       = "#ffffff"

    UPDATE_BG      = "#d4e8f8"
    UPDATE_BADGE   = "#0078d4"
    UPDATE_TEXT    = "#ffffff"

    BACKPORT_BG    = "#f8e8d4"
    BACKPORT_BADGE = "#ca5010"
    BACKPORT_TEXT  = "#ffffff"

    # Statuts
    SUCCESS        = "#107c10"
    WARNING        = "#ca5010"
    ERROR          = "#e05a5a"
    INFO           = "#0067c0"

    # Danger
    DANGER_BG      = "#fff5f5"
    DANGER_BORDER  = "#ffd0d0"
    DANGER_TEXT    = "#e05a5a"


# ------------------------------------------------------------------ #
#  Dimensions                                                         #
# ------------------------------------------------------------------ #

class Dimensions:
    TOPBAR_HEIGHT    = 52
    SUBBAR_HEIGHT    = 40
    STATUSBAR_HEIGHT = 26
    BACK_BAR_HEIGHT  = 40

    CARD_COLS        = 4
    CARD_RADIUS      = 12
    CARD_BORDER      = 1

    RADIUS_SM        = 5
    RADIUS_MD        = 7
    RADIUS_LG        = 10
    RADIUS_XL        = 12

    PADDING_SM       = 8
    PADDING_MD       = 14
    PADDING_LG       = 18
    PADDING_XL       = 24

    ICON_SM          = 14
    ICON_MD          = 16
    ICON_LG          = 20
    ICON_XL          = 24


# ------------------------------------------------------------------ #
#  Polices                                                            #
# ------------------------------------------------------------------ #

class Fonts:
    FAMILY     = "Segoe UI"
    FAMILY_ALT = "Arial"

    SIZE_XS    = 9
    SIZE_SM    = 10
    SIZE_MD    = 12
    SIZE_LG    = 13
    SIZE_XL    = 15
    SIZE_XXL   = 21
    SIZE_TITLE = 24

    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_BOLD   = 700


# ------------------------------------------------------------------ #
#  Types PKG                                                          #
# ------------------------------------------------------------------ #

PKG_TYPES = {
    "game": {
        "label":  "BASE",
        "icon":   "🎮",
        "bg":     Colors.GAME_BG,
        "badge":  Colors.GAME_BADGE,
        "text":   Colors.GAME_TEXT,
    },
    "dlc": {
        "label":  "DLC",
        "icon":   "🧩",
        "bg":     Colors.DLC_BG,
        "badge":  Colors.DLC_BADGE,
        "text":   Colors.DLC_TEXT,
    },
    "update": {
        "label":  "UPDATE",
        "icon":   "⬆",
        "bg":     Colors.UPDATE_BG,
        "badge":  Colors.UPDATE_BADGE,
        "text":   Colors.UPDATE_TEXT,
    },
    "backport": {
        "label":  "BACKPORT",
        "icon":   "⏮",
        "bg":     Colors.BACKPORT_BG,
        "badge":  Colors.BACKPORT_BADGE,
        "text":   Colors.BACKPORT_TEXT,
    },
}


# ------------------------------------------------------------------ #
#  QSS Global                                                         #
# ------------------------------------------------------------------ #

APP_STYLE = f"""
    /* === BASE === */
    QMainWindow, QWidget {{
        background-color: {Colors.BG_APP};
        font-family: {Fonts.FAMILY}, {Fonts.FAMILY_ALT};
        font-size: {Fonts.SIZE_MD}px;
        color: {Colors.TEXT_PRIMARY};
    }}

    /* === SCROLLBAR === */
    QScrollBar:vertical {{
        background: {Colors.BG_APP};
        width: 6px;
        border-radius: 3px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.BORDER};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.BORDER_STRONG};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {Colors.BG_APP};
        height: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Colors.BORDER};
        border-radius: 3px;
        min-width: 30px;
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* === SCROLL AREA === */
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}

    /* === TOOLTIP === */
    QToolTip {{
        background-color: {Colors.BG_WHITE};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        padding: 5px 9px;
        font-size: {Fonts.SIZE_SM}px;
    }}

    /* === INPUT === */
    QLineEdit {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        padding: 5px 11px;
        font-size: {Fonts.SIZE_MD}px;
        color: {Colors.TEXT_PRIMARY};
        selection-background-color: {Colors.ACCENT_LIGHT};
    }}
    QLineEdit:focus {{
        border-color: {Colors.ACCENT};
    }}
    QLineEdit::placeholder {{
        color: {Colors.TEXT_HINT};
    }}

    /* === COMBOBOX === */
    QComboBox {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        padding: 5px 10px;
        font-size: {Fonts.SIZE_MD}px;
        color: {Colors.TEXT_PRIMARY};
        min-width: 140px;
    }}
    QComboBox:hover {{
        border-color: {Colors.ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        selection-background-color: {Colors.ACCENT_LIGHT};
        color: {Colors.TEXT_PRIMARY};
        padding: 4px;
    }}

    /* === MESSAGE BOX === */
    QMessageBox {{
        background-color: {Colors.BG_WHITE};
    }}
    QMessageBox QPushButton {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        padding: 6px 18px;
        font-size: {Fonts.SIZE_MD}px;
        color: {Colors.TEXT_PRIMARY};
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        border-color: {Colors.ACCENT};
        color: {Colors.ACCENT};
    }}

    /* === INPUT DIALOG === */
    QInputDialog {{
        background-color: {Colors.BG_WHITE};
    }}
    QInputDialog QPushButton {{
        background: {Colors.BG_INPUT};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_MD}px;
        padding: 6px 18px;
        min-width: 80px;
    }}

    /* === MENU CONTEXTUEL === */
    QMenu {{
        background-color: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_LG}px;
        padding: 4px;
        font-size: {Fonts.SIZE_MD}px;
        color: {Colors.TEXT_PRIMARY};
    }}
    QMenu::item {{
        padding: 7px 28px 7px 12px;
        border-radius: {Dimensions.RADIUS_SM}px;
    }}
    QMenu::item:selected {{
        background-color: {Colors.ACCENT_LIGHT};
        color: {Colors.ACCENT};
    }}
    QMenu::item:disabled {{
        color: {Colors.TEXT_HINT};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {Colors.BORDER_LIGHT};
        margin: 3px 6px;
    }}
"""


# ------------------------------------------------------------------ #
#  Helpers QSS réutilisables                                          #
# ------------------------------------------------------------------ #

def btn_primary() -> str:
    """Style bouton principal bleu."""
    return f"""
        QPushButton {{
            background: {Colors.ACCENT};
            border: none;
            border-radius: {Dimensions.RADIUS_MD}px;
            color: #ffffff;
            font-size: {Fonts.SIZE_MD}px;
            padding: 7px 16px;
            font-family: {Fonts.FAMILY};
        }}
        QPushButton:hover {{
            background: {Colors.ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background: #004f9a;
        }}
        QPushButton:disabled {{
            background: {Colors.BORDER};
            color: {Colors.TEXT_HINT};
        }}
    """


def btn_secondary() -> str:
    """Style bouton secondaire gris."""
    return f"""
        QPushButton {{
            background: {Colors.BG_INPUT};
            border: 1px solid {Colors.BORDER};
            border-radius: {Dimensions.RADIUS_MD}px;
            color: {Colors.TEXT_SECONDARY};
            font-size: {Fonts.SIZE_MD}px;
            padding: 7px 14px;
            font-family: {Fonts.FAMILY};
        }}
        QPushButton:hover {{
            border-color: {Colors.ACCENT};
            color: {Colors.ACCENT};
        }}
        QPushButton:pressed {{
            background: {Colors.ACCENT_LIGHT};
        }}
    """


def btn_danger() -> str:
    """Style bouton danger rouge."""
    return f"""
        QPushButton {{
            background: {Colors.DANGER_BG};
            border: 1px solid {Colors.DANGER_BORDER};
            border-radius: {Dimensions.RADIUS_MD}px;
            color: {Colors.DANGER_TEXT};
            font-size: {Fonts.SIZE_MD}px;
            padding: 7px 14px;
            font-family: {Fonts.FAMILY};
        }}
        QPushButton:hover {{
            background: #ffe0e0;
            border-color: #e05a5a;
        }}
    """


def card_style(selected: bool = False) -> str:
    """Style carte PKG."""
    border = f"2px solid {Colors.ACCENT}" if selected else f"1px solid {Colors.BORDER}"
    shadow = f"box-shadow: 0 0 0 2px {Colors.ACCENT_LIGHT};" if selected else ""
    return f"""
        QWidget {{
            background: {Colors.BG_WHITE};
            border: {border};
            border-radius: {Dimensions.CARD_RADIUS}px;
            {shadow}
        }}
        QWidget:hover {{
            border: 1px solid {Colors.ACCENT};
        }}
    """


def section_card_style() -> str:
    """Style carte section (détail, paramètres)."""
    return f"""
        QWidget {{
            background: {Colors.BG_WHITE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Dimensions.RADIUS_LG}px;
        }}
    """


def badge_style(bg: str, text: str) -> str:
    """Style badge coloré."""
    return f"""
        QLabel {{
            background: {bg};
            color: {text};
            border-radius: 4px;
            font-size: 9px;
            font-weight: 700;
            padding: 2px 7px;
            font-family: {Fonts.FAMILY};
        }}
    """


def pill_style(bg: str, text: str, border: str) -> str:
    """Style pill (genre, langue)."""
    return f"""
        QLabel {{
            background: {bg};
            color: {text};
            border: 1px solid {border};
            border-radius: 12px;
            font-size: 11px;
            padding: 3px 10px;
            font-family: {Fonts.FAMILY};
        }}
    """