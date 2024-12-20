
This doc explains (and links) some of the terms used in `argrelay` docs and sources.

# A

### `arg_name`

= a name for `command_arg`.

It is applicable only to:
*   FS_20_88_05_60 `dictated_arg`-s

Do not confuse with `prop_name` (which is used in `data_envelope`-s) -
`arg_name` and `prop_name` are not the same concept (and may be different in name),
but they are still closely related
(as `arg_name` is mapped into `prop_name` via FS_31_70_49_15 `search_control`).

See also:
*   `command_arg`
*   `arg_value`
*   `prop_name`
*   FS_10_93_78_10 `arg_name_to_prop_name_map`

### `arg_value`

= a value of `command_arg`.

It is applicable to both:
*   FS_96_46_42_30 `offered_arg`-s
*   FS_20_88_05_60 `dictated_arg`-s

Do not confuse with `prop_value` (which is used in `data_envelope`-s) -
`arg_value` and `prop_value` are not the same concept,
but they have the same values
(when corresponding `arg_name` is mapped into corresponding `prop_name` via FS_31_70_49_15 `search_control`).

See also:
*   `command_arg`
*   `arg_name`
*   `prop_value`

# C

### `command_arg`

= a higher level concept (composition) built out of `command_token`-s.

There are few type of `command_arg`-s:
*   FS_96_46_42_30 `offered_arg`-s
*   FS_20_88_05_60 `dictated_arg`-s

See also:
*   `token_bucket`
*   `command_token`

### `command_id`

= the very first arg on the command line (`offered_arg` with 0 ipos = index 0).

For example, `some_command` is `command_id` in this command line:

```sh
some_command goto host dev amer upstream qwer
```

In fact, `command_id` is equivalent to `zero_index_arg`, but two different terms are used depending on the context.

See also:
*   `zero_index_arg`
*   FS_01_89_09_24 (interp tree) and FS_42_76_93_51 (zero arg interp).
*   `ipos`

### `command_token`

= a string of contiguous non-whitespace chars between two whitespaces.

`argrelay` server splits command line string into tokens by whitespaces.

In all cases, the server receives the entire command line
(concatenated back into single string if required) to re-tokenize, re-parse, re-interpret by
the server with its own logic...

For example, in case of `ServerAction.RelayLineArgs`, `argrelay` client receives CLI input as
`sys.argv` (in Python) which is a result of parsing by shell,
but despite that `sys.argv` name, they correspond to `command_token`-s (rather than `command_arg`-s) because
they are subsequently concatenated and re-tokenized.

`command_token` and `command_arg` bear confusingly close meaning,
but there are `argrelay`-specific differences
*   `command_token` is a lower-level (atomic) concept
*   `command_arg`-s is a higher-level (composite) concept

See also:
*  `command_arg`
*  `token_bucket`

### `cpos`

= a char index within a string.

See also `ipos`.

# D

### `data_envelope`

= a `dict` storable as is in data backend.

This `dict` has `prop_name` and `prop_value` for searching.

See also:
*   FS_37_57_36_29 (containers, envelopes, payloads).

### `dictated_arg`

= a `command_arg` which has both a name and a value.

See also:
*   FS_20_88_05_60 dictated_arg
*   FS_96_46_42_30 offered_arg

# E

### `envelope_class`

= a name which determines `data_envelope` payload schema.

See also:
*   FS_37_57_36_29 containers, envelopes, payloads

### `envelope_container`

= a runtime object which wraps `data_envelope` with associated runtime processing info.

See also FS_37_57_36_29 (containers, envelopes, payloads).

### `envelope_collection`

A wrapper providing data for a MongoDB collection:
*   list of `index_prop`-s
*   set of `data_envelope`-s

See also:
*    FS_56_43_05_79 search in different collections
*   `EnvelopeCollection`

### `envelope_payload`

= a custom (plugin-specific) nested data within `data_envelope` opaque to `argrelay`
(only specific plugins understand it).

See also FS_37_57_36_29 (containers, envelopes, payloads).

# F

### `func`

= synonym to `function` (`func` is just shorter to type).

Each `func` has `func_id` and it is implemented by delegator plugin (see `DelegatorAbstract` hierarchy).

# I

### `incomplete_token`

= a `tangent_token` with empty `token_right_part` matching some of the enum items.

This is a token which is actually complete (matching one of the value, maybe matching more a prefix)
except that it is also a `tangent_token` and should behave differently depending on
whether it is `ServerAction.ProposeArgValues` or not.

### `index_prop`

MongoDB allows declaring `index_prop`-s per collection to make `data_envelope` search faster.
There are some limits - see FS_56_43_05_79 search in different collection.

List of `index_prop`-s per collection is defined in `EnvelopeCollection`.

### `interp`

= synonym to `interpreter` (`interp` is just easier to pronounce and shorter to type).

See usage of `AbstractInterp`.

### `interpreter`

See `interp`.

