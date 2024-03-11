"""
"""
import os
import subprocess
from typing import Union


def get_git_repo_root_path(
    git_repo_path,
) -> Union[str, None]:
    if not os.path.isdir(git_repo_path):
        # A git repo can only be inside a dir:
        return None

    sub_proc = subprocess.run(
        [
            "git",
            "-C",
            git_repo_path,
            "rev-parse",
            "--show-toplevel",
        ],
        cwd = git_repo_path,
        capture_output = True,
    )
    exit_code = sub_proc.returncode

    if exit_code == 0:
        return sub_proc.stdout.decode("utf-8").strip()
    else:
        return None


def is_git_repo(
    git_repo_path,
) -> bool:
    """
    Detects whether `git_repo_path` points within a git repository.

    It is not required for `git_repo_path` to match git repo root (any sub-dir is accepted).
    """
    git_repo_root_path = get_git_repo_root_path(git_repo_path)
    if git_repo_root_path is None:
        return False
    else:
        return True


def get_full_commit_id(
    git_repo_path: str,
) -> str:
    sub_proc = subprocess.run(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        cwd = git_repo_path,
        capture_output = True,
    )
    exit_code = sub_proc.returncode

    if exit_code == 0:
        return sub_proc.stdout.decode("utf-8").strip()
    else:
        # If `is_git_repo` returns `True`, this should not happen:
        raise RuntimeError


def get_short_commit_id(
    git_repo_path: str,
) -> str:
    sub_proc = subprocess.run(
        [
            "git",
            "rev-parse",
            "--short",
            "HEAD",
        ],
        cwd = git_repo_path,
        capture_output = True,
    )
    exit_code = sub_proc.returncode

    if exit_code == 0:
        return sub_proc.stdout.decode("utf-8").strip()
    else:
        # If `is_git_repo` returns `True`, this should not happen:
        raise RuntimeError


def get_commit_time(
    git_repo_path: str,
) -> int:
    """
    Returns seconds since epoch (Unix time) for the last commit.
    """

    sub_proc = subprocess.run(
        [
            "git",
            "log",
            "-1",
            "--format=%ct",
        ],
        cwd = git_repo_path,
        capture_output = True,
    )
    exit_code = sub_proc.returncode

    if exit_code == 0:
        return int(sub_proc.stdout.decode("utf-8").strip())
    else:
        # If `is_git_repo` returns `True`, this should not happen:
        raise RuntimeError
