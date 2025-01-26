from enum import (
    auto,
    Enum,
)


class GitRepoEnvelopeClass(Enum):
    class_git_repo = auto()
    class_git_tag = auto()
    class_git_commit = auto()

    def __str__(self):
        return self.name
