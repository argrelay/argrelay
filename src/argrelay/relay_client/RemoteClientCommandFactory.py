from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.server_spec.CallContext import CallContext


class RemoteClientCommandFactory(AbstractClientCommandFactory):

    def __init__(
        self,
        client_config: ClientConfig,
    ):
        self.client_config: ClientConfig = client_config

    # noinspection PyMethodMayBeStatic
    def create_command(
        self,
        call_ctx: CallContext,
    ) -> AbstractRemoteClientCommand:
        if call_ctx.server_action is ServerAction.ProposeArgValues:
            from argrelay.client_command_remote.ProposeArgValuesRemoteClientCommand import (
                ProposeArgValuesRemoteClientCommand,
            )
            return ProposeArgValuesRemoteClientCommand(
                call_ctx,
                self.client_config.connection_config,
            )
        if call_ctx.server_action is ServerAction.DescribeLineArgs:
            from argrelay.client_command_remote.DescribeLineArgsRemoteClientCommand import (
                DescribeLineArgsRemoteClientCommand,
            )
            return DescribeLineArgsRemoteClientCommand(
                call_ctx,
                self.client_config.connection_config,
            )
        if call_ctx.server_action is ServerAction.RelayLineArgs:
            from argrelay.client_command_remote.RelayLineArgsRemoteClientCommand import (
                RelayLineArgsRemoteClientCommand,
            )
            return RelayLineArgsRemoteClientCommand(
                call_ctx,
                self.client_config.connection_config,
            )
        raise RuntimeError
