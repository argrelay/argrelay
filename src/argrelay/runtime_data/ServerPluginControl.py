from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.composite_tree.CompositeForest import CompositeForest


@dataclass(frozen = True)
class ServerPluginControl:
    """
    Configures (controls) usage of plugins by the server.

    See also `ServerPluginControlSchema.py`.
    """

    first_interp_factory_id: str = field()

    reusable_config_data: str = field()

    composite_forest: CompositeForest = field()
