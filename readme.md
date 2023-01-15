
Project status: prototype

# What's this?

An integration framework to provide contextual Tab-auto-completion for command line interfaces (CLI) in Bash shell.

The original use case is to make auto-completion based on large (config) data sets.

This requires data indexing for responsive lookup (the client has to start and find relevant data on each Tab-request).

The straightforward approach to meet performance requirements taken by `argrelay` is to run a standby data server.

# What's in a name?

Eventually, `argrelay` will "relay" (hence, the name) command line arguments to user domain-specific command/procedure.

To clarify, `argrelay` _framework_ can be compared with (independent) `argparse` _library_:

| Category        | `argparse` is a library                            | `argrelay` is a framework                                           |
|:----------------|:---------------------------------------------------|:--------------------------------------------------------------------|
| Given:          | `A.py` is some script                              | `A_relay` is a command configured in Bash to call `argrelay` client |
| In Bash:        | type `A.py` to execute it                          | type `A_relay` to let `argrelay` decide whether to execute `A.py`   |
| Execution flow: | `A.py` calls `argparse` library                    | `A.py` is called by the framework when `A_relay` is invoked         |
| Function:       | `A.py` directly does some domain-specific task     | `A_relay` directly only "relays" the command line to `argrelay`     |
| CLI source:     | `A.py` defines its CLI itself via `argparse`       | CLI for `A_relay` is defined by the framework via configs/plugins   |
| To modify CLI:  | modify `A.py`                                      | keep `A.py` intact, re-configure `argrelay` instead                 |
| Prog language:  | `A.py` has to be a Python script to use `argparse` | `A.py` can be anything somehow executable by `argrelay`             |

# What's missing?

*   Any (real) domain-specific data
*   Any (useful) domain-specific plugins

# What's in the package?

*   **Client** to be invoked by Bash hook on every Tab to send command line arguments to the server.
*   **Server** to parse command line and propose values from pre-loaded data for the argument under the cursor.
*   **Plugins** to customize:
    *   actions the client can run
    *   objects the server can search
    *   grammar the command line can have
*   **Interfaces** to bind these all together.
*   **Demo** plugins to show an example.

# CLI-friendly completion: primary focus

GUI-s are secondary for `argrelay`'s niche because they do not have the restrictions that CLI-s have:
*   Technically, the server can handle requests for any GUI.
*   But API-s are primarily tailored to support CLI.

# Syntax: origin story

When an interface is limited...

You probably heard about research when apes were taught to communicate with humans in sign language
(their vocal apparatus cannot reproduce speech effectively).

Naturally, with limited vocabulary, they combined known words to describe unnamed things.

For example, to ask for a watermelon (without knowing the exact sign), they used combination of known "drink" + "sweet".

### Narrow down options

Without context, just two words "drink" + "sweet" leave a lot of ambiguity to guess a watermelon (many sweet drinks).

A more clarified "sentence" could be:
> drink round red sweet fruit

Each word narrows down matching object set to more specific candidates (including watermelon).

### Avoid strict order

Notice that the word order is not important - this line provides equivalent hints to guess the same thing:
> round sweet fruit red drink

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

### Address any object

Suppose enums are binary = having only two values (cardinality = 2: black/white, hot/cold, true/false, ...).

5 words could slice the object space and single out (identify exactly one) up to 2^5 = 32 objects.

To "address" larger object spaces, larger enum cardinalities or more word places are required.

*   Each enum type = a dimension.
*   Each specific enum value = a coordinate.
*   Each object fills a slot in this multi-dimensional discrete space.

### Apply to CLI

CLI-s are used to write commands - imperative sentences: specific actions on specific objects.

The "enum language" above covers searching/specifying both an action and any object it requires.

### Suggest contextually

Not every combination of enum values may point to an existing object.

For data with sparse object spaces, the CLI-suggestion should be limited by coordinates applicable to existing objects.

### Differentiate on purpose

All above may be an obvious approach to come up with, but it is not ordinary for CLI-s of most common commands:

| Common commands (think `ls`, `git`, `ssh`, ...):                             | `argrelay`-wrapped actions                        |
|:-----------------------------------------------------------------------------|:--------------------------------------------------|
| have succinct syntax and prefer single-char switches (defined by code)       | prefer explicit "enum language" defined by data   |
| rely on a human to memorize syntax (options, ordering, etc.)                 | assume a human have a loose idea about the syntax |
| auto-complete for objects known to the operating system (hosts, files, etc.) | auto-complete from a domain-specific index        |

The default `argrelay` parsing and CLI-interpretation plugin (see `GenericInterp`) implies to such syntax.

# Quick demo

To start both the server and the client, two terminal windows are required.

*   Server:

    Start the first sub-shell:

    ```sh
    ./dev-shell.bash
    ```

    In this sub-shell, start the server:

    ```sh
    # in server `dev-shell.bash`:
    python -m argrelay.relay_server
    ```

*   Client:

    Start the second sub-shell:

    ```sh
    ./dev-shell.bash
    ```

    While it is running (temporarily), this sub-shell is configured with completion for `relay_demo` command.

*   Try to complete command `relay_demo`:

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

    *   client config: `~/.argrelay.client.yaml`
    *   server config: `~/.argrelay.server.yaml`

*   To clean up, exit the sub-shells:

    ```sh
    # in client or server `dev-shell.bash`:
    exit
    ```
