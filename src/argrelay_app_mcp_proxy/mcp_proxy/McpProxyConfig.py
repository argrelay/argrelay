from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)


@dataclass(frozen=True)
class McpProxyConfig:
    __comment__: str = field()
    log_dir_rel_path: str = field()
    heartbeat_interval_sec: float = field(default=5.0)
