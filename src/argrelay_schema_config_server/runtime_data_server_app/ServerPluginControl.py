from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from argrelay_schema_config_server.runtime_data_server_app.CompositeForest import (
    CompositeForest,
)


@dataclass(frozen=True)
class ServerPluginControl:
    """
    Configures (controls) usage of plugins by the server.

    See also `ServerPluginControlSchema.py`.
    """

    first_interp_factory_id: str = field()

    composite_forest: CompositeForest = field()
