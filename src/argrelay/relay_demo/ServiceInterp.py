from __future__ import annotations

from argrelay.interp_plugin.ArgProcessor import ArgProcessor
from argrelay.interp_plugin.GenericInterp import GenericInterp
from argrelay.relay_demo.CodeMaturityProcessor import CodeMaturityProcessor
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.runtime_context.CommandContext import CommandContext

"""
`ServiceInterp` is a configured use case of :class:`GenericInterp` for auto-completion of service attributes.

The command line tokens are translated to typed args.
A user keeps adding the typed arg values until all requited types unambiguously specify what to do:
    `[some_command] rw upstream goto amer`
The order is (usually) not important.

If there is an ambiguity, auto-completion suggests possible options -
in this case, the missing option is `CodeMaturity` ("prod", "qa", "dev", ...):
    `[some_command] rw upstream goto amer prod`

Each arg value belongs to its own type (see :class:`ServiceArgType`), for example:
*   "rw": `AccessType`
*   "upstream": `FlowStage`
*   "goto": `ActionType`
*   "amer": `GeoRegion`
*   "prod": `CodeMaturity`
These types are:
*   discrete (limited set of values) and
*   non-orthogonal (possible values of one type may affect/depend on already given values for another type).

TODO: fix description (below): not just value, first by its key, then by its item position (ipos), then by its value.
The arg type is determined by its value.
If value sets from different arg types overlap, the order of the args becomes important,
but it does not have to be remembered because auto-completion suggest them according to that order.
"""


class ServiceInterp(GenericInterp):

    def __init__(self, command_ctx: CommandContext, config_dict: dict):
        keys_to_types = config_dict["keys_to_types"]
        # reverse:
        types_to_keys = {v: k for k, v in keys_to_types.items()}

        super().__init__(
            command_ctx,
            config_dict,
            [
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.ActionType.name],
                    ServiceArgType.ActionType.name,
                ),
                CodeMaturityProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.CodeMaturity.name],
                ),
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.FlowStage.name],
                    ServiceArgType.FlowStage.name,
                ),
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.GeoRegion.name],
                    ServiceArgType.GeoRegion.name,
                ),
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.HostName.name],
                    ServiceArgType.HostName.name,
                ),
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.ServiceName.name],
                    ServiceArgType.ServiceName.name,
                ),
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.AccessType.name],
                    ServiceArgType.AccessType.name,
                ),
                ArgProcessor(
                    command_ctx.static_data,
                    types_to_keys[ServiceArgType.ColorTag.name],
                    ServiceArgType.ColorTag.name,
                ),
            ],
        )
