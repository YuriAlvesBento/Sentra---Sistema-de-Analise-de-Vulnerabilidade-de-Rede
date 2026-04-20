"""
Perfis de scan com diferentes niveis de complexidade e tempo.
Cada perfil define as flags nmap a serem usadas como base.
"""

SCAN_PROFILES = {
    0: {
        "name": "Rapido",
        "description": "Descoberta basica de hosts e portas principais",
        "nmap_flags": ["-sV", "-Pn", "--open", "--top-ports", "100"],
        "timeout": 20,
        "estimated_time": "5-10s por host",
    },
    1: {
        "name": "Completo",
        "description": "Varredura ampliada de portas e servicos",
        "nmap_flags": ["-sV", "-Pn", "--open", "-p-"],
        "timeout": 90,
        "estimated_time": "30-60s por host",
    },
    2: {
        "name": "Deteccao de servicos",
        "description": "Versoes, banners e contexto operacional com scripts",
        "nmap_flags": ["-sV", "-Pn", "-sC", "--open", "--top-ports", "1000"],
        "timeout": 60,
        "estimated_time": "15-30s por host",
    },
    3: {
        "name": "Auditoria avancada",
        "description": "Coleta ampliada com OS detection e scripts NSE",
        "nmap_flags": [
            "-sV",
            "-Pn",
            "-O",
            "-sC",
            "--open",
            "-p-",
            "--script",
            "vuln,default",
        ],
        "timeout": 180,
        "estimated_time": "60-120s por host",
    },
}


def get_scan_profile(scan_type: int) -> dict:
    return SCAN_PROFILES.get(scan_type, SCAN_PROFILES[0])


def get_nmap_flags(
    scan_type: int,
    os_detection: bool = False,
    version_detection: bool = True,
    nse_enabled: bool = False,
    full_port_scan: bool = False,
    firewall_detection: bool = False,
    custom_ports: str = "",
    timing_template: str = "Normal (T3)",
    host_timeout_ms: int = 3000,
    parallelism: int | None = None,
) -> tuple[list[str], int]:
    profile = get_scan_profile(scan_type)
    flags = profile["nmap_flags"].copy()
    timeout = profile["timeout"]

    if not version_detection:
        flags = [flag for flag in flags if flag != "-sV"]
    elif "-sV" not in flags:
        flags.insert(0, "-sV")

    if not nse_enabled:
        flags = _strip_script_flags(flags)
    elif "--script" not in flags and "-sC" not in flags:
        flags.extend(["--script", "vuln,default"])

    if "-O" in flags and not os_detection:
        flags = [flag for flag in flags if flag != "-O"]
    elif os_detection and "-O" not in flags:
        flags.insert(2, "-O")
        timeout = int(timeout * 1.5)

    if full_port_scan and not custom_ports:
        flags = _strip_port_scope_flags(flags)
        flags.append("-p-")
        timeout = int(timeout * 1.4)

    if custom_ports:
        flags = _strip_port_scope_flags(flags)
        flags.extend(["-p", custom_ports])

    if firewall_detection and "-sA" not in flags:
        flags.append("-sA")
        timeout = int(timeout * 1.1)
    elif not firewall_detection and "-sA" in flags:
        flags = [flag for flag in flags if flag != "-sA"]

    timing_flag = _build_timing_flag(timing_template)
    if timing_flag not in flags:
        flags.append(timing_flag)

    if parallelism is not None and parallelism > 1:
        flags = [flag for flag in flags if flag != "--min-parallelism"]
        flags.extend(["--min-parallelism", str(parallelism)])

    return flags, timeout


def _build_timing_flag(timing_template: str) -> str:
    mapping = {
        "Silenciosa (T1)": "-T1",
        "Normal (T3)": "-T3",
        "Elevada (T4)": "-T4",
        "Maxima (T5)": "-T5",
    }
    return mapping.get(timing_template, "-T3")


def _strip_port_scope_flags(flags: list[str]) -> list[str]:
    cleaned: list[str] = []
    skip_next = False

    for flag in flags:
        if skip_next:
            skip_next = False
            continue

        if flag in {"--top-ports", "-p"}:
            skip_next = True
            continue

        if flag == "-p-":
            continue

        cleaned.append(flag)

    return cleaned


def _strip_script_flags(flags: list[str]) -> list[str]:
    cleaned: list[str] = []
    skip_next = False

    for flag in flags:
        if skip_next:
            skip_next = False
            continue

        if flag == "--script":
            skip_next = True
            continue

        if flag == "-sC":
            continue

        cleaned.append(flag)

    return cleaned
