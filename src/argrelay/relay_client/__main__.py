# Keep minimal import on start:
from argrelay.misc_helper import get_config_path
from argrelay.misc_helper.ElapsedTime import ElapsedTime

ElapsedTime.measure("after_program_entry")


def main():
    # Initial imports - see `completion_perf_notes.md`.
    import os
    import sys
    from argrelay.runtime_context.InputContext import InputContext
    ElapsedTime.measure("after_initial_imports")

    file_path = get_config_path("argrelay.client.json")
    client_config = load_client_config(file_path)
    ElapsedTime.measure("after_loading_client_config")

    input_ctx = InputContext.from_env(sys.argv)

    if client_config.use_local_requests:
        from argrelay.relay_client.LocalClient import LocalClient

        command_obj = make_request(LocalClient(client_config), input_ctx)
    else:
        from argrelay.relay_client.RemoteClient import RemoteClient

        command_obj = make_request(RemoteClient(client_config), input_ctx)

    ElapsedTime.measure("on_exit")
    if input_ctx.is_debug_enabled:
        ElapsedTime.print_all()

    return command_obj


def load_client_config(file_path):
    import json
    with open(file_path) as config_file:
        client_config_dict = json.load(config_file)
    client_config = client_config_dict_to_object(client_config_dict)
    return client_config


def client_config_dict_to_object(client_config_dict):
    from argrelay.runtime_data.ClientConfig import ClientConfig
    from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
    client_config = ClientConfig(
        # Not importing constants like `use_local_requests_` from *Schema for performance:
        use_local_requests = client_config_dict["use_local_requests"],
        connection_config = ConnectionConfig(
            server_host_name = client_config_dict["connection_config"]["server_host_name"],
            server_port_number = client_config_dict["connection_config"]["server_port_number"],
        ),
    )
    return client_config


def make_request(abstract_client, input_ctx) -> "AbstractClientCommand":
    ElapsedTime.measure("before_client_invocation")
    return abstract_client.make_request(input_ctx)


if __name__ == "__main__":
    main()
