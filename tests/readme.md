
TODO: TODO_04_84_79_11: Update/change categories to include:
*   split `offline_tests`:
    *   in_process_tests - tests which do not start other processes to communicate with
    *   local_tests - tests which may start other processes to communicate with (potentially occupying port numbers)
*   redefine `online_tests` - these must be only those which connect to services outside of those controlled by the test code
*   split `online_tests` into:
    *   `internet_tests` (required services in the world)
    *   `intranet_tests` (requiring services in the org)
    *   `local_tests` (see splitting `offline_tests`) running on the same machine.

All tests for `argrelay` are integration at different degree
(thin ~ single function or thick ~ almost entire client-side and server-side code).

The only useful practical difference between them are these directories:

*   `offline_tests`

    Tests which use only offline resources e.g. files (except package downloads by `pip`, `tox`, etc.).

    They are expected to run during build process in continuous integration.

*   `online_tests`

    Tests which use network resources (e.g. internet services, databases, etc.).

    They are not supposed to run during build process,
    but could be easily run in some environments without steps to set them up.

*   `env_tests`

    Similar to `online_tests`, but these tests require special setup and normally run on demand
    (rely on some running service, need some files, etc.).

    They are in a separate directory (excluded from running automatically) instead of `@skip`-ping them.

    This dir is the only one where `__init__.py` is absent -
    tests there are not discoverable if started from root `tests` dir.

*   `slow_tests`

    Same as `offline_tests`, but run longer and not that important for quick feedback cycles.

*   `release_tests`

    Separate category of tests which are okay to fail on branches
    (and it is okay not to run them to avoid the noise during development),
    but they will eventually need to pass before the release.

*   `gui_tests`

    Cypress tests for built-in GUI - they are started manually and separately at the moment.

See also `FS_66_17_43_42.test_infra.md`.
