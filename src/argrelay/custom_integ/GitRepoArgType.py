from __future__ import annotations

from enum import Enum, auto


class GitRepoArgType(Enum):
    """
    Envelope arg types (properties) used by `GitRepoLoader`.
    """

    # Short name for a repo (to avoid specifying its `git_repo_root_rel_path`):
    git_repo_alias = auto()

    # Absolute path common to multiple Git repos - what `git_repo_root_rel_path` are relative to:
    git_repo_root_abs_path = auto()

    # Git root path relative to `git_repo_root_abs_path`:
    git_repo_root_rel_path = auto()

    # Git root dir base name:
    git_repo_root_base_name = auto()

    # Categorize repo content: conf, code, ...
    git_repo_content_type = auto()

    # Git tag, for example: `v0.6.7.final`
    git_repo_tag_name = auto()

    # Git commit, for example: 52a3d54d17fe5cba6bad57abc4b6bebd881d3ce6
    git_repo_commit_id = auto()

    # Git commit, for example: 52a3d54d17fe5cba6bad57abc4b6bebd881d3ce6
    git_repo_short_commit_id = auto()

    # Git commit comment:
    git_repo_commit_message = auto()

    # Git commit author name:
    git_repo_commit_author_name = auto()

    # Git commit author email:
    git_repo_commit_author_email = auto()

    # Git commit date (UTC):
    git_repo_commit_date = auto()

    # Git commit time (UTC):
    git_repo_commit_time = auto()

    # FS_06_99_43_60: example of using non-scalar value (array|list):
    # List of categories object belongs to:
    git_repo_object_category = auto()

    def __str__(self):
        return self.name
