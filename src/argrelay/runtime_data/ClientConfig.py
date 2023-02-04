from dataclasses import dataclass

from argrelay.runtime_data.ConnectionConfig import ConnectionConfig


@dataclass(frozen = True)
class ClientConfig:
    use_local_requests: bool
    connection_config: ConnectionConfig
