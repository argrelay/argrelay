
# What does `argrelay` solve?

Imagine you operate an automated warehouse by typing and running commands -
you use CLI (command line interface) to craft commands for both cases:
*   to run commands manually from time to time (especially, to query read-only info)
*   to run commands automatically on schedule (especially, actions prepared in script files for replay)

# The problem

```
some_warehouse_coomand retrive 2020-11-12 e04b X15 ▋
```

**Your single most annoying problem** is to know what to type next **in the middle of typing**.

Actually, simply making sense of the command above is already a problem.

You can look up possible command input somewhere else (e.g. search via some separate tools), but...

**Wouldn't it be convenient to look up that possible input directly on the command line in the middle of typing?**

Let's explore progressively how `argrelay` does it.

# Case A: single search property

The warehouse stores items with single search property `item_id`:

| `item_id` |
|-----------|
| `df3a`    |
| `df3b`    |
| `df3c`    |
| `e04a`    |
| `e04b`    |

If you want to run `some_warehouse_coomand` against an item, you execute:

```
some_warehouse_coomand df3a ▋
```

However, normally, you don't remember `item_id`-s.

**Wouldn't it be convenient to see all possible options for `item_id`-s?**

# Feature: `Tab`-completion

You can load all `item_id`-s into a stand-by `argrelay` server and use `Tab`-completion:

```
# Tab:
some_warehouse_coomand ▋

df3a df3b df3c ef0a ef0b
```

You can limit the list of options by prefix - just start typing initial characters:

```
# Tab:
some_warehouse_coomand ef0▋

ef0a ef0b
```

However, even if you see suggested `item_id`-s, they are meaningless -
for example, `ef0a` might be a random string (which makes it difficult to remember).

**Wouldn't it be convenient to select stored items by meaningful properties?**

# Case B: multiple search properties

Item may have, for example, `expiration_date`-s:

| `expiration_date` | `item_id` |
|-------------------|-----------|
| `2020-11-12`      | `df3a`    |
| `2021-02-04`      | `df3b`    |
| `2022-02-09`      | `df3c`    |
| `2022-05-18`      | `e04a`    |
| `2020-11-12`      | `e04b`    |

Now, you can select them by `expiration_date` if you do not remember its `item_id`:

```
some_warehouse_coomand 2021-02-04 ▋
```

If there are many items with the same `expiration_date`,
you can disambiguate the specific item.

In that case, `Tab`-completion will suggest only `item_id`-s matching the given `expiration_date`:

```
# Tab:
some_warehouse_coomand 2020-11-12 ▋

df3a e04b
```

`expiration_date`-s:
*   have meaning
*   but the entire value set might be too overwhelming to scan through and select by a human

Maybe you also often need to plan and execute operations based on weekdays and months -
in that case, you need to transform `expiration_date` somehow.

**Wouldn't it be convenient to search items by weekdays and months without transforming `expiration_date` on your own?**

# Feature: arbitrary search properties

You can build a search index with extra search properties for items,
for example (in that case, compute-able from `expiration_date`):
*   `exp_weekday`
*   `exp_month`

| `exp_weekday` | `exp_month` | `expiration_date` | `item_id` |
|---------------|-------------|-------------------|-----------|
| `Thu`         | `NOV`       | `2020-11-12`      | `df3a`    |
| `Fri`         | `FEB`       | `2021-02-05`      | `df3b`    |
| `Wed`         | `FEB`       | `2022-02-09`      | `df3c`    |
| `Wed`         | `MAY`       | `2022-05-18`      | `e04a`    |
| `Thu`         | `NOV`       | `2020-11-12`      | `e04b`    |

Now, when you select items, you can choose any of the 4 properties in any combination.

<details open>
<summary>
<code>Tab</code>-completion example: <b>single unassigned search property:</b>
</summary>

<br/>

When `Thu` is specified, you still need to disambiguate items by `item_id`
(the only property left with different values - other properties already have the same values):

```
# Tab:
some_warehouse_coomand Thu ▋

df3a e04b
```

</details>

<details>
<summary>
<code>Tab</code>-completion example: <b>multiple unassigned search properties:</b>
</summary>

