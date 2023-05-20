
TODO: Content of this file is obsolete due to FS_85_33_46_53 `bootstrap_dev_env.bash`. To be updated.

# Initial installation

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

# Bootstrapping a new project

After installation, initial config files can be found
together with installed package.

Find `bootstrap_dev_env.bash` script, for example:

```sh
find . -name 'bootstrap_dev_env.bash'
```

```
./venv/lib/python3.10/site-packages/argrelay/custom_integ_res/bootstrap_dev_env.bash
```

Run it to deploy necessary artifacts from `^/` integration project root dir<br/>
(it creates necessary artifacts relative to the dir where it is called from, not where it resides):

```sh
./venv/lib/python3.10/site-packages/argrelay/custom_integ_res/bootstrap_dev_env.bash
```

Depending on current state of config files, it may prompt for more info - follow the instructions.

Eventually, it will deploy:

*   Helper scripts relative to the **current directory**.

*   Config files for server and client config into `~/.argrelay.conf.d/.*`.

*   Copy of itself in `^/exe/bootstrap_dev_env.bash` to be version controlled together with the integration project.

One of the deployed script is `^/exe/dev_shell.bash` -
it should work the same way as the demo in the main [readme.md][root_readme.md].

# Next steps

The steps above setup initial version.

Subsequent `argrelay` version upgrades will need a re-run of `^/exe/bootstrap_dev_env.bash` script.

Most of the details specific to custom project come with customization (using custom plugins)<br/>
which may require setting up additional dependencies - see `plugin_development.md`.

To run real Mongo DB (instead of `mongomock`), see also `mongo_notes.md`.

[root_readme.md]: ../../readme.md
