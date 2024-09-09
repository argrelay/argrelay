from enum import Enum


class DataOperation(Enum):
    """
    `DataOperation` defines server API to manipulate data at its backend.

    Implements FS_74_69_61_79 get set data envelope.

    For user operations on command line see `ServerAction`.
    """

    get_data_envelopes = "/get_data_envelopes/"

    set_data_envelopes = "/set_data_envelopes/"
