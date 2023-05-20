########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay

# This is a custom build script *sourced* by `@/exe/bootstrap_dev_env.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, for integration project, the deploy scripts like this should pip-install itself (in the editable mode).

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r "${argrelay_dir}/conf/dev_env_packages.txt"
fi
########################################################################################################################
