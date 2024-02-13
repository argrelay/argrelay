from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

import jsonpath_ng
from jsonpath_ng import DatumInContext


@dataclass
class JsonTestOutputVerifier:
    """
    Implements TODO_32_99_70_35 verify data via JSONPath queries.
    """

    json_query_assert_list: dict[
        str,
        list[
            Callable[
                [list[DatumInContext]],
                None,
            ]
        ]
    ] = field(default_factory = lambda: {})
    """
    JSON query `str` to list of verifiers as `Callable`-s.

    The `Callable` verifier accepts list query results (to assert anything).
    """

    def add_verifier(
        self,
        json_query: str,
        *assert_func: Callable[[list[DatumInContext]], None],
    ):
        callable_list = self.json_query_assert_list.setdefault(json_query, [])
        for func_item in assert_func:
            callable_list.append(func_item)

        return self

    def verify_all(
        self,
        json_str: str,
    ):
        json_dict = json.loads(json_str)
        for json_query in self.json_query_assert_list:
            jsonpath_expression = jsonpath_ng.parse(json_query)
            json_match = jsonpath_expression.find(json_dict)
            callable_list = self.json_query_assert_list[json_query]
            for callable_item in callable_list:
                callable_item(json_match)
