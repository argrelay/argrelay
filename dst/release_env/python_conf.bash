########################################################################################################################
# `argrelay` integration file: https://github.com/argrelay/argrelay
# This config file is supposed to be owned and version-controlled by target project integrated with `argrelay`.

# Path to `venv` to create or reuse:
# shellcheck disable=SC2034
path_to_venvX="venv"
# Path to specific Python interpreter (to override any default in the `PATH`):
# shellcheck disable=SC2034
path_to_pythonX="$( which python )"
# Custom prompt prefix - see:
# https://docs.python.org/3/library/venv.html
# --prompt PROMPT Provides an alternative prompt prefix for this environment.
# shellcheck disable=SC2034
venv_prompt_prefix="@~release"
########################################################################################################################

