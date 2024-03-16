from enum import auto, Enum


class DistinctValuesQuery(Enum):
    """
    Selects implementation for FS_02_25_41_81 `query_enum_items_func`.

    See `test_QueryEngine_perf.py` for perf test used to produce these tables:

    Numbers for "use_single_collection: True" are more evident as `object_count` directly affects the query.

    Numbers for "use_single_collection: False" are less evident as `object_count` is distributed across collections.

    *   `mongomock`:

        ```
        ================================
        use_mongomock: True
        use_single_collection: True

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.011     0.035     0.122     0.461     1.650     5.945    27.836
                         native_distinct     0.062     0.192     0.576     1.455     2.993     6.287    10.603
                        native_aggregate     0.084     0.212     0.909     3.650    15.173    58.340   326.188
        ================================
        use_mongomock: True
        use_single_collection: False

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.007     0.028     0.096     0.439     1.672     5.939    27.561
                         native_distinct     0.048     0.159     0.465     1.224     2.725     5.539     9.572
                        native_aggregate     0.031     0.109     0.398     1.758     7.802    28.463   126.566
        ```

        *   The fastest on small collections is `original_find_and_loop`.
        *   The fastest on large collections is `native_distinct`.

    *   `pymongo`:

        ```
        ================================
        use_mongomock: False
        use_single_collection: True

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.022     0.031     0.065     0.115     0.222     0.505     0.748
                         native_distinct     0.063     0.102     0.195     0.435     0.857     1.493     2.591
                        native_aggregate     0.022     0.038     0.064     0.109     0.165     0.324     0.469
        ================================
        use_mongomock: False
        use_single_collection: False

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.020     0.025     0.048     0.144     0.175     0.383     0.590
                         native_distinct     0.048     0.067     0.123     0.228     0.365     0.594     0.991
                        native_aggregate     0.022     0.027     0.040     0.067     0.109     0.176     0.271
        ```

        The fastest is `native_aggregate`.
    """

    original_find_and_loop = auto()
    """
    See `QueryEngine._query_prop_values_original_find_and_loop`.

    It calls  MongoDB `find()` with `query_dict`, then loops to collect distinct values.

    This is the fastest option for small collections with `mongomock`.
    """

    native_distinct = auto()
    """
    See `QueryEngine._query_prop_values_native_distinct`.

    It does multiple calls to MongoDB `distinct()` with `query_dict`
    to collect set of distinct values per field at a time:
    https://stackoverflow.com/a/20655662/441652

    This is the fastest option for large collections with `mongomock`.
    """

    native_aggregate = auto()
    """
    See `QueryEngine._query_prop_values_native_aggregate`.

    It calls MongoDB `aggregate()` with `$match: query_dict`, then `$group` with `$addToSet`:
    *   See `test_MongoClient_distinc_values_search.py`:
        https://stackoverflow.com/a/63595331/441652
    *   Another example:
        https://stackoverflow.com/a/11991854/441652

    This is:
    *   the fastest option with `pymongo`.
    *   the slowest option with `mongomock`.
    """
