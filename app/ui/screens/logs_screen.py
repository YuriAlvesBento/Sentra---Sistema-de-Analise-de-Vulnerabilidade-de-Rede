from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from ui.ui_data import RISK_COLORS


class LogsScreen(QWidget):
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.entries: list[dict[str, Any]] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        title = QLabel("Logs do sistema SENTRA")
        title.setObjectName("SectionTitle")
        header_layout.addWidget(title)
        header_layout.addStretch(1)

        self.level_filter = QComboBox()
        self.level_filter.addItems(["Todos", "INFO", "WARN", "ERR", "OK"])
        self.level_filter.currentTextChanged.connect(self._refresh_table)
        header_layout.addWidget(self.level_filter)
        header_layout.addWidget(QPushButton("Exportar"))

        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.clear_requested.emit)
        header_layout.addWidget(clear_button)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Nivel", "Modulo", "Mensagem", "Host origem"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        layout.addLayout(header_layout)
        layout.addWidget(self.table, 1)

    def set_entries(self, entries: list[dict[str, Any]]) -> None:
        self.entries = list(entries)
        self._refresh_table()

    def _refresh_table(self) -> None:
        level_filter = self.level_filter.currentText()
        filtered = [
            entry
            for entry in reversed(self.entries)
            if level_filter == "Todos" or entry["level"] == level_filter
        ]

        self.table.setRowCount(len(filtered))
        for row_index, entry in enumerate(filtered):
            self.table.setItem(row_index, 0, QTableWidgetItem(entry["timestamp"]))

            level_item = QTableWidgetItem(entry["level"])
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if entry["level"] == "ERR":
                background, foreground = RISK_COLORS["CRITICO"]
            elif entry["level"] == "WARN":
                background, foreground = RISK_COLORS["MEDIO"]
            elif entry["level"] == "OK":
                background, foreground = RISK_COLORS["BAIXO"]
            else:
                background, foreground = ("#dcecff", "#1d4f91")
            level_item.setBackground(QColor(background))
            level_item.setForeground(QColor(foreground))

            self.table.setItem(row_index, 1, level_item)
            self.table.setItem(row_index, 2, QTableWidgetItem(entry["module"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(entry["message"]))
            self.table.setItem(row_index, 4, QTableWidgetItem(entry["host"]))
