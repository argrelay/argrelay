from dataclasses import dataclass

from argrelay.enum_desc.ArgSource import ArgSource


# TODO: Forget about coords everywhere (rename `coord` to something else unless it's just an analogy).
#       Use args for input.
@dataclass
class AssignedValue:
    arg_value: str
    arg_source: ArgSource
