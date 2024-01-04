"""
"""
import subprocess


def is_git_repo(
    git_repo_path,
) -> bool:
    sub_proc = subprocess.run(
        [
            "git",
            "-C",
            git_repo_path,
            "rev-parse",
            "--show-toplevel",
        ],
        cwd = git_repo_path,
    )
    exit_code = sub_proc.returncode

    if exit_code == 0:
        return True
    else:
        return False


def get_shor_commit_id(
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
        return sub_proc.stdout.decode("utf-8")
    else:
        # If `is_git_repo` returns `True`, this should not happen:
        raise RuntimeError
