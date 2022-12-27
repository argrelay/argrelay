"""
Internal constants
"""

UNUSED_TITLE = "argrelay"
UNUSED_VERSION = "0.0.0"

DEFAULT_OPEN_API_VERSION = "3.0.2"

# server_op paths:
DESCRIBE_LINE_ARGS_PATH = "/describeLineArgs/"
PROPOSE_ARG_VALUES_PATH = "/proposeArgValues/"
RELAY_LINE_ARGS_PATH = "/relayLineArgs/"

# main:
DEFAULT_IP_ADDRESS = "localhost"
DEFAULT_PORT_NUMBER = 8787

API_SPEC = "/argrelay.relay_server.json"

# noinspection HttpUrlsUsage
BASE_URL_FORMAT = "http://{server_host_name}:{server_port_number}"
