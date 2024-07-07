from dataclasses import asdict

import requests

from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.client_pipeline.BytesSrcAbstract import BytesSrcAbstract
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.server_spec.CallContext import CallContext
from argrelay.server_spec.const_int import BASE_URL_FORMAT


class ClientCommandRemoteWorkerJson(ClientCommandRemoteAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
        connection_config: ConnectionConfig,
        bytes_src: BytesSrcAbstract,
    ):
        super().__init__(
            call_ctx,
        )
        self.connection_config: ConnectionConfig = connection_config
        self.bytes_src: BytesSrcAbstract = bytes_src

    def execute_command(
        self,
    ):
        server_url = BASE_URL_FORMAT.format(**asdict(self.connection_config)) + f"{self.call_ctx.server_action.value}"
        headers_dict = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # NOTE: So far, single `CallContextSchema` is reused for all client requests:
        request_json = call_context_desc.dict_schema.dumps(self.call_ctx)
        ElapsedTime.measure("before_request")
        response_obj = requests.post(
            server_url,
            headers = headers_dict,
            data = request_json,
        )
        ElapsedTime.measure("after_request")
        try:
            if response_obj.ok:
                self.bytes_src.accept_bytes(response_obj.content)
            else:
                self.raise_error(response_obj.status_code)
        finally:
            ElapsedTime.measure("after_handle_response")
