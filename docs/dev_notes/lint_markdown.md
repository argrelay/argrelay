
# Primary purposes

*   Ensure Markdown links are not broken.
*   Use forced rule-based formatting for consistency.

# Quick howto-s

Install:

```sh
pip install pymarkdownlnt
```

Config:

```sh
less ./.pymarkdown.yaml
```

Run:

```sh
python -m pymarkdown scan path/to/markdown/files
```

Force specific rules:

```sh
python -m pymarkdown -e MD033 scan path/to/markdown/files
```

Help:

```sh
python -m pymarkdown -h
```

```sh
python -m pymarkdown scan -h
```

Investigate:

```sh
python -m pymarkdown --stack-trace --set log.level=DEBUG scan path/to/markdown/files
```
