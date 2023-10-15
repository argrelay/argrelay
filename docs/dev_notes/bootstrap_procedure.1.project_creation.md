
This procedure describes using [`FS_85_33_46_53.bootstrap_dev_env.md`][FS_85_33_46_53.bootstrap_dev_env.md] feature for step 1:
1.  project creation from scratch: [`bootstrap_procedure.1.project_creation.md`][bootstrap_procedure.1.project_creation.md]
2.  initial deployment for existing project: [`bootstrap_procedure.2.initial_deployment.md`][bootstrap_procedure.2.initial_deployment.md]
3.  `argrelay` upgrade as (dependency for existing project): [`bootstrap_procedure.3.argrelay_upgrade.md`][bootstrap_procedure.3.argrelay_upgrade.md]

# Project creation with bootstrap script

Obtain (copy and paste or download) [`bootstrap_dev_env.bash`][bootstrap_dev_env.bash] into temporary path,<br/>
for example, `/tmp/bootstrap_dev_env.bash`.

Then, run it **from the project root directory**:
*   The project root dir is referred to as `@/` - see [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md].
*   The project root dir is not necessarily Git repo root dir - it might be any sub-dir.

```sh
cd path/to/project/dir
bash /tmp/bootstrap_dev_env.bash
```

It will likely fail first time (exits with code other than 0) due to missing config files,<br/>
but it is meant to be re-run multiple times until it succeeds (until it exits with code 0).

# Prepare `@/conf/` for the bootstrap of the current environment

See [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md].

Directory (or symlink) `@/conf/` contains (current) target environment config files.
Normally, it has to be a symlink to one of the sub-dirs under `@/dst/` (different per target environment).

To keep config files under version control, if `@/conf/` is not a symlink yet:

*   Move `@/conf/` dir under `@/dst/` dir giving it a name of the current environment, for example, `sample_target_env`:

    ```sh
    cd path/to/project/dir
    mkdir -p ./dst
    mv ./conf ./dst/sample_target_env
    ```

*   Create `@/conf/` symlink pointing to the dir with the given name, for example:

    ```sh
    cd path/to/project/dir
    ln -snf ./dst/sample_target_env ./conf
    ```

This way config files for multiple target environments can co-exist under `@/dst/` and be selected via `@/conf/` symlink.

# What else might bootstrap need?

Keep re-running bootstrap until it succeeds (until it exits with code 0) addressing all issues step by step:

```sh
cd path/to/project/dir
bash /tmp/bootstrap_dev_env.bash
```

If it is a new `argrelay`-based project created from scratch,<br/>
bootstrap will fail (exits with code other than 0) due to many missing files and dirs.

Normally, it is clear from the output what is the reason for the failure.

This is a non-exhaustive list of reasons and clues how to address them:

*   Missing `@/exe/` dir.

    Bootstrap expects specific directory structure (see [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md])
    and checks at least existence of `@/exe` dir.

    If it is correct directory (where new project is being created from scratch), simply create `@/exe` dir.

*   Missing `@/bin/` dir.

    Create it - again, see also [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md].

*   Missing `@/conf/python_conf.bash` file.

    This file provides config for Python interpreter and creation of Python virtual environment.

    If missing, bootstrap prints initial copy-and-paste-able content of this file.

*   Missing `@/exe/deploy_project.bash` file.

    This file is project-specific custom script to deploy project packages into Python venv.

    If missing, bootstrap prints initial copy-and-paste-able content of this file.

*   Missing `setup.py` file.

    This is expected by template version of `@/exe/deploy_project.bash` file.

    If missing, either create minimal `setup.py` or modify `@/exe/deploy_project.bash`.

*   Missing `argrelay` package.

    To generate client and server executables, bootstrap needs installed `argrelay` package
    in the venv (as configured in `@/conf/python_conf.bash`) used by the bootstrap process.

    In turn, `@/exe/deploy_project.bash` script should deploy `argrelay` (directly or indirectly via dependencies).

    *   Long-term fix is to ensure `@/exe/deploy_project.bash` installs `argrelay`.
    *   Short-term fix is to activate the same venv (as configured in `@/conf/python_conf.bash`) and install `argrelay` manually.

*   Other missing files.

    This could be:

    *   `@/exe/deploy_config_files_conf.bash`
    *   `@/exe/deploy_resource_files_conf.bash`
    *   `@/exe/build_project.bash`
    *   ...

    When missing, bootstrap prints initial copy-and-paste-able content for these files.

# When bootstrap succeeds

Eventually, when bootstrap succeeds (exits with code 0),<br/>
its copy will be stored into `@/exe/bootstrap_dev_env.bash` (it should be version-controlled).

To see how it works, try [`FS_58_61_77_69.dev_shell.md`][FS_58_61_77_69.dev_shell.md].

[bootstrap_procedure.1.project_creation.md]: bootstrap_procedure.1.project_creation.md
[bootstrap_procedure.2.initial_deployment.md]: bootstrap_procedure.2.initial_deployment.md
[bootstrap_procedure.3.argrelay_upgrade.md]: bootstrap_procedure.3.argrelay_upgrade.md

[FS_85_33_46_53.bootstrap_dev_env.md]: ../feature_stories/FS_85_33_46_53.bootstrap_dev_env.md
[FS_29_54_67_86.dir_structure.md]: ../feature_stories/FS_29_54_67_86.dir_structure.md
[FS_58_61_77_69.dev_shell.md]: ../feature_stories/FS_58_61_77_69.dev_shell.md
[bootstrap_dev_env.bash]: ../../exe/bootstrap_dev_env.bash
[root_readme.md]: ../../readme.md
