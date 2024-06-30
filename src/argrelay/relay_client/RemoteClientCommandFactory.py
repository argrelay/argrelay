from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.client_pipeline.BytesHandlerJson import BytesHandlerJson
from argrelay.client_pipeline.PipeSrcLocal import PipeSrcLocal
from argrelay.client_pipeline.PipeSrcSender import PipeSrcSender
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.server_spec.CallContext import CallContext


class RemoteClientCommandFactory(AbstractClientCommandFactory):

    def __init__(
        self,
        client_config: ClientConfig,
        is_split_mode: bool,
        child_pipe_src,
    ):
        self.client_config: ClientConfig = client_config
        self.is_split_mode: bool = is_split_mode
        self.child_pipe_src = child_pipe_src
        if is_split_mode:
            assert self.child_pipe_src is not None
        else:
            assert self.child_pipe_src is None

    @staticmethod
    def select_response_handler(
        server_action: ServerAction,
    ):
        if server_action is ServerAction.ProposeArgValues:
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
            from argrelay.handler_response.ProposeArgValuesClientResponseHandler import (
                ProposeArgValuesClientResponseHandler
            )
            return ProposeArgValuesClientResponseHandler()
        if server_action is ServerAction.DescribeLineArgs:
            from argrelay.handler_response.DescribeLineArgsClientResponseHandler import (
                DescribeLineArgsClientResponseHandler
            )
            return DescribeLineArgsClientResponseHandler()
        if server_action is ServerAction.RelayLineArgs:
            from argrelay.handler_response.RelayLineArgsClientResponseHandler import (
                RelayLineArgsClientResponseHandler
            )
            return RelayLineArgsClientResponseHandler()

    # noinspection PyMethodMayBeStatic
    def create_command(
        self,
        call_ctx: CallContext,
    ) -> AbstractRemoteClientCommand:

        if self.is_split_mode:
            return AbstractRemoteClientCommand(
                call_ctx,
                PipeSrcSender(
                    self.child_pipe_src,
                ),
                self.client_config.connection_config,
            )
        else:
            return AbstractRemoteClientCommand(
                call_ctx,
                PipeSrcLocal(
                    BytesHandlerJson(
                        self.select_response_handler(
                            call_ctx.server_action,
                        ),
                    ),
                ),
                self.client_config.connection_config,
            )

