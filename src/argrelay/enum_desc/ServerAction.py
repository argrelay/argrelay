from enum import Enum


class ServerAction(Enum):
    """
    Defines both:
    *   `ServerAction` in REST API URL path for server request (via enum item value)
    *   `ServerAction` in server request payload (via enum item name)
    """

    ProposeArgValues = "/propose_arg_values/"

    DescribeLineArgs = "/describe_line_args/"
    """
    This action is closely related to FS_02_25_41_81 `query_enum_items_func`.
    """

    RelayLineArgs = "/relay_line_args/"
