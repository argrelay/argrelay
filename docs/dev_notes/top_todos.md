
TODO: top todos


To demo:

*   Consumed and unconsumed tokens:
    *   Send them to invocation (e.g. to decide to run or not to run function and how they can be used).
    *   Verify them in tests.

*   In describe, show other arg value options when default value is applied.

*   If command accept one envelope, but not yet disambiguated, then it should be possible to provide generic hook to list envelopes based on existing filter.

*   Meta function: list all objects of specified query.
*   Meta function: get and set objects (via corresponding API).

*   If there are multiple `data_envelope` anywhere in `query_plan` (as last `data_envelope` or not),
    it should be possible to hit enter and provide some meaningful action for the list of
    these currently found `data_envelope`-s of the same single class
    (even if function needs envelopes of subsequent classes).

*   Add named args.

Integration:

*   Add tests that config loading respects `ARGRELAY_CONF_BASE_DIR`.

*   Expect all files inside common `~/.argrelay` directory.
    Make it point to `custom_integ_res` dir - since there is no other files, it works nicely.

*   It should be possible to run some kind of "init" Python command immediately after `pip install argrelay`
    to make all necessary setup for custom integration done.

*   Make it possible to reuse (rather than copy and modify) every integration script.

*   FS_61_67_08_53: arbitrary text args.

*   Live status / live updates.
    Design support for online data updates.
    It should be an API to {get, set} envelope.

*   Search via different collections: https://github.com/uvsmtid/argrelay/issues/10
    Query specific Mongo DB collection.

Before `0.0.0`:

*   Rename weird names.

*   Translate class-level vars to instance-level ones.

*   What is even `args_context`? It is meaningless (or means many things).
    Also describe or merged `assigned_context` vs `args_context`.

*   Establish some clear order for:
    *   `init_control`
    *   `search_control`
    *   `fill_control`
    *   `invoke_control`
    And how they affect `args_context`.

    Plan (TODO: merge this plan with "how search works"):
    *   Implement constant number of searches (S) per `data_envelope` required:
        1. S1: Implement query of unique values at the start of the new `data_envelope` search.
        2. Consume all args after "enum search" per `data_envelope` because no other narrowed down search for this envelope can help to consume more arg values (enum sets will only narrow down).
        3. S2: How do we call the process (to be controlled as `*_control`) when we assign implicit values? Populate singled out. This requires search for data envelopes before defaults assigned.
        4. Implement `fill_control` to provide default values.
        5. S3: Last search is to see if default values singled out envelope (or more values) - these can be colored separately from singled-out (as they singled out by defaults).

    TODO: document with examples (on how search works) for each step:
    *   TODO: `search_control`
    *   TODO: `init_control`
    *   TODO: `fill_control`
    *   TODO: `invoke_control`

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

*   Document search logic.

*   Document integration logic.

*   Add consciously written semver doc.

Ease integration into external project:

*   Enable debug in all bootstrap scripts.

*   Boostrap file names do not make much:
    *   `bootstrap_outside_venv.bash`
    *   `bootstrap_inside_venv.bash` - sometimes we want to boostrap within existing `venv` (inside) but still for development (symlinks, not copies)

*   How to deal with `dev_shell.bash` symlink in custom project?
    This symlink (unlike inside `argrelay` itself) is not pointing into existing file within the repo,
    instead, it points into `argrelay` package which still has to be installed.

*   There is constant need to distinguish:
    *   project_dir - the path to special dir (where venv is configured via relative path, artifacts generated, config files, etc.)
    *   package_dir - the path to useful artifacts (where known after venv is sourced)

*   Split `argrelay.server.yaml` into: `argrelay.common.yaml` and `argrelay.server.yaml`.

*   Make it possible to override location of `argrelay.conf.d` via env var
    (to allow experimental development co-exists).

*   Make yaml config composable (to reduce chances of merging):
    allow loading external config which should plug itself into existing config.
    Maybe it should be possible to provide just configured plugins and they

*   Extend EnvMock to help testing on external project side.
    Basically, the main one is a mock to ensure some function is called (although, that's easily done without EnvMock).

*   Make Git plugin a bit more useful (e.g. in addition to loading commit data, be able to switch to pre-configured Git repos).
    Use `help_hint` (FS_71_87_33_52) for selection of the repo.

*   Use `ssh` on selected service (a useful case).

*   Think of integration with `tmux` specifically, or other ways to open new shell windows in general.
    Use `tmux` integration (built-in optional feature).

*   Make operation to dump entire server config for support (without going to the server).

Perf:

*   Try querying values only - many queries may only need values (to provide suggestion) not entire `data_envelope`-s:
    https://stackoverflow.com/a/11991854/441652

Docs:

*   Split "arg" group of concepts (`arg_value`, `arg_type`) and "prop" group of concepts (`prop_value`, `prop_type`):
    *   `command_line` args are mapped to `data_envelope` props and almost identical
    *   BUT: they are not naturally/intuitively inter-change-able as `data_envelope` properties are hardly `command_line` arguments.

Extra:

*   Consider adding options to be able to limit possible values for some selected tree leaf (FS_01_89_09_24 tree).
    Currently, we can specify `ArgSource.InitValue` to one value which will reduce search results (and limit values).
    But that requires introduction of special field on `data_envlope`-s.
    Maybe it should be possible to exclude certain values from suggestions for specific arg type?

*   Add test coverage reporting and cover most important logic.

*   Try to reduce number of search requests (e.g.) file it as known issue to fix.

*   Consider splitting argrelay -> argrelay-core, argrelay-integ (server and client), argrelay-demo, while keeping argrelay as an easy to install package.

*   Check start of mongo db server by client connection (instead of delay).

*   Describe selected service (extra meta or show payload?).
    Print `help_doc` (FS_94_30_49_28)?

*   Run mongodb with reloader in debugger (need to fix reload handling).

*   Add `echo` command to test arbitrary tail args.

*   Add `describe` internal command to do exactly the same what Ctrl +Alt + Q does, but via Invocation.
