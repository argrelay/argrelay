import json

from argrelay_app_client.relay_client.__main__ import load_client_config
from argrelay_app_mcp_proxy.mcp_proxy.ArgrelayMcpProxy import ArgrelayMcpProxy
from argrelay_app_mcp_proxy.mcp_proxy.McpProxyConfig import McpProxyConfig
from argrelay_app_mcp_proxy.mcp_proxy.McpProxyConfigSchema import mcp_proxy_config_desc
from argrelay_lib_root.misc_helper_common import get_config_path


def load_mcp_proxy_config(file_path: str) -> McpProxyConfig:
    with open(file_path) as f:
        config_dict = json.load(f)
    return mcp_proxy_config_desc.dict_schema.load(config_dict)


def main():
    client_config_path = get_config_path("argrelay_client.json")
    client_config = load_client_config(client_config_path)

    mcp_proxy_config_path = get_config_path("argrelay_mcp_proxy.json")
    mcp_proxy_config = load_mcp_proxy_config(mcp_proxy_config_path)

    mcp_proxy = ArgrelayMcpProxy(client_config, mcp_proxy_config)
    mcp_proxy.start()
    mcp_proxy.register_handlers()
    mcp_proxy.run()


if __name__ == "__main__":
    main()
