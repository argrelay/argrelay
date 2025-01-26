from enum import Enum


class ServerAction(Enum):
    """
    `ServerAction`-s are specific to operations on command line (primary purpose of `argrelay`).

    Defines both:
    *   `ServerAction` in REST API URL path for server request (via enum item value)
    *   `ServerAction` in server request payload (via enum item name)

    See `DataOperation` to perform data updates.
    """

    ProposeArgValues = "/propose_arg_values/"

    DescribeLineArgs = "/describe_line_args/"
    """
    This action is closely related to FS_02_25_41_81 `func_id_query_enum_items`.
    """

    RelayLineArgs = "/relay_line_args/"
