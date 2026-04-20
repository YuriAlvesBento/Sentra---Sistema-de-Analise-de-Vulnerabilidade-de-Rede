from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from modules.reports.report_service import ReportExportError, ReportService
from ui.ui_data import FINDING_ROWS, HISTORY_ROWS, REPORT_ROWS, RESULT_ROWS


class ReportsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.report_service = ReportService()
        self.report_rows = [dict(row) for row in REPORT_ROWS]
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("Relatorios gerados")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        options_group = QGroupBox("Geracao de relatorios")
        options_layout = QFormLayout(options_group)
        options_layout.setSpacing(10)

        self.report_type = QComboBox()
        self.report_type.addItems(
            [
                "Executivo (sumario)",
                "Tecnico completo",
                "Por host",
                "Apenas criticos",
                "Conformidade PCI-DSS",
                "Conformidade ISO 27001",
            ]
        )

        self.report_format = QComboBox()
        self.report_format.addItems(["PDF", "TXT"])

        include_box = QWidget()
        include_layout = QVBoxLayout(include_box)
        include_layout.setContentsMargins(0, 0, 0, 0)
        include_layout.setSpacing(6)

        self.include_topology = QCheckBox("Topologia de rede")
        self.include_topology.setChecked(True)
        include_layout.addWidget(self.include_topology)

        self.include_references = QCheckBox("Referencias tecnicas")
        self.include_references.setChecked(True)
        include_layout.addWidget(self.include_references)

        self.include_recommendations = QCheckBox("Recomendacoes tecnicas")
        self.include_recommendations.setChecked(True)
        include_layout.addWidget(self.include_recommendations)

        self.include_evidence = QCheckBox("Capturas de evidencia")
        include_layout.addWidget(self.include_evidence)

        options_layout.addRow("Tipo de relatorio:", self.report_type)
        options_layout.addRow("Formato:", self.report_format)
        options_layout.addRow("Incluir:", include_box)

        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Gerar relatorio")
        self.generate_button.clicked.connect(self._generate_report)
        buttons_layout.addWidget(self.generate_button)

        self.preview_button = QPushButton("Pre-visualizar")
        self.preview_button.clicked.connect(self._preview_report)
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addStretch(1)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nome", "Data", "Tipo", "Tamanho", "Acao"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.cellClicked.connect(self._handle_table_click)
        self.table.cellDoubleClicked.connect(self._handle_table_activation)
        self._refresh_report_table()

        layout.addWidget(options_group)
        layout.addLayout(buttons_layout)
        previous_title = QLabel("Relatorios anteriores")
        previous_title.setObjectName("SectionTitle")
        layout.addWidget(previous_title)
        layout.addWidget(self.table, 1)

    def _build_report_document(self):
        if not HISTORY_ROWS:
            latest_history = {
                "target": "Pendente",
                "scan_type": "Pendente",
                "operator": "admin",
            }
        else:
            latest_history = HISTORY_ROWS[0]

        report = self.report_service.build_report(
            report_type=self.report_type.currentText(),
            target=latest_history["target"],
            scan_type=latest_history["scan_type"],
            operator=latest_history["operator"],
            results=RESULT_ROWS if RESULT_ROWS else [],
            findings=FINDING_ROWS if FINDING_ROWS else [],
            include_recommendations=self.include_recommendations.isChecked(),
            include_references=self.include_references.isChecked(),
        )

        if self.include_topology.isChecked():
            report.metadata.notes.append(
                "Topologia de rede sera anexada quando o modulo visual de descoberta estiver integrado."
            )

        if self.include_evidence.isChecked():
            report.metadata.notes.append(
                "Capturas de evidencia dependem de armazenamento local e ainda nao estao conectadas."
            )

        return report

    def _generate_report(self) -> None:
        report = self._build_report_document()
        output_format = self.report_format.currentText().strip().lower()
        suggested_name = self._build_default_filename(output_format)
        file_filter = "Arquivos PDF (*.pdf)" if output_format == "pdf" else "Arquivos TXT (*.txt)"

        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio do SENTRA",
            suggested_name,
            file_filter,
        )
        if not selected_path:
            return

        try:
            generated_path = self.report_service.export_report(
                report,
                selected_path,
                output_format,
            )
        except ReportExportError as exc:
            QMessageBox.warning(self, "Falha na exportacao", str(exc))
            return
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Erro ao salvar relatorio",
                f"Nao foi possivel gravar o arquivo:\n{exc}",
            )
            return

        self._append_generated_report(generated_path)
        QMessageBox.information(
            self,
            "Relatorio gerado",
            f"Arquivo salvo com sucesso em:\n{generated_path}",
        )

    def _preview_report(self) -> None:
        report = self._build_report_document()
        preview_text = self.report_service.preview_text(report)

        dialog = QDialog(self)
        dialog.setWindowTitle("Pre-visualizacao do relatorio")
        dialog.resize(860, 620)

        layout = QVBoxLayout(dialog)
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setPlainText(preview_text)
        layout.addWidget(text_area)

        close_button = QPushButton("Fechar")
        close_button.clicked.connect(dialog.accept)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

        dialog.exec()

    def _append_generated_report(self, path: Path) -> None:
        size_in_bytes = path.stat().st_size
        size_label = self._format_size(size_in_bytes)
        self.report_rows.insert(
            0,
            {
                "name": path.name,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "type": self.report_type.currentText(),
                "size": size_label,
                "action": "Abrir arquivo",
                "path": str(path),
            },
        )
        self._refresh_report_table()

    def _refresh_report_table(self) -> None:
        self.table.setRowCount(len(self.report_rows))
        for row_index, row in enumerate(self.report_rows):
            name_item = QTableWidgetItem(row["name"])
            file_path = row.get("path", "")
            if file_path:
                name_item.setToolTip(file_path)
            self.table.setItem(row_index, 0, name_item)
            self.table.setItem(row_index, 1, QTableWidgetItem(row["date"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(row["type"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(row["size"]))
            action_label = row.get("action", "Historico")
            action_item = QTableWidgetItem(action_label)
            if file_path:
                action_item.setToolTip("Clique para abrir o arquivo exportado.")
            self.table.setItem(row_index, 4, action_item)

    def _handle_table_click(self, row: int, column: int) -> None:
        if column == 4:
            self._open_report_from_row(row)

    def _handle_table_activation(self, row: int, _column: int) -> None:
        self._open_report_from_row(row)

    def _open_report_from_row(self, row: int) -> None:
        if row < 0 or row >= len(self.report_rows):
            return

        report_row = self.report_rows[row]
        file_path = str(report_row.get("path", "")).strip()
        if not file_path:
            QMessageBox.information(
                self,
                "Relatorio historico",
                "Este item faz parte apenas do historico visual atual.\n"
                "Gere um novo relatorio para abrir um arquivo real.",
            )
            return

        path = Path(file_path)
        if not path.exists():
            QMessageBox.warning(
                self,
                "Arquivo nao encontrado",
                f"O arquivo esperado nao foi localizado:\n{path}",
            )
            return

        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        if not opened:
            QMessageBox.warning(
                self,
                "Falha ao abrir relatorio",
                "O sistema nao conseguiu abrir o arquivo exportado automaticamente.",
            )

    def _build_default_filename(self, output_format: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_type = (
            self.report_type.currentText()
            .lower()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
        )
        return f"sentra_{safe_type}_{timestamp}.{output_format}"

    @staticmethod
    def _format_size(size_in_bytes: int) -> str:
        if size_in_bytes >= 1024 * 1024:
            return f"{size_in_bytes / (1024 * 1024):.1f} MB"
        if size_in_bytes >= 1024:
            return f"{size_in_bytes / 1024:.1f} KB"
        return f"{size_in_bytes} B"
