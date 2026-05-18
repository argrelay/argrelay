from argrelay_app_client.relay_client.__main__ import load_client_config
from argrelay_app_mcp_proxy.mcp_proxy.ArgrelayMcpProxy import ArgrelayMcpProxy
from argrelay_lib_root.misc_helper_common import get_config_path


def main():
    file_path = get_config_path("argrelay_client.json")
    client_config = load_client_config(file_path)
    proxy = ArgrelayMcpProxy(client_config)
    proxy.start()
    proxy.register_handlers()
    proxy.run()


if __name__ == "__main__":
    main()
