
Install `asciinema`:

```sh
sudo dnf install asciinema
```

Go inside `dev-shell.bash`:

```sh
./dev-shell.bash
```

When `asciinema` starts, it spawns another user shell.

To hide all unnecessary details in Bash prompt, for example,
place this at the bottom of your `~/.bashrc` temporarily:

```sh
export PS1="\[\e[90m\](relay_demo) \u@oven \W:\n\[\e[0m\] "
```

Start recording:

```sh
asciinema rec --stdin
```
