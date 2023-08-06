import json
from dataclasses import asdict

import requests
from marshmallow import Schema

from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommand import AbstractClientCommand
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_request.RequestContextSchema import request_context_desc
from argrelay.server_spec.const_int import BASE_URL_FORMAT


class AbstractRemoteClientCommand(AbstractClientCommand):

    def __init__(
        self,
        server_path: str,
        connection_config: ConnectionConfig,
        response_handler: AbstractClientResponseHandler,
        response_schema: Schema,
        request_schema: Schema = request_context_desc.dict_schema,
    ):
        super().__init__(
            response_handler,
        )
        self.server_path: str = server_path
        self.connection_config: ConnectionConfig = connection_config
        self.response_schema: Schema = response_schema
        self.request_schema: Schema = request_schema

    def execute_command(self, input_ctx: InputContext):
        server_url = BASE_URL_FORMAT.format(**asdict(self.connection_config)) + f"{self.server_path}"
        headers_dict = {
            "Content-Type": "application/json",
        }
        request_json = self.request_schema.dumps(input_ctx)
        ElapsedTime.measure("before_request")
        response_obj = requests.post(
            server_url,
            headers = headers_dict,
            json = request_json,
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
