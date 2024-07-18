from enum import IntEnum


class ClientExitCode(IntEnum):
    """
    Lists argrelay client exit codes.
    """

    ClientSuccess = 0

    GeneralError = 1

    ConnectionError = 2

    # maximum exit code:
    # https://stackoverflow.com/a/67219932/441652
    UnknownError = 255
