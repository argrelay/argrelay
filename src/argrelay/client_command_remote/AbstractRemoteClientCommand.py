import json
from dataclasses import asdict

import requests
from marshmallow import Schema

from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommand import AbstractClientCommand
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.server_spec.CallContext import CallContext
from argrelay.server_spec.const_int import BASE_URL_FORMAT


class AbstractRemoteClientCommand(AbstractClientCommand):

    def __init__(
        self,
        call_ctx: CallContext,
        connection_config: ConnectionConfig,
        response_handler: AbstractClientResponseHandler,
        response_schema: Schema,
        request_schema: Schema = call_context_desc.dict_schema,
    ):
        super().__init__(
            response_handler,
        )
        self.call_ctx: CallContext = call_ctx
        self.connection_config: ConnectionConfig = connection_config
        self.response_schema: Schema = response_schema
        self.request_schema: Schema = request_schema

    def execute_command(
        self,
    ):
        server_url = BASE_URL_FORMAT.format(**asdict(self.connection_config)) + f"{self.call_ctx.server_action.value}"
        headers_dict = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        request_json = self.request_schema.dumps(self.call_ctx)
        ElapsedTime.measure("before_request")
        response_obj = requests.post(
            server_url,
            headers = headers_dict,
            data = request_json,
        )
        ElapsedTime.measure("after_request")
        try:
            if response_obj.ok:
                # Leave both object creation and validation via schemas to `response_handler`.
                # Just deserialize into dict here:
                response_dict = json.loads(response_obj.text)
                ElapsedTime.measure("after_deserialization")
                self.response_handler.handle_response(response_dict)
            else:
                raise RuntimeError
        finally:
            ElapsedTime.measure("after_handle_response")
