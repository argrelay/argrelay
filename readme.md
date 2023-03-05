
Project status: working prototype

[![asciicast](https://asciinema.org/a/mkjmtGTShGpXHJ7kwojoSXyTL.svg)](https://asciinema.org/a/mkjmtGTShGpXHJ7kwojoSXyTL)

<!--
See: docs/dev_notes/screen_cast_notes.md
-->

# What's this?

An integration framework to provide contextual Tab-auto-completion<br/>
for command line interfaces (CLI) in Bash shell.

**Original use case:**<br/>
Auto-complete based on large structured data sets (e.g. config or ref data).[^1]

This requires data indexing for [responsive lookup][completion_perf_notes.md]<br/>
(the client has to start and find relevant data on each Tab-request).

The straightforward approach to meet performance requirements taken by `argrelay` is<br/>
to run a standby data server.
> For example, with several thousands of service instances,<br/>
> even if someone manages to generate Bash completion config,<br/>
> it takes considerable time to load it for every shell instance.

**Extended use case:**<br/>
Catalogues of searchable functions and (live) data<br/>
with auto-completion of keywords -<br/>
**directly from standard shell**.

# What's in a name?

Eventually, `argrelay` will "relay" (hence, the name) command line arguments to<br/>
user domain-specific command/procedure.

To clarify,<br/>
`argrelay` _framework_ can be compared with (independent)<br/>
`argparse` _library_:

| Category       | `argparse` is a library                                 | `argrelay` is a framework                                                   |
|:---------------|:--------------------------------------------------------|:----------------------------------------------------------------------------|
| Given:         | `A.py` is some script                                   | `A_relay` is a "wrapper" command<br/> configured in Bash to call `argrelay` |
| In Bash:       | type `A.py` to execute it                               | type `A_relay` to let `argrelay` decide<br/> whether to execute `A.py`      |
| Execution:     | `A.py` calls `argparse` library                         | `A.py` is called by the framework<br/> when `A_relay` is invoked            |
| Function:      | `A.py` directly does<br/> some domain-specific task     | `A_relay` directly only "relays"<br/> the command line to `argrelay`        |
| CLI source:    | `A.py` defines its CLI<br/> itself via `argparse`       | CLI for `A_relay` is defined by<br/> the framework via configs/plugins/data |
| CLI is:        | mostly code-driven                                      | mostly data-driven                                                          |
| Modify CLI:    | modify `A.py`                                           | keep `A.py` intact,<br/> re-configure `argrelay` instead                    |
| Prog lang:     | `A.py` has to be<br/> a Python script to use `argparse` | `A.py` can be anything<br/> somehow executable by `argrelay`                |
| **Important:** | `A.py`/`argparse` have no domain data<br/> to query     | `A_relay` may access any<br/> domain data from `argrelay` server            |

# What's missing?

*   Any (real) domain-specific data
*   Any (useful) domain-specific plugins

# What's in the package?

*   **Client** to be invoked by Bash hook on every Tab to<br/>
    send command line arguments to the server.
*   **Server** to parse command line and propose values from<br/>
    pre-loaded data for the argument under the cursor.
*   **Plugins** to customize:
    *   actions the client can run
    *   objects the server can search
    *   grammar the command line can have
*   **Interfaces** to bind these all together.
*   **Demo** example to start from.
*   **Testing** support and coverage.

# CLI-friendly completion: primary focus

GUI-s are secondary for `argrelay`'s niche because<br/>
GUI-s do not have the restrictions CLI-s have:
*   Technically, the server can handle requests for any GUI.
*   But API-s are primarily feature-tailored to support CLI.

<details>
<summary>show example</summary>
For example, in GUI-s, typing a query into a search bar may easily be accompanied by<br/>
(1) a separate (from the search bar) area<br/>
(2) with individually selectable<br/>
(3) full-text-search results<br/>
(4) populated in async execution.<br/>

In CLI-s, `grep` does (3) full-text-search, but what about the rest (1), (2), (4)?

To facilitate selection of results via auto-completion,<br/>
catalogue-like navigation (rather than full-text-search) seems the answer.
</details>

# Syntax: origin story

When an interface is limited...

You probably heard about research where<br/>
apes were taught to communicate with humans in sign language<br/>
(their vocal apparatus cannot reproduce speech effectively).

Naturally, with limited vocabulary,<br/>
they combined known words to describe unnamed things.

For example,<br/>
to ask for a watermelon (without knowing the exact sign),<br/>
they used combination of known "drink" + "sweet".

The default `argrelay` CLI-interpretation plugin (see `FuncArgsInterp`)<br/>
prompts for object properties to disambiguate search results until single one is found.

<details>
<summary>continue story</summary>

### Narrow down options

Without any context, just two words "drink" + "sweet" leave<br/>
a lot of ambiguity to guess a watermelon (many drinks are sweet).

A more clarified "sentence" could be:
> drink striped red sweet fruit

Each word narrows down matching object set<br/>
to more specific candidates (including watermelon).

### Avoid strict order

Notice that the word order is not important -<br/>
this line provides (almost) equivalent hints for guessing:
> striped sweet fruit red drink

It is not valid English grammar, but it somewhat works.

### Use "enum language"

Think of speaking "enum language":
*   Each word is an enum value of some enum type:
    *   Color: red, green, ...
    *   Taste: sweet, salty, ...
    *   Temperature: hot, cold, ...
    *   Action: drink, play, ...
*   Word order is irrelevant because _enum value spaces do not overlap_ (almost).
*   To "say" something, one keeps clarifying meaning by more enum values.

Now, imagine the enum types and values are not supposed to be memorized,<br/>
they are proposed to select from (based on the current context).

### Address any object

Suppose enums are binary = having only two values<br/>
(cardinality = 2: black/white, hot/cold, true/false, ...).

For example,<br/>
5 words could slice the object space to<br/>
single out (identify exactly) up to 2^5 = 32 objects.

To "address" larger object spaces,<br/>
larger enum cardinalities or more word places are required.

*   Each enum type ~ a dimension.
*   Each specific enum value ~ a coordinate.
*   Each object fills a slot in such multi-dimensional discrete space.

### Apply to CLI

CLI-s are used to write commands - imperative sentences:<br/>
specific actions on specific objects.

The "enum language" above covers searching both<br/>
an action and any object it requires.

### Suggest contextually

Not every combination of enum values may point to an existing object.

For data with sparse object spaces,<br/>
the CLI-suggestion should be limited by coordinates applicable to<br/>
remaining (narrowed down) object sets.

### Differentiate on purpose

All above may be an obvious approach to come up with,<br/>
but it is not ordinary for CLI-s of most common commands:

| Common commands (think `ls`, `git`, `ssh`, ...):                            | `argrelay`-wrapped actions:                           |
|:----------------------------------------------------------------------------|:------------------------------------------------------|
| have succinct syntax and prefer<br/> single-char switches (defined by code) | prefer explicit "enum language"<br/> defined by data  |
| rely on humans to memorize syntax<br/> (options, ordering, etc.)            | assume humans have<br/> a loose idea about the syntax |
| auto-complete only for objects<br/> known to the OS (hosts, files, etc.)    | auto-complete from<br/> a domain-specific index       |

</details>

Learn more about [how search works][how_search_works.md].

# Quick demo

This is a non-intrusive demo (without permanent changes to user env).

Clone this repo somewhere.

If `dev-shell.bash` is run for the first time,<br/>
it will ask to provide `python-conf.bash` file - follow instruction on error.

To start both the server and the client,<br/>
two terminal windows are required.

*   Server:

    Start the first sub-shell:

    ```sh
    ./dev-shell.bash
    ```

    In this sub-shell, start the server:

    ```sh
    # in server `dev-shell.bash`:
    run_argrelay_server
    ```

*   Client:

    Start the second sub-shell:

    ```sh
    ./dev-shell.bash
    ```

    While it is running (temporarily),<br/>
    this sub-shell is configured for Bash Tab-completion for `relay_demo` command.

*   Try to `Tab`-complete command `relay_demo` using [demo test data][TD_63_37_05_36.demo_services_data.md]:

    ```sh
    # in client `dev-shell.bash`:
    relay_demo goto host            # press Tab one or multiple times
    ```

    ```sh
    # in client `dev-shell.bash`:
    relay_demo goto host dev        # press Alt+Shift+Q shortcut to describe command line args
    ```

*   Inspect how auto-completion binds to `relay_demo` command:

    ```sh
    # in client `dev-shell.bash`:
    complete -p relay_demo
    ```

*   Inspect client and server config:

    *   server config: `~/.argrelay.server.yaml`
    *   client config: `~/.argrelay.client.json`

*   To clean up, exit the sub-shells:

    ```sh
    # in client or server `dev-shell.bash`:
    exit
    ```

# Data backend

There are two options at the moment - both using [MongoDB][MongoDB] API:

| Category       | `mongomock` (default)                                                                   | `PyMongo`                                                                                        |
|:---------------|:----------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|
| Data set size: | practical limit ~ 10K                                                                   | tested at 1M                                                                                     |
| Pro:           | nothing else to install                                                                 | no practical data set size limit found (yet)<br/> for `argrelay` intended use cases              |
| Con:           | understandably, does not meet<br/> non-functional requirements<br/> for large data sets | require some knowledge of MongoDB,<br/> additional setup,<br/> additional running processes<br/> |

`PyMongo` connects to running MongoDB instance which has to be configured in `mongo_config`<br/>
and `mongomock` should be disabled in `argrelay.server.yaml`:

```diff
-    use_mongomock_only: True
+    use_mongomock_only: False
```

# What's next?

*   After trying non-intrusive demo, try [intrusive one][dev_env_and_target_env_diff.md] for permanent setup.

*   Modify `ServiceLoader.py` plugin to provide data beyond [demo data set][TD_63_37_05_36.demo_services_data.md].

    The data can be simply hard-coded with different `test_data` tag<br/>
    (other than `TD_63_37_05_36` demo) and selected in `argrelay.server.yaml`:

    ```diff
        ServiceLoader:
            plugin_module_name: argrelay.custom_integ.ServiceLoader
            plugin_class_name: ServiceLoader
            plugin_type: LoaderPlugin
            plugin_config:
                test_data_ids_to_load:
                    #-   TD_70_69_38_46  # no data
    -               -   TD_63_37_05_36  # demo
    +               -   TD_NN_NN_NN_NN  # custom data
                    #-   TD_38_03_48_51  # large generated
    ```

    If hard-coding is boring, soft-code to load it from external data source.

*   Replace [redirect to `ErrorInvocator.py` plugin][link_to_redirect_to_error]<br/>
    to execute something useful instead when use hits `Enter`.

*   ...

*   Many features and docs are actively taking their shape -<br/>
    any (minimal, unfiltered, first-thought) feedback is welcome.

    [Raise questions or suggestions as issues][repo_issues] to influence the dev direction.

### [footnotes]

[^1]: **Brief History**

    Tab-completion with custom (domain-specific) arg values is<br/>
    constantly on a dev wish list for complex backend.
    *   DEC 2022: Attempts to find an adequate solution for sizeable data yielded no results.
    *   JAN 2023: The [earlier question][earlier_stack_question] received zero activity for a month</br>
        (with a single silent downvote, auto-deleted by a bot).<br/>
        Request to restore it was &#127925; Shut Down In Flames.
        <!--
        It seeked recommendations which tend to be spammed by answers<br/>
        (controversially, some spam once a month helps more than none).
        -->
    *   FEB 2023: The [explanation hangs on the appropriate site][later_stack_question] now -<br/>
        recommendations are still very welcome there.<br/>
        But, with some patience for integration, `argrelay` already became satisfying enough.

<!-- refs ---------------------------------------------------------------------------------------------------------- -->

[completion_perf_notes.md]: docs/dev_notes/completion_perf_notes.md
[MongoDB]: https://www.mongodb.com/
[dev_env_and_target_env_diff.md]: docs/dev_notes/dev_env_and_target_env_diff.md
[TD_63_37_05_36.demo_services_data.md]: docs/test_data/TD_63_37_05_36.demo_services_data.md
[earlier_stack_question]: https://stackoverflow.com/questions/74996560/
[later_stack_question]: https://softwarerecs.stackexchange.com/questions/85247/
[how_search_works.md]: docs/dev_notes/how_search_works.md
[link_to_redirect_to_error]: https://github.com/uvsmtid/argrelay/blob/6b28badd41ed697089305a01ba2da566573138b4/src/argrelay/custom_integ/ServiceInvocator.py#L110
[repo_issues]: https://github.com/uvsmtid/argrelay/issues
