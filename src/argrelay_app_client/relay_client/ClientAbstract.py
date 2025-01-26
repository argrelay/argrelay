from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_client.relay_client import ClientCommandAbstract
from argrelay_app_client.relay_client.ClientCommandFactoryAbstract import ClientCommandFactoryAbstract
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay_schema_config_client.runtime_data_client_app.ClientConfig import ClientConfig


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
