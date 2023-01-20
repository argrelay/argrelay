from enum import auto, IntEnum


class ArgSource(IntEnum):
    """
    Specifies how each :class:`ArgValue` was obtained.

    They are listed in the order of priority:
    *  The first one is the lowest priority = can be overriden by any other `ArgSource.*`
    *  The last one is the highest priority = cannot be overriden by any other `ArgSource.*`
    """

    # TODO: The context should be specify-able in the client config (TODO: low priority use case).
    #       TODO: See "over-specified" context in FD-2023-01-17--1:
    #       it might be a useless in simple/dumb implementation by hiding envelopes.
    ConfigValue = 1

    # TODO: The context should be specify-able in the env var (TODO: low priority use case).
    #       TODO: See "over-specified" context in FD-2023-01-17--1:
    #       it might be a useless in simple/dumb implementation by hiding envelopes.
    EnvVarValue = 2

    # TODO: Search for "default vs implicit" - defaults may not be known until other arg types are specified.
    # It was initially thought of as `DefaultValue`, but this is cannot be the default applicable to all.
    # Instead, it is a value computed through rules with input from:
    # * Static config.
    # * Some special keys in `data_envelope` (`context_control`).
    # * Plugins.
    ComputedValue = 3

    # TODO: Provide detailed description in FD-2023-01-17--3?
    # TODO: Actually, to provide implicit value, the envelope should not necessarily be singled out.
    #       If a set of all envelopes constrained by current context provide the same value for some type,
    #       such value should be implied (and user should not be proposed/interrogated for that).
    # Provided in the envelope singled-out by the search:
    ImplicitValue = 4

    # If command line arg is explicitly provided as positional argument (`TokenType.PosArg`):
    ExplicitPosArg = 5

    # If command line arg is explicitly provided as named argument (`TokenType.KeyArg` + `TokenType.ValArg`):
    ExplicitNamedArg = 6

    def __str__(self):
        return self.name
