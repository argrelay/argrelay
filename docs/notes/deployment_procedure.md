
To upgrade package:

```sh
pip install --upgrade argrelay
```

If newer version does not show up,
try uninstalling and installing without cache:


```sh
pin uninstall argrelay
pip install --no-cache-dir --upgrade argrelay
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
copy ./venv/lib/python3.10/site-packages/argrelay/relay_demo/argrelay.client.yaml ~/.argrelay.client.yaml
copy ./venv/lib/python3.10/site-packages/argrelay/relay_demo/argrelay.server.yaml ~/.argrelay.server.yaml
```



