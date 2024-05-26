#!/usr/bin/env bash

# Publish artifacts to pypi.org.

# It is expected to be run from started `@/exe/dev_shell.bash`.

# It must be run from repo root:
#     ./exe/publish_package.bash

# See: `docs/dev_notes/release_procedure.md`.
# See: `docs/dev_notes/version_format.md`.
# A single "atomic" step to make a release:
# - ensure no local modifications
# - ensure commit is published
# - build and test
# - create tag
# - publish package

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

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

script_source="${BASH_SOURCE[0]}"
# The dir of this script:
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

# Switch to `@/` to avoid creating temporary dirs somewhere else:
cd "${argrelay_dir}" || exit 1

# Run `@/exe/bootstrap_env.bash` if this file does not exits:
source "${argrelay_dir}/exe/argrelay_common_lib.bash"
ensure_inside_dev_shell

# Ensure debug is disabled
# (it causes tests matching output to fail confusingly):
if [[ -n "${ARGRELAY_DEBUG+x}" ]]
then
    echo "ERROR: ARGRELAY_DEBUG is set" 1>&2
    exit 1
fi

# TODO_64_79_28_85: switch to `dst/release_env`
# TODO_64_79_28_85: use upgrade_env_packages.bash

# Clear venv (only to be restored in the next step):
pip uninstall -y -r <( pip freeze )
# Restore only saved dev packages
# (if fresh dependencies are required, clear `@/conf/env_packages.txt` first):
pip install -r "${argrelay_dir}/conf/env_packages.txt"
# Packages installed by `@/exe/bootstrap_env.bash` depend on
# `@/exe/install_project.bash`, but normally it:
# *  installs only those missing in `@/conf/env_packages.txt`
#    (specifically those with editable mode like `argrelay` itself)
# *  restores missing transitive dependencies
"${argrelay_dir}/exe/bootstrap_env.bash"

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
rm -rf "${argrelay_dir}/dist/"

# Run max tests with `ARGRELAY_DEV_SHELL` defined:
"${argrelay_dir}/exe/run_max_tests.bash"

# Now prepare to run without `ARGRELAY_DEV_SHELL`.
# Ensure any "privileges" of `@/exe/dev_shell.bash` are disabled:
unset ARGRELAY_DEV_SHELL

# Build and test via `tox`:
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

git_hash="$( git rev-parse HEAD )"
time_stamp="$( date -u +"%Y-%m-%dT%H:%M:%SZ" )"
publisher_user="$( whoami )"
publisher_host="$( hostname )"

# Versions has to be prefixed with `v` in tag:
if [[ "v${argrelay_version}" != "${git_tag}" ]]
then
    git_tag="v${argrelay_version}"
    if [[ "${is_dev_version}" != "true" ]]
    then
        # Append `.final` for non-dev (release) version to make a tag:
        git_tag="${git_tag}.final"
    fi
    echo "INFO: next git_tag: ${git_tag}" 1>&2
    # No matching tag exists yet:
    if true
    then
        # Note: unsigned unannotated tags appear "Verified" in GitHub:
        git tag "${git_tag}"
    else
        # Note: unsigned annotated does not appear "Verified" in GitHub:
        git tag --annotate "${git_tag}" -m "${git_hash} | ${time_stamp} | ${publisher_user} | ${publisher_host}"
    fi
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

# Create temporary `venv` for twine (do not pollute `venv` used for `argrelay`):
rm -rf         "${argrelay_dir}/tmp/venv.twine"
python -m venv "${argrelay_dir}/tmp/venv.twine"
source         "${argrelay_dir}/tmp/venv.twine/bin/activate"

# Apparently, `tox` already builds `sdist`, for example:
# @/.tox/.pkg/dist/argrelay-0.0.0.dev3.tar.gz
# However, the following are the staps found in majority of the web resources:
python setup.py sdist
pip install twine
# This will prompt for login credentials:
twine upload "dist/argrelay-${argrelay_version}.tar.gz"

# Change version to non-release-able to force user to change it later:
sed --in-place "s/${argrelay_version}/change-from-intentionally-wrong.${argrelay_version}/g" "setup.py"
