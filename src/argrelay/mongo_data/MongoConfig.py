from __future__ import annotations

from dataclasses import dataclass

from argrelay.mongo_data.MongoClientConfig import MongoClientConfig
from argrelay.mongo_data.MongoServerConfig import MongoServerConfig


@dataclass
class MongoConfig:
    use_mongomock_only: bool
    """
    See :class:`MongoConfigSchema.use_mongomock_only`.
    """

    mongo_client: MongoClientConfig

    mongo_server: MongoServerConfig
