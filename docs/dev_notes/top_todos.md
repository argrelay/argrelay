
TODO: top todos

Tags:
*   FINALIZE: The feature already works but needs coverage, small non-functional improvements, documentation.
*   CLOSED: The issue is done or being tracked otherwise = no need to keep this todo, but still kept to keep in the view.
*   REGISTER: The item is not yet registered, requires new feature story (FS) entry.
*   USER_VISIBLE: Something what is visible to user (rather than just making things better).
*   DEV_VISIBLE: Something what is visible to dev (may not be visible for users as USER_VISIBLE, but helps dev).

Top:

To demo:

*   Add color for envelope class in desc output - green if found 1, yellow if not yet (still N), gray if 0.
    See also: FS_80_45_89_81 / list_envelope
    FINALIZE
*   If command accept one envelope, but not yet disambiguated, then it should be possible to provide generic hook to list envelopes based on existing filter.
    Basically, if 1, invoke target function, if N, invoke list, print error to stderr, exit with non 0.
    See also: FS_80_45_89_81 / list_envelope
    REGISTER

*   Clean `#`-comments from command line arguments by parser.
    Tracked via FS_92_75_93_01.clean_command_line.md
    CLOSED

*   Consumed and unconsumed tokens:
    *   Send them to invocation (e.g. to decide to run or not to run function and how they can be used).
    *   Verify them in tests.
    FINALIZE

*   In describe, show other arg value options when default value is applied.
    Tracked via FS_72_53_55_13.show_non_default_options.md
    CLOSED


*   Meta function: list all objects of specified query.
    See also: FS_80_45_89_81 / list_envelope
    REGISTER

*   Meta function: get and set objects (via corresponding API).
    Tracked via: FS_74_69_61_79 / get_envelope and set_envelope: https://github.com/argrelay/argrelay/issues/20
    CLOSED

*   If there are multiple `data_envelope` anywhere in `query_plan` (as last `data_envelope` or not),
    it should be possible to hit enter and provide some meaningful action for the list of
    these currently found `data_envelope`-s of the same single class
    (even if function needs envelopes of subsequent classes).
    REGISTER

*   Add named args.
    Tracked via FS_20_88_05_60 and TODO: add issue on GH linked to FS.
    CLOSED

*   Dilemma: if function expects N envelopes, there is no way to detect no args option because no args option lists all max N envelopes.
    Maybe there should be a way to indicate it for client side (that the last envelope search had no criteria to search)?
    REGISTER

*   Print best-effort stable command line at invocation to share (strict mode, no room for mis-interpretation).
    This should ensure any dynamic values are translated into more fully-qualified ones.
    See: https://github.com/argrelay/argrelay/issues/22
    CLOSED

Integration:

*   Review all locations where `.argrelay.conf.d` is mentioned - it is likely that `@/conf` has to be used there instead.
    FINALIZE

*   Add tests that config loading respects `ARGRELAY_CONF_BASE_DIR`, `~/.argrelay.conf.d`, or `@/conf`.
    See FS_16_07_78_84.conf_dir_priority.md.
    FINALIZE

*   FS_61_67_08_53: arbitrary text args.
    Tracked via FS_61_67_08_53 and https://github.com/argrelay/argrelay/issues/46
    CLOSED

*   Live status / live updates.
    Design support for online data updates.
    It should be an API to {get, set} envelope.
    Tracked via issue: https://github.com/argrelay/argrelay/issues/20Live
    CLOSED

*   Search via different collections
    Query specific Mongo DB collection.
    Tracked via FS_56_43_05_79: https://github.com/argrelay/argrelay/issues/10
    CLOSED

GUI bits:

*   Make input element classes as states:
    *   client_server_synced
    *   pending_request
    *   pending_response
    Test transition:
    *   pending_response -> on_eq -> client_server_synced
    *   pending_response -> on_response -> client_server_synced
    REGISTER

*   Add info descriptions (tooltip or question mark with description).
    REGISTER

*   When there is no common prefix, Tab should not work, flash command line with red color.
    REGISTER

*   When there is no common prefix, Tab should not work (do not replace current token).
    REGISTER

*   Be able to enable verbose server logging and disable it via GUI.
    REGISTER

*   Add info in GUI that describe output is accessible in shell via Alt+Shift+Q.
    REGISTER

