
This doc notes down steps to record screencast.

See [`@/exe/play_x_server_demo.bash`][play_x_server_demo.bash] for automatic demo.

Install [`asciinema`][asciinema]:

```sh
sudo dnf install asciinema
```

Go inside `@/exe/dev_shell.bash`:

```sh
./exe/dev_shell.bash
```

When `asciinema` starts, it spawns another user shell.

To hide all unnecessary details in Bash prompt, for example,
place this at the bottom of your `~/.bashrc` temporarily:

```sh
export PS1="\[\e[90m\]argrelay.git:\[\e[0m\] "
```

Start recording:

```sh
asciinema rec --stdin
```

[Generate GIF][generate_GIF], if necessary.

[asciinema]: https://github.com/asciinema/asciinema
[generate_GIF]: https://dstein64.github.io/gifcast/
[play_x_server_demo.bash]: ../../exe/play_x_server_demo.bash
