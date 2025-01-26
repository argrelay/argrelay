from enum import IntEnum


class ClientExitCode(IntEnum):
    """
    Lists argrelay client exit codes.
    """

    ClientSuccess = 0

    GeneralError = 1

    ConnectionError = 2
    """
    Used to communicate specifically connection issues between client `ProcRole`-s.

    Provides a mechanism to implement FS_93_18_57_91 client fail over.
    """

    ServerError = 3
    """
    Server responded with an error (e.g. HTTP status code not 200),
    but it is not a `ConnectionError`.

    See also `ServerResponseError`.
    """

    # maximum exit code:
    # https://stackoverflow.com/a/67219932/441652
    UnknownError = 255
