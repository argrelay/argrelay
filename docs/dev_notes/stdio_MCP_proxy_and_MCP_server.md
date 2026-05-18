# stdio MCP proxy and MCP server extension -- design spec

## 1. Overview

Expose argrelay commands as MCP (Model Context Protocol) tools so AI clients
(Claude, Claude Code, etc.) can discover and invoke argrelay functions with
typed, named arguments.

Architecture:

```
[AI client / Claude]
        |
      stdio (MCP JSON-RPC 2.0)
        |
[argrelay_mcp_proxy]  <-- new lightweight process (short-lived, per MCP session)
        |
      HTTP REST
        |
      GET /mcp_tools/        <-- new server endpoint (function discovery)
      POST /relay_line_args/ <-- existing endpoint (tool invocation)
        |
[argrelay Flask server]  <-- extended with one new route
```

Two deliverables:

1.  New server endpoint `GET /mcp_tools/` -- returns all registered argrelay
    functions as MCP tool descriptors (arg names, help hints, command paths).
    No enum value queries at startup (see Section 3 for why).

2.  `argrelay_app_mcp_proxy` -- short-lived stdio MCP process that:
    -   On session start: calls `GET /mcp_tools/` once, holds result in memory.
    -   Serves `tools/list` from memory.
    -   On `tools/call`: builds command line, calls `POST /relay_line_args/`,
        returns `custom_plugin_data` + any `remaining` arg values to AI.

---

## 2. Background: existing argrelay architecture

### 2.1 Three existing server endpoints

All accept `CallContext` JSON body
(`src/argrelay_api_server_cli/schema_request/CallContextSchema.py`).

| Endpoint | HTTP | Purpose |
|---|---|---|
| `POST /propose_arg_values/` | POST | Tab-completion: returns `arg_values: list[str]` |
| `POST /describe_line_args/` | POST | Parsed state: returns `InterpResult` with remaining values |
| `POST /relay_line_args/`    | POST | Execute: returns `InvocationInput` with `custom_plugin_data` |

URL prefix defined in `src/argrelay_lib_root/enum_desc/ServerAction.py`.
Routes wired in `src/argrelay_app_server/relay_server/route_api.py`.

### 2.2 How functions are registered

Each argrelay function is a document in the `class_function` MongoDB collection.
Every function document contains:

-   `tree_step_0 .. tree_step_N` -- command path tokens; unused steps are `"~"`
-   `help_hint` -- human-readable description
-   `instance_data.func_id` -- unique function identifier
-   `instance_data.search_control_list` -- list of `SearchControl` dicts; each
    defines a MongoDB collection to search and its `arg_name_to_prop_name_map`

Example function document (abbreviated):

```json
{
  "envelope_class": "class_function",
  "func_id": "func_id_goto_service",
  "help_hint": "Go (log in) to remote host and dir path with specified service",
  "tree_step_0": "relay_demo",
  "tree_step_1": "goto",
  "tree_step_2": "service",
  "tree_step_3": "~",
  "instance_data": {
    "func_id": "func_id_goto_service",
    "search_control_list": [
      {
        "collection_name": "class_service",
        "props_to_values_dict": {"envelope_class": "class_service"},
        "arg_name_to_prop_name_map": [
          {"class":    "envelope_class"},
          {"code":     "code_maturity"},
          {"stage":    "flow_stage"},
          {"region":   "geo_region"},
          {"service":  "service_name"}
        ]
      }
    ]
  }
}
```

### 2.3 Argument model -- order-independent tokens

argrelay arguments are positional tokens that act as order-independent filters.
Providing `{code: prod, region: apac}` maps to appending those values to the
command path (order does not matter to argrelay):

```
relay_demo goto service prod apac  ==  relay_demo goto service apac prod
```

This order-independence is what lets MCP named parameters map cleanly to
argrelay tokens: append each provided value to the command-path prefix.

---

## 3. New server endpoint: GET /mcp_tools/

### 3.1 Why a new endpoint (not reusing existing 3)

