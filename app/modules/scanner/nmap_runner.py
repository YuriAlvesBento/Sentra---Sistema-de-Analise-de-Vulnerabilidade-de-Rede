from __future__ import annotations

import ipaddress
import re
import shutil
import subprocess
from itertools import islice
from pathlib import Path


class NmapRunner:
    NMAP_PATHS = [
        r"C:\Program Files (x86)\Nmap\nmap.exe",
        r"C:\Program Files\Nmap\nmap.exe",
    ]

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def _find_nmap(self) -> str | None:
        for path in self.NMAP_PATHS:
            if Path(path).exists():
                return path
        return shutil.which("nmap")

    def discover_hosts(self, network: str) -> list[str]:
        try:
            net = ipaddress.ip_network(network, strict=False)

            if net.num_addresses == 1:
                return [str(net.network_address)]

            nmap_binary = self._find_nmap()
            if nmap_binary and net.num_addresses <= 4096:
                discovery_command = [nmap_binary, "-sn", "-n", network]
                print(f"[SCAN] Descobrindo hosts ativos em {network}...")
                try:
                    process = subprocess.run(
                        discovery_command,
                        capture_output=True,
                        text=True,
                        timeout=max(20, self.timeout * 3),
                    )
                    discovered = self._parse_discovery_output(process.stdout)
                    if discovered:
                        print(f"[SCAN] Hosts ativos encontrados: {discovered}")
                        return discovered
                except subprocess.TimeoutExpired:
                    print(f"[SCAN] Descoberta de hosts excedeu o limite em {network}.")
                except Exception as error:
                    print(f"[SCAN] Falha na descoberta real de hosts: {error}")

            fallback_hosts = [str(host) for host in islice(net.hosts(), 3)]
            print(
                f"[SCAN] Usando descoberta simplificada para {network}. "
                f"Escopo reduzido a: {fallback_hosts}"
            )
            return fallback_hosts
        except ValueError:
            print(f"[SCAN] Input '{network}' nao e CIDR valido. Tratando como host unico.")
            return [network]

    def run(
        self, host: str, nmap_flags: list[str] | None = None, timeout: int | None = None
    ) -> str:
        if nmap_flags is None:
            nmap_flags = ["-sV", "-Pn", "--open", "--top-ports", "100"]
        if timeout is None:
            timeout = self.timeout

        nmap_binary = self._find_nmap()
        if nmap_binary:
            command = [nmap_binary] + nmap_flags + [host]
            print(f"[SCAN] >>> Iniciando nmap em {host}...")
            print(f"[SCAN] >>> Flags: {' '.join(nmap_flags)}")

            try:
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                raw_output = process.stdout.strip()
                if not raw_output:
                    print(f"[SCAN] <<< {host}: Nenhuma porta aberta encontrada")
                    return ""
                lines_count = len(raw_output.splitlines())
                print(f"[SCAN] <<< {host}: Concluido com {lines_count} linhas")
                return raw_output
            except subprocess.TimeoutExpired as error:
                print(f"[SCAN] <<< {host}: TIMEOUT apos {timeout}s")
                raise TimeoutError(f"Nmap timeout em {host}: {error}")
            except Exception as error:
                print(f"[SCAN] <<< {host}: ERRO ao executar nmap: {error}")
                raise Exception(f"Erro nmap em {host}: {error}")

        print(f"[SCAN] >>> Nmap nao encontrado. Usando dados simulados para {host}")
        services = [
            "22/tcp open ssh",
            "80/tcp open http",
            "443/tcp open https",
        ]
        return "\n".join(services)

    @staticmethod
    def _parse_discovery_output(raw_output: str) -> list[str]:
        hosts: list[str] = []
        for line in raw_output.splitlines():
            normalized = line.strip()
            if "Nmap scan report for" not in normalized:
                continue

            match = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)$", normalized)
            if match:
                hosts.append(match.group(1))
                continue

            match = re.search(r"for (\d+\.\d+\.\d+\.\d+)$", normalized)
            if match:
                hosts.append(match.group(1))

        return hosts
