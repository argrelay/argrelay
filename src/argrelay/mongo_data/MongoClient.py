from __future__ import annotations

from copy import deepcopy

# TODO: rename this module from MongoClient as it matches pymongo.MongoClient class not locally owned one.
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.api_ext.meta_data.DataObjectSchema import object_id_
from argrelay.api_ext.relay_server.StaticData import StaticData
from argrelay.api_ext.relay_server.StaticDataSchema import data_objects_
from argrelay.api_int.meta_data import ArgValue
from argrelay.mongo_data.MongoConfig import MongoConfig


def get_mongo_client(mongo_config: MongoConfig):
    return MongoClient(mongo_config.client_connection_string)


def store_objects(mongo_db: Database, static_data: StaticData):
    col_object: Collection = mongo_db[data_objects_]
    col_object.delete_many({})

    for data_object in static_data.data_objects:
        object_to_store = deepcopy(data_object)
        if object_id_ in object_to_store:
            object_to_store["_id"] = data_object[object_id_]
        col_object.insert_one(object_to_store)


def find_objects(mongo_db: Database, assigned_types_to_values: dict[str, ArgValue]):
    print("mongo_db: ", mongo_db)
    print("assigned_types_to_values: ", assigned_types_to_values)
    col_object: Collection = mongo_db[data_objects_]
    query_dict = {}
    for arg_type, arg_val in assigned_types_to_values.items():
        query_dict[arg_type] = arg_val.arg_value

    return col_object.find(query_dict)
