from enum import (
    auto,
    Enum,
)


class PluginSide(Enum):
    """
    Specifies which side client can be used at.
    """

    PluginServerSideOnly = auto()

    PluginClientSideOnly = auto()

    PluginAnySide = auto()

    def __str__(self):
        return self.name
