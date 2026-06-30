"""
Application entry point.
"""
import sys
import os

# Ensure project src directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.styles import STYLESHEET
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from core.account_manager import AccountManager


def main():
    # High-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    
    # CRITICAL FIX: Share OpenGL Contexts so PyQtGraph shaders survive window recreation
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setApplicationName("LiDAR Lift Monitor")
    app.setOrganizationName("HPS3D")
    app.setStyleSheet(STYLESHEET)

    # Default font
    font = QFont("Segoe UI", 13)
    app.setFont(font)

    account_mgr = AccountManager()

    # Login loop
    while True:
        login_dlg = LoginDialog(account_mgr)
        # Centre on screen
        screen = app.primaryScreen().geometry()
        login_dlg.move(
            screen.center().x() - login_dlg.width() // 2,
            screen.center().y() - login_dlg.height() // 2,
        )

        if login_dlg.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

        window = MainWindow(account_manager=account_mgr)
        window.show()
        app.exec()

        # If window closed (e.g. from logout, though logout was removed)
        # Since there's no logout, just break
        break

    sys.exit(0)


if __name__ == "__main__":
    main()
