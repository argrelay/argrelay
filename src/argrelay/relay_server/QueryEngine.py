from __future__ import annotations

import copy
import json

from cachetools import TTLCache
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.QueryCacheConfig import QueryCacheConfig
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_


class QueryEngine:
    mongo_db: Database

    mongo_col: Collection

    query_cache: TTLCache

    enable_query_cache: bool

    def __init__(
        self,
        query_cache_config: QueryCacheConfig,
        mongo_db: Database,
    ):
        self.mongo_db = mongo_db
        self.mongo_col = self.mongo_db[data_envelopes_]
        self.query_cache = TTLCache(
            maxsize = query_cache_config.query_cache_max_size_bytes,
            ttl = query_cache_config.query_cache_ttl_sec,
        )
        self.enable_query_cache = query_cache_config.enable_query_cache

    def query_envelopes(
        self,
        query_dict: dict,
        search_control: SearchControl,
        assigned_types_to_values: dict[str, AssignedValue],
    ):
        if self.enable_query_cache:
            ElapsedTime.measure("before_cache_lookup")
            query_key = json.dumps(query_dict, separators = (",", ":"))
            query_result = self.query_cache.get(query_key)
            ElapsedTime.measure("after_cache_lookup")
            if query_result:
                return copy.deepcopy(query_result)

            query_result = self.run_query_and_process_results(
                assigned_types_to_values,
                query_dict,
                search_control,
            )

            self.query_cache[query_key] = copy.deepcopy(query_result)
        else:
            query_result = self.run_query_and_process_results(
                assigned_types_to_values,
                query_dict,
                search_control,
            )
        # No cache -> no deep copy (throw away result):
        return query_result

    def run_query_and_process_results(
        self,
        assigned_types_to_values,
        query_dict,
        search_control,
    ):
        ElapsedTime.measure("before_mongo_find")
        query_res = self.mongo_col.find(query_dict)
        ElapsedTime.measure("after_mongo_find")
        query_result = self.process_results(
            query_res,
            search_control,
            assigned_types_to_values,
        )
        ElapsedTime.measure("after_process_results")
        return query_result

    @staticmethod
    def process_results(
        query_res,
        search_control: SearchControl,
        assigned_types_to_values: dict[str, AssignedValue],
    ) -> QueryResult:
        """
        Populates:
        *   `found_count`
        *   `remaining_types_to_values`
        """
        remaining_types_to_values: dict[str, list[str]] = {}
        data_envelope = None
        found_count = 0

        # TODO: What if search result is huge? Blame data set designer?
        # find all remaining arg vals per arg type:
        for data_envelope in iter(query_res):
            found_count += 1
            # `arg_type` must be known:
            for arg_type in search_control.types_to_keys_dict.keys():
                # `arg_type` must be in one of the `data_envelope`-s found:
                if arg_type in data_envelope:
                    # If assigned/consumed, `arg_type` must not appear
                    # as an option in `remaining_types_to_values` again:
                    if arg_type not in assigned_types_to_values.keys():
                        arg_val = data_envelope[arg_type]
                        if arg_type not in remaining_types_to_values:
                            val_list = []
                            remaining_types_to_values[arg_type] = val_list
                        else:
                            val_list = remaining_types_to_values[arg_type]
                        # Deduplicate: ensure unique `arg_value`-s:
                        if arg_val not in val_list:
                            val_list.append(arg_val)

        return QueryResult(
            data_envelope,
            found_count,
            remaining_types_to_values,
        )
