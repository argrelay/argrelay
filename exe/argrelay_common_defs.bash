#!/usr/bin/env bash
# `argrelay` integration file: https://github.com/argrelay/argrelay

# TODO: draft:
exit 0

# This script is supposed to be sourced by others, not run directly:
[[ "${BASH_SOURCE[0]}" == "${0}" ]] && exit 1

# Path for the script which sources this: using [1] instead of [0]:
script_path="${BASH_SOURCE[1]}"
# shellcheck disable=SC2034
script_dir="$( cd -- "$( dirname -- "${script_path}" )" &> /dev/null && pwd )"
# shellcheck disable=SC2034
script_name="$( basename -- "${script_path}" )"

# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
function derive_argrelay_dir_relative_to {

    # Must be prefixed with "@/":
    local prefixed_script_rel_path="${1}"
    test "${prefixed_script_rel_path:0:2}" == "@/"

    local script_rel_path="${prefixed_script_rel_path:2}"

    # Remove `script_rel_path` from `script_path`:
    # https://stackoverflow.com/a/16623897/441652
    # shellcheck disable=SC2034
    local argrelay_dir="${script_path%"${script_rel_path}"}"
}



