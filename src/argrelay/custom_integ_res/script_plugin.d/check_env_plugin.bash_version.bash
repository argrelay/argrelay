
########################################################################################################################
# Report `bash_version`:
# shellcheck disable=SC2154
if [[ -z "${BASH_VERSION+x}" ]]
then
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}bash_version:${reset_style} ${failure_message}# The env var is not defined: \`BASH_VERSION\`${reset_style}"
    exit 1
fi

# Sample output for `bash --version`:
# GNU bash, version 5.2.26(1)-release (x86_64-redhat-linux-gnu)
# GNU bash, version 4.2.46(2)-release (x86_64-redhat-Linux-gnu)
full_bash_version="$( bash --version | head -n 1 | cut -f4 -d' ' )"

major_bash_version="$( echo "${full_bash_version}" | sed -n 's/^\([^.]*\).*$/\1/gp' )"
required_major_version=4

if [[ "${major_bash_version}" -lt "${required_major_version}" ]]
then
    # shellcheck disable=SC2154
    echo -e "${warning_color}WARN:${reset_style} ${field_color}bash_version:${reset_style} ${full_bash_version} ${warning_message}# The major version of \`bash\` is below ${required_major_version} (bad).${reset_style}"
else
    if [[ "${full_bash_version}" != "${BASH_VERSION}" ]]
    then
        echo -e "${warning_color}WARN:${reset_style} ${field_color}bash_version:${reset_style} ${full_bash_version} ${warning_message}# \`bash --version\` hash different version string from \`\${BASH_VERSION}\`: ${BASH_VERSION}${reset_style}"
    else
        # shellcheck disable=SC2154
        echo -e "${success_color}INFO:${reset_style} ${field_color}bash_version:${reset_style} ${full_bash_version} ${success_message}# The major version of \`bash\` is above ${required_major_version} (good).${reset_style}"
    fi
fi
