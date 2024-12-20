

<!--

# Features

For sizeable and inter-dependent data, need for perf, relaxed syntax, keyword search, try [`argrelay`][argrelay_org].

*   Single server API for all commands.

    Commands behave differently because of the command line interpretation, local logic, and server data,<br/>
    not by extending server API.

*   Command execution is still trivially local to shell.

    The client only fetches more data from the server based on command line args before passing control to user code.

*   All security (auth and authz) to execute command must also be resolved by local process (just like for any script).

*   Precise structured search.

    It may appear fuzzy due to relaxed args order - but any ambiguity is resolved via simple rules of priority.

*   Support for any number of custom command names.

*   Support for any number of custom functions (registered).

    Functions are bound to any command name and args combination.

-->

<a name="argrelay-focus"></a>

# Project focus

> Data-assisted CLI with search and completion

GUI-s are targeted secondarily as they not have the restrictions vs the benefits CLI-s have:
*   To leverage minimal syntax queries, API requests can be handled from anything (including GUI).
*   But API-s are purposefully feature-tailored to support (both challenging and rewarding) CLI peculiarities.

<details>

<summary>show example</summary>

For example, in GUI-s, typing a query into a search bar may easily be accompanied by<br/>
[1] a separate (from the search bar) window area<br/>
[2] with individually selectable<br/>
[3] full-text-search results<br/>
[4] populated async-ly with typing...<br/>

In CLI-s, `grep` does [3] full-text-search,<br/>
but it is slow and completely misses the rest [1], [2], [4].

Also, simple full-text-search is imprecise - facilitating selection in CLI works best with:<br/>
a catalogue-like navigation selecting keywords via structured data search with auto-completion.

</details>

<!-- TODO: update the doc first before publishing its link
Learn more about [how search works][how_search_works.md].
-->

<!--

<a name="argrelay-overview"></a>

# Interaction overview

User is interrogated for each next input arg based on server knowledge of:
*   custom command **input schema**
*   custom data which matches already given input on the command line

Each command resembles "enum language":
*   Tokens are tags | labels | keywords from one of the `enum` sets.
*   The `enum` sets are the objects property values within user data.
*   Fuzzy-search (yet easily predictable) is achieved by:
    *   relying on rare intersection between `enum` sets
    *   allowing unordered args (using priorities to resolve `prop_name` in case `enum` sets intersect)

Wrapping any command by `argrelay`:
*   provides generic help and navigation (see `Alt+Shift+Q` hotkey below)
*   naturally enables contextual auto-completion in Bash shell (see `Tab` hotkey below)
*   reduces cognitive load with minimalistic enum-based query syntax (matching target executable command line)
*   maintains small client-side footprint (suitable for resource-constrained terminals)
*   exposes conveniently browsable data inventory (generic CLI builder)

-->

<a name="argrelay-general-dilemma"></a>

# General dilemma

Neither GUI nor CLI will ever go way:

| GUI                                                                           | CLI                                                       |
|-------------------------------------------------------------------------------|-----------------------------------------------------------|
| :heavy_plus_sign: diagrams, images, video                                     | :heavy_multiplication_x: only via integration with GUI    |
| :heavy_minus_sign: might be time-consuming for an ad-hoc functionality        | :heavy_plus_sign: always quick dev option (low ceremony)  |
| :heavy_minus_sign: may not exist early in feature development                 | :heavy_plus_sign: likely available early in development   |
| :heavy_minus_sign: error is a pop-up requiring human attendance               | :heavy_plus_sign: error is an error code = ubiquitous API |
| :heavy_minus_sign: no simple way to store and share GUI output                | :heavy_plus_sign: store and share results as **text**     |
| :heavy_minus_sign: repeat steps 500 times? give up!                           | :heavy_plus_sign: repeat steps 500 time? loop!            |
| :heavy_minus_sign: no universal way to reproduce (composite) GUI actions      | :heavy_plus_sign: paste and "replay" commands as **text** |
| :heavy_minus_sign: no universal way to search stored GUI output               | :heavy_plus_sign: `grep`-search results as **text**       |
| :heavy_minus_sign: no universal way to compare GUI output                     | :heavy_plus_sign: `diff`-compare results as **text**      |
| :heavy_minus_sign: no universal way to auto-trigger GUI actions on events     | :heavy_plus_sign: hook commands anyhow (e.g. schedule)    |
| :heavy_minus_sign: a separate stack (skill set) from backend to contribute to | :heavy_plus_sign: familiarly dominates backend tools      |
| :heavy_minus_sign: uses APIs but hardly exposes API to integrate itself       | :heavy_plus_sign: inherent script-ability                 |
| :heavy_minus_sign: limits system access (a layer behind a narrow API)         | :heavy_plus_sign: ultimate control                        |
| :heavy_plus_sign: keyword captions                                            | :heavy_minus_sign: hardly remembered cryptic `-o` options |
| :heavy_plus_sign: point-click actions                                         | :heavy_minus_sign: increased typing:exclamation:          |
| :heavy_plus_sign: intuitive data-driven human interface                       | :heavy_minus_sign: human interface:question: API, in fact |

