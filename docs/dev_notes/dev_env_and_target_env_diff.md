
There are two kinds of environments `argrelay` can be used:

*   Development environment (dev env) where `argrelay` Git repo is `git`-cloned to develop `argrelay` itself.
*   Target environment where `argrelay` Python package is `pip`-installed to be part of another project.

Both environments can actually be used for development or production use,
the differences are only in the installation method:

| Category:                 | `git clone`            | `pip install`                   |
|---------------------------|------------------------|---------------------------------|
| Purpose:                  | to develop `argrelay`  | to integrate in another project |
| Script to run:            | `build-git-env.bash`   | `build-pip-env.bash`            |
| Deploys artifacts:        | to `git` root          | to current dir                  |
| Python config from:       | `python-conf.bash`     | exiting `venv`                  |
| `venv`:                   | creates new `venv`     | uses existing `venv`            |
| `argrelay` package is in: | editable `pip`-install | regular `pip`-install           |

*   For `pip install` method, see `deployment_procedure.md`.
*   For `git clone` method, see main `readme.md`.

