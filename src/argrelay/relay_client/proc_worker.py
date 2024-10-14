from argrelay.misc_helper_common.ElapsedTime import ElapsedTime


def worker_main(
    call_ctx,
    client_config,
    proc_role,
    is_optimized_completion,
    w_pipe_end,
    server_index: int,
) -> "ClientCommandAbstract":
    if client_config.use_local_requests:
        # This branch with `use_local_requests` is used only for testing
        # (to inspect internal server data via `ClientLocal` and `LocalServer`):
        from argrelay.test_infra.ClientLocal import ClientLocal
        abstract_client = ClientLocal(
            client_config,
        )
    else:
        from argrelay.relay_client.ClientRemote import ClientRemote
        abstract_client = ClientRemote(
            client_config,
            proc_role,
            w_pipe_end,
            is_optimized_completion,
            server_index,
        )

    ElapsedTime.measure("before_client_invocation")
    command_obj = abstract_client.make_request(call_ctx)

    ElapsedTime.measure("on_exit")
    if call_ctx.is_debug_enabled:
        ElapsedTime.print_all()
    return command_obj
