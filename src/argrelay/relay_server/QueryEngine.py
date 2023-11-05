from __future__ import annotations

import copy
import json

from cachetools import TTLCache
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.QueryCacheConfig import QueryCacheConfig
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_


class QueryEngine:

    def __init__(
        self,
        query_cache_config: QueryCacheConfig,
        mongo_db: Database,
    ):
        self.mongo_db: Database = mongo_db
        self.mongo_col: Collection = self.mongo_db[data_envelopes_]
        self.query_cache: TTLCache = TTLCache(
            maxsize = query_cache_config.query_cache_max_size_bytes,
            ttl = query_cache_config.query_cache_ttl_sec,
        )
        self.enable_query_cache: bool = query_cache_config.enable_query_cache

    def query_data_envelopes(
        self,
        query_dict: dict,
    ) -> list[dict]:
        """
        This query is used for `ServerAction.RelayLineArgs` with
        final invocation for vararg-like multiple `data_envelope`-s (FS_18_64_57_18).
        Therefore, it is not latency-sensitive (results are not cached).

        See also `QueryResult.data_envelopes`.
        """

        query_res = self.mongo_col.find(query_dict)
        return list(iter(query_res))

    def query_prop_values(
        self,
        query_dict: dict,
        search_control: SearchControl,
        assigned_types_to_values: dict[str, AssignedValue],
    ) -> QueryResult:
        """
        Implements FS_39_58_01_91 query cache (if `enable_query_cache`).

        Returned `QueryResult` is used in for `ServerAction.ProposeArgValues` (Tab-completion)
        which makes it latency-sensitive (so the result is cached - see FS_39_58_01_91).

        Unlike `QueryEngine.query_data_envelopes` which returns all `data_envelopes` directly,
        `QueryEngine.query_prop_values` populates 0 to 1 envelope only (for performance reasons).

        See also `QueryResult.query_data_envelopes` and `QueryResult.data_envelopes`
        """

        if self.enable_query_cache:
            ElapsedTime.measure("before_cache_lookup")
            query_key = json.dumps(query_dict, separators = (",", ":"))
            query_result = self.query_cache.get(query_key)
            ElapsedTime.measure("after_cache_lookup")
            if query_result:
                return copy.deepcopy(query_result)

            query_result = self._query_prop_values(
                assigned_types_to_values,
                query_dict,
                search_control,
            )

            self.query_cache[query_key] = copy.deepcopy(query_result)
        else:
            query_result = self._query_prop_values(
                assigned_types_to_values,
                query_dict,
                search_control,
            )
        # No cache -> no deep copy (throw away result):
        return query_result

    def _query_prop_values(
        self,
        assigned_types_to_values,
        query_dict,
        search_control,
    ) -> QueryResult:

        ElapsedTime.measure("before_mongo_find")
        mongo_result = self.mongo_col.find(query_dict)
        ElapsedTime.measure("after_mongo_find")
        query_result = self._process_prop_values(
            mongo_result,
            search_control,
            assigned_types_to_values,
        )
        ElapsedTime.measure("after_process_results")
        return query_result

    @staticmethod
    def _process_prop_values(
        mongo_result,
        search_control: SearchControl,
        assigned_types_to_values: dict[str, AssignedValue],
    ) -> QueryResult:
        """
        Process `mongo_result` per types in `search_control` and populates `remaining_types_to_values`.

        It combines in one loop:
        *   counting total `found_count` of `data_envelope`-s returned and
        *   storing the last `data_envelope`.
        The last `data_envelope` is only useful when `found_count` is one (making it unambiguous `data_envelope`).
        To search all `data_envelope`, use `query_data_envelopes` function.

        Populates:
        *   `found_count`
        *   `remaining_types_to_values`
        """

        remaining_types_to_values: dict[str, list[str]] = {}
        data_envelope = None
        data_envelopes = []
        found_count = 0

        # TODO: What if search result is huge? Blame data set designer?
        # find all remaining arg vals per arg type:
        for data_envelope in iter(mongo_result):
            found_count += 1
            # `arg_type` must be known:
            for arg_type in search_control.types_to_keys_dict:
                # `arg_type` must be in one of the `data_envelope`-s found:
                if arg_type in data_envelope:
                    # If assigned/consumed, `arg_type` must not appear
                    # as an option in `remaining_types_to_values` again:
                    if arg_type not in assigned_types_to_values:
                        arg_vals = scalar_to_list_values(data_envelope[arg_type])

                        val_list = remaining_types_to_values.setdefault(arg_type, [])

                        # Deduplicate: ensure unique `arg_value`-s:
                        for arg_val in arg_vals:
                            if arg_val not in val_list:
                                val_list.append(arg_val)

        # Populate max one `data_envelope` on prop query for performance reasons:
        if data_envelope is not None:
            data_envelopes.append(data_envelope)

        return QueryResult(
            data_envelopes,
            found_count,
            remaining_types_to_values,
        )


def scalar_to_list_values(arg_type_val: list | str) -> list[str]:
    """
    FS_06_99_43_60 providing scalar value for list/array field is also possible (and vice versa).
    """
    if not isinstance(arg_type_val, list):
        return [arg_type_val]
    else:
        return arg_type_val


def populate_query_dict(envelope_container):
    query_dict = {
        ReservedArgType.EnvelopeClass.name: envelope_container.search_control.envelope_class,
    }
    # FS_31_70_49_15: populate arg values to search from the context:
    for arg_type in envelope_container.search_control.types_to_keys_dict:
        if arg_type in envelope_container.assigned_types_to_values:
            query_dict[arg_type] = envelope_container.assigned_types_to_values[arg_type].arg_value
    return query_dict
