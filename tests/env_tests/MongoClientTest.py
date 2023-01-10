from unittest import TestCase

from pymongo.collection import Collection


class MongoClientTest(TestCase):

    @staticmethod
    def show_all_envelopes(col_proxy: Collection):
        print("show_all_envelopes:")
        for data_envelope in col_proxy.find():
            print("data_envelope: ", data_envelope)

    @staticmethod
    def remove_all_envelopes(col_proxy):
        col_proxy.delete_many({})
