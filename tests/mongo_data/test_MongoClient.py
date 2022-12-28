from unittest import TestCase, skip

from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.mongo_data.MongoClient import get_mongo_client
from argrelay.mongo_data.MongoConfigSchema import mongo_config_desc


class ThisTestCase(TestCase):

    @staticmethod
    def show_all_items(col_object: Collection):
        for item_object in col_object.find():
            print("item_object: ", item_object)

    @staticmethod
    def remove_all_items(col_object):
        col_object.delete_many({})

    # noinspection PyMethodMayBeStatic
    @skip
    def test_live_mongo(self):
        mongo_config = mongo_config_desc.from_input_dict(mongo_config_desc.dict_example)
        mongo_client = get_mongo_client(mongo_config)
        print("list_database_names: ", mongo_client.list_database_names())

        mongo_db: Database = mongo_client[mongo_config.database_name]
        print("list_collection_names: ", mongo_db.list_collection_names())

        col_name = "user_1_items"
        col_object: Collection = mongo_db[col_name]

        self.show_all_items(col_object)

        self.remove_all_items(col_object)

        item_1 = {
            "_id": "U1IT00001",
            "item_name": "Blender",
            "max_discount": "10%",
            "batch_number": "RR450020FRG",
            "price": 340,
            "category": "kitchen appliance",
        }

        item_2 = {
            "_id": "U1IT00002",
            "item_name": "Egg",
            "category": "food",
            "quantity": 12,
            "price": 36,
            "item_description": "brown country eggs",
        }

        item_3 = {
            "item_name": "whatever",
            "category": "whatever",
            "batch_number": "whatever",
            "price": 999,
        }

        item_4 = {
            "item_name": "butter",
            "category": "food",
            "batch_number": "BU5E0020FK",
            "price": 20,
        }

        item_5 = {
            "item_name": "face cream",
            "category": "beauty",
            "max_discount": "4%",
            "ingredients": "Hyaluronic acid, Ceramides, vitamins A,C,E, fruit acids",
        }

        item_6 = {
            "item_name": "fishing plier",
            "category": "sports",
            "item_description": "comes with tungsten carbide cutters to easily cut fishing lines and hooks",
        }

        item_7 = {
            "item_name": "pizza sauce",
            "category": "food",
            "quantity": 5,
        }

        item_8 = {
            "item_name": "fitness band",
            "price": 300,
            "max_discount": "12%",
        }

        item_9 = {
            "item_name": "cinnamon",
            "category": "food",
            "warning": "strong smell, not to be consumed directly",
            "price": 2,
        }

        item_10 = {
            "item_name": "lego building set",
            "category": "toys",
            "warning": "very small parts, not suitable for children below 3 years",
            "parts_included": "colored interlocking plastic bricks, gears, minifigures, plates, cones, round bricks",
        }

        item_11 = {
            "item_name": "dishwasher",
            "category": "kitchen appliance",
            "warranty": "2 years",
        }

        item_12 = {
            "item_name": "running shoes",
            "brand": "Nike",
            "category": "sports",
            "price": 145,
            "max_discount": "5%",
        }

        item_13 = {
            "item_name": "leather bookmark",
            "category": "books",
            "design": "colored alphabets",
            "item_description": "hand-made, natural colors used",
        }

        item_14 = {
            "item_name": "maple syrup",
            "category": "food",
            "item_description": "A-grade, dark, organic, keep in refrigerator after opening",
            "price": 25,
        }

        col_object.insert_many([
            item_1,
            item_2,
            item_3,
            item_4,
            item_5,
            item_6,
            item_7,
            item_8,
            item_9,
            item_10,
            item_11,
            item_12,
            item_13,
            item_14,
        ])

        col_object.create_index("category")
