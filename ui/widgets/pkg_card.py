import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSizePolicy, QMenu, QInputDialog,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QAction
from ui.theme import Colors, Fonts, Dimensions, PKG_TYPES


CARD_WIDTH  = 200
CARD_HEIGHT = 310


CARD_STYLE = f"""
    QWidget#pkg_card {{
        background: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.CARD_RADIUS}px;
    }}
    QWidget#pkg_card:hover {{
        border-color: {Colors.ACCENT};
    }}
"""

CARD_SELECTED_STYLE = f"""
    QWidget#pkg_card {{
        background: {Colors.BG_WHITE};
        border: 2px solid {Colors.ACCENT};
        border-radius: {Dimensions.CARD_RADIUS}px;
    }}
"""

CARD_FLASH_STYLE = f"""
    QWidget#pkg_card {{
        background: {Colors.BG_WHITE};
        border: 2px solid {Colors.SUCCESS};
        border-radius: {Dimensions.CARD_RADIUS}px;
    }}
"""

CONTEXT_MENU_STYLE = f"""
    QMenu {{
        background-color: {Colors.BG_WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.RADIUS_LG}px;
        padding: 4px;
        font-size: {Fonts.SIZE_MD}px;
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
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


class TypeBadge(QLabel):
    """Badge coloré indiquant le type du PKG."""

    def __init__(self, pkg_type: str, parent=None):
        super().__init__(parent)
        info = PKG_TYPES.get(pkg_type, PKG_TYPES["game"])
        self.setText(info["label"])
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {info['badge']};
                color: {info['text']};
                border-radius: 4px;
                font-size: 9px;
                font-weight: 700;
                padding: 2px 7px;
                font-family: {Fonts.FAMILY};
            }}
        """)


class PkgCard(QWidget):
    """
    Carte PKG affichant la jaquette et les infos de base.

    Signaux :
        clicked(pkg_data)   → clic gauche
        deleted(filepath)   → fichier supprimé
    """

    clicked = pyqtSignal(dict)
    deleted = pyqtSignal(str)

    def __init__(self, pkg_data: dict, parent=None):
        super().__init__(parent)
        self.pkg_data = pkg_data
        self.setObjectName("pkg_card")
        self.setStyleSheet(CARD_STYLE)
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._selected = False
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
        """Zone jaquette avec badges superposés."""
        pkg_type = self.pkg_data.get("type", "game")
        info     = PKG_TYPES.get(pkg_type, PKG_TYPES["game"])

        # Conteneur cover
        cover = QWidget()
        cover.setFixedSize(CARD_WIDTH, 267)
        cover.setStyleSheet(f"""
            background: {info['bg']};
            border-radius: {Dimensions.CARD_RADIUS}px
                           {Dimensions.CARD_RADIUS}px 0px 0px;
        """)

        # Image / placeholder
        self.cover_label = QLabel(cover)
        self.cover_label.setFixedSize(CARD_WIDTH, 267)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText(info["icon"])
        self.cover_label.setStyleSheet(f"""
            background: transparent;
            font-size: 52px;
            border-radius: {Dimensions.CARD_RADIUS}px
                           {Dimensions.CARD_RADIUS}px 0px 0px;
        """)

        # Badge type (haut gauche)
        badge = TypeBadge(pkg_type, cover)
        badge.move(8, 8)
        badge.adjustSize()

        # Badge firmware (bas droite)
        firmware = self.pkg_data.get("firmware", "")
        if firmware and firmware != "—":
            fw = QLabel(f"FW {firmware}", cover)
            fw.setStyleSheet(f"""
                background: rgba(255,255,255,0.92);
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                font-size: 9px;
                padding: 2px 6px;
                font-family: {Fonts.FAMILY};
            """)
            fw.adjustSize()
            fw.move(
                CARD_WIDTH - fw.width() - 8,
                267 - fw.height() - 8
            )

        return cover

    def _make_info(self) -> QWidget:
        """Zone infos sous la jaquette."""
        info_widget = QWidget()
        info_widget.setStyleSheet(f"""
            background: {Colors.BG_WHITE};
            border-radius: 0px 0px
                           {Dimensions.CARD_RADIUS}px
                           {Dimensions.CARD_RADIUS}px;
        """)
        layout = QVBoxLayout(info_widget)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(3)

        # Titre
        title_text = self.pkg_data.get("title", "Inconnu")
        title = QLabel()
        title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: {Fonts.SIZE_MD}px;
            font-weight: 600;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)
        fm     = title.fontMetrics()
        elided = fm.elidedText(
            title_text,
            Qt.TextElideMode.ElideRight,
            CARD_WIDTH - 20
        )
        title.setText(elided)
        layout.addWidget(title)

        # Content-ID
        cid = QLabel(self.pkg_data.get("content_id", "")[:16])
        cid.setStyleSheet(f"""
            color: {Colors.TEXT_HINT};
            font-size: {Fonts.SIZE_SM}px;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)
        layout.addWidget(cid)

        # Taille + Région
        bottom = QHBoxLayout()
        bottom.setSpacing(0)

        size = QLabel(self.pkg_data.get("size_str", ""))
        size.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: {Fonts.SIZE_SM}px;
            font-family: {Fonts.FAMILY};
            background: transparent;
        """)

        region = QLabel(self.pkg_data.get("region", ""))
        region.setStyleSheet(f"""
            color: {Colors.TEXT_HINT};
            font-size: {Fonts.SIZE_SM}px;
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
    #  Jaquette                                                            #
    # ------------------------------------------------------------------ #

    def set_cover_pixmap(self, pixmap: QPixmap):
        """Affiche une vraie jaquette."""
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(
                CARD_WIDTH, 267,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(scaled)
            self.cover_label.setText("")

    def set_selected(self, state: bool):
        """Sélectionne / désélectionne la carte."""
        self._selected = state
        self.setStyleSheet(
            CARD_SELECTED_STYLE if state else CARD_STYLE
        )

    def flash(self):
        """Flash vert pour confirmer une action."""
        self.setStyleSheet(CARD_FLASH_STYLE)
        QTimer.singleShot(700, lambda: self.setStyleSheet(CARD_STYLE))

    # ------------------------------------------------------------------ #
    #  Événements souris                                                   #
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.pkg_data)

    def contextMenuEvent(self, event):
        """Menu clic droit."""
        menu = QMenu(self)
        menu.setStyleSheet(CONTEXT_MENU_STYLE)

        # Titre désactivé
        title_act = QAction(
            self.pkg_data.get("title", "Inconnu")[:40], self
        )
        title_act.setEnabled(False)
        menu.addAction(title_act)
        menu.addSeparator()

        act_open   = QAction("📁  Ouvrir le dossier",   self)
        act_copy   = QAction("📋  Copier le chemin",     self)
        act_cid    = QAction("🔑  Copier le Content-ID", self)
        menu.addAction(act_open)
        menu.addAction(act_copy)
        menu.addAction(act_cid)
        menu.addSeparator()

        act_rename = QAction("✏️  Renommer le fichier",  self)
        menu.addAction(act_rename)
        menu.addSeparator()

        act_delete = QAction("🗑️  Supprimer le fichier", self)
        menu.addAction(act_delete)

        # Connexions
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
            QMessageBox.critical(self, "Erreur", f"Impossible de renommer :\n{e}")

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
            QMessageBox.critical(self, "Erreur", f"Impossible de supprimer :\n{e}")