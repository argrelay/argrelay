from enum import Enum, auto


class ServiceArgType(Enum):
    """
    Custom arg types used by :class:`ServiceLoader`.

    See also:
    *   `FS_53_81_66_18` (TnC) for arg types.
    *   `TD_63_37_05_36` (demo) for `test_data`.
    """

    # ---

    CodeMaturity = auto()
    GeoRegion = auto()
    FlowStage = auto()

    # ---

    ClusterName = auto()

    # ---

    DataCenter = auto()
    HostName = auto()
    IpAddress = auto()
    GroupLabel = auto()
    ServiceName = auto()

    # ---

    AccessType = auto()

    # ---

    LiveStatus = auto()
    """
    TODO: Currently `LiveStatus` is not used - it can be thought of as manually or dynamically assigned to the resource.
    """

    def __str__(self):
        return self.name
