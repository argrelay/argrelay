from enum import Enum, auto


class ReservedPropName(Enum):
    """
    Some of the `data_envelope` props used to implement various `argrelay` features.
    """

    collection_name = auto()
    """
    Normally, `collection_name` is not part of `data_envelope` - instead, it is only used in MongoDB query API.
    But it is part of `data_envelope` (see FS_74_69_61_79 get set data envelope)
    with `ReservedEnvelopeClass.class_collection` `envelope_class`.
    """

    # TODO: Maybe rename to `envelope_class` everywhere for consistency?
    envelope_class = auto()
    """
    See also synonym `class_name`.
    """

    func_id = auto()
    """
    Used by FS_26_43_73_72 func tree to distinguish leaves (func ids).
    It is normally the same with `FunctionEnvelopeInstanceDataSchema.func_id_`.
    """

    prop_name = auto()

    prop_value = auto()

    help_hint = auto()

    func_state = auto()
