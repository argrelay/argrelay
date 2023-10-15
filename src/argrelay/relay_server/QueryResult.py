from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QueryResult:
    """
    Results of a query via `QueryEngine.query_prop_values`.

    Do not confuse with results of `QueryEngine.query_data_envelopes` (which returns all `data_envelope`-s directly).
    """

    data_envelopes: list[dict] = field()
    """
    Contains 0 or 1 `data_envelope`-s from search results.

    *   0: Nothing found.
    *   1: One of the found ones (possibly many).
        If `found_count` > 1, it is the last `data_envelope`-s among many found.
        If `found_count` = 1, it is exactly the `data_envelope` uniquely selected.

    Returning 1 while `found_count` > 1 is used for performance reasons with `QueryEngine.query_prop_values`.

    See also `EnvelopeContainer.data_envelopes`.
    """

    found_count: int = field()
    """
    Total number of `data_envelope`-s found - see `data_envelopes`.
    """

    remaining_types_to_values: dict[str, list[str]] = field()
    """
    See `EnvelopeContainer.remaining_types_to_values`.
    """
