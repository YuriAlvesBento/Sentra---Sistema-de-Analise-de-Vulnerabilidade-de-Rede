from __future__ import annotations

from PySide6.QtGui import QColor, QPalette


def build_light_palette() -> QPalette:
    palette = QPalette()
    role = QPalette.ColorRole
    group = QPalette.ColorGroup

    palette.setColor(role.Window, QColor("#d8dde6"))
    palette.setColor(role.WindowText, QColor("#112134"))
    palette.setColor(role.Base, QColor("#ffffff"))
    palette.setColor(role.AlternateBase, QColor("#f7faff"))
    palette.setColor(role.ToolTipBase, QColor("#ffffff"))
    palette.setColor(role.ToolTipText, QColor("#112134"))
    palette.setColor(role.Text, QColor("#112134"))
    palette.setColor(role.Button, QColor("#dbe9f7"))
    palette.setColor(role.ButtonText, QColor("#123250"))
    palette.setColor(role.BrightText, QColor("#ffffff"))
    palette.setColor(role.Highlight, QColor("#d7e7f7"))
    palette.setColor(role.HighlightedText, QColor("#0a2b4f"))
    palette.setColor(role.PlaceholderText, QColor("#6b7f94"))

    palette.setColor(group.Disabled, role.WindowText, QColor("#7b8794"))
    palette.setColor(group.Disabled, role.Text, QColor("#7b8794"))
    palette.setColor(group.Disabled, role.ButtonText, QColor("#7b8794"))

    return palette

APP_STYLESHEET = """
QWidget {
    color: #112134;
    background-color: #eef3f8;
}

QMainWindow {
    background: #d8dde6;
    color: #112134;
}

QMenuBar {
    background: #f2f5f9;
    border-bottom: 1px solid #bcc8d8;
    padding: 3px;
}

QMenuBar::item {
    padding: 6px 10px;
    background: transparent;
}

QMenuBar::item:selected,
QMenu::item:selected {
    background: #d7e7f7;
    color: #0a2b4f;
}

QMenu,
QToolBar {
    background: #f8fbff;
    border: 1px solid #cad4e2;
    color: #112134;
}

QToolButton {
    background: #dbe9f7;
    border: 1px solid #b2c4d8;
    border-radius: 8px;
    padding: 6px 10px;
    color: #123250;
}

QToolButton:hover {
    background: #cfe1f5;
}

QToolButton:pressed {
    background: #bdd5ef;
}

QToolBar {
    spacing: 6px;
    padding: 6px;
}

QStatusBar {
    background: #f2f5f9;
    border-top: 1px solid #bcc8d8;
}

QWidget#SidebarPane,
QWidget#DetailPane,
QWidget#BottomLogPane,
QWidget#CenterPane {
    background: #eef3f8;
}

QScrollArea {
    border: none;
    background: transparent;
}

QAbstractScrollArea {
    background: #eef3f8;
    color: #112134;
}

QLabel,
QCheckBox,
QRadioButton,
QGroupBox,
QStatusBar,
QTreeWidget,
QListWidget,
QTableWidget,
QTextEdit,
QLineEdit,
QComboBox,
QSpinBox,
QProgressBar {
    color: #112134;
}

QCheckBox,
QRadioButton {
    spacing: 8px;
}

QCheckBox::indicator,
QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QTreeWidget,
QTableWidget,
QListWidget,
QTextEdit,
QLineEdit,
QComboBox,
QSpinBox {
    background: #ffffff;
    border: 1px solid #bcc8d8;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: #d7e7f7;
    selection-color: #0a2b4f;
}

QTreeWidget::item {
    padding: 6px 4px;
}

QTreeWidget::item:selected,
QListWidget::item:selected,
QTableWidget::item:selected {
    background: #d7e7f7;
    color: #0a2b4f;
}

QTabWidget::pane {
    border: 1px solid #cad4e2;
    background: #eef3f8;
}

QTabBar::tab {
    background: #dbe5f0;
    border: 1px solid #bcc8d8;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 130px;
    padding: 9px 16px;
    margin-right: 4px;
    color: #18324b;
}

QTabBar::tab:selected {
    background: #eef3f8;
    font-weight: 600;
    color: #15324c;
}

QTabBar::scroller {
    width: 28px;
}

QGroupBox {
    border: 1px solid #cad4e2;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 12px;
    background: #f7faff;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #15324c;
}

QHeaderView::section {
    background: #dbe5f0;
    color: #18324b;
    border: none;
    border-bottom: 1px solid #bcc8d8;
    border-right: 1px solid #d3dce8;
    padding: 7px 6px;
    font-weight: 600;
}

QPushButton {
    background: #dbe9f7;
    border: 1px solid #b2c4d8;
    border-radius: 8px;
    padding: 8px 12px;
    color: #123250;
}

QPushButton:hover {
    background: #cfe1f5;
}

QPushButton:pressed {
    background: #bdd5ef;
}

QPushButton:disabled {
    background: #e6edf5;
    color: #7b8794;
}

QLabel#PaneTitle,
QLabel#SectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #15324c;
}

QLabel#MutedLabel {
    color: #556779;
}

QLineEdit[readOnly="true"] {
    background: #f6f8fb;
    color: #4a5d72;
}

QTextEdit {
    font-family: Consolas, 'Courier New', monospace;
}

QTableWidget {
    alternate-background-color: #f7faff;
    gridline-color: #d6e0eb;
}

QScrollBar:vertical {
    background: #e7edf4;
    width: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #b8c8d9;
    min-height: 24px;
    border-radius: 6px;
}

QScrollBar:horizontal {
    background: #e7edf4;
    height: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #b8c8d9;
    min-width: 24px;
    border-radius: 6px;
}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {
    background: transparent;
    border: none;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #112134;
    selection-background-color: #d7e7f7;
    selection-color: #0a2b4f;
}

QProgressBar {
    background: #ffffff;
    border: 1px solid #bcc8d8;
    border-radius: 6px;
    text-align: center;
    padding: 2px;
}

QProgressBar::chunk {
    background: #4e8fd0;
    border-radius: 4px;
}

QSplitter::handle {
    background: #d2dbe6;
}

QFrame#StatusChip {
    background: #ffffff;
    border: 1px solid #bcc8d8;
    border-radius: 8px;
}

QFrame#StatusChip QLabel {
    color: #15324c;
}

QLabel#StatusDot {
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
    border-radius: 5px;
    background: #6b7785;
}

QLabel#StatusDot[dotState="ready"] {
    background: #2f9e44;
}

QLabel#StatusDot[dotState="running"] {
    background: #e0a800;
}

QLabel#StatusDot[dotState="stopped"] {
    background: #c92a2a;
}

QLabel#StatusDot[dotState="idle"] {
    background: #6b7785;
}
"""
