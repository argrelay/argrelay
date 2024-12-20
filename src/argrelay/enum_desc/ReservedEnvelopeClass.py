from enum import Enum, auto


class ReservedEnvelopeClass(Enum):
    """
    Names of the `data_envelope` classes reserved by `argrelay`.
    """

    ClassUnknown = auto()

    class_function = auto()

    class_help = auto()
    """
    See FS_71_87_33_52 help_hint.
    """

    class_collection = auto()
    """
    See FS_74_69_61_79 get set data envelope.
    """

    class_no_data = auto()
    """
    Class which is supposed to have no `data_envelope`-s loaded.

    See also `SpecialFunc.func_id_no_data`.
    """

    def __str__(self):
        return self.name
