from __future__ import annotations

from enum import (
    auto,
    Enum,
)

from offline_tests.mongo_query.MongoClientTestClass import MongoClientTestClass


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


class ThisTestClass(MongoClientTestClass):

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

        self.test_size = TestSize.SmallSize

        if self.test_size == TestSize.SmallSize:
            self.prop_count = 17
            self.envelope_count = 163
            self.max_value_ordinal = 11
            self.max_array_size = 19

            self.col_query = {
                "prop_8": "scalar_value_8",
                "prop_11": "array_value_1",
                "prop_3": "array_value_3",
            }

        if self.test_size == TestSize.MediumSize:
            # Maximum number of indexes in MongoDB = 64:
            # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Number-of-Indexes-per-Collection
            self.prop_count = 63
            self.envelope_count = 7057
            self.max_value_ordinal = 379
            self.max_array_size = 113

            self.col_query = {
                "prop_3": "array_value_3",
                "prop_7": "array_value_56",
                "prop_31": "array_value_46",
                "prop_51": "array_value_26",
            }

        if self.test_size == TestSize.LargeSize:
            self.prop_count = 263
            self.envelope_count = 7057
            self.max_value_ordinal = 379
            self.max_array_size = 113

            self.col_query = {
                "prop_3": "array_value_3",
                "prop_11": "array_value_259",
                "prop_83": "array_value_343",
            }

        self.assertTrue(
            self.prop_count * self.envelope_count * self.max_array_size < 1_000_000_000,
            "estimated (roughly) mem size should not exceed 1 G",
        )

        self.curr_value_ordinal = 1
        self.curr_array_size = 1
        # the other one is "array"
        self.curr_array_prop_value_type = "scalar"

    # noinspection PyMethodMayBeStatic
    def test_live_index_limits(self):
        """
        Test mongodb index limits:
        *   generates prop names to be indexed
        *   decides which prop will contain array values or not
        *   generates `data_envelope`-s with generated values
        *   array props of `data_envelope`-s are populated with either scalar or array
        *   runs few queries

        Note:
        These limitation to have multiple props with array values actually
        *   apply for `pymongo`
        *   do not apply for `mongomock`
        # https://www.mongodb.com/docs/manual/reference/limits/#mongodb-limit-Number-of-Indexes-per-Collection
        Real MongoDB (`pymongo`) fails for larger numbers with this:
        ```
        pymongo.errors.OperationFailure: add index fails, too many indexes for argrelay.argrelay key:{ prop_61: 1 }, full error: {'ok': 0.0, 'errmsg': 'add index fails, too many indexes for argrelay.argrelay key:{ prop_61: 1 }', 'code': 67, 'codeName': 'CannotCreateIndex'}
        ```
        """

        # props which will be indexed:
        index_props = self.generate_prop_names()

        array_prop_names = self.decide_array_prop_names(index_props)

        data_envelopes = self.generate_data_envelopes(index_props, array_prop_names)

        self.col_proxy.insert_many(data_envelopes)

        self.index_props(self.col_proxy, index_props)

        # noinspection PyUnreachableCode
        if False:
            self.show_all_envelopes(col_proxy)

        print("query 1:")
        for data_envelope in self.col_proxy.find(self.col_query):
            print("data_envelope: ", data_envelope)

    def generate_prop_names(self) -> list[str]:
        prop_names = []
        for prop_n in range(1, self.prop_count + 1):
            prop_names.append(f"prop_{prop_n}")
        return prop_names

    # noinspection PyMethodMayBeStatic
    def decide_array_prop_names(
        self,
        prop_names,
    ):
        """
        even = scalar props
        odd = array props
        """
        array_prop_names = []
        for prop_n in range(1, len(prop_names) + 1):
            if prop_n % 2 != 0:
                array_prop_names.append(prop_names[prop_n - 1])
        return array_prop_names

    def generate_data_envelopes(
        self,
        prop_names: list[str],
        array_prop_names: list[str],
    ) -> list[dict]:
        data_envelopes = []
        for envelope_n in range(1, self.envelope_count + 1):
            data_envelope = self.generate_data_envelope(prop_names, array_prop_names)
            data_envelopes.append(data_envelope)
            if envelope_n % 1_000 == 0:
                print(f"{envelope_n}/{self.envelope_count}")
        return data_envelopes

    def generate_data_envelope(
        self,
        prop_names: list[str],
        array_prop_names: list[str],
    ) -> dict:
        data_envelope = {}
        for prop_name in prop_names:
            if prop_name in array_prop_names:
                self.generate_array_prop_values(data_envelope, prop_name)
            else:
                self.generate_prop_scalar_value(data_envelope, prop_name)
        return data_envelope

    def generate_array_prop_values(
        self,
        data_envelope: dict,
        array_prop_name: str,
    ) -> None:
        if self.curr_array_prop_value_type == "array":
            self.generate_prop_array_values(data_envelope, array_prop_name)
        else:
            self.generate_prop_scalar_value(data_envelope, array_prop_name)
        self.increment_curr_array_prop_value_type()

    def generate_prop_array_values(
        self,
        data_envelope: dict,
        prop_name: str,
    ) -> None:
        array_values = []
        for i in range(self.curr_array_size):
            array_value = f"array_value_{self.curr_value_ordinal}"
            self.increment_curr_value_ordinal()
            array_values.append(array_value)
        self.increment_curr_array_size()
        data_envelope[prop_name] = array_values

    def generate_prop_scalar_value(
        self,
        data_envelope: dict,
        prop_name: str,
    ) -> None:
        scalar_value = f"scalar_value_{self.curr_value_ordinal}"
        self.increment_curr_value_ordinal()
        data_envelope[prop_name] = scalar_value

    def increment_curr_value_ordinal(self):
        self.curr_value_ordinal += 1
        if self.curr_value_ordinal > self.max_value_ordinal:
            self.curr_value_ordinal = 1

    def increment_curr_array_size(self):
        self.curr_array_size += 1
        if self.curr_array_size > self.max_array_size:
            self.curr_array_size = 1

    def increment_curr_array_prop_value_type(self):
        if self.curr_array_prop_value_type == "scalar":
            self.curr_array_prop_value_type = "array"
        else:
            self.curr_array_prop_value_type = "scalar"
