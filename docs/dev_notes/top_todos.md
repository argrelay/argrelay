
TODO: top todos

Tags:
*   FINALIZE: The feature already works but needs coverage, small qualitative improvements, documentation.
*   CLOSED: The issue is done or being tracked otherwise = no need to keep this todo, but still kept to keep in the view.
*   REGISTER: The item is not yet registered, requires new feature story (FS) entry.
*   USER_VISIBLE: Something what is visible to user (rather than just making things better).
*   DEV_VISIBLE: Something what is visible to dev (may not be visible for users as USER_VISIBLE, but helps dev).

Top:


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

*   Consumed and remaining tokens:
    *   Send them to invocation (e.g. to decide to run or not to run function and how they can be used).
    *   Verify them in tests.
    FINALIZE

*   Meta function: list all objects of specified query.
    See also: FS_80_45_89_81 / list_envelope
    REGISTER

*   If there are multiple `data_envelope` anywhere in `query_plan` (as last `data_envelope` or not),
    it should be possible to hit enter and provide some meaningful action for the list of
    these currently found `data_envelope`-s of the same single class
    (even if function needs envelopes of subsequent classes).
    REGISTER

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

*   FS_61_67_08_53: arbitrary text args.
    Tracked via FS_61_67_08_53 and https://github.com/argrelay/argrelay/issues/46
    CLOSED

*   Live status / live updates.
    Design support for online data updates.
    It should be an API to {get, set} envelope.
    Tracked via issue: https://github.com/argrelay/argrelay/issues/20Live
    CLOSED

GUI bits:

*   Add info descriptions (tooltip or question mark with description).
    REGISTER

*   When there is no common prefix, Tab should not work, flash command line with red color.
    REGISTER

*   When there is no common prefix, Tab should not work (do not replace current token).
    REGISTER

*   Be able to enable verbose server logging and disable it via GUI.
    Basically, this is debug flag, but set on GUI client (via GUI), not CLI client (via env var).
    REGISTER

*   Test with lots of data - run same tests against server with lots of data.
    Are there any issues with races between user input and server response?
    FINALIZE

*   Handle `help` response differently in GUI - print help.
    REGISTER

*   Make command history a list (not drop down). Make it scrollable beyond 20 commands.
    REGISTER

*   Can we cancel request if new request has to be made and old one is invalid (e.g. caret has moved)?
    See also: https://stackoverflow.com/a/47250621/441652
    FINALIZE

Conceptual:

*   Instead of providing positional parameter list for test cases (see those with subTests),
    introduce generic ResultAssertBuilder (or something like that) which can build expectations in any order.
    REGISTER

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

*   There is constant need to distinguish (TODO: name it properly):
    *   argrelay_target_dir - the path to special dir (where venv is configured via relative path, artifacts generated, config files, etc.)
    *   argrelay_distrib_dir - the path to useful artifacts (where known after venv is sourced)
    TODO: Is this still a problem?
          Yes.
          *   `argrelay_inst_dir` must be the project (where argrelay is used or itself, or where it is deployed).
          *   Anything else like `argrelay_module_dir_path` obtained by running Python is package_dir
    See also: FS_29_54_67_86.dir_structure.md
    FINALIZE

*   Make yaml config composable:
    *   reduce size and chances of merging unrelated parts
    *   avoid config modification by loading other parts from known (by convention) places
    *   allow loading external config which should plug itself into existing config
    Maybe it should be possible to provide just the list of configured plugins (their loading order)
    and they will load automatically from expected location?
    Also split core server config (open ports, mongo, cache) and plugin management.
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

Extra:

*   Add version arg type to the test data.
    See `TD_63_37_05_36.demo_services_data.md` - it does not have source version or source tag.
    REGISTER

*   Make describe output take into account current prefix (incomplete and not yet consumed) arg
    which matches several options (which are suggested on Tab, but describe should reduce output from all to just
    data which pertain to options matching that prefix).
    Already tracked under `FS_80_82_13_35.option_list_on_describe_with_prefix.md`.
    REGISTER

*   Consider adding options to be able to limit possible values for some selected tree leaf (FS_01_89_09_24 interp tree).
    Currently, we can specify `ArgSource.InitValue` to one value which will reduce search results (and limit values).
    But that requires introduction of special field on `data_envlope`-s
    (which gets assigned a value with `ArgSource.InitValue`) which looks very surrogate.
    Maybe it should be possible to exclude certain values from suggestions for specific arg type at selected tree leaves?
    REGISTER

*   Add test coverage reporting.
    It could be a result of `@/exe/run_max_tests.bash` or `tox`.
    REGISTER

*   Consider splitting argrelay into separate packages (install-able independently but interdependent):
    argrelay-core
    argrelay-rest-api
    argrelay-client
    argrelay-server
    argrelay-integ (server and client)
    argrelay-demo
    while keeping `argrelay` as an easy to install package for everything at once.
    REGISTER

*   Check start of mongo db server by client connection (instead of delay).
    Based on answers to this SO, there are many ways and all non-standard:
    https://stackoverflow.com/q/5091624/441652
    Simply allow to configure command to check for mongo db status
    (it could be different commands based on target system).
    Use return code: 0 = server started, 1 = wait, anything else = failure (stop).
    REGISTER

*   Split `intercept` into: `intercept_json`, `intercept_str` (Python __str__ output), `intercept_table`.
    See also: FS_88_66_66_73.intercept_invocation_func.md, FS_80_45_89_81 / intercept_invocation_func
    REGISTER

