from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class StaticData:
    """
    All data which normally does not change between requests.

    See also `StaticDataSchema.py`.
    """

    known_arg_types: list = field()
    """
    TODO_26_75_13_27:
    Field `known_arg_types` lists fields of `data_envelop` - they are used to create MongoDB index.
    """

    data_envelopes: list = field()