The existing 3 endpoints accept `CallContext` (a command-line string). To get
function descriptors from them requires:

-   Calling `relay_line_args` with `"relay_demo help"` -> parse response
-   Calling `describe_line_args` per function to get per-arg value sets

This is N+1 HTTP roundtrips from proxy to server. Moving the logic server-side
eliminates all roundtrips: one `GET /mcp_tools/` call returns everything the
proxy needs.

The new endpoint is a 4th Flask route (`route_mcp.py` blueprint), outside the
`ServerAction` enum framework. It does not require a `CallContext` request body.

### 3.2 Server logic for GET /mcp_tools/

```python
# step 1: one query -- all registered functions
func_envelopes = db["class_function"].find(
    {"envelope_class": "class_function"}
)

# step 2: for each function, extract all fields needed for MCP tool descriptor
for envelope in func_envelopes:
    # tool name: strip "func_id_" prefix from func_id
    func_id = envelope["instance_data"]["func_id"]
    tool_name = func_id[len("func_id_"):] if func_id.startswith("func_id_") else func_id
    # tool_name -> "goto_service"

    # description from help_hint field on the envelope
    description = envelope.get("help_hint", func_id)
    # description -> "Go (log in) to remote host and dir path with specified service"

    # command path: tree_step_* values, excluding wildcard "~"
    step_keys = sorted(k for k in envelope if k.startswith("tree_step_"))
    command_path = [envelope[k] for k in step_keys if envelope[k] != "~"]
    # command_path -> ["relay_demo", "goto", "service"]

    # arg names and their prop names (for remaining remapping)
    arg_names = []
    prop_name_for_arg = {}
    for sc in envelope["instance_data"]["search_control_list"]:
        for mapping in sc["arg_name_to_prop_name_map"]:
            for arg_name, prop_name in mapping.items():
                if arg_name != "class":
                    arg_names.append(arg_name)
                    prop_name_for_arg[arg_name] = prop_name
    # arg_names          -> ["code", "stage", "region", "service"]
    # prop_name_for_arg  -> {"code": "code_maturity", "stage": "flow_stage", ...}
```

### 3.3 Why no enum value queries at startup

Enum values could be fetched with `collection.distinct(prop_name, filter)` per
arg -- one `distinct` call per arg per function (N functions x M args each).
This gives independent per-dimension value sets: `{M1}`, `{M2}`, `{M3}` -- not
their Cartesian product (which is never needed and never computed).

However, this is skipped intentionally for the short-lived proxy:

-   Enum values are a snapshot at session start -- stale if DB changes.
-   Not needed for correct invocation -- AI passes free-text values.
-   Argrelay returns `remaining_prop_name_to_prop_value` on error/ambiguity,
    giving the AI live enum values at call time (see Section 5).
-   Keeping `GET /mcp_tools/` as a single `class_function` query keeps it fast
    and simple.

### 3.4 Response format

```json
{
  "tools": [
    {
      "name": "goto_service",
      "description": "Go (log in) to remote host and dir path with specified service",
      "command_path": ["relay_demo", "goto", "service"],
      "inputSchema": {
        "type": "object",
        "properties": {
          "code":    {"type": "string", "description": "code_maturity"},
          "stage":   {"type": "string", "description": "flow_stage"},
          "region":  {"type": "string", "description": "geo_region"},
          "service": {"type": "string", "description": "service_name"}
        }
      }
    }
  ]
}
```

All parameters optional (argrelay filters by whatever is provided; omitted
dimensions are left unfiltered).

`tool.name` = `func_id` with `func_id_` prefix stripped (e.g.
`func_id_goto_service` -> `goto_service`). Names are globally unique within
argrelay, so no collision possible.

### 3.5 Key source files for server extension

| File | Role |
|---|---|
| `src/argrelay_app_server/relay_server/route_api.py` | Existing 3 routes -- pattern to follow |
| `src/argrelay_app_server/relay_server/LocalServer.py` | Holds DB access, plugin registry |
| `src/argrelay_app_server/relay_server/CustomFlaskApp.py` | Blueprint registration |
| `src/argrelay_api_server_cli/server_spec/const_int.py` | URL path constants |

