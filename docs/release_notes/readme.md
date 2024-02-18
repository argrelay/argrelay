
# TL;DR

Combine all release notes in chronological order to see them on command line:

```sh
tail -n +1 docs/release_notes/v0.*
```

# Release notes

These release notes are part of the Git history and can be updated retroactively because:
*   they do not update the immutable past, instead, they clarify it
*   all their updates are part of the immutable past as well and cannot accidentally erase anything

It does not make sense to use Git commit messages to auto-generate release notes because:
*   they do not summarize highlights
*   they are immutable and cannot be corrected (if incomplete or misleading)

# File format

Each release note should have its own file named based on the Git tag:

```sh
${git_tag}.md
```

But it is not required for every tag to have a release note file.

# Combined release notes for multiple releases

There is no files with combined release notes (e.g. everything for Git tags `v0.*`).

To combine multiple release notes, use scripts, for example:

```sh
tail -n +1 docs/release_notes/v0.*
```

This is enough because lexicographical sort for Git tag format matches the release order
(see [`version_format.md`][version_format.md] for details).

[version_format.md]: ../dev_notes/version_format.md

