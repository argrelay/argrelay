from enum import Enum, auto


class ReservedEnvelopeClass(Enum):
    """
    Names of the `data_envelope` classes reserved by `argrelay`.
    """

    ClassUnknown = auto()

    ClassFunction = auto()

    ClassHelp = auto()
    """
    See FS_71_87_33_52 help_hint.
    """

    ClassCollectionMeta = auto()
    """
    See FS_74_69_61_79 get set data envelope.
    """

    def __str__(self):
        return self.name
