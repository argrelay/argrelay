"""
Internal constants
"""

# See `server_title` and `server_version` instead.
UNUSED_TITLE = "argrelay"
UNUSED_VERSION = "0.0.0"

# This will make `apispec` generate schema compatible with `flasgger` (placing schemas under `#/definitions/`):
DEFAULT_OPEN_API_VERSION = "2.0"

# Built-in GUI:
ARGRELAY_GUI_PATH = "/argrelay_gui/"

# Run API docs GUI at the root:
API_DOCS_PATH = "/argrelay_api/"

# main:
DEFAULT_IP_ADDRESS = "localhost"
DEFAULT_PORT_NUMBER = 8787

API_SPEC_PATH = "/argrelay_server_api_spec.json"

# noinspection HttpUrlsUsage
BASE_URL_FORMAT = "http://{server_host_name}:{server_port_number}"
