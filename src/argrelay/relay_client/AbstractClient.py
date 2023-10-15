import argrelay.relay_client.__main__ as relay_client_main
from argrelay.relay_client import AbstractClientCommand
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.server_spec.CallContext import CallContext


class AbstractClient:
    """
    An abstract `relay_client` to `relay_server`
    """

    def __init__(
        self,
        client_config: ClientConfig,
        command_factory: AbstractClientCommandFactory
    ):
        self.client_config: ClientConfig = client_config
        self.command_factory: AbstractClientCommandFactory = command_factory

    # noinspection PyMethodMayBeStatic
    def make_request(
        self,
        call_ctx: CallContext,
    ) -> AbstractClientCommand:
        command_obj = self.command_factory.create_command(call_ctx)
        return relay_client_main.make_request(
            command_obj,
        )
