from enum import IntEnum


class ValueSource(IntEnum):
    """
    Specifies how each :class:`AssignedValue` was obtained.

    They are listed in the order of priority:
    *  The first one is the lowest priority = can be overridden by any other `ValueSource.*`
    *  The last one is the highest priority = cannot be overridden by any other `ValueSource.*`
    """

    # Default value selected via `fill_control` (FS_72_40_53_00).
    default_value = 3

    # TODO: Provide detailed description in FS_13_51_07_97?
    # Provided in the envelope singled-out by the search:
    implicit_value = 4

    # If command line arg is explicitly provided as FS_96_46_42_30 `offered_arg`:
    explicit_offered_arg = 5

    # If command line arg is explicitly provided as FS_20_88_05_60 `dictated_arg`:
    explicit_dictated_arg = 6

    # This is pre-assigned value which cannot be changed subsequently (the highest priority).
    # It is a value computed by plugin domain-specific logic with input from:
    # * Env vars.
    # * Config.
    # * Currently found `data_envelope`-s
    init_value = 7

    def __str__(self):
        return self.name
