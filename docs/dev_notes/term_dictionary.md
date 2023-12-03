
TODO: reformat, sort, populate, link to `feature_story`-ies.

*   token: substring of command line (split by one or more delimiter chars), see usage of `SpecialChar`.
*   argument = arg: one or more command line token interpreted as a function argument, see usage of `TokenType`.
*   curr, prev, next: current, previous, next item during processing.
*   tangent = tan: token "touched" by the cursor - see FS_23_62_89_43.
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

= a char index within a string.

See also `ipos`.

### `command_id`

= the very first arg on the command line (`PosArg` with 0 ipos = index 0).

For example, `some_command` is `command_id` in this command line:

```sh
some_command goto host dev amer upstream qwer
```

See also:
*   FS_01_89_09_24 (interp tree) and FS_42_76_93_51 (zero arg interp).
*   `ipos`

# D

### `data_envelope`

= a `dict` storable as is in data backend.

This `dict` has properties for searching.

See also FS_37_57_36_29 (containers, envelopes, payloads).

# E

### `envelope_container`

= a runtime object which wraps `data_envelope` with associated runtime processing info.

See also FS_37_57_36_29 (containers, envelopes, payloads).

### `envelope_payload`

= a custom (plugin-specific) nested data within `data_envelope` opaque to `argrelay`
(only specific plugins understand it).

See also FS_37_57_36_29 (containers, envelopes, payloads).

# I

### `interp`

= synonym to `interperter` (`interp` is just easier to pronounce and shorter type).

### `interrogation`

= process when user types a selected command line arg (normally, based on previous Tab-completion).

This is "interrogation" in the sense that suggested arg values via Tab-completion appear to user
as a question with answer options choose from.

### `ipos`

= a short form from "index position".

An item index within a list.

The term emphasizes 0-base indexing.

It is also explicitly different from `cpos` (which points to individual character)<br/>
to avoid confusion in parsing where both command line arg list and command line string is dealt with:

```
some_command goto host dev amer upstream qwer
             0123
0            1 ^  2    3   4    5        6
               |           ^
               |           |
               |           |
               |           ipos = 4
               cpos = 2
```

*   `ipos` is an index of arg within list of command line args
*   `cpos` is an index of char within string (e.g. individual arg or entire command line)

See also `cpos`.

# P

### `plugin_config`

= "plugin instance config"

This may mean either specifically `plugin_config` (part of `plugin_entry`) or `plubin_entry`.

See also FS_00_13_77_97 plugin framework.

### `plugin_entry`

= "plugin instance entry" which describes a plugin instance to `argrelay` via `PluginEntrySchema.py`.

See also FS_00_13_77_97 plugin framework.
