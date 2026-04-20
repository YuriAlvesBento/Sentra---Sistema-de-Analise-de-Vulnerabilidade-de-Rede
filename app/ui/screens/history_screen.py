from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from ui.ui_data import HISTORY_ROWS, RISK_COLORS


class HistoryScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        title = QLabel("Historico de scans")
        title.setObjectName("SectionTitle")
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(QPushButton("Excluir"))

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "Data/Hora",
                "Alvo",
                "Tipo de scan",
                "Hosts",
                "Achados",
                "Risco geral",
                "Duracao",
                "Operador",
            ]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setRowCount(len(HISTORY_ROWS))

        for row_index, row in enumerate(HISTORY_ROWS):
            self.table.setItem(row_index, 0, QTableWidgetItem(row["datetime"]))
            self.table.setItem(row_index, 1, QTableWidgetItem(row["target"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(row["scan_type"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(row["hosts"]))
            self.table.setItem(row_index, 4, QTableWidgetItem(row["findings"]))

            risk_item = QTableWidgetItem(row["risk"])
            risk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            background, foreground = RISK_COLORS.get(row["risk"], ("#ffffff", "#1f2937"))
            risk_item.setBackground(QColor(background))
            risk_item.setForeground(QColor(foreground))
            self.table.setItem(row_index, 5, risk_item)

            self.table.setItem(row_index, 6, QTableWidgetItem(row["duration"]))
            self.table.setItem(row_index, 7, QTableWidgetItem(row["operator"]))

        layout.addLayout(header_layout)
        layout.addWidget(self.table, 1)
