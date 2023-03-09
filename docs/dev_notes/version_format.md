
# Version format

See also [semver notes][semver_notes.md].

The format is according to PEP440 (which conflicts with `semver` - see below):

```
X.Y.Z.devN
```

Normal versions `X.Y.Z` follow `semver` spec - they are released from commits on the `main` branch.

Suffix `.devN` is pre-release (which `semver` requires to be `-devN` instead) and<br/>
is allowed to be published off any commit (even if this commit will never end up visible on the `main` branch).<br/>
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

Actually, PEP440 disagrees with `semver` - it only allows `*.devN`:
https://peps.python.org/pep-0440/

Since it is mostly a Python lang project, let's use `N.N.N[.devN]` format.

[semver_notes.md]: semver_notes.md
