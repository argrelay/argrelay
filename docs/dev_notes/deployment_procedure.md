
This doc describes `pip install` method from `dev_env_and_target_env_diff.md`.

It is assumed the project using `argrelay` already has Python configured (e.g. via `venv`).

To upgrade package:

```sh
pip install --upgrade argrelay
```

If newer version does not show up, try this:

```sh
pin uninstall argrelay
pip install --upgrade --force-reinstall argrelay
```

Note:
Forcing to download new version does not appear consistent.
Apparently, there are many replicas with packages on the web.
And some of them take minutes to get the latest updates.

After installation, initial config files can be found
together with installed package.

Find `build-pip-env.bash` file, for example:

```sh
find . -name 'build-pip-env.bash'
./venv/lib/python3.10/site-packages/argrelay/relay_demo/build-pip-env.bash
```

Run it to deploy necessary artifacts
(into **current directory**, not where `build-pip-env.bash` is):

```sh
./venv/lib/python3.10/site-packages/argrelay/relay_demo/build-pip-env.bash
```

It will deploy:

*   Helper scripts in the **current directory**.

*   User dot files (`~/.*`) for server and client config.

To enable auto-completion:

*   Update deployed `argrelay-rc.bash`:

    Minimally, assign `PATH_TO_SCRIPTS` there to absolute path of **current directory**.

*   Source deployed `argrelay-rc.bash` from the **current directory** in `~/.bashrc`.

This deployment covers only vanilla version.

Customization (with custom plugins) may require setting up additional dependencies - see `plugin_development.md`.

To run real Mongo DB (instead of `mongomock`), see also `mongo_notes.md`.
