#!/usr/bin/env bash

# This script tries to run maximum test set.

# It is expected to be run from started `^/exe/dev_shell.bash` session.

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

# Ensure the script was started in `^/exe/dev_shell.bash`:
if [[ -z "${ARGRELAY_DEV_SHELL:-}" ]]
then
    echo "ERROR: Run this script under \`^/exe/dev_shell.bash\`." 1>&2
    exit 1
fi

default_test_dir="tests"

input_path="${1:-"${default_test_dir}"}"

if [[ -d "${input_path}" ]]
then
    python -m unittest discover --verbose "${input_path}"
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
        # Assuming all test classes named as `ThisTestCase`:
        python -m unittest "${module_name}.ThisTestCase.${method_name}"
    else
        python -m unittest discover --verbose --start-directory "${path_dirname}" --pattern "${path_basename}"
    fi
    # Unreachable, if test fail:
    exit 0
fi

# Neither dir nor file:
echo "ERROR: specify valid dir path or file path: ${input_path}" 1>&2
exit 1

