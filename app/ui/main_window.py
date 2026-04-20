from __future__ import annotations

from ui.workers.scan_worker import ScanWorker

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.ui_data import APP_TITLE, BOOT_LOGS, DETAIL_DEFAULT, FINDING_ROWS, HISTORY_ROWS, RESULT_ROWS, TAB_PATHS
from ui.screens.history_screen import HistoryScreen
from ui.screens.logs_screen import LogsScreen
from ui.screens.reports_screen import ReportsScreen
from ui.screens.results_screen import ResultsScreen
from ui.screens.scan_screen import ScanScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.vulnerabilities_screen import VulnerabilitiesScreen


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.log_entries: list[dict[str, str]] = []
        self.tab_index_by_key: dict[str, int] = {}
        self.tree_items_by_key: dict[str, QTreeWidgetItem] = {}
        self.current_detail = dict(DETAIL_DEFAULT)

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1100, 720)
        self._apply_window_geometry()

        self._build_menu()
        self._build_toolbar()
        self._build_central_ui()
        self._build_status_bar()
        self._connect_signals()
        self._load_boot_logs()
        self._set_detail(self.current_detail)
        self._switch_to_tab("nova_analise")

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        new_scan_action = QAction("Nova analise", self)
        new_scan_action.triggered.connect(lambda: self._switch_to_tab("nova_analise"))
        file_menu.addAction(new_scan_action)

        file_menu.addSeparator()
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        analysis_menu = self.menuBar().addMenu("Analise")
        results_action = QAction("Resultados", self)
        results_action.triggered.connect(lambda: self._switch_to_tab("resultados"))
        analysis_menu.addAction(results_action)

        findings_action = QAction("Achados", self)
        findings_action.triggered.connect(lambda: self._switch_to_tab("vulnerabilidades"))
        analysis_menu.addAction(findings_action)

        reports_menu = self.menuBar().addMenu("Relatorios")
        reports_action = QAction("Gerar relatorios", self)
        reports_action.triggered.connect(lambda: self._switch_to_tab("relatorios"))
        reports_menu.addAction(reports_action)

        view_menu = self.menuBar().addMenu("Exibir")
        logs_action = QAction("Logs do sistema", self)
        logs_action.triggered.connect(lambda: self._switch_to_tab("logs"))
        view_menu.addAction(logs_action)

        help_menu = self.menuBar().addMenu("Ajuda")
        about_action = QAction("Sobre o SENTRA", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Atalhos principais")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        actions = [
            ("Nova analise", "nova_analise"),
            ("Resultados", "resultados"),
            ("Achados", "vulnerabilidades"),
            ("Relatorios", "relatorios"),
            ("Atualizar", "refresh"),
            ("Limpar logs", "clear_logs"),
            ("Configuracoes", "configuracoes"),
        ]

        for label, key in actions:
            action = QAction(label, self)
            if key == "refresh":
                action.triggered.connect(self._refresh_current_view)
            elif key == "clear_logs":
                action.triggered.connect(self._clear_logs)
            else:
                action.triggered.connect(
                    lambda checked=False, tab_key=key: self._switch_to_tab(tab_key)
                )
            toolbar.addAction(action)
            if key in {"relatorios", "clear_logs"}:
                toolbar.addSeparator()

    def _build_central_ui(self) -> None:
        root_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = self._build_sidebar()
        root_splitter.addWidget(self.sidebar)

        center_pane = QWidget()
        center_pane.setObjectName("CenterPane")
        center_layout = QVBoxLayout(center_pane)
        center_layout.setContentsMargins(10, 10, 10, 10)
        center_layout.setSpacing(10)

        self.address_bar = QLineEdit()
        self.address_bar.setReadOnly(True)

        address_layout = QHBoxLayout()
        address_label = QLabel("Escopo:")
        address_label.setObjectName("MutedLabel")
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_bar, 1)
        center_layout.addLayout(address_layout)

        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.setChildrenCollapsible(False)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setUsesScrollButtons(True)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        vertical_splitter.addWidget(self.tabs)
        vertical_splitter.addWidget(self._build_bottom_log_panel())
        vertical_splitter.setSizes([680, 180])
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 0)

        self.scan_screen = ScanScreen()
        self.results_screen = ResultsScreen()
        self.vulnerabilities_screen = VulnerabilitiesScreen()
        self.reports_screen = ReportsScreen()
        self.settings_screen = SettingsScreen()
        self.logs_screen = LogsScreen()
        self.history_screen = HistoryScreen()

        self._add_tab("nova_analise", "Nova analise", self.scan_screen)
        self._add_tab("resultados", "Resultados", self.results_screen)
        self._add_tab("vulnerabilidades", "Achados", self.vulnerabilities_screen)
        self._add_tab("relatorios", "Relatorios", self.reports_screen)
        self._add_tab("configuracoes", "Configuracoes", self.settings_screen)
        self._add_tab("logs", "Logs", self.logs_screen)
        self._add_tab("historico", "Historico", self.history_screen)

        center_layout.addWidget(vertical_splitter, 1)
        root_splitter.addWidget(center_pane)

        self.detail_pane = self._build_detail_pane()
        root_splitter.addWidget(self.detail_pane)
        root_splitter.setChildrenCollapsible(False)
        root_splitter.setStretchFactor(0, 0)
        root_splitter.setStretchFactor(1, 1)
        root_splitter.setStretchFactor(2, 0)
        root_splitter.setSizes([220, 920, 250])

        self.setCentralWidget(root_splitter)

    def _build_sidebar(self) -> QWidget:
        pane = QWidget()
        pane.setObjectName("SidebarPane")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Navegacao")
        title.setObjectName("PaneTitle")
        layout.addWidget(title)

        self.tree = QTreeWidget()
        self.tree.setMinimumWidth(200)
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_tree_item_clicked)
        layout.addWidget(self.tree, 1)

        root_item = QTreeWidgetItem(["SENTRA"])
        self.tree.addTopLevelItem(root_item)

        self._add_tree_item(root_item, "Nova analise", "nova_analise")
        self._add_tree_item(root_item, "Historico de scans", "historico")

        devices_item = QTreeWidgetItem(["Dispositivos detectados"])
        root_item.addChild(devices_item)
        self._add_tree_item(devices_item, "Hosts ativos (12)", "resultados")
        self._add_tree_item(devices_item, "Servidores (4)", "resultados")
        self._add_tree_item(devices_item, "Roteadores (2)", "resultados")
        self._add_tree_item(devices_item, "Desconhecidos (1)", "resultados")

        findings_item = QTreeWidgetItem(["Achados de seguranca"])
        root_item.addChild(findings_item)
        self._add_tree_item(findings_item, "Criticos (3)", "vulnerabilidades")
        self._add_tree_item(findings_item, "Altos (2)", "vulnerabilidades")
        self._add_tree_item(findings_item, "Medios (2)", "vulnerabilidades")

        self._add_tree_item(root_item, "Relatorios", "relatorios")
        self._add_tree_item(root_item, "Configuracoes", "configuracoes")
        self._add_tree_item(root_item, "Logs do sistema", "logs")

        root_item.setExpanded(True)
        devices_item.setExpanded(True)
        findings_item.setExpanded(True)
        self.tree.expandAll()

        return pane

    def _build_bottom_log_panel(self) -> QWidget:
        pane = QWidget()
        pane.setObjectName("BottomLogPane")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        title = QLabel("Log de eventos")
        title.setObjectName("PaneTitle")
        header_layout.addWidget(title)

        self.log_count_label = QLabel("0 entradas")
        header_layout.addWidget(self.log_count_label)
        header_layout.addStretch(1)

        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self._clear_logs)
        header_layout.addWidget(clear_button)

        self.bottom_log_output = QTextEdit()
        self.bottom_log_output.setReadOnly(True)

        layout.addLayout(header_layout)
        layout.addWidget(self.bottom_log_output, 1)
        return pane

    def _build_detail_pane(self) -> QWidget:
        pane = QWidget()
        pane.setObjectName("DetailPane")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        title = QLabel("Detalhes do item")
        title.setObjectName("PaneTitle")
        content_layout.addWidget(title)

        detail_group = QGroupBox("Resumo do item")
        detail_layout = QVBoxLayout(detail_group)
        detail_layout.setSpacing(8)

        self.detail_labels = {}
        fields = [
            ("Host", "host"),
            ("IP", "ip"),
            ("Porta", "port"),
            ("Servico", "service"),
            ("Sistema", "os"),
            ("Risco", "risk"),
            ("Referencia", "reference"),
            ("CVSS", "cvss"),
            ("Ultima deteccao", "detected_at"),
        ]

        for label_text, key in fields:
            row = QWidget()
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(2)
            row_layout.addWidget(QLabel(label_text))
            value = QLabel("-")
            value.setWordWrap(True)
            self.detail_labels[key] = value
            row_layout.addWidget(value)
            detail_layout.addWidget(row)

        detail_layout.addWidget(QLabel("Descricao"))
        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        detail_layout.addWidget(self.description_label)

        detail_layout.addWidget(QLabel("Recomendacao"))
        self.recommendation_label = QLabel("-")
        self.recommendation_label.setWordWrap(True)
        detail_layout.addWidget(self.recommendation_label)

        copy_button = QPushButton("Copiar informacoes")
        copy_button.clicked.connect(self._copy_current_detail)
        detail_layout.addWidget(copy_button)

        reference_button = QPushButton("Ver referencia tecnica")
        reference_button.clicked.connect(self._show_reference_message)
        detail_layout.addWidget(reference_button)

        content_layout.addWidget(detail_group)
        content_layout.addStretch(1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        return pane

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        indicator = self._create_status_chip()
        status_bar.addWidget(indicator, 1)

        self.hosts_chip = self._create_info_chip("Hosts", "12")
        self.findings_chip = self._create_info_chip("Achados", "9")
        self.risk_chip = self._create_info_chip("Risco geral", "CRITICO")
        self.operator_chip = self._create_info_chip("Operador", "admin")
        self.version_chip = self._create_info_chip("UI", "PySide6")

        status_bar.addPermanentWidget(self.hosts_chip)
        status_bar.addPermanentWidget(self.findings_chip)
        status_bar.addPermanentWidget(self.risk_chip)
        status_bar.addPermanentWidget(self.operator_chip)
        status_bar.addPermanentWidget(self.version_chip)

    def _create_status_chip(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("StatusChip")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(8)

        self.status_dot = QLabel()
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setProperty("dotState", "idle")
        self.status_text = QLabel("Status: Pronto")

        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)
        layout.addStretch(1)
        return frame

    def _create_info_chip(self, label: str, value: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("StatusChip")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        title = QLabel(f"{label}:")
        current_value = QLabel(value)
        current_value.setObjectName(f"{label}Value")
        layout.addWidget(title)
        layout.addWidget(current_value)

        return frame

    def _connect_signals(self) -> None:
        self.scan_screen.log_generated.connect(self._append_log)
        self.scan_screen.status_changed.connect(self._update_status_summary)
        self.scan_screen.results_ready.connect(self._handle_scan_results)
        self.results_screen.result_selected.connect(self._set_detail)
        self.vulnerabilities_screen.finding_selected.connect(self._set_detail)
        self.logs_screen.clear_requested.connect(self._clear_logs)

    def _load_boot_logs(self) -> None:
        for level, module, message, host in BOOT_LOGS:
            self._append_log(level, module, message, host)

    def _append_log(self, level: str, module: str, message: str, host: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = {
            "timestamp": timestamp,
            "level": level,
            "module": module,
            "message": message,
            "host": host,
        }
        self.log_entries.append(entry)
        self.logs_screen.set_entries(self.log_entries)
        self.log_count_label.setText(f"{len(self.log_entries)} entradas")

        colors = {
            "INFO": "#2f6fb0",
            "WARN": "#9a6700",
            "ERR": "#b42318",
            "OK": "#157347",
        }
        color = colors.get(level, "#334155")
        self.bottom_log_output.append(
            f"<span style='color:#64748b'>{timestamp}</span> "
            f"<span style='color:{color}'><b>{level}</b></span> "
            f"<span>[{module}] {message} - {host}</span>"
        )
        cursor = self.bottom_log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.bottom_log_output.setTextCursor(cursor)

    def _clear_logs(self) -> None:
        self.log_entries.clear()
        self.logs_screen.set_entries(self.log_entries)
        self.bottom_log_output.clear()
        self.log_count_label.setText("0 entradas")

    def _update_status_summary(self, payload: dict) -> None:
        self.status_dot.setProperty("dotState", payload["state"])
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)

        self.status_text.setText(f"Status: {payload['status_text']}")
        self._set_chip_value(self.hosts_chip, str(payload["hosts"]))
        self._set_chip_value(self.findings_chip, str(payload["findings"]))
        self._set_chip_value(self.risk_chip, payload["risk"])

    def _set_detail(self, detail: dict) -> None:
        self.current_detail = dict(detail)
        for key, label in self.detail_labels.items():
            label.setText(self.current_detail.get(key, "-"))

        self.description_label.setText(self.current_detail.get("description", "-"))
        self.recommendation_label.setText(self.current_detail.get("recommendation", "-"))

    def _copy_current_detail(self) -> None:
        lines = [
            f"Host: {self.current_detail.get('host', '-')}",
            f"IP: {self.current_detail.get('ip', '-')}",
            f"Porta: {self.current_detail.get('port', '-')}",
            f"Servico: {self.current_detail.get('service', '-')}",
            f"Risco: {self.current_detail.get('risk', '-')}",
            f"Referencia: {self.current_detail.get('reference', '-')}",
            f"Recomendacao: {self.current_detail.get('recommendation', '-')}",
        ]
        QApplication.clipboard().setText("\n".join(lines))
        self.statusBar().showMessage("Detalhes copiados para a area de transferencia.", 3000)

    def _show_reference_message(self) -> None:
        QMessageBox.information(
            self,
            "Referencia tecnica",
            "A abertura de referencias externas sera conectada quando o backend de integracao estiver pronto.",
        )

    def _show_about_dialog(self) -> None:
        QMessageBox.information(
            self,
            "Sobre o SENTRA",
            "SENTRA em PySide6\n\n"
            "Esta versao recria a visao do produto em interface desktop nativa, "
            "pronta para receber a integracao com scanner, parser, risco e banco.",
        )

    def _add_tab(self, key: str, title: str, widget: QWidget) -> None:
        index = self.tabs.addTab(widget, title)
        self.tab_index_by_key[key] = index

    def _add_tree_item(
        self, parent: QTreeWidgetItem, label: str, tab_key: str | None = None
    ) -> QTreeWidgetItem:
        item = QTreeWidgetItem([label])
        if tab_key:
            item.setData(0, Qt.ItemDataRole.UserRole, tab_key)
            self.tree_items_by_key.setdefault(tab_key, item)
        parent.addChild(item)
        return item

    def _on_tree_item_clicked(self, item: QTreeWidgetItem) -> None:
        tab_key = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(tab_key, str):
            self._switch_to_tab(tab_key)
        else:
            item.setExpanded(not item.isExpanded())

    def _switch_to_tab(self, tab_key: str) -> None:
        index = self.tab_index_by_key.get(tab_key)
        if index is None:
            return
        self.tabs.setCurrentIndex(index)
        tree_item = self.tree_items_by_key.get(tab_key)
        if tree_item is not None:
            self.tree.setCurrentItem(tree_item)
        self.address_bar.setText(TAB_PATHS.get(tab_key, "SENTRA"))

    def _on_tab_changed(self, index: int) -> None:
        for key, tab_index in self.tab_index_by_key.items():
            if tab_index == index:
                self.address_bar.setText(TAB_PATHS.get(key, "SENTRA"))
                tree_item = self.tree_items_by_key.get(key)
                if tree_item is not None:
                    self.tree.setCurrentItem(tree_item)
                break

    def _refresh_current_view(self) -> None:
        self.statusBar().showMessage("Interface atualizada.", 2500)

    def _handle_scan_results(self, results: list[dict[str, str]]) -> None:
        target = self.scan_screen.cidr_input.text().strip() or self.scan_screen.ip_input.text().strip()

        # Atualizar listas globais para relatórios
        RESULT_ROWS[:] = results

        findings = self._build_finding_rows(results)
        FINDING_ROWS[:] = findings

        # Adicionar ao histórico
        scan_type = self.scan_screen.scan_type_group.checkedId()
        scan_type_name = {
            0: "Rápido",
            1: "Completo",
            2: "Detecção de Serviços",
            3: "Auditoria Avançada",
        }.get(scan_type, "Desconhecido")
        
        history_entry = {
            "target": target,
            "scan_type": scan_type_name,
            "operator": "admin",  # TODO: implementar usuário logado
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "hosts_found": len({item.get("host") for item in results if item.get("host")}),
            "findings_count": len(findings),
            "status": "Concluído",
        }
        HISTORY_ROWS.insert(0, history_entry)

        self.results_screen.set_scan_target(target)
        self.results_screen.set_rows(results)

        self.vulnerabilities_screen.set_scan_target(target)
        self.vulnerabilities_screen.set_rows(findings)

        if results:
            self._set_detail(self._build_detail_from_result(results[0]))
            self.statusBar().showMessage(
                f"Scan concluido: {len(results)} registros carregados para analise.",
                5000,
            )
        else:
            self.statusBar().showMessage(
                "Scan concluido sem resultados visiveis para o escopo informado.",
                5000,
            )

        self._switch_to_tab("resultados")

    @staticmethod
    def _build_detail_from_result(row: dict[str, str]) -> dict[str, str]:
        return {
            "host": row.get("host", "-"),
            "ip": row.get("ip", "-"),
            "port": f"{row.get('port', '-')}/{row.get('protocol', '-')}",
            "service": row.get("service", "-"),
            "os": row.get("os", "-"),
            "risk": row.get("risk", "-"),
            "reference": row.get("reference", "-"),
            "cvss": row.get("cvss", "-"),
            "detected_at": row.get("detected_at", "-"),
            "description": row.get("description", "-"),
            "recommendation": row.get("recommendation", "-"),
        }

    @staticmethod
    def _build_finding_rows(results: list[dict[str, str]]) -> list[dict[str, str]]:
        finding_rows: list[dict[str, str]] = []
        for row in results:
            risk = str(row.get("risk", "BAIXO")).upper()
            if risk == "BAIXO":
                continue

            finding_rows.append(
                {
                    "severity": risk,
                    "reference": row.get("reference", "Risco identificado"),
                    "description": row.get(
                        "description",
                        "Exposicao relevante identificada durante a analise.",
                    ),
                    "host": row.get("host", row.get("ip", "-")),
                    "service_port": (
                        f"{row.get('port', '-')}/{row.get('protocol', '-')} "
                        f"({row.get('service', '-')})"
                    ),
                    "cvss": row.get("cvss", "-"),
                    "recommendation": row.get(
                        "recommendation",
                        "Revisar exposicao do servico e aplicar mitigacoes.",
                    ),
                    "ip": row.get("ip", "-"),
                    "service": row.get("service", "-"),
                    "os": row.get("os", "-"),
                    "risk": risk,
                    "detected_at": row.get("detected_at", "-"),
                }
            )
        return finding_rows

    def _apply_window_geometry(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(1380, 860)
            return

        available = screen.availableGeometry()
        width = min(1500, int(available.width() * 0.94))
        height = min(940, int(available.height() * 0.92))
        width = max(1100, min(width, available.width()))
        height = max(720, min(height, available.height()))
        self.resize(width, height)

    @staticmethod
    def _set_chip_value(chip: QFrame, value: str) -> None:
        labels = chip.findChildren(QLabel)
        if labels:
            labels[-1].setText(value)
