
The procedure is rather manual at the moment (not run by some specific CI platform).

The details are automated/ensured via `publish-package.bash` script.

Just run and address any errors:

```sh
./publish-package.bash
```

TODO: There is no Git-tagged/versioned releases yet.

Until the very first release `0.0.0` (TODO),
all published versions are pre-releases `0.0.0.devN`.

There is no way to publish artifacts on pypi.org with the same version twice.
The version in the metadata of the package has to be updated - see `setup.py`:

```diff
 git diff -U1 setup.py
diff --git a/setup.py b/setup.py
index e984f6b..e7a1475 100644
--- a/setup.py
+++ b/setup.py
@@ -16,3 +16,3 @@ setuptools.setup(
     name = "argrelay",
-    version = "0.0.0.dev3",
+    version = "0.0.0.dev4",
     author = "uvsmtid",
```

