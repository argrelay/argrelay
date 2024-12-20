from __future__ import annotations

import copy
import json

from cachetools import TTLCache
from pymongo.cursor import Cursor
from pymongo.database import Database

from argrelay.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.misc_helper_server import insert_unique_to_sorted_list
from argrelay.relay_server.QueryCacheConfig import QueryCacheConfig
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import mongo_id_
from argrelay.schema_response.EnvelopeContainerSchema import found_count_


class QueryEngine:

    def __init__(
        self,
        query_cache_config: QueryCacheConfig,
        mongo_db: Database,
        distinct_values_query: DistinctValuesQuery,
    ):
        self.mongo_db: Database = mongo_db

        self.query_cache_max_size_bytes = query_cache_config.query_cache_max_size_bytes
        self.query_cache_ttl_sec = query_cache_config.query_cache_ttl_sec

        # There is a separate cache per `collection_name`:
        self.query_caches: dict[str, TTLCache] = {}

        self.enable_query_cache: bool = query_cache_config.enable_query_cache
        self.distinct_values_query: DistinctValuesQuery = distinct_values_query

    def query_data_envelopes_for(
        self,
        envelope_container: EnvelopeContainer,
    ) -> list[dict]:
        query_dict = populate_query_dict(envelope_container)
        return self.query_data_envelopes(
            envelope_container.search_control.collection_name,
            query_dict,
        )

    def query_data_envelopes(
        self,
        collection_name: str,
        query_dict: dict,
    ) -> list[dict]:
        """
        This query is used for `ServerAction.RelayLineArgs` with
        final invocation for vararg-like multiple `data_envelope`-s (FS_18_64_57_18).
        Therefore, it is not latency-sensitive (results are not cached).

        See also `QueryResult.query_prop_values`.
        """

        mongo_cursor: Cursor = self.get_data_envelopes_cursor(
            collection_name,
            query_dict,
        )
        return list(iter(mongo_cursor))

    def get_data_envelopes_cursor(
        self,
        collection_name: str,
        query_dict: dict,
    ) -> Cursor:
        return self.mongo_db[collection_name].find(query_dict)

    def invalidate_cache_for_collection(
        self,
        collection_name: str,
    ):
        query_cache = self._get_query_cache_for_collection(collection_name)
        query_cache.clear()

    def query_prop_values(
        self,
        query_dict: dict,
        search_control: SearchControl,
        assigned_prop_name_to_prop_value: dict[str, AssignedValue],
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
            query_cache = self._get_query_cache_for_collection(search_control.collection_name)
            query_result = query_cache.get(query_key)
            ElapsedTime.measure("after_cache_lookup")
            if query_result:
                return copy.deepcopy(query_result)

            query_result = self._query_prop_values(
                assigned_prop_name_to_prop_value,
                query_dict,
                search_control,
            )

            query_cache[query_key] = copy.deepcopy(query_result)
        else:
            query_result = self._query_prop_values(
                assigned_prop_name_to_prop_value,
                query_dict,
                search_control,
            )
        # No cache -> no deep copy (throw away result):
        return query_result

    def _get_query_cache_for_collection(
        self,
        collection_name: str,
    ):
        query_cache = self.query_caches.setdefault(
            collection_name,
            TTLCache(
                maxsize = self.query_cache_max_size_bytes,
                ttl = self.query_cache_ttl_sec,
            ),
        )
        return query_cache

    def _query_prop_values(
        self,
        assigned_prop_name_to_prop_value,
        query_dict,
        search_control,
    ) -> QueryResult:
        """
        Implements query for FS_02_25_41_81 `func_id_query_enum_items`.
        """
        if self.distinct_values_query is DistinctValuesQuery.original_find_and_loop:
            return self._query_prop_values_original_find_and_loop(
                assigned_prop_name_to_prop_value,
                query_dict,
                search_control,
            )
        elif self.distinct_values_query is DistinctValuesQuery.native_distinct:
            return self._query_prop_values_native_distinct(
                assigned_prop_name_to_prop_value,
                query_dict,
                search_control,
            )
        elif self.distinct_values_query is DistinctValuesQuery.native_aggregate:
            return self._query_prop_values_native_aggregate(
                assigned_prop_name_to_prop_value,
                query_dict,
                search_control,
            )
        else:
            raise RuntimeError(self.distinct_values_query)

    def _query_prop_values_original_find_and_loop(
        self,
        assigned_prop_name_to_prop_value,
        query_dict,
        search_control,
    ) -> QueryResult:
        """
        See `DistinctValuesQuery.original_find_and_loop`.
        """

        ElapsedTime.measure("before_mongo_find")
        mongo_result = self.mongo_db[search_control.collection_name].find(query_dict)
        ElapsedTime.measure("after_mongo_find")
        query_result = self._process_prop_values(
            mongo_result,
            search_control,
            assigned_prop_name_to_prop_value,
        )
        ElapsedTime.measure("after_process_results")
        return query_result

    def _query_prop_values_native_distinct(
        self,
        assigned_prop_name_to_prop_value,
        query_dict,
        search_control,
    ) -> QueryResult:
        """
        See `DistinctValuesQuery.native_distinct`.
        """

        remaining_prop_name_to_prop_value: dict[str, list[str]] = {}
        data_envelopes = []

        # Construct grouping instruction:
        for prop_name in search_control.prop_name_to_arg_name_dict:
            # If assigned/consumed, `prop_name` must not appear as an option again:
            if prop_name not in assigned_prop_name_to_prop_value:

                ElapsedTime.measure(f"before_mongo_distinct.{prop_name}")
                distinct_vals: list = self.mongo_db[search_control.collection_name].distinct(prop_name, query_dict)
                ElapsedTime.measure(f"after_mongo_distinct.{prop_name}")

                if len(distinct_vals) > 0:
                    remaining_prop_name_to_prop_value[prop_name] = sorted(distinct_vals)

                ElapsedTime.measure(f"after_process_results.{prop_name}")

        found_count = self.mongo_db[search_control.collection_name].count_documents(query_dict)
        ElapsedTime.measure("after_count_documents")
        if found_count == 1:
            data_envelopes.append(self.mongo_db[search_control.collection_name].find_one(query_dict))
            ElapsedTime.measure("after_find_one")

        query_result = QueryResult(
            data_envelopes,
            found_count,
            remaining_prop_name_to_prop_value,
        )
        return query_result

    def _query_prop_values_native_aggregate(
        self,
        assigned_prop_name_to_prop_value,
        query_dict,
        search_control,
    ) -> QueryResult:
        """
        See `DistinctValuesQuery.native_aggregate`.
        """

        remaining_prop_name_to_prop_value: dict[str, list[str]] = {}
        data_envelopes = []

        group_dict: dict = {
            "$group": {
                mongo_id_: None,
            },
        }

        # Construct grouping instruction:
        inner_group_dict: dict = group_dict["$group"]
        for prop_name in search_control.prop_name_to_arg_name_dict:
            # If assigned/consumed, `prop_name` must not appear as an option again:
            if prop_name not in assigned_prop_name_to_prop_value:
                inner_group_dict[prop_name] = {
                    "$addToSet": f"${prop_name}",
                }

        # Count number of objects:
        # Direct use of `$count` did not work:
        # https://www.mongodb.com/docs/manual/reference/operator/aggregation/count/#behavior
        inner_group_dict[found_count_] = {
            "$sum": 1,
        }

        # Overall MongoDB:
        aggregate_pipeline = [
            {
                "$match": query_dict,
            },
            group_dict,
        ]

        ElapsedTime.measure("before_mongo_aggregate")
        mongo_result = self.mongo_db[search_control.collection_name].aggregate(aggregate_pipeline)
        ElapsedTime.measure("after_mongo_aggregate")

        # Get the first (and the only) object from the result:
        result_object: dict = next(iter(mongo_result))

        found_count: int = result_object[found_count_]
        result_object.pop(mongo_id_)
        result_object.pop(found_count_)

        for prop_name in result_object:
            # Flatten and deduplicate:
            prop_values = list(dict.fromkeys(flatten_list(result_object[prop_name])))
            if len(prop_values) > 0:
                remaining_prop_name_to_prop_value[prop_name] = sorted(prop_values)

        if found_count == 1:
            data_envelopes.append(self.mongo_db[search_control.collection_name].find_one(query_dict))

        ElapsedTime.measure("after_process_results")

        query_result = QueryResult(
            data_envelopes,
            found_count,
            remaining_prop_name_to_prop_value,
        )
        return query_result

    @staticmethod
    def _process_prop_values(
        mongo_result,
        search_control: SearchControl,
        assigned_prop_name_to_prop_value: dict[str, AssignedValue],
    ) -> QueryResult:
        """
        Process `mongo_result` per types in `search_control` and populates `remaining_prop_name_to_prop_value`.

        It combines in one loop:
        *   counting total `found_count` of `data_envelope`-s returned and
        *   storing the last `data_envelope`.
        The last `data_envelope` is only useful when `found_count` is one (making it unambiguous `data_envelope`).
        To search all `data_envelope`, use `query_data_envelopes` function.

        Populates:
        *   `found_count`
        *   `remaining_prop_name_to_prop_value`
        """

        remaining_prop_name_to_prop_value: dict[str, list[str]] = {}
        data_envelope = None
        data_envelopes = []
        found_count = 0

        # TODO: What if search result is huge? Blame data set designer?
        # find all remaining `prp_value`-s per `prop_name`:
        for data_envelope in iter(mongo_result):
            found_count += 1
            # `prop_name` must be known:
            for prop_name in search_control.prop_name_to_arg_name_dict:
                # `prop_name` must be in one of the `data_envelope`-s found:
                if prop_name in data_envelope:
                    # If assigned/consumed, `prop_name` must not appear
                    # as an option in `remaining_prop_name_to_prop_value` again:
                    if prop_name not in assigned_prop_name_to_prop_value:
                        prop_values_src = scalar_to_list_values(data_envelope[prop_name])

                        prop_values_dst = remaining_prop_name_to_prop_value.setdefault(prop_name, [])

                        # Deduplicate: ensure unique `prop_value`-s:
                        for prop_value in prop_values_src:
                            insert_unique_to_sorted_list(prop_values_dst, prop_value)

        # Populate max one (last) `data_envelope` on prop query for performance reasons:
        if found_count == 1:
            assert data_envelope is not None
            data_envelopes.append(data_envelope)

        return QueryResult(
            data_envelopes,
            found_count,
            remaining_prop_name_to_prop_value,
        )


def flatten_list(
    prop_values: list | str,
) -> list[str]:
    """
    FS_06_99_43_60 providing scalar value for array `prop_value` is also possible (and vice versa).
    """
    if not isinstance(prop_values, list):
        # Scalar value -> list:
        return [prop_values]
    else:
        flat_list: list[str] = []
        for prop_value in prop_values:
            # FS_06_99_43_60 (array `prop_value`): avoid array of arrays per value:
            # In case of using `aggregate` from MongoDB API, lists can contain lists - flatten:
            if isinstance(prop_value, list):
                # List of lists -> list:
                flat_list.extend(flatten_list(prop_value))
            else:
                flat_list.append(prop_value)
        return flat_list


def scalar_to_list_values(
    prop_values: list | str,
) -> list[str]:
    """
    FS_06_99_43_60 providing scalar value for array `prop_name` is also possible (and vice versa).
    """
    if not isinstance(prop_values, list):
        return [prop_values]
    else:
        return prop_values


def populate_query_dict(
    envelope_container: EnvelopeContainer,
) -> dict:
    query_dict = {}
    # FS_31_70_49_15: populate `prop_value`-s to search from the context:
    for prop_name in envelope_container.search_control.prop_name_to_arg_name_dict:
        if prop_name in envelope_container.assigned_prop_name_to_prop_value:
            query_dict[prop_name] = envelope_container.assigned_prop_name_to_prop_value[prop_name].prop_value
    return query_dict
