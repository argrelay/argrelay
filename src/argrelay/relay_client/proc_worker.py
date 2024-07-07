import signal

from argrelay.misc_helper_common import eprint
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime

has_error_happened = False


def _signal_handler(signal_number, signal_frame):
    if signal_number == signal.SIGALRM:
        # Import hanged:
        eprint("ERROR: `import` hanged - see: https://github.com/argrelay/argrelay/issues/89")
        global has_error_happened
        has_error_happened = True


def worker_main(
    call_ctx,
    client_config,
    proc_role,
    is_optimized_completion,
    w_pipe_end,
    shell_ctx,
) -> "ClientCommandAbstract":

    if client_config.use_local_requests:
        # This branch with `use_local_requests` is used only for testing
        # (to inspect internal server data via `ClientLocal` and `LocalServer`):
        from argrelay.test_infra.ClientLocal import ClientLocal
        abstract_client = ClientLocal(
            client_config,
        )
    else:
        # TODO: TODO_30_69_19_14: infinite spinner:
        #     There is a bug - if a child is used, it deadlocks occasionally while importing `requests`:
        #     https://github.com/argrelay/argrelay/issues/89
        #     The workaround is to abort (Ctrl+C) and retry - but this is annoying.
        # Attempt to detect hanging import by setting an alarm at least (not resolving it yet):
        signal.signal(signal.SIGALRM, _signal_handler)
        signal.alarm(1)
        from argrelay.relay_client.ClientRemote import ClientRemote
        signal.alarm(0)
        if has_error_happened:
            eprint("INFO: `import` passed")
        abstract_client = ClientRemote(
            client_config,
            proc_role,
            w_pipe_end,
            is_optimized_completion,
        )

    ElapsedTime.measure("before_client_invocation")
    command_obj = abstract_client.make_request(call_ctx)

    ElapsedTime.measure("on_exit")
    if shell_ctx.is_debug_enabled:
        ElapsedTime.print_all()
    return command_obj
