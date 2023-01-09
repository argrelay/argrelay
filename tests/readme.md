
All tests for `argrelay` are integration at different degree
(thin ~ single function or thick ~ almost entire client-side and server-side code).

The only useful practical difference between them are these directories:

*   `offline_tests`

    Tests which use only offline resources e.g. files (except package downloads by `pip`, `tox`, etc.).

    They are expected to run during build process in continuous integration.

*   `online_tests`

    Tests which use network resources (e.g. internet services, databases, etc.).

    They are not supposed to run during build process, but could be run in some environments.

*   `env_tests`

    Similar to `online_tests`, these tests require special setup and normally run on demand
    (rely on some running service, need some files, etc.).

    They are in separate directory (excluded from running automatically) instead of `@skip`-ping them.
