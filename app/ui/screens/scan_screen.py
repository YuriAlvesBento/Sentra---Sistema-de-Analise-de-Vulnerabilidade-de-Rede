from __future__ import annotations

import html

from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.ui_data import SCAN_STEPS
from ui.workers.scan_worker import ScanWorker


class ToggleOptionRow(QWidget):
    def __init__(self, button: QAbstractButton, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.button = button
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.button.setText("")
        self.button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        label = QLabel(text)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.label = label

        layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.label, 1)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.button.isEnabled():
            if isinstance(self.button, QRadioButton):
                self.button.setChecked(True)
            else:
                self.button.toggle()
            event.accept()
            return
        super().mousePressEvent(event)


class ScanScreen(QWidget):
    log_generated = Signal(str, str, str, str)
    status_changed = Signal(dict)
    results_ready = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_elapsed_time)

        self._elapsed_seconds = 0
        self._scan_running = False
        self._hosts_count = 0
        self._ports_count = 0
        self._findings_count = 0
        self.worker = None

        self._build_ui()
        self._reset_view()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        root_layout.addWidget(content_splitter, 1)

        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QFrame.Shape.NoFrame)

        form_container = QWidget()
        left_column = QVBoxLayout(form_container)
        left_column.setContentsMargins(0, 0, 8, 0)
        left_column.setSpacing(10)

        left_column.addWidget(self._build_target_group())
        left_column.addWidget(self._build_scan_type_group())
        left_column.addWidget(self._build_options_group())
        left_column.addWidget(self._build_advanced_group())
        left_column.addLayout(self._build_controls_row())
        left_column.addWidget(self._build_progress_group())
        left_column.addStretch(1)

        form_scroll.setWidget(form_container)
        content_splitter.addWidget(form_scroll)

        console_group = QGroupBox("Console de saida")
        console_group.setMinimumWidth(320)
        console_layout = QVBoxLayout(console_group)
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        content_splitter.addWidget(console_group)

        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 2)

    def _build_target_group(self) -> QGroupBox:
        group = QGroupBox("Alvo da analise")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        self.target_mode_combo = QComboBox()
        self.target_mode_combo.addItems(["IP unico", "Faixa CIDR", "Host/Dominio"])
        self.ip_input = QLineEdit("192.168.1.1")
        self.cidr_input = QLineEdit("192.168.1.0/24")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("ex: servidor.empresa.local")

        layout.addRow("Tipo de alvo:", self.target_mode_combo)
        layout.addRow("IP alvo:", self.ip_input)
        layout.addRow("Faixa (CIDR):", self.cidr_input)
        layout.addRow("Host/Dominio:", self.host_input)
        return group

    def _build_scan_type_group(self) -> QGroupBox:
        group = QGroupBox("Tipo de scan")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.scan_type_group = QButtonGroup(self)
        options = [
            "Rapido - descoberta basica de hosts e portas principais.",
            "Completo - varredura ampliada de portas e servicos do alvo.",
            "Deteccao de servicos - versoes, banners e contexto operacional.",
            "Auditoria avancada - coleta ampliada de evidencias defensivas.",
        ]
        for index, text in enumerate(options):
            radio = QRadioButton()
            if index == 0:
                radio.setChecked(True)
            self.scan_type_group.addButton(radio, index)
            layout.addWidget(ToggleOptionRow(radio, text))
        return group

    def _build_options_group(self) -> QGroupBox:
        group = QGroupBox("Opcoes da analise")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.os_checkbox = QCheckBox()
        self.os_checkbox.setChecked(True)
        self.version_checkbox = QCheckBox()
        self.version_checkbox.setChecked(True)
        self.full_ports_checkbox = QCheckBox()
        self.nse_checkbox = QCheckBox()
        self.firewall_checkbox = QCheckBox()
        self.report_checkbox = QCheckBox()

        options = [
            (self.os_checkbox, "Detectar sistema operacional do host."),
            (
                self.version_checkbox,
                "Detectar versoes de servicos e softwares publicados.",
            ),
            (
                self.full_ports_checkbox,
                "Executar varredura ampliada de portas no escopo selecionado.",
            ),
            (
                self.nse_checkbox,
                "Executar scripts NSE padrao voltados a verificacao defensiva.",
            ),
            (
                self.firewall_checkbox,
                "Detectar firewall, filtros de pacotes e servicos protegidos.",
            ),
            (
                self.report_checkbox,
                "Gerar relatorio automaticamente ao concluir a analise.",
            ),
        ]

        for checkbox, text in options:
            layout.addWidget(ToggleOptionRow(checkbox, text))

        return group

    def _build_advanced_group(self) -> QGroupBox:
        group = QGroupBox("Parametros avancados")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1000, 120000)
        self.timeout_input.setValue(10000)
        self.timeout_input.setSuffix(" ms")

        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 512)
        self.threads_input.setValue(64)

        self.ports_input = QLineEdit()
        self.ports_input.setPlaceholderText("21,22,80,443,8080-8090")

        self.intensity_combo = QComboBox()
        self.intensity_combo.addItems(
            ["Normal (T3)", "Elevada (T4)", "Maxima (T5)", "Silenciosa (T1)"]
        )

        layout.addWidget(QLabel("Timeout:"), 0, 0)
        layout.addWidget(self.timeout_input, 0, 1)
        layout.addWidget(QLabel("Threads:"), 0, 2)
        layout.addWidget(self.threads_input, 0, 3)
        layout.addWidget(QLabel("Portas customizadas:"), 1, 0)
        layout.addWidget(self.ports_input, 1, 1, 1, 3)
        layout.addWidget(QLabel("Intensidade:"), 2, 0)
        layout.addWidget(self.intensity_combo, 2, 1, 1, 2)
        return group

    def _build_controls_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.start_button = QPushButton("Iniciar analise")
        self.stop_button = QPushButton("Parar")
        self.clear_console_button = QPushButton("Limpar console")
        self.save_profile_button = QPushButton("Salvar perfil")

        self.start_button.clicked.connect(self.start_scan)
        self.stop_button.clicked.connect(self.stop_scan)
        self.clear_console_button.clicked.connect(self.clear_console)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.clear_console_button)
        layout.addStretch(1)
        layout.addWidget(self.save_profile_button)
        return layout

    def _build_progress_group(self) -> QGroupBox:
        group = QGroupBox("Progresso")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.scan_status_label = QLabel("Aguardando...")
        status_layout.addWidget(self.scan_status_label)
        status_layout.addStretch(1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        counters_layout = QHBoxLayout()
        self.hosts_scanned_label = QLabel("Hosts varridos: 0")
        self.ports_open_label = QLabel("Portas abertas: 0")
        self.elapsed_time_label = QLabel("Tempo decorrido: 00:00")
        counters_layout.addWidget(self.hosts_scanned_label)
        counters_layout.addWidget(self.ports_open_label)
        counters_layout.addWidget(self.elapsed_time_label)
        counters_layout.addStretch(1)

        layout.addLayout(status_layout)
        layout.addWidget(self.progress_bar)
        layout.addLayout(counters_layout)
        return group

    def _reset_view(self) -> None:
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.scan_status_label.setText("Aguardando...")
        self.hosts_scanned_label.setText("Hosts varridos: 0")
        self.ports_open_label.setText("Portas abertas: 0")
        self.elapsed_time_label.setText("Tempo decorrido: 00:00")
        self.console_output.setHtml(
            "<span style='color:#2f6fb0'>[SENTRA] Interface pronta para iniciar uma nova analise.</span>"
        )

    def _legacy_start_scan(self) -> None:
        if self._scan_running:
            return

        self._scan_running = True
        self._elapsed_seconds = 0
        self._hosts_count = 0
        self._ports_count = 0
        self._findings_count = 0

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.scan_status_label.setText("Executando analise...")
        self.hosts_scanned_label.setText("Hosts varridos: 0")
        self.ports_open_label.setText("Portas abertas: 0")
        self.elapsed_time_label.setText("Tempo decorrido: 00:00")
        self.console_output.clear()

        self._append_console_line(
            "[SENTRA] Nova analise iniciada pela interface do sistema.", "info"
        )
        self.log_generated.emit(
            "INFO",
            "Scanner",
            "Analise iniciada pela interface local.",
            "localhost",
        )
        self.status_changed.emit(
            {
                "state": "running",
                "status_text": "Analisando...",
                "hosts": 0,
                "findings": 0,
                "risk": "--",
            }
        )

        # Captura alvo
        if self.target_mode_combo.currentIndex() == 0:
            network = self.ip_input.text().strip()
        elif self.target_mode_combo.currentIndex() == 1:
            network = self.cidr_input.text().strip()
        else:
            network = self.host_input.text().strip()

        # Captura tipo de scan selecionado
        scan_type = self.scan_type_group.checkedId()
        
        # Captura opções adicionais
        os_detection = self.os_checkbox.isChecked()
        firewall_detection = self.firewall_checkbox.isChecked()
        custom_ports = self.ports_input.text().strip()
        
        version_detection = self.version_checkbox.isChecked()
        full_port_scan = self.full_ports_checkbox.isChecked()
        nse_scripts = self.nse_checkbox.isChecked()
        auto_report = self.report_checkbox.isChecked()
        custom_timeout_ms = self.timeout_input.value()
        parallelism = self.threads_input.value()
        intensity = self.intensity_combo.currentText()

        self._append_console_line(
            (
                f"[SENTRA] Tipo de scan: {scan_type} | OS: {os_detection} | Firewall: {firewall_detection} "
                f"| Versao: {version_detection} | Portas amplas: {full_port_scan} | NSE: {nse_scripts} "
                f"| Timeout(ms): {custom_timeout_ms} | Threads: {parallelism} | Intensidade: {intensity}"
            ),
            "info"
        )

        # Cria worker com todas as opções
        self.worker = ScanWorker(
            network,
            scan_type=scan_type,
            os_detection=os_detection,
            firewall_detection=firewall_detection,
            custom_ports=custom_ports,
            version_detection=version_detection,
            full_port_scan=full_port_scan,
            nse_enabled=nse_scripts,
            auto_report=auto_report,
            timeout_ms=custom_timeout_ms,
            parallelism=parallelism,
            intensity=intensity,
        )
        self.worker.log.connect(lambda message: self._append_console_line(message, "info"))
        self.worker.error.connect(lambda msg: self._append_console_line(msg, "err"))
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()
        self._clock_timer.start()

    def start_scan(self) -> None:
        if self._scan_running:
            return

        target = self._resolve_target()
        if not target:
            self._append_console_line(
                "[SENTRA] Defina um alvo valido antes de iniciar a analise.",
                "warn",
            )
            self.log_generated.emit(
                "WARN",
                "Scanner",
                "Tentativa de inicio sem alvo valido configurado.",
                "localhost",
            )
            return

        self._scan_running = True
        self._elapsed_seconds = 0
        self._hosts_count = 0
        self._ports_count = 0
        self._findings_count = 0

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.scan_status_label.setText("Executando analise...")
        self.hosts_scanned_label.setText("Hosts varridos: 0")
        self.ports_open_label.setText("Portas abertas: 0")
        self.elapsed_time_label.setText("Tempo decorrido: 00:00")
        self.console_output.clear()

        self._append_console_line(
            "[SENTRA] Nova analise iniciada pela interface do sistema.", "info"
        )
        self.log_generated.emit(
            "INFO",
            "Scanner",
            "Analise iniciada pela interface local.",
            "localhost",
        )
        self.status_changed.emit(
            {
                "state": "running",
                "status_text": "Analisando...",
                "hosts": 0,
                "findings": 0,
                "risk": "--",
            }
        )

        scan_type = self.scan_type_group.checkedId()
        os_detection = self.os_checkbox.isChecked()
        version_detection = self.version_checkbox.isChecked()
        full_port_scan = self.full_ports_checkbox.isChecked()
        nse_enabled = self.nse_checkbox.isChecked()
        firewall_detection = self.firewall_checkbox.isChecked()
        custom_ports = self.ports_input.text().strip()
        timing_template = self.intensity_combo.currentText()
        host_timeout_ms = self.timeout_input.value()
        parallelism = self.threads_input.value()
        auto_report = self.report_checkbox.isChecked()

        self._append_console_line(
            (
                f"[SENTRA] Alvo: {target} | Tipo de scan: {scan_type} | "
                f"OS: {os_detection} | Versao: {version_detection} | "
                f"NSE: {nse_enabled} | Full ports: {full_port_scan} | "
                f"Firewall: {firewall_detection} | Portas: {custom_ports or 'padrao'} | "
                f"Timeout: {host_timeout_ms}ms | Threads: {parallelism} | Timing: {timing_template}"
            ),
            "info",
        )

        self.worker = ScanWorker(
            target,
            scan_type=scan_type,
            os_detection=os_detection,
            version_detection=version_detection,
            nse_enabled=nse_enabled,
            full_port_scan=full_port_scan,
            firewall_detection=firewall_detection,
            custom_ports=custom_ports,
            auto_report=auto_report,
            timeout_ms=host_timeout_ms,
            parallelism=parallelism,
            intensity=timing_template,
        )
        self.worker.log.connect(lambda message: self._append_console_line(message, "info"))
        self.worker.error.connect(lambda msg: self._append_console_line(msg, "err"))
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()
        self._clock_timer.start()

    def stop_scan(self) -> None:
        if not self._scan_running:
            return

        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

        self._clock_timer.stop()
        self._scan_running = False

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.scan_status_label.setText("Interrompido")

        self._append_console_line(
            "[SENTRA] Analise interrompida pelo operador.", "warn"
        )
        self.log_generated.emit(
            "WARN",
            "Scanner",
            "Analise interrompida pelo operador.",
            "localhost",
        )
        self.status_changed.emit(
            {
                "state": "stopped",
                "status_text": "Interrompido",
                "hosts": self._hosts_count,
                "findings": self._findings_count,
                "risk": "--",
            }
        )

    def _on_worker_finished(self, results: list[dict[str, str]]) -> None:
        self._hosts_count = len({item.get("host") for item in results if item.get("host")})
        self._ports_count = len(results)
        self._findings_count = len(results)

        self._append_console_line(
            "[SENTRA] Analise concluida. Resultados consolidados para revisao.", "ok"
        )
        self.log_generated.emit(
            "OK",
            "Scanner",
            "Analise concluida com sucesso e pronta para validacao do backend.",
            "localhost",
        )
        self.status_changed.emit(
            {
                "state": "ready",
                "status_text": "Pronto",
                "hosts": self._hosts_count,
                "findings": self._findings_count,
                "risk": "CRITICO",
            }
        )
        self.results_ready.emit(results)
        self._finish_scan()

    def clear_console(self) -> None:
        self.console_output.setHtml(
            "<span style='color:#2f6fb0'>[SENTRA] Console limpo.</span>"
        )
        if not self._scan_running:
            self.progress_bar.setValue(0)
            self.scan_status_label.setText("Aguardando...")

    def _finish_scan(self) -> None:
        self._clock_timer.stop()
        self._scan_running = False

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.scan_status_label.setText("Concluido")

        self._append_console_line(
            "[SENTRA] Analise concluida. Resultados consolidados para revisao.", "ok"
        )
        self.log_generated.emit(
            "OK",
            "Scanner",
            "Analise concluida com sucesso e pronta para validacao do backend.",
            "localhost",
        )
        self.status_changed.emit(
            {
                "state": "ready",
                "status_text": "Pronto",
                "hosts": self._hosts_count,
                "findings": self._findings_count,
                "risk": "CRITICO",
            }
        )

    def _update_elapsed_time(self) -> None:
        self._elapsed_seconds += 1
        minutes, seconds = divmod(self._elapsed_seconds, 60)
        self.elapsed_time_label.setText(
            f"Tempo decorrido: {minutes:02d}:{seconds:02d}"
        )

    def _append_console_line(self, text: str, tone: str) -> None:
        colors = {
            "info": "#2f6fb0",
            "warn": "#9a6700",
            "err": "#b42318",
            "ok": "#157347",
        }
        escaped = html.escape(text)
        color = colors.get(tone, "#1f2937")
        self.console_output.append(f"<span style='color:{color}'>{escaped}</span>")
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console_output.setTextCursor(cursor)

    def _resolve_target(self) -> str:
        selected_mode = self.target_mode_combo.currentText()
        if selected_mode == "IP unico":
            return self.ip_input.text().strip()
        if selected_mode == "Faixa CIDR":
            return self.cidr_input.text().strip()
        return self.host_input.text().strip()
