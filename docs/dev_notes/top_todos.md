
TODO: top todos

Before `0.0.0`:

*   Establish some clear order for:
    *   `init_control` (should be renamed from `context_control`)
    *   `search_control`
    And how they affect `args_context`.
    Also describe or merged `assigned_context` vs `args_context`.
    Apparently, they shouldn't be provided by data, they should be given by a function -
    consider deleting FS_83_48_41_30 (prototype envelopes).

*   Populate TD_63_37_05_36 default demo data.

*   Document search logic.

*   Add consciously written semver doc.

*   Add release automation script to enforce non-dev version publishing.

Extra:

*   Translate class-level vars to instance-level ones.

*   Add named args.

*   Search via different collections.

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
