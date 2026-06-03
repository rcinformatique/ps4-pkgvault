import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow
from ui.theme import APP_STYLE, Fonts


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PS4 PKGVault")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("RC Informatique")

    # Police globale Segoe UI
    font = QFont(Fonts.FAMILY, Fonts.SIZE_MD)
    app.setFont(font)

    # Thème global
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()