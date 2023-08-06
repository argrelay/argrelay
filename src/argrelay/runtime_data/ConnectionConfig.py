from dataclasses import dataclass, field


@dataclass(frozen = True)
class ConnectionConfig:
    server_host_name: str = field()
    server_port_number: int = field()
