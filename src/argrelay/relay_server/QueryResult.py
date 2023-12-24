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

    The contents of the `data_envelopes` is only reliable (the `data_envelope` found) when `found_count == 1`.

    Returning maximum single `data_envelope` (when `found_count` != 0) is used for
    performance reasons with `QueryEngine.query_prop_values`.

    See also `EnvelopeContainer.data_envelopes` to get the entire list of the `data_envelopes`.
    """

    found_count: int = field()
    """
    Total number of `data_envelope`-s found - see `data_envelopes`.

    When `found_count == 1`, `data_envelopes` contains exactly the one `data_envelope` found.
    """

    remaining_types_to_values: dict[str, list[str]] = field()
    """
    See `EnvelopeContainer.remaining_types_to_values`.

    Each list is sorted.
    """
