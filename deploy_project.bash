########################################################################################################################
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# This is a custom build script *sourced* by `bootstrap_venv.bash`.
# Python `venv` is already activated before it is sourced.

# Normally, the deploy scripts like this for integration project should pip-install it (in the editable mode).

# Use editable install:
# https://pip.pypa.io/en/latest/topics/local-project-installs/
python -m pip install -e .[tests]

if false
then
    # This is NOT necessary (extra dev dependencies):
    python -m pip install -r requirements.txt
fi
########################################################################################################################
