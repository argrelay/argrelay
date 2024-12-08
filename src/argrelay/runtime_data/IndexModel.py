from __future__ import annotations

from dataclasses import dataclass, field

index_props_ = "index_props"


@dataclass(frozen = True)
class IndexModel:
    """
    Defines index model for FS_45_08_22_15 index model API.
    """

    collection_name: str

    index_props: list[str] = field()
    """
    Lists fields of `data_envelope` which are to be indexed by MongoDB for given collection.
    """
