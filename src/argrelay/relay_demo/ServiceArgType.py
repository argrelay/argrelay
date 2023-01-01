from enum import Enum, auto


class ServiceArgType(Enum):
    ActionType = auto()
    ObjectSelector = auto()
    CodeMaturity = auto()
    FlowStage = auto()
    GeoRegion = auto()
    HostName = auto()
    ServiceName = auto()
    AccessType = auto()
    ColorTag = auto()

    def __str__(self):
        return self.name
