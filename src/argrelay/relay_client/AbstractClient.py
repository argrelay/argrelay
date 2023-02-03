from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client import AbstractClientCommand
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_data.ClientConfig import ClientConfig


class AbstractClient:
    """
    An abstract `relay_client` to `relay_server`
    """

    client_config: ClientConfig
    command_factory: AbstractClientCommandFactory

    def __init__(self, client_config: ClientConfig, command_factory: AbstractClientCommandFactory):
        self.client_config = client_config
        self.command_factory = command_factory

    # noinspection PyMethodMayBeStatic
    def make_request(self, input_ctx: InputContext) -> AbstractClientCommand:
        input_ctx.print_debug()
        command_obj = self.command_factory.create_command(input_ctx)
        command_obj.execute_command(input_ctx)
        ElapsedTime.measure("after_execute_command")
        return command_obj
