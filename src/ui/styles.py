"""
Global dark-theme stylesheet and color constants.
Monochrome palette — no decorative accent colors.
"""

# Color palette — pure monochrome + functional status colors only
C_BG          = "#0a0c10"
C_SIDEBAR     = "#0d1117"
C_PANEL       = "#161b22"
C_CARD        = "#1c2128"
C_BORDER      = "#30363d"
C_GREEN       = "#3fb950"
C_RED         = "#f85149"
C_YELLOW      = "#d29922"
C_TEXT        = "#e6edf3"
C_TEXT2       = "#8b949e"
C_TEXT3       = "#484f58"

# Semantic aliases
C_ACCENT      = C_TEXT
C_BTN_BG      = "#30363d"
C_BTN_ACTIVE  = "#3d444d"

STYLESHEET = f"""
/* Global */
QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "SF Pro Text", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {C_BG};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {C_PANEL};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {C_PANEL};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {C_BORDER};
    border-radius: 4px;
}}

/* Buttons — neutral, no colored backgrounds */
QPushButton {{
    background-color: {C_BTN_BG};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:pressed {{
    background-color: {C_BTN_ACTIVE};
}}
QPushButton:disabled {{
    background-color: {C_CARD};
    color: {C_TEXT3};
    border-color: {C_CARD};
}}

QPushButton[danger="true"] {{
    background-color: {C_RED};
    border: none;
    color: white;
}}

QPushButton[secondary="true"] {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    color: {C_TEXT2};
}}

/* Line Edits */
QLineEdit {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {C_TEXT};
    selection-background-color: {C_BTN_ACTIVE};
}}
QLineEdit:focus {{
    border-color: {C_TEXT2};
}}

/* Combo Box */
QComboBox {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    color: {C_TEXT};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {C_PANEL};
    border: 1px solid {C_BORDER};
    selection-background-color: {C_BTN_ACTIVE};
    color: {C_TEXT};
}}

/* Labels */
QLabel {{
    background-color: transparent;
}}

/* Group Box */
QGroupBox {{
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    color: {C_TEXT2};
    font-size: 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    background-color: {C_BG};
}}

/* Table Widget */
QTableWidget {{
    background-color: {C_PANEL};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    gridline-color: {C_BORDER};
    selection-background-color: {C_BTN_ACTIVE};
}}
QHeaderView::section {{
    background-color: {C_CARD};
    color: {C_TEXT2};
    border: none;
    border-bottom: 1px solid {C_BORDER};
    padding: 6px 10px;
    font-weight: 600;
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 4px 8px;
}}

/* List Widget */
QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
}}
QListWidget::item {{
    padding: 8px 12px;
    border-radius: 6px;
    color: {C_TEXT2};
}}
QListWidget::item:selected {{
    background-color: {C_CARD};
    color: {C_TEXT};
}}

/* Tooltip */
QToolTip {{
    background-color: {C_PANEL};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {C_BORDER};
}}

/* Message Box */
QMessageBox {{
    background-color: {C_CARD};
}}

/* Tab Widget (Minimalist text toggle) */
QTabWidget {{
    background-color: {C_BG};
    border: none;
}}
QTabWidget::pane {{
    border: none;
    background-color: {C_BG};
}}
QTabBar {{
    background-color: {C_BG};
    border: none;
}}
QTabBar::tab {{
    background-color: {C_BG};
    color: {C_TEXT3};
    border: none;
    padding: 8px 16px;
    margin-right: 16px;
    font-weight: 600;
    font-size: 14px;
}}
QTabBar::tab:selected {{
    background-color: {C_BG};
    color: {C_TEXT};
    border: none;
    border-bottom: 2px solid {C_TEXT};
}}

/* Spin Box & Double Spin Box */
QSpinBox, QDoubleSpinBox {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    color: {C_TEXT};
}}
"""
