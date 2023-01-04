from enum import Enum, auto


class GitRepoObjectClass(Enum):
    ClassGitRepo = auto()
    ClassGitCommit = auto()

    def __str__(self):
        return self.name
