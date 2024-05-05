from dataclasses import dataclass, field

from argrelay.runtime_data.ConnectionConfig import ConnectionConfig


@dataclass(frozen = True)
class ClientConfig:
    __comment__: str = field()
    use_local_requests: bool = field()
    optimize_completion_request: bool = field()
    connection_config: ConnectionConfig = field()
    show_pending_spinner: bool = field()
    spinless_sleep_sec: float = field()
