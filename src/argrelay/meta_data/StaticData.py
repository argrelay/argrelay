from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class StaticData:
    """
    All data which normally does not change between requests
    """

    first_interp_factory_id: str = field(init = True, default = "")

    # TODO: It is currently populated, but not used.
    #       It should probably be populated with config how to index these types in MongoDB:
    known_types: list = field(init = True, default_factory = lambda: [])

    data_envelopes: list = field(init = True, default_factory = lambda: [])