<br/>

When `FEB` is specified, there are multiple properties to disambiguate items -
`argrelay` suggests from `exp_weekday`
(the first ambiguous one in the table from left to right):

```
# Tab:
some_warehouse_coomand FEB ▋

Fri Wed
```

</details>

<details>
<summary>
<code>Tab</code>-completion example: <b>use prefix to select from multiple unassigned search properties:</b>
</summary>

<br/>

If you provide value prefix, the property to select values for will be based on that prefix
(instead of the order of the property in the index by default) -
for example, prefix `202` matches values in `expiration_date` instead of `exp_weekday`:

```
# Tab:
some_warehouse_coomand FEB 202▋

2021-02-05 2022-02-09
```

</details>

Note again that suggested ambiguous values are narrowed down by already specified values.

Also, think of more categories (search properties) - all can be searched **fuzzily**:
*   `item_size`: `small`, `medium`, `large`, ...
*   Warehouse coordinates:
    *   `warehouse_rack`: ...
    *   `rack_level`: ...
    *   ...
*   Product categories

# Feature: `Alt+Shift+Q`-query

Command line with `Tab`-completion alone does not reveal status of matching arguments against indexed data:
*   What search properties were already assigned?
*   What search properties still have to be specified?
*   Which values did each search property take from the command line?
*   How many items are selected by the given command line?

**Wouldn't it be convenient to explain status of matching arguments against indexed data?**

In addition to `Tab`-completion, `argrelay` explains command line via `Alt+Shift+Q`-query.

This is the most valuable feature which ultimately solves
**your single most annoying problem** to know what to type next **in the middle of typing**.

The output below is simplified to get the idea.

Let's use `Alt+Shift+Q`-query with the same data index from the previous section:

| `exp_weekday` | `exp_month` | `expiration_date` | `item_id` |
|---------------|-------------|-------------------|-----------|
| `Thu`         | `NOV`       | `2020-11-12`      | `df3a`    |
| `Fri`         | `FEB`       | `2021-02-05`      | `df3b`    |
| `Wed`         | `FEB`       | `2022-02-09`      | `df3c`    |
| `Wed`         | `MAY`       | `2022-05-18`      | `e04a`    |
| `Thu`         | `NOV`       | `2020-11-12`      | `e04b`    |

<details open>
<summary>
<code>Alt+Shift+Q</code>-query example: <b>multiple unassigned search properties:</b>
</summary>

<br/>

The following output tells you:
*   The number of `wharehouse_item`-s matching the command line is `2`.
*   All matching `wharehouse_item`-s have:
    *   `exp_month` property equal to `FEB` which was `explicit`-ly specified.
*   To disambiguate there are:
    *   `exp_weekday` property with two values to select from `Fri` and `Wed`
    *   `expiration_date` property with two values to select from `2021-02-05` and `2022-02-09`
    *   `item_id` property with two values to select from `df3b` and `df3c`

```
# Alt+Shift+Q:
some_warehouse_coomand FEB ▋

wharehouse_item: 2
  exp_weekday: ? Fri Wed
  exp_month: FEB [explicit]
  expiration_date: ? 2021-02-05 2022-02-09
  item_id: ? df3b df3c
```

</details>

<details>
<summary>
<code>Alt+Shift+Q</code>-query example: <b>single unassigned search property:</b>
</summary>

<br/>

The following output tells you:
*   The number of `wharehouse_item`-s matching the command line is `2`.
*   All matching `wharehouse_item`-s have:
    *   `exp_weekday` property equal to `Thu` which was `explicit`-ly specified.
    *   `exp_month` property equal to `NOV` which was `implicit`-ly deduced.
    *   `expiration_date` property equal to `2020-11-12` which was `implicit`-ly deduced.
*   To disambiguate there is only `item_id` property with two values to select from `df3a` and `e04b`

```
# Alt+Shift+Q:
some_warehouse_coomand Thu ▋

wharehouse_item: 2
  exp_weekday: Thu [explicit]
  exp_month: NOV [implicit]
  expiration_date: 2020-11-12 [implicit]
  item_id: ? df3a e04b
```

