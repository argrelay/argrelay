from enum import Enum, auto


class ServicePropName(Enum):
    """
    Custom `prop_name`-s used by :class:`ServiceLoader`.

    See also:
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

    # FS_06_99_43_60: example of using non-scalar `prop_value` (array):
    group_label = auto()

    service_name = auto()

    run_mode = auto()

    # ---

    access_type = auto()

    # ---

    user_name = auto()

    # ---

    dir_path = auto()

    # ---

    live_status = auto()
    """
    A value manually or dynamically assigned to the resource indicating its status.
    """

    def __str__(self):
        return self.name
