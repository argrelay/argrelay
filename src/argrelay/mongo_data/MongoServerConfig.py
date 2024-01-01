from dataclasses import dataclass, field


@dataclass
class MongoServerConfig:
    # Example:
    # "test"
    database_name: str = field()

    start_server: bool = field()

    # Example:
    # "~/argrelay.git/tmp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/argrelay.git/tmp/mongo/data"
    server_start_command: str = field()
