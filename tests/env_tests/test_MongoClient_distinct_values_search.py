from offline_tests.mongo_query import test_MongoClient_distinc_values_search


class ThisTestClass(test_MongoClient_distinc_values_search.ThisTestClass):
    """
    Reconfigures existing tests to run against real MongoDB.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super(
            ThisTestClass,
            self,
        ).__init__(
            *args,
            **kwargs,
        )

        self.use_mongomock = False
