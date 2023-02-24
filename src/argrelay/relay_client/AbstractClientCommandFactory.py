from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.RunMode import RunMode

from argrelay.relay_client import AbstractClientCommand
from argrelay.runtime_context.InputContext import InputContext
from argrelay.server_spec.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    RELAY_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
)


class AbstractClientCommandFactory:

    def create_command_by_server_path(self, server_path: str) -> AbstractClientCommand:
        pass

    def create_command(self, input_ctx: InputContext):
        server_path = self.select_command(input_ctx)
        return self.create_command_by_server_path(server_path)

    @staticmethod
    def select_command(input_ctx: InputContext) -> str:
        if input_ctx.run_mode == RunMode.InvocationMode:
            if input_ctx.comp_type == CompType.DescribeArgs:
                return DESCRIBE_LINE_ARGS_PATH
            else:
                assert input_ctx.comp_type == CompType.InvokeAction
                return RELAY_LINE_ARGS_PATH
        else:
            assert input_ctx.run_mode == RunMode.CompletionMode
            return PROPOSE_ARG_VALUES_PATH
