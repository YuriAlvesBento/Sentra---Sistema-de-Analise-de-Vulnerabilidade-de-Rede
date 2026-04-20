from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from modules.reports.report_service import ReportService
from modules.scanner.scan_service import ScanService


class ScanWorker(QThread):
    finished = Signal(list)
    log = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        network: str,
        scan_type: int = 0,
        os_detection: bool = False,
        version_detection: bool = True,
        nse_enabled: bool = False,
        full_port_scan: bool = False,
        firewall_detection: bool = False,
        custom_ports: str = "",
        auto_report: bool = False,
        timeout_ms: int = 3000,
        parallelism: int = 64,
        intensity: str = "Normal (T3)",
        parent=None,
    ):
        super().__init__(parent)
        self.network = network
        self.scan_type = scan_type
        self.os_detection = os_detection
        self.version_detection = version_detection
        self.nse_enabled = nse_enabled
        self.full_port_scan = full_port_scan
        self.firewall_detection = firewall_detection
        self.custom_ports = custom_ports
        self.auto_report = auto_report
        self.timeout_ms = timeout_ms
        self.parallelism = parallelism
        self.intensity = intensity
        self.service: ScanService | None = None

        try:
            self.service = ScanService()
        except Exception as error:
            message = f"[SENTRA] Falha ao inicializar servico de scan: {error}"
            self.log.emit(message)
            self.error.emit(message)

    def run(self) -> None:
        try:
            if not self.network or not self.network.strip():
                self.log.emit("[SENTRA] Nenhum alvo informado para scan.")
                self.finished.emit([])
                return

            if self.service is None:
                self.error.emit("[SENTRA] Servico de scan nao esta disponivel.")
                self.finished.emit([])
                return

            self.log.emit(f"[SENTRA] Iniciando scan tipo {self.scan_type} em {self.network}...")

            result = self.service.execute_network_scan(
                self.network,
                scan_type=self.scan_type,
                os_detection=self.os_detection,
                version_detection=self.version_detection,
                nse_enabled=self.nse_enabled,
                full_port_scan=self.full_port_scan,
                firewall_detection=self.firewall_detection,
                custom_ports=self.custom_ports,
                host_timeout_ms=self.timeout_ms,
                parallelism=self.parallelism,
                timing_template=self.intensity,
            )
            self.log.emit(f"[SENTRA] Scan concluido: {len(result)} registros obtidos.")
            if self.auto_report and result:
                self._generate_auto_report(result)
            self.finished.emit(result)
        except TimeoutError as error:
            message = f"[SENTRA] TIMEOUT! Scan levou muito tempo: {error}"
            self.log.emit(message)
            print(f"[WORKER ERROR] {message}")
            print(f"[WORKER TRACEBACK]\n{traceback.format_exc()}")
            self.finished.emit([])
        except Exception as error:
            message = f"[SENTRA] Falha critica no scan: {error}"
            self.log.emit(message)
            print(f"[WORKER ERROR] {message}")
            print(f"[WORKER TRACEBACK]\n{traceback.format_exc()}")
            self.error.emit(message)
            self.finished.emit([])

    def _generate_auto_report(self, results: list[dict[str, str]]) -> None:
        try:
            report_service = ReportService()
            findings: list[dict[str, str]] = []
            report_type = "Tecnico completo"
            target = self.network
            scan_type = {
                0: "Rapido",
                1: "Completo",
                2: "Deteccao de servicos",
                3: "Auditoria avancada",
            }.get(self.scan_type, "Customizado")

            report = report_service.build_report(
                report_type=report_type,
                target=target,
                scan_type=scan_type,
                operator="admin",
                results=results,
                findings=findings,
                include_recommendations=True,
                include_references=True,
            )

            out_dir = Path.cwd() / "sentra_reports"
            out_dir.mkdir(exist_ok=True)
            filename = out_dir / f"sentra_auto_report_{target.replace(' ', '_').replace('/', '_')}.txt"
            generated_path = report_service.export_report(report, str(filename), "txt")
            self.log.emit(f"[SENTRA] Relatorio automatico gerado em: {generated_path}")
        except Exception as error:
            self.log.emit(f"[SENTRA] Falha ao gerar relatorio automatico: {error}")
