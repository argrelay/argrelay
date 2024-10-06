from enum import auto, Enum


class DistinctValuesQuery(Enum):
    """
    Selects implementation for FS_02_25_41_81 `func_id_query_enum_items`.

    See `test_QueryEngine_perf.py` for perf test used to produce these tables (time is in seconds):

    *   `mongomock`:

        ```
        ================================
        use_mongomock: True

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
