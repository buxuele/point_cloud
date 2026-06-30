"""
Password dialogs for system settings authentication.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from ui.styles import C_PANEL, C_TEXT, C_BTN_BG, C_BORDER, C_ACCENT, C_RED

class PasswordVerifyDialog(QDialog):
    """Dialog to verify the user's password."""
    def __init__(self, account_mgr, parent=None):
        super().__init__(parent)
        self.account_mgr = account_mgr
        self.setWindowTitle("Authentication Required")
        self.setFixedSize(320, 180)
        self.setStyleSheet(f"background: {C_PANEL};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl = QLabel("Enter your password to continue:")
        lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 13px;")
        layout.addWidget(lbl)

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setFixedHeight(36)
        self.pass_edit.setStyleSheet(f"color: {C_TEXT}; background: #0a0e14; border: 1px solid {C_BORDER}; border-radius: 4px; padding: 0 8px;")
        layout.addWidget(self.pass_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(80, 32)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_TEXT}; border: 1px solid {C_BORDER}; border-radius: 4px; font-weight: bold; }}")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(80, 32)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet(f"QPushButton {{ background: {C_BTN_BG}; color: {C_TEXT}; border: none; border-radius: 4px; font-weight: bold; }}")
        ok_btn.clicked.connect(self._verify)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _verify(self):
        pwd = self.pass_edit.text()
        if self.account_mgr.verify_password(pwd):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Incorrect password.")
            self.pass_edit.clear()
            self.pass_edit.setFocus()


class PasswordChangeDialog(QDialog):
    """Dialog to change the user's password."""
    def __init__(self, account_mgr, parent=None):
        super().__init__(parent)
        self.account_mgr = account_mgr
        self.setWindowTitle("Change Your Password")
        self.setFixedSize(360, 260)
        self.setStyleSheet(f"background: {C_PANEL};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        def make_row(label_text: str):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 13px;")
            edit = QLineEdit()
            edit.setEchoMode(QLineEdit.EchoMode.Password)
            edit.setFixedHeight(36)
            edit.setStyleSheet(f"color: {C_TEXT}; background: #0a0e14; border: 1px solid {C_BORDER}; border-radius: 4px; padding: 0 8px;")
            layout.addWidget(lbl)
            layout.addWidget(edit)
            return edit

        self.old_edit = make_row("Old Password:")
        self.new_edit = make_row("New Password:")
        self.confirm_edit = make_row("Confirm New Password:")

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(80, 32)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C_TEXT}; border: 1px solid {C_BORDER}; border-radius: 4px; font-weight: bold; }}")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setFixedSize(80, 32)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"QPushButton {{ background: {C_BTN_BG}; color: {C_TEXT}; border: none; border-radius: 4px; font-weight: bold; }}")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _save(self):
        old_pwd = self.old_edit.text()
        new_pwd = self.new_edit.text()
        conf_pwd = self.confirm_edit.text()

        if not old_pwd or not new_pwd:
            QMessageBox.warning(self, "Error", "Fields cannot be empty.")
            return

        if new_pwd != conf_pwd:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return

        ok, msg = self.account_mgr.change_password(old_pwd, new_pwd)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)
            self.old_edit.clear()
            self.old_edit.setFocus()
