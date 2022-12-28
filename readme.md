
TODO: project description.

## Quick demo

To start both the server and the client, 2 terminal windows are required.

*   Server:

    Start first sub-shell:

    ```sh
    ./dev-shell.bash
    ```

    In this sub-shell, start the server:

    ```sh
    python -m argrelay.relay_server
    ```

    FYI: server config: `~/.argrelay.server.yaml`

*   Client:

    Start second sub-shell:

    ```sh
    ./dev-shell.bash
    ```

    This sub-shell is already configured with completion for `relay_demo` command (temporarily) while it is running.

    FYI: client config: `~/.argrelay.client.yaml`

*   Try to complete command `relay_demo`:

    ```sh
    relay_demo prod         # press Tab one or multiple times
    ```

    ```sh
    relay_demo prod ro      # press Alt+Shift+Q shortcut to describe command line args
    ```

*   To clean up, exit sub-shells:

    ```sh
    exit
    ```
