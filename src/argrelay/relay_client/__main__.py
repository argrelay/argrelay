# Keep minimal import on start:
import sys

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common import get_config_path
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client.client_utils import handle_main_exception
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.server_spec.CallContext import CallContext

ElapsedTime.measure("after_program_entry")


def main():
    # noinspection PyBroadException
    try:
        return prepare_and_run_client()
    except BaseException as e1:
        handle_main_exception(e1)


def prepare_and_run_client():
    ElapsedTime.measure("after_initial_imports")

    file_path = get_config_path("argrelay_client.json")
    client_config = load_client_config(file_path)
    ElapsedTime.measure("after_loading_client_config")

    shell_ctx = ShellContext.from_env(sys.argv)
    shell_ctx.print_debug()

    call_ctx = shell_ctx.create_call_context()

    return run_client(
        client_config,
        call_ctx,
    )


def run_client(
    client_config: ClientConfig,
    call_ctx: CallContext,
):
    is_split_mode: bool = (
        # FS_14_59_14_06 pending requests: at the moment the process is split only to provide spinner:
        client_config.show_pending_spinner
        and
        call_ctx.server_action is not ServerAction.RelayLineArgs
    )

    is_optimized_completion = (
        call_ctx.server_action is ServerAction.ProposeArgValues
        and
        client_config.optimize_completion_request
    )

    w_pipe_end = None
    if is_split_mode:
        # TODO: TODO_30_69_19_14: infinite spinner
        #       Perform `import encodings.idna` explicitly ahead of fork.
        #       Similar to this:
        #       https://github.com/psf/requests/commit/d7227fbb7e07af35f23a0d370ab3b01661af9e40#commitcomment-146935826
        # noinspection PyUnresolvedReferences
        import encodings.idna

        from argrelay.relay_client.proc_splitter import split_process
        (
            is_parent,
            child_pid,
            r_pipe_end,
            w_pipe_end,
        ) = split_process()

        if is_parent:
            proc_role: ProcRole = ProcRole.ParentProcSpinner
            from argrelay.relay_client.proc_spinner import spinner_main
            spinner_main(
                call_ctx,
                client_config,
                proc_role,
                is_optimized_completion,
                r_pipe_end,
            )
            return None
        else:
            proc_role: ProcRole = ProcRole.ChildProcWorker
    else:
        proc_role: ProcRole = ProcRole.SoleProcWorker

    from argrelay.relay_client.proc_worker import worker_main
    command_obj = worker_main(
        call_ctx,
        client_config,
        proc_role,
        is_optimized_completion,
        w_pipe_end,
        -1,
    )
    return command_obj


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
    redundant_servers: list[ConnectionConfig] = []
    for redundant_server in client_config_dict["redundant_servers"]:
        redundant_servers.append(ConnectionConfig(
            server_host_name = redundant_server["server_host_name"],
            server_port_number = redundant_server["server_port_number"],
        ))
    client_config = ClientConfig(
        __comment__ = client_config_dict.get("use_local_requests", None),
        use_local_requests = client_config_dict.get("use_local_requests", False),
        optimize_completion_request = client_config_dict.get("optimize_completion_request", True),
        redundant_servers = redundant_servers,
        show_pending_spinner = client_config_dict.get("show_pending_spinner", True),
        spinless_sleep_sec = client_config_dict.get("spinless_sleep_sec", 0.0),
    )
    return client_config


if __name__ == "__main__":
    main()
