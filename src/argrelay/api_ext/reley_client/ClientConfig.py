from dataclasses import dataclass

from argrelay.api_ext.ConnectionConfig import ConnectionConfig


@dataclass(frozen = True)
class ClientConfig:
    use_local_requests: bool
    connection_config: ConnectionConfig
