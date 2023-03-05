#!/usr/bin/env bash

# Publish artifacts to pypi.org.
# See: docs/dev_notes/release_procedure.md
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
if [[ -z "${ARGRELAY_DEV_SHELL:-whatever}" ]]
then
    echo "ERROR: Run this script under \`dev-shell.bash\`." 2>&1
    exit 1
fi

# Ensure any "privileges" of `dev-shell.bash` are disabled:
unset ARGRELAY_DEV_SHELL

# Python config:
source ./python-conf.bash

# Use `"${path_to_venvX}"` (if does not exists, run `build-git-env.bash`):
source "${path_to_venvX}"/bin/activate

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

# Get path of `argrelay` module:
argrelay_version="$(
python << 'PYTHON_GET_PACKAGE_VERSION_EOF'
import pkg_resources
print(pkg_resources.require("argrelay")[0].version)
PYTHON_GET_PACKAGE_VERSION_EOF
)"

echo "argrelay version: ${argrelay_version}"

if [[ "${argrelay_version}" =~ -dev.[[:digit:]]*$ ]]
then
    echo "handle dev version"
else
    echo "handle non-dev version"

    git_tag="$(git describe --tags)"
    echo "git_tag: ${git_tag}"

    if [[ "v${argrelay_version}" != "${git_tag}" ]]
    then
        # TODO: try for non-dev release:
        exit 1
        git tag "v${argrelay_version}"
    fi
    # TODO: For proper releases, ensure that:
    #       * the commit is on public `main` branch
    #       * it is tagged and the tag name matches that of `setup.py`
    #       * anything else?
fi
exit 1

# Clean up previously built packages:
rm -rf ./dist/

# Build and test:
python -m tox

# Apparently, `tox` already builds `sdist`, for example:
# ./.tox/.pkg/dist/argrelay-0.0.0.dev3.tar.gz
# However, the following are the staps found in majority of the web resources:
python setup.py sdist
pip install twine
# This will prompt for login credentials:
twine upload dist/*

