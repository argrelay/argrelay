
These are some guidelines for the code style = list of excuses with justifications.

## Naming style

Names often go against what would sound "more English".
Instead, the preferred name strings serve sorting and searching properties
(especially across files with different syntax like *.py, *.bash, *.yaml, *.md, ...).

## Specific guidelines

*   Use at least two words for identifiers.

    For example, `server_action` (or `ServerAction`) instead of just `action` (or `Action`).

    This helps in refactoring and searching. Two words are less likely to have the same meaning
    across the same repo and will significantly narrow down the scope excluding unwanted search hits to review.

*   Prefer single file per class.

    Cons:
    *   This makes content appear bloated.
    *   It is also **not** how many other Python projects are structured.

    Nevertheless:
    *   It removes the need to decide how classes should be combined.
    *   It helps navigation.
    *   The content is not really bloated - there are more files but each has fewer lines.

*   Stick with flat module structure = only one sub-dir under package name.

    Until number of dirs in the list is excessively large, it is just simpler.

    There are ordering ambiguity with "sub-categories".
    Where should "one of the client response handlers" be placed?
    *   `./handler/response/`
    *   `./response/handler/`

    Yet, "sub-categories" can still be represented by a dir with extra suffix
    (to consistently survive renames and refactoring).
    *   `./handler_request/`
    *   `./handler_response/`

    This also embeds the ordering pattern to follow without hiding it in sub dirs.

*   Reorder words in identifiers if it helps dir grouping.

    For example,
    these two modules will appear grouped together
    (when sorted lexicographically in IDEs) due to common prefix:
    *   `client_command_local`
    *   `client_command_remote`

    Naming them "in English" will break the grouping
    as there is no common prefix anymore:
    *   `local_client_command`
    *   [something in between]
    *   `remote_client_command`

    After all, the three keywords (`local` | `remote`, `command`, `client`)
    are present in any of the naming style and
    there is no ambiguity in meaning.

    For another example, see hierarchy of plugins where ordering of keywords embedded in
    the names reflects inheritance which sorts list of classes in IDE as they all have common prefix.

*   Use new lines excessively - prefer "tall" code rather than "wide" one.

    For example, this:

    ```python
    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        self.server_config = server_config
        self.plugin_instance_id = plugin_instance_id
        self.plugin_config_dict = plugin_config_dict
    ```

    instead of this:

    ```python
    def __init__(self, server_config: ServerConfig, plugin_instance_id: str, plugin_config_dict: dict):
        self.server_config = server_config
        self.plugin_instance_id = plugin_instance_id
        self.plugin_config_dict = plugin_config_dict
    ```

    In this case of constructor args list,
    the first style (where each arg is on its own line):
    *   makes diff output cleaner for reviews
    *   preserves the history through `git blame` for more lines

