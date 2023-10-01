from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.handler_response.ProposeArgValuesClientResponseHandler import ProposeArgValuesClientResponseHandler
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_response.InterpResultSchema import interp_result_desc
from argrelay.server_spec.CallContext import CallContext


class ProposeArgValuesRemoteClientCommand(AbstractRemoteClientCommand):
    """
    This command is unused most of the time in favor of another (optimized):
    `ProposeArgValuesRemoteOptimizedClientCommand`

    See `completion_perf_notes.md` for details.

    This non-optimized implementation is still useful to get access to
    internal server state in tests via `LocalClient` - see FS_66_17_43_42 test_infra / special test mode #1.

    To enable use of this command, see:
    *   ClientConfig.optimize_completion_request
    *   LocalClientEnvMockBuilder
    """

    def __init__(
        self,
        call_ctx: CallContext,
        connection_config: ConnectionConfig,
    ):
        super().__init__(
            call_ctx = call_ctx,
            connection_config = connection_config,
            response_handler = ProposeArgValuesClientResponseHandler(),
            response_schema = interp_result_desc.dict_schema,
        )
