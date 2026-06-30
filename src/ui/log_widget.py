"""
System log widget — scrolling dark terminal-style log.
"""
from __future__ import annotations

from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLabel, QPushButton
from ui.styles import C_BORDER, C_TEXT, C_TEXT2, C_TEXT3, C_ACCENT, C_GREEN, C_RED, C_CARD


class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumHeight(150)
        self.setStyleSheet(f"background: #0a0e14; border-top: 1px solid {C_BORDER};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)



        # Text area
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(QFont("Courier New", 11))
        self._text.setStyleSheet(f"""
            QTextEdit {{
                background: #0a0e14;
                color: {C_TEXT};
                border: none;
                padding: 6px 12px;
                selection-background-color: {C_CARD};
            }}
        """)
        layout.addWidget(self._text)

    # Public API

    def append(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        # Colour-code by prefix
        if "[ERROR]" in message:
            color = C_RED
        elif "[WARN]" in message or "BYPASS" in message:
            color = C_TEXT # Use white instead of yellow to stick to pure monochrome/red/green
        elif "[MOCK]" in message:
            color = C_TEXT3
        elif "[INFO]" in message or "[SDK]" in message:
            color = C_GREEN
        else:
            color = C_TEXT

        html = f'<span style="color:{C_TEXT3}">{ts}</span> <span style="color:{color}">{message}</span>'
        self._text.append(html)

        # Auto-scroll to bottom
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._text.setTextCursor(cursor)

    def _clear(self):
        self._text.clear()
