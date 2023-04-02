
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

*   `release_tests`

    Separate category of tests which are okay to fail on branches
    (and it is okay not to run them to avoid the noise during development),
    but they will eventually need to pass before the release.

*   `ui_tests`

    Cypress tests for built-in UI - they are started manually and separately at the moment.
