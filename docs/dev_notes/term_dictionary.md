
TODO: reformat, sort, populate, link to `feature_story`-ies.

*   token: substring of command line (split by one or more delimiter chars), see usage of `SpecialChar`.
*   argument = arg: one or more command line token interpreted as a function argument, see usage of `TokenType`.
*   curr, prev, next: current, previous, next item during processing.
*   tangent = tan: token "touched" by the cursor.
*   token left part: tangent token substring on the left from the cursor.
*   token right part: tangent token substring on the right from the cursor.
*   interpreter = interp: see usage of `AbstractInterp`.

*   type: unique (across all interpreters) name for a set of values.
*   key: unique (within current interpreter) alias name for a type.

*   interrogate (user to specify arg value)
*   suggest (arg values to user (to interrogate the user))

*   arg type = describes arg value, see also: FS_53_81_66_18 # TnC
*   arg value = any string from a value set according to arg type.
*   envelope class = describes `data_envelope` schema, see also: FS_53_81_66_18 # TnC

# C

### `cpos`

A char index within a string.

See also `ipos`.

### `command_id`

The very first arg on the command line (`PosArg` with 0 ipos = index 0).

For example, `some_command` is `command_id` in this command line:

```sh
some_command goto host dev amer upstream qwer
```

# D

### `data_envelope`

A `dict` storable as is in data backend.

This `dict` has properties for searching.

See also FS_37_57_36_29 (envelopes and payloads).

# E

### `envelope_container`

A runtime object which wraps `data_envelope` with associated runtime processing info.

# I

### `ipos`

A short form from "index position".

An item index within a list.

The term emphasizes 0-base indexing.

It is also explicitly different from `cpos` (which points to individual character)<br/>
to avoid confusion in parsing where both command line arg list and command line string is dealt with.

See also `cpos`.
