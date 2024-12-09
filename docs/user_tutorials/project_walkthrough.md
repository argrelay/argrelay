
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

<!-- links --------------------------------------------------------------------------------------------------------- -->

[interactive_demo]: ../../readme.md#argrelay-demo
