
# `protoprimer`

## TL;DR

The copy of self-contained `protoprimer` module hosted within the client code bootstraps the client environment:

```sh
./proto_copy.py
```

## Why not ad-hoc bootstrap scripts?

The combination of the following features makes such scripts rather complex:

*   automatic bootstrap of `venv` with desired `python` version
*   support for multiple target environments
*   support for generated config & code (to avoid boilerplate)
*   support for value overrides: client-wide -> environment-specific -> command line arg
*   testability

Because it is a bootstrap process, all that should work from scratch or in a partially initialized environment.

## What is `protoprimer`?

The `protoprimer` provides a human-oriented single-file single-run configurable script to
bootstrap the client in multiple stages with environment-specific generate-able configuration which
eventually passes control to client-specific implementation.

Its job is done when:
(1) required `python` version can start
(2) inside activated `vevn`
(3) with the necessary dependencies
(4) configured based on environment-specific conditions
(5) and other client-specific code can take over.

## Basic scenario

```mermaid
flowchart TD
    client_conf[load client-wide config for `proto_code.py`]
    env_conf[load env-specific config for `proto_code.py`]

```

## Min dir layout

```
^/                                      # repo root = script dir = client root
│
├─ boot_env.py                          # renamed copy of `envincept.proto_code`
└─ boot_env.json                        # config found via default search list
```

## Max dir layout

```
^/                                      # repo root
│
├─ script_dir/
│  ├─ local_proto_code.py               # local copy of `envincept.proto_code`
│  ├─ boot_env.py                       # custom wrapper for ./local_proto_code.py
│  ├─ conf_primer/
│  │  ├─ conf_primer.proto_code.json    #
│  │  └─ ...
│  └─ ...
│
├─ client_dir/                          # client root
│  ├─ conf_client/
│  │  ├─ conf_client.proto_code.json
│  │  └─ ...
│  ├─ conf_env/                         # symlink to (e.g.) ./env_dir/conf_default/
│  │  ├─ conf_env.proto_code.json       # same as (e.g.) ./env_dir/conf_default/conf_env.proto_code.json
│  │  └─ ...
│  ├─ env_dir/
│  │  ├─ conf_default/
│  │  │  ├─ conf_env.proto_code.json
│  │  │  └─ ...
│  │  ├─ conf_special/
│  │  │  ├─ conf_env.proto_code.json
│  │  │  └─ ...
│  │  └─ ...
│  └─ ...
└─ ...
```

## Script modes

*   init_env mode

    Generate initial config files for a new client.

*   boot_env mode

    Bootstrap local environment for an existing client.

*   check_env mode

    Check the local environment.

*   print_dag mode

    Show DAG leading to the selected state node.

## Configuration path chain

*   proto dir + proto config

    Their location is specified by `python` runtime.

*   client dir + client config

    proto config specifies their location.

*   env dir + env config

    client config specifies their location.

## Dir categories

*   `^/` repo root

*   `@/` client root

*   `=/` script dir

## File categories

Files are named in the following pattern:

```
${func_name}.${file_source}.${file_scope}.${file_format}
```

For example, it is possible to see all these co-existing:

```
path/to/client-wide/config/proto_code.man.client.json
path/to/client-wide/config/proto_code.gen.client.json
path/to/environment-specific/config/proto_code.man.env.json
path/to/environment-specific/config/proto_code.gen.env.json
```
TODO: Do we need those `client` and `env` suffixes if the path to their containing dir differentiates them clearly?

### source: manual vs generated

`protoprimer` **never overwrites** files which are supposed to be changed manually.

TODO: update docs: files no longer marked by `man` or `gen`:

To do that, files are marked by suffix (or their containing dirs are marked by suffix) to differentiate them:

*   `man` = manual

*   `gen` = generated

Note that "never overwrites" means that `protoprimer` may still generate initial `man` files if they do not exist.

### scope: client-wide vs environment-specific

*   `client`

    Client-wide files apply to the entire client regardless of the environment.

    These files either/or

    *   have `client` suffix
    *   stay under `client` directory
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

### stage `primer_conf`

TODO: explain

### stage `client_conf`

Loads:

*   `=/proto_code.man.client.json`

### stage `env_conf`

Loads:

*   `=/proto_code.gen.conf.json` if exists

Generates:

*   TODO

Generates:

*   `@/env.conf`

*   `path/to/env.conf.d`

### stage `init_env`

---

[readme.md]: readme.md