*   Test with lots of data - is there any issues with races between user input and server response?
    FINALIZE

*   Handle `help` response differently in GUI - print help.
    REGISTER

*   When request is running suggestion should be empty or indicate they are invalid.
    Tab should only work when no request is running.
    FINALIZE

*   Request should start when no request running and there is a change in input.
    FINALIZE

*   Make command history a list (not drop down). Make it scrollable beyond 20 commands.
    REGISTER

*   Do not render query results if the command line is changed again on the result arrival.
    FINALIZE

*   Can we cancel request if new request has to be made and old one is invalid (e.g. caret has moved)?
    See also: https://stackoverflow.com/a/47250621/441652
    FINALIZE

*   Add `describe` (or `itemize`) internal command to do exactly the same what Ctrl+Alt+Q does, but via Invocation.
    Rename "describe" to "search" (outline) and implement function which does what Alt+Shift+Q does but on enter.
    Or maybe "itemize" or "enum"?
    See also: FS_80_45_89_81 / enumerate_values
    REGISTER

*   Add note that GUI is dev/test/discovery/monitoring tool.
    REGISTER

Conceptual:

*   What is even `args_context`? It is meaningless (or means many things).
    Also describe or merged `assigned_context` vs `args_context`.
    REGISTER

*   Establish some clear order for:
    *   `init_control`
    *   `search_control`
    *   `fill_control`
    *   `invoke_control`
    And how they affect `args_context`.
    REGISTER

    Plan (TODO: merge this plan with "how search works"):
    *   Implement constant number of searches (S) per `data_envelope` required:
        1. S1: Implement query of unique values at the start of the new `data_envelope` search.
        2. Consume all args after "enum search" per `data_envelope` because no other narrowed down search for this envelope can help to consume more arg values (enum sets will only narrow down).
        3. S2: How do we call the process (to be controlled as `*_control`) when we assign implicit values? Populate singled out. This requires search for data envelopes before defaults assigned.
        4. Implement `fill_control` to provide default values.
        5. S3: Last search is to see if default values singled out envelope (or more values) - these can be colored separately from singled-out (as they singled out by defaults).
    REGISTER
    *   Try to reduce number of search requests (e.g.) file it as known issue to fix.
        REGISTER

    *   Explain mental model:
        *   Interpreter searches specific `data_envelope`-s of specific `envelope_class`.
        *   The search continues by narrowing down candidate list to one or none.
        *   If found, the search switches to next `envelope_class`.
        *   What context (list of type-value-source) is transferred from previous
            object type search to the next one is up to interpreter.

    TODO: document with examples (on how search works) for each step:
    *   TODO: `search_control`
    *   TODO: `init_control`
    *   TODO: `fill_control`
    *   TODO: `invoke_control`
    REGISTER

    ALSO:
    *   `init_control` sets values which are ensured non-overridable (by placing arg value consumable to replace default).
    *   `fill_control` sets exactly the default values (when none are selected).
    Therefore, there are several views at remaining values generated at different stages:
    *    full enum set (after `init_control` is applied) - it is actually not full because `init_control` is already effective.
    *    pre-default remaining values
    *    post-default remaining values
    Full enum set is used to see if command line value can be consumed. Note that it intentionally extended set (without taking into account filter already set by current args) to support FS_90_48_11_45.
    Pre-default remaining values are needed to provide description (options available to override defaults).
    Post-default remaining values are those used to suggest auto-completion (and show description what is reduced by defaults).
    TODO: Basically, it is nice to compute a diff between pre and post and show it in the describe output.
    REGISTER

*   Document search logic.
    REGISTER

*   Document integration logic.
    REGISTER

Ease integration into external project:

*   Extend EnvMock to assert returned JSON via JSONPath:
    https://www.digitalocean.com/community/tutorials/python-jsonpath-examples
    REGISTER
    DEV_VISIBLE

*   There is constant need to distinguish:
    *   project_dir - the path to special dir (where venv is configured via relative path, artifacts generated, config files, etc.)
    *   package_dir - the path to useful artifacts (where known after venv is sourced)
    TODO: Is this still a problem? Using `argrelay_dir` seems to solve both - each file knows its relative path from `argrelay_dir`, but does it matter if it is a deployed `argrelay` package or `argrelay` Git repo root?
    See also: FS_29_54_67_86.dir_structure.md
    FINALIZE

