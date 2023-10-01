# Keep minimal import on start:

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper import get_config_path
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig

ElapsedTime.measure("after_program_entry")


def main():
    # Initial imports - see `completion_perf_notes.md`.
    import sys
    ElapsedTime.measure("after_initial_imports")

    file_path = get_config_path("argrelay.client.json")
    client_config = load_client_config(file_path)
    ElapsedTime.measure("after_loading_client_config")

    shell_ctx = ShellContext.from_env(sys.argv)
    shell_ctx.print_debug()
    call_ctx = shell_ctx.create_call_context()

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