New files:

| File | Role |
|---|---|
| `src/argrelay_app_server/relay_server/route_mcp.py` | New Flask blueprint for MCP routes |
| `src/argrelay_app_server/handler_request/MCPToolsServerRequestHandler.py` | Handler that queries class_function |

---

## 4. MCP proxy: argrelay_app_mcp_proxy

### 4.1 Process lifetime (short-lived)

The proxy is a stdio subprocess spawned by the MCP client (Claude Code, Claude
Desktop, etc.) when it starts a session. It serves that session and exits when
the client closes it. This is the standard MCP stdio transport pattern.

No persistent daemon. No reconnection logic. No cross-session state.

Contrast with a "long-standing" proxy that would cache function discovery across
sessions or run as a background service.

### 4.2 Startup sequence

```
1. proxy starts (spawned by AI client via stdio)
2. GET /mcp_tools/ -> parse tool list, hold in memory
3. ready to serve MCP protocol
```

Single HTTP call at startup. No per-function queries.

### 4.3 Tool invocation flow

```
AI: tools/call  goto_service  {code: "prod", region: "apac"}
    |
proxy: command_path = ["relay_demo", "goto", "service"]
       tokens = command_path + [v for v in args.values() if v]
       command_line = "relay_demo goto service prod apac"
    |
proxy: POST /relay_line_args/
       body: CallContext(
           server_action = RelayLineArgs,
           command_line  = "relay_demo goto service prod apac",
           cursor_cpos   = len(command_line),
           comp_scope    = ScopeInitial,
           ...
       )
    |
server: returns InvocationInput (custom_plugin_data + envelope_containers)
    |
proxy: extract custom_plugin_data
       extract remaining_prop_name_to_prop_value from envelope_containers
       return both to AI as MCP TextContent
```

### 4.4 Package layout

```
src/argrelay_app_mcp_proxy/
+-- __init__.py
+-- mcp_proxy/
    +-- __init__.py
    +-- __main__.py           # entry point: load config, run proxy
    +-- ArgrelayMcpProxy.py  # core: session init, MCP handler callbacks
    +-- ToolBuilder.py        # pure functions: parse /mcp_tools/ response,
                              #   build MCP tool objects, build command lines
```

### 4.5 Executable generation

Bootstrap (`src/argrelay_app_bootstrap/cmd_bootstrap_env.py`) generates
`exe/argrelay_mcp_proxy` via `_generate_runner_script()` -- same pattern as
`exe/run_argrelay_client` and `exe/run_argrelay_server`.

Generated file (not version-controlled, differs per environment):

```python
#!/path/to/venv/bin/python
import os
from argrelay_lib_root import misc_helper_common
misc_helper_common.set_argrelay_dir(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from argrelay_app_mcp_proxy.mcp_proxy.__main__ import main
if __name__ == '__main__':
    main()
```

Server connection read from `@/conf/argrelay_client.json` (same config as
`exe/run_argrelay_client`), resolved via `set_argrelay_dir` set by the shebang.

### 4.6 MCP library dependency

Use the official `mcp` Python package. Provides:

-   `mcp.server.Server` -- MCP server implementation
-   `mcp.server.stdio.stdio_server()` -- stdio transport (async context manager)
-   `mcp.types.Tool`, `mcp.types.TextContent` -- type definitions

Add `mcp>=1.0` to `pyproject.toml` dependencies. Do NOT add `anyio` separately --
`mcp>=1.0` already depends on `anyio`; a duplicate explicit pin risks version conflicts.

The proxy does NOT need to implement JSON-RPC 2.0 framing manually.

### 4.7 Integration with Claude Code / Claude Desktop

`.mcp.json` in project root:

```json
{
  "mcpServers": {
    "argrelay": {
      "command": "/abs/path/to/argrelay.git/exe/argrelay_mcp_proxy"
    }
  }
}
```

