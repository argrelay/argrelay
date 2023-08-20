from argrelay.client_spec.ShellContext import ShellContext
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client import AbstractClientCommand
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig


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
        shell_ctx: ShellContext,
    ) -> AbstractClientCommand:
        shell_ctx.print_debug()
        command_obj = self.command_factory.create_command(shell_ctx)
        command_obj.execute_command()
        ElapsedTime.measure("after_execute_command")
        return command_obj