*   Split `argrelay.server.yaml` into: `argrelay.plugins.yaml` and `argrelay.server.yaml`.
    Or at least make it less confusing
    (because client-side still uses `argrelay.server.yaml` to use plugin configuration on server response).
    It should be called `argrelay.plugins.yaml` which is exactly the part seen and
    reused by both server and client, right?
    REGISTER

*   Make yaml config composable (to reduce chances of merging):
    allow loading external config which should plug itself into existing config.
    Maybe it should be possible to provide just configured plugins and they
    REGISTER

*   Extend EnvMock to help testing on external project side.
    Basically, the main one is a mock to ensure some function is called (although, that's easily done without EnvMock - right?).
    REGISTER

*   Make Git plugin a bit more useful (e.g. in addition to loading commit data, be able to switch to pre-configured Git repos).
    Use `help_hint` (FS_71_87_33_52) for selection of the repo.
    FINALIZE

*   Use `ssh` on selected service (a useful case).
    REGISTER

*   Think of integration with `tmux` specifically, or other ways to open new shell windows in general.
    Use `tmux` integration (built-in optional feature).
    REGISTER

*   Make operation to dump entire server config for support (without going to the server).
    See also: FS_80_45_89_81 / dump_config
    REGISTER

Perf:

*   Try querying values only - many queries may only need values (to provide suggestion) not entire `data_envelope`-s:
    https://stackoverflow.com/a/11991854/441652
    REGISTER

Docs:

*   Split "arg" group of concepts (`arg_value`, `arg_type`) and "prop" group of concepts (`prop_value`, `prop_type`):
    *   `command_line` args are mapped to `data_envelope` props and almost identical
    *   BUT: they are not naturally/intuitively inter-change-able as `data_envelope` properties are hardly `command_line` arguments.
    *   Maybe write doc on bounded contexts? Add dictionaries (ubiquitous language) per bash, client, server, data backend?
    REGISTER

Extra:

*   Add version arg type to the test data.
    REGISTER

*   Make describe output take into account current prefix (incomplete and not yet consumed) arg
    which matches several options (which are suggested on Tab, but describe should reduce output from all to just
    data which pertain to options matching that prefix).
    As the first step, instead of reducing, add different background to matching prefix of all options.
    REGISTER

*   Consider adding options to be able to limit possible values for some selected tree leaf (FS_01_89_09_24 tree).
    Currently, we can specify `ArgSource.InitValue` to one value which will reduce search results (and limit values).
    But that requires introduction of special field on `data_envlope`-s.
    Maybe it should be possible to exclude certain values from suggestions for specific arg type?
    REGISTER

*   Add test coverage reporting and cover most important logic.
    REGISTER

*   Consider splitting argrelay:
    argrelay-core
    argrelay-rest-api
    argrelay-client
    argrelay-server
    argrelay-integ (server and client)
    argrelay-demo
    while keeping `argrelay` as an easy to install package for everything at once.
    REGISTER

*   Check start of mongo db server by client connection (instead of delay).
    REGISTER

*   Describe selected service (extra meta or show payload?).
    Print `help_doc` (FS_94_30_49_28)?
    REGISTER

*   Run mongodb with reloader in debugger (need to fix reload handling).
    REGISTER

*   Add `echo` command to test arbitrary tail args.
    See also: FS_80_45_89_81 / echo_args
    REGISTER

*   Split `intercept` into two `intercept_json` and `intercept_str` (Python __str__ output).
    See also: FS_88_66_66_73.intercept_func.md, FS_80_45_89_81 / intercept_func
    REGISTER

*   Runtime stats and control:
    *   Add directory for PID and other runtime data (is it `./var/`?).
    *   Collect usage statistic per plugin in runtime dir (`./var/`?).
    *   Add scripts to manage start/stop/check of the server to the framework.
    REGISTER

*   Config-only plugins: loader and delegator.
    Target to replace standard Bash completion config.
    Data should be loaded from yaml directly without defining any enums in code.
    Launching local commands/scripts should be done via template parameterized by data envelope.
    If config-only plugin is possible and useful, every other plugin can be developed.
    REGISTER
    USER_VISIBLE

*   Why `relay_demo subshell start` ALT+SHIFT+Q fails?
    REGISTER
