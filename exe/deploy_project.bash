########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the deploy scripts like this should pip-install itself (in the editable mode).

# Saved dev dependencies (if clean deployment is required, make `@/conf/dev_env_packages.txt` file empty):
python -m pip install -r "${argrelay_dir}/conf/dev_env_packages.txt"

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install --editable .[tests]
########################################################################################################################
