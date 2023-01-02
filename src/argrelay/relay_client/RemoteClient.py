from argrelay.client_command.AbstractCommand import AbstractCommand
from argrelay.client_command.DescribeLineArgsCommand import DescribeLineArgsCommand
from argrelay.client_command.ProposeArgValuesCommand import ProposeArgValuesCommand
from argrelay.client_command.RelayLineArgsCommand import RelayLineArgsCommand
from argrelay.meta_data.ClientConfig import ClientConfig
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.runtime_context.InputContext import InputContext


class RemoteClient:
    """
    Client remote to server
    """

    client_config: ClientConfig

    @staticmethod
    def make_request(client_config: ClientConfig, input_ctx: InputContext) -> None:
        assert not client_config.use_local_requests

        command_obj = RemoteClient.select_command(input_ctx)
        command_obj.execute_command(client_config.connection_config, input_ctx)
        ElapsedTime.measure("after_request_processed")

    @staticmethod
    def select_command(input_ctx) -> AbstractCommand:
        if input_ctx.run_mode == RunMode.CompletionMode:
            if input_ctx.comp_type == CompType.DescribeArgs:
                return DescribeLineArgsCommand()
            else:
                return ProposeArgValuesCommand()
        else:
            return RelayLineArgsCommand()
