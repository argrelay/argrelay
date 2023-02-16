
TODO: top todos

Integration:

*   List data = function with multiple envelopes

*   Get help metadata
    Showing help: help_title, help_details.

*   Live status

Before `0.0.0`:

*   Establish some clear order for:
    *   `init_control` (should be renamed from `context_control`)
    *   `search_control`
    And how they affect `args_context`.
    Also describe or merged `assigned_context` vs `args_context`.
    Apparently, they shouldn't be provided by data, they should be given by a function -
    consider deleting FS_83_48_41_30 (prototype envelopes).

*   Populate TD_63_37_05_36 demo services data.

*   Document search logic.

*   Document integration logic.

*   Add consciously written semver doc.

*   Add release automation script to enforce non-dev version publishing.

Extra:

*   Translate class-level vars to instance-level ones.

*   Add named args.

*   Search via different collections: https://github.com/uvsmtid/argrelay/issues/10

*   FS_18_64_57_18: Var args

*   Meta functions:
    *   List all objects of specified query.
    *   Show catalog of functions.
    *   Print help string.

*   Fix arg overlap test data TD_76_09_29_31 and test cases.

*   Add tests to ensure override arg works (e.g. from implicit `ro` by explicit `rw`).

*   Add test coverage reporting and cover most important logic.

*   Try to reduce number of search requests (e.g.) file it as known issue to fix.

*   KI_12_84_57_78: Fix singled out arg values for multiple `data_envelope`-s.

*   Query specific Mongo DB collection.

*   Fix perf output in server-side logs.

*   Make server config composable (allow including other files).

*   Think to start each arg as `ArgSource.UnassignedValue` (or at least mark it in the described arg output as this).

*   FS_61_67_08_53: arbitrary text args.

*   Make Git plugin a bit more useful (e.g. in addition to loading commit data, be able to switch to pre-configured Git repos).

*   Think of integration with `tmux` specifically, or other ways to open new shell windows in general.

*   Add data center and server rack to demo data.
