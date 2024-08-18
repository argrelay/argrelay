
########################################################################################################################
# Report `git_version`.
#
# Sample output for `git --version`:
# git version 2.45.0 
full_git_version="$( git --version | sed -n 's/^git version \(.*\)$/\1/gp' )"

major_git_version="$( echo "${full_git_version}" | sed -n 's/^\([^.]*\).*$/\1/gp' )"
required_major_version=2

if [[ "${major_git_version}" -lt "${required_major_version}" ]]
then
    # shellcheck disable=SC2154
    echo -e "${warning_color}WARN:${reset_style} ${field_color}git_version:${reset_style} ${full_git_version} ${warning_message}# The major version of \`git\` is below ${required_major_version} (bad).${reset_style}"
else
    # shellcheck disable=SC2154
    echo -e "${success_color}INFO:${reset_style} ${field_color}git_version:${reset_style} ${full_git_version} ${success_message}# The major version of \`git\` is above ${required_major_version} (good).${reset_style}"
fi
