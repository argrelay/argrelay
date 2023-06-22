
This procedure describes using [`FS_85_33_46_53.bootstrap_dev_env.md`][FS_85_33_46_53.bootstrap_dev_env.md] feature
to upgrade existing `argrelay`-based project.

If the project is created from scratch, see [`bootstrap_procedure.initial_setup.md`][bootstrap_procedure.initial_setup.md] instead.

# Subsequent `argrelay` upgrade

Run `@/exe/dev_shell.bash` to activate `venv`:

```sh
./exe/dev_shell.bash
```

Upgrade `argrelay` package to newer version:

```sh
pip install --upgrade --force-reinstall argrelay
```

Re-run `@/exe/bootstrap_dev_env.bash`:

``sh
./exe/bootstrap_dev_env.bash
``

To see how it works after upgrade, try [`FS_58_61_77_69.dev_shell.md`][FS_58_61_77_69.dev_shell.md].

# Project customization

Most of the upgrade details are specific to project customization -<br/>
they depend on custom plugins (see `plugin_development.md`) and may require extra steps.

To run real Mongo DB (instead of `mongomock`), see also `mongo_notes.md`.

[bootstrap_procedure.initial_setup.md]: bootstrap_procedure.initial_setup.md
[FS_58_61_77_69.dev_shell.md]: ../feature_stories/FS_58_61_77_69.dev_shell.md
