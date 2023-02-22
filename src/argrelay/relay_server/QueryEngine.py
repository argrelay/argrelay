from __future__ import annotations

import json
from datetime import timedelta

from cachetools import TTLCache
from pymongo.collection import Collection
from pymongo.database import Database

from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_core_server.StaticDataSchema import data_envelopes_


class QueryEngine:
    mongo_db: Database

    mongo_col: Collection

    query_cache: TTLCache

    is_cache_enabled: bool

    def __init__(self, mongo_db: Database):
        self.mongo_db = mongo_db
        self.mongo_col = self.mongo_db[data_envelopes_]
        self.query_cache = TTLCache(
            maxsize = 1024,
            ttl = timedelta(seconds = 60).total_seconds(),
        )
        self.is_cache_enabled = True

    def query_envelopes(
        self,
        query_dict: dict,
        search_control: SearchControl,
        assigned_types_to_values: dict[str, AssignedValue],
    ):
        if self.is_cache_enabled:
            ElapsedTime.measure("before_cache_lookup")
            query_key = json.dumps(query_dict, separators = (",", ":"))
            query_result = self.query_cache.get(query_key)
            ElapsedTime.measure("after_cache_lookup")
            if query_result:
                return query_result

        ElapsedTime.measure("before_mongo_find")
        query_res = self.mongo_col.find(query_dict)
        ElapsedTime.measure("after_mongo_find")
        query_result = self.process_results(
            query_res,
            search_control,
            assigned_types_to_values,
        )
        if self.is_cache_enabled:
            self.query_cache[query_key] = query_result
        return query_result

    @staticmethod
    def process_results(
        query_res,
        search_control: SearchControl,
        assigned_types_to_values: dict[str, AssignedValue],
    ) -> QueryResult:
        """
        Primarily populates remaining_types_to_values.
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
                    # `arg_type` must not be assigned/consumed:
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
