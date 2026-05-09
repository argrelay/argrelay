########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the install scripts like this should pip-install itself (in the editable mode).

# Use version constraints and editable mode:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
# (if clean install is required, make `@/conf/env_packages.txt` file empty):
python -m pip install --constraint "${argrelay_dir}/conf/env_packages.txt" --editable "${argrelay_dir}/"[tests]
########################################################################################################################
