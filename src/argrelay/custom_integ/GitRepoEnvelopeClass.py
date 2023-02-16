from enum import Enum, auto


class GitRepoEnvelopeClass(Enum):
    ClassGitRepo = auto()
    ClassGitCommit = auto()

    def __str__(self):
        return self.name
