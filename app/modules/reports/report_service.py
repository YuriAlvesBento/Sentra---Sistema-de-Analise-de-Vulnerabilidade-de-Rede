from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from modules.reports.exporter import (
    PdfReportExporter,
    ReportDocument,
    ReportExportError,
    ReportFindingItem,
    ReportFormat,
    ReportMetadata,
    ReportResultItem,
    ReportSummary,
    TextReportExporter,
    render_text_report,
)


class ReportService:
    def build_report(
        self,
        *,
        report_type: str,
        target: str,
        scan_type: str,
        operator: str,
        results: Iterable[Mapping[str, Any]],
        findings: Iterable[Mapping[str, Any]],
        include_recommendations: bool = True,
        include_references: bool = True,
        generated_at: datetime | None = None,
    ) -> ReportDocument:
        timestamp = generated_at or datetime.now()
        filtered_results, filtered_findings, notes = self._filter_content(
            report_type=report_type,
            results=results,
            findings=findings,
        )

        result_items = [
            self._build_result_item(
                row,
                include_recommendations=include_recommendations,
                include_references=include_references,
            )
            for row in filtered_results
        ]
        finding_items = [
            self._build_finding_item(
                row,
                include_recommendations=include_recommendations,
                include_references=include_references,
            )
            for row in filtered_findings
        ]

        summary = self._build_summary(result_items, finding_items)
        metadata = ReportMetadata(
            title=self._build_title(report_type),
            report_type=report_type,
            target=target,
            scan_type=scan_type,
            operator=operator,
            generated_at=timestamp,
            risk_level=self._compute_overall_risk(result_items, finding_items),
            notes=notes,
        )

        return ReportDocument(
            metadata=metadata,
            summary=summary,
            results=result_items,
            findings=finding_items,
        )

    def export_report(
        self,
        report: ReportDocument,
        destination: str | Path,
        output_format: str,
    ) -> Path:
        resolved_format = ReportFormat.from_value(output_format)
        output_path = Path(destination)

        if output_path.suffix.lower() != f".{resolved_format.value}":
            output_path = output_path.with_suffix(f".{resolved_format.value}")

        exporter = self._get_exporter(resolved_format)
        return exporter.export(report, output_path)

    def preview_text(self, report: ReportDocument) -> str:
        return render_text_report(report)

    def report_to_dict(self, report: ReportDocument) -> dict[str, Any]:
        return asdict(report)

    def _build_result_item(
        self,
        row: Mapping[str, Any],
        *,
        include_recommendations: bool,
        include_references: bool,
    ) -> ReportResultItem:
        return ReportResultItem(
            host=str(row.get("host", "-")),
            ip=str(row.get("ip", "-")),
            port=str(row.get("port", "-")),
            protocol=str(row.get("protocol", "-")),
            service=str(row.get("service", "-")),
            version=str(row.get("version", "-")),
            os_name=str(row.get("os", "-")),
            status=str(row.get("status", "-")),
            risk=str(row.get("risk", "-")),
            reference=str(row.get("reference", "-")) if include_references else "-",
            description=str(row.get("description", "")),
            recommendation=(
                str(row.get("recommendation", "")) if include_recommendations else ""
            ),
        )

    def _build_finding_item(
        self,
        row: Mapping[str, Any],
        *,
        include_recommendations: bool,
        include_references: bool,
    ) -> ReportFindingItem:
        return ReportFindingItem(
            severity=str(row.get("severity", row.get("risk", "-"))),
            reference=str(row.get("reference", "-")) if include_references else "-",
            description=str(row.get("description", "-")),
            host=str(row.get("host", "-")),
            service_port=str(row.get("service_port", "-")),
            cvss=str(row.get("cvss", "-")),
            recommendation=(
                str(row.get("recommendation", "")) if include_recommendations else ""
            ),
        )

    def _build_summary(
        self,
        results: list[ReportResultItem],
        findings: list[ReportFindingItem],
    ) -> ReportSummary:
        host_count = len({item.ip for item in results if item.ip != "-"})
        service_count = len(results)
        open_ports = sum(1 for item in results if item.status.lower() == "aberta")

        severity_counts = {
            level: 0 for level in ("CRITICO", "ALTO", "MEDIO", "BAIXO")
        }
        for finding in findings:
            level = finding.severity.upper()
            if level in severity_counts:
                severity_counts[level] += 1

        return ReportSummary(
            total_hosts=host_count,
            total_services=service_count,
            total_open_ports=open_ports,
            total_findings=len(findings),
            critical_findings=severity_counts["CRITICO"],
            high_findings=severity_counts["ALTO"],
            medium_findings=severity_counts["MEDIO"],
            low_findings=severity_counts["BAIXO"],
        )

    def _compute_overall_risk(
        self,
        results: list[ReportResultItem],
        findings: list[ReportFindingItem],
    ) -> str:
        priority = {"CRITICO": 4, "ALTO": 3, "MEDIO": 2, "BAIXO": 1}
        highest = 0
        highest_label = "BAIXO"

        for level in [item.risk for item in results] + [item.severity for item in findings]:
            normalized = str(level).upper()
            if priority.get(normalized, 0) > highest:
                highest = priority[normalized]
                highest_label = normalized

        return highest_label

    def _build_title(self, report_type: str) -> str:
        return f"SENTRA - Relatorio {report_type}"

    def _filter_content(
        self,
        *,
        report_type: str,
        results: Iterable[Mapping[str, Any]],
        findings: Iterable[Mapping[str, Any]],
    ) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]], list[str]]:
        normalized_type = report_type.strip().lower()
        result_rows = list(results)
        finding_rows = list(findings)
        notes: list[str] = []

        if normalized_type == "apenas criticos":
            result_rows = [
                row for row in result_rows if str(row.get("risk", "")).upper() == "CRITICO"
            ]
            finding_rows = [
                row
                for row in finding_rows
                if str(row.get("severity", row.get("risk", ""))).upper() == "CRITICO"
            ]
            notes.append("Escopo filtrado somente para itens criticos.")
        elif normalized_type == "por host":
            result_rows = sorted(result_rows, key=lambda row: (str(row.get("host", "")), str(row.get("ip", ""))))
            finding_rows = sorted(finding_rows, key=lambda row: (str(row.get("host", "")), str(row.get("reference", ""))))
            notes.append("Resultados organizados por host para facilitar analise individual.")
        elif normalized_type == "executivo (sumario)":
            notes.append("Relatorio resumido para visao gerencial e priorizacao rapida.")
        elif normalized_type == "conformidade pci-dss":
            notes.append("Relatorio orientado a pontos relevantes de exposicao para PCI-DSS.")
        elif normalized_type == "conformidade iso 27001":
            notes.append("Relatorio orientado a controles e remediacoes alinhadas a ISO 27001.")

        return result_rows, finding_rows, notes

    @staticmethod
    def _get_exporter(report_format: ReportFormat):
        if report_format is ReportFormat.TXT:
            return TextReportExporter()
        if report_format is ReportFormat.PDF:
            return PdfReportExporter()
        raise ReportExportError(f"Formato nao suportado: {report_format.value}")
