from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
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

from ui.ui_data import FINDING_COLUMNS, FINDING_ROWS, RISK_COLORS


class VulnerabilitiesScreen(QWidget):
    finding_selected = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.all_rows = list(FINDING_ROWS)
        self.rows = list(self.all_rows)
        self._build_ui()
        self._populate_table()

    def set_rows(self, rows: list[dict[str, str]]) -> None:
        self.all_rows = list(rows)
        self.rows = list(rows)
        self._populate_table()

    def set_scan_target(self, target: str) -> None:
        normalized_target = target.strip() or "escopo nao informado"
        self.title_label.setText(f"Vulnerabilidades e exposicoes - {normalized_target}")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Vulnerabilidades e exposicoes")
        self.title_label.setObjectName("SectionTitle")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(
            ["Todas", "CRITICO", "ALTO", "MEDIO", "BAIXO"]
        )
        self.severity_filter.currentTextChanged.connect(self._apply_filter)
        header_layout.addWidget(self.severity_filter)
        header_layout.addWidget(QPushButton("Exportar achados"))
        header_layout.addWidget(QPushButton("Filtrar"))

        self.table = QTableWidget()
        self.table.setColumnCount(len(FINDING_COLUMNS))
        self.table.setHorizontalHeaderLabels([label for label, _ in FINDING_COLUMNS])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.itemSelectionChanged.connect(self._emit_selected_row)

        self.summary_label = QLabel()

        layout.addLayout(header_layout)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.summary_label)

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self.rows))

        for row_index, row in enumerate(self.rows):
            for col_index, (_, key) in enumerate(FINDING_COLUMNS):
                item = QTableWidgetItem(str(row.get(key, "-")))

                if key == "severity":
                    background, foreground = RISK_COLORS.get(
                        row["severity"], ("#ffffff", "#1f2937")
                    )
                    item.setBackground(QColor(background))
                    item.setForeground(QColor(foreground))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif key == "cvss":
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.table.setItem(row_index, col_index, item)

        if self.rows:
            counts = {
                risk: sum(1 for row in self.rows if row["severity"] == risk)
                for risk in ("CRITICO", "ALTO", "MEDIO", "BAIXO")
            }
            self.summary_label.setText(
                f"{len(self.rows)} achados relevantes | {counts['CRITICO']} criticos | "
                f"{counts['ALTO']} altos | {counts['MEDIO']} medios | CVSS medio: 8.7"
            )
            self.table.selectRow(0)
            self._emit_selected_row()
        else:
            self.summary_label.setText("Nenhum achado relevante para o scan atual.")

    def _apply_filter(self, selected_severity: str) -> None:
        if selected_severity == "Todas":
            self.rows = list(self.all_rows)
        else:
            self.rows = [
                row for row in self.all_rows if row["severity"] == selected_severity
            ]
        self._populate_table()

    def _emit_selected_row(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.rows):
            return

        row = self.rows[current_row]
        detail = {
            "host": row["host"],
            "ip": row["ip"],
            "port": row["service_port"],
            "service": row["service"],
            "os": row["os"],
            "risk": row["risk"],
            "reference": row["reference"],
            "cvss": row["cvss"],
            "detected_at": row["detected_at"],
            "description": row["description"],
            "recommendation": row["recommendation"],
        }
        self.finding_selected.emit(detail)
