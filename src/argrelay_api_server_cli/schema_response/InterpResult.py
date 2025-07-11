from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from argrelay_api_server_cli.schema_response.ArgValues import ArgValues
from argrelay_app_server.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_app_server.runtime_context.token_bucket_utils import (
    token_buckets_to_token_ipos_list,
)


@dataclass
class InterpResult(ArgValues):
    """
    See also :class:`InterpResultSchema`.

    Unlike `InvocationInput` this class contains at most one `data_envelope` per `envelope_container`
    because it executes in the mode which queries values only for latency-sensitive Tab-completion.
    """

    all_tokens: list[str] = field()
    """
    Copy from `ParsedContext.all_tokens` - command line args.
    """

    excluded_tokens: list[int] = field()
    """
    Copy from `InterpContext.excluded_tokens` -
    indexes into `all_tokens` pointing to tokens with special meaning (e.g. tangent token, `token_bucket` separator, ...).
    """

    consumed_token_buckets: list[list[int]] = field()
    """
    Copy from `InterpContext.consumed_token_buckets` -
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

    @staticmethod
    def from_interp_context(
        interp_ctx: InterpContext,
    ) -> InterpResult:
        return InterpResult(
            arg_values=interp_ctx.comp_suggestions,
            all_tokens=interp_ctx.parsed_ctx.all_tokens,
            excluded_tokens=interp_ctx.excluded_tokens,
            consumed_token_buckets=interp_ctx.consumed_token_buckets,
            envelope_containers=interp_ctx.envelope_containers,
            tan_token_ipos=interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part=interp_ctx.parsed_ctx.tan_token_l_part,
        )

    def get_data_envelopes(self) -> list[dict]:
        data_envelopes = []
        for envelope_container in self.envelope_containers:
            data_envelopes.extend(envelope_container.data_envelopes)
        return data_envelopes

    def consumed_token_ipos_list(
        self,
    ) -> list[int]:
        return token_buckets_to_token_ipos_list(self.consumed_token_buckets)
