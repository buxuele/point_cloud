"""
Account Management Dialog (Admin only).
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from ui.styles import C_PANEL, C_CARD, C_BORDER, C_TEXT, C_TEXT2, C_RED, C_BTN_BG


class AccountDialog(QDialog):
    def __init__(self, account_manager, parent=None):
        super().__init__(parent)
        self._mgr = account_manager
        self.setWindowTitle("Account Management")
        self.setMinimumSize(560, 480)
        self.setStyleSheet(f"background: {C_PANEL};")
        self._build_ui()
        self._load_accounts()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Account Management")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        # Account table
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Username", "Role"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setFixedHeight(200)
        layout.addWidget(self._table)

        # Delete button
        del_btn = QPushButton("Delete Selected")
        del_btn.setProperty("danger", True)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_RED}; color: white; border: none;
                border-radius: 6px; padding: 6px 16px; font-weight: 600;
            }}
        """)
        del_btn.clicked.connect(self._delete_selected)
        layout.addWidget(del_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add new account form
        add_label = QLabel("Add New Account")
        add_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        add_label.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(add_label)

        form = QFormLayout()
        form.setSpacing(10)

        self._new_user = QLineEdit()
        self._new_user.setPlaceholderText("Username")
        self._new_user.setFixedHeight(36)
        form.addRow("Username:", self._new_user)

        self._new_pass = QLineEdit()
        self._new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pass.setPlaceholderText("Password")
        self._new_pass.setFixedHeight(36)
        form.addRow("Password:", self._new_pass)

        self._role_combo = QComboBox()
        self._role_combo.addItems(["user", "admin"])
        form.addRow("Role:", self._role_combo)

        layout.addLayout(form)

        self._err_lbl = QLabel("")
        self._err_lbl.setStyleSheet(f"color: {C_RED}; font-size: 12px;")
        layout.addWidget(self._err_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton("Add Account")
        add_btn.setFixedHeight(36)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_BTN_BG}; color: {C_TEXT};
                border: 1px solid {C_BORDER}; border-radius: 6px;
                font-size: 13px; font-weight: 700;
            }}
        """)
        add_btn.clicked.connect(self._add_account)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

    def _load_accounts(self):
        self._table.setRowCount(0)
        for acc in self._mgr.get_all_accounts():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(acc["username"]))
            self._table.setItem(row, 1, QTableWidgetItem(acc["role"]))

    def _add_account(self):
        self._err_lbl.setText("")
        username = self._new_user.text().strip()
        password = self._new_pass.text()
        role = self._role_combo.currentText()

        if not username or not password:
            self._err_lbl.setText("[ERROR] Username and password required.")
            return

        ok, msg = self._mgr.add_account(username, password, role)
        if ok:
            self._new_user.clear()
            self._new_pass.clear()
            self._load_accounts()
        else:
            self._err_lbl.setText(f"[ERROR] {msg}")

    def _delete_selected(self):
        rows = self._table.selectedItems()
        if not rows:
            return
        username = self._table.item(self._table.currentRow(), 0).text()
        ok, msg = self._mgr.remove_account(username)
        if ok:
            self._load_accounts()
        else:
            self._err_lbl.setText(f"[ERROR] {msg}")