The absolute path carries the venv Python shebang, so no venv activation needed.

`.mcp.json` contains an environment-specific absolute path and must be added to
`.gitignore` -- it is local-only, analogous to `exe/argrelay_mcp_proxy` itself.

---

## 5. Error feedback loop (replaces upfront enum enumeration)

Two distinct error cases arise from `relay_line_args`. The proxy surfaces both
`custom_plugin_data` and the `remaining` dict to the AI in both cases.

### 5.1 More than one match (ambiguity)

Too few arg values provided -- multiple data envelopes match. Argrelay returns
a non-zero `error_code` and `remaining_prop_name_to_prop_value` is non-empty
(lists the values that would narrow the search):

```json
{
  "custom_plugin_data": {
    "error_message": "ERROR: more than one match",
    "error_code": 1
  },
  "remaining": {
    "code":   ["dev", "prod", "qa"],
    "region": ["amer", "apac", "emea"]
  }
}
```

AI action: pick a value from `remaining`, retry. Live enum set at call time --
always current, never a stale startup snapshot.

### 5.2 Zero matches

Arg values provided do not match any data envelope (typo, invalid value, or
impossible combination). Argrelay returns a non-zero `error_code` and
`remaining_prop_name_to_prop_value` is empty (nothing to pick from):

```json
{
  "custom_plugin_data": {
    "error_message": "ERROR: zero matches",
    "error_code": 1
  },
  "remaining": {}
}
```

AI action: cannot self-correct from `remaining` -- must ask the user to clarify
the intended value. The proxy should signal this case explicitly in its response
so the AI does not retry blindly with the same (invalid) values.

### 5.3 Collection of remaining values

The proxy collects `remaining_prop_name_to_prop_value` from
`envelope_containers[1:]` only -- `envelope_containers[0]` is the function
container (`class_function` match) and does not hold param remaining values.
All param containers (`[1:]`) are merged into a single flat dict.

The proxy maps `prop_name` keys back to `arg_name` keys using
`inputSchema.properties[arg_name].description` (inverted) from the tool
descriptor so the AI sees the same names it used in the original call.

---

## 6. Step-by-step implementation plan

### Phase 1: Server extension (GET /mcp_tools/)

1.  Create `src/argrelay_app_server/handler_request/MCPToolsServerRequestHandler.py`:
    -   Constructor takes `LocalServer`.
    -   `handle_request()`: queries `class_function`, builds tool descriptor list,
        returns dict matching Section 3.4 format.
    -   Pure logic: no Flask imports, testable in isolation.

2.  Create `src/argrelay_app_server/relay_server/route_mcp.py`:
    -   `create_blueprint_mcp(local_server)` -> Flask `Blueprint`.
    -   `GET /mcp_tools/` route calls `MCPToolsServerRequestHandler.handle_request()`.
    -   Returns JSON response.

3.  Register blueprint in `CustomFlaskApp.py` (same pattern as `route_api.py`).

4.  Add URL constant to `src/argrelay_api_server_cli/server_spec/const_int.py`:
    `MCP_TOOLS_PATH = "/mcp_tools/"`.

5.  Verify with `curl http://localhost:8787/mcp_tools/`.

### Phase 2: ToolBuilder (pure functions, no network)

Create `src/argrelay_app_mcp_proxy/mcp_proxy/ToolBuilder.py`:

-   `ToolDesc` dataclass: `name`, `description`, `command_path`, `arg_names`,
    `prop_name_for_arg` (maps arg_name -> prop_name for remaining remapping).
-   `parse_mcp_tools_response(response_dict) -> list[ToolDesc]`
-   `build_command_line(tool: ToolDesc, args: dict) -> str`
-   `extract_remaining(invocation_input: dict, tool: ToolDesc) -> dict`
    Maps `prop_name` -> `arg_name` in `remaining_prop_name_to_prop_value`.
-   `build_mcp_tool(tool: ToolDesc) -> mcp.types.Tool`

### Phase 3: Proxy core

