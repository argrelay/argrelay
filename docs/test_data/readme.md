This is a dir with explanation for test data sets,
referenced by `test_data`'s id,
abbreviated as `TD`.

Each `test_data` set has its own id to
find them in related places in files
(to bind these places all together).

This helps to highlight a special purpose of some data and avoid
inadvertently changing it making a test invalid.

The format of the `test_data` id is:

```
TD_NN_NN_NN_NN
```

*   `TD`: prefix as is
*   `NN_NN_NN_NN`: random numbers

It can be followed by ignorable mnemonic keywords, for example:

```
TD_70_69_38_46 # no data
```
