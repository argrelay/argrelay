This is a dir with test data,
abbreviated as `TD`,
referenced as `test_data`.

It is supposed to define reference ids to
find them in related places in source files
(to bind these places all together).

This highlights a special purpose of some data | code and helps to avoid
inadvertently changing them breaking the test.

The format of the test data id is:

```
TD-YYYY-MM-DD--N
```

*   `TD`: prefix as is
*   `YYYY-MM-DD`: date of creation
*   `N`: ordinal number (within `YYYY-MM-DD`)

For example:

```
TD-2023-01-07--1
```

