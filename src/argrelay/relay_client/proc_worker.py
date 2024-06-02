import signal

from argrelay.enum_desc.ServerAction import ServerAction
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
    shell_ctx
) -> "AbstractClientCommand":
    if client_config.use_local_requests:
        # This branch with `use_local_requests` is used only for testing
        # (to inspect internal server data via `LocalClient` and `LocalServer`):
        from argrelay.test_infra.LocalClient import LocalClient

        command_obj = make_request_via_abstract_client(
            LocalClient(client_config),
            call_ctx,
        )
    else:
        if (
            call_ctx.server_action is ServerAction.ProposeArgValues
            and
            client_config.optimize_completion_request
        ):
            from argrelay.client_command_remote.ProposeArgValuesRemoteOptimizedClientCommand import (
                ProposeArgValuesRemoteOptimizedClientCommand
            )
            command_obj = ProposeArgValuesRemoteOptimizedClientCommand(
                call_ctx = call_ctx,
                connection_config = client_config.connection_config,
            )
            make_request(
                command_obj,
            )
        else:
            # TODO: TODO_30_69_19_14: infinite spinner:
            #     There is a bug - if a child is used, it deadlocks occasionally while importing `requests`:
            #     https://github.com/argrelay/argrelay/issues/89
            #     The workaround is to abort (Ctrl+C) and retry - but this is annoying.
            # Attempt to detect hanging import by setting an alarm at least (not resolving it yet):
            signal.signal(signal.SIGALRM, _signal_handler)
            signal.alarm(1)
            from argrelay.relay_client.RemoteClient import RemoteClient
            signal.alarm(0)
            if has_error_happened:
                eprint("INFO: `import` passed")
            command_obj = make_request_via_abstract_client(
                RemoteClient(client_config),
                call_ctx,
            )
    ElapsedTime.measure("on_exit")
    if shell_ctx.is_debug_enabled:
        ElapsedTime.print_all()
    return command_obj


def make_request_via_abstract_client(
    abstract_client: "AbstractClient",
    call_ctx,
) -> "AbstractClientCommand":
    ElapsedTime.measure("before_client_invocation")
    return abstract_client.make_request(call_ctx)


def make_request(
    command_obj,
):
    command_obj.execute_command()
    ElapsedTime.measure("after_execute_command")
    return command_obj
