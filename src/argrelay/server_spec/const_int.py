"""
Internal constants
"""

# See `server_title` and `server_version` instead.
UNUSED_TITLE = "argrelay"
UNUSED_VERSION = "0.0.0"

# This will make `apispec` generate schema compatible with `flasgger` (placing schemas under `#/definitions/`):
DEFAULT_OPEN_API_VERSION = "2.0"

# server_op paths:
DESCRIBE_LINE_ARGS_PATH = "/describe_line_args/"
PROPOSE_ARG_VALUES_PATH = "/propose_arg_values/"
RELAY_LINE_ARGS_PATH = "/relay_line_args/"

# Built-in GUI:
ARGRELAY_GUI_PATH = "/argrelay_gui/"

# Run API docs UI at the root:
API_DOCS_PATH = "/argrelay_api/"

# main:
DEFAULT_IP_ADDRESS = "localhost"
DEFAULT_PORT_NUMBER = 8787

API_SPEC_PATH = "/argrelay_server_api_spec.json"

# noinspection HttpUrlsUsage
BASE_URL_FORMAT = "http://{server_host_name}:{server_port_number}"

