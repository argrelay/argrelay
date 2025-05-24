from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    mongo_id_,
)
from offline_tests.mongo_query.MongoClientTestClass import MongoClientTestClass


class ThisTestClass(MongoClientTestClass):

    # noinspection PyMethodMayBeStatic
    def test_tutorial(self):
        """
        Borrowed from: https://www.mongodb.com/languages/python
        """

        envelope_1 = {
            mongo_id_: "U1IT00001",
            "envelope_name": "Blender",
            "max_discount": "10%",
            "batch_number": "RR450020FRG",
            "price": 340,
            "category": "kitchen appliance",
        }

        envelope_2 = {
            mongo_id_: "U1IT00002",
            "envelope_name": "Egg",
            "category": "food",
            "quantity": 12,
            "price": 36,
            "envelope_description": "brown country eggs",
        }

        envelope_3 = {
            "envelope_name": "whatever",
            "category": "whatever",
            "batch_number": "whatever",
            "price": 999,
        }

        envelope_4 = {
            "envelope_name": "butter",
            "category": "food",
            "batch_number": "BU5E0020FK",
            "price": 20,
        }

        envelope_5 = {
            "envelope_name": "face cream",
            "category": "beauty",
            "max_discount": "4%",
            "ingredients": "Hyaluronic acid, Ceramides, vitamins A,C,E, fruit acids",
        }

        envelope_6 = {
            "envelope_name": "fishing plier",
            "category": "sports",
            "envelope_description": "comes with tungsten carbide cutters to easily cut fishing lines and hooks",
        }

        envelope_7 = {
            "envelope_name": "pizza sauce",
            "category": "food",
            "quantity": 5,
        }

        envelope_8 = {
            "envelope_name": "fitness band",
            "price": 300,
            "max_discount": "12%",
        }

        envelope_9 = {
            "envelope_name": "cinnamon",
            "category": "food",
            "warning": "strong smell, not to be consumed directly",
            "price": 2,
        }

        envelope_10 = {
            "envelope_name": "lego building set",
            "category": "toys",
            "warning": "very small parts, not suitable for children below 3 years",
            "parts_included": "colored interlocking plastic bricks, gears, minifigures, plates, cones, round bricks",
        }

        envelope_11 = {
            "envelope_name": "dishwasher",
            "category": "kitchen appliance",
            "warranty": "2 years",
        }

        envelope_12 = {
            "envelope_name": "running shoes",
            "brand": "Nike",
            "category": "sports",
            "price": 145,
            "max_discount": "5%",
        }

        envelope_13 = {
            "envelope_name": "leather bookmark",
            "category": "books",
            "design": "colored alphabets",
            "envelope_description": "hand-made, natural colors used",
        }

        envelope_14 = {
            "envelope_name": "maple syrup",
            "category": "food",
            "envelope_description": "A-grade, dark, organic, keep in refrigerator after opening",
            "price": 25,
        }

        self.col_proxy.insert_many(
            [
                envelope_1,
                envelope_2,
                envelope_3,
                envelope_4,
                envelope_5,
                envelope_6,
                envelope_7,
                envelope_8,
                envelope_9,
                envelope_10,
                envelope_11,
                envelope_12,
                envelope_13,
                envelope_14,
            ]
        )

        self.col_proxy.create_index("category")

        self.show_all_envelopes(self.col_proxy)
