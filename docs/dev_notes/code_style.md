
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

*   Use `reversed_naming_order` to group relevant components in lists via sorting.

    See [`reversed_naming_order.md`][reversed_naming_order.md].

*   Prefer single file per class.

    Cons:
    *   This makes content appear bloated.
    *   It is also **not** how many other Python projects are structured.

    Nevertheless:
    *   It removes the need to decide how classes should be combined.
    *   It helps navigation.
    *   The content is not really bloated - there are more files but each has fewer lines.

*   Flatten module structure = only one sub-dir under package name.

    TODO: TODO_78_94_31_68: split argrelay into multiple packages
          Due to ongoing package-splitting activity, the flatness (or depth) of the nesting
          is rather arbitrary:
          *   simpler top-level modules have 0-level nesting
          *   more complex top-level modules may have N-level nesting

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

[reversed_naming_order.md]: reversed_naming_order.md
