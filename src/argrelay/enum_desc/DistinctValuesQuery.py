from enum import auto, Enum


class DistinctValuesQuery(Enum):
    """
    Selects implementation for FS_02_25_41_81 `query_enum_items_func`.

    See `test_QueryEngine_perf.py` for perf test used to produce these tables:

    *   `mongomock`:

        ```
                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.015     0.050     0.179     0.712     2.563     8.348    34.640
                         native_distinct     0.070     0.204     0.597     1.568     3.006     5.927    10.550
                        native_aggregate     0.096     0.380     1.527     7.102    24.525    93.765   419.467
        ```

        *   The fastest on small collections is `original_find_and_loop`.
        *   The fastest on large collections is `native_distinct`.

    *   `pymongo`:

        ```
                       object_multiplier         3         4         5         6         7         8         9
                            object_count       243      1024      3125      7776     16807     32768     59049
        --------------------------------
                  original_find_and_loop     0.031     0.023     0.059     0.196     0.387     0.788     1.419
                         native_distinct     0.077     0.122     0.193     0.406     0.723     1.357     2.137
                        native_aggregate     0.027     0.035     0.080     0.144     0.278     0.450     0.715
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
