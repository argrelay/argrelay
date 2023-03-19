#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/uvsmtid/argrelay

# Generate `run_argrelay_server` and `run_argrelay_client` in curr dir.

# This script is NOT supposed to be run directly.
# It is a common part of two deployment methods (see `dev_env_and_target_env_diff.md`):
# *   `bootstrap_outside_venv.bash` FS_66_29_28_85
# *   `bootstrap_inside_venv.bash` FS_90_56_42_04

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

# Get path of `argrelay` module:
argrelay_path="$( dirname "$(
python << 'python_module_path_EOF'
import argrelay
print(argrelay.__file__)
python_module_path_EOF
)" )"

# Test files to ensure it is the right place:
test -f "${argrelay_path}/relay_server/__main__.py"
test -f "${argrelay_path}/relay_client/__main__.py"

# Generate `run_argrelay_server`:
cat << PYTHON_SERVER_EOF > ./run_argrelay_server
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/uvsmtid/argrelay
# It is NOT supposed to be version-controlled per project as it differs per environment (due to \`venv\`).
# It should rather be added to \`.gitignore\`.

from argrelay.relay_server.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_SERVER_EOF

# Generate `run_argrelay_client`:
cat << PYTHON_CLIENT_EOF > ./run_argrelay_client
#!$(which python)
# \`argrelay\`-generated integration file: https://github.com/uvsmtid/argrelay
# It is NOT supposed to be version-controlled per project as it differs per environment (due to \`venv\`).
# It should rather be added to \`.gitignore\`.

from argrelay.relay_client.__main__ import main

if __name__ == '__main__':
    main()
PYTHON_CLIENT_EOF

# Make both executable:
chmod u+x run_argrelay_server
chmod u+x run_argrelay_client

