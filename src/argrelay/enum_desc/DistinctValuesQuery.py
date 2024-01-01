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
                  original_find_and_loop     0.009     0.030     0.115     0.440     1.632     6.137    33.669
                         native_distinct     0.038     0.122     0.363     0.969     2.183     4.740     7.102
                        native_aggregate     0.044     0.151     0.679     2.899    13.257    49.728   292.153
        ================================
        use_mongomock: True
        use_single_collection: False

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.006     0.018     0.113     0.414     1.662     5.831    29.375
                         native_distinct     0.027     0.096     0.327     0.812     1.830     3.578     6.403
                        native_aggregate     0.020     0.066     0.258     1.108     4.923    17.561    95.461
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
                  original_find_and_loop     0.013     0.023     0.043     0.090     0.182     0.428     0.746
                         native_distinct     0.041     0.065     0.117     0.241     0.462     0.796     1.458
                        native_aggregate     0.022     0.027     0.050     0.081     0.125     0.210     0.368
        ================================
        use_mongomock: False
        use_single_collection: False

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.015     0.020     0.039     0.087     0.148     0.345     0.633
                         native_distinct     0.044     0.048     0.087     0.173     0.299     0.512     0.903
                        native_aggregate     0.016     0.021     0.033     0.054     0.086     0.159     0.231
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
