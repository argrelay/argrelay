from enum import Enum


class ProcRole(Enum):
    """
    Defines role of the (operating system) process.

    Part of FS_14_59_14_06 pending requests implementation.
    """

    SoleProcWorker = False, True
    """
    Combination of `ParentProcSpinner` and `ChildProcWorker` within single process.
    """

    ParentProcSpinner = True, False
    """
    A parent (foreground) process which spins waiting for data from `ChildProcWorker`.
    """

    ChildProcWorker = True, True
    """
    A child (background) process which makes request to the server and sends data to `ParentProcSpinner`.
    """

    CheckEnvWorker = False, True
    """
    Similar to `SoleProcWorker` but used exclusively for FS_36_17_84_44 `check_env` implementation.
    """

    def __new__(
        cls,
        is_split_mode: bool,
        is_worker_proc: bool,
    ):
        enum_value = len(cls.__members__) + 1
        enum_obj = object.__new__(cls)
        enum_obj._value_ = enum_value
        return enum_obj

    def __init__(
        self,
        is_split_mode: bool,
        is_worker_proc: bool,
    ):
        self.is_split_mode = is_split_mode
        self.is_worker_proc = is_worker_proc
