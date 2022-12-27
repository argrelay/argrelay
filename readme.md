
TODO: project description.

## Quick start

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

    This sub-shell is already configured with completion for `try_relay` command (temporarily) while it is running.

    FYI: client config: `~/.argrelay.client.yaml`

*   Try to complete command `try_relay`:

    ```sh
    try_relay prod        # press Tab one or multiple times
    ```

    ```sh
    try_relay prod ro     # press keyboard shortcut (if configured correctly in `dev-shell.bash`)
    ```

*   To clean up, exit sub-shells:

    ```sh
    exit
    ```
