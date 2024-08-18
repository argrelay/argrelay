from __future__ import annotations

from dataclasses import dataclass

from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.ServerAction import ServerAction


@dataclass
class UsageStatsEntry:
    """
    Stored entry for FS_87_02_77_34: usage stats.
    """

    server_action: ServerAction

    comp_scope: CompScope

    server_ts_ns: int = 0

    client_version: str = ""

    client_conf_target: str = ""

    client_user_id: str = ""

    command_line: str = ""

    cursor_cpos: int = 0
