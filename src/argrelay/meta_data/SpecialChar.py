from enum import Enum


class SpecialChar(Enum):
    value: str

    TokenDelimiter = "\\s+"
    KeyValueDelimiter = ":"
