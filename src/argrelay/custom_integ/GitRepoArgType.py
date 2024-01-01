from __future__ import annotations

from enum import Enum, auto


class GitRepoArgType(Enum):
    """
    Envelope arg types (properties) used by `GitRepoLoader`.
    """

    # Short name for a repo (to avoid specifying its `GitRepoRootRelPath`):
    GitRepoAlias = auto()

    # Absolute path common to multiple Git repos - what `GitRepoRootRelPath` are relative to:
    GitRepoRootAbsPath = auto()

    # Git root path relative to `GitRepoRootAbsPath`:
    GitRepoRootRelPath = auto()

    # Git root dir base name:
    GitRepoRootBaseName = auto()

    # Categorize repo content: conf, code, ...
    GitRepoContentType = auto()

    # FS_06_99_43_60: example of using non-scalar value (array|list):
    # Path component leading to Git repo root path (e.g. ["qwer", "asdf", "zxcv"] of "zxcv/qwer/asdf"):
    GitRepoPathComp = auto()

    # TODO: clean up or make use of:
    # FS_06_99_43_60: example of using non-scalar value (array|list):
    # Git remote, for example: "git@github.com:uvsmtid/argrelay.git"
    GitRepoRemoteUrl = auto()

    # TODO: clean up or make use of:
    # FS_06_99_43_60: example of using non-scalar value (array|list):
    # Git local branch name:
    GitRepoLocalBranch = auto()

    # Git commit, for example: 52a3d54d17fe5cba6bad57abc4b6bebd881d3ce6
    GitRepoCommitId = auto()

    # Git commit comment:
    GitRepoCommitMessage = auto()

    # Git commit author name:
    GitRepoCommitAuthorName = auto()

    # Git commit author email:
    GitRepoCommitAuthorEmail = auto()

    def __str__(self):
        return self.name
