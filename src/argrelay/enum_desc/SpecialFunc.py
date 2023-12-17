from enum import Enum, auto


class SpecialFunc(Enum):
    """
    See also: FS_80_45_89_81 / integrated functions
    """

    intercept_invocation_func = auto()
    """
    Implements FS_88_66_66_73 intercept func.
    """

    help_hint_func = auto()
    """
    Implements FS_71_87_33_52 help hint.
    """

    echo_args_func = auto()
    """
    Implements FS_43_50_57_71 `echo_args` func.
    """

    query_enum_items_func = auto()
    """
    Implements FS_02_25_41_81 `query_enum_items_func`.
    """