</details>

<details>
<summary>
<code>Alt+Shift+Q</code>-query example: <b>no unassigned search properties:</b>
</summary>

<br/>

The following output tells you:
*   The number of `wharehouse_item`-s matching the command line is `1`.
*   The matching `wharehouse_item` has:
    *   `exp_weekday` property equal to `Wed` which was `implicit`-ly deduced.
    *   `exp_month` property equal to `MAY` which was `implicit`-ly deduced.
    *   `expiration_date` property equal to `2022-05-18` which was `explicit`-ly specified.
*   The selected `wharehouse_item` is completely disambiguated (singled out) - there is no more input required.

```
# Alt+Shift+Q:
some_warehouse_coomand 2022-05-18 ▋

wharehouse_item: 1
  exp_weekday: Wed [implicit]
  exp_month: MAY [implicit]
  expiration_date: 2022-05-18 [explicit]
  item_id: e04a [implicit]
```

</details>

**How does `argrelay` know what input each command expects?**

# Feature: input schema

The actual logic your command runs in `argrelay` is called "function"
(it is actually a function in Python programming language - it receives data from the server).

Without going into details, it is obvious that each function needs to declare input it expects.

In general terms, it might be called "input schema", but `argrelay` calls it `search_control`.

The point is that the expected input is customizable per function -
each function declares object classes it needs to select from.

Functions also decide themselves:
*   whether they require disambiguated (singled out) objects
*   or they can deal with multiple objects for each class

# Case C: multiple functions against single object class

You may have many items in the warehouse.

But you may also have many actions to run against them.

**Wouldn't it be convenient to use search for possible actions as well?**

<details>
<summary>
Example:
</summary>

<br/>

Before selecting `wharehouse_item`-s, you need to select a function (action):
*   If you have only one function, no selection is needed (it is deduced `implicit`-ly).
*   If you have multiple functions, you need to disambiguate them (specify `explicit`-ly).

Naturally, `argrelay` searches functions via search properties (like any other data).

For example, selecting a function by matching `retrieve` or `dispose` values:

```
some_warehouse_coomand retrieve 2020-11-12 e04b ▋
```

```
some_warehouse_coomand dispose 2020-11-12 e04b ▋
```

Obviously, `Tab`-completion and `Alt+Shift+Q`-query would work in the similar way:

```
# Alt+Shift+Q:
some_warehouse_coomand dispose 2020-11-12 e04b ▋

class_function: 1
  tree_step_0: some_warehouse_coomand [explicit]
  tree_step_1: dispose [explicit]
  func_id: func_id_dispose_warehouse_item [implicit]
wharehouse_item: 1
  exp_weekday: Thu [implicit]
  exp_month: NOV [implicit]
  expiration_date: 2020-11-12 [explicit]
  item_id: e04b [explicit]
```

</details>

# Case D: multiple functions against multiple object classes

The same search approach extends to selection of multiple object classes.

<details>
<summary>
Example:
</summary>

<br/>

So far, our functions required single object class `warehouse_item`.

We can also think of selecting a `warehouse_dron` which is supposed to execute the action:

For example:

```
# Alt+Shift+Q:
some_warehouse_coomand dispose 2020-11-12 e04b X15 ▋

class_function: 1
  tree_step_0: some_warehouse_coomand [explicit]
  tree_step_1: dispose [explicit]
  func_id: func_id_dispose_warehouse_item [implicit]
wharehouse_item: 1
  exp_weekday: Thu [implicit]
  exp_month: NOV [implicit]
  expiration_date: 2020-11-12 [explicit]
  item_id: e04b [explicit]
warehouse_dron: 5
  dron_model: X15 [explicit]
  dron_id: ? a2119085 a2119086 a2119087 a2119088 a2119089
```

The function has a choice:
*   may require disambiguating `warehouse_dron` to specific one (by `dron_id`)
*   may be able to automatically select specific drone (from those already narrowed down by `dron_model` = `X15`)

</details>

# Case E: multiple commands

In addition to `some_warehouse_command`,
you may want to have `some_drone_command` with a functions to `activate` or `deactivate` them:

