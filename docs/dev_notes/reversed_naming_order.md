
This describes naming approach used throughout `argrelay` sources.

Principle:
reorder words in identifiers if it helps grouping relevant components via sorting.

For example,
these two modules will appear grouped together
(when sorted lexicographically in IDEs) due to common prefix:
*   `client_command_local`
*   `client_command_remote`

Naming them "in English" will break the grouping
as there is no common prefix anymore:
*   `local_client_command`
*   [something in between]
*   `remote_client_command`

After all, the three keywords (`local` | `remote`, `command`, `client`)
are present in any of the naming style and
there is no ambiguity in meaning.

For another example, see hierarchy of plugins where ordering of keywords embedded in
the names reflects inheritance which sorts list of classes in IDE as they all have common prefix.
