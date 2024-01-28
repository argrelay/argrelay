#!/usr/bin/env bash

# The script creates a new `squashed_branch_name` from the current `source_branch_name`
# by squashing with all comments against common ancestor with `target_branch`
# (e.g. first commit common with `origin/main`).
#
# The idea is to have a single script with no args to squash everything.

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
script_name="$( basename -- "${script_source}" )"
# Absolute script dirname:
# https://stackoverflow.com/a/246128/441652
script_dir="$( cd -- "$( dirname -- "${script_source}" )" &> /dev/null && pwd )"
# FS_29_54_67_86 dir_structure: `@/exe/` -> `@/`:
argrelay_dir="$( dirname "${script_dir}" )"

target_branch="origin/main"

squashed_tag="SQUASHED"

source_branch_name="$( git rev-parse --abbrev-ref HEAD )"

# Fail on uncommitted changes:
git diff --exit-code
git diff --exit-code --cached
git add .
if ! git diff --exit-code HEAD --
then
    git reset
    echo "ERROR: uncommitted changes" 1>&2
    exit 1
fi

# Fail if `squashed_tag` is already present in the branch name:
if [[ "${source_branch_name}" == *"${squashed_tag}"* ]]
then
    echo "ERROR: Tag ${squashed_tag} is already part of the branch name: ${source_branch_name}" 1>&2
    exit 1
fi

# Fail if previously squashed branch still exists (it has to be removed manually):
if git for-each-ref --format='%(refname:short)' refs/heads/ | grep "${source_branch_name}.${squashed_tag}"
then
    echo "ERROR: Branch prefixed with ${source_branch_name}.${squashed_tag} already exists" 1>&2
    exit 1
fi

# Abbreviated commit id:
git_short_commit="$( git rev-parse --short HEAD )"

# Name squashed branch with clear tag and abbreviated commit id:
squashed_branch_name="${source_branch_name}.${squashed_tag}.${git_short_commit}"

# Find common ancestor between source branch and target branch
# (basically, this is where source branch was branched off from the trunk):
git_base_commit="$( git merge-base HEAD "${target_branch}" )"

# Use separate branch to squash:
git checkout -b "${squashed_branch_name}" HEAD

# Squash by staging for commit:
git reset --soft "${git_base_commit}"

# Use branch name as the commit message:
git commit -m "${source_branch_name}"

# Set remote target branch named after the source branch:
git branch --set-upstream-to="origin/${source_branch_name}"
