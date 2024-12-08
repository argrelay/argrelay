from __future__ import annotations

from copy import deepcopy

import mongomock
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.mongo_data.MongoConfig import MongoConfig
from argrelay.mongo_data.ProgressTracker import ProgressTracker
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
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
    cleaned_mongo_collections: set[str],
    envelope_collections: list[EnvelopeCollection],
    progress_tracker: ProgressTracker,
):
    # Calculate total:
    for envelope_collection in envelope_collections:
        progress_tracker.total_envelope_n += len(envelope_collection.data_envelopes)

    # Index all:
    for envelope_collection in envelope_collections:
        store_envelope_collection(
            mongo_db,
            cleaned_mongo_collections,
            envelope_collection,
            progress_tracker,
        )

    assert progress_tracker.total_envelope_i == progress_tracker.total_envelope_n


def delete_data_envelopes(
    mongo_db: Database,
    collection_name: str,
    query_dict: dict,
) -> None:
    col_proxy: Collection = mongo_db[collection_name]
    col_proxy.delete_many(query_dict)


def store_envelope_collection(
    mongo_db: Database,
    cleaned_mongo_collections: set[str],
    envelope_collection: EnvelopeCollection,
    progress_tracker: ProgressTracker,
) -> None:
    collection_name = envelope_collection.collection_name
    col_proxy: Collection = mongo_db[collection_name]
    if collection_name not in cleaned_mongo_collections:
        col_proxy.delete_many({})
        col_proxy.drop_indexes()
        cleaned_mongo_collections.add(collection_name)

    progress_tracker.track_collection_indexing_start(
        collection_name,
        len(envelope_collection.data_envelopes),
    )

    for data_envelope in envelope_collection.data_envelopes:

        progress_tracker.track_collection_indexing_increment(collection_name)
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

    progress_tracker.track_collection_indexing_stop(collection_name)


def create_index(
    mongo_db: Database,
    collection_name: str,
    index_props: list[str],
):
    col_proxy: Collection = mongo_db[collection_name]

    for index_prop in index_props:
        col_proxy.create_index(index_prop)
