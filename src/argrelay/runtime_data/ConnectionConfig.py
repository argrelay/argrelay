from dataclasses import dataclass


@dataclass(frozen = True)
class ConnectionConfig:
    server_host_name: str
    server_port_number: int
