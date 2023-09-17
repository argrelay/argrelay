from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.schema_response.BaseResponse import BaseResponse


@dataclass
class InterpResult(BaseResponse):
    """
    See also :class:`InterpResultSchema`.

    Unlike `InvocationInput` this class contains at most one `data_envelope` per `envelope_container`
    because interpretation for Tab-completion is latency-sensitive.

    Both `InterpResult` and `InvocationInput` might be combined in the future.
    """

    envelope_containers: list[EnvelopeContainer] = field()

    tan_token_ipos: int = field()
    """
    Value from `ParsedContext.tan_token_ipos`.
    """

    tan_token_l_part: str = field(default = 0)
    """
    Value from `ParsedContext.tan_token_l_part`.
    """
