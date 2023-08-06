from dataclasses import dataclass, field

from argrelay.enum_desc.CompType import CompType


@dataclass(frozen = True)
class RequestContext:
    """
    Part of :class:`InputContext` which is used in requests from client to server.
    """

    command_line: str = field()
    cursor_cpos: int = field()
    comp_type: CompType = field()
    is_debug_enabled: bool = field()

    def __post_init__(self):
        assert 0 <= self.cursor_cpos <= len(self.command_line)
