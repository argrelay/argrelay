from enum import Enum, auto


class ServiceArgType(Enum):
    """
    Custom arg types used by :class:`ServiceLoader`.

    See also:
    *   `FS_53_81_66_18` (TnC) for arg types.
    *   `TD_63_37_05_36` (demo) for `test_data`.
    """

    # ---

    code_maturity = auto()
    geo_region = auto()
    flow_stage = auto()

    # ---

    cluster_name = auto()

    # ---

    data_center = auto()
    host_name = auto()
    ip_address = auto()

    # FS_06_99_43_60: example of using non-scalar value (array|list):
    group_label = auto()

    service_name = auto()

    run_mode = auto()

    # ---

    access_type = auto()

    # ---

    live_status = auto()
    """
    TODO: Currently `live_status` is not used - it can be thought of as manually or dynamically assigned to the resource.
    """

    def __str__(self):
        return self.name
