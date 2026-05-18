from argrelay_app_client.relay_client.__main__ import load_client_config
from argrelay_app_mcp_proxy.mcp_proxy.ArgrelayMcpProxy import ArgrelayMcpProxy
from argrelay_lib_root.misc_helper_common import get_config_path


def main():
    config_file_path = get_config_path("argrelay_client.json")
    client_config = load_client_config(config_file_path)
    mcp_proxy = ArgrelayMcpProxy(client_config)
    mcp_proxy.start()
    mcp_proxy.register_handlers()
    mcp_proxy.run()


if __name__ == "__main__":
    main()
