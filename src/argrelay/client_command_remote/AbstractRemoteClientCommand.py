from dataclasses import asdict

import requests

from argrelay.client_pipeline.PipeSrcAbstract import PipeSrcAbstract
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommand import AbstractClientCommand
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.server_spec.CallContext import CallContext
from argrelay.server_spec.const_int import BASE_URL_FORMAT


# TODO: remove Abstract:
class AbstractRemoteClientCommand(AbstractClientCommand):

    def __init__(
        self,
        # TODO: reorder args:
        call_ctx: CallContext,
        pipe_src: PipeSrcAbstract,
        connection_config: ConnectionConfig,
    ):
        # TODO: reorder assignments:
        super().__init__(
            call_ctx,
        )
        self.pipe_src: PipeSrcAbstract = pipe_src
        self.connection_config: ConnectionConfig = connection_config

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
                self.pipe_src.accept_bytes(response_obj.content)
            else:
                raise RuntimeError
        finally:
            ElapsedTime.measure("after_handle_response")
