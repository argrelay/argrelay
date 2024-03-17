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
                  original_find_and_loop     0.012     0.044     0.134     0.459     1.715     6.159    28.553
                         native_distinct     0.077     0.209     0.581     1.538     3.186     6.295    11.231
                        native_aggregate     0.077     0.227     0.913     3.717    15.944    63.955   375.196
        ================================
        use_mongomock: True
        use_single_collection: False

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.011     0.031     0.102     0.431     1.750     6.061    35.473
                         native_distinct     0.057     0.172     0.468     1.247     2.938     5.556    10.528
                        native_aggregate     0.037     0.116     0.401     1.725     7.852    27.517   169.423
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
                  original_find_and_loop     0.028     0.034     0.070     0.147     0.255     0.493     1.040
                         native_distinct     0.070     0.137     0.264     0.550     0.976     1.896     3.452
                        native_aggregate     0.028     0.046     0.070     0.115     0.207     0.354     0.550
        ================================
        use_mongomock: False
        use_single_collection: False

                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.033     0.027     0.055     0.141     0.197     0.342     0.744
                         native_distinct     0.047     0.088     0.158     0.285     0.479     0.821     1.389
                        native_aggregate     0.023     0.030     0.054     0.073     0.120     0.191     0.326
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
