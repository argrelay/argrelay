from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_client.relay_client import ClientCommandAbstract
from argrelay_lib_root.enum_desc.ProcRole import ProcRole
from argrelay_lib_root.enum_desc.ServerAction import ServerAction


class ClientCommandFactoryAbstract:

    def create_command(
        self,
        call_ctx: CallContext,
    ) -> ClientCommandAbstract:
        pass


def select_client_response_handler(
    proc_role: ProcRole,
    server_action: ServerAction,
):
    if server_action is ServerAction.ProposeArgValues:
        """
        This handler is unused most of the time in favor of direct (optimized):
        `BytesHandlerTextProposeArgValuesOptimized`

        See `completion_perf_notes.md` for details.

        This non-optimized implementation is still useful to get access to
        internal server state in tests via `ClientLocal` - see FS_66_17_43_42 test_infra / special test mode #1.

        To enable use of this command, see:
        *   ClientConfig.optimize_completion_request
        *   LocalClientEnvMockBuilder
        """
        from argrelay_app_client.handler_response.ClientResponseHandlerProposeArgValues import (
            ClientResponseHandlerProposeArgValues
        )
        return ClientResponseHandlerProposeArgValues()
    if server_action is ServerAction.DescribeLineArgs:
        from argrelay_app_client.handler_response.ClientResponseHandlerDescribeLineArgs import (
            ClientResponseHandlerDescribeLineArgs
        )
        return ClientResponseHandlerDescribeLineArgs()
    if server_action is ServerAction.RelayLineArgs:
        if proc_role == ProcRole.CheckEnvWorker:
            from argrelay_app_client.handler_response.ClientResponseHandlerCheckEnv import (
                ClientResponseHandlerCheckEnv
            )
            return ClientResponseHandlerCheckEnv()
        else:
            from argrelay_app_client.handler_response.ClientResponseHandlerRelayLineArgs import (
                ClientResponseHandlerRelayLineArgs
            )
            return ClientResponseHandlerRelayLineArgs()
    raise RuntimeError
