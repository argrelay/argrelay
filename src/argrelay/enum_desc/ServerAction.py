from enum import Enum


class ServerAction(Enum):
    """
    Defines both:
    *   `ServerAction` in REST API URL path for server request (via enum item value)
    *   `ServerAction` in server request payload (via enum item name)
    """

    DescribeLineArgs = "/describe_line_args/"
    ProposeArgValues = "/propose_arg_values/"
    RelayLineArgs = "/relay_line_args/"
