
These are environment variables used by `argrelay`:

*   `ARGRELAY_DEBUG` used to enable debug output - see `RequestContext.is_debug_enabled`.

*   `ARGRELAY_DEV_SHELL` used while running `@/exe/dev_shell.bash`, for example, to run some tests conditionally.

*   `ARGRELAY_BOOTSTRAP_DEV_ENV` used while running `@/exe/bootstrap_dev_env.bash`, for example, to run some tests conditionally.

*   `ARGRELAY_CONF_BASE_DIR` specifies base dir for all config files (default ~ = user home).

    See also `FS_16_07_78_84.conf_dir_priority.md`.
