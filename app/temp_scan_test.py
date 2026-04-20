from modules.scanner.scan_service import ScanService

service = ScanService()
results = service.execute_network_scan(
    '127.0.0.1',
    scan_type=0,
    os_detection=True,
    version_detection=True,
    nse_enabled=False,
    full_port_scan=False,
    firewall_detection=False,
    custom_ports='',
    timing_template='Normal (T3)',
    host_timeout_ms=3000,
    parallelism=1,
)
print('RESULT_COUNT=', len(results))
print(results)
