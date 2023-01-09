from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class StaticData:
    """
    All data which normally does not change between requests
    """

    first_interp_factory_id: str = field(init = True, default = "")
    types_to_values: dict[str, list[str]] = field(init = True, default_factory = lambda: {})
    data_envelopes: list = field(init = True, default_factory = lambda: [])
