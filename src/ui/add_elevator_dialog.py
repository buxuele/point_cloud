"""
Add Elevator Dialog.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSpinBox
)
from ui.styles import C_PANEL, C_BORDER, C_TEXT, C_TEXT2, C_RED, C_BTN_BG


class AddElevatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Elevator")
        self.setFixedSize(400, 360)
        self.setStyleSheet(f"background: {C_PANEL};")
        self._result = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Add New Elevator")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Elevator 1")
        self._name_edit.setFixedHeight(36)
        form.addRow("Name:", self._name_edit)

        self._ip_edit = QLineEdit("192.168.30.202")
        self._ip_edit.setFixedHeight(36)
        form.addRow("Sensor IP:", self._ip_edit)

        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(12345)
        self._port_spin.setFixedHeight(36)
        form.addRow("Port:", self._port_spin)

        self._occ_edit = QLineEdit("80")
        self._occ_edit.setFixedHeight(36)
        form.addRow("Max Occupancy (%):", self._occ_edit)

        layout.addLayout(form)

        self._err = QLabel("")
        self._err.setStyleSheet(f"color: {C_RED}; font-size: 12px;")
        layout.addWidget(self._err)

        layout.addStretch()

        ok = QPushButton("Add Elevator")
        ok.setFixedHeight(36)
        ok.setCursor(Qt.CursorShape.PointingHandCursor)
        ok.setStyleSheet(f"""
            QPushButton {{
                background: {C_BTN_BG}; color: {C_TEXT};
                border: 1px solid {C_BORDER}; border-radius: 6px;
                font-size: 13px; font-weight: 700;
            }}
        """)
        ok.clicked.connect(self._on_ok)
        layout.addWidget(ok)

    def _on_ok(self):
        name = self._name_edit.text().strip()
        ip = self._ip_edit.text().strip()
        if not name:
            self._err.setText("[ERROR] Please enter a name.")
            return
        try:
            max_occ = float(self._occ_edit.text().replace("%", "").strip())
        except ValueError:
            self._err.setText("[ERROR] Invalid occupancy value.")
            return

        self._result = {
            "name": name,
            "ip": ip,
            "port": self._port_spin.value(),
            "max_occupancy": max_occ,
        }
        self.accept()

    def get_result(self) -> dict | None:
        return self._result
