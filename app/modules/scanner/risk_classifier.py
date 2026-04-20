from __future__ import annotations


class RiskClassifier:
    _risk_by_service = {
        "ssh": "ALTO",
        "http": "MEDIO",
        "https": "MEDIO",
    }

    def classify(self, parsed: list[dict[str, str]]) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []

        for item in parsed:
            service_key = item.get("service", "").lower()
            risk = self._risk_by_service.get(service_key, "BAIXO")
            description = f"Servico {service_key} identificado com status {item.get('status')}"
            recommendation = (
                "Revisar configuracao e aplicar politicas de acesso."
                if risk != "BAIXO"
                else "Monitorar e manter configuracao atualizada."
            )

            results.append(
                {
                    "port": item.get("port", ""),
                    "protocol": item.get("protocol", ""),
                    "status": item.get("status", ""),
                    "service": item.get("service", ""),
                    "risk": risk,
                    "reference": "Risco inicial",
                    "description": description,
                    "recommendation": recommendation,
                }
            )

        return results
