
# Version format

See also [semver notes][semver_notes.md].

The format is according to PEP440 (which conflicts with `semver` - see below):

| release type | Python / `setup.py` | Git tag        |
|--------------|---------------------|----------------|
| `dev`        | `X.Y.Z.devN`        | `vX.Y.Z.devN`  |
| `final`      | `X.Y.Z`             | `vX.Y.Z.final` |

#  `final`-release

A `final`-release version `X.Y.Z` in Python (as in `setup.py`) follows `semver` spec.

It must be released from commits on the `main` branch<br/>
(which means `setup.py` has to be merged to the `main` branch with required version ahead of the publishing).

# `dev`-release

A `dev`-release version `X.Y.Z.devN` follows PEP440 but violates `semver`<br/>
(which requires it to be `X.Y.Z-devN` instead - see below).

This project allows `dev`-release version to be published off **any** commit<br/>
(even if this version uses commit that will never be tagged or visible on the `main` branch).

Technically, it means `X.Y.Z.devN` can be **anything** (unknown commit, unknown compatibility).

# Decision details: Python version format

According to `semver` version (rather than Git tag) should **not** contain prefix `v`:
https://github.com/semver/semver/blob/a4f21e1a6fdf7d1a78a2d965889d958f96b11b42/semver.md?plain=1#L329

Following approach of `semver` spec itself - version has no `v` refix:
https://github.com/semver/semver/blob/a4f21e1a6fdf7d1a78a2d965889d958f96b11b42/package.json#L3

While Git tag is prefixed with `v` (again following approach of `semver` spec itself):
https://github.com/semver/semver/releases/tag/v2.0.0

See also about pre-release versions to use hyphen `-` separator:
https://github.com/semver/semver/blob/a4f21e1a6fdf7d1a78a2d965889d958f96b11b42/semver.md?plain=1#L93

Note that `pkg_resources.get_distribution` replaces non-alphanum and non-dot chars with dot `.`<br/>
even in version (not just package names).<br/>
Therefore, version `0.0.0-dev.23` is problematic with Python:
https://stackoverflow.com/a/65678242/441652

Actually, PEP440 disagrees with `semver` - it only allows `*.devN`<br/>
(normalize everything else like `-`, `_`, or no char to `.`):
https://peps.python.org/pep-0440/

# Decision details: Git tag format

The problem with `vX.Y.Z.devN` Git tag is sorting.

Listing Git tags via `git tag` or sorting them via `sort -V`<br/>
places `vX.Y.Z.devN` tags  _after_ (later) those without (`vX.Y.Z`).

Tests showed that `pip` does not have such problem - it treats dev pre-releases with `*.devN` as older ones<br/>
(e.g. having both `0.2.0` and `0.2.0.dev1`, `pip` with `--pre` installs `0.2.0`, not `0.2.0.dev1`).

To align sorting with meaning (Git with Python), the `final`-release tag has to have a postfix<br/>
which is lexicographically later than any corresponding `vX.Y.Z.devN` leading to it - for example, `.final`:

```sh
( echo "v0.0.0.dev1" ; echo "v0.0.0.final" ; echo "v0.0.0.dev0" ) | sort -V
```

```
v0.0.0.dev0
v0.0.0.dev1
v0.0.0.final

```

# Decision summary

Since it is mostly a Python lang project:
*   use Git tag format `vX.Y.Z.devN` for `dev`-version `X.Y.Z.devN` in Python
*   use Git tag format `vX.Y.Z.final` for `final`-version `X.Y.Z` in Python

[semver_notes.md]: semver_notes.md
