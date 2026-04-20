from __future__ import annotations

import re


class NmapParser:
    def parse(self, raw_output: str) -> list[dict[str, str]]:
        lines = [line.rstrip() for line in raw_output.splitlines()]
        results: list[dict[str, str]] = []

        for line in lines:
            if not line.strip():
                continue

            normalized = line.strip()
            if normalized.lower().startswith("port") and "state" in normalized.lower():
                continue

            if not self._looks_like_port_line(normalized):
                continue

            parts = normalized.split()
            if len(parts) < 3:
                continue

            port_proto = parts[0]
            status = self._normalize_status(parts[1])
            service = parts[2]
            version = " ".join(parts[3:]) if len(parts) > 3 else "-"

            if "/" not in port_proto:
                continue

            port, protocol = port_proto.split("/", 1)
            results.append(
                {
                    "port": port,
                    "protocol": protocol.upper(),
                    "status": status,
                    "service": service,
                    "version": version,
                }
            )

        return results

    @staticmethod
    def _looks_like_port_line(line: str) -> bool:
        return bool(re.match(r"^\d+/(tcp|udp)\s+\S+\s+\S+", line, re.IGNORECASE))

    @staticmethod
    def _normalize_status(status: str) -> str:
        mapping = {
            "open": "Aberta",
            "filtered": "Filtrada",
            "closed": "Fechada",
        }
        return mapping.get(status.lower(), status.capitalize())
