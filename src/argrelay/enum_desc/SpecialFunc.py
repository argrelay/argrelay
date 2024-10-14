from enum import Enum, auto


class SpecialFunc(Enum):
    """
    See also: FS_80_45_89_81 / integrated functions
    """

    func_id_unplugged = auto()
    """
    Function which is not plugged anywhere.
    """

    func_id_no_data = auto()
    """
    Function which has no data it searches for via FS_31_70_49_15 `search_control`.

    Such func is required for testing.
    This case allows defining funcs on start (statically) while adding data later (dynamically).
    """

    func_id_intercept_invocation = auto()
    """
    Implements FS_88_66_66_73 intercept func.
    """

    func_id_help_hint = auto()
    """
    Implements FS_71_87_33_52 help hint.
    """

    func_id_echo_args = auto()
    """
    Implements FS_43_50_57_71 `echo_args` func.
    """

    func_id_query_enum_items = auto()
    """
    Implements FS_02_25_41_81 `func_id_query_enum_items`.
    """

    func_id_get_data_envelopes = auto()
    """
    Implements "get" of FS_74_69_61_79 get set data envelope.
    """

    func_id_set_data_envelopes = auto()
    """
    Implements "set" of FS_74_69_61_79 get set data envelope.
    """
