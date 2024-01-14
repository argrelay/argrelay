from __future__ import annotations

import copy
import json

from cachetools import TTLCache
from pymongo.database import Database

from argrelay.enum_desc.DistinctValuesQuery import DistinctValuesQuery
from argrelay.enum_desc.ReservedArgType import ReservedArgType
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
        self.query_cache: TTLCache = TTLCache(
            maxsize = query_cache_config.query_cache_max_size_bytes,
            ttl = query_cache_config.query_cache_ttl_sec,
        )
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

        See also `QueryResult.data_envelopes`.
        """

        query_res = self.mongo_db[collection_name].find(query_dict)
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
        """
        Implements query for FS_02_25_41_81 `query_enum_items_func`.
        """
        if self.distinct_values_query is DistinctValuesQuery.original_find_and_loop:
            return self._query_prop_values_original_find_and_loop(
                assigned_types_to_values,
                query_dict,
                search_control,
            )
        elif self.distinct_values_query is DistinctValuesQuery.native_distinct:
            return self._query_prop_values_native_distinct(
                assigned_types_to_values,
                query_dict,
                search_control,
            )
        elif self.distinct_values_query is DistinctValuesQuery.native_aggregate:
            return self._query_prop_values_native_aggregate(
                assigned_types_to_values,
                query_dict,
                search_control,
            )
        else:
            raise RuntimeError(self.distinct_values_query)

    def _query_prop_values_original_find_and_loop(
        self,
        assigned_types_to_values,
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
            assigned_types_to_values,
        )
        ElapsedTime.measure("after_process_results")
        return query_result

    def _query_prop_values_native_distinct(
        self,
        assigned_types_to_values,
        query_dict,
        search_control,
    ) -> QueryResult:
        """
        See `DistinctValuesQuery.native_distinct`.
        """

        remaining_types_to_values: dict[str, list[str]] = {}
        data_envelopes = []

        # Construct grouping instruction:
        for prop_name in search_control.types_to_keys_dict:
            # If assigned/consumed, `arg_type` must not appear as an option again:
            if prop_name not in assigned_types_to_values:

                ElapsedTime.measure(f"before_mongo_distinct.{prop_name}")
                distinct_vals: list = self.mongo_db[search_control.collection_name].distinct(prop_name, query_dict)
                ElapsedTime.measure(f"after_mongo_distinct.{prop_name}")

                if len(distinct_vals) > 0:
                    remaining_types_to_values[prop_name] = sorted(distinct_vals)

                ElapsedTime.measure(f"after_process_results.{prop_name}")

        found_count = self.mongo_db[search_control.collection_name].count_documents(query_dict)
        ElapsedTime.measure("after_count_documents")
        if found_count == 1:
            data_envelopes.append(self.mongo_db[search_control.collection_name].find_one(query_dict))
            ElapsedTime.measure("after_find_one")

        query_result = QueryResult(
            data_envelopes,
            found_count,
            remaining_types_to_values,
        )
        return query_result

    def _query_prop_values_native_aggregate(
        self,
        assigned_types_to_values,
        query_dict,
        search_control,
    ) -> QueryResult:
        """
        See `DistinctValuesQuery.native_aggregate`.
        """

        remaining_types_to_values: dict[str, list[str]] = {}
        data_envelopes = []

        group_dict: dict = {
            "$group": {
                mongo_id_: None,
            },
        }

        # Construct grouping instruction:
        inner_group_dict: dict = group_dict["$group"]
        for prop_name in search_control.types_to_keys_dict:
            # If assigned/consumed, `arg_type` must not appear as an option again:
            if prop_name not in assigned_types_to_values:
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

        for arg_type in result_object:
            # Flatten and deduplicate:
            arg_vals = list(dict.fromkeys(flatten_list(result_object[arg_type])))
            if len(arg_vals) > 0:
                remaining_types_to_values[arg_type] = sorted(arg_vals)

        if found_count == 1:
            data_envelopes.append(self.mongo_db[search_control.collection_name].find_one(query_dict))

        ElapsedTime.measure("after_process_results")

        query_result = QueryResult(
            data_envelopes,
            found_count,
            remaining_types_to_values,
        )
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
                            insert_unique_to_sorted_list(val_list, arg_val)

        # Populate max one (last) `data_envelope` on prop query for performance reasons:
        if found_count == 1:
            assert data_envelope is not None
            data_envelopes.append(data_envelope)

        return QueryResult(
            data_envelopes,
            found_count,
            remaining_types_to_values,
        )


def flatten_list(arg_vals: list | str) -> list[str]:
    """
    FS_06_99_43_60 providing scalar value for list/array field is also possible (and vice versa).
    """
    if not isinstance(arg_vals, list):
        # Scalar value -> list:
        return [arg_vals]
    else:
        flat_list: list[str] = []
        for arg_val in arg_vals:
            # FS_06_99_43_60 (list arg value): avoid list of lists per value:
            # In case of using `aggregate` from MongoDB API, lists can contain lists - flatten:
            if isinstance(arg_val, list):
                # List of lists -> list:
                flat_list.extend(flatten_list(arg_val))
            else:
                flat_list.append(arg_val)
        return flat_list


def scalar_to_list_values(arg_type_val: list | str) -> list[str]:
    """
    FS_06_99_43_60 providing scalar value for list/array field is also possible (and vice versa).
    """
    if not isinstance(arg_type_val, list):
        return [arg_type_val]
    else:
        return arg_type_val


def populate_query_dict(
    envelope_container: EnvelopeContainer,
) -> dict:
    query_dict = {
        ReservedArgType.EnvelopeClass.name: envelope_container.search_control.envelope_class,
    }
    # FS_31_70_49_15: populate arg values to search from the context:
    for arg_type in envelope_container.search_control.types_to_keys_dict:
        if arg_type in envelope_container.assigned_types_to_values:
            query_dict[arg_type] = envelope_container.assigned_types_to_values[arg_type].arg_value
    return query_dict
