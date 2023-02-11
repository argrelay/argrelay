
TODO: top todos

*   Establish some clear order for:
    *   `init_control` (should be renamed from `context_control`)
    *   `search_control`
    And how they affect `args_context`.
    Also describe or merged `assigned_context` vs `args_context`.
    Apparently, they shouldn't be provided by data, they should be given by a function -
    consider deleting FS_83_48_41_30 (prototype envelopes).

*   Add named args.

*   Search via different collections.

*   FS_18_64_57_18: Var args

*   Meta functions:
    *   List all objects of specified query.
    *   Show catalog of functions.

*   Fix arg overlap test data and test cases.

*   Document search logic, add test cases.
    Try to reduce number of search requests (e.g.) file it as known issue to fix.

*   KI_12_84_57_78: Fix singled out args test case.
