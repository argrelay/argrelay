from dataclasses import dataclass


@dataclass
class MongoServerConfig:
    # Example:
    # "test"
    database_name: str

    start_server: bool

    # Example:
    # "~/argrelay.git/temp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/argrelay.git/temp/mongo/data"
    server_start_command: str
