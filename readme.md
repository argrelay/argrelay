
[![PyPI package](https://badge.fury.io/py/argrelay.svg)](https://badge.fury.io/py/argrelay)
[![GitHub build](https://github.com/argrelay/argrelay/actions/workflows/argrelay.bootstrap.yaml/badge.svg?branch=main)](https://github.com/argrelay/argrelay/actions/workflows/argrelay.bootstrap.yaml)

<a name="argrelay-secreencast"></a>
[![asciicast](https://asciinema.org/a/LTHj0DHN2kfXJCHCGuJugNG4P.svg)](https://asciinema.org/a/LTHj0DHN2kfXJCHCGuJugNG4P)

<!--
See: docs/dev_notes/screencast_notes.md
-->

<a name="argrelay-about"></a>
# What's this?

A tool to provide object selector (structured data search filter) for command line interface (CLI):
*   User select objects via "enum language" using tags|labels|keywords which belong to one of the `enum` sets.
*   The `enum` sets are dynamically composed of all the objects property values within user data.
*   Fuzzy-search (yet easily predictable) is achieved by:
    *   relying on rare intersection between `enum` sets
    *   allowing unordered args (using priorities to resolve arg type in case `enum` sets intersect)

Wrapping any command by `argrelay`:
*   naturally enables contextual auto-completion in Bash shell (see `Tab` hotkey below)
*   provides generic help and navigation (see `Alt+Shift+Q` hotkey below)

<a name="argrelay-general-problem"></a>
# General problem

| GUI                                                                         | CLI                                        |
|-----------------------------------------------------------------------------|--------------------------------------------|
| :heavy_minus_sign: prohibitively time-consuming for an ad-hoc functionality | :heavy_plus_sign: quick dev option         |
| :heavy_minus_sign: uses APIs but hardly exposes API to integrate itself     | :heavy_plus_sign: essential script-ability |
| :heavy_minus_sign: limits system access (a layer behind a narrow API)       | :heavy_plus_sign: ultimate control         |
| :heavy_plus_sign: intuitive data lookup                                     | :heavy_minus_sign:                         |

While retaining advantages of a CLI tool, `argrelay` tries to provide solution for intuitive data lookup.

Selecting args directly in shell avoids error-prone coping-and-pasting and clumsy window switching.

<a name="argrelay-original-use-case"></a>
# Original use case

Auto-complete [based on arbitrary data sets][later_stack_question] (e.g. config or ref data)<br/>
**directly from standard shell** to run infra commands.

Flexible and [responsive lookup][completion_perf_notes.md] requires data indexing<br/>
(e.g. the client has to start and query relevant data on each Tab-request)<br/>
suggesting...

<a name="argrelay-client-server"></a>
# Straightforward split: client & server

The performance is achieved by running a standby server pre-loaded with data<br/>
(instead of loading this data into each client).
> For example, with several thousands of data entries,<br/>
> even if someone could generate Bash completion config,<br/>
> it would take considerable time to load it for every shell instance.

Unlike static|generated|offline index per client, standby server also naturally supports dynamic data updates.

<!--
<a name="argrelay-accidental-use-case"></a>
### Accidental use cases

Familiar terminal with:
*   data-intensive CLI and seamless search through live data
*   minimalistic enum-based query syntax
*   catalogues of selectable functions with unified/redefined CLI
-->

<a name="argrelay-request-hotkeys"></a>
# Request hotkeys

| Bash:             | Server:                            | Client:                                   |
|-------------------|:-----------------------------------|:------------------------------------------|
| **`Alt+Shift+Q`** | reports existing and missing input | displays command completion status        |
| **`Tab`**         | suggests options for missing input | lists options to Bash for auto-completion |
| **`Enter`**       | provides data to invoke a command  | executes the command                      |

<a name="argrelay-name"></a>
# What's in a name?

CLI for any program is wrapped by `argrelay` interaction and invoked by the user indirectly.

Eventually, `argrelay` "relays" command line args (hence, the name)<br/>
with associated data around to invoke the program selected by the user:

```mermaid
sequenceDiagram
    autonumber
    participant P as Any program:<br/>user-required<br/>client-side-local
    actor U as <br/>User
    box transparent <br/>argrelay
    participant C as Client
    participant S as Server
    end
    U ->> C: invoke via shell<br/>on hotkeys
    activate C
    C ->> S: "relay" all args
    activate S
    S ->> C: "relay" enriched lookup details
    deactivate S
    C ->> P: "relay" details to invoke
    deactivate C
    activate P
    P ->> U: show results
    deactivate P
```

<a name="argrelay-demo"></a>
# Interactive demo

This is a non-intrusive demo (e.g. without permanent changes to `~/.bashrc`).

Clone this repo somewhere (`@/` is [the project root][FS_29_54_67_86.dir_structure.md]).

Start `@/exe/relay_demo.bash` (it may take a couple of minutes to start for the first time):

```sh
./exe/relay_demo.bash
```

This sub-shell configures request hot keys to bind `relay_demo` command with `@/bin/run_argrelay_client`:

*   Interact with `relay_demo` command (which uses [demo test data][TD_63_37_05_36.demo_services_data.md]):

    ```sh
    relay_demo goto                 # press `Alt+Shift+Q` to describe available options
    ```

    ```sh
    relay_demo goto host            # press `Tab` one or multiple times
    ```

    ```sh
    relay_demo goto host dev        # press Alt+Shift+Q to observe changes in the output
    ```

*   To clean up, exit the sub-shell:

    ```sh
    exit
    ```

# Behind the demo

*   While inside the sub-shell, inspect how auto-completion is configured for `relay_demo`:

    ```sh
    complete -p relay_demo
    ```

*   See `@/logs/relay_demo.bash.log` of the background server:

    ```sh
    less ./logs/relay_demo.bash.log
    ```

*   Inspect configs:

    *   `@/conf/argrelay.server.yaml`
    *   `@/conf/argrelay.client.json`

*   To reset the demo, remove `@/conf`:

    ```sh
    rm conf
    ```

    Script `@/exe/relay_demo.bash` relies on `@/conf` being a symlink specifically to `@/dst/relay_demo`:

    If `@/conf` is absent, it re-creates the symlink with that destination and re-installs everything.

*   To debug shell scripts, export `ARGRELAY_DEBUG` with value containing `s`:

    ```sh
    export ARGRELAY_DEBUG="s"
    ./exe/relay_demo.bash
    ```

<a name="argrelay-includes"></a>
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
*   **Bootstrap** process to init the environment and maintain it.
*   **Demo** example to start from.
*   **Testing** support and coverage.

<a name="argrelay-focus"></a>
# Focus: CLI search and data-assisted completion

GUI-s are secondary for `argrelay`'s niche because<br/>
GUI-s do not have the restrictions CLI-s have:
*   Technically, the server can handle requests from anywhere (GUI).
*   But primary API-s are feature-tailored to support CLI (because everyone does GUI).

<details>
<summary>show example</summary>
For example, in GUI-s, typing a query into a search bar may easily be accompanied by<br/>
(1) a separate (from the search bar) window area<br/>
(2) with individually selectable<br/>
(3) full-text-search results<br/>
(4) populated **async-ly** with typing.<br/>

In CLI-s, `grep` does (3) full-text-search, but slow and what about the rest (1), (2), (4)?

To facilitate selection of results,<br/>
catalogue-like navigation via structured search (rather than full-text-search) with auto-completion<br/>
seems the answer.
</details>

Nevertheless, GUI can also benefit from minimalist single line structured search queries.

<!-- TODO: update the doc first before publishing its link
Learn more about [how search works][how_search_works.md].
-->

<a name="argrelay-backend"></a>
# Data backend

There are two options at the moment - both using [MongoDB][MongoDB] API:

| Category       | `mongomock` (default)                                                                | `pymongo`                                                                                        |
|:---------------|:-------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|
| Data set size: | practical convenience limit ~ 10K objects                                            | tested with ~ 1M objects                                                                         |
| Pro:           | nothing else to install                                                              | no practical data set size limit found (yet)<br/> for `argrelay` intended use cases              |
| Con:           | understandably, does not meet<br/> performance requirements<br/> for large data sets | require some knowledge of MongoDB,<br/> additional setup,<br/> additional running processes<br/> |

Quantitative comparison tables between the two can be seen in docstring for `DistinctValuesQuery` enum.

`pymongo` connects to a running MongoDB instance which has to be configured in<br/>
`argrelay.server.yaml` under `mongo_config` and `mongomock` should be disabled:

```diff
-    use_mongomock: True
+    use_mongomock: False
```

<a name="argrelay-full-picture"></a>
# Full picture

```mermaid
sequenceDiagram
    autonumber
    actor U as <br/>User
    participant B as Bash
    participant P as Any program:<br/>user-required<br/>client-side-local
    box transparent <br/>argrelay
    participant C as Client
    participant S as Server
    participant DB as Data backend<br/>(internal or external)
    end
    participant DS as Data sources
    DS ->> S: load data
    activate S
    S ->> DB: load data
    deactivate S
    Note over S: <br/>stand-by<br/>
    U ->> B: enter command and use hotkeys
    B ->> C: invoke
    activate C
    C ->> S: "relay" all args
    activate S
    S ->> DB: query request
    activate DB
    DB ->> S: query result
    deactivate DB
    S ->> C: "relay" enriched lookup details
    deactivate S
    Note over C: next steps depend on hotkeys
    C ->> U: show results
    C ->> P: "relay" details to invoke
    deactivate C
    activate P
    P ->> U: show results
    deactivate P
```

<a name="argrelay-feedback"></a>
# Feedback

Feel free to [raise issues][repo_issues] for:
*   **any** questions (due to missing docs)
*   bugs
*   features

<!-- refs ---------------------------------------------------------------------------------------------------------- -->

[completion_perf_notes.md]: docs/dev_notes/completion_perf_notes.md
[MongoDB]: https://www.mongodb.com/
[TD_63_37_05_36.demo_services_data.md]: docs/test_data/TD_63_37_05_36.demo_services_data.md
[how_search_works.md]: docs/dev_notes/how_search_works.md
[repo_issues]: https://github.com/argrelay/argrelay/issues
[FS_29_54_67_86.dir_structure.md]: docs/feature_stories/FS_29_54_67_86.dir_structure.md
[later_stack_question]: https://softwarerecs.stackexchange.com/questions/85247/
