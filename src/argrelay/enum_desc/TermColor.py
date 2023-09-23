from enum import Enum


class TermColor(Enum):
    """
    Color codes for terminal text

    Reference:
    *   https://pkg.go.dev/github.com/whitedevops/colors
    *   https://gist.github.com/vratiu/9780109
    """

    ###################################################################################################################
    # Direct colors:
    # do not use them directly, use semantic colors instead (below).

    back_dark_blue = "\033[44m"
    back_dark_yellow = "\033[43m"

    fore_dark_red = "\033[31m"
    fore_dark_green = "\033[32m"
    fore_dark_cyan = "\033[36m"
    fore_dark_magenta = "\033[35m"
    fore_dark_gray = "\033[90m"

    fore_bright_yellow = "\033[93m"
    fore_bright_blue = "\033[94m"
    fore_bright_cyan = "\033[96m"
    fore_bright_white = "\033[97m"

    ###################################################################################################################
    # Semantic colors:

    prefix_highlight = back_dark_blue

    known_envelope_id = fore_dark_gray
    unknown_envelope_id = fore_dark_red

    no_help_hint = fore_dark_red

    help_hint = fore_dark_green

    tangent_token_l_part = fore_bright_white
    """
    See `ParsedContext.tan_token_l_part`
    """

    tangent_token_r_part = fore_bright_cyan
    """
    See `ParsedContext.tangent_token_r_part`
    """

    explicit_pos_arg_value = fore_bright_blue
    """
    See `ArgSource.ExplicitPosArg`.
    """

    other_assigned_arg_value = fore_dark_green
    """
    Any other assigned arg value except `explicit_pos_arg_value`.
    """

    remaining_value = fore_bright_yellow
    """
    See `EnvelopeContainer.remaining_types_to_values`.
    """

    consumed_token = fore_bright_blue
    """
    See:
    *   `InterpContext.consumed_tokens`
    *   `BaseResponse.consumed_tokens`
    """

    unconsumed_token = fore_dark_magenta
    """
    See:
    *   `InterpContext.unconsumed_tokens`
    """

    no_option_to_suggest = fore_dark_gray

    debug_output = fore_dark_gray

    reset_style = "\033[0m"
