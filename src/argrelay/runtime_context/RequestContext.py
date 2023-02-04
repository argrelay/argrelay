from dataclasses import dataclass

from argrelay.enum_desc.CompType import CompType


@dataclass(frozen = True)
class RequestContext:
    """
    Part of :class:`InputContext` which is used in requests from client to server.
    """

    command_line: str
    cursor_cpos: int
    comp_type: CompType
    is_debug_enabled: bool

    def __post_init__(self):
        assert 0 <= self.cursor_cpos <= len(self.command_line)
