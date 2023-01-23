from enum import Enum, auto


class ServiceArgType(Enum):
    """
    Custom arg types used by :class:`ServiceLoader`.

    See also `FD-2023-01-23--1`.
    """

    CodeMaturity = auto()
    FlowStage = auto()
    GeoRegion = auto()
    ClusterName = auto()
    HostName = auto()
    ServiceName = auto()
    AccessType = auto()
    ColorTag = auto()

    def __str__(self):
        return self.name
