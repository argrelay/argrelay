
TODO: Create separate FS with the first two sections of this doc to describe args to props mapping:
      what we have on input (command line)
      what we have on output (Mongo query)
      This should be description in a nutshell, with references to details on arg groups (per each `data_envelope` type), defaults, etc.

# Example

*   Command line:

    ```sh
      some_command goto dev rw apac upstream host         # command line
    # 0            1    2   3  4    5        6            # arg index
    ```

*   Command line args mapping:

    ```mermaid
    flowchart TB
        goto(goto 1) --> F([func impl])
        dev(dev 3) --> H([host])
        rw(rw 2) --> A([access])
        apac(apac 4) --> H([host])
        upstream(upstream 5) --> H([host])
        host(host 6) --> F([func impl])
    ```

*   Legend:

    *   [func impl] = group of command line args to find `data_envelope` of `ClassFunction`

    *   [host] = group of command line args to find `data_envelope` of `ClassHost`

    *   [access] = group of command line args (only one) to find `data_envelope` providing `access_type`

# A few things to note in the example ahead of the explanation

*   The order of `data_evelope`-s to find is:

    ```
    [func impl] [host] [access]
    ```

    Which suggest _natural_ order of the args on the command line as:

    ```sh
      some_command    goto host      dev apac upstream    rw          # command line
    #                 [func impl]    [host]               [access]    # group
    ```

*   The _actual_ order of the command line args in the example _interleave_:

    *   `host` for func impl is specified 6th, not 2nd.

    *   `rw` for access is specified 3rd, not 6th (the last).

# Explanation

TODO: Merge this section of the doc with FS_55_57_45_04 enum selector.

*   The ultimate purpose of the command line is to execute some function with some arguments.

    Think of function overloading when there is one function name
    but multiple implementations depending on argument types.
    Remember - there is no such thing as function overloading in `argrelay`.

    There is also no attempt to guess required function implementation by provided arguments.

    In other words, user must unambiguously specify required function implementation first.

    In the example above, function implementation is determined by two args: `goto` and `host`.

*   Search is done in phases:
    *   Phase 1: search single func impl (function implementation)
    *   Phase 1+N: search multiple func args (function arguments)

*   The same search mechanism is used in all phases of finding `data_envelope`-s:
    *   Phase 1: Each function impl is a `data_envelope` to find.
    *   Phase 1+N: All function args are `data_envelope`-s to find.

*   Matching `data_envelope`-s.

    Each `data_envelope` has unique set of key-value paris ~ (`arg_key`, `arg_value`) to be searched by.

    The command line args provide `arg_value`-s to perform the search of `data_envelope`-s.

    The task is to decide which `arg_key` each command line arg belongs to.

*   The role of phase 1 (func impl)

    Function impl is more than just a target code to invoke ultimately,
    it is an extension (provided via a plugin) with multiple callbacks.
    *   The first such callback is `search_control` to tell what func args this func impl requires (to start phase 1+N).
    *   Callback `init_control` to init some search params via logic (rather than via command line args).
    *   Callback `fill_control` to populate default params, if possible, if no other option available.
    *   Ultimately, callback `invoke_control` to prepare data for client to invoke target code.

*   General steps

    Phase 1:
    *   Invoke `search_control` (not on func impl yet, but on interp) to learn `search_control` structure.
    *   Invoke `init_control` (not on func impl yet, but on interp) to pre-assign some fields in `search_control` structure.
    *   Enum query: in database, find all unique values for unassigned fields in `search_control` structure of func impl class (`ReservedEnvelopeClass.ClassFunction`).
    *   Assign command line args to `search_control` structure by matching if arg type belongs to enum class.
    *   TODO: Invoke `fill_control` (not on func impl yet, but on interp) to select default values.
    *   Perform final search to see if func impl is uniquely identified (only one fits the criteria).

    Phase 1 does not move to next one until unique func impl is selected.

    Phase 1+N:
    *   Invoke `search_control` (now on func impl) to learn `search_control` structure.
    *   Invoke `init_control` (now on func impl) to pre-assign some fields in `search_control` structure.
    *   Enum query: in database, find all unique values for unassigned fields in `search_control` structure of this `data_envelope` class (for example, `ServiceEnvelopeClass`).
    *   Assign command line args to `search_control` structure by matching if arg type belongs to enum class.
    *   TODO: Invoke `fill_control` now on func impl to select default values.
    *   Perform final search to see if `data_envelope` is uniquely identified (only one fits the criteria).

