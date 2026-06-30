"""
Left sidebar: elevator list + system links.
"""
from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QSizePolicy
)
from ui.styles import (
    C_SIDEBAR, C_BORDER, C_ACCENT, C_TEXT, C_TEXT2,
    C_TEXT3, C_GREEN, C_RED, C_CARD, C_BTN_BG
)


class ElevatorListWidget(QWidget):
    elevator_selected = pyqtSignal(str)   # elevator_id
    add_elevator_clicked = pyqtSignal()
    account_manage_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: dict[str, QListWidgetItem] = {}   # id → item
        self._build_ui()
        self.setFixedWidth(200)

    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {C_SIDEBAR};
                border-right: 1px solid {C_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet(f"background-color: {C_SIDEBAR}; border-bottom: 1px solid {C_BORDER};")
        header.setFixedHeight(52)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        lbl = QLabel("Elevators")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {C_TEXT}; border: none;")
        hl.addWidget(lbl)
        layout.addWidget(header)

        # List
        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {C_SIDEBAR};
                border: none;
                padding: 8px 4px;
            }}
            QListWidget::item {{
                padding: 9px 12px;
                border-radius: 6px;
                color: {C_TEXT2};
                font-size: 13px;
            }}
            QListWidget::item:selected {{
                background-color: #2b313a;
                color: #ffffff;
            }}
        """)
        self._list.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._list)

        # Add button
        add_btn = QPushButton("+ Elevator")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_BTN_BG};
                color: {C_TEXT};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                margin: 4px 12px;
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        add_btn.clicked.connect(self.add_elevator_clicked)
        layout.addWidget(add_btn)

        layout.addStretch()

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {C_BORDER}; border: none; background: {C_BORDER}; max-height: 1px;")
        layout.addWidget(div)

        layout.addSpacing(12)

    # Public API

    def add_elevator(self, elevator_id: str, connected: bool = True):
        item = QListWidgetItem(elevator_id)
        item.setData(Qt.ItemDataRole.UserRole, elevator_id)
        self._list.addItem(item)
        self._items[elevator_id] = item
        self.set_status(elevator_id, connected)
        if self._list.count() == 1:
            self._list.setCurrentItem(item)

    def remove_elevator(self, elevator_id: str):
        item = self._items.pop(elevator_id, None)
        if item:
            row = self._list.row(item)
            self._list.takeItem(row)

    def set_status(self, elevator_id: str, connected: bool, bypass: bool = False):
        item = self._items.get(elevator_id)
        if not item:
            return
        item.setText(elevator_id)

    def _on_selection(self, current, previous):
        if current:
            eid = current.data(Qt.ItemDataRole.UserRole)
            self.elevator_selected.emit(eid)

    def select_elevator(self, elevator_id: str):
        item = self._items.get(elevator_id)
        if item:
            self._list.setCurrentItem(item)

    def current_elevator(self) -> str | None:
        item = self._list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None
