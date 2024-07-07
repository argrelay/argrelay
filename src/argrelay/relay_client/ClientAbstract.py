from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client import ClientCommandAbstract
from argrelay.relay_client.ClientCommandFactoryAbstract import ClientCommandFactoryAbstract
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.server_spec.CallContext import CallContext


class ClientAbstract:
    """
    An abstract `relay_client` to `relay_server`
    """

    def __init__(
        self,
        client_config: ClientConfig,
        command_factory: ClientCommandFactoryAbstract
    ):
        self.client_config: ClientConfig = client_config
        self.command_factory: ClientCommandFactoryAbstract = command_factory

    # noinspection PyMethodMayBeStatic
    def make_request(
        self,
        call_ctx: CallContext,
    ) -> ClientCommandAbstract:
        command_obj = self.command_factory.create_command(call_ctx)
        command_obj.execute_command()
        ElapsedTime.measure("after_execute_command")
        return command_obj
