from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterable


class ReportExportError(Exception):
    """Raised when the report cannot be exported."""


class ReportFormat(str, Enum):
    PDF = "pdf"
    TXT = "txt"

    @classmethod
    def from_value(cls, value: str) -> "ReportFormat":
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ReportExportError(f"Formato de exportacao nao suportado: {value}")


@dataclass(slots=True)
class ReportMetadata:
    title: str
    report_type: str
    target: str
    scan_type: str
    operator: str
    generated_at: datetime
    risk_level: str
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReportSummary:
    total_hosts: int
    total_services: int
    total_open_ports: int
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int


@dataclass(slots=True)
class ReportResultItem:
    host: str
    ip: str
    port: str
    protocol: str
    service: str
    version: str
    os_name: str
    status: str
    risk: str
    reference: str
    description: str = ""
    recommendation: str = ""


@dataclass(slots=True)
class ReportFindingItem:
    severity: str
    reference: str
    description: str
    host: str
    service_port: str
    cvss: str
    recommendation: str


@dataclass(slots=True)
class ReportDocument:
    metadata: ReportMetadata
    summary: ReportSummary
    results: list[ReportResultItem]
    findings: list[ReportFindingItem]


def render_text_report(report: ReportDocument) -> str:
    metadata = report.metadata
    summary = report.summary

    lines = [
        "SENTRA - RELATORIO DE ANALISE DE REDE",
        "=" * 72,
        f"Titulo: {metadata.title}",
        f"Tipo de relatorio: {metadata.report_type}",
        f"Alvo: {metadata.target}",
        f"Tipo de scan: {metadata.scan_type}",
        f"Operador: {metadata.operator}",
        f"Gerado em: {metadata.generated_at.strftime('%d/%m/%Y %H:%M:%S')}",
        f"Risco geral: {metadata.risk_level}",
    ]

    if metadata.notes:
        lines.append("Observacoes:")
        lines.extend(f"- {note}" for note in metadata.notes)

    lines.extend(
        [
            "",
            "RESUMO EXECUTIVO",
            "-" * 72,
            f"Hosts detectados: {summary.total_hosts}",
            f"Servicos mapeados: {summary.total_services}",
            f"Portas abertas: {summary.total_open_ports}",
            f"Achados relevantes: {summary.total_findings}",
            (
                "Distribuicao de risco: "
                f"criticos={summary.critical_findings}, "
                f"altos={summary.high_findings}, "
                f"medios={summary.medium_findings}, "
                f"baixos={summary.low_findings}"
            ),
            "",
            "ACHADOS PRIORITARIOS",
            "-" * 72,
        ]
    )

    if report.findings:
        for index, finding in enumerate(report.findings, start=1):
            lines.extend(
                [
                    (
                        f"{index}. [{finding.severity}] {finding.host} - "
                        f"{finding.service_port} - {finding.reference}"
                    ),
                    f"   Descricao: {finding.description}",
                    f"   CVSS: {finding.cvss}",
                    f"   Recomendacao: {finding.recommendation}",
                ]
            )
    else:
        lines.append("Nenhum achado relevante para o escopo selecionado.")

    lines.extend(["", "RESULTADOS TECNICOS", "-" * 72])

    if report.results:
        for result in report.results:
            lines.extend(
                [
                    (
                        f"- {result.host} ({result.ip}) | {result.port}/{result.protocol} | "
                        f"{result.service} | status={result.status} | risco={result.risk}"
                    ),
                    f"  Versao: {result.version}",
                    f"  Sistema: {result.os_name}",
                    f"  Referencia: {result.reference}",
                ]
            )
            if result.recommendation:
                lines.append(f"  Recomendacao: {result.recommendation}")
    else:
        lines.append("Nenhum resultado tecnico disponivel para este relatorio.")

    lines.append("")
    return "\n".join(lines)


class TextReportExporter:
    def export(self, report: ReportDocument, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_text_report(report), encoding="utf-8")
        return destination


