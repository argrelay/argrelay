
# Version format

See also [semver notes][semver_notes.md].

The format is according to PEP440 (which conflicts with `semver` - see below):

```
X.Y.Z.devN
```

Normal versions `X.Y.Z` follow `semver` spec - they are released from commits on the `main` branch.

Suffix `.devN` is pre-release (which `semver` requires to be `-devN` instead).<br/>
This project allows pre-release version to be published off any commit<br/>
(even if this version uses commit that will never be visible on the `main` branch).<br/>
Technically, it means `.devN` can be anything.

# Decision details

According to `semver` version (rather than Git tag) should not contain prefix `v`:
https://github.com/semver/semver/blob/a4f21e1a6fdf7d1a78a2d965889d958f96b11b42/semver.md?plain=1#L329

Following approach of `semver` spec itself - version has no `v` refix:
https://github.com/semver/semver/blob/a4f21e1a6fdf7d1a78a2d965889d958f96b11b42/package.json#L3

While Git tag is prefixed with `v` (again following approach of `semver` spec itself):
https://github.com/semver/semver/releases/tag/v2.0.0

See also about pre-release versions:
https://github.com/semver/semver/blob/a4f21e1a6fdf7d1a78a2d965889d958f96b11b42/semver.md?plain=1#L93

Note that `pkg_resources.get_distribution` replaces non-alphanum and non-dot chars with dot `.`<br/>
even in version (not just package names).<br/>
Therefore, version `0.0.0-dev.23` is problematic with Python:
https://stackoverflow.com/a/65678242/441652

Actually, PEP440 disagrees with `semver` - it only allows (normalize everything else like `-`, `_`, or no char to) `*.devN`:
https://peps.python.org/pep-0440/

The problem with `*.devN` is version sorting.<br/>
Listing Git tags via `git tag` or sorting them via `sort -V` places versions with `*.devN` _after_ (later) those without.<br/>
Tests showed that `pip` does not have such problem - it treats dev pre-releases with `*.devN` as older ones<br/>
(e.g. having both `0.2.0` and `0.2.0.dev1`, `pip` with `--pre` installs `0.2.0`, not `0.2.0.dev1`).<br/>
To align sorting with meaning, the final release tag has to have a postfix<br/>
which is lexicographically later than any `*.devN` leading to it - for example, `.final`:

```sh
( echo "v0.0.0.dev1" ; echo "v0.0.0.final" ; echo "v0.0.0.dev0" ) | sort -V
```

```
v0.0.0.dev0
v0.0.0.dev1
v0.0.0.final

```

# Decision summary

Since it is mostly a Python lang project, it should use Git tag format:
*   `vN.N.N.devN` for dev version `N.N.N.devN`
*   `vN.N.N.final` for final version `N.N.N`

[semver_notes.md]: semver_notes.md
