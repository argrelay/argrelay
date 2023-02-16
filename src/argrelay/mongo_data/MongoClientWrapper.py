from __future__ import annotations

from copy import deepcopy

import mongomock
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.misc_helper import eprint
from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_, data_envelope_desc, mongo_id_


def get_mongo_client(mongo_config: MongoConfig):
    if mongo_config.use_mongomock_only:
        return mongomock.MongoClient()
    else:
        return MongoClient(mongo_config.mongo_client.client_connection_string)


def store_envelopes(mongo_db: Database, static_data: StaticData):
    # TODO: Currently, we use single collection,
    #       but we never search across all object,
    #       we always search specific `ReservedArgType.EnvelopeClass.name`.
    #       Should we use collection per envelope class?
    #       However, what if we need to list all envelop classes?
    #       Then, single collection is fine (and simple).
    col_proxy: Collection = mongo_db[data_envelopes_]
    col_proxy.delete_many({})

    envelope_i: int = 0
    envelope_n = len(static_data.data_envelopes)
    for data_envelope in static_data.data_envelopes:
        if envelope_i % 1_000 == 0:
            eprint(f"indexed envelopes {envelope_i}/{envelope_n}...")
        envelope_i += 1
        envelope_to_store = deepcopy(data_envelope)
        data_envelope_desc.validate_dict(envelope_to_store)
        if envelope_id_ in envelope_to_store:
            envelope_to_store[mongo_id_] = data_envelope[envelope_id_]
        col_proxy.insert_one(envelope_to_store)


def create_index(mongo_db: Database, static_data: StaticData):
    col_proxy: Collection = mongo_db[data_envelopes_]

    for index_field in static_data.known_arg_types:
        col_proxy.create_index(index_field)


def find_envelopes(mongo_db: Database, assigned_types_to_values: dict[str, AssignedValue]):
    col_proxy: Collection = mongo_db[data_envelopes_]
    query_dict = {}
    for arg_type, arg_val in assigned_types_to_values.items():
        query_dict[arg_type] = arg_val.arg_value

    return col_proxy.find(query_dict)
