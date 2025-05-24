#!/usr/bin/env bash

# GitHub job script to run `@/exe/bootstrap_env.bash` in different modes directly or via `@/exe/relay_demo.bash`.

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
# Note that this script expects no `@/conf/` config,
# so the location it knows is not through `@/conf/` but the direct one via `@/dst/`:
# FS_29_54_67_86 dir_structure: `@/dst/.github/` -> `@/`:
argrelay_dir="$( dirname "$( dirname "${script_dir}" )" )"

function ensure_no_uncommitted_changes_except {
    # Show any dirty repo state for investigation (before potential failure):
    git status
    git diff

    # Ensure no uncommitted changes:
    # https://stackoverflow.com/a/3879077/441652
    # Exclude files expected to be changed:
    # https://stackoverflow.com/a/39943727
    git add .
    if ! git diff --exit-code HEAD -- "${@}"
    then
        echo "ERROR: uncommitted changes" 1>&2
        exit 1
    fi
}

# Bootstrap should be run from the target dir:
cd "${argrelay_dir}" || exit 1

# Run each `stage_name` provided in args
# (see `argrelay.bootstrap.yaml` how each stage is run):
for stage_name in "${@}"
do
    case "${stage_name}" in
        "existing_conf_and_no_args")
            # There should be no `conf` in the repo
            # (it is supposed to be configured locally e.g. to point somewhere under `@/dst/`):
            test ! -d "${argrelay_dir}/conf"

            # Configure `@/conf/` (make it existing) before running bootstrap with no args:
            ln -sn "dst/.github" "conf"

            "${argrelay_dir}/exe/bootstrap_env.bash"

            # Run selected set of tests:
            "${argrelay_dir}/dst/.github/run_build_tests.bash"

            # Script `check_env` should succeed after bootstrap:
            "${argrelay_dir}/exe/check_env.bash" "offline"

            ensure_no_uncommitted_changes_except \
                ":(exclude)dst/.github/env_packages.txt" \
                ":(exclude)dst/.github/argrelay_client.json" \
                ":(exclude)dst/.github/argrelay_server.yaml" \
                ":(exclude)dst/.github/argrelay_plugin.yaml" \
                ":(exclude)dst/.github/check_env_plugin.conf.bash" \
                ":(exclude)dst/.github/check_env_plugin.conf.yaml" \

        ;;
        "fail_on_conf_mismatch")
            # Ensure bootstrap fails with `path/to/config` mismatch when `@/conf/` already exits:
            set +e
            "${argrelay_dir}/exe/relay_demo.bash" lay help
            exit_code="${?}"
            set -e
            test "${exit_code}" != "0"

            ensure_no_uncommitted_changes_except \
                ":(exclude)dst/.github/env_packages.txt" \
                ":(exclude)dst/.github/argrelay_client.json" \
                ":(exclude)dst/.github/argrelay_server.yaml" \
                ":(exclude)dst/.github/argrelay_plugin.yaml" \
                ":(exclude)dst/.github/check_env_plugin.conf.bash" \
                ":(exclude)dst/.github/check_env_plugin.conf.yaml" \

        ;;
        "reset_conf")
            # Remove `@/conf/` and re-start `@/exe/relay_demo.bash` in non-interactive mode:
            rm conf
            "${argrelay_dir}/exe/relay_demo.bash" lay help

            ensure_no_uncommitted_changes_except \
                ":(exclude)dst/.github/env_packages.txt" \
                ":(exclude)dst/.github/argrelay_client.json" \
                ":(exclude)dst/.github/argrelay_server.yaml" \
                ":(exclude)dst/.github/argrelay_plugin.yaml" \
                ":(exclude)dst/.github/check_env_plugin.conf.bash" \
                ":(exclude)dst/.github/check_env_plugin.conf.yaml" \

        ;;
        "succeed_on_conf_match")
            # Run with the same `@/conf/` left by `reset_conf`:
            "${argrelay_dir}/exe/relay_demo.bash" lay list service aaa

            ensure_no_uncommitted_changes_except \
                ":(exclude)dst/.github/env_packages.txt" \
                ":(exclude)dst/.github/argrelay_client.json" \
                ":(exclude)dst/.github/argrelay_server.yaml" \
                ":(exclude)dst/.github/argrelay_plugin.yaml" \
                ":(exclude)dst/.github/check_env_plugin.conf.bash" \
                ":(exclude)dst/.github/check_env_plugin.conf.yaml" \

        ;;
        *)
            echo "ERROR: unknown stage_name: \"${stage_name}\"" 1>&2
            exit 1
        ;;
    esac
done
