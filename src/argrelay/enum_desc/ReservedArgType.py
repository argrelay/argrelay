from enum import Enum, auto


# TODO: TODO_66_66_75_78: Rename to `ReservedPropType` (or `ReservedPropName`?) - see term dictionary.
class ReservedArgType(Enum):
    """
    Some of the `data_envelope` props used to implement various `argrelay` features.
    """

    EnvelopeClass = auto()

    FuncId = auto()
    """
    Used by FS_26_43_73_72 func tree to distinguish leaves (func ids).
    It is normally the same with `FunctionEnvelopeInstanceDataSchema.func_id_`.
    """

    ArgType = auto()

    ArgValue = auto()

    HelpHint = auto()
