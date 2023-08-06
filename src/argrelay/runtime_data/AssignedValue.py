from dataclasses import dataclass, field

from argrelay.enum_desc.ArgSource import ArgSource


@dataclass
class AssignedValue:
    arg_value: str = field()
    arg_source: ArgSource = field()
