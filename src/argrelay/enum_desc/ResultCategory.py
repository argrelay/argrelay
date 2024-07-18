from enum import Enum, auto


class ResultCategory(Enum):
    """
    Used for implementation of FS_36_17_84_44 `check_env`.
    """

    VerificationSuccess = auto()
    """
    Able to retrieve data to check and the check is successful.
    """

    VerificationWarning = auto()
    """
    Able to retrieve data to check, the result of the check is successful but not not absolutely clean.
    """

    VerificationFailure = auto()
    """
    Able to retrieve data to check, but the result of the check is not successful.
    """

    ServerOffline = auto()
    """
    Unable to retrieve data to check for the check which required server online.
    """

    ExecutionFailure = auto()
    """
    Unable to retrieve data to check.
    """
