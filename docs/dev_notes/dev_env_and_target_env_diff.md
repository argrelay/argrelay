
TODO: remove: this file is obsoleted by FS_85_33_46_53 `bootstrap_venv.bash`.

There are two kinds of environments `argrelay` can be used:

*   Development environment where `argrelay` Git repo is `git`-cloned to develop `argrelay` itself.
*   Target environment where `argrelay` Python package is `pip`-installed to be part of another project.

Both environments can actually be used for development or production use,
the differences are only in the installation method:

| Category:                 | `git_deployment`                  | `pip_deployment`              |
|---------------------------|-----------------------------------|-------------------------------|
| Command:                  | `git clone`                       | `pip install`                 |
| Audience role:            | mostly developers                 | mostly users                  |
| Purpose:                  | to develop `argrelay`-based tools | to use `argrelay`-based tools |
| `feature_story`:          | `FS_66_29_28_85`                  | `FS_90_56_42_04`              |
| Bootstrap script:         | `bootstrap_outside_venv.bash`     | `bootstrap_inside_venv.bash`  |
| Deploys artifacts:        | to current dir                    | to current dir                |
| Current dir:              | `git` root (dir in `PATH`)        | any dir (dir in `PATH`)       |
| Python config from:       | `python_conf.bash`                | exiting `venv`                |
| `argrelay` package is in: | editable `pip`-install            | regular `pip`-install         |
| **Config files**:         | symlinked                         | copied                        |

What happens with config files (bottom line in the table) is the primary reason for different methods,<br/>
the secondary reason is initial conditions (has `venv` activated or not).

*   To try `git clone` method, see demo in the root `readme.md`.
*   To try `pip install` method, see `deployment_procedure.md`.

# End result

Regardless of the initial deployment method, the end result is the same:
*   `git_deployment` deploy necessary files to run `dev_shell.bash` repeatedly
*   `pip_deployment` deploy necessary files to run `dev_shell.bash` repeatedly

Or alternatively, to avoid `dev_shell.bash`, configure `~/.bashrc` to source `argrelay_rc.bash`.

# Annotated call graphs

For `argrelay` itself, running `bootstrap_outside_venv.bash` - `dev_shell.bash` can be started right away
because all necessary artifacts are available after `git clone`.
Other projects (integrating with `argrelay`) should run `bootstrap_outside_venv.bash` once at least to make
`dev_shell.bash` available in the project dir.

*   `bootstrap_venv.bash`

    *   `python_conf.bash`

    *   `deploy_project.bash` (provides `venv` for all scripts that follow)

    *   `bootstrap_venv.bash` (call refreshed copy of itself recursively)

    *   `deploy_config_files.bash` symlink

    *   `deploy_resource_files.bash` symlink

    *   `generate_artifacts.bash`

    *   `build_project.bash`

*   `bootstrap_outside_venv.bash`

    *   `bootstrap_venv.bash` (provides `venv` for all scripts that follow)

    *   `deploy_config_files.bash` symlink

    *   `deploy_resource_files.bash` symlink

    *   `generate_artifacts.bash`

    *   `build_project.bash`

*   `bootstrap_inside_venv.bash`

    Note that, subsequently, after this bootstrap is done,
    `dev_shell.bash` (via `bootstrap_venv.bash`) will still prompt once to provide `python_conf.bash`.

    *   `deploy_config_files.bash` copy

    *   `deploy_resource_files.bash` symlink

    *   `generate_artifacts.bash`

    *   `build_project.bash`

*   `dev_shell.bash` is used repeatedly after initial deployment or subsequent upgrades via bootstrap scripts.

    *   `init_shell_env.bash`

        *   `bootstrap_venv.bash`
            (so that subsequent call `bootstrap_outside_venv.bash` goes to package artifact in `venv`)

        *   `bootstrap_outside_venv.bash` (again, every time - see annotations above)
            *   `bootstrap_venv.bash`
            *   `deploy_config_files.bash`
            *   `deploy_resource_files.bash`
            *   `generate_artifacts.bash`
            *   `build_project.bash`

        *   `argrelay_rc.bash`
