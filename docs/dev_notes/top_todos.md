
TODO: top todos


To demo:

*   Fix this:

    ```
    relay_demo goto host dev-emea-downstream ro

    ClassFunction:
      ActionType: goto [ExplicitPosArg]
      ObjectSelector: host [ExplicitPosArg]
    ClassCluster:
      *CodeMaturity: ? dev                                                        # Fixed, but why no [ImplicitArg]?
      FlowStage: ? downstream                                                     # Why not fixed?
      GeoRegion: ? emea                                                           # Why not fixed?
      ClusterName: dev-emea-downstream [ExplicitPosArg]
    ClassHost:
      ClusterName: dev-emea-downstream [InitValue]
      HostName: xcvb-dd [ImplicitValue]
      LiveStatus: [none]
    AccessType:
      AccessType: ro [ExplicitPosArg]
    ```

*   Populate TD_63_37_05_36 demo services data.
    Complete demo data: add (1) data center, (2) server rack, (3) process id, to demo data.

*   "Describe" should run with InvocationMode instead of CompletionMode (to include current tangent tocken).

*   Meta functions:
    *   List all objects of specified query.
    *   Show catalog of functions.
    *   Print help string.

*   List data = function with multiple envelopes

*   Get help metadata
    Showing help: help_title, help_details.

*   FS_18_64_57_18: Var args

*   If there are multiple `data_envelope` anywhere in `query_plan` (as last `data_envelope` or not), it should be possible to hit enter and provide some meaningful action for the list of these `data_envelope`-s of one clas currently found (even if function needs envelopes of subsequent classes).

*   KI_12_84_57_78: Fix singled out arg values for multiple `data_envelope`-s.

*   Change separator from `|` to ` `.

*   Add tests to ensure override arg works (e.g. from implicit `ro` by explicit `rw`).

*   Add named args.

Integration:

*   FS_61_67_08_53: arbitrary text args.

*   Fix arg overlap test data TD_76_09_29_31 and test cases.

*   Live status / live updates.
    Design support for online data updates.
    It should be an API to {get, set} envelope.

*   Fix perf output in server-side logs.

Before `0.0.0`:

*   Translate class-level vars to instance-level ones.

*   What is even `args_context`? It is meaningless (or means many things).
    Also describe or merged `assigned_context` vs `args_context`.

*   Establish some clear order for:
    *   `init_control`
    *   `search_control`
    *   `fill_control`
    *   `invoke_control`
    And how they affect `args_context`.
    Apparently, they shouldn't be provided by data, they should be given by a function -
    consider deleting FS_83_48_41_30 (prototype envelopes).

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

*   Add release automation script to enforce non-dev version publishing.

Extra:

*   Search via different collections: https://github.com/uvsmtid/argrelay/issues/10
    Query specific Mongo DB collection.

*   Add test coverage reporting and cover most important logic.

*   Try to reduce number of search requests (e.g.) file it as known issue to fix.

*   Make server config composable (allow including other files).

*   Think to start each arg as `ArgSource.UnassignedValue` (or at least mark it in the described arg output as this).

*   Make Git plugin a bit more useful (e.g. in addition to loading commit data, be able to switch to pre-configured Git repos).

*   Think of integration with `tmux` specifically, or other ways to open new shell windows in general.
    Use `tmux` integration (built-in optional feature).


*   Extend EnvMock to help testing on external project side.
    Basically, the main one is a mock to ensure some function is called (although, that's easily done without EnvMock).

*   Consider splitting argrelay -> argrelay-core, argrelay-integ (server and client), argrelay-demo, while keeping argrelay as an easy to install package.

*   Use `ssh` on selected service (a useful case).

*   Describe selected service (extra meta or show payload?).

*   Try help for every suggested option:
    https://stackoverflow.com/questions/7267185/bash-autocompletion-add-description-for-possible-completions/10130007#10130007

