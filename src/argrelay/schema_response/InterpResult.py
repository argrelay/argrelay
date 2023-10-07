from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer


@dataclass
class InterpResult:
    """
    See also :class:`InterpResultSchema`.

    Unlike `InvocationInput` this class contains at most one `data_envelope` per `envelope_container`
    because interpretation for Tab-completion is latency-sensitive.

    Both `InterpResult` and `InvocationInput` might be combined in the future.
    """

    all_tokens: list[str] = field()
    """
    Copy from `ParsedContext.all_tokens` - command line args.
    """

    consumed_tokens: list[int] = field()
    """
    Copy from `InterpContext.consumed_tokens` -
    indexes into `all_tokens` pointing to tokens consumed during interpretation.
    """

    envelope_containers: list[EnvelopeContainer] = field()

    tan_token_ipos: int = field()
    """
    Value from `ParsedContext.tan_token_ipos`.
    """

    tan_token_l_part: str = field()
    """
    Value from `ParsedContext.tan_token_l_part`.
    """

    def get_data_envelopes(self) -> list[dict]:
        data_envelopes = []
        for envelope_container in self.envelope_containers:
            data_envelopes.extend(envelope_container.data_envelopes)
        return data_envelopes
