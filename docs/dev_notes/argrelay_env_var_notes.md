
These are environment variables used by `argrelay`:

*   `ARGRELAY_DEBUG` used to enable debug output - see `RequestContext.is_debug_enabled`.

*   `ARGRELAY_DEV_SHELL` used in dev env to run some tests conditionally.

*   `ARGRELAY_CONF_BASE_DIR` specifies base dir for all config files (default ~ = user home).

    If `ARGRELAY_CONF_BASE_DIR` is defined, config files will be looked up in:

    ```sh
    ls ${ARGRELAY_CONF_BASE_DIR}/.argrelay.conf.d/argrelay.server.yaml
    ls ${ARGRELAY_CONF_BASE_DIR}/.argrelay.conf.d/argrelay.client.json
    ```
