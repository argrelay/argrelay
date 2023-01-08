# Keep minimal import on start for LocalClient:
# @formatter:off
from argrelay.misc_helper.ElapsedTime import ElapsedTime
ElapsedTime.measure("after_program_entry")
# @formatter:on


def main():
    import sys
    from argrelay.runtime_context.InputContext import InputContext
    from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc

    ElapsedTime.measure("after_initial_imports")

    client_config = client_config_desc.from_default_file()
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


def make_request(abstract_client, input_ctx) -> "AbstractClientCommand":
    ElapsedTime.measure("before_client_invocation")
    return abstract_client.make_request(input_ctx)


if __name__ == "__main__":
    main()
