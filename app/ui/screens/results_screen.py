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

from ui.ui_data import RESULT_COLUMNS, RESULT_ROWS, RISK_COLORS, STATUS_COLORS


class ResultsScreen(QWidget):
    result_selected = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.all_rows = list(RESULT_ROWS)
        self.rows = list(self.all_rows)
        self._build_ui()
        self._populate_table()

    def set_rows(self, rows: list[dict[str, str]]) -> None:
        self.all_rows = list(rows)
        self.rows = list(rows)
        self._populate_table()

    def set_scan_target(self, target: str) -> None:
        normalized_target = target.strip() or "escopo nao informado"
        self.title_label.setText(f"Resultados do scan - {normalized_target}")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Resultados do scan - 192.168.1.0/24")
        self.title_label.setObjectName("SectionTitle")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(QPushButton("Filtrar"))
        header_layout.addWidget(QPushButton("Exportar"))

        self.risk_filter = QComboBox()
        self.risk_filter.addItems(
            ["Todos os riscos", "CRITICO", "ALTO", "MEDIO", "BAIXO"]
        )
        self.risk_filter.currentTextChanged.connect(self._apply_filter)
        header_layout.addWidget(self.risk_filter)

        self.table = QTableWidget()
        self.table.setColumnCount(len(RESULT_COLUMNS))
        self.table.setHorizontalHeaderLabels([label for label, _ in RESULT_COLUMNS])
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
            for col_index, (_, key) in enumerate(RESULT_COLUMNS):
                item = QTableWidgetItem(str(row.get(key, "-")))

                if key == "risk":
                    background, foreground = RISK_COLORS.get(
                        row["risk"], ("#ffffff", "#1f2937")
                    )
                    item.setBackground(QColor(background))
                    item.setForeground(QColor(foreground))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif key == "status":
                    item.setForeground(QColor(STATUS_COLORS.get(row["status"], "#1f2937")))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif key in {"port", "protocol"}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.table.setItem(row_index, col_index, item)

        if self.rows:
            host_count = len({row["ip"] for row in self.rows if row.get("ip")})
            counts = {
                risk: sum(1 for row in self.rows if row.get("risk") == risk)
                for risk in ("CRITICO", "ALTO", "MEDIO", "BAIXO")
            }
            self.summary_label.setText(
                f"{len(self.rows)} registros | {host_count} hosts ativos | "
                f"{counts['CRITICO']} criticos, {counts['ALTO']} altos, "
                f"{counts['MEDIO']} medios, {counts['BAIXO']} baixos"
            )
            self.table.selectRow(0)
            self._emit_selected_row()
        else:
            self.summary_label.setText("Nenhum resultado disponivel para o scan atual.")

    def _apply_filter(self, selected_risk: str) -> None:
        if selected_risk == "Todos os riscos":
            self.rows = list(self.all_rows)
        else:
            self.rows = [
                row for row in self.all_rows if row["risk"] == selected_risk
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
            "port": f"{row['port']}/{row['protocol']}",
            "service": row["service"],
            "os": row["os"],
            "risk": row["risk"],
            "reference": row["reference"],
            "cvss": row["cvss"],
            "detected_at": row["detected_at"],
            "description": row["description"],
            "recommendation": row["recommendation"],
        }
        self.result_selected.emit(detail)
