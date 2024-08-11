
########################################################################################################################
# Report `bash_version`:
# shellcheck disable=SC2154
if [[ -n "${BASH_VERSION+x}" ]]
then
    echo -e "${success_color}INFO:${reset_style} ${field_color}bash_version:${reset_style} ${BASH_VERSION}"
else
    echo -e "${failure_color}ERROR:${reset_style} ${field_color}bash_version:${reset_style} ${failure_message}# Env var \`BASH_VERSION\` is not defined${reset_style}"
    exit 1
fi
