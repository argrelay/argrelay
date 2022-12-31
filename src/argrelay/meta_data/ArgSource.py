from enum import Enum, auto


class ArgSource(Enum):
    """
    Specifies how each :class:`ArgValue` was obtained.
    """

    # TODO: Do we even need this given default is conditional?
    #       Search for "default vs implicit" - defaults may not be known until other arg types are specified.
    # If there is a sensible static default:
    DefaultValue = auto()

    # If command line arg is explicitly provided:
    ExplicitArg = auto()
    # If any ExplicitArg or other ImplicitValue makes other values impossible:
    ImplicitValue = auto()

    # TODO: Do we even need to separate RuleBased and RankedValue (if RankedValue is also RuleBased)?
    #       Maybe delete RankedValue (use RuleBased generically) and add SingledOut if there is only one value left possible? But even in this case it is kind of RuleBased...
    # If some rule provided single value based on selected ExplicitArg and ImplicitValue values:
    RuleBased = auto()
    # If some rule provided multiple values based on selected ExplicitArg and ImplicitValue values:
    RankedValue = auto()

    def __str__(self):
        return self.name
