from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class StaticData:
    """
    All data which normally does not change between requests
    """

    first_interp_factory_id: str = field(init = True, default = "")

    known_arg_types: list = field(init = True, default_factory = lambda: [])
    """
    TODO: rename to make it explicit that it is indexed fields.
    Field `known_arg_types` lists fields of `data_envelop` - they are used to create MongoDB index.
    """

    data_envelopes: list = field(init = True, default_factory = lambda: [])
