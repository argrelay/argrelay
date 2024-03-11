from __future__ import annotations

from copy import deepcopy

import mongomock
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.misc_helper_common import eprint
from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.StaticData import StaticData
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_id_,
    data_envelope_desc,
    mongo_id_,
)


def get_mongo_client(mongo_config: MongoConfig):
    if mongo_config.use_mongomock:
        return mongomock.MongoClient()
    else:
        return MongoClient(mongo_config.mongo_client.client_connection_string)


def store_envelopes(
    mongo_db: Database,
    static_data: StaticData,
):
    # Calculate total:
    total_envelope_n: int = 0
    for mongo_collection in static_data.envelope_collections:
        envelope_collection: EnvelopeCollection = static_data.envelope_collections[
            mongo_collection
        ]
        total_envelope_n += len(envelope_collection.data_envelopes)

    # Index all:
    curr_envelope_i: int = 0
    for mongo_collection in static_data.envelope_collections:
        envelope_collection: EnvelopeCollection = static_data.envelope_collections[
            mongo_collection
        ]
        curr_envelope_i += store_envelope_collection(
            mongo_db,
            mongo_collection,
            envelope_collection,
            curr_envelope_i,
            total_envelope_n,
        )

    assert curr_envelope_i == total_envelope_n


def store_envelope_collection(
    mongo_db: Database,
    mongo_collection: str,
    envelope_collection: EnvelopeCollection,
    curr_envelope_i: int,
    total_envelope_n: int,
) -> int:
    col_proxy: Collection = mongo_db[mongo_collection]
    col_proxy.delete_many({})
    col_proxy.drop_indexes()

    base_curr_envelope_i: int = curr_envelope_i
    envelope_per_col_i: int = 0
    log_index_progress(mongo_collection, envelope_per_col_i, curr_envelope_i, total_envelope_n)
    for data_envelope in envelope_collection.data_envelopes:
        if curr_envelope_i % 1_000 == 0:
            log_index_progress(mongo_collection, envelope_per_col_i, curr_envelope_i, total_envelope_n)
        curr_envelope_i += 1
        envelope_per_col_i += 1
        envelope_to_store = deepcopy(data_envelope)

        try:
            data_envelope_desc.validate_dict(envelope_to_store)

            if envelope_id_ in envelope_to_store:
                envelope_to_store[mongo_id_] = data_envelope[envelope_id_]

            col_proxy.insert_one(envelope_to_store)
        except:
            print(f"envelope_to_store: {envelope_to_store}")
            # Rethrow previous error:
            raise

    log_index_progress(mongo_collection, envelope_per_col_i, curr_envelope_i, total_envelope_n)

    assert envelope_per_col_i == curr_envelope_i - base_curr_envelope_i
    return envelope_per_col_i


def log_index_progress(
    mongo_collection: str,
    envelope_per_col_i: int,
    curr_envelope_i: int,
    total_envelope_n: int,
):
    try:
        assert envelope_per_col_i <= curr_envelope_i <= total_envelope_n
    finally:
        eprint(
            f"collection: {mongo_collection}: indexed envelopes: {envelope_per_col_i}/{curr_envelope_i}/{total_envelope_n}..."
        )


def create_index(
    mongo_db: Database,
    collection_name: str,
    index_fields: list[str],
):
    col_proxy: Collection = mongo_db[collection_name]

    for index_field in index_fields:
        col_proxy.create_index(index_field)
