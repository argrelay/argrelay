########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the build scripts like this for integration project should build it and test it.

# It is fine to run tox on every start of FS_58_61_77_69 `dev_shell` because it is only used by `argrelay` devs:
# Build and test:
python -m tox
########################################################################################################################
