from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.relay_client.ClientCommandFactoryAbstract import (
    ClientCommandFactoryAbstract,
    select_client_response_handler,
)
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.server_spec.CallContext import CallContext


class ClientCommandFactoryRemote(ClientCommandFactoryAbstract):
    """
    Constructs communication between `ProcRole.ParentProcSpinner` and `ProcRole.ChildProcWorker`.

    Part of FS_14_59_14_06 pending requests implementation.
    """

    def __init__(
        self,
        client_config: ClientConfig,
        proc_role: ProcRole,
        w_pipe_end,
        is_optimized_completion: bool,
        server_index: int,
    ):
        self.client_config: ClientConfig = client_config
        self.proc_role: ProcRole = proc_role
        self.w_pipe_end = w_pipe_end
        self.is_optimized_completion = is_optimized_completion
        self.server_index = server_index
        if proc_role.is_worker_proc and proc_role.is_split_mode:
            assert self.w_pipe_end is not None
        else:
            assert self.w_pipe_end is None

    # noinspection PyMethodMayBeStatic
    def create_command(
        self,
        call_ctx: CallContext,
    ) -> ClientCommandRemoteAbstract:

        if self.proc_role.is_worker_proc:
            if self.is_optimized_completion:
                from argrelay.client_command_remote.ClientCommandRemoteWorkerTextProposeArgValuesOptimized import (
                    ClientCommandRemoteWorkerTextProposeArgValuesOptimized,
                )
                command_cls = ClientCommandRemoteWorkerTextProposeArgValuesOptimized
                if self.proc_role.is_split_mode:
                    from argrelay.client_pipeline.BytesSrcSender import BytesSrcSender
                    bytes_src = BytesSrcSender(
                        self.w_pipe_end,
                    )
                else:
                    from argrelay.client_pipeline.BytesSrcLocal import BytesSrcLocal
                    from argrelay.client_pipeline.BytesHandlerTextProposeArgValuesOptimized import (
                        BytesHandlerTextProposeArgValuesOptimized,
                    )
                    bytes_src = BytesSrcLocal(
                        BytesHandlerTextProposeArgValuesOptimized(),
                    )
            else:
                from argrelay.client_command_remote.ClientCommandRemoteWorkerJson import (
                    ClientCommandRemoteWorkerJson,
                )
                command_cls = ClientCommandRemoteWorkerJson
                if self.proc_role.is_split_mode:
                    from argrelay.client_pipeline.BytesSrcSender import BytesSrcSender
                    bytes_src = BytesSrcSender(
                        self.w_pipe_end,
                    )
                else:
                    from argrelay.client_pipeline.BytesSrcLocal import BytesSrcLocal
                    from argrelay.client_pipeline.BytesHandlerJson import BytesHandlerJson
                    bytes_src = BytesSrcLocal(
                        BytesHandlerJson(
                            select_client_response_handler(
                                self.proc_role,
                                call_ctx.server_action,
                            ),
                        ),
                    )
            return command_cls(
                call_ctx,
                self.proc_role,
                self.client_config.redundant_servers,
                self.server_index,
                bytes_src,
            )
        else:
            from argrelay.client_command_remote.ClientCommandRemoteSpinner import ClientCommandRemoteSpinner
            if self.is_optimized_completion:
                from argrelay.client_pipeline.BytesHandlerTextProposeArgValuesOptimized import (
                    BytesHandlerTextProposeArgValuesOptimized,
                )
                bytes_handler = BytesHandlerTextProposeArgValuesOptimized()
            else:
                from argrelay.client_pipeline.BytesHandlerJson import BytesHandlerJson
                bytes_handler = BytesHandlerJson(
                    select_client_response_handler(
                        self.proc_role,
                        call_ctx.server_action,
                    ),
                )
            return ClientCommandRemoteSpinner(
                call_ctx,
                self.proc_role,
                bytes_handler,
            )
