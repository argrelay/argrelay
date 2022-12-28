from pymongo import MongoClient

from argrelay.mongo_data.MongoConfig import MongoConfig


def get_mongo_client(mongo_config: MongoConfig):
    return MongoClient(mongo_config.client_connection_string)
