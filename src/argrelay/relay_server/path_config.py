from flasgger import swag_from
from flask import request, Blueprint

from argrelay.enum_desc.RunMode import RunMode
from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.handler_request.DescribeLineArgsServerRequestHandler import DescribeLineArgsServerRequestHandler
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.handler_request.RelayLineArgsServerRequestHandler import RelayLineArgsServerRequestHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_desc, arg_values_
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.server_spec import DescribeLineArgsSpec, ProposeArgValuesSpec, RelayLineArgsSpec
from argrelay.server_spec.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
    RELAY_LINE_ARGS_PATH,
)


def create_blueprint(local_server: LocalServer):
    root_blueprint = Blueprint("root_blueprint", __name__)

    describe_line_args_handler = DescribeLineArgsServerRequestHandler(local_server)
    propose_arg_values_handler = ProposeArgValuesServerRequestHandler(local_server)
    relay_line_args_handler = RelayLineArgsServerRequestHandler(local_server)

    def create_input_ctx(run_mode: RunMode):
        ElapsedTime.clear_measurements()
        ElapsedTime.measure("before_request_payload_load")
        # TODO: Figure out why:
        #       *   requests by `ProposeArgValuesRemoteClientCommand` arrive as dict
        #       *   requests by `AbstractRemoteClientCommand` arrive as str
        request_ctx = None
        if isinstance(request.json, str):
            request_ctx = request_context_desc.dict_schema.loads(request.json)
        if isinstance(request.json, dict):
            request_ctx = request_context_desc.dict_schema.load(request.json)
        input_ctx = AbstractServerRequestHandler.create_input_ctx(request_ctx, run_mode)
        ElapsedTime.measure("after_input_context_creation")
        ElapsedTime.is_debug_enabled = input_ctx.is_debug_enabled
        return input_ctx

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(DESCRIBE_LINE_ARGS_PATH, methods = ['post'])
    @swag_from(DescribeLineArgsSpec.spec_data)
    def describe_line_args():
        input_ctx = create_input_ctx(RunMode.CompletionMode)
        response_dict = describe_line_args_handler.handle_request(input_ctx)
        response_json = interp_result_desc.dict_schema.dumps(response_dict)

        ElapsedTime.measure("before_sending_response")
        return response_json

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(PROPOSE_ARG_VALUES_PATH, methods = ['post'])
    @swag_from(ProposeArgValuesSpec.spec_data)
    def propose_arg_values():
        input_ctx = create_input_ctx(RunMode.CompletionMode)
        response_dict = propose_arg_values_handler.handle_request(input_ctx)

        # Sending plain text is used for perf reasons on client side (minimal parsing required, minimal imports):
        send_plain_text = True
        try:
            if send_plain_text:
                return "\n".join(response_dict[arg_values_])
            else:
                response_json = arg_values_desc.dict_schema.dumps(response_dict)
                return response_json
        finally:
            ElapsedTime.measure("before_sending_response")

    # TODO: Add REST test on client and server side.
    @root_blueprint.route(RELAY_LINE_ARGS_PATH, methods = ['post'])
    @swag_from(RelayLineArgsSpec.spec_data)
    def relay_line_args():
        input_ctx = create_input_ctx(RunMode.InvocationMode)
        response_dict = relay_line_args_handler.handle_request(input_ctx)
        response_json = invocation_input_desc.dict_schema.dumps(response_dict)
        ElapsedTime.measure("before_sending_response")
        return response_json

    @root_blueprint.teardown_request
    def show_teardown(exception):
        ElapsedTime.print_all_if_debug()

    return root_blueprint
