
To use `semver`, there should be a definition of braking interface change (to release `X+1.Y.Z`).

For `argrelay`, there are multiple interfaces:
*   user interface (expected behaviour)
*   internal plugin interfaces
*   config schema
*   client-server REST interface
*   filesystem structure
*   shell scripts (env vars and source-able funcs)

This is a very wide interface surface to track for a single package.

As `semver` suggests, there is no guarantee of compatibility for all `0.Y.Z` versions of `argrelay`
(until `1.0.0` is released) - version numbers are changed discretionarily:
*   "important" changes increment `0.Y+1.Z`
*   others (less "important") increment `0.Y.Z+1`

TODO_78_94_31_68: Split argrelay into multiple packages.
This will make it simpler to track compatibilities if each interface is represented by a package with its definition:
*   each package is smaller to track incompatible interface changes
*   major version increase in one such interface dependency will cause increase of parent package major version

See also [version format][version_format.md].

[version_format.md]: version_format.md
