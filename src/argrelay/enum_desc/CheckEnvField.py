from enum import Enum, auto


class CheckEnvField(Enum):
    """
    Field names reported by FS_36_17_84_44 `check_env`.
    """

    server_version = auto()

    server_git_commit_id = auto()

    server_start_time = auto()
