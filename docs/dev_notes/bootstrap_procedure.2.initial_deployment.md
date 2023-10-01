
This procedure describes using [`FS_85_33_46_53.bootstrap_dev_env.md`][FS_85_33_46_53.bootstrap_dev_env.md] feature for step 2:
1.  project creation from scratch: [`bootstrap_procedure.1.project_creation.md`][bootstrap_procedure.1.project_creation.md]
2.  initial deployment for existing project: [`bootstrap_procedure.2.initial_deployment.md`][bootstrap_procedure.2.initial_deployment.md]
3.  `argrelay` upgrade as (dependency for existing project): [`bootstrap_procedure.3.argrelay_upgrade.md`][bootstrap_procedure.3.argrelay_upgrade.md]

# Creating config for current environment

Directory `@/conf/` should be either|or:
*   (conventionally) a symlink and point to one of the config dir under `@/dst/`
*   (optionally) simply contain required files

Note that, depending on the project, there could be no initial config required -<br/>
in this case `@/exe/bootstrap_dev_env.bash` simply creates default config files.

The documents follow the first conventional symlink approach (which allows all configs be stored under `@/dst`).

When a project already exists, there could be many sample config dirs<br/>
under `@/dst/` to copy and modify, then use it as `@/conf/` target, for example:

```sh
cp -pr ./dst/some_config ./dst/this_config
ln -ns ./dst/this_config ./conf
```

Modify files under `@/conf/` if necessary.

# Running bootstrap

Re-run `@/exe/bootstrap_dev_env.bash` until it succeeds (exit with non-0 code):

```sh
./exe/bootstrap_dev_env.bash
```

There could be many things to fix if something wrong with the config or dependencies -<br/>
some are explained in [`bootstrap_procedure.1.project_creation.md`][bootstrap_procedure.1.project_creation.md].

# Project customization

Most of the initial deployment details are specific to project customization -<br/>
they depend on custom plugins (see `plugin_development.md`) and may require extra steps.

To run real Mongo DB (instead of `mongomock`), see also `mongo_notes.md`.

# Trying the deployment

To see how this deployment works, try [`FS_58_61_77_69.dev_shell.md`][FS_58_61_77_69.dev_shell.md].

[bootstrap_procedure.1.project_creation.md]: bootstrap_procedure.1.project_creation.md
[bootstrap_procedure.2.initial_deployment.md]: bootstrap_procedure.2.initial_deployment.md
[bootstrap_procedure.3.argrelay_upgrade.md]: bootstrap_procedure.3.argrelay_upgrade.md

[FS_85_33_46_53.bootstrap_dev_env.md]: ../feature_stories/FS_85_33_46_53.bootstrap_dev_env.md
[FS_58_61_77_69.dev_shell.md]: ../feature_stories/FS_58_61_77_69.dev_shell.md
