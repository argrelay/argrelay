#!/usr/bin/env bash

# Publish artifacts to pypi.org.

# It is expected to be run from started `dev_shell.bash`.

# It must be run from repo root:
#     ./scripts/publish_package.bash

# See: `docs/dev_notes/release_procedure.md`.
# See: `docs/dev_notes/version_format.md`.
# A single "atomic" step to make a release:
# - ensure no local modifications
# - ensure commit is published
# - build and test
# - create tag
# - publish package

# Debug: Print commands before execution:
#set -x
# Debug: Print commands after reading from a script:
#set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

# Switch to dir of the script:
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${script_dir}" || exit 1
# Change to one level up (from `scripts` to repo root):
cd ".." || exit 1

# Ensure the script was started in `dev_shell.bash`:
if [[ -z "${ARGRELAY_DEV_SHELL:-whatever}" ]]
then
    echo "ERROR: Run this script under \`dev_shell.bash\`." 1>&2
    exit 1
fi

# Ensure any "privileges" of `dev_shell.bash` are disabled:
unset ARGRELAY_DEV_SHELL

# Python config:
source ./python_conf.bash
# Use `"${path_to_venvX}"` (if does not exists, run `bootstrap_venv.bash` by starting `dev_shell.bash`):
# shellcheck disable=SC2154
source "${path_to_venvX}"/bin/activate

# Re-install itself:
pip install -e .

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
# https://stackoverflow.com/a/3879077/441652
git update-index --refresh
if ! git diff-index --quiet HEAD --
then
    echo "ERROR: uncommitted changes" 1>&2
    exit 1
fi

# See also: `docs/dev_notes/version_format.md`.
# Get version of `argrelay` distribution:
argrelay_version="$(
python << 'python_get_package_version_EOF'
from pkg_resources import get_distribution
print(get_distribution("argrelay").version)
python_get_package_version_EOF
)"
echo "INFO: argrelay version: ${argrelay_version}" 1>&2

# Determine if it is a dev version (which relaxes many checks):
if [[ "${argrelay_version}" =~ ^[[:digit:]]*\.[[:digit:]]*\.[[:digit:]]*\.dev.[[:digit:]]*$ ]]
then
    echo "INFO: dev version pattern: ${argrelay_version}" 1>&2
    is_dev_version="true"
elif [[ "${argrelay_version}" =~ ^[[:digit:]]*\.[[:digit:]]*\.[[:digit:]]*$ ]]
then
    echo "INFO: release version pattern: ${argrelay_version}" 1>&2
    is_dev_version="false"
else
    echo "ERROR: unrecognized version pattern: ${argrelay_version}" 1>&2
    exit 1
fi
echo "INFO: is_dev_version: ${is_dev_version}" 1>&2

# Clean up previously built packages:
rm -rf ./dist/

# Build and test:
python -m tox

# Fetch from upstream:
git_main_remote="origin"
git fetch "${git_main_remote}"

# Check if current commit is in the main branch:
git_main_branch="main"
if ! git merge-base --is-ancestor HEAD "${git_main_remote}/${git_main_branch}"
then
    if [[ "${is_dev_version}" == "true" ]]
    then
        echo "WARN: current HEAD is not in ${git_main_remote}/${git_main_branch}" 1>&2
    else
        echo "ERROR: current HEAD is not in ${git_main_remote}/${git_main_branch}" 1>&2
        exit 1
    fi
else
    echo "INFO: current HEAD is in ${git_main_remote}/${git_main_branch}" 1>&2
fi

git_tag="$(git describe --tags)"
echo "INFO: curr git_tag: ${git_tag}" 1>&2

# Versions has to be prefixed with `v` in tag:
if [[ "v${argrelay_version}" != "${git_tag}" ]]
then
    git_tag="v${argrelay_version}"
    echo "INFO: next git_tag: ${git_tag}" 1>&2
    # No matching tag exists yet:
    git tag "${git_tag}"
else
    # Matching tag already exists - either already released or something is wrong.
    # It can be fixed by removing the tag, but user has to do it consciously.
    echo "ERROR: tag already exits: ${git_tag}" 1>&2
    exit 1
fi

# Push to remote only if it is non-dev version:
if [[ "${is_dev_version}" == "true" ]]
then
    echo "WARN: tag is not pushed to remote: ${git_tag}" 1>&2
else
    echo "INFO: tag is about to be pushed to remote: ${git_tag}" 1>&2
    git push "${git_main_remote}" "${git_tag}"
fi

# Apparently, `tox` already builds `sdist`, for example:
# ./.tox/.pkg/dist/argrelay-0.0.0.dev3.tar.gz
# However, the following are the staps found in majority of the web resources:
python setup.py sdist
pip install twine
# This will prompt for login credentials:
twine upload "dist/argrelay-${argrelay_version}.tar.gz"

# Change version to non-release-able to force user to change it later:
sed --in-place "s/${argrelay_version}/change-from-intentionally-wrong.${argrelay_version}/g" "setup.py"
