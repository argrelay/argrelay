from dataclasses import dataclass

from argrelay.enum_desc.ArgSource import ArgSource


@dataclass
class AssignedValue:
    arg_value: str
    arg_source: ArgSource
