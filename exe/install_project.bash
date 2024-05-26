########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the install scripts like this should pip-install itself (in the editable mode).

# Saved env dependencies (if clean install is required, make `@/conf/env_packages.txt` file empty):
python -m pip install -r "${argrelay_dir}/conf/env_packages.txt"

# Use editable mode:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install --editable .[tests]
########################################################################################################################
