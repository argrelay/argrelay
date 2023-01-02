from dataclasses import asdict

import requests
from marshmallow import Schema

from argrelay.data_schema.RequestContextSchema import request_context_desc
from argrelay.meta_data.ConnectionConfig import ConnectionConfig
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.runtime_context.InputContext import InputContext
from argrelay.server_spec.const_int import BASE_URL_FORMAT


class AbstractCommand:
    server_path: str
    response_schema: Schema
    request_schema: Schema

    def __init__(
        self,
        server_path,
        response_schema,
        request_schema = request_context_desc.object_schema,
    ):
        self.server_path = server_path
        self.response_schema = response_schema
        self.request_schema = request_schema

    def execute_command(self, connection_config: ConnectionConfig, input_ctx: InputContext):
        server_url = BASE_URL_FORMAT.format(**asdict(connection_config)) + f"{self.server_path}"
        headers_dict = {
            "Content-Type": "application/json",
        }
        request_json = self.request_schema.dumps(input_ctx)
        ElapsedTime.measure("before_request")
        response = requests.post(
            server_url,
            headers = headers_dict,
            json = request_json,
        )
        ElapsedTime.measure("after_request")
        if response.ok:
            response_data = self.response_schema.loads(response.text)
            print("\n".join(response_data["arg_values"]))
        else:
            raise RuntimeError
