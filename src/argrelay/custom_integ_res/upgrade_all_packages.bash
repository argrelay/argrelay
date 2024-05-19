#!/usr/bin/env bash

# This script upgrades all Python packages in `venv`.
#
# If Python has to be upgraded as well based on the latest version in `@/conf/python_conf.bash`,
# remove the `venv` first and re-run `@/exe/bootstrap_dev_env.bash`.
#
# The basic steps are:
# *   remove all package version records in `@/conf/dev_env_packages.txt`
# *   optionally, set user-specified `argrelay` version in `@/conf/dev_env_packages.txt`
# *   uninstall everything from `venv`
# *   let `@/exe/bootstrap_dev_env.bash` re-install all (transitive) dependencies at their latest versions

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
# shellcheck disable=SC2034
script_name="$( basename -- "${script_source}" )"
# Absolute script dirname:
# https://stackoverflow.com/a/246128/441652
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

if [[ -n "${1+x}" ]]
then
    # For example, `0.6.1`:
    exact_argrelay_version="${1}"
fi

# TODO_64_79_28_85: deduplicate this file with publish_package.bash (move upgrade function here from there).

# Switch to `@/` to avoid creating temporary dirs somewhere else:
cd "${argrelay_dir}" || exit 1

# Run `@/exe/bootstrap_dev_env.bash` if this file does not exits:
source "${argrelay_dir}/exe/argrelay_common_lib.bash"
ensure_inside_dev_shell

# Clear all package versions:
true > "conf/dev_env_packages.txt"

if [[ -n "${exact_argrelay_version+x}" ]]
then
    # Set `argrelay` to the specified exact version:
    echo "argrelay==${exact_argrelay_version}" > "conf/dev_env_packages.txt"
elif [[ "$( pip show argrelay | grep '^Version:' | cut -f2 -d' ' || true )" == *dev* ]]
then
    # Do not allow upgrades without specifying `exact_argrelay_version` if current version is a pre-release one:
    echo "ERROR: package \`argrelay\` has pre-release version - specify its next version manually" 1>&2
    exit 1
fi

# TODO: The step below also uninstalls `argrelay` (which provides this script) -
#       subsequently, if bootstrap fails to install `argrelay` again,
#       this script will be missing to re-try upgrade and user will have to `pip install argrelay` manually.
# Clear `venv` (only to be restored in the next step):
pip uninstall -y -r <( pip freeze )

# Bootstrap to let `@/exe/deploy_project.bash` install all packages
# via transitive dependencies and at their latest versions:
"${argrelay_dir}/exe/bootstrap_dev_env.bash"
