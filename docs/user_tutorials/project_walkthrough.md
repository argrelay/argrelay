
This tutorial accumulates pointers to places within the repo or<br/>
deployed instance describing their purposes.

# Beyond the demo

Start with the ["interactive demo"][interactive_demo] from the main readme.

*   While inside the sub-shell, inspect how auto-completion is configured for `relay_demo`:

    ```sh
    complete -p lay
    ```

*   See `@/logs/relay_demo.bash.log` of the background server:

    ```sh
    less ./logs/relay_demo.bash.log
    ```

*   Inspect configs:

    *   `@/conf/argrelay_client.json`
    *   `@/conf/argrelay_server.yaml`
    *   `@/conf/argrelay_plugin.yaml`

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

# What is in the package?

<!--
    TODO: add links to separate docs for each of the points
--->

At the moment, `argrelay` is still bundled into single Python package:

*   **Client** to be invoked by Bash hook on every Tab to<br/>
    send command line arguments to the server.
*   **Server** to parse command line and propose values from<br/>
    pre-loaded data for the argument under the cursor.
*   **Plugins** to customize:
    *   actions the client can run
    *   objects the server can search
    *   grammar the command line can have
*   **Interfaces** and schemas to bind these all together.
*   **Bootstrap** process to init the environment and maintain it.
*   **Demo** example to start from.
*   **Testing** support and coverage.
*   **Documentation** to explain things and capture decisions made.

<!-- links --------------------------------------------------------------------------------------------------------- -->

[interactive_demo]: ../../readme.md#argrelay-demo
