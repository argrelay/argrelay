from __future__ import annotations

from enum import Enum, auto


class GitRepoArgType(Enum):
    # Git root path relative to `base_path_`:
    GitRepoRelPath = auto()
    # Path component leading to Git repo root path (e.g. ["qwer", "asdf", "zxcv"] of "zxcv/qwer/asdf"):
    GitRepoPathComp = auto()
    # Git remote, for example: "git@github.com:uvsmtid/argrelay.git"
    GitRepoRemoteUrl = auto()
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
