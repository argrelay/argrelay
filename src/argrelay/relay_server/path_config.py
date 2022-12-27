import inspect

from flasgger import swag_from
from flask import request, Blueprint

from argrelay.api_ext.relay_server.ServerConfig import ServerConfig
from argrelay.api_int.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
    RELAY_LINE_ARGS_PATH,
)
from argrelay.api_int.data_schema.ArgValuesSchema import arg_values_desc
from argrelay.api_int.data_schema.RequestContextSchema import request_context_desc
from argrelay.api_int.meta_data import RunMode, CompType
from argrelay.api_int.server_op import DescribeLineArgsSpec, RelayLineArgsSpec, ProposeArgValuesSpec
from argrelay.relay_server.call_context import ParsedContext, CommandContext
from argrelay.shared_unit.call_context import InputContext


def create_blueprint(server_config: ServerConfig):
    root_blueprint = Blueprint("root_blueprint", __name__)

    def interpret_command(input_ctx: InputContext) -> CommandContext:
        parsed_ctx = ParsedContext.from_instance(input_ctx)
        # TODO: Split server_config and static_data (both top level, not config including data):
        command_ctx = CommandContext(parsed_ctx, server_config.static_data, server_config.interp_factories)
        command_ctx.interpret_command()
        return command_ctx

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(DESCRIBE_LINE_ARGS_PATH, methods = ['post'])
    @swag_from(DescribeLineArgsSpec.spec_data)
    def describe_line_args():
        # TODO: move implementation to command_impl instance:
        request_ctx = request_context_desc.object_schema.loads(request.json)
        input_ctx = InputContext.from_request_context(
            request_ctx,
            run_mode = RunMode.CompletionMode,
            comp_key = "0",
        )
        assert input_ctx.comp_type == CompType.DescribeArgs
        command_ctx = interpret_command(input_ctx)
        # TODO: Print to stdout/stderr on client side. Send back data instead:
        command_ctx.invoke_action()
        # TODO: send data instead of text:
        return inspect.currentframe().f_code.co_name

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(PROPOSE_ARG_VALUES_PATH, methods = ['post'])
    @swag_from(ProposeArgValuesSpec.spec_data)
    def propose_arg_values():
        # TODO: move implementation to command_impl instance:
        request_ctx = request_context_desc.object_schema.loads(request.json)
        input_ctx = InputContext.from_request_context(
            request_ctx,
            run_mode = RunMode.CompletionMode,
            comp_key = "0",
        )
        assert input_ctx.comp_type != CompType.DescribeArgs
        assert input_ctx.comp_type != CompType.InvokeAction
        command_ctx = interpret_command(input_ctx)
        response_dict = {
            "arg_values": command_ctx.propose_arg_values()
        }
        return arg_values_desc.object_schema.dumps(response_dict)

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(RELAY_LINE_ARGS_PATH, methods = ['post'])
    @swag_from(RelayLineArgsSpec.spec_data)
    def relay_line_args():
        # TODO: move implementation to command_impl instance:
        request_ctx = request_context_desc.object_schema.loads(request.json)
        input_ctx = InputContext.from_request_context(
            request_ctx,
            run_mode = RunMode.CompletionMode,
            comp_key = "0",
        )
        assert input_ctx.comp_type == CompType.InvokeAction

        # TODO: remove:
        print(input_ctx)

        command_ctx = interpret_command(input_ctx)
        command_ctx.invoke_action()
        # TODO: send data instead of text:
        return inspect.currentframe().f_code.co_name

    return root_blueprint
