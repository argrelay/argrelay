from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QueryResult:
    """
    Results of a query via `QueryEngine.query_prop_values`.
    """

    data_envelope: dict
    """
    Last `data_envelope` in search results

    Normally, it is only useful when `found_count` = 1
    """

    found_count: int
    """
    Total number of `data_envelope`-s found.
    """

    remaining_types_to_values: dict[str, list[str]]
    """
    See `EnvelopeContainer.remaining_types_to_values`.
    """
