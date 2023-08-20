from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.server_spec.CallContext import CallContext


class DescribeLineArgsRemoteClientCommand(AbstractRemoteClientCommand):

    def __init__(
        self,
        call_ctx: CallContext,
        connection_config: ConnectionConfig,
    ):
        super().__init__(
            call_ctx = call_ctx,
            connection_config = connection_config,
            response_handler = DescribeLineArgsClientResponseHandler(),
            response_schema = interp_result_desc.dict_schema,
        )
