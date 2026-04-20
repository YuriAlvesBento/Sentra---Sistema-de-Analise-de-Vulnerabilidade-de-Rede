from __future__ import annotations

from datetime import datetime

from modules.scanner.nmap_runner import NmapRunner
from modules.scanner.parser import NmapParser
from modules.scanner.risk_classifier import RiskClassifier
from modules.scanner.scan_profiles import get_nmap_flags, get_scan_profile


class ScanService:
    def __init__(self):
        self.runner = NmapRunner()
        self.parser = NmapParser()
        self.classifier = RiskClassifier()

    def execute_network_scan(
        self,
        network: str,
        scan_type: int = 0,
        os_detection: bool = False,
        version_detection: bool = True,
        nse_enabled: bool = False,
        full_port_scan: bool = False,
        firewall_detection: bool = False,
        custom_ports: str = "",
        timing_template: str = "Normal (T3)",
        host_timeout_ms: int = 3000,
        parallelism: int | None = None,
    ) -> list[dict[str, str]]:
        profile = get_scan_profile(scan_type)
        nmap_flags, timeout = get_nmap_flags(
            scan_type=scan_type,
            os_detection=os_detection,
            version_detection=version_detection,
            nse_enabled=nse_enabled,
            full_port_scan=full_port_scan,
            firewall_detection=firewall_detection,
            custom_ports=custom_ports,
            timing_template=timing_template,
            parallelism=parallelism,
        )
        if host_timeout_ms > 0:
            timeout = max(timeout, int(host_timeout_ms / 1000))

        print("[SCAN] ========== INICIANDO NOVO SCAN ==========")
        print(f"[SCAN] Tipo: {profile['name'].upper()}")
        print(f"[SCAN] Descricao: {profile['description']}")
        print(f"[SCAN] Tempo estimado: {profile['estimated_time']}")
        print(f"[SCAN] Alvo: {network}")
        print(f"[SCAN] Flags Nmap: {' '.join(nmap_flags)}")
        print(f"[SCAN] Timeout do processo: {timeout}s por host")
        if os_detection:
            print("[SCAN] >> OS detection ativado")
        if firewall_detection:
            print("[SCAN] >> Indicadores de filtragem/firewall ativados")
        if custom_ports:
            print(f"[SCAN] >> Portas customizadas: {custom_ports}")

        hosts = self.runner.discover_hosts(network)
        print(f"[SCAN] Hosts a escanear: {hosts}")

        if not hosts:
            print("[SCAN] Nenhum host valido encontrado!")
            return []

        all_results: list[dict[str, str]] = []

        for index, host in enumerate(hosts, start=1):
            print(f"\n[SCAN] ===== [{index}/{len(hosts)}] Escaneando: {host} =====")

            try:
                raw_output = self.runner.run(host, nmap_flags, timeout)
            except TimeoutError as error:
                print(f"[SCAN] TIMEOUT em {host}: {error} - pulando para o proximo host")
                continue
            except Exception as error:
                print(f"[SCAN] ERRO em {host}: {error} - pulando para o proximo host")
                continue

            if not raw_output:
                print(f"[SCAN] {host}: nenhuma porta relevante encontrada")
                continue

            try:
                parsed = self.parser.parse(raw_output)
                print(f"[SCAN] {host}: encontradas {len(parsed)} portas relevantes")

                classified = self.classifier.classify(parsed)

                for item in classified:
                    item["host"] = host
                    item.setdefault("ip", host)
                    item.setdefault("version", "-")
                    item.setdefault("os", "-")
                    item.setdefault("cvss", "-")
                    item.setdefault(
                        "detected_at",
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    )

                all_results.extend(classified)
                print(f"[SCAN] {host}: processadas {len(classified)} entradas")
            except Exception as error:
                print(f"[SCAN] ERRO ao processar {host}: {error}")
                continue

        print("\n[SCAN] ========== SCAN FINALIZADO ==========")
        print(f"[SCAN] Total de registros: {len(all_results)}")
        print(f"[SCAN] Perfil: {profile['name']}")
        return all_results
