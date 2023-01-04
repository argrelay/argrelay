from enum import Enum, auto


class ServiceArgType(Enum):
    CodeMaturity = auto()
    FlowStage = auto()
    GeoRegion = auto()
    HostName = auto()
    ServiceName = auto()
    AccessType = auto()
    ColorTag = auto()

    def __str__(self):
        return self.name
