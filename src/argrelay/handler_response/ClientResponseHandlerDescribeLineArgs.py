from __future__ import annotations

from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.handler_response.ClientResponseHandlerAbstract import ClientResponseHandlerAbstract
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.schema_response.InterpResultSchema import interp_result_desc

indent_size = 2


class ClientResponseHandlerDescribeLineArgs(ClientResponseHandlerAbstract):
    default_overrides_caption: str = "overrides"
    """
    FS_72_53_55_13: Caption for options hidden by defaults.
    """

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
        self.render_result(interp_result)

    @staticmethod
    def render_result(
        interp_result: InterpResult,
    ):
        """
        FS_02_25_41_81: Renders results `func_id_query_enum_items` (Alt+Shift+Q)
        """

        print()

        # Print command line:
        for i in range(len(interp_result.all_tokens)):
            if i == interp_result.tan_token_ipos:
                ClientResponseHandlerDescribeLineArgs.render_tangent_token(interp_result, interp_result.all_tokens[i])
            elif i in interp_result.consumed_token_ipos_list():
                print(
                    f"{TermColor.consumed_token.value}{interp_result.all_tokens[i]}{TermColor.reset_style.value}",
                    end = " ",
                )
            elif i in interp_result.excluded_tokens:
                print(
                    f"{TermColor.excluded_token.value}{interp_result.all_tokens[i]}{TermColor.reset_style.value}",
                    end = " ",
                )
            else:
                print(
                    f"{TermColor.remaining_token.value}{interp_result.all_tokens[i]}{TermColor.reset_style.value}",
                    end = " ",
                )

        ClientResponseHandlerDescribeLineArgs.render_envelope_containers(
            interp_result.envelope_containers,
            interp_result.tan_token_l_part,
        )

    @staticmethod
    def render_tangent_token(
        interp_result: InterpResult,
        tan_token_value,
    ):
        """
        Implements FS_11_87_76_73 (highlight tangent prefix).
        """

        ClientResponseHandlerDescribeLineArgs.highlight_prefix(
            [tan_token_value],
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

            if envelope_container.found_count == 1:
                count_color = TermColor.found_count_1
            elif envelope_container.found_count > 1:
                count_color = TermColor.found_count_n
            else:
                count_color = TermColor.found_count_0
            print(
                f"{envelope_container.search_control.collection_name}: {count_color.value}{envelope_container.found_count}{TermColor.reset_style.value}"
            )

            for arg_name_to_prop_name_entry in envelope_container.search_control.arg_name_to_prop_name_map:
                arg_name = next(iter(arg_name_to_prop_name_entry))
                prop_name = arg_name_to_prop_name_entry[arg_name]

                if prop_name in envelope_container.assigned_prop_name_to_prop_value:
                    print(" " * indent_size, end = "")

                    # Set color based on `ValueSource`:
                    value_source_color: TermColor
                    value_source_color = ClientResponseHandlerDescribeLineArgs.select_value_source_color(
                        envelope_container,
                        prop_name,
                    )
                    print(value_source_color.value, end = "")

                    # Key = `prop_name`:
                    print(f"{prop_name}:", end = " ")

                    # Single value = `prop_value` (with prefix highlight):
                    ClientResponseHandlerDescribeLineArgs.highlight_prefix(
                        [envelope_container.assigned_prop_name_to_prop_value[prop_name].prop_value],
                        value_prefix,
                    )

                    # Restore color to name `ValueSource`:
                    print(value_source_color.value, end = "")
                    print(
                        f"[{envelope_container.assigned_prop_name_to_prop_value[prop_name].value_source.name}]",
                        end = ""
                    )
                    print(TermColor.reset_style.value, end = "")

                    # FS_72_53_55_13: Renders options hidden by default:
                    if len(envelope_container.filled_prop_values_hidden_by_defaults) != 0:
                        if prop_name in envelope_container.filled_prop_values_hidden_by_defaults:
                            print(" ", end = "")
                            print(TermColor.caption_hidden_by_default.value, end = "")
                            print(f"{ClientResponseHandlerDescribeLineArgs.default_overrides_caption}:", end = "")
                            print(TermColor.reset_style.value, end = " ")

                            values_hidden_by_defaults = envelope_container.filled_prop_values_hidden_by_defaults[
                                prop_name
                            ]
                            ClientResponseHandlerDescribeLineArgs.highlight_prefix(
                                values_hidden_by_defaults,
                                value_prefix,
                                TermColor.value_hidden_by_default,
                            )

                elif prop_name in envelope_container.remaining_prop_name_to_prop_value:
                    print(" " * indent_size, end = "")

                    # Key = `prop_name`:
                    print(TermColor.remaining_value.value, end = "")
                    if not is_first_missing_found:
                        print(f"*{prop_name}:", end = "")
                        is_first_missing_found = True
                    else:
                        print(f"{prop_name}:", end = "")
                    print(f" ?", end = "")
                    print(TermColor.reset_style.value, end = " ")

                    # Multiple values = `prop_value` (with prefix highlight):
                    ClientResponseHandlerDescribeLineArgs.highlight_prefix(
                        envelope_container.remaining_prop_name_to_prop_value[prop_name],
                        value_prefix,
                    )

                else:
                    # The `prop_name` is in the remaining but data have no `prop_value`-s to suggest.
                    # Such `prop_name`-s are shown because they are part of `search_control`.
                    # But they cannot be specified for current situation,
                    # because, if already no data, any `prop_value` assigned to such
                    # `prop_name` would return no results.
                    print(" " * indent_size, end = "")
                    print(TermColor.no_option_to_suggest.value, end = "")
                    print(f"{prop_name}: ", end = "")
                    print(SpecialChar.NoPropValue.value, end = "")
                    print(TermColor.reset_style.value, end = "")

                print()

    @staticmethod
    def select_value_source_color(
        envelope_container,
        prop_name,
    ):
        if (
            envelope_container.assigned_prop_name_to_prop_value[prop_name].value_source
            is
            ValueSource.explicit_offered_arg
        ):
            value_source_color = TermColor.explicit_offered_arg_value
        elif (
            envelope_container.assigned_prop_name_to_prop_value[prop_name].value_source
            is
            ValueSource.explicit_dictated_arg
        ):
            value_source_color = TermColor.explicit_dictated_arg_name_and_arg_value
        else:
            value_source_color = TermColor.other_assigned_arg_value
        return value_source_color

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
