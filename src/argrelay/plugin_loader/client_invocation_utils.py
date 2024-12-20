from __future__ import annotations

import os
from typing import Union

from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import get_argrelay_dir, eprint
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.schema_response.InvocationInput import InvocationInput


def load_client_plugin_config(
    plugin_instance_id: str,
    type_desc: TypeDesc,
) -> Union[dict, None]:
    """
    This function loads plugin config on client side.

    See FS_83_23_99_90 client plugin config override.
    """

    config_file_path = f"{get_argrelay_dir()}/conf/plugin_config/{plugin_instance_id}.yaml"
    if os.path.isfile(config_file_path):
        return type_desc.dict_from_yaml_file(config_file_path)
    else:
        return None


def filter_remaining_args(
    invocation_input: InvocationInput,
) -> list[str]:
    """
    Returns list of all unconsumed args from all FS_97_64_39_94 `token_bucket`s.

    TODO: TODO_66_09_41_16: clarify command line processing
          What this function really returns is list of unconsumed tokens.
          Consider rename.
    """

    remaining_args = []
    for i, curr_token in enumerate(invocation_input.all_tokens):
        if (
            (i not in invocation_input.consumed_token_ipos_list())
            and
            (i not in invocation_input.excluded_tokens)
        ):
            remaining_args.append(curr_token)
    return remaining_args


def prohibit_unconsumed_args(
    ii: InvocationInput,
) -> None:
    """
    TODO: TODO_86_57_50_38: Common delegator behavior: consider using delegator/func config to cause this error.
          Also, it can be caused on the server-side with redirection to DelegatorError
          (so that clients do not call that explicitly).
    """

    unconsumed_args = filter_remaining_args(ii)
    if len(unconsumed_args) > 0:
        eprint(
            f"ERROR: this function prohibits unrecognized args " +
            f"(see {TermColor.remaining_token.value}highlighted{TermColor.reset_style.value} on Alt+Shift+Q results): " +
            f"{TermColor.remaining_token.value}" +
            " ".join(unconsumed_args) +
            f"{TermColor.reset_style.value}"
        )
        exit(ClientExitCode.GeneralError.value)
