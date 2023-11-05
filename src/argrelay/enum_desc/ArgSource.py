from enum import IntEnum


# TODO: TODO_66_66_75_78: Rename to prop source - see also `ReservedArgType` (to be renamed to `ReservedPropType`).
class ArgSource(IntEnum):
    """
    Specifies how each :class:`AssignedValue` was obtained.

    They are listed in the order of priority:
    *  The first one is the lowest priority = can be overriden by any other `ArgSource.*`
    *  The last one is the highest priority = cannot be overriden by any other `ArgSource.*`
    """

    # Default value selected via `fill_control` (FS_72_40_53_00).
    DefaultValue = 3

    # TODO: Provide detailed description in FS_13_51_07_97?
    # Provided in the envelope singled-out by the search:
    ImplicitValue = 4

    # If command line arg is explicitly provided as positional argument (`TokenType.PosArg`):
    ExplicitPosArg = 5

    # TODO: FS_20_88_05_60: named args
    # If command line arg is explicitly provided as named argument (`TokenType.KeyArg` + `TokenType.ValArg`):
    ExplicitNamedArg = 6

    # This is pre-assigned value which cannot be changed subsequently (the highest priority).
    # It is a value computed by plugin domain-specific logic with input from:
    # * Env vars.
    # * Config.
    # * Currently found `data_envelope`-s
    InitValue = 7

    def __str__(self):
        return self.name
