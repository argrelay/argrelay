from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_response.InterpResult import InterpResult


@dataclass
class InvocationInput(InterpResult):
    """
    See also :class:`InvocationInputSchema`.

    Unlike `InterpResult` this class provides full list of `data_envelope`-s per `envelope_container`
    because invocation is not latency-sensitive and funcs expect all `data_envelope`-s.
    """

    delegator_plugin_entry: PluginEntry = field()
    """
    The `PluginEntry` taken from config on the server side to let client invoke that plugin.

    It is assumed that server and client code, if not of the same version, at least, compatible.
    """

    custom_plugin_data: dict = field()
    """
    A placeholder dict for exclusive use by plugin.

    Whatever plugin server side needs to tell its plugin peer on the client side.
    """

    @staticmethod
    def with_interp_context(
        interp_ctx: InterpContext,
        delegator_plugin_entry: PluginEntry,
        custom_plugin_data: dict,
    ) -> InvocationInput:
        return InvocationInput(
            arg_values = interp_ctx.comp_suggestions,
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            excluded_tokens = interp_ctx.excluded_tokens,
            consumed_arg_buckets = interp_ctx.consumed_arg_buckets,
            envelope_containers = interp_ctx.envelope_containers,
            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
            delegator_plugin_entry = delegator_plugin_entry,
            custom_plugin_data = custom_plugin_data,
        )
