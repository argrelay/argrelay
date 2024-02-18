
TODO: Move this into FS_29_54_67_86 `dir_structure`

Table

| Script                         | Sets `PATH` | Activates `venv` | Re-installs | Purpose                                                      |
|--------------------------------|-------------|------------------|-------------|--------------------------------------------------------------|
| `@/exe/bootstrap_dev_env.bash` | -           | -                | yes         | to set up dev env, re-install or upgrade `argrelay`, etc.    |
| `@/exe/dev_shell.bash`         | yes         | yes              | no          | to start shell session with project-specific auto-completion |
| `@/exe/argrelay_rc.bash`       | yes         | no               | no          | to be used in `~/.bashrc` for all shell sessions             |

