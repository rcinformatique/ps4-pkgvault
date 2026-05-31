from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from ui.theme import Colors, Fonts, Dimensions


STATUSBAR_STYLE = f"""
    QStatusBar {{
        background-color: {Colors.BG_WHITE};
        border-top: 1px solid {Colors.BORDER_LIGHT};
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        padding: 0px 18px;
    }}
    QStatusBar::item {{
        border: none;
    }}
    QLabel#sb_item {{
        color: {Colors.TEXT_HINT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
        padding: 0px 2px;
    }}
    QLabel#sb_sep {{
        color: {Colors.BORDER};
        font-size: 12px;
        background: transparent;
        padding: 0px 4px;
    }}
    QLabel#sb_msg_ok {{
        color: {Colors.SUCCESS};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#sb_msg_warn {{
        color: {Colors.WARNING};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#sb_msg_info {{
        color: {Colors.ACCENT};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
    QLabel#sb_msg_error {{
        color: {Colors.ERROR};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""


class StatItem(QLabel):
    """Un élément de stat dans la statusbar (ex: Jeux 3)."""

    def __init__(self, dot_color: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("sb_item")
        self._dot_color = dot_color
        self._label     = label
        self._count     = 0
        self._update_text()

    def _update_text(self):
        dot  = f'<span style="color:{self._dot_color};">●</span>'
        text = f'{dot} {self._label} {self._count}'
        self.setText(text)
        self.setTextFormat(Qt.TextFormat.RichText)

    def set_count(self, count: int):
        self._count = count
        self._update_text()


class StatusBar(QStatusBar):
    """
    Barre de statut en bas de la fenêtre.
    Affiche les stats par type et un message d'état.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(STATUSBAR_STYLE)
        self.setSizeGripEnabled(False)
        self.setFixedHeight(Dimensions.STATUSBAR_HEIGHT)
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):

        # Stats par type
        self._stat_game     = StatItem(Colors.GAME_BADGE,     "Jeux")
        self._stat_dlc      = StatItem(Colors.DLC_BADGE,      "DLC")
        self._stat_update   = StatItem(Colors.UPDATE_BADGE,   "Updates")
        self._stat_backport = StatItem(Colors.BACKPORT_BADGE, "Backports")

        for stat in [
            self._stat_game,
            self._stat_dlc,
            self._stat_update,
            self._stat_backport,
        ]:
            self.addWidget(stat)
            self.addWidget(self._make_sep())

        # Taille totale
        self._size_label = QLabel("0 Go total")
        self._size_label.setObjectName("sb_item")
        self.addWidget(self._size_label)

        # Message d'état (droite)
        self._msg_label = QLabel("Prêt")
        self._msg_label.setObjectName("sb_msg_info")
        self.addPermanentWidget(self._msg_label)

        # Version (droite)
        sep = self._make_sep()
        self.addPermanentWidget(sep)

        ver = QLabel("PS4 PKGVault v1.0.0")
        ver.setObjectName("sb_item")
        ver.setStyleSheet(
            f"color: {Colors.BORDER}; font-size: {Fonts.SIZE_SM}px; background: transparent;"
        )
        self.addPermanentWidget(ver)

    def _make_sep(self) -> QLabel:
        sep = QLabel("|")
        sep.setObjectName("sb_sep")
        return sep

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #

    def update_stats(self, packages: list[dict]):
        """Met à jour toutes les stats depuis une liste de PKG."""
        counts = {"game": 0, "dlc": 0, "update": 0, "backport": 0}
        total_bytes = 0

        for pkg in packages:
            pkg_type = pkg.get("type", "game")
            if pkg_type in counts:
                counts[pkg_type] += 1
            total_bytes += pkg.get("size_bytes", 0)

        self._stat_game.set_count(counts["game"])
        self._stat_dlc.set_count(counts["dlc"])
        self._stat_update.set_count(counts["update"])
        self._stat_backport.set_count(counts["backport"])
        self._size_label.setText(self._format_size(total_bytes))

    def update_counts(self, counts: dict):
        """Met à jour les stats depuis un dict de comptages."""
        self._stat_game.set_count(counts.get("game", 0))
        self._stat_dlc.set_count(counts.get("dlc", 0))
        self._stat_update.set_count(counts.get("update", 0))
        self._stat_backport.set_count(counts.get("backport", 0))

    def set_message(self, text: str, level: str = "info"):
        """
        Affiche un message dans la statusbar.
        level : "info" | "ok" | "warn" | "error"
        """
        obj_names = {
            "info":  "sb_msg_info",
            "ok":    "sb_msg_ok",
            "warn":  "sb_msg_warn",
            "error": "sb_msg_error",
        }
        icons = {
            "info":  "ℹ️",
            "ok":    "✅",
            "warn":  "⚠️",
            "error": "❌",
        }
        obj  = obj_names.get(level, "sb_msg_info")
        icon = icons.get(level, "")
        self._msg_label.setText(f"{icon}  {text}")
        self._msg_label.setObjectName(obj)
        self._msg_label.style().unpolish(self._msg_label)
        self._msg_label.style().polish(self._msg_label)

    def set_scanning(self, folder: str):
        """Indique qu'un scan est en cours."""
        short = folder[-40:] if len(folder) > 40 else folder
        self.set_message(f"Scan en cours : {short}…", "info")

    def set_scan_done(self, count: int, errors: int = 0):
        """Indique que le scan est terminé."""
        if errors:
            self.set_message(
                f"{count} PKG chargés — {errors} fichier(s) ignorés",
                "warn"
            )
        else:
            self.set_message(
                f"{count} PKG chargés avec succès",
                "ok"
            )

    def set_ready(self):
        """Remet le message par défaut."""
        self.set_message("Prêt", "info")

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes >= 1_073_741_824:
            return f"{size_bytes / 1_073_741_824:.1f} Go total"
        if size_bytes >= 1_048_576:
            return f"{size_bytes / 1_048_576:.1f} Mo total"
        return f"{size_bytes / 1024:.1f} Ko total"