#!/usr/bin/env bash

# Publish artifacts to pypi.org.
# See: docs/notes/release_procedure.md
# TODO: Merge in a single "atomic" step to make a release:
#       (1) create tag, (2) build, (3) publish, ...
#       At the moment, at least until first version `0.0.0`,
#       artifacts are published under `0.0.0.devN` version from any commit
#       (which may not be even seen publicly) and they may also deleted
#       from pypi.org as test uploads.

# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Error on undefined variables:
set -u
# Debug: Print commands after reading from a script:
#set -v
# Debug: Print commands before execution:
#set -x

# Switch to dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${script_dir}" || exit 1

# Ensure the script was started in `dev-shell.bash`:
# https://stackoverflow.com/questions/3601515/how-to-check-if-a-variable-is-set-in-bash/13864829#13864829
if [[ -z "${ARGRELAY_DEV_SHELL:-whatever}" ]]
then
    echo "ERROR: Run this command in \`dev-shell.bash\`." 2>&1
    exit 1
fi

# Ensure any "privileges" of `dev-shell.bash` are disabled:
unset ARGRELAY_DEV_SHELL

# Use `venv/relay_demo` (if does not exists, run `build-git-env.bash`):
source venv/relay_demo/bin/activate

# Update `requirements.txt` to know what was there at the time of publishing:
cat << 'REQUIREMENTS_EOF' > ./requirements.txt
###############################################################################
# Note that these dependencies are not necessarily required ones,
# those required listed in `setup.py` script and can be installed as:
# pip install -e .
###############################################################################
REQUIREMENTS_EOF
# Ignore `argrelay` itself (installed in editable mode):
pip freeze | grep -v '#egg=argrelay$' >> requirements.txt

# Ensure all changes are committed:
# https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes/3879077#3879077
git update-index --refresh
git diff-index --quiet HEAD --

# TODO: For proper releases, ensure that:
#       * the commit is on public `main` branch
#       * it is tagged and the tag name matches that of `setup.py`
#       * anything else?

# Clean up previously built packages:
rm -rf ./dist/

# Build and test:
python -m tox

# Apparently, `tox` already builds `sdist`, for example:
# ./.tox/.pkg/dist/argrelay-0.0.0.dev3.tar.gz
# TODO: Is there a way to make `tox` publish the package?
# However, the following are the staps found in majority of the web resources.

python setup.py sdist
pip install twine
# This will prompt for login credentials:
twine upload dist/*
