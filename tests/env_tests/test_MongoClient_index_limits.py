from enum import Enum, auto

from env_tests.MongoClientTest import MongoClientTest


class TestSize(Enum):
    SmallSize = auto()
    """
    Works for both `pymongo` and `mongomock`.
    """

    MediumSize = auto()
    """
    Works for both `pymongo` and `mongomock`.
    But it is maximum size for `pymongo`.
    """

    LargeSize = auto()
    """
    Works only for `mongomock`.
    """


# TODO: Run this test in `offline_tests` with override to use `mongomock` and here without that override:
class ThisTestCase(MongoClientTest):

    def __init__(self, *args, **kwargs):
        super(MongoClientTest, self).__init__(*args, **kwargs)

        self.test_size = TestSize.SmallSize

        if self.test_size == TestSize.SmallSize:
            self.field_count = 17
            self.envelope_count = 163
            self.max_value_ordinal = 11
            self.max_array_size = 19

            self.col_query = {
                "field_8": "scalar_value_8",
                "field_11": "array_value_1",
                "field_3": "array_value_3",
            }

        if self.test_size == TestSize.MediumSize:
            # Maximum number of indexes in MongoDB = 64:
            # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Number-of-Indexes-per-Collection
            self.field_count = 63
            self.envelope_count = 7057
            self.max_value_ordinal = 379
            self.max_array_size = 113

            self.col_query = {
                "field_3": "array_value_3",
                "field_7": "array_value_56",
                "field_31": "array_value_46",
                "field_51": "array_value_26",
            }

        if self.test_size == TestSize.LargeSize:
            self.field_count = 263
            self.envelope_count = 7057
            self.max_value_ordinal = 379
            self.max_array_size = 113

            self.col_query = {
                "field_3": "array_value_3",
                "field_11": "array_value_259",
                "field_83": "array_value_343",
            }

        self.assertTrue(
            self.field_count * self.envelope_count * self.max_array_size < 1_000_000_000,
            "estimated (roughly) mem size should not exceed 1 G"
        )

        self.curr_value_ordinal = 1
        self.curr_array_size = 1
        # the other one is "array"
        self.curr_array_field_value_type = "scalar"

    # noinspection PyMethodMayBeStatic
    def test_live_index_limits(self):
        """
        Test mongodb index limits:
        *   generates field names to be indexed
        *   decides which field will contain array values or not
        *   generates `data_envelope`-s with generated values
        *   array fields of `data_envelope`-s are populated with either scalar or array
        *   runs few queries

        Note:
        These limitation to have multiple fields with array values actually
        *   apply for `pymongo`
        *   do not apply for `mongomock`
        # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Number-of-Indexes-per-Collection
        Real MongoDB (`pymongo`) fails for larger numbers with this:
        ```
        pymongo.errors.OperationFailure: add index fails, too many indexes for argrelay.argrelay key:{ field_61: 1 }, full error: {'ok': 0.0, 'errmsg': 'add index fails, too many indexes for argrelay.argrelay key:{ field_61: 1 }', 'code': 67, 'codeName': 'CannotCreateIndex'}
        ```
        """

        col_proxy = self.create_collection_proxy("argrelay")

        self.remove_all_envelopes(col_proxy)

        # Fields which will be indexed:
        known_arg_types = self.generate_field_names()

        array_field_names = self.decide_array_field_names(known_arg_types)

        data_envelopes = self.generate_data_envelopes(known_arg_types, array_field_names)

        col_proxy.insert_many(data_envelopes)

        self.index_fields(col_proxy, known_arg_types)

        # noinspection PyUnreachableCode
        if False:
            self.show_all_envelopes(col_proxy)

        print("query 1:")
        for data_envelope in col_proxy.find(self.col_query):
            print("data_envelope: ", data_envelope)

    def generate_field_names(self) -> list[str]:
        field_names = []
        for field_n in range(1, self.field_count + 1):
            field_names.append(f"field_{field_n}")
        return field_names

    # noinspection PyMethodMayBeStatic
    def decide_array_field_names(
        self,
        field_names,
    ):
        """
        even = scalar fields
        odd = array fields
        """
        array_field_names = []
        for field_n in range(1, len(field_names) + 1):
            if field_n % 2 != 0:
                array_field_names.append(field_names[field_n - 1])
        return array_field_names

    def generate_data_envelopes(
        self,
        field_names: list[str],
        array_field_names: list[str],
    ) -> list[dict]:
        data_envelopes = []
        for envelope_n in range(1, self.envelope_count + 1):
            data_envelope = self.generate_data_envelope(field_names, array_field_names)
            data_envelopes.append(data_envelope)
            if envelope_n % 1_000 == 0:
                print(f"{envelope_n}/{self.envelope_count}")
        return data_envelopes

    def generate_data_envelope(
        self,
        field_names: list[str],
        array_field_names: list[str],
    ) -> dict:
        data_envelope = {}
        for field_name in field_names:
            if field_name in array_field_names:
                self.generate_array_field_values(data_envelope, field_name)
            else:
                self.generate_field_scalar_value(data_envelope, field_name)
        return data_envelope

    def generate_array_field_values(
        self,
        data_envelope: dict,
        array_field_name: str,
    ) -> None:
        if self.curr_array_field_value_type == "array":
            self.generate_field_array_values(data_envelope, array_field_name)
        else:
            self.generate_field_scalar_value(data_envelope, array_field_name)
        self.increment_curr_array_field_value_type()

    def generate_field_array_values(
        self,
        data_envelope: dict,
        field_name: str,
    ) -> None:
        array_values = []
        for i in range(self.curr_array_size):
            array_value = f"array_value_{self.curr_value_ordinal}"
            self.increment_curr_value_ordinal()
            array_values.append(array_value)
        self.increment_curr_array_size()
        data_envelope[field_name] = array_values

    def generate_field_scalar_value(
        self,
        data_envelope: dict,
        field_name: str,
    ) -> None:
        scalar_value = f"scalar_value_{self.curr_value_ordinal}"
        self.increment_curr_value_ordinal()
        data_envelope[field_name] = scalar_value

    def increment_curr_value_ordinal(self):
        self.curr_value_ordinal += 1
        if self.curr_value_ordinal > self.max_value_ordinal:
            self.curr_value_ordinal = 1

    def increment_curr_array_size(self):
        self.curr_array_size += 1
        if self.curr_array_size > self.max_array_size:
            self.curr_array_size = 1

    def increment_curr_array_field_value_type(self):
        if self.curr_array_field_value_type == "scalar":
            self.curr_array_field_value_type = "array"
        else:
            self.curr_array_field_value_type = "scalar"
