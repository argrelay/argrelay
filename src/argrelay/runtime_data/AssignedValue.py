from dataclasses import dataclass, field

from argrelay.enum_desc.ValueSource import ValueSource


@dataclass
class AssignedValue:
    prop_value: str = field()
    value_source: ValueSource = field()
