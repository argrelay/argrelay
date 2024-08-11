from enum import Enum, auto


class CheckEnvFunc(Enum):
    """
    Functions used by FS_36_17_84_44 `check_env`.
    """

    func_id_get_server_argrelay_version = auto()
    """
    Query server `argrelay` package version.
    """

    func_id_get_server_project_git_commit_id = auto()
    """
    Query server git commit id.
    """

    func_id_get_server_start_time = auto()
    """
    Query server start time (millis since epoch).
    """
