
Until the very first release `0.0.0` (TODO),
all published versions are pre-releases `0.0.0.devN`.

There is no Git-tagged/versioned releases yet.

Nevertheless, to publish, the version in the metadata of the package
still has to be changed:

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

The procedure is manual at the moment.

It is simpler to run all the steps below inside `./dev-shell.sh`.

Next, minimally, ensure that `tox` runs successfully:

```sh
tox
```

Also, snapshot current dev env packages:

```sh
pip freeze > requirements.txt
```

Apparently, `tox` builds `sdist`, for example:

```
./.tox/.pkg/dist/argrelay-0.0.0.dev3.tar.gz
```

TODO: Is there a way to make `tox` publish the package?

Instead, following majority of Inet sources, the steps to publish are these:

```sh
python setup.py sdist
```

```sh
pip install twine
```

```sh
twine upload dist/*
```

