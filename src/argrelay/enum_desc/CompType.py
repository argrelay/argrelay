from enum import IntEnum


class CompType(IntEnum):
    """
    These enum items are codes set by Bash into `COMP_TYPE` env var on different completion actions.

    In principle, there are 3 behaviors of the client (rather than behaviors of Bash invoking it):
    *   `PrefixShown` == `PrefixHidden` == `MenuCompletion`:
        provide all values suitable for the given command line and cursor position.
    *   `SubsequentHelp`:
        possibly provide more values.
    *   `DescribeArgs`:
        print how each arg is parsed from given command line and cursor position.

    These code given by Bash depends on (1) completion action by user and (2) Readline config.

    See Bash docs on `COMP_TYPE` env var:
    https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html

    This part of `~/.inputrc` configures Tab to do `complete` and Shift-Tab to do `menu-complete` completion actions:
    ```
    "\t": complete
    "\e[Z": menu-complete
    ```

    Other recommended settings for Readline:
    ```
    set show-all-if-ambiguous on
    set show-all-if-unmodified on
    set skip-completed-text on
    ```

    See Readline docs for details on `~/.inputrc` config:
    https://www.gnu.org/software/bash/manual/html_node/Readline-Init-File-Syntax.html
    """

    """
    This happens on first `complete` only when `set show-all-if-ambiguous on`.
    Subsequent `complete` results in `SubsequentHelp`.
    """
    PrefixShown = 33  # ASCII '!'

    """
    This happens on first `complete` only when `set show-all-if-ambiguous off`.
    In that case, it appears to work exactly like `PrefixShown`
    except Bash hides suggested values from user if these values are ambiguous
    (more than one value matching tangent token left part).
    """
    PrefixHidden = 9  # ASCII '\t'

    """
    This happens on subsequent `complete` actions (after the first `PrefixShown` or `PrefixHidden`).
    It is normally used as an opportunity for the client to suggest more values for completion.
    """
    SubsequentHelp = 63  # ASCII '?'

    """
    This happens on `menu-complete` - for example, on Shift-Tab given the `~/.inputrc` config above.
    Subsequent Shift-Tab-s do not invoke client - instead, Bash uses cashed suggestions and cycles through them.
    """
    # TODO: Test if it is feasible to cycle through options limited by current prefix (versus cycling through every item at current arg space).
    MenuCompletion = 37  # ASCII '%'

    """
    This `COMP_TYPE` value does not originate in Bash completion.
    Instead, it is set by `argrelay` Bash config script when invoked via special key combination (e.g. `ALT+SHIFT+Q`).
    It is used to describe args in the given command line.
    """
    DescribeArgs = 94  # ASCII '^'

    """
    This `COMP_TYPE` value does not originate in Bash completion.
    Instead, it is set by `argrelay` client for `CallConv.CliArgsConv`.
    """
    InvokeAction = 42  # ASCII '*'
