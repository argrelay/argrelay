This is a dir with feature stories,
referenced by `feature_story`'s id,
abbreviated as `FS`.

Each `feature_story` has its own id to
find them in related places in files
(to bind these places all together).

This helps to highlight a strong relationship of some data | code to a specific feature.

The format of the `feature_story` id is:

``
FS_NN_NN_NN_NN
```

*   `FS`: prefix as is
*   `NN_NN_NN_NN`: random numbers

It can be followed by ignorable mnemonic keywords, for example:

```
FS_53_81_66_18 # TnC
```

There are several `feature_status`-es:
*   `TBD`: not clear yet whether useful or adequate - to be discussed.
*   `TODO`: clear how it should work, but not implemented.
*   `TEST`: implemented and seems working - cover by tests.
*   `DONE`: all good, maintain.
