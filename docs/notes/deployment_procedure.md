
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
Apparently, there are many replicas with packages.
And some of them take minutes to get updates.

After installation, initial config files can be found
together with installed package:

```sh
find . -name '*.yaml'
./venv/lib/python3.10/site-packages/argrelay/relay_demo/argrelay.client.yaml
./venv/lib/python3.10/site-packages/argrelay/relay_demo/argrelay.server.yaml
```

Copy sample config files into expected path:

```sh
cp ./venv/lib/python3.10/site-packages/argrelay/relay_demo/argrelay.client.yaml       ~/.argrelay.client.yaml
cp ./venv/lib/python3.10/site-packages/argrelay/relay_demo/argrelay.server.yaml       ~/.argrelay.server.yaml
```

Create a (demo) dir, link there `dev-init.bash` and `dev-shell.bash`, and start `dev-shell.bash` from there:

TODO: These steps are not finalized: `dev-shell.bash` so far assumed it runs from `argrelay.git` repo.
TODO: Automate entire deployment procedure.

```sh
mkdir ~/relay_demo
ln -snf $(pwd)/venv/lib/python3.10/site-packages/argrelay/relay_demo/dev-init.bash    ~/relay_demo/dev-init.bash
ln -snf $(pwd)/venv/lib/python3.10/site-packages/argrelay/relay_demo/dev-shell.bash   ~/relay_demo/dev-shell.bash
cd ~/relay_demo
./dev-shell.bash
```
