
The procedure is manual at the moment (not run by some specific CI platform).

The details are automated/ensured via `@/exe/publish_package.bash` script.

Just run and address any errors:

```sh
./exe/publish_package.bash
```

# The meaning of version

There is no way to publish artifacts on pypi.org with the same version twice.<br/>
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

The meaning of version:
*   is **not** what is written in `setup.py`
*   is what package that version on pypi.org points to

In other words, until package of that version is published on pypi.org,<br/>
there is no such version (no matter what `setup.py` says).<br/>
And if `setup.py` indicates some version,<br/>
it does not mean it corresponds to the version published on pypi.org.

See also [version_format.md][version_format.md].

# Ensuring Git tag points to the version on pypi.org

Non-`dev` releases can only be done from the `main` branch - the commit must already exist there.

This means the version will appear earlier in `setup.py` on the `main` branch<br/>
than corresponding version of the package on pypi.org.

The same version may exist in `setup.py` on `main` branch across multiple commits<br/>
until single Git tag marks one of them the moment when package is published to pypi.org.<br/>
Script `@/exe/publish_package.bash` ensures that Git tag corresponds to pypi.org-published version.

[version_format.md]: version_format.md
