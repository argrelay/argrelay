from enum import Enum, auto


class ServiceArgType(Enum):
    ActionType = auto()
    CodeMaturity = auto()
    FlowStage = auto()
    GeoRegion = auto()
    HostName = auto()
    AccessType = auto()
    ServerTag = auto()

    def __str__(self):
        return self.name