class PdfReportExporter:
    def export(self, report: ReportDocument, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            from fpdf import FPDF
        except ImportError as exc:
            raise ReportExportError(
                "Exportacao em PDF indisponivel. Instale a dependencia 'fpdf2'."
            ) from exc

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()

        self._write_title(pdf, report.metadata)
        self._write_summary(pdf, report.summary)
        self._write_findings(pdf, report.findings)
        self._write_results(pdf, report.results)

        pdf.output(str(destination))
        return destination

    def _write_title(self, pdf, metadata: ReportMetadata) -> None:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, self._safe_text(metadata.title), ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, self._safe_text(f"Tipo: {metadata.report_type}"), ln=True)
        pdf.cell(0, 7, self._safe_text(f"Alvo: {metadata.target}"), ln=True)
        pdf.cell(0, 7, self._safe_text(f"Scan: {metadata.scan_type}"), ln=True)
        pdf.cell(0, 7, self._safe_text(f"Operador: {metadata.operator}"), ln=True)
        pdf.cell(
            0,
            7,
            self._safe_text(
                f"Gerado em: {metadata.generated_at.strftime('%d/%m/%Y %H:%M:%S')}"
            ),
            ln=True,
        )
        pdf.cell(0, 7, self._safe_text(f"Risco geral: {metadata.risk_level}"), ln=True)
        if metadata.notes:
            pdf.ln(1)
            for note in metadata.notes:
                try:
                    truncated_note = str(note)[:250] if note else ""
                    if truncated_note:
                        pdf.multi_cell(0, 5, self._safe_text(f"Obs: {truncated_note}"))
                except Exception as e:
                    print(f"[PDF DEBUG] Erro ao escrever nota: {e}")
        pdf.ln(4)

    def _write_summary(self, pdf, summary: ReportSummary) -> None:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Resumo executivo", ln=True)
        pdf.set_font("Helvetica", "", 10)
        summary_lines = [
            f"Hosts detectados: {summary.total_hosts}",
            f"Servicos mapeados: {summary.total_services}",
            f"Portas abertas: {summary.total_open_ports}",
            f"Achados relevantes: {summary.total_findings}",
            (
                "Distribuicao de risco: "
                f"criticos={summary.critical_findings}, "
                f"altos={summary.high_findings}, "
                f"medios={summary.medium_findings}, "
                f"baixos={summary.low_findings}"
            ),
        ]
        for line in summary_lines:
            try:
                safe_line = self._safe_text(line)
                if safe_line:
                    pdf.multi_cell(0, 5, safe_line)
            except Exception as e:
                print(f"[PDF DEBUG] Erro ao escrever linha resumo: {e}")
                try:
                    pdf.cell(0, 5, safe_line[:100] if len(safe_line) > 100 else safe_line, ln=True)
                except:
                    pass
        pdf.ln(3)

    def _write_findings(self, pdf, findings: Iterable[ReportFindingItem]) -> None:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Achados prioritarios", ln=True)
        pdf.set_font("Helvetica", "", 10)

        has_any = False
        for index, finding in enumerate(findings, start=1):
            has_any = True
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(
                0,
                6,
                self._safe_text(
                    f"{index}. [{finding.severity}] {finding.host} - "
                    f"{finding.service_port} - {finding.reference}"
                ),
            )
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, self._safe_text(f"Descricao: {finding.description}"))
            pdf.multi_cell(0, 5, self._safe_text(f"CVSS: {finding.cvss}"))
            pdf.multi_cell(
                0,
                5,
                self._safe_text(f"Recomendacao: {finding.recommendation}"),
            )
            pdf.ln(1)

        if not has_any:
            pdf.multi_cell(0, 6, "Nenhum achado relevante para o escopo selecionado.")

        pdf.ln(3)

    def _write_results(self, pdf, results: Iterable[ReportResultItem]) -> None:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Resultados tecnicos", ln=True)
        pdf.set_font("Helvetica", "", 10)

        has_any = False
        for result in results:
            has_any = True
            header = (
                f"{result.host} ({result.ip}) - {result.port}/{result.protocol} - "
                f"{result.service} - status={result.status} - risco={result.risk}"
            )
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 5, self._safe_text(header))
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, self._safe_text(f"Versao: {result.version}"))
            pdf.multi_cell(0, 5, self._safe_text(f"Sistema: {result.os_name}"))
            pdf.multi_cell(0, 5, self._safe_text(f"Referencia: {result.reference}"))
            if result.recommendation:
                pdf.multi_cell(
                    0,
                    5,
                    self._safe_text(f"Recomendacao: {result.recommendation}"),
                )
            pdf.ln(1)

        if not has_any:
            pdf.multi_cell(0, 6, "Nenhum resultado tecnico disponivel para este relatorio.")

    @staticmethod
    def _safe_text(value: str) -> str:
        return value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2022", "*")
