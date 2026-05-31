import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSizePolicy, QMenu, QInputDialog,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPixmap, QAction, QFont
from ui.theme import Colors, Fonts, Dimensions, PKG_TYPES


CARD_STYLE = f"""
    QWidget#pkg_card {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 12px;
    }}
    QWidget#pkg_card:hover {{
        border: 2px solid {Colors.ACCENT};
    }}
"""

CARD_SELECTED_STYLE = f"""
    QWidget#pkg_card {{
        background: {Colors.BG_WHITE};
        border: 2px solid {Colors.ACCENT};
        border-radius: 12px;
    }}
"""

CARD_FLASH_STYLE = f"""
    QWidget#pkg_card {{
        background: {Colors.BG_WHITE};
        border: 2px solid {Colors.SUCCESS};
        border-radius: 12px;
    }}
"""

CONTEXT_MENU_STYLE = f"""
    QMenu {{
        background-color: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 10px;
        padding: 4px;
        font-size: 13px;
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
    }}
    QMenu::item {{
        padding: 8px 28px 8px 12px;
        border-radius: 6px;
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

TYPE_BG_COLORS = {
    "game":     "#dce8f8",
    "dlc":      "#d4ecd4",
    "update":   "#d4e8f8",
    "backport": "#f8e8d4",
}

TYPE_ICONS = {
    "game":     "🎮",
    "dlc":      "🧩",
    "update":   "⬆️",
    "backport": "⏮️",
}


class TypeBadge(QLabel):
    """Badge coloré type PKG."""

    def __init__(self, pkg_type: str, parent=None):
        super().__init__(parent)
        info = PKG_TYPES.get(pkg_type, PKG_TYPES["game"])
        self.setText(info["label"])
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(22)
        self.setStyleSheet(f"""
            QLabel {{
                background: {info['badge']};
                color: {info['text']};
                border-radius: 5px;
                font-size: 11px;
                font-weight: 700;
                padding: 2px 9px;
                font-family: {Fonts.FAMILY};
            }}
        """)


class PkgCard(QWidget):
    """
    Carte PKG — s'étire pour remplir sa cellule de grille.
    """

    clicked = pyqtSignal(dict)
    deleted = pyqtSignal(str)

    def __init__(self, pkg_data: dict, parent=None):
        super().__init__(parent)
        self.pkg_data  = pkg_data
        self._selected = False
        self.setObjectName("pkg_card")
        self.setStyleSheet(CARD_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # La carte s'étire horizontalement
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.setMinimumHeight(300)
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._make_cover())
        layout.addWidget(self._make_info())

    def _make_cover(self) -> QWidget:
        pkg_type = self.pkg_data.get("type", "game")
        info     = PKG_TYPES.get(pkg_type, PKG_TYPES["game"])
        bg_color = TYPE_BG_COLORS.get(pkg_type, "#dce8f8")

        # Conteneur cover — ratio PS4 : 2:3
        cover = QWidget()
        cover.setStyleSheet(f"""
            background: {bg_color};
            border-radius: 12px 12px 0px 0px;
        """)
        cover.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        cover.setFixedHeight(220)

        cover_layout = QVBoxLayout(cover)
        cover_layout.setContentsMargins(0, 0, 0, 0)
        cover_layout.setSpacing(0)

        # Image / placeholder
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.cover_label.setFixedHeight(220)
        self.cover_label.setStyleSheet(
            "background: transparent; font-size: 64px;"
        )
        self.cover_label.setText(info["icon"])
        cover_layout.addWidget(self.cover_label)

        # Badge type (haut gauche) — superposé
        self._badge = TypeBadge(pkg_type, cover)
        self._badge.move(10, 10)
        self._badge.adjustSize()

        # Badge firmware (bas droite)
        firmware = self.pkg_data.get("firmware", "")
        if firmware and firmware != "—":
            fw = QLabel(f"FW {firmware}", cover)
            fw.setStyleSheet(f"""
                background: rgba(255,255,255,0.92);
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 5px;
                font-size: 11px;
                font-weight: 600;
                padding: 3px 8px;
                font-family: {Fonts.FAMILY};
            """)
            fw.adjustSize()
            fw.move(0, 0)  # repositionné dans resizeEvent
            self._fw_badge = fw
        else:
            self._fw_badge = None

        return cover

    def _make_info(self) -> QWidget:
        info_widget = QWidget()
        info_widget.setStyleSheet(f"""
            background: {Colors.BG_WHITE};
            border-radius: 0px 0px 12px 12px;
        """)
        info_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(4)

        # Titre
        title_text = self.pkg_data.get("title", "Inconnu")
        self._title_label = QLabel(title_text)
        self._title_label.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 600;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)
        self._title_label.setWordWrap(False)
        layout.addWidget(self._title_label)

        # Content-ID
        cid_text = self.pkg_data.get("content_id", "")
        if len(cid_text) > 20:
            cid_text = cid_text[:20]
        cid = QLabel(cid_text)
        cid.setStyleSheet(f"""
            color: {Colors.TEXT_HINT};
            font-size: 11px;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)
        layout.addWidget(cid)

        # Taille + Région
        bottom = QHBoxLayout()
        bottom.setSpacing(0)
        bottom.setContentsMargins(0, 2, 0, 0)

        size = QLabel(self.pkg_data.get("size_str", ""))
        size.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 12px;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)

        region = QLabel(self.pkg_data.get("region", ""))
        region.setStyleSheet(f"""
            color: {Colors.TEXT_HINT};
            font-size: 11px;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)
        region.setAlignment(Qt.AlignmentFlag.AlignRight)

        bottom.addWidget(size)
        bottom.addStretch()
        bottom.addWidget(region)
        layout.addLayout(bottom)

        return info_widget

    # ------------------------------------------------------------------ #
    #  Resize — repositionne le badge FW                                  #
    # ------------------------------------------------------------------ #

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fw_badge:
            fw = self._fw_badge
            fw.adjustSize()
            # Bas droite de la cover
            fw.move(
                self.width() - fw.width() - 10,
                self._badge.y() + 220 - fw.height() - 10
            )
        # Met à jour le titre tronqué
        if hasattr(self, "_title_label"):
            fm     = self._title_label.fontMetrics()
            elided = fm.elidedText(
                self.pkg_data.get("title", ""),
                Qt.TextElideMode.ElideRight,
                self.width() - 24
            )
            self._title_label.setText(elided)

    # ------------------------------------------------------------------ #
    #  Jaquette                                                            #
    # ------------------------------------------------------------------ #

    def set_cover_pixmap(self, pixmap: QPixmap):
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(
                self.cover_label.width(),
                self.cover_label.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(scaled)
            self.cover_label.setText("")

    def set_selected(self, state: bool):
        self._selected = state
        self.setStyleSheet(
            CARD_SELECTED_STYLE if state else CARD_STYLE
        )

    def flash(self):
        self.setStyleSheet(CARD_FLASH_STYLE)
        QTimer.singleShot(700, lambda: self.setStyleSheet(CARD_STYLE))

    # ------------------------------------------------------------------ #
    #  Événements                                                          #
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.pkg_data)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(CONTEXT_MENU_STYLE)

        title_act = QAction(
            self.pkg_data.get("title", "Inconnu")[:40], self
        )
        title_act.setEnabled(False)
        menu.addAction(title_act)
        menu.addSeparator()

        act_open   = QAction("📁  Ouvrir le dossier",   self)
        act_copy   = QAction("📋  Copier le chemin",     self)
        act_cid    = QAction("🔑  Copier le Content-ID", self)
        act_rename = QAction("✏️  Renommer le fichier",  self)
        act_delete = QAction("🗑️  Supprimer le fichier", self)

        menu.addAction(act_open)
        menu.addAction(act_copy)
        menu.addAction(act_cid)
        menu.addSeparator()
        menu.addAction(act_rename)
        menu.addSeparator()
        menu.addAction(act_delete)

        act_open.triggered.connect(self._ctx_open_folder)
        act_copy.triggered.connect(self._ctx_copy_path)
        act_cid.triggered.connect(self._ctx_copy_cid)
        act_rename.triggered.connect(self._ctx_rename)
        act_delete.triggered.connect(self._ctx_delete)

        menu.exec(event.globalPos())

    # ------------------------------------------------------------------ #
    #  Actions contextuelles                                               #
    # ------------------------------------------------------------------ #

    def _ctx_open_folder(self):
        filepath = self.pkg_data.get("filepath", "")
        if filepath:
            folder = os.path.dirname(filepath)
            subprocess.Popen(f'explorer "{folder}"')

    def _ctx_copy_path(self):
        filepath = self.pkg_data.get("filepath", "")
        if filepath:
            QApplication.clipboard().setText(filepath)
            self.flash()

    def _ctx_copy_cid(self):
        cid = self.pkg_data.get("content_id", "")
        if cid:
            QApplication.clipboard().setText(cid)
            self.flash()

    def _ctx_rename(self):
        filepath = self.pkg_data.get("filepath", "")
        if not filepath:
            return
        old_name = os.path.basename(filepath)
        new_name, ok = QInputDialog.getText(
            self, "Renommer", "Nouveau nom :", text=old_name
        )
        if not ok or not new_name.strip() or new_name == old_name:
            return
        if not new_name.lower().endswith(".pkg"):
            new_name += ".pkg"
        new_path = os.path.join(os.path.dirname(filepath), new_name)
        try:
            os.rename(filepath, new_path)
            self.pkg_data["filepath"] = new_path
            self.pkg_data["filename"] = new_name
            self.flash()
        except OSError as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de renommer :\n{e}"
            )

    def _ctx_delete(self):
        filepath = self.pkg_data.get("filepath", "")
        if not filepath:
            return
        reply = QMessageBox.warning(
            self,
            "Supprimer le fichier",
            f"Supprimer définitivement ?\n\n"
            f"{os.path.basename(filepath)}\n\n"
            f"Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            os.remove(filepath)
            self.deleted.emit(filepath)
            self.setParent(None)
            self.deleteLater()
        except OSError as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de supprimer :\n{e}"
            )