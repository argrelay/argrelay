
This doc describes `pip install` method from `dev_env_and_target_env_diff.md`.

# Installation

It is assumed the project integrating with `argrelay` has Python already configured (e.g. via `venv`).

To upgrade package:

```sh
pip install --upgrade argrelay
```

If newer version does not show up, try this:

```sh
pip install --upgrade --force-reinstall argrelay
```

Note:<br/>
Forcing to download new version does not appear consistent.
Apparently, depending on the replicas hosting the packages,
sometimes it take minutes to get the latest updates.

# Bootstrapping

After installation, initial config files can be found
together with installed package.

Find `bootstrap_inside_venv.bash` script, for example:

```sh
find . -name 'bootstrap_inside_venv.bash'
./venv/lib/python3.10/site-packages/argrelay/custom_integ_res/bootstrap_inside_venv.bash
```

Run it to deploy necessary artifacts
(into **current directory**, not where `bootstrap_inside_venv.bash` is):

```sh
./venv/lib/python3.10/site-packages/argrelay/custom_integ_res/bootstrap_inside_venv.bash
```

Depending on current state of config files, it may prompt for more info - follow the instructions.

Eventually, it will deploy:

*   Helper scripts in the **current directory**.

*   Config files for server and client config into `~/argrelay.conf.d/.*`.

One of the deployed script is `dev_shell.bash` -
it should work the same way as the demo in the main [readme.md][root_readme.md].

# Next steps

This deployment targets mostly initial version.

Subsequent upgrades still need to re-run `bootstrap_inside_venv.bash` script.

However, most of the details come with customization (using custom plugins)<br/>
which may require setting up additional dependencies - see `plugin_development.md`.

To run real Mongo DB (instead of `mongomock`), see also `mongo_notes.md`.

[root_readme.md]: ../../readme.md
