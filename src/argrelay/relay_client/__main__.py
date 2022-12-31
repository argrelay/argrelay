# @formatter:off
from argrelay.misc_helper.ElapsedTime import ElapsedTime
ElapsedTime.measure("after_program_entry")
# @formatter:on

from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.runtime_context.CommandContext import CommandContext
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.meta_data.ConnectionConfig import ConnectionConfig
from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.data_schema.ServerConfigSchema import server_config_desc
from argrelay.data_schema.ClientConfigSchema import client_config_desc
from argrelay.client_command.AbstractCommand import AbstractCommand
from argrelay.client_command.DescribeLineArgsCommand import DescribeLineArgsCommand
from argrelay.client_command.ProposeArgValuesCommand import ProposeArgValuesCommand
from argrelay.client_command.RelayLineArgsCommand import RelayLineArgsCommand

import sys

ElapsedTime.measure("after_imports")


def main():
    input_ctx = InputContext.from_env(sys.argv)
    client_config = client_config_desc.from_default_file()
    if client_config.use_local_requests:
        local_request(input_ctx)
    else:
        remote_request(input_ctx, client_config.connection_config)

    ElapsedTime.measure("on_exit")
    if input_ctx.is_debug_enabled:
        ElapsedTime.print_all()


def local_request(input_ctx: InputContext):
    server_config: ServerConfig = server_config_desc.from_default_file()
    ElapsedTime.measure("after_config_load")
    parsed_ctx = ParsedContext.from_instance(input_ctx)
    # TODO: this will not work without loading plugins:
    #       refactor "local server" and start it in both cases for REST-wrapped remote and direct one built into client like here:
    command_ctx = CommandContext(parsed_ctx, server_config.static_data, server_config.interp_factories)
    command_ctx.interpret_command()
    ElapsedTime.measure("after_interp")
    command_ctx.invoke_action()


def remote_request(input_ctx: InputContext, connection_config: ConnectionConfig):
    command_obj = select_command(input_ctx)
    command_obj.execute_command(connection_config)


def select_command(input_ctx) -> AbstractCommand:
    if input_ctx.run_mode == RunMode.CompletionMode:
        if input_ctx.comp_type == CompType.DescribeArgs:
            return DescribeLineArgsCommand()
        else:
            return ProposeArgValuesCommand()
    else:
        return RelayLineArgsCommand()


if __name__ == "__main__":
    ElapsedTime.measure("after_main_entry")
    main()
