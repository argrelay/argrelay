
This procedure describes using [`FS_85_33_46_53.bootstrap_dev_env.md`][FS_85_33_46_53.bootstrap_dev_env.md] feature for step 3:
1.  project creation from scratch: [`bootstrap_procedure.1.project_creation.md`][bootstrap_procedure.1.project_creation.md]
2.  initial deployment for existing project: [`bootstrap_procedure.2.initial_deployment.md`][bootstrap_procedure.2.initial_deployment.md]
3.  `argrelay` upgrade as (dependency for existing project): [`bootstrap_procedure.3.argrelay_upgrade.md`][bootstrap_procedure.3.argrelay_upgrade.md]

# Upgrading `argrelay` as project dependency

The steps below are explained as package management in [`FS_85_33_46_53.bootstrap_dev_env.md`][FS_85_33_46_53.bootstrap_dev_env.md].

Run `@/exe/dev_shell.bash` to activate `venv`:

```sh
./exe/dev_shell.bash
```

Remove saved `argrelay` entry from `@/conf/dev_env_packages.txt` (otherwise subsequent bootstrap will restore it):

```sh
sef -i "/argrelay/d" ./conf/dev_env_packages.txt
```

Upgrade `argrelay` package to newer version:

```sh
pip install --upgrade --force-reinstall argrelay
```

Re-run `@/exe/bootstrap_dev_env.bash`:

```sh
./exe/bootstrap_dev_env.bash
```

# Upgrading project customization

Most of the upgrade details are specific to project customization -<br/>
they depend on custom plugins (see `plugin_development.md`) and may require extra steps.

# Trying the upgrade

To see how it works after upgrade, try [`FS_58_61_77_69.dev_shell.md`][FS_58_61_77_69.dev_shell.md].

[bootstrap_procedure.1.project_creation.md]: bootstrap_procedure.1.project_creation.md
[bootstrap_procedure.2.initial_deployment.md]: bootstrap_procedure.2.initial_deployment.md
[bootstrap_procedure.3.argrelay_upgrade.md]: bootstrap_procedure.3.argrelay_upgrade.md

[FS_85_33_46_53.bootstrap_dev_env.md]: ../feature_stories/FS_85_33_46_53.bootstrap_dev_env.md
[FS_58_61_77_69.dev_shell.md]: ../feature_stories/FS_58_61_77_69.dev_shell.md
