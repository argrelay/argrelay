#!/usr/bin/env bash

# This script tries to run maximum test set.

# It is expected to be run from started `@/exe/dev_shell.bash` session.

# It must be run from repo root:
#     ./exe/run_max_tests.bash

# See `tests/readme.md`.
# It also allows running tests:
# *   in specific dir only:
#         run_max_tests.bash path/to/dir
# *   in specific test file only
#         run_max_tests.bash path/to/file
# *   in specific test method only
#         run_max_tests.bash path/to/file method

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v
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

# TODO: TODO_78_94_31_68: split argrelay into multiple packages:
#       Think of contributing to `import-linter` to invoke it via tests
#       instead of external tool with static config.
#       As of now, just run it ahead of selecting any tests:
lint-imports

default_test_dir="${argrelay_dir}/tests"

input_path="${1:-"${default_test_dir}"}"

# Leave abs path as is, adjust relative:
if [[ "${input_path:0:1}" != "/" ]]
then
    input_path="$(pwd)/${input_path}"
fi

# Note for `discover`:
# `--top-level-directory` is what imports are relative to.
# `--start-directory` is the starting root for test scanning.
# Current directory `.` is what the above path should be relative to.

if [[ -d "${input_path}" ]]
then
    python -m unittest discover --failfast --verbose --top-level-directory "${argrelay_dir}/tests" --start-directory "${input_path}"
    # Unreachable, if test fail:
    exit 0
fi

if [[ -f "${input_path}" ]]
then
    path_dirname="$(dirname "${input_path}")"
    path_basename="$(basename "${input_path}")"
    method_name="${2:-}"
    if [[ -n "${method_name}" ]]
    then
        # Try to invoke this:
        #    python -m unittest test_module.TestClass.test_method

        # Strip test dir path:
        module_path="$( realpath --relative-to="${default_test_dir}" "${input_path}" )"
        # Drop the `.py` extension and replace `/` -> `.` :
        module_name="$( echo "${module_path}" | rev | cut -f 2- -d '.' | rev | sed "s/\//./g" )"
        # Neet to switch to the test dir to let test module name lookup work:
        cd "${default_test_dir}"
        # Assuming all test classes named as `ThisTestClass`:
        python -m unittest --failfast "${module_name}.ThisTestClass.${method_name}"
    else
        python -m unittest discover --failfast --verbose --top-level-directory "${argrelay_dir}/tests" --start-directory "${path_dirname}" --pattern "${path_basename}"
    fi
    # Unreachable, if test fail:
    exit 0
fi

# Neither dir nor file:
echo "ERROR: specify valid dir path or file path: ${input_path}" 1>&2
exit 1

