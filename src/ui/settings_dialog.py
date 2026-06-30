"""
Settings Dialog.
Serial port configuration, theme and other app settings.
"""
from __future__ import annotations

import json, os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox
)
from ui.styles import C_PANEL, C_TEXT, C_RED, C_BORDER, C_BTN_BG

# Config path is two levels up from src/ui/settings_dialog.py
CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "config.json"))


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load config.json: {e}")
    return {"serial_port": "", "baud_rate": 9600, "data_dir": "data", "bypass_delay": 3.0}


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(420, 300)
        self.setStyleSheet(f"background: {C_PANEL};")
        self._cfg = load_config()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("System Settings")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self._port_edit = QLineEdit(self._cfg.get("serial_port", ""))
        self._port_edit.setPlaceholderText("e.g. COM3 or /dev/ttyUSB0")
        form.addRow("Bypass Serial Port:", self._port_edit)

        self._baud_combo = QComboBox()
        for b in [9600, 19200, 38400, 57600, 115200]:
            self._baud_combo.addItem(str(b))
        idx = self._baud_combo.findText(str(self._cfg.get("baud_rate", 9600)))
        if idx >= 0:
            self._baud_combo.setCurrentIndex(idx)
        form.addRow("Baud Rate:", self._baud_combo)
        
        self._delay_spin = QDoubleSpinBox()
        self._delay_spin.setRange(0.5, 30.0)
        self._delay_spin.setSingleStep(0.5)
        self._delay_spin.setValue(self._cfg.get("bypass_delay", 3.0))
        form.addRow("Bypass Delay (s):", self._delay_spin)
        
        layout.addLayout(form)
        layout.addSpacing(16)

        # Password Management inside Settings
        pwd_btn = QPushButton("Change System Password...")
        pwd_btn.clicked.connect(self._change_password)
        layout.addWidget(pwd_btn)
        
        layout.addSpacing(8)

        # Clear Data Logs
        clear_btn = QPushButton("Clear Audit Logs & Snapshots")
        clear_btn.setStyleSheet(f"color: {C_RED};")
        clear_btn.clicked.connect(self._clear_data)
        layout.addWidget(clear_btn)

        layout.addSpacing(16)

        save_btn = QPushButton("Save Settings")
        save_btn.setFixedHeight(36)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_BTN_BG}; color: {C_TEXT};
                border: 1px solid {C_BORDER}; border-radius: 6px;
                font-size: 13px; font-weight: 700;
            }}
        """)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

    def _save(self):
        self._cfg["serial_port"] = self._port_edit.text().strip()
        self._cfg["baud_rate"] = int(self._baud_combo.currentText())
        self._cfg["bypass_delay"] = self._delay_spin.value()
        save_config(self._cfg)
        self.accept()



    def _change_password(self):
        from ui.password_dialog import PasswordChangeDialog
        from core.account_manager import AccountManager
        parent = self.parent()
        if parent and hasattr(parent, '_account_mgr'):
            dlg = PasswordChangeDialog(parent._account_mgr, self)
            dlg.exec()
        else:
            # Fallback if opened standalone
            dlg = PasswordChangeDialog(AccountManager(), self)
            dlg.exec()

    def _clear_data(self):
        from PyQt6.QtWidgets import QMessageBox
        from core.data_store import DataStore
        
        reply = QMessageBox.question(
            self, 'Clear Audit Logs',
            "This will delete all bypass event logs and 3D snapshots. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            ds = DataStore(self._cfg.get("data_dir", "data"))
            ds.clear_all_data()
            QMessageBox.information(self, "Success", "All audit logs and snapshots have been cleared.")
