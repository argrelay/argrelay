from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from argrelay_lib_root.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay_schema_config_server.runtime_data_server_app.MongoClientConfig import (
    MongoClientConfig,
)
from argrelay_schema_config_server.runtime_data_server_app.MongoServerConfig import (
    MongoServerConfig,
)


@dataclass
class MongoConfig:
    use_mongomock: bool = field()
    """
    See :class:`MongoConfigSchema.use_mongomock`.
    """

    distinct_values_query: DistinctValuesQuery = field()
    """
    See `DistinctValuesQuery`.
    """

    mongo_client: MongoClientConfig = field()

    mongo_server: MongoServerConfig = field()
