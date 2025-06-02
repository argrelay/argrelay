
# `protoscript`

## TL;DR

Store this single self-contained script within project files and run it to bootstrap the environment:

```sh
./boot_env.py
```

## Why not ad-hoc bootstrap scripts?

The combination of the following features makes such scripts rather complex:

*   automatic bootstrap of `venv` with desired `python` version
*   support for multiple target environments
*   support for generated config & code (to avoid boilerplate)
*   support for value overrides: project-wide -> environment-specific -> command line arg
*   testability

Because it is a bootstrap process, all that should work from scratch or in a partially initialized environment.

## What is `protoscript`?

The `protoscript` project provides a human-oriented single-file single-run configurable script to
bootstrap the project in multiple stages with environment-specific generate-able configuration which
eventually passes control to project-specific implementation.

Its job is done when:
(1) required `python` version can start
(2) inside activated `vevn`
(3) with the necessary dependencies
(4) configured based on environment-specific conditions
(5) and other project-specific code can take over.

## Basic scenario

```mermaid
flowchart TD
    proj_conf[load project-wide config for `boot_env.py`]
    env_conf[load env-specific config for `boot_env.py`]

```

## Dir categories

*   `@/` project root

*   `=/` script dir

## File categories

Files are named in the following pattern:

```
${func_name}.${file_source}.${file_scope}.${file_format}
```

For example, it is possible to see all these co-existing:

```
path/to/project-wide/config/boot_env.man.proj.json
path/to/project-wide/config/boot_env.gen.proj.json
path/to/environment-specific/config/boot_env.man.env.json
path/to/environment-specific/config/boot_env.gen.env.json
```
TODO: Do we need those `proj` and `env` suffixes if the path to their containing dir differentiates them clearly?

### source: manual vs generated

`protoscript` **never overwrites** files which are supposed to be changed manually.

To do that, files are marked by suffix (or their containing dirs are marked by suffix) to differentiate them:

*   `man` = manual

*   `gen` = generated

Note that "never overwrites" means that `protoscript` may still generate initial `man` files if they do not exist.

### scope: project-wide vs environment-specific

*   `proj`

    Project-wide files apply to the entire project regardless of the environment.

    These files either/or

    *   have `proj` suffix
    *   stay under `proj` directory
    *   have different names according to config

*   `env`

    Environment-specific files apply to the selected environment only.

    The environment is selected by `@/env.conf` file.

### tracked vs ignored

This category refers to tracking or ignoring files by a version-control system (e.g. `git`).

There is no special suffix for such files
because some files might be tracked in one env and ignored in another.
There is only a recommendation to track or ignore for each one.

## Config files

Because it is a multi-stage bootstrap, some config input may be required at each stage.

### stage `proj_conf`

Loads:

*   `=/boot_env.man.proj.json`

### stage `env_conf`

Loads:

*   `=/boot_env.gen.conf.json` if exists

Generates:

*   TODO

Generates:

*   `@/env.conf`

*   `path/to/env.conf.d`

### stage `init_env`

---

[readme.md]: readme.md
