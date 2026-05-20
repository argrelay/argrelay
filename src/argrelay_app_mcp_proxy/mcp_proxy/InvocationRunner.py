from __future__ import annotations

import json
import os
import sys
import traceback

from argrelay_lib_root.misc_helper_common import set_argrelay_dir


def main() -> None:
    argrelay_dir = os.environ.get("ARGRELAY_DIR")
    if argrelay_dir:
        set_argrelay_dir(argrelay_dir)
    try:
        relay_result = json.load(sys.stdin)
        from argrelay_api_server_cli.schema_response.InvocationInputSchema import (
            invocation_input_desc,
        )
        from argrelay_api_plugin_abstract.AbstractPlugin import import_plugin_class

        invocation_input = invocation_input_desc.dict_schema.load(relay_result)
        plugin_class = import_plugin_class(invocation_input.delegator_plugin_entry)
        exit_code = plugin_class.run_invoke_action(invocation_input)
        sys.exit(exit_code if exit_code is not None else 0)
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