To resolve this dilemma, while retaining advantages of a CLI tool,<br/>
`argrelay` compensates for those last :heavy_plus_sign:-s by:
*   intuitive data-driven interface
*   reduced typing (args auto-reduction)
*   keyword options (args auto-completion)

<a name="argrelay-alternatives"></a>

# In search for alternatives

As opposed to GUI-demanding approaches like [Warp][Warp_site] or [IDEA terminal][IDEA_terminal]<br/>
(in desktop environment where any tool competes for installation),<br/>
`argrelay` is slim and survives everywhere in basic text modes (over telnet or SSH).

Also, none of these desktop tools allow building commands with custom input spec -<br/>
they simply augment interaction, in fact, they complement `argrelay` (as they may work together).

Alternatively, unlike this `argrelay` framework, independent [`argcomplete`][argcomplete_github] library:
*   :heavy_plus_sign: queries args directly from the source
*   :heavy_minus_sign: supports only `Tab`-completion
*   :heavy_minus_sign: does not search data inline
*   :heavy_minus_sign: does not provide feedback on input interrogation status
*   :heavy_minus_sign: does not eliminate irrelevant args
*   :heavy_minus_sign: uses stringent CLI syntax
*   :heavy_minus_sign: suffers performance limitations (no specialized data index)

<a name="argrelay-productivity"></a>

# Dev productivity

Given that `argrelay` target audience are devs (using shell),<br/>
the advantages of CLI tools over GUI can be summarized aspect-by-aspect:

| aspect          | :heavy_minus_sign: GUI | :heavy_plus_sign: CLI |
|-----------------|------------------------|-----------------------|
| **output**      | image                  | text                  |
| **interaction** | manual                 | automate-able         |
| **design**      | heavy                  | light                 |
| **languages**   | exclusive              | inclusive             |
| **integration** | denying                | composable            |
| **cycle**       | days                   | hours                 |
| **reviewers**   | many                   | few                   |
| **team**        | another                | same                  |
| **users**       | anyone                 | devs                  |
| **resources**   | max                    | min                   |

<a name="argrelay-original-use-case"></a>

# Original use case

It aimed at command auto-completion [based on arbitrary data sets][later_stack_question],<br/>
for example, using metadata for 10s x clusters, 100s x hosts, 1000s x processes, ...<br/>
(over 15K objects in total) **directly from the standard shell**.

Selecting args directly in shell CLI avoids **otherwise** error-prone<br/>
coping-and-pasting via clumsy GUI window switching.

Flexible and [responsive lookup][completion_perf_notes.md] required data indexing<br/>
(e.g. each Tab-request demands short loading and querying time for context-specific data)<br/>
which suggested a server...

<a name="argrelay-client-server"></a>

# Design choice: client-server vs static rules

The performance qualities are achieved by running a standby server with pre-loaded data<br/>
(instead of loading this data into each client).
> For example, with 1000s of data entries,<br/>
> even if someone could generate static Bash completion rules,<br/>
> it would take considerable time to load them for every shell instance.

Unlike static | generated | offline index per client,<br/>
standby server also naturally supports dynamic data updates.

<!-- links --------------------------------------------------------------------------------------------------------- -->

[argrelay_org]: https://argrelay.org/
[Warp_site]: https://warp.dev/
[IDEA_terminal]: https://www.jetbrains.com/help/idea/terminal-emulator.html
[argcomplete_github]: https://github.com/kislyuk/argcomplete
[completion_perf_notes.md]: docs/dev_notes/completion_perf_notes.md
[how_search_works.md]: docs/dev_notes/how_search_works.md
[later_stack_question]: https://softwarerecs.stackexchange.com/questions/85247/
