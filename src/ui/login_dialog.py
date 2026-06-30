"""
Login Dialog.
Updated to support Admin / User login using the AccountManager.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox
)
import os

from ui.styles import C_PANEL, C_TEXT, C_BTN_BG, C_BORDER

class LoginDialog(QDialog):
    def __init__(self, account_mgr, parent=None):
        super().__init__(parent)
        self.account_mgr = account_mgr
        self.setWindowTitle("LiDAR Lift Monitor - Login")
        self.setFixedSize(380, 300)
        self.setStyleSheet(f"background: {C_PANEL};")
        self._build_ui()

    def _build_ui(self):
        from PyQt6.QtCore import QSettings
        self.settings = QSettings()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("System Login")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(8)

        # Username input
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Enter username")
        self.user_edit.setFixedHeight(40)
        self.user_edit.setStyleSheet(f"""
            QLineEdit {{
                background: #0a0e14;
                color: {C_TEXT};
                border: 1px solid {C_BORDER};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.user_edit)

        # Password input
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Enter password")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setFixedHeight(40)
        self.pass_edit.setStyleSheet(f"""
            QLineEdit {{
                background: #0a0e14;
                color: {C_TEXT};
                border: 1px solid {C_BORDER};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.pass_edit)

        # Remember username checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.remember_cb = QCheckBox("Remember Username")
        self.remember_cb.setStyleSheet(f"color: {C_TEXT}; font-size: 13px;")
        
        # Load saved username
        saved_user = self.settings.value("login/username", "")
        remember = self.settings.value("login/remember", False, type=bool)
        if remember and saved_user:
            self.user_edit.setText(saved_user)
            self.remember_cb.setChecked(True)
        else:
            self.remember_cb.setChecked(True) # Default checked

        layout.addWidget(self.remember_cb)

        layout.addStretch()

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(40)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Removed hover animation as per global rules
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_BTN_BG};
                color: {C_TEXT};
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        login_btn.clicked.connect(self._do_login)
        layout.addWidget(login_btn)

    def _do_login(self):
        user = self.user_edit.text().strip()
        pwd = self.pass_edit.text()
        
        if self.account_mgr.login(user, pwd):
            if self.remember_cb.isChecked():
                self.settings.setValue("login/username", user)
                self.settings.setValue("login/remember", True)
            else:
                self.settings.setValue("login/username", "")
                self.settings.setValue("login/remember", False)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Incorrect username or password")
            self.pass_edit.clear()
            self.pass_edit.setFocus()

