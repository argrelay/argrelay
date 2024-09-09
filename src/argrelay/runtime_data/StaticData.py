from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection


@dataclass(frozen = True)
class StaticData:
    """
    All data which normally does not change between requests.

    See also `StaticDataSchema`.
    """

    envelope_collections: dict[str, EnvelopeCollection] = field()
    """
    MondoDB collection name to its `EnvelopeCollection`.

    TODO: TODO_08_25_32_95: redesign `class_to_collection_map`:
    Collection name is normally (but not necessarily) matching
    the value of `ReservedPropName.envelope_class` prop.
    """
