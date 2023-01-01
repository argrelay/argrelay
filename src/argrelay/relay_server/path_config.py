import inspect

from flasgger import swag_from
from flask import request, Blueprint

from argrelay.data_schema.ArgValuesSchema import arg_values_desc
from argrelay.data_schema.RequestContextSchema import request_context_desc
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.RunMode import RunMode
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.server_spec import DescribeLineArgsSpec, ProposeArgValuesSpec, RelayLineArgsSpec
from argrelay.server_spec.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
    RELAY_LINE_ARGS_PATH,
)


def create_blueprint(local_server: LocalServer):
    root_blueprint = Blueprint("root_blueprint", __name__)

    def interpret_command(input_ctx: InputContext) -> InterpContext:
        parsed_ctx = ParsedContext.from_instance(input_ctx)
        # TODO: Split server_config and static_data (both top level, not config including data):
        interp_ctx = InterpContext(
            parsed_ctx,
            local_server.server_config.static_data,
            local_server.server_config.interp_factories,
            local_server.get_mongo_database(),
        )
        interp_ctx.interpret_command()
        return interp_ctx

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(DESCRIBE_LINE_ARGS_PATH, methods = ['post'])
    @swag_from(DescribeLineArgsSpec.spec_data)
    def describe_line_args():
        # TODO: move implementation to command_impl instance:
        request_ctx = request_context_desc.object_schema.loads(request.json)
        input_ctx = InputContext.from_request_context(
            request_ctx,
            run_mode = RunMode.CompletionMode,
            comp_key = str(0),
        )
        assert input_ctx.comp_type == CompType.DescribeArgs
        interp_ctx = interpret_command(input_ctx)
        # TODO: Print to stdout/stderr on client side. Send back data instead:
        interp_ctx.invoke_action()
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
            comp_key = str(0),
        )
        assert input_ctx.comp_type != CompType.DescribeArgs
        assert input_ctx.comp_type != CompType.InvokeAction
        interp_ctx = interpret_command(input_ctx)
        response_dict = {
            "arg_values": interp_ctx.propose_arg_values()
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
            run_mode = RunMode.InvocationMode,
            comp_key = str(0),
        )
        assert input_ctx.comp_type == CompType.InvokeAction

        # TODO: remove:
        print(input_ctx)

        interp_ctx = interpret_command(input_ctx)
        interp_ctx.invoke_action()
        # TODO: send data instead of text:
        return inspect.currentframe().f_code.co_name

    return root_blueprint
