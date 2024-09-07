
# TODO: Remove this file

This file tests whether broken links are verified by `pymarkdownlnt`.
This is the main feature needed to lint Markdown files:

*   link this way to [`TODO_this_file_does_not_exits.md`](TODO_this_file_does_not_exits.md).
*   or link this way to [`TODO_this_file_does_not_exits.md`][TODO_this_file_does_not_exits.md].

To test this (it should fail, but does not):

```sh
python -m pymarkdown scan docs/dev_notes/TODO_remove_this_file.md
```

See also:
*   link this way [`lint_markdown.md`](lint_markdown.md)
*   or link this way [`link_markdown.md`][lint_markdown.md]

[lint_markdown.md]: lint_markdown.md
[TODO_this_file_does_not_exits.md]: TODO_this_file_does_not_exits.md
