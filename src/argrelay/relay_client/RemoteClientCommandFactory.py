from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.server_spec.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    RELAY_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
)


class RemoteClientCommandFactory(AbstractClientCommandFactory):
    client_config: ClientConfig

    def __init__(
        self,
        client_config: ClientConfig,
    ):
        self.client_config = client_config

    # noinspection PyMethodMayBeStatic
    def create_command_by_server_path(self, server_path: str) -> "AbstractRemoteClientCommand":
        if server_path == DESCRIBE_LINE_ARGS_PATH:
            from argrelay.client_command_remote.DescribeLineArgsRemoteClientCommand import (
                DescribeLineArgsRemoteClientCommand,
            )
            return DescribeLineArgsRemoteClientCommand(self.client_config.connection_config)
        if server_path == PROPOSE_ARG_VALUES_PATH:
            from argrelay.client_command_remote.ProposeArgValuesRemoteClientCommand import (
                ProposeArgValuesRemoteClientCommand,
            )
            return ProposeArgValuesRemoteClientCommand(self.client_config.connection_config)
        if server_path == RELAY_LINE_ARGS_PATH:
            from argrelay.client_command_remote.RelayLineArgsRemoteClientCommand import (
                RelayLineArgsRemoteClientCommand,
            )
            return RelayLineArgsRemoteClientCommand(self.client_config.connection_config)
        raise RuntimeError
