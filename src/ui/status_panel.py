"""
Right-side status panel.
Shows: current occupancy %, status, 24h/7d counts.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QDoubleSpinBox, QPushButton
)
from ui.styles import (
    C_PANEL, C_CARD, C_BORDER, C_ACCENT, C_TEXT2,
    C_GREEN, C_RED, C_TEXT, C_BTN_BG
)

class InfoRow(QFrame):
    """A single labelled value row inside the status panel."""

    def __init__(self, label: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setObjectName("InfoRow")
        self.setStyleSheet(f"#InfoRow {{ background: {C_PANEL}; border: 1px solid {C_BORDER}; border-radius: 8px; padding: 16px; }}")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._lbl = QLabel(label)
        self._lbl.setStyleSheet(f"color: {C_TEXT2}; font-weight: 600; font-size: 13px; background: transparent; border: none; padding: 0;")
        layout.addWidget(self._lbl)

        self._link_btn = QPushButton()
        self._link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._link_btn.setStyleSheet(f"color: #1f6feb; background: transparent; border: none; font-size: 11px; text-decoration: underline; margin-top: 1px;")
        self._link_btn.hide()
        layout.addWidget(self._link_btn)

        layout.addStretch()

        self._val = QLabel(value)
        self._val.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._val.setStyleSheet(f"color: {C_ACCENT}; background: transparent; border: none; padding: 0;")
        self._val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._val)

    def set_value(self, text: str):
        self._val.setText(text)

    def set_color(self, color: str):
        self._val.setStyleSheet(f"color: {color}; background: transparent; border: none; padding: 0;")
        
    def add_link(self, text: str, callback):
        self._link_btn.setText(text)
        self._link_btn.clicked.connect(callback)
        self._link_btn.show()


class StatusPanel(QWidget):
    apply_occupancy_clicked = pyqtSignal(float)
    set_baseline_clicked = pyqtSignal()
    reset_baseline_clicked = pyqtSignal()
    export_csv_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ── Status Overview ──────────────────────────────────────────
        self._occ_row = InfoRow("OCCUPANCY", "0.0%")
        layout.addWidget(self._occ_row)

        self._status_row = InfoRow("STATUS", "ALLOW")
        self._status_row.set_color(C_GREEN)
        layout.addWidget(self._status_row)

        # ── Past 24-HR ───────────────────────────────────────────────
        self._24h_row = InfoRow("PAST 24-HR", "0 rej.")
        self._24h_row.add_link("Export as CSV", self.export_csv_clicked.emit)
        layout.addWidget(self._24h_row)

        # ── Past 7-Day ───────────────────────────────────────────────
        self._7d_row = InfoRow("PAST 7-DAY", "0 rej.")
        self._7d_row.add_link("Export as CSV", self.export_csv_clicked.emit)
        layout.addWidget(self._7d_row)

        layout.addStretch(1)

        # ── Config Controls ──────────────────────────────────────────
        config_box = QFrame()
        config_box.setStyleSheet(f"background: {C_PANEL}; border: 1px solid {C_BORDER}; border-radius: 8px;")
        config_layout = QVBoxLayout(config_box)
        config_layout.setContentsMargins(16, 20, 16, 20)
        config_layout.setSpacing(20)

        # Row 1: Max Occupancy
        occ_layout = QVBoxLayout()
        occ_layout.setSpacing(8)
        occ_lbl = QLabel("Max. Occupancy")
        occ_lbl.setStyleSheet(f"color: {C_TEXT2}; font-weight: 600; font-size: 14px; border: none; background: transparent;")
        occ_layout.addWidget(occ_lbl)
        
        occ_h = QHBoxLayout()
        self._max_occ_spin = QDoubleSpinBox()
        self._max_occ_spin.setRange(1.0, 100.0)
        self._max_occ_spin.setSingleStep(5.0)
        self._max_occ_spin.setValue(80.0)
        self._max_occ_spin.setSuffix("%")
        self._max_occ_spin.setFixedHeight(44)
        self._max_occ_spin.setStyleSheet(f"color: {C_TEXT}; background: {C_CARD}; border: 1px solid {C_BORDER}; padding: 4px 8px; border-radius: 4px; font-size: 16px; font-weight: bold;")
        occ_h.addWidget(self._max_occ_spin, stretch=1)

        apply_btn = QPushButton("Apply")
        apply_btn.setFixedHeight(44)
        apply_btn.setStyleSheet(f"background: #1f6feb; color: white; border: none; border-radius: 4px; padding: 4px 16px; font-weight: bold; font-size: 15px;")
        apply_btn.clicked.connect(lambda: self.apply_occupancy_clicked.emit(self._max_occ_spin.value()))
        occ_h.addWidget(apply_btn)
        occ_layout.addLayout(occ_h)
        config_layout.addLayout(occ_layout)

        # Row 2: Set Baseline
        set_base_btn = QPushButton("Set Baseline")
        set_base_btn.setFixedHeight(50)
        set_base_btn.setStyleSheet(f"background: #1f6feb; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; letter-spacing: 1px;")
        set_base_btn.clicked.connect(lambda: self.set_baseline_clicked.emit())
        config_layout.addWidget(set_base_btn)

        # Row 3: Reset Baseline
        reset_base_btn = QPushButton("Reset Baseline")
        reset_base_btn.setFixedHeight(50)
        reset_base_btn.setStyleSheet(f"background: {C_RED}; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; letter-spacing: 1px;")
        reset_base_btn.clicked.connect(lambda: self.reset_baseline_clicked.emit())
        config_layout.addWidget(reset_base_btn)

        layout.addWidget(config_box)

    # Update methods

    def set_occupancy(self, pct: float):
        self._occ_row.set_value(f"{pct:.1f}%")
        color = C_RED if pct >= 90 else C_ACCENT
        self._occ_row.set_color(color)

    def set_status(self, status: str):
        self._status_row.set_value(status)
        self._status_row.set_color(C_RED if status == "BYPASS" else C_GREEN)

    def set_counts(self, count_24h: int, count_7d: int):
        self._24h_row.set_value(f"{count_24h} rej.")
        self._7d_row.set_value(f"{count_7d} rej.")

    def set_max_occupancy(self, val: float):
        self._max_occ_spin.blockSignals(True)
        self._max_occ_spin.setValue(val)
        self._max_occ_spin.blockSignals(False)