Create `src/argrelay_app_mcp_proxy/mcp_proxy/ArgrelayMcpProxy.py`:

-   `__init__(client_config, server_url)`: init `requests.Session`, MCP `Server`.
-   `start()`: `GET /mcp_tools/` -> `parse_mcp_tools_response` -> store tool list.
-   `register_tools()`: register `list_tools` and `call_tool` callbacks on MCP server.
-   `_call_tool(name, arguments)`: `build_command_line` -> `POST /relay_line_args/`
    -> extract result + remaining -> return `TextContent`.
-   `run_stdio()`: `async with stdio_server()` -> `mcp_server.run(...)`.

Create `src/argrelay_app_mcp_proxy/mcp_proxy/__main__.py`:

-   Load `argrelay_client.json` via `get_config_path`.
-   Parse `--server-url` override (optional; default from config).
-   Instantiate `ArgrelayMcpProxy`, call `start()`, `register_tools()`, `run_stdio()`.

### Phase 4: Bootstrap integration

Extend `src/argrelay_app_bootstrap/cmd_bootstrap_env.py`:

-   Add `_generate_runner_script(path=".../exe/argrelay_mcp_proxy", ...)` call.

### Phase 5: End-to-end test

1.  Start argrelay server (`exe/run_argrelay_server`).
2.  `curl http://localhost:8787/mcp_tools/` -- verify function list.
3.  Run proxy, send MCP `tools/list` via stdin -- verify tool names match.
4.  Send MCP `tools/call goto_service {code: prod, region: apac}` -- verify
    `custom_plugin_data` in response.
5.  Send with wrong value -- verify `remaining` in response with correct enum values.
6.  Configure `.mcp.json`, restart Claude Code, verify argrelay tools available.

---

## 7. Files to create / modify

### New files

```
src/argrelay_app_server/relay_server/route_mcp.py
src/argrelay_app_server/handler_request/MCPToolsServerRequestHandler.py
src/argrelay_app_mcp_proxy/__init__.py
src/argrelay_app_mcp_proxy/mcp_proxy/__init__.py
src/argrelay_app_mcp_proxy/mcp_proxy/__main__.py
src/argrelay_app_mcp_proxy/mcp_proxy/ArgrelayMcpProxy.py
src/argrelay_app_mcp_proxy/mcp_proxy/ToolBuilder.py
```

### Modified files

```
src/argrelay_app_server/relay_server/CustomFlaskApp.py  -- register route_mcp blueprint
src/argrelay_api_server_cli/server_spec/const_int.py    -- add MCP_TOOLS_PATH constant
src/argrelay_app_bootstrap/cmd_bootstrap_env.py         -- generate exe/argrelay_mcp_proxy
pyproject.toml                                          -- add mcp>=1.0, mcp dep
```

### Generated file (not version-controlled)

```
exe/argrelay_mcp_proxy   -- produced by bootstrap, differs per environment
```

---

## 8. Open questions

Q1 -- `command_path` in response: should `GET /mcp_tools/` include `command_path`
in its response (needed by proxy for command line construction), or should the
proxy reconstruct it from `tree_step_*` fields?
Decision: include `command_path` as a pre-computed field in the response.

Q2 -- RESOLVED by Section 3.4: `prop_name_for_arg` map is already present in
the response -- `inputSchema.properties[arg_name].description` IS the `prop_name`
(e.g. `"code": {"description": "code_maturity"}`). Proxy inverts that to remap
`remaining` keys: `prop_name_for_arg = {prop.description: arg for arg, prop in
properties.items()}`. No separate field needed.

Q3 -- Auth / access control: `GET /mcp_tools/` is unauthenticated (same as
existing 3 endpoints). Acceptable for local deployment.

Q4 -- Tool name collision: `func_id_` prefix strip is safe only if stripped names
are unique. argrelay enforces unique `func_id`, so stripped names are unique too.
No deduplication logic needed.

Q5 -- `.mcp.json` location: project root vs user home. Project root is preferred
for Claude Code (per-project config). Document both options.
