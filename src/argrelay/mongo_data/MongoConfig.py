from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay.mongo_data.MongoClientConfig import MongoClientConfig
from argrelay.mongo_data.MongoServerConfig import MongoServerConfig


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
