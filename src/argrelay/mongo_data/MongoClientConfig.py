from dataclasses import dataclass


@dataclass
class MongoClientConfig:
    # Example:
    # "mongodb://test:test@localhost/test?authSource=admin"
    client_connection_string: str