```
some_drone_command deactivate X15
some_drone_command activate a2119085
```

<details>
<summary>
Details:
</summary>

<br/>

Ultimately, `argrelay` supports any number commands with N-to-M commands-to-functions relationship:

*   Each command may or may not have many functions.

*   Each function may be mapped into one or many commands.

    For example, `func_id_dispose_warehouse_item` may be mapped into two commands:

    *   `some_warehouse_command dispose` (one of a few other functions for this command)

    *   `dispose_warehouse_item` (dedicated command for single function)

</details>

# Feature: `Enter`-invocation

Apart from assistance **in the middle of typing**, `argrelay` supplies functions with data on invocation:

```
# Enter:
some_warehouse_coomand 2022-05-18 ▋
```

The single argument `2022-05-18` retrieves entire `wharehouse_item` object with arbitrary data in `envelope_payload` -
similar to specifying a file name and receiving the entire file content:

```json
{
    "exp_weekday": "Thu",
    "exp_month": "NOV",
    "expiration_date": "2022-05-18",
    "item_id": "e04a",
    "envelope_payload": { ... arbitrary custom data ... },
}
```

Unlike selecting a file by its name to get its content,
`argrelay` allows selecting single or multiple `envelope_payload`-s by multiple arbitrary search properties.

When user hits `Enter`:
*   client sends entire command line to the server
*   server queries all objects by their search properties (similar to `Tab`-completion or `Alt+Shift+Q`-query)
*   client receive data and finds the function selected by user locally
*   client passes control and all data to the local function

In case of `argrelay` client, from the shell point of view, it is a regular command -
the shell does not know `argrely` server exists.

# Feature: generic structured data search

Instead of using a search server, you may think of shell-scripting to search input for a command locally, for example:

*   `grep`-ing a line with input from a text file:

    ```
    some_warehouse_command $( cat all_warehouse_items.txt | grep 2020-11-12 | grep e04b )
    ```

*   instead of `argrelay`:

    ```
    some_warehouse_command 2020-11-12 e04b
    ```

But you should immediately see many problems with `grep`-ing approach.

<details>
<summary>
And <code>argrelay`</code> <b>solves many of them:</b>
</summary>

<br/>

*   `grep` uses plain text search which matches data indiscriminately.

    With `grep`, arbitrary comment containing `2022-05-18` and `e04b` may yield unexpected results.

    `argrelay` uses structured data search:
    *   `expiration_date` = `2022-05-18`
    *   `item_id` = `e04b`

*   Only you know what you mean when you `grep`-ing `2020-11-12` and `e04b`.

    With `argrelay`, it has to match command schema and indexed data to become a validated input.

    You actually may know nothing to start with - and that is the point:
    *   you can learn what is going on via `Alt+Shift+Q`-query
    *   then you select from suggested values

*   `grep` is relatively slow to scan large files.

    `argrelay` uses a pre-built index in a stand-by server to be responsive.

*   How complex your ad-hoc shell-script can become before you lose trust in it?

    `argrelay` follows conventional development cycles with constantly evolving test coverage.

</details>

# The deal

Basically, `argrelay` offers combination of both:
*   **hiding complexity** of generic structured search engine inside its server
*   exposing data to command line via **trivial syntax** assisted by input schema and indexed data

# Summary

You interact with `argrelay` via:
*   `Tab`-completion
*   `Alt+Shift+Q`-query

This solves **your single most annoying problem** to know what to type next **in the middle of typing**:
*   matches command line input against command input schema to navigate and interrogate you
*   suggests arguments based on generic structured search within indexed data

All that leads to:
*   `Enter`-invocation
*   supporting multiple commands
*   with multiple functions
*   against multiple object classes
*   with multiple search properties
*   delivering categorized `envelope_payload`-s to your business logic

# Next steps

Start the ["interactive demo"][interactive_demo] -
see `lay ssh` and `ar_ssh` commands which allow simple modification of code & data.

<!-- links --------------------------------------------------------------------------------------------------------- -->

[argrelay_org]: https://argrelay.org/

[interactive_demo]: ../../readme.md#argrelay-changes-to-code-and-data
