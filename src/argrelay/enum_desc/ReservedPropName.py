from enum import Enum, auto


class ReservedPropName(Enum):
    """
    Some of the `data_envelope` props used to implement various `argrelay` features.
    """

    collection_name = auto()

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

    # TODO: TODO_66_66_75_78.split_arg_and_prop_concepts: Rename: `arg_type` to `prop_name`:
    # TODO: Review: how it is used. Should it be renamed to `prop_name`? Does it make sense to have a property named as `prop_name`?
    arg_type = auto()

    # TODO: TODO_66_66_75_78.split_arg_and_prop_concepts: Rename: `arg_type` to `prop_name`:
    # TODO: Review: how it is used. Should it be renamed to `prop_value`? Does it make sense to have a property named as `prop_value`?
    arg_value = auto()

    help_hint = auto()

    func_state = auto()
