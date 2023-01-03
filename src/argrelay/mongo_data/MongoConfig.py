from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MongoConfig:
    # Example:
    # "mongodb://test:test@localhost/test?authSource=admin"
    client_connection_string: str

    # Example:
    # "test"
    database_name: str

    start_server: bool

    # Example:
    # "~/argrelay.git/temp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/argrelay.git/temp/mongo/data"
    server_start_command: str
