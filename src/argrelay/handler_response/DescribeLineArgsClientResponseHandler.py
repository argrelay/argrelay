from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.TermColor import TermColor
from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.schema_response.InterpResultSchema import interp_result_desc

indent_size = 2


class DescribeLineArgsClientResponseHandler(AbstractClientResponseHandler):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_response(
        self,
        response_dict: dict,
    ):
        interp_result: InterpResult = interp_result_desc.dict_schema.load(response_dict)
        ElapsedTime.measure("after_object_creation")
        DescribeLineArgsClientResponseHandler.render_result(interp_result)

    @staticmethod
    def render_result(
        interp_result: InterpResult,
    ):

        print()

        for i in range(len(interp_result.all_tokens)):
            if i == interp_result.tan_token_ipos:
                DescribeLineArgsClientResponseHandler.render_tangent_token(interp_result, interp_result.all_tokens[i])
            elif i in interp_result.consumed_tokens:
                print(
                    f"{TermColor.consumed_token.value}{interp_result.all_tokens[i]}{TermColor.reset_style.value}",
                    end = " ",
                )
            else:
                print(
                    f"{TermColor.unconsumed_token.value}{interp_result.all_tokens[i]}{TermColor.reset_style.value}",
                    end = " ",
                )

        DescribeLineArgsClientResponseHandler.render_envelope_containers(
            interp_result.envelope_containers,
            interp_result.tan_token_l_part,
        )

    @staticmethod
    def render_tangent_token(
        interp_result: InterpResult,
        tan_token,
    ):
        """
        Implements FS_11_87_76_73 (highlight tangent prefix).
        """

        DescribeLineArgsClientResponseHandler.highlight_prefix(
            [tan_token],
            interp_result.tan_token_l_part,
            TermColor.tangent_token_r_part,
        )

    @staticmethod
    def render_envelope_containers(
        envelope_containers: list[EnvelopeContainer],
        value_prefix: str,
    ):
        print()
        is_first_missing_found: bool = False
        for envelope_container in envelope_containers:
            print(f"{envelope_container.search_control.envelope_class}: {envelope_container.found_count}")

            for key_to_type_dict in envelope_container.search_control.keys_to_types_list:
                arg_key = next(iter(key_to_type_dict))
                arg_type = key_to_type_dict[arg_key]

                if arg_type in envelope_container.assigned_types_to_values:
                    print(" " * indent_size, end = "")

                    # Set color based on `ArgSource`:
                    arg_source_color: TermColor
                    arg_source_color = DescribeLineArgsClientResponseHandler.select_arg_source_color(
                        envelope_container,
                        arg_type,
                    )
                    print(arg_source_color.value, end = "")

                    # Key = `arg_type`:
                    print(f"{arg_type}:", end = " ")

                    # Single value = `arg_value` (with prefix highlight):
                    DescribeLineArgsClientResponseHandler.highlight_prefix(
                        [envelope_container.assigned_types_to_values[arg_type].arg_value],
                        value_prefix,
                    )

                    # Restore color to name `ArgSource`:
                    print(arg_source_color.value, end = "")
                    print(
                        f"[{envelope_container.assigned_types_to_values[arg_type].arg_source.name}]",
                        end = ""
                    )
                    print(TermColor.reset_style.value, end = "")

                elif arg_type in envelope_container.remaining_types_to_values:
                    print(" " * indent_size, end = "")

                    # Key = `arg_type`:
                    print(TermColor.remaining_value.value, end = "")
                    if not is_first_missing_found:
                        print(f"*{arg_type}:", end = "")
                        is_first_missing_found = True
                    else:
                        print(f"{arg_type}:", end = "")
                    print(f" ?", end = "")
                    print(TermColor.reset_style.value, end = " ")

                    # Multiple values = `arg_value` (with prefix highlight):
                    DescribeLineArgsClientResponseHandler.highlight_prefix(
                        envelope_container.remaining_types_to_values[arg_type],
                        value_prefix,
                    )

                else:
                    # The arg type is in the remaining but data have no arg values to suggest.
                    # Such arg types are shown because they are part of `search_control`.
                    # But they cannot be specified for current situation, otherwise, if already no data,
                    # any arg value assigned to such arg type would return no results.
                    print(" " * indent_size, end = "")
                    print(TermColor.no_option_to_suggest.value, end = "")
                    print(f"{arg_type}:", end = "")
                    print(" [none]", end = "")
                    print(TermColor.reset_style.value, end = "")

                print()

    @staticmethod
    def select_arg_source_color(
        envelope_container,
        arg_type,
    ):
        if envelope_container.assigned_types_to_values[arg_type].arg_source is ArgSource.ExplicitPosArg:
            arg_source_color = TermColor.explicit_pos_arg_value
        else:
            arg_source_color = TermColor.other_assigned_arg_value
        return arg_source_color

    @staticmethod
    def highlight_prefix(
        arg_values: list[str],
        value_prefix: str,
        default_color: TermColor = None,
    ):
        """
        Implements FS_32_05_46_00: highlight tangent prefix.
        """

        prefix_len: int = len(value_prefix)
        for arg_value in arg_values:
            # FS_32_05_46_00: use `startswith`
            if prefix_len > 0 and arg_value.startswith(value_prefix):
                print(
                    f"{TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}{arg_value[:prefix_len]}{TermColor.reset_style.value}",
                    # no space between L and R parts of the token:
                    end = "",
                )
                print(
                    f"{TermColor.tangent_token_r_part.value}{arg_value[prefix_len:]}{TermColor.reset_style.value}",
                    end = " ",
                )
            else:
                if default_color:
                    print(
                        f"{default_color.value}{arg_value}{TermColor.reset_style.value}",
                        end = " ",
                    )
                else:
                    print(
                        f"{arg_value}",
                        end = " ",
                    )
