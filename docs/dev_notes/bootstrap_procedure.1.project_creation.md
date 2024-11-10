
This procedure describes using [`FS_85_33_46_53.bootstrap_env.md`][FS_85_33_46_53.bootstrap_env.md] feature for step 1:
1.  project creation from scratch: [`bootstrap_procedure.1.project_creation.md`][bootstrap_procedure.1.project_creation.md]
2.  initial installation for existing project: [`bootstrap_procedure.2.initial_installation.md`][bootstrap_procedure.2.initial_installation.md]
3.  `argrelay` upgrade as (dependency for existing project): [`bootstrap_procedure.3.argrelay_upgrade.md`][bootstrap_procedure.3.argrelay_upgrade.md]

# Understand project root dir

See [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md]:

*   The project root dir is referred to as `@/`.
*   The project root dir is not necessarily Git repo root dir - it might be any sub-dir.

# Download bootstrap script

Obtain (copy and paste or download) [`bootstrap_env.bash`][bootstrap_env.bash] into temporary path,<br/>
for example, `/tmp/bootstrap_env.bash`.

# Bootstrap dependencies

The bootstrap dependencies are various files and dirs relative to `@/` (project root dir).

The script will fail (intentionally) if some of the dependencies are missing.

# First run

Run bootstrap **from the project root directory `@/`**:

```sh
cd path/to/project/root_dir
bash /tmp/bootstrap_env.bash
```

The script will likely fail for the first time (exits with code other than 0) due to missing dependencies,<br/>
but it is meant to be re-run multiple times until it succeeds<br/>
(until exits with code 0 after resolving all dependencies manually).

# Create `@/exe/` dir

Bootstrap script validates target dir by checking that it contains `@/exe/` dir<br/>
(as a safety mechanism to ensure it is not run accidentally in a wrong dir).

It also creates a copy of itself in `@/exe/` dir (to be versioned)<br/>
so that anyone can bootstrap project quickly after cloning the repo.

# Prepare `@/conf/` for the bootstrap of the current environment

Symlink `@/conf/` is supposed to point to (current) target environment config files.
Normally, it points to one of the sub-dirs under `@/dst/` (different per target environment).

To keep config files under version control:

*   Create `@/dst/` dir and a sub-dir giving it a name of the current environment, for example, `sample_target_env`:

    ```sh
    cd path/to/project/root_dir
    mkdir -p ./dst/sample_target_env
    ```

*   Create `@/conf/` symlink pointing to the dir with the given name, for example:

    ```sh
    cd path/to/project/root_dir
    ln -snf ./dst/sample_target_env ./conf
    ```

    This way config files for multiple target environments can co-exist under `@/dst/` and<br/>
    be selected via `@/conf/` symlink.

*   Ignore `@/conf/` symlink by revision control because the dir it points to is a local config (per deployment):

    ```sh
    cd path/to/project/root_dir
    cat .gitignore
    ```
    
    ```
    # Ignore local config:
    /conf
    ```

# What else might bootstrap need?

Keep re-running bootstrap until it succeeds (until it exits with code 0) addressing all issues step by step:

```sh
cd path/to/project/root_dir
bash /tmp/bootstrap_env.bash
```

If it is a new `argrelay`-based project created from scratch,<br/>
bootstrap will fail (exits with code other than 0) due to many missing files and dirs.

Normally, it is clear from the output what is the reason for the failure.

This is a non-exhaustive list of reasons and clues how to address them (trying to be in the order of occurrence):

*   Missing `@/exe/` dir.

    Bootstrap expects specific directory structure (see [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md])
    and checks at least existence of `@/exe` dir.

    If it is correct directory (where new project is being created from scratch), simply create `@/exe` dir.

*   Missing `@/bin/` dir.

    Bootstrap generates some files there.

    Create this dir - again, see also [`FS_29_54_67_86.dir_structure.md`][FS_29_54_67_86.dir_structure.md].

*   Missing `@/conf/python_env.conf.bash` file.

    This file provides config for Python interpreter and creation of Python virtual environment.

    If missing, bootstrap prints initial copy-and-paste-able content of this file.

*   Missing `@/exe/install_project.bash` file.

    This file is project-specific custom script to install project packages into Python venv.

    If missing, bootstrap prints initial copy-and-paste-able content of this file.

*   Missing Python project files (e.g. missing `setup.py` file).

    Default `@/exe/install_project.bash` (see its sources) file assumes it is a Python project which is built via:

    ```
    python -m pip install -e .[tests]
    ```

    If it is not the case (yet), you can comment out this line.

*   Missing `argrelay` package.

    To generate client and server executables, bootstrap needs installed `argrelay` package
    in the venv (as configured in `@/conf/python_env.conf.bash`) used by the bootstrap process.

    In turn, `@/exe/install_project.bash` script should install `argrelay` (directly or indirectly via dependencies).

    *   Long-term fix is to ensure `@/exe/install_project.bash` installs `argrelay`.
    *   Short-term fix is to activate the same venv (as configured in `@/conf/python_env.conf.bash`) and install `argrelay` manually.

*   Other missing files.

    When missing, bootstrap normally prints an initial copy-and-paste-able content for these files.

    This could be:

    *   `@/exe/config_files.conf.bash`
    *   `@/exe/resource_files.conf.bash`
    *   `@/exe/build_project.bash`
    *   `@/conf/shell_env.conf.bash`
    *   ...

# When bootstrap succeeds

Eventually, when bootstrap succeeds (exits with code 0),<br/>
its copy will be stored into `@/exe/bootstrap_env.bash` (it should be version-controlled).

To see how it works, try [`FS_58_61_77_69.dev_shell.md`][FS_58_61_77_69.dev_shell.md].

[bootstrap_procedure.1.project_creation.md]: bootstrap_procedure.1.project_creation.md
[bootstrap_procedure.2.initial_installation.md]: bootstrap_procedure.2.initial_installation
[bootstrap_procedure.3.argrelay_upgrade.md]: bootstrap_procedure.3.argrelay_upgrade.md

[FS_85_33_46_53.bootstrap_env.md]: ../feature_stories/FS_85_33_46_53.bootstrap_env.md
[FS_29_54_67_86.dir_structure.md]: ../feature_stories/FS_29_54_67_86.dir_structure.md
[FS_58_61_77_69.dev_shell.md]: ../feature_stories/FS_58_61_77_69.dev_shell.md
[bootstrap_env.bash]: ../../exe/bootstrap_env.bash
[root_readme.md]: ../../readme.md
