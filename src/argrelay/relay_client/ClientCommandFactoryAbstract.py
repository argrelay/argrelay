from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.relay_client import ClientCommandAbstract
from argrelay.server_spec.CallContext import CallContext


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
        from argrelay.handler_response.ClientResponseHandlerProposeArgValues import (
            ClientResponseHandlerProposeArgValues
        )
        return ClientResponseHandlerProposeArgValues()
    if server_action is ServerAction.DescribeLineArgs:
        from argrelay.handler_response.ClientResponseHandlerDescribeLineArgs import (
            ClientResponseHandlerDescribeLineArgs
        )
        return ClientResponseHandlerDescribeLineArgs()
    if server_action is ServerAction.RelayLineArgs:
        if proc_role == ProcRole.CheckEnvWorker:
            from argrelay.handler_response.ClientResponseHandlerCheckEnv import (
                ClientResponseHandlerCheckEnv
            )
            return ClientResponseHandlerCheckEnv()
        else:
            from argrelay.handler_response.ClientResponseHandlerRelayLineArgs import (
                ClientResponseHandlerRelayLineArgs
            )
            return ClientResponseHandlerRelayLineArgs()
    raise RuntimeError
