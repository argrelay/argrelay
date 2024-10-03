from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen = True)
class DataModel:
    """
    Defines data model for FS_45_08_22_15 data model manipulation API.

    TODO: TODO_08_25_32_95: redesign `class_to_collection_map`:
          this class replaces `class_to_collection_map`
    """

    collection_name: str

    # TODO: Maybe rename to `envelope_class` everywhere for consistency?
    # TODO: TODO_98_35_14_72: exclude `class_name` from `search_control`:
    class_name: str
    """
    See also synonym `ReservedPropName.envelope_class`.
    """

    # TODO: FS_45_08_22_15 data model manipulation: move to DataModel
    index_props: list[str] = field()
    """
    Lists fields of `data_envelop` which are to be indexed by MongoDB for given collection.
    """