### `interrogate`

See `interrogation`

### `interrogation`

= process when user types a selected `command_arg`-s (normally, based on previous Tab-completion).

This is "interrogation" in the sense that `suggest`-ed `arg_value`-s via Tab-completion appear to user
as a question with answer options choose from.

See also `suggestion`.

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

*   `ipos` is an index of token within list of command line tokens
*   `cpos` is an index of char within string (e.g. individual arg or entire command line)

See also `cpos`.

# O

### `offered_arg`

= a `command_arg` which has only a value.

See also:
*   FS_96_46_42_30 offered_arg
*   FS_20_88_05_60 dictated_arg

# P

### `plugin_config`

= "plugin instance config"

This may mean either specifically `plugin_config` (part of `plugin_entry`) or `plubin_entry`.

See also FS_00_13_77_97 plugin framework.

### `plugin_entry`

= "plugin instance entry" which describes a plugin instance to `argrelay` via `PluginEntrySchema.py`.

See also FS_00_13_77_97 plugin framework.

### `prop_name`

= a name of a property in `data_envelope` and `envelope_container`.

Do not confuse with `arg_name` (which is part of `command_arg`), but compare them - see `arg_name`.

See also:
*   FS_10_93_78_10 `arg_name_to_prop_name_map`
*   `prop_value`

### `prop_value`

= a value of a property in `data_envelope` and `envelope_container`.

Do not confuse with `arg_value` (which is part of `command_arg`), but compare them - see `arg_value`.

See also:
*   `prop_name`

# S

### `suggest`

See `suggestion`.

### `suggestion`

= a process to request `command_arg`-s options to choose from (normally, during Tab-completion).

See also `interrogation`.

# T

### `tangent_token`

= a token "touched" by the cursor.

See FS_23_62_89_43 `tangent_token`.

It can be touched on the side as in `apac|` or can be touched within `ap|ac`.

*   `token_left_part`: tangent token substring on the left from the cursor (can be empty).
*   `token_right_part`: tangent token substring on the right from the cursor (can be empty).

### `token_bucket`

= a collection of `command_token`-s separated by `SpecialChar.TokenBucketDelimiter` token

It does not include `SpecialChar.TokenBucketDelimiter` token.

`token_bucket` form a sub-set of `command_token`-s.

`token_bucket` is used to set boundaries for `command_arg`-s consumption.

See [`FS_97_64_39_94.token_bucket.md`][FS_97_64_39_94.token_bucket.md].

### `token_left_part`

See `tangent_token`.

### `token_right_part`

See `tangent_token`.

### `tree_path`

Tree (direct acyclic graphs with one parent per child) are often used in config - see:
*   FS_33_76_82_84 composite forest
*   FS_01_89_09_24 interp tree
*   FS_26_43_73_72 func tree
*   FS_91_88_07_23 jump tree

For example, a tree can be expressed in YAML as:

```yaml
    l1_1: some_id_1
    l1_2:
        l2_1:
            l3_1:
                l4_1: some_id_2
                l4_2: some_id_3
    l1_3:
        l2_2: some_id_4
        l2_3: some_id_5
        l2_4:
            l3_2: some_id_6
```

Nodes like `some_id_n` are leaves (having no other children).

In this case, tree path is just any path leading to any node, for example, expressed in Python tuple as:

```python
# tree path leading to leaf node `some_id_4`:
("l1_4", "l2_2", )
# tree path leading to node with children `l4_1` and `l4_2`:
("l1_2", "l2_1", "l3_1", )
```

They could be expressed in file system (FS) notation as `l1_4/l2_2` and `l1_2/l2_1/l3_1`,
but runtime deals with Python tuples.

Tree paths can also be:
*   `tree_abs_path` = absolute tree path (e.g. equivalent to FS notation `/l1_4/l2_2` starting from the root)
*   `tree_rel_path` = relative tree path (e.g. equivalent to FS notation `l2_1/l3_1` starting anywhere within the tree).

# U

### `unrecognized_token`

= a token matching none of the enum items (under given context)

It can be match some enum items as prefix, but if left as is, it does not match any.

# Z

### `zero_index_arg`

This is the first arg on the command line (which is accessed via zero index into array of args).

`zero_index_arg` is equivalent to `command_id`.

For example:

```sh
ls -lrt
git log
```

In the example above, `ls` and `git` are `zero_index_arg`-s.

Such arg is special:

*   on client side:

    It defines what shell does (e.g. what Tab-completion logic to run) or
    what executable file to start.

*   on server side:

    It is supposed to select interpretation logic of the entire command line
    (e.g. via FS_15_79_76_85 line processor).

See also:
*   `command_id`
*   FS_42_76_93_51 very first zero arg mapping interp

<!-- links --------------------------------------------------------------------------------------------------------- -->

[FS_97_64_39_94.token_bucket.md]: ../feature_stories/FS_97_64_39_94.token_bucket.md
