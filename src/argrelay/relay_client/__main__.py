# Keep minimal import on start:
import os
import sys
import time
from random import randrange

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import get_config_path, eprint
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig

ElapsedTime.measure("after_program_entry")


def main():
    ElapsedTime.measure("after_initial_imports")

    file_path = get_config_path("argrelay.client.json")
    client_config = load_client_config(file_path)
    ElapsedTime.measure("after_loading_client_config")

    shell_ctx = ShellContext.from_env(sys.argv)
    shell_ctx.print_debug()
    call_ctx = shell_ctx.create_call_context()

    if not is_requestor(
        client_config,
        shell_ctx,
    ):
        return

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
            from argrelay.relay_client.RemoteClient import RemoteClient
            command_obj = make_request_via_abstract_client(
                RemoteClient(client_config),
                call_ctx,
            )

    ElapsedTime.measure("on_exit")
    if shell_ctx.is_debug_enabled:
        ElapsedTime.print_all()

    return command_obj


def is_requestor(
    client_config: ClientConfig,
    shell_ctx: ShellContext,
) -> bool:
    """
    Implements FS_14_59_14_06 pending requests and forks a child proces for some requests.

    It returns true if the process is a requestor (the one who sends requests to the server).
    """

    if (
        client_config.show_pending_spinner
        and
        shell_ctx.comp_type is not CompType.InvokeAction
    ):
        # Create pipe for child to write results to its stdout:
        r_child_stdout, w_child_stdout = os.pipe()

        child_pid: int = os.fork()
        if child_pid == 0:
            os.close(r_child_stdout)
            # Child writes to the pipe (instead of the terminal):
            sys.stdout = os.fdopen(w_child_stdout, "w")
            # Child performs request:
            return True
        else:
            os.close(w_child_stdout)
            # Parent reads from the pipe to the child (later, when child has completed):
            child_stdout = os.fdopen(r_child_stdout)
            # Parent spins:
            spin_while_waiting(child_pid, child_stdout)
            return False


def generate_pending_cursor():
    # TODO: Use one and clean up the rest:
    cursor_states = [
        # f"{TermColor.spinner_state_0.value}┛{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}┗{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}┏{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}┓{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}▁{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▂{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▃{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▄{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▅{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▆{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▇{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}█{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▇{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▆{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▅{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▄{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▃{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▂{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▁{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}0{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}1{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}2{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}3{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}4{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}5{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}6{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}7{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}8{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}9{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}▖{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▘{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▝{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▗{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}<{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}={TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}>{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}={TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}{{{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}}}{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}[{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}]{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}\\{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}/{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",

        f"{TermColor.spinner_state_0.value}<{TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value}={TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value}>{TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
    ]
    # Use random start state:
    random_shift = randrange(len(cursor_states))
    shifted_states = cursor_states[random_shift:] + cursor_states[:random_shift]
    while True:
        for cursor_state in shifted_states:
            yield cursor_state


def spin_while_waiting(
    child_pid: int,
    child_stdout,
):
    """
    Display spinner while child request is running.
    """
    pending_cursor = generate_pending_cursor()
    while is_running(child_pid):
        eprint(next(pending_cursor), end = "", flush = True)
        time.sleep(0.1)
        eprint("\b", end = "", flush = True)

    # Clean up last spinner state char:
    eprint(" \b", end = "", flush = True)

    # Print everything what child has written:
    print(child_stdout.read())


def is_running(pid: int):
    (
        pid,
        status,
    ) = os.waitpid(pid, os.WNOHANG)
    if pid == 0 and status == 0:
        return True
    else:
        return False


def load_client_config(file_path):
    import json
    with open(file_path) as config_file:
        client_config_dict = json.load(config_file)
    client_config = client_config_dict_to_object(client_config_dict)
    return client_config


def client_config_dict_to_object(client_config_dict):
    """
    Optimized dict -> object conversion avoiding import of `*Schema` for performance:
    """
    client_config = ClientConfig(
        use_local_requests = client_config_dict.get("use_local_requests", False),
        optimize_completion_request = client_config_dict.get("optimize_completion_request", True),
        connection_config = ConnectionConfig(
            server_host_name = client_config_dict["connection_config"]["server_host_name"],
            server_port_number = client_config_dict["connection_config"]["server_port_number"],
        ),
        # TODO: Change to enabled by default:
        #       Keep disabled by default while in preview:
        show_pending_spinner = client_config_dict.get("show_pending_spinner", False)
    )
    return client_config


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


if __name__ == "__main__":
    main()
