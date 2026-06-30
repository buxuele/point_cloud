"""
Bypass Frequency Chart widget.
Shows a line chart of bypass events over 24H / 7D / Custom range.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDateEdit, QSizePolicy, QFileDialog
)
from PyQt6.QtCore import QDate
import pyqtgraph as pg

from ui.styles import C_PANEL, C_CARD, C_BORDER, C_ACCENT, C_TEXT, C_TEXT2, C_TEXT3


class ChartWidget(QWidget):
    """
    Bypass frequency chart with time-range toggle buttons.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[dict] = []
        self._build_ui()

    def _build_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_PANEL}; border-top: 1px solid {C_BORDER};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        # Header row
        header = QHBoxLayout()
        header.addStretch()

        # Range buttons
        self._range_btns: dict[str, QPushButton] = {}
        for label in ["24H", "7D", "Custom"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            # Increase width for "Custom" to avoid truncation
            btn.setFixedSize(80 if label == "Custom" else 60, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_CARD}; color: {C_TEXT2};
                    border: 1px solid {C_BORDER}; border-radius: 5px;
                    font-size: 11px; font-weight: 600;
                }}
                QPushButton:checked {{
                    background: {C_TEXT}; color: {C_PANEL}; border: none;
                }}
            """)
            btn.clicked.connect(lambda checked, l=label: self._on_range(l))
            header.addWidget(btn)
            self._range_btns[label] = btn

        self._range_btns["24H"].setChecked(True)
        layout.addLayout(header)

        # Custom date row (hidden by default)
        self._custom_row = QWidget()
        self._custom_row.setStyleSheet("background: transparent;")
        cr_layout = QHBoxLayout(self._custom_row)
        cr_layout.setContentsMargins(0, 0, 0, 0)

        cr_layout.addWidget(QLabel("From:"))
        self._from_date = QDateEdit(QDate.currentDate().addDays(-30))
        self._from_date.setCalendarPopup(True)
        cr_layout.addWidget(self._from_date)

        cr_layout.addWidget(QLabel("To:"))
        self._to_date = QDateEdit(QDate.currentDate())
        self._to_date.setCalendarPopup(True)
        cr_layout.addWidget(self._to_date)

        apply_btn = QPushButton("Apply")
        apply_btn.setFixedWidth(60)
        apply_btn.clicked.connect(self._refresh_chart)
        cr_layout.addWidget(apply_btn)
        cr_layout.addStretch()
        self._custom_row.setVisible(False)
        layout.addWidget(self._custom_row)

        # pyqtgraph PlotWidget
        pg.setConfigOption("background", C_PANEL)
        pg.setConfigOption("foreground", C_TEXT2)

        self._plot = pg.PlotWidget()
        self._plot.setMinimumHeight(160)  # Increased from 120 to 160 to fit the word "Events" vertically
        self._plot.showGrid(x=True, y=True, alpha=0.15)
        
        left_axis = self._plot.getAxis("left")
        left_axis.setLabel("Bypass Events", color=C_TEXT2)
        left_axis.enableAutoSIPrefix(False)
        left_axis.setWidth(75)  # Increased from 50 to 75 to ensure "Events" isn't cut off
        
        self._plot.getAxis("bottom").setLabel("Time", color=C_TEXT2)
        self._plot.getAxis("bottom").enableAutoSIPrefix(False)
        self._plot.setMouseEnabled(x=True, y=False)
        self._plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Style the plot background
        self._plot.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px;")

        layout.addWidget(self._plot)

        # Removed blue, using white/grey
        self._curve = self._plot.plot(
            pen=pg.mkPen(color=C_TEXT, width=3),
            fillLevel=0,
            brush=pg.mkBrush(230, 237, 243, 90), # whiteish with alpha
            antialias=True
        )

    # Public API

    def load_data(self, events: List[dict]):
        """events: list of {'timestamp': ISO str, 'occupancy_pct': float}"""
        self._data = events
        self._refresh_chart()

    def _on_range(self, label: str):
        for k, b in self._range_btns.items():
            b.setChecked(k == label)
        self._custom_row.setVisible(label == "Custom")
        if label != "Custom":
            self._refresh_chart()

    def _refresh_chart(self):
        """Re-plot based on current range selection."""
        now = datetime.utcnow()

        if self._range_btns["24H"].isChecked():
            since = now - timedelta(hours=24)
        elif self._range_btns["7D"].isChecked():
            since = now - timedelta(days=7)
        else:
            since = datetime(
                self._from_date.date().year(),
                self._from_date.date().month(),
                self._from_date.date().day()
            )

        filtered = []
        for ev in self._data:
            try:
                ts = datetime.fromisoformat(ev["timestamp"])
                if ts >= since:
                    filtered.append(ts.timestamp())
            except Exception as e:
                print(f"[WARN] Failed to parse timestamp {ev.get('timestamp')}: {e}")

        if not filtered:
            self._curve.setData([], [])
            return

        # Bin events into time slots
        filtered.sort()
        start_ts = since.timestamp()
        end_ts = now.timestamp()
        
        # 60 bins for smooth appearance
        bins = np.linspace(start_ts, end_ts, 60)
        counts, _ = np.histogram(filtered, bins=bins)
        
        # Smooth data with a simple moving average for the "spline" look
        window = np.ones(3) / 3.0
        smoothed = np.convolve(counts, window, mode='same')
        
        x = (bins[:-1] + bins[1:]) / 2
        y = smoothed
        
        self._curve.setData(x=x, y=y)

        # Prettier x axis with timestamps
        ax = self._plot.getAxis("bottom")
        ax.setTicks([[(ts, datetime.fromtimestamp(ts).strftime("%m/%d %H:%M"))
                      for ts in x[::max(1, len(x)//6)]]])
