from enum import Enum, auto


class SpecialFunc(Enum):
    """
    See also: FS_80_45_89_81 / integrated functions
    """

    func_id_unplugged = auto()
    """
    Function which is not plugged anywhere.
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
