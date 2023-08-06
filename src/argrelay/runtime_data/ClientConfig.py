from dataclasses import dataclass, field

from argrelay.runtime_data.ConnectionConfig import ConnectionConfig


@dataclass(frozen = True)
class ClientConfig:
    use_local_requests: bool = field()
    connection_config: ConnectionConfig = field()
