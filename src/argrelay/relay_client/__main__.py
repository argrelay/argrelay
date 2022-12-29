# @formatter:off
from argrelay.misc_helper.ElapsedTime import ElapsedTime
ElapsedTime.measure("after_program_entry")
# @formatter:on

from argrelay.api_ext.ConnectionConfig import ConnectionConfig
from argrelay.api_ext.relay_server.ServerConfig import ServerConfig
from argrelay.api_ext.relay_server.ServerConfigSchema import server_config_desc
from argrelay.api_ext.reley_client.ClientConfigSchema import client_config_desc

from argrelay.api_int.meta_data import CompType, RunMode
from argrelay.relay_client.command_impl.AbstractCommand import AbstractCommand
from argrelay.relay_client.command_impl.DescribeLineArgsCommand import DescribeLineArgsCommand
from argrelay.relay_client.command_impl.ProposeArgValuesCommand import ProposeArgValuesCommand
from argrelay.relay_client.command_impl.RelayLineArgsCommand import RelayLineArgsCommand

import sys

from argrelay.relay_server.call_context import ParsedContext, CommandContext
from argrelay.shared_unit.call_context import InputContext

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
