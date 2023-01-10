from __future__ import annotations

from copy import deepcopy

import mongomock
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.meta_data.ArgValue import ArgValue
from argrelay.meta_data.StaticData import StaticData
from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_


def get_mongo_client(mongo_config: MongoConfig):
    if mongo_config.use_mongomock_only:
        return mongomock.MongoClient()
    else:
        return MongoClient(mongo_config.mongo_client.client_connection_string)


def store_envelopes(mongo_db: Database, static_data: StaticData):
    col_proxy: Collection = mongo_db[data_envelopes_]
    col_proxy.delete_many({})

    for data_envelope in static_data.data_envelopes:
        envelope_to_store = deepcopy(data_envelope)
        if envelope_id_ in envelope_to_store:
            envelope_to_store["_id"] = data_envelope[envelope_id_]
        col_proxy.insert_one(envelope_to_store)


def find_envelopes(mongo_db: Database, assigned_types_to_values: dict[str, ArgValue]):
    col_proxy: Collection = mongo_db[data_envelopes_]
    query_dict = {}
    for arg_type, arg_val in assigned_types_to_values.items():
        query_dict[arg_type] = arg_val.arg_value

    return col_proxy.find(query_dict)
