from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from argrelay_lib_root.schema_config.ConnectionConfig import ConnectionConfig


@dataclass(frozen = True)
class ClientConfig:
    __comment__: str = field()
    use_local_requests: bool = field()
    optimize_completion_request: bool = field()
    redundant_servers: list[ConnectionConfig] = field()
    show_pending_spinner: bool = field()
    spinless_sleep_sec: float = field()
