from __future__ import annotations

from json import dumps

from flasgger import swag_from
from flask import request, Blueprint, Response, abort

from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.handler_request.DescribeLineArgsServerRequestHandler import DescribeLineArgsServerRequestHandler
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.handler_request.RelayLineArgsServerRequestHandler import RelayLineArgsServerRequestHandler
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.schema_response.ArgValuesSchema import arg_values_
from argrelay.server_spec import DescribeLineArgsSpec, ProposeArgValuesSpec, RelayLineArgsSpec
from argrelay.server_spec.CallContext import CallContext


def create_blueprint_api(local_server: LocalServer):
    blueprint_api = Blueprint("blueprint_api", __name__)

    describe_line_args_handler = DescribeLineArgsServerRequestHandler(local_server)
    propose_arg_values_handler = ProposeArgValuesServerRequestHandler(local_server)
    relay_line_args_handler = RelayLineArgsServerRequestHandler(local_server)

    def create_call_ctx() -> CallContext:
        ElapsedTime.clear_measurements()
        ElapsedTime.measure("before_request_payload_load")

        call_ctx: CallContext
        if request.content_type is None:
            data_json = request.data.decode("utf-8")
            call_ctx = call_context_desc.dict_schema.loads(data_json)
        elif request.content_type == "application/json":
            call_ctx = call_context_desc.dict_schema.load(request.json)
        else:
            abort(415)

        ElapsedTime.measure("after_call_context_creation")
        ElapsedTime.is_debug_enabled = call_ctx.is_debug_enabled
        return call_ctx

    @blueprint_api.route(
        ServerAction.ProposeArgValues.value,
        methods = ["post"],
    )
    @swag_from(ProposeArgValuesSpec.spec_data)
    def propose_arg_values():
        try:
            call_ctx = create_call_ctx()
            response_dict = propose_arg_values_handler.handle_request(call_ctx)

            if request.accept_mimetypes["text/plain"] or len(request.accept_mimetypes) == 0:
                # Required for `ProposeArgValuesRemoteOptimizedClientCommand`:
                # Sending "text/plain" (default) for stripped down clients (who may not even specify headers)
                # also serving perf reasons on client side (trivial parsing, no lib required, minimal imports):
                return Response(
                    "\n".join(response_dict[arg_values_]),
                    mimetype = "text/plain",
                )
            elif request.accept_mimetypes["application/json"]:
                # JSON - parsing lib is required on the client side:
                response_json = dumps(response_dict)
                return Response(
                    response_json,
                    mimetype = "application/json",
                )
            else:
                # Not acceptable:
                abort(406)
        finally:
            ElapsedTime.measure("before_sending_response")

    @blueprint_api.route(
        ServerAction.DescribeLineArgs.value,
        methods = ["post"],
    )
    @swag_from(DescribeLineArgsSpec.spec_data)
    def describe_line_args():
        try:
            call_ctx = create_call_ctx()
            response_dict = describe_line_args_handler.handle_request(call_ctx)

            if request.accept_mimetypes["application/json"] or len(request.accept_mimetypes) == 0:
                response_json = dumps(response_dict)
                return Response(
                    response_json,
                    mimetype = "application/json",
                )
            else:
                # Not acceptable:
                abort(406)
        finally:
            ElapsedTime.measure("before_sending_response")

    @blueprint_api.route(
        ServerAction.RelayLineArgs.value,
        methods = ["post"],
    )
    @swag_from(RelayLineArgsSpec.spec_data)
    def relay_line_args():
        try:
            call_ctx = create_call_ctx()
            response_dict = relay_line_args_handler.handle_request(call_ctx)

            if request.accept_mimetypes["application/json"] or len(request.accept_mimetypes) == 0:
                response_json = dumps(response_dict)
                return Response(
                    response_json,
                    mimetype = "application/json",
                )
            else:
                # Not acceptable:
                abort(406)
        finally:
            ElapsedTime.measure("before_sending_response")

    @blueprint_api.teardown_request
    def show_teardown(exception):
        ElapsedTime.print_all_if_debug()

    return blueprint_api
