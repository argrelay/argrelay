from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.mongo_data.MongoClientWrapper import get_mongo_client
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.schema_config_core_server.MongoConfigSchema import mongo_config_desc
from env_tests.MongoClientTest import MongoClientTest


class ThisTestCase(MongoClientTest):

    # noinspection PyMethodMayBeStatic
    def test_live_envelope_searched_by_multiple_typed_vals(self):
        """
        Example with data searched by multiple { type: value } pairs
        """

        mongo_config = mongo_config_desc.from_input_dict(mongo_config_desc.dict_example)
        mongo_client = get_mongo_client(mongo_config)
        print("list_database_names: ", mongo_client.list_database_names())

        mongo_db: Database = mongo_client[mongo_config.mongo_server.database_name]
        print("list_collection_names: ", mongo_db.list_collection_names())

        col_name = "argrelay"
        col_proxy: Collection = mongo_db[col_name]

        self.remove_all_envelopes(col_proxy)

        known_arg_types = [
            ServiceArgType.AccessType.name,
            ServiceArgType.LiveStatus.name,
            ServiceArgType.CodeMaturity.name,
        ]

        envelope_001 = {
            "envelope_payload": {
                "object_name": "envelope_001",
            },
            ServiceArgType.AccessType.name: "ro",
        }

        envelope_002 = {
            "envelope_payload": {
                "object_name": "envelope_002",
            },
            ServiceArgType.AccessType.name: "rw",
            ServiceArgType.LiveStatus.name: "red",
        }

        envelope_003 = {
            "envelope_payload": {
                "object_name": "envelope_003",
            },
            ServiceArgType.AccessType.name: "rw",
            ServiceArgType.LiveStatus.name: "blue",
        }

        envelope_004 = {
            "envelope_payload": {
                "object_name": "envelope_004",
            },
            ServiceArgType.AccessType.name: "rw",
            ServiceArgType.LiveStatus.name: "red",
            ServiceArgType.CodeMaturity.name: "prod",
        }

        col_proxy.insert_many([
            envelope_001,
            envelope_002,
            envelope_003,
            envelope_004,
        ])

        for index_field in known_arg_types:
            col_proxy.create_index(index_field)

        print("query 1:")
        for data_envelope in col_proxy.find(
            {
                ServiceArgType.AccessType.name: "rw",
                ServiceArgType.LiveStatus.name: "red",
            }
        ):
            print("data_envelope: ", data_envelope)

        self.remove_all_envelopes(col_proxy)
